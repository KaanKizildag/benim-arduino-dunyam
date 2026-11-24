import os
import uuid
from datetime import datetime
from typing import List, Optional, Dict, Any
from fastapi import FastAPI, HTTPException, Depends
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import StreamingResponse
from pydantic import BaseModel
from dotenv import load_dotenv

os.environ["LITELLM_LOCAL_MODEL_COST_MAP"] = "True"
import litellm

# Yeni nesil modellerin (Gemini 3.x vb.) desteklemediği parametreleri (ör. temperature) sessizce düşür
litellm.drop_params = True

from schemas import (
    ProjeTasarimi,
    CircuitNetlist,
    WiringDesignResponse,
    LogicDesignResponse,
    SavedProjectEntry,
    AILogEntry,
)
from prompt_filter import validate_project_prompt
from ai_service import (
    generate_full_project_one_shot,
    generate_full_project_stream,
    generate_revised_project_stream,
    generate_wiring_only,
    generate_logic_and_code_for_wiring,
    fix_arduino_code,
    get_all_available_models,
    get_saved_projects,
    save_project_entry,
    delete_saved_project,
    get_ai_logs,
    clear_ai_logs,
)
from arduino_service import (
    get_connected_ports,
    compile_and_upload,
    stream_serial_port_events,
)

from database import init_db, get_db_connection
from auth_service import get_current_user_optional
from rbac_api import router as rbac_router

load_dotenv()

# Veritabanını ve ilk seed verilerini başlat
init_db()

app = FastAPI(
    title="Kid Arduino Studio Backend",
    description="Çocuklar İçin AI Destekli Görsel Arduino Stüdyosu API",
    version="1.2.0"
)

# RBAC ve Yönetim Yönlendiricisini Ekle
app.include_router(rbac_router)

# CORS yapılandırması
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

DEFAULT_OLLAMA_URL = os.getenv("OLLAMA_API_BASE") or os.getenv("OLLAMA_URL") or "http://127.0.0.1:11434"


# ---------------------------------------------------------
# İstek Modelleri
# ---------------------------------------------------------

class GenerateRequest(BaseModel):
    prompt: str
    inventory: List[str]
    model: Optional[str] = None
    api_key: Optional[str] = None
    ollama_url: Optional[str] = None

class GenerateLogicRequest(BaseModel):
    prompt: str
    proje_adi: Optional[str] = "Akıllı Arduino Projem"
    netlist: CircuitNetlist
    model: Optional[str] = None
    api_key: Optional[str] = None
    ollama_url: Optional[str] = None

class SaveProjectRequest(BaseModel):
    id: Optional[str] = None
    prompt: Optional[str] = ""
    badge: Optional[str] = "AI Tasarımım ✨"
    project: ProjeTasarimi

class UploadRequest(BaseModel):
    code: str
    port: Optional[str] = None

class FixCodeRequest(BaseModel):
    code: str
    error: str
    project_context: Optional[str] = ""
    model: Optional[str] = None

class ReviseProjectRequest(BaseModel):
    current_project: ProjeTasarimi
    revision_prompt: str
    inventory: List[str]
    model: Optional[str] = None
    api_key: Optional[str] = None
    ollama_url: Optional[str] = None


# ---------------------------------------------------------
# API Endpoints
# ---------------------------------------------------------

@app.get("/api/health")
def health_check():
    return {
        "status": "healthy",
        "service": "Kid Arduino Studio API",
        "version": "1.2.0"
    }


@app.get("/api/models")
def list_available_models(gemini_api_key: Optional[str] = None, ollama_url: Optional[str] = None):
    """Sistemde algılanan yerel Ollama modellerini ve desteklenen bulut (Gemini, OpenAI, Claude) modellerini döner."""
    return get_all_available_models(
        ollama_url=ollama_url or DEFAULT_OLLAMA_URL,
        gemini_api_key=gemini_api_key
    )


@app.get("/api/ports")
def list_ports():
    """Bağlı seri portları ve Arduino kartlarını listeler."""
    ports = get_connected_ports()
    return {"ports": ports}


@app.get("/api/ai-logs", response_model=List[AILogEntry])
def list_ai_logs_endpoint():
    """Admin modu için yapay zekaya gönderilen istekleri ve alınan ham cevapları listeler."""
    return get_ai_logs()


@app.delete("/api/ai-logs")
def clear_ai_logs_endpoint():
    """Admin modundaki yapay zeka istek/cevap geçmişini temizler."""
    clear_ai_logs()
    return {"cleared": True}


@app.get("/api/mock-projects")
def list_mock_projects():
    """Örnek projeler kaldırıldı."""
    return []


@app.post("/api/generate-wiring", response_model=WiringDesignResponse)
def generate_wiring_endpoint(req: GenerateRequest):
    """
    1. Aşama AI Çağrısı: Yalnızca kablolama (netlist: hangi komponentler ve hangi pin nereye bağlanacak) üretir.
    Hatasızlığı doğrulanmış kablolama bilgisini döner; devre bu bilgiyle anında render edilir.
    """
    if not req.prompt.strip():
        raise HTTPException(status_code=400, detail="Lütfen bir proje fikri yazın!")

    # Prompt Güvenlik ve Proje Uygunluğu Denetimi
    prompt_val = validate_project_prompt(req.prompt)
    if not prompt_val.is_valid:
        raise HTTPException(status_code=400, detail=prompt_val.user_message)

    inventory = list(req.inventory) if req.inventory else ["ARDUINO_UNO", "BREADBOARD", "LED_RED", "RESISTOR_220"]
    if "ARDUINO_UNO" not in inventory:
        inventory.append("ARDUINO_UNO")
    if "BREADBOARD" not in inventory:
        inventory.append("BREADBOARD")

    try:
        return generate_wiring_only(
            prompt=req.prompt,
            inventory=inventory,
            model=req.model or "default",
            ollama_url=req.ollama_url or DEFAULT_OLLAMA_URL,
            api_key=req.api_key
        )
    except RuntimeError as e:
        raise HTTPException(status_code=502, detail=str(e))


@app.post("/api/generate-logic", response_model=LogicDesignResponse)
def generate_logic_endpoint(req: GenerateLogicRequest):
    """
    2. Aşama AI Çağrısı: Devre render edildiği anda, kesinleşmiş kablolamaya (netlist) uygun
    Akış Diyagramı ve Arduino C++ Kodu üretir ve kablolamayla %100 uyumlu olduğunu teyit eder.
    """
    try:
        return generate_logic_and_code_for_wiring(
            prompt=req.prompt,
            proje_adi=req.proje_adi or "Akıllı Arduino Projem",
            netlist=req.netlist,
            model=req.model or "default",
            ollama_url=req.ollama_url or DEFAULT_OLLAMA_URL,
            api_key=req.api_key
        )
    except RuntimeError as e:
        raise HTTPException(status_code=502, detail=str(e))


@app.get("/api/projects", response_model=List[SavedProjectEntry])
def list_saved_projects_endpoint():
    """Projelerim menüsü için daha önce kurgulanmış ve hazır projeleri listeler."""
    return get_saved_projects()


@app.post("/api/projects", response_model=SavedProjectEntry)
def save_project_endpoint(
    req: SaveProjectRequest,
    current_user: Optional[Dict[str, Any]] = Depends(get_current_user_optional)
):
    """Yeni kurgulanan bir projeyi Projelerim menüsüne ve SQLite veritabanına kaydeder."""
    entry = save_project_entry(
        project=req.project,
        prompt=req.prompt or "",
        project_id=req.id,
        badge=req.badge or "AI Tasarımım ✨"
    )

    # Kullanıcı giriş yaptıysa SQLite ilişkisel tablosuna da kaydet
    if current_user:
        try:
            with get_db_connection() as conn:
                cursor = conn.cursor()
                netlist_str = json.dumps(req.project.netlist.model_dump() if req.project.netlist else {})
                flow_str = json.dumps(req.project.akis_diyagrami.model_dump() if req.project.akis_diyagrami else {})
                cursor.execute("""
                    INSERT OR REPLACE INTO projects (
                        id, institution_id, student_id, proje_adi, prompt, badge,
                        netlist_json, arduino_kodu, akis_diyagrami_json, updated_at
                    ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, CURRENT_TIMESTAMP);
                """, (
                    entry.id,
                    current_user.get("institution_id"),
                    current_user["id"],
                    req.project.proje_adi,
                    req.prompt or "",
                    entry.badge,
                    netlist_str,
                    req.project.arduino_kodu,
                    flow_str
                ))
                conn.commit()
        except Exception as e:
            print(f"[Database Save Error] {e}")

    return entry


@app.delete("/api/projects/{project_id}")
def delete_project_endpoint(project_id: str):
    """Kayıtlı bir kullanıcı projesini siler."""
    deleted = delete_saved_project(project_id)
    return {"deleted": deleted, "id": project_id}


def check_daily_quota(user_id: str, max_daily: int = 15) -> bool:
    """Öğrencinin günlük AI tasarım kotasını denetler."""
    today = datetime.now().strftime("%Y-%m-%d")
    with get_db_connection() as conn:
        cursor = conn.cursor()
        cursor.execute("""
            INSERT INTO daily_usage_quotas (id, user_id, usage_date, request_count)
            VALUES (?, ?, ?, 1)
            ON CONFLICT(user_id, usage_date) DO UPDATE SET request_count = request_count + 1;
        """, (str(uuid.uuid4()), user_id, today))
        cursor.execute("SELECT request_count FROM daily_usage_quotas WHERE user_id = ? AND usage_date = ?;", (user_id, today))
        row = cursor.fetchone()
        conn.commit()
        if row and row[0] > max_daily:
            return False
    return True


@app.post("/api/generate-project", response_model=ProjeTasarimi)
def generate_project(
    req: GenerateRequest,
    current_user: Optional[Dict[str, Any]] = Depends(get_current_user_optional)
):
    """
    Tek Sorgu (One-Shot) AI Çağrısı:
    Hem devre kablolamasını (netlist), hem akış diyagramını (akis_adimlari), hem de Arduino C++ kodunu (arduino_kodu)
    tek bir LLM çağrısında alır, birbiriyle doğrular ve döner.
    Hata durumunda hiçbir şey sentezlemez, HTTP 502 döner.
    """
    if not req.prompt.strip():
        raise HTTPException(status_code=400, detail="Lütfen bir proje fikri yazın!")

    # Öğrenci Kotası Kontrolü (Günde en fazla 15 istek)
    if current_user and current_user.get("role") == "ogrenci":
        if not check_daily_quota(current_user["id"], max_daily=15):
            raise HTTPException(
                status_code=429,
                detail="Günlük AI devre üretim kotan doldu (15/15). Lütfen öğretmeninden destek al veya yarın tekrar dene! 🤖"
            )

    prompt_val = validate_project_prompt(req.prompt)
    if not prompt_val.is_valid:
        raise HTTPException(status_code=400, detail=prompt_val.user_message)
    
    inventory = list(req.inventory) if req.inventory else ["ARDUINO_UNO", "BREADBOARD", "LED_RED", "RESISTOR_220"]
    if "ARDUINO_UNO" not in inventory:
        inventory.append("ARDUINO_UNO")
    if "BREADBOARD" not in inventory:
        inventory.append("BREADBOARD")

    try:
        return generate_full_project_one_shot(
            prompt=req.prompt,
            inventory=inventory,
            model=req.model or "default",
            ollama_url=req.ollama_url or DEFAULT_OLLAMA_URL,
            api_key=req.api_key
        )
    except RuntimeError as e:
        raise HTTPException(status_code=502, detail=str(e))

# Alias endpoint
@app.post("/api/generate", response_model=ProjeTasarimi)
def generate_project_alias(req: GenerateRequest):
    return generate_project(req)


@app.post("/api/generate-stream")
def generate_project_stream_endpoint(
    req: GenerateRequest,
    current_user: Optional[Dict[str, Any]] = Depends(get_current_user_optional)
):
    """
    Streaming (Server-Sent Events) AI Çağrısı:
    Yapay zekanın ürettiği bileşenleri, kabloları, akış adımlarını ve C++ kodunu
    canlı olarak istemciye (frontend) akar.
    """
    if not req.prompt.strip():
        raise HTTPException(status_code=400, detail="Lütfen bir proje fikri yazın!")

    # Öğrenci Kotası Kontrolü (Günde en fazla 15 istek)
    if current_user and current_user.get("role") == "ogrenci":
        if not check_daily_quota(current_user["id"], max_daily=15):
            raise HTTPException(
                status_code=429,
                detail="Günlük AI devre üretim kotan doldu (15/15). Lütfen öğretmeninden destek al veya yarın tekrar dene! 🤖"
            )

    prompt_val = validate_project_prompt(req.prompt)
    if not prompt_val.is_valid:
        raise HTTPException(status_code=400, detail=prompt_val.user_message)

    inventory = list(req.inventory) if req.inventory else ["ARDUINO_UNO", "BREADBOARD", "LED_RED", "RESISTOR_220"]
    if "ARDUINO_UNO" not in inventory:
        inventory.append("ARDUINO_UNO")
    if "BREADBOARD" not in inventory:
        inventory.append("BREADBOARD")

    generator = generate_full_project_stream(
        prompt=req.prompt,
        inventory=inventory,
        model=req.model or "default",
        ollama_url=req.ollama_url or DEFAULT_OLLAMA_URL,
        api_key=req.api_key
    )

    return StreamingResponse(
        generator,
        media_type="text/event-stream",
        headers={
            "Cache-Control": "no-cache",
            "Connection": "keep-alive",
            "X-Accel-Buffering": "no"
        }
    )


@app.post("/api/revise-stream")
def revise_project_stream_endpoint(req: ReviseProjectRequest):
    """
    Streaming Proje Revizyon AI Çağrısı:
    Mevcut devreyi ve kodu kullanıcının revizyon isteğine göre günceller ve
    canlı olarak istemciye (frontend) akar.
    """
    if not req.revision_prompt.strip():
        raise HTTPException(status_code=400, detail="Lütfen yapılmasını istediğin değişikliği yazın!")

    prompt_val = validate_project_prompt(req.revision_prompt)
    if not prompt_val.is_valid:
        raise HTTPException(status_code=400, detail=prompt_val.user_message)

    inventory = list(req.inventory) if req.inventory else ["ARDUINO_UNO", "BREADBOARD", "LED_RED", "RESISTOR_220"]
    if "ARDUINO_UNO" not in inventory:
        inventory.append("ARDUINO_UNO")
    if "BREADBOARD" not in inventory:
        inventory.append("BREADBOARD")

    generator = generate_revised_project_stream(
        current_project=req.current_project.model_dump(by_alias=True),
        revision_prompt=req.revision_prompt,
        inventory=inventory,
        model=req.model or "default",
        ollama_url=req.ollama_url or DEFAULT_OLLAMA_URL,
        api_key=req.api_key
    )

    return StreamingResponse(
        generator,
        media_type="text/event-stream",
        headers={
            "Cache-Control": "no-cache",
            "Connection": "keep-alive",
            "X-Accel-Buffering": "no"
        }
    )


@app.post("/api/upload")
def upload_code(req: UploadRequest):
    """Arduino kodunu derler ve karta yükler."""
    if not req.code.strip():
        raise HTTPException(status_code=400, detail="Yüklenecek Arduino kodu boş olamaz!")

    result = compile_and_upload(req.code, req.port)
    return result


@app.post("/api/fix-code")
def fix_code(req: FixCodeRequest):
    """Kendi kendini iyileştirme endpoint'i."""
    fixed_code = fix_arduino_code(
        code=req.code,
        error=req.error,
        project_context=req.project_context or "",
        model=req.model
    )
    return {"fixed_code": fixed_code}


@app.get("/api/serial-events")
def stream_serial_events(port: Optional[str] = "auto", baudrate: int = 9600):
    """Canlı Serial Monitor ve görselleştirici için SSE veri akışı sağlar."""
    return StreamingResponse(
        stream_serial_port_events(port=port, baudrate=baudrate),
        media_type="text/event-stream"
    )

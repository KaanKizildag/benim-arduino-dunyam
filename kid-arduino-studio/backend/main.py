import os
from typing import List, Optional
from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import StreamingResponse
from pydantic import BaseModel
from dotenv import load_dotenv

from schemas import (
    ProjeTasarimi,
    CircuitNetlist,
    WiringDesignResponse,
    LogicDesignResponse,
    SavedProjectEntry,
    AILogEntry,
)
from ai_service import (
    generate_full_project_one_shot,
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

load_dotenv()

app = FastAPI(
    title="Kid Arduino Studio Backend",
    description="Çocuklar İçin AI Destekli Görsel Arduino Stüdyosu API",
    version="1.2.0"
)

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
def save_project_endpoint(req: SaveProjectRequest):
    """Yeni kurgulanan bir projeyi Projelerim menüsüne kaydeder."""
    return save_project_entry(
        project=req.project,
        prompt=req.prompt or "",
        project_id=req.id,
        badge=req.badge or "AI Tasarımım ✨"
    )


@app.delete("/api/projects/{project_id}")
def delete_project_endpoint(project_id: str):
    """Kayıtlı bir kullanıcı projesini siler."""
    deleted = delete_saved_project(project_id)
    return {"deleted": deleted, "id": project_id}


@app.post("/api/generate-project", response_model=ProjeTasarimi)
def generate_project(req: GenerateRequest):
    """
    Tek Sorgu (One-Shot) AI Çağrısı:
    Hem devre kablolamasını (netlist), hem akış diyagramını (akis_adimlari), hem de Arduino C++ kodunu (arduino_kodu)
    tek bir LLM çağrısında alır, birbiriyle doğrular ve döner.
    Hata durumunda hiçbir şey sentezlemez, HTTP 502 döner.
    """
    if not req.prompt.strip():
        raise HTTPException(status_code=400, detail="Lütfen bir proje fikri yazın!")
    
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

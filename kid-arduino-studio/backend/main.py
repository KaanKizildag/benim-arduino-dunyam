import os
from typing import List, Optional
from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import StreamingResponse
from pydantic import BaseModel
from dotenv import load_dotenv

from schemas import ProjeTasarimi
from ai_service import (
    MOCK_PROJECTS,
    generate_project_with_ai,
    fix_arduino_code,
    get_all_available_models,
)
from arduino_service import (
    get_connected_ports,
    compile_and_upload,
    generate_simulated_serial_events,
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


# ---------------------------------------------------------
# İstek Modelleri
# ---------------------------------------------------------

class GenerateRequest(BaseModel):
    prompt: str
    inventory: List[str]
    model: Optional[str] = None
    api_key: Optional[str] = None
    ollama_url: Optional[str] = "http://127.0.0.1:11434"

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
def list_available_models():
    """Sistemde algılanan yerel Ollama modellerini ve desteklenen bulut modellerini döner."""
    return get_all_available_models()


@app.get("/api/ports")
def list_ports():
    """Bağlı seri portları ve Arduino kartlarını listeler."""
    ports = get_connected_ports()
    return {"ports": ports}


@app.get("/api/mock-projects")
def list_mock_projects():
    """Hazır demo projelerin özet listesini döner."""
    return [
        {
            "id": "gece_lambasi",
            "title": "Akıllı Gece Bekçisi Lambası",
            "badge": "En Popüler 🌙",
            "description": "Oda kararınca kendiliğinden yanan sevimli gece lambası.",
            "parts": ["ARDUINO_UNO", "BREADBOARD", "LDR_SENSOR", "LED_RED", "RESISTOR_220"],
            "difficulty": "Başlangıç Seviyesi"
        },
        {
            "id": "park_sensoru",
            "title": "Yarasa Kulaklı Park Sensörü",
            "badge": "Eğlenceli Korna 🦇",
            "description": "Ses dalgalarıyla mesafeyi ölçüp yaklaşınca öten akıllı alarm.",
            "parts": ["ARDUINO_UNO", "BREADBOARD", "HCSR04", "BUZZER", "LED_RED"],
            "difficulty": "Kolay Seviye"
        }
    ]


@app.get("/api/mock-projects/{project_id}", response_model=ProjeTasarimi)
def get_mock_project(project_id: str):
    """Belirtilen demo projenin tüm detaylı JSON sözleşmesini döner."""
    if project_id not in MOCK_PROJECTS:
        raise HTTPException(status_code=404, detail="Proje bulunamadı")
    return MOCK_PROJECTS[project_id]


@app.post("/api/generate-project", response_model=ProjeTasarimi)
def generate_project(req: GenerateRequest):
    """Çocuğun Türkçe fikrini, envanterini ve seçilen modeli kullanarak projeyi üretir."""
    if not req.prompt.strip():
        raise HTTPException(status_code=400, detail="Lütfen bir proje fikri yazın!")
    
    inventory = req.inventory if req.inventory else ["ARDUINO_UNO", "BREADBOARD", "LED_RED", "RESISTOR_220"]
    if "ARDUINO_UNO" not in inventory:
        inventory.append("ARDUINO_UNO")
    if "BREADBOARD" not in inventory:
        inventory.append("BREADBOARD")

    project = generate_project_with_ai(
        prompt=req.prompt,
        inventory=inventory,
        model=req.model,
        api_key=req.api_key,
        ollama_url=req.ollama_url or "http://127.0.0.1:11434"
    )
    return project

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
def stream_serial_events(port: Optional[str] = "simulated"):
    """Canlı sensör ibresi için SSE veri akışı sağlar."""
    return StreamingResponse(
        generate_simulated_serial_events(),
        media_type="text/event-stream"
    )

import json
import os
import re
from typing import List, Optional, Dict, Any
import httpx
from dotenv import load_dotenv

from schemas import (
    ProjeTasarimi,
    BaglantiAdimi,
    AkisAdimi,
    CircuitNetlist,
    NetlistComponent,
    NetlistConnection
)

load_dotenv()

# ---------------------------------------------------------
# Hazır Mock Demo Projeler (Netlist Şemasına Tam Uyumlu)
# ---------------------------------------------------------

MOCK_PROJECTS: Dict[str, ProjeTasarimi] = {
    # 1. Akıllı Gece Lambası (Senaryo A: LED + Direnç + LDR)
    "gece_lambasi": ProjeTasarimi(
        proje_adi="Akıllı Gece Bekçisi Lambası 🌙",
        karsilama_mesaji="Harika bir fikir! Odan karardığında sihir gibi kendiliğinden yanan akıllı bir gece lambası yapıyoruz. 🌙✨",
        gerekli_parcalar=["ARDUINO_UNO", "BREADBOARD", "LDR_SENSOR", "LED_RED", "RESISTOR_220"],
        netlist=CircuitNetlist(
            board="arduino-uno",
            components=[
                NetlistComponent(id="r1", type="wokwi-resistor", props={"value": "220"}, label="220Ω Direnç"),
                NetlistComponent(id="led1", type="wokwi-led", props={"color": "red"}, label="Kırmızı LED"),
                NetlistComponent(id="ldr1", type="wokwi-photoresistor-sensor", label="LDR Işık Sensörü")
            ],
            connections=[
                NetlistConnection(from_pin="uno.D13", to_pin="r1.1", color="orange"),
                NetlistConnection(from_pin="r1.2", to_pin="led1.A", color="red"),
                NetlistConnection(from_pin="led1.C", to_pin="GND", color="black"),
                NetlistConnection(from_pin="ldr1.VCC", to_pin="5V", color="red"),
                NetlistConnection(from_pin="ldr1.GND", to_pin="GND", color="black"),
                NetlistConnection(from_pin="ldr1.AO", to_pin="uno.A0", color="green")
            ]
        ),
        baglanti_adimlari=[
            BaglantiAdimi(
                adim_no=1,
                talimat="Arduino D13 pininden 220Ω Direncin 1. ucuna kablo bağla.",
                ipucu="Direnç LED'in fazla akımdan yanmasını önler.",
                kaynak_parca="ARDUINO_UNO",
                kaynak_pin="D13",
                hedef_parca="BREADBOARD",
                hedef_pin="2A",
                kablo_rengi="#F97316"
            ),
            BaglantiAdimi(
                adim_no=2,
                talimat="220Ω Direnç ile Kırmızı LED anot bacağını breadboard üzerinde aynı sütunda buluştur.",
                ipucu="Breadboard dikey sütunu üzerinden kablosuz bağlanırlar!",
                kaynak_parca="BREADBOARD",
                kaynak_pin="6C",
                hedef_parca="BREADBOARD",
                hedef_pin="6E",
                kablo_rengi="#EF4444"
            ),
            BaglantiAdimi(
                adim_no=3,
                talimat="LED'in katot (kısa) bacağını GND hattına bağla.",
                ipucu="GND devreyi tamamlar.",
                kaynak_parca="BREADBOARD",
                kaynak_pin="7E",
                hedef_parca="BREADBOARD",
                hedef_pin="GND",
                kablo_rengi="#1F2937"
            )
        ],
        akis_adimlari=AkisAdimi(
            gozlemle="LDR ışık sensörü odadaki karanlık seviyesini sürekli takip eder.",
            karar_ver="Oda karardı mı? (Ölçülen ışık 400'ün altına düştü mü?)",
            evet_sonucu="Evet, oda karanlık! D13 pinine enerji gönder ve Kırmızı Lambayı Yak! 💡",
            hayir_sonucu="Hayır, oda aydınlık. Enerjiyi kes ve Lambayı Söndür! ☀️"
        ),
        arduino_kodu="""// Kid Arduino Studio - Akıllı Gece Lambası
const int LDR_PIN = A0;
const int LED_PIN = 13;
const int KARANLIK_ESIK = 400;

void setup() {
  pinMode(LED_PIN, OUTPUT);
  Serial.begin(9600);
  Serial.println("Gece Lambasi Devrede!");
}

void loop() {
  int isik = analogRead(LDR_PIN);
  Serial.print("Isik: ");
  Serial.println(isik);

  if (isik < KARANLIK_ESIK) {
    digitalWrite(LED_PIN, HIGH);
  } else {
    digitalWrite(LED_PIN, LOW);
  }
  delay(100);
}
""",
        guvenlik_notu="LED'in zarar görmemesi için araya mutlaka 220 Ohm direnç koyduk."
    ),

    # 2. 3 LED'li Trafik Lambası (Senaryo B)
    "trafik_isiklari": ProjeTasarimi(
        proje_adi="Akıllı Şehir Trafik Lambası 🚦",
        karsilama_mesaji="Sırayla yanan kırmızı, sarı ve yeşil lambalarla trafiği yöneteceğiz! 🚦🚗",
        gerekli_parcalar=["ARDUINO_UNO", "BREADBOARD", "LED_RED", "LED_YELLOW", "LED_GREEN", "RESISTOR_220"],
        netlist=CircuitNetlist(
            board="arduino-uno",
            components=[
                NetlistComponent(id="r1", type="wokwi-resistor", props={"value": "220"}, label="Kırmızı Direnç"),
                NetlistComponent(id="led1", type="wokwi-led", props={"color": "red"}, label="Kırmızı LED"),
                NetlistComponent(id="r2", type="wokwi-resistor", props={"value": "220"}, label="Sarı Direnç"),
                NetlistComponent(id="led2", type="wokwi-led", props={"color": "yellow"}, label="Sarı LED"),
                NetlistComponent(id="r3", type="wokwi-resistor", props={"value": "220"}, label="Yeşil Direnç"),
                NetlistComponent(id="led3", type="wokwi-led", props={"color": "green"}, label="Yeşil LED")
            ],
            connections=[
                NetlistConnection(from_pin="uno.D12", to_pin="r1.1", color="red"),
                NetlistConnection(from_pin="r1.2", to_pin="led1.A", color="red"),
                NetlistConnection(from_pin="led1.C", to_pin="GND", color="black"),
                NetlistConnection(from_pin="uno.D11", to_pin="r2.1", color="yellow"),
                NetlistConnection(from_pin="r2.2", to_pin="led2.A", color="yellow"),
                NetlistConnection(from_pin="led2.C", to_pin="GND", color="black"),
                NetlistConnection(from_pin="uno.D10", to_pin="r3.1", color="green"),
                NetlistConnection(from_pin="r3.2", to_pin="led3.A", color="green"),
                NetlistConnection(from_pin="led3.C", to_pin="GND", color="black")
            ]
        ),
        baglanti_adimlari=[],
        akis_adimlari=AkisAdimi(
            gozlemle="Trafik lambası zaman sayacını sürekli izler.",
            karar_ver="Hangi lambanın yanma sırası geldi?",
            evet_sonucu="Sırası gelen lambayı yak!",
            hayir_sonucu="Diğer lambaları söndür ve bekle!"
        ),
        arduino_kodu="""// Kid Arduino Studio - Trafik Lambasi
const int RED_LED = 12;
const int YELLOW_LED = 11;
const int GREEN_LED = 10;

void setup() {
  pinMode(RED_LED, OUTPUT);
  pinMode(YELLOW_LED, OUTPUT);
  pinMode(GREEN_LED, OUTPUT);
}

void loop() {
  digitalWrite(RED_LED, HIGH);
  delay(3000);
  digitalWrite(YELLOW_LED, HIGH);
  delay(1000);
  digitalWrite(RED_LED, LOW);
  digitalWrite(YELLOW_LED, LOW);
  digitalWrite(GREEN_LED, HIGH);
  delay(3000);
  digitalWrite(GREEN_LED, LOW);
}
"""
    ),

    # 3. Akıllı Park Sensörü
    "park_sensoru": ProjeTasarimi(
        proje_adi="Yarasa Kulaklı Akıllı Park Sensörü 🦇",
        karsilama_mesaji="Süper bir fikir! Tıpkı yarasalar gibi ses dalgaları fırlatarak yaklaşan nesneleri fark eden bir alarm yapıyoruz! 🦇🚗",
        gerekli_parcalar=["ARDUINO_UNO", "BREADBOARD", "HCSR04", "BUZZER", "LED_RED"],
        netlist=CircuitNetlist(
            board="arduino-uno",
            components=[
                NetlistComponent(id="hcsr1", type="wokwi-hc-sr04", label="Mesafe Sensörü"),
                NetlistComponent(id="buzzer1", type="wokwi-buzzer", label="Uyarı Buzzerı"),
                NetlistComponent(id="r1", type="wokwi-resistor", props={"value": "220"}, label="220Ω Direnç"),
                NetlistComponent(id="led1", type="wokwi-led", props={"color": "red"}, label="Kırmızı LED")
            ],
            connections=[
                NetlistConnection(from_pin="hcsr1.VCC", to_pin="5V", color="red"),
                NetlistConnection(from_pin="hcsr1.GND", to_pin="GND", color="black"),
                NetlistConnection(from_pin="hcsr1.TRIG", to_pin="uno.D9", color="blue"),
                NetlistConnection(from_pin="hcsr1.ECHO", to_pin="uno.D10", color="green"),
                NetlistConnection(from_pin="buzzer1.1", to_pin="uno.D8", color="orange"),
                NetlistConnection(from_pin="buzzer1.2", to_pin="GND", color="black"),
                NetlistConnection(from_pin="uno.D13", to_pin="r1.1", color="red"),
                NetlistConnection(from_pin="r1.2", to_pin="led1.A", color="red"),
                NetlistConnection(from_pin="led1.C", to_pin="GND", color="black")
            ]
        ),
        baglanti_adimlari=[],
        akis_adimlari=AkisAdimi(
            gozlemle="Ultrasonik sensör önüne gelen engellerin mesafesini santimetre olarak dinler.",
            karar_ver="Önünde bir engel çok yaklaştı mı? (Mesafe 15 cm'den az mı?)",
            evet_sonucu="Evet, tehlike var! D8 pinini tetikle ve Korna ile Bip Bip uyar! 🔊",
            hayir_sonucu="Hayır, yol açık ve güvenli. Kornayı sessiz tut! 🚗"
        ),
        arduino_kodu="""// Kid Arduino Studio - Akıllı Park Sensörü
const int TRIG_PIN = 9;
const int ECHO_PIN = 10;
const int BUZZER_PIN = 8;
const int LED_PIN = 13;

void setup() {
  pinMode(TRIG_PIN, OUTPUT);
  pinMode(ECHO_PIN, INPUT);
  pinMode(BUZZER_PIN, OUTPUT);
  pinMode(LED_PIN, OUTPUT);
  Serial.begin(9600);
}

void loop() {
  digitalWrite(TRIG_PIN, LOW);
  delayMicroseconds(2);
  digitalWrite(TRIG_PIN, HIGH);
  delayMicroseconds(10);
  digitalWrite(TRIG_PIN, LOW);

  long sure = pulseIn(ECHO_PIN, HIGH);
  int mesafe = sure * 0.034 / 2;

  if (mesafe > 0 && mesafe < 15) {
    digitalWrite(BUZZER_PIN, HIGH);
    digitalWrite(LED_PIN, HIGH);
    delay(80);
    digitalWrite(BUZZER_PIN, LOW);
    digitalWrite(LED_PIN, LOW);
    delay(80);
  } else {
    digitalWrite(BUZZER_PIN, LOW);
    digitalWrite(LED_PIN, LOW);
    delay(100);
  }
}
"""
    ),

    # 4. Buton + Servo Motor (Senaryo C)
    "buton_servo": ProjeTasarimi(
        proje_adi="Otomatik Robotik Kapı Bariyeri 🦾",
        karsilama_mesaji="Butona basıldığında açılan akıllı bir bariyer kolu tasarlıyoruz! 🦾✨",
        gerekli_parcalar=["ARDUINO_UNO", "BREADBOARD", "PUSH_BUTTON", "RESISTOR_10K", "SERVO_SG90"],
        netlist=CircuitNetlist(
            board="arduino-uno",
            components=[
                NetlistComponent(id="btn1", type="wokwi-pushbutton", props={"color": "red"}, label="Açma Butonu"),
                NetlistComponent(id="r1", type="wokwi-resistor", props={"value": "10000"}, label="10kΩ Pull-down Direnç"),
                NetlistComponent(id="servo1", type="wokwi-servo", label="SG90 Servo Motor")
            ],
            connections=[
                NetlistConnection(from_pin="btn1.1", to_pin="5V", color="red"),
                NetlistConnection(from_pin="btn1.2", to_pin="uno.D2", color="blue"),
                NetlistConnection(from_pin="btn1.2", to_pin="r1.1", color="blue"),
                NetlistConnection(from_pin="r1.2", to_pin="GND", color="black"),
                NetlistConnection(from_pin="servo1.V+", to_pin="5V", color="red"),
                NetlistConnection(from_pin="servo1.GND", to_pin="GND", color="black"),
                NetlistConnection(from_pin="servo1.PWM", to_pin="uno.D9", color="orange")
            ]
        ),
        baglanti_adimlari=[],
        akis_adimlari=AkisAdimi(
            gozlemle="Butona basılıp basılmadığını sürekli gözlemle.",
            karar_ver="Butona tıklandı mı?",
            evet_sonucu="Evet! Servo motoru 90 derece döndür ve kapıyı aç! 🚪",
            hayir_sonucu="Hayır, kapıyı kapalı tut (0 derece)."
        ),
        arduino_kodu="""// Kid Arduino Studio - Buton ve Servo Kapi
#include <Servo.h>

const int BUTTON_PIN = 2;
const int SERVO_PIN = 9;
Servo myServo;

void setup() {
  pinMode(BUTTON_PIN, INPUT);
  myServo.attach(SERVO_PIN);
  myServo.write(0);
}

void loop() {
  int buttonState = digitalRead(BUTTON_PIN);
  if (buttonState == HIGH) {
    myServo.write(90);
    delay(2000);
    myServo.write(0);
  }
  delay(50);
}
"""
    )
}

# ---------------------------------------------------------
# Pedagojik AI Sistem Promptu (LLM Koordinat Yasağı ile Netlist)
# ---------------------------------------------------------

SYSTEM_PROMPT = """Sen 8-14 yaş arasındaki çocuklar için tasarlanmış bir 'Arduino Robot Arkadaşı'sın.
GÖREVİN: Çocuğun hayalindeki projeyi ve elindeki parçaları inceleyerek Arduino projesini standart Netlist JSON olarak tasarlamak.

KESİN KURAL (LLM KOORDİNAT YASAĞI):
ASLA breadboard deliği (5A, 12C, A1 vb.) veya piksel koordinatı üretme! Fiziksel yerleşimi, sütun dağıtımını ve kablo çizimini sistemin deterministik Auto-Layout motoru yapacaktır. Sen yalnızca mantıksal bağlantıları (Netlist) üreteceksin.

NETLIST ŞEMASI:
1. "board": "arduino-uno"
2. "components": Devredeki fiziksel parçalar:
   - "id": Benzersiz kimlik (örn: led1, r1, ldr1, buzzer1, btn1, servo1)
   - "type": Wokwi eleman tipi (wokwi-led, wokwi-resistor, wokwi-photoresistor-sensor, wokwi-buzzer, wokwi-pushbutton, wokwi-servo, wokwi-hc-sr04, wokwi-potentiometer)
   - "props": Özellikler (örn: {"color": "red"}, {"value": "220"})
   - "label": Çocuk dostu Türkçe isim (örn: "Kırmızı LED", "220Ω Direnç")

3. "connections": Mantıksal pin bağlantıları (from -> to):
   - Arduino pinleri: uno.D13, uno.D12, uno.D9, uno.D2, uno.A0
   - Güç hatları: 5V, GND
   - Bileşen pinleri:
     - wokwi-resistor: r1.1, r1.2
     - wokwi-led: led1.A (Anot), led1.C (Katot)
     - wokwi-photoresistor-sensor: ldr1.VCC, ldr1.GND, ldr1.AO
     - wokwi-buzzer: buzzer1.1, buzzer1.2
     - wokwi-pushbutton: btn1.1, btn1.2
     - wokwi-servo: servo1.V+, servo1.GND, servo1.PWM
     - wokwi-hc-sr04: hcsr1.VCC, hcsr1.GND, hcsr1.TRIG, hcsr1.ECHO

JSON ÇIKTI FORMATI:
{
  "proje_adi": "string",
  "karsilama_mesaji": "string",
  "gerekli_parcalar": ["ARDUINO_UNO", "BREADBOARD", ...],
  "netlist": {
    "board": "arduino-uno",
    "components": [
      { "id": "r1", "type": "wokwi-resistor", "props": { "value": "220" }, "label": "220Ω Direnç" },
      { "id": "led1", "type": "wokwi-led", "props": { "color": "red" }, "label": "Kırmızı LED" }
    ],
    "connections": [
      { "from": "uno.D13", "to": "r1.1", "color": "orange" },
      { "from": "r1.2", "to": "led1.A", "color": "red" },
      { "from": "led1.C", "to": "GND", "color": "black" }
    ]
  },
  "akis_adimlari": {
    "gozlemle": "string",
    "karar_ver": "string",
    "evet_sonucu": "string",
    "hayir_sonucu": "string"
  },
  "arduino_kodu": "string",
  "guvenlik_notu": "string"
}
"""

def clean_llm_json_response(raw_text: str) -> str:
    """LLM çıktısından JSON'ı temiz bir şekilde ayıklar."""
    text = raw_text.strip()
    text = re.sub(r"<think>.*?</think>", "", text, flags=re.DOTALL).strip()
    text = re.sub(r"^```(?:json)?\s*", "", text).strip()
    text = re.sub(r"```$", "", text).strip()
    
    start = text.find("{")
    end = text.rfind("}")
    if start != -1 and end != -1 and end > start:
        return text[start:end+1]
        
    return text

def get_installed_ollama_models(ollama_url: str = "http://127.0.0.1:11434") -> List[Dict[str, Any]]:
    """Yerel Ollama sunucusundaki kurulu modelleri döner."""
    try:
        res = httpx.get(f"{ollama_url}/api/tags", timeout=3.0)
        if res.status_code == 200:
            data = res.json()
            models = []
            for m in data.get("models", []):
                name = m.get("name")
                if not name or "embed" in name:
                    continue
                size_mb = round(m.get("size", 0) / (1024 * 1024), 1)
                size_str = f"{size_mb} MB" if size_mb < 1000 else f"{round(size_mb/1024, 2)} GB"
                models.append({
                    "id": f"ollama/{name}",
                    "name": f"{name} ({size_str})",
                    "raw_name": name,
                    "provider": "local",
                    "category": "Yerel (Ollama)",
                    "badge": "💻 Yerel"
                })
            return models
    except Exception:
        pass
    return []

def get_all_available_models(ollama_url: str = "http://127.0.0.1:11434") -> Dict[str, Any]:
    """Tüm yerel ve bulut modelleri ve yapılandırma durumlarını listeler."""
    local_models = get_installed_ollama_models(ollama_url)
    ollama_running = len(local_models) > 0

    cloud_models = [
        {"id": "gemini/gemini-2.0-flash", "name": "Gemini 2.0 Flash (Hızlı & Yetenekli)", "provider": "gemini", "category": "Google Gemini", "badge": "☁️ Bulut"},
        {"id": "gemini/gemini-1.5-flash", "name": "Gemini 1.5 Flash (Dengeli)", "provider": "gemini", "category": "Google Gemini", "badge": "☁️ Bulut"},
        {"id": "gemini/gemini-1.5-pro", "name": "Gemini 1.5 Pro (Gelişmiş Düşünme)", "provider": "gemini", "category": "Google Gemini", "badge": "☁️ Bulut"},
        {"id": "gpt-4o-mini", "name": "GPT-4o Mini (Hızlı & Ekonomik)", "provider": "openai", "category": "OpenAI", "badge": "☁️ Bulut"},
        {"id": "gpt-4o", "name": "GPT-4o (Amiral Gemisi)", "provider": "openai", "category": "OpenAI", "badge": "☁️ Bulut"},
        {"id": "claude-3-5-haiku-20241022", "name": "Claude 3.5 Haiku (Hızlı & Canlı)", "provider": "anthropic", "category": "Anthropic Claude", "badge": "☁️ Bulut"},
        {"id": "claude-3-5-sonnet-20241022", "name": "Claude 3.5 Sonnet (Kodlama Uzmanı)", "provider": "anthropic", "category": "Anthropic Claude", "badge": "☁️ Bulut"},
    ]

    configured_keys = {
        "gemini": bool(os.getenv("GEMINI_API_KEY")),
        "openai": bool(os.getenv("OPENAI_API_KEY")),
        "anthropic": bool(os.getenv("ANTHROPIC_API_KEY")),
    }

    default_model = "ollama/qwen2.5-coder:1.5b" if any(m["id"] == "ollama/qwen2.5-coder:1.5b" for m in local_models) else (
        local_models[0]["id"] if local_models else "gemini/gemini-1.5-flash"
    )

    return {
        "ollama_active": ollama_running,
        "default_model": default_model,
        "local_models": local_models,
        "cloud_models": cloud_models,
        "configured_keys": configured_keys
    }

def generate_with_ollama(model_name: str, prompt: str, inventory: List[str], ollama_url: str = "http://127.0.0.1:11434") -> ProjeTasarimi:
    clean_model = model_name.replace("ollama/", "")
    user_prompt = f"""KULLANICI PROJE HAYALİ:
"{prompt}"

KULLANICININ MALZEME ÇANTASI (ENVANTER):
{json.dumps(inventory, ensure_ascii=False)}

Yukarıdaki hayali ve envanteri kullanarak standart Netlist şeması ile tam bir Arduino projesi tasarla."""

    try:
        res = httpx.post(
            f"{ollama_url}/api/generate",
            json={
                "model": clean_model,
                "prompt": f"{SYSTEM_PROMPT}\n\n{user_prompt}",
                "stream": False,
                "format": "json"
            },
            timeout=45.0
        )
        if res.status_code == 200:
            raw_response = res.json().get("response", "")
            cleaned = clean_llm_json_response(raw_response)
            data = json.loads(cleaned)
            return ProjeTasarimi(**data)
    except Exception as e:
        print(f"Ollama üretimi başarısız: {e}")

    # Fallback to smart matching mock project
    return select_best_mock_project(prompt)

def generate_with_litellm(model_name: str, prompt: str, inventory: List[str], api_key: Optional[str] = None) -> ProjeTasarimi:
    from litellm import completion

    user_prompt = f"""KULLANICI PROJE HAYALİ:
"{prompt}"

KULLANICININ MALZEME ÇANTASI:
{json.dumps(inventory, ensure_ascii=False)}

Standart Netlist şeması ile tam bir Arduino projesi üret."""

    try:
        response = completion(
            model=model_name,
            messages=[
                {"role": "system", "content": SYSTEM_PROMPT},
                {"role": "user", "content": user_prompt}
            ],
            response_format={"type": "json_object"},
            api_key=api_key,
            temperature=0.3
        )
        content = response.choices[0].message.content
        cleaned = clean_llm_json_response(content)
        data = json.loads(cleaned)
        return ProjeTasarimi(**data)
    except Exception as e:
        print(f"LiteLLM üretimi başarısız: {e}")

    return select_best_mock_project(prompt)

def select_best_mock_project(prompt: str) -> ProjeTasarimi:
    p = (prompt or "").lower()
    if any(k in p for k in ["trafik", "lamba", "isik", "kirmizi sari"]):
        return MOCK_PROJECTS["trafik_isiklari"]
    if any(k in p for k in ["park", "mesafe", "yarasa", "hcsr04", "korna", "engel"]):
        return MOCK_PROJECTS["park_sensoru"]
    if any(k in p for k in ["buton", "servo", "kapi", "bariyer", "motor"]):
        return MOCK_PROJECTS["buton_servo"]
    return MOCK_PROJECTS["gece_lambasi"]

def generate_project_idea(
    prompt: str,
    inventory: List[str],
    model: str = "default",
    ollama_url: str = "http://127.0.0.1:11434",
    api_key: Optional[str] = None
) -> ProjeTasarimi:
    models_info = get_all_available_models(ollama_url)
    chosen_model = model if model != "default" and model is not None else models_info["default_model"]

    if chosen_model.startswith("ollama/") or chosen_model == "local":
        if models_info["ollama_active"]:
            return generate_with_ollama(chosen_model, prompt, inventory, ollama_url)
        else:
            return select_best_mock_project(prompt)

    if not api_key:
        if "gemini" in chosen_model:
            api_key = os.getenv("GEMINI_API_KEY")
        elif "gpt" in chosen_model:
            api_key = os.getenv("OPENAI_API_KEY")
        elif "claude" in chosen_model:
            api_key = os.getenv("ANTHROPIC_API_KEY")

    if api_key:
        return generate_with_litellm(chosen_model, prompt, inventory, api_key)

    return select_best_mock_project(prompt)

# Geriye dönük takma ad
generate_project_with_ai = generate_project_idea

def fix_arduino_code(code: str, error: str, project_context: str = "", model: Optional[str] = None) -> str:
    """Derleme veya yükleme hatasını analiz edip düzelten kendini iyileştirme fonksiyonu."""
    chosen_model = model or "gemini/gemini-1.5-flash"
    prompt = f"""Aşağıdaki Arduino Uno kodunda derleme/yükleme hatası oluştu.
LÜTFEN HATAYI DÜZELT VE SADECE DÜZELTİLMİŞ C++ ARDUINO KODUNU DÖNDÜR.

HATALI KOD:
```cpp
{code}
```

HATA MESAJI:
{error}

PROJE BAĞLAMI:
{project_context}
"""
    try:
        import litellm
        res = litellm.completion(
            model=chosen_model,
            messages=[{"role": "user", "content": prompt}],
            temperature=0.1
        )
        out = res.choices[0].message.content.strip()
        out = re.sub(r"^```(?:cpp)?\s*", "", out).strip()
        out = re.sub(r"```$", "", out).strip()
        return out
    except Exception as e:
        print(f"[Self-Healing Hatası] Kod düzeltilemedi ({e}). Orijinal kod korunuyor.")
        return code


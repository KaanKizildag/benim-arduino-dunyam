import json
import os
import re
from typing import List, Optional, Literal, Dict, Any
from pydantic import BaseModel, Field
import httpx

# ---------------------------------------------------------
# Pydantic Veri Sözleşmesi (Data Contract)
# ---------------------------------------------------------

class ConnectionEndpoint(BaseModel):
    parca: str = Field(description="Bileşenin adı (örn: ARDUINO_UNO, LED_RED, HCSR04)")
    pin: str = Field(description="Bileşen üzerindeki pin (örn: D13, A0, 5V, GND, ANODE, ECHO)")

class BaglantiAdimi(BaseModel):
    adim_no: int = Field(description="Adım sırası (1'den başlar)")
    talimat: str = Field(description="Çocuğa yönelik sade, samimi montaj talimatı")
    ipucu: str = Field(description="Çocuğun aklında kalacak eğlenceli ve pratik ipucu")
    kaynak: ConnectionEndpoint = Field(description="Kablonun başladığı parça ve pin")
    hedef: ConnectionEndpoint = Field(description="Kablonun bağlandığı parça ve pin")
    kablo_rengi: str = Field(description="Kablonun görsel rengi (örn: #EF4444, #3B82F6, #1F2937, #10B981, #F59E0B)")

class DusunmeAdimi(BaseModel):
    tip: Literal["BASLANGIC", "DONGU", "EGER", "YAP"] = Field(
        description="Düşünme kartının tipi: BASLANGIC, DONGU, EGER, YAP"
    )
    baslik: str = Field(description="Kartın Türkçe başlığı")
    aciklama: str = Field(description="Kartın ne yaptığını anlatan sade Türkçe açıklama")

class ProjectResponse(BaseModel):
    proje_adi: str = Field(description="Projenin heyecan verici Türkçe adı")
    karsilama_mesaji: str = Field(description="Çocuğu cesaretlendiren neşeli karşılama mesajı")
    gerekli_parcalar: List[str] = Field(description="Projede kullanılan parçaların listesi")
    baglanti_adimlari: List[BaglantiAdimi] = Field(description="Adım adım kablo bağlantıları")
    dusunme_adimlari: List[DusunmeAdimi] = Field(description="Kodun mantığını açıklayan düşünme kartları")
    arduino_kodu: str = Field(description="arduino:avr:uno kartı için derlenebilir tam C++ kodu")
    guvenlik_notu: str = Field(description="Elektronik ve güvenlik hakkında çocuğa dostça hatırlatma")


# ---------------------------------------------------------
# Hazır Mock Demo Projeler
# ---------------------------------------------------------

MOCK_PROJECTS = {
    "gece_lambasi": ProjectResponse(
        proje_adi="Akıllı Gece Bekçisi Lambası",
        karsilama_mesaji="Harika bir fikir! Odan karardığında sihir gibi kendiliğinden yanan akıllı bir gece lambası yapıyoruz. 🌙✨",
        gerekli_parcalar=["ARDUINO_UNO", "LDR_SENSOR", "LED_RED", "RESISTOR_220"],
        baglanti_adimlari=[
            BaglantiAdimi(
                adim_no=1,
                talimat="Kırmızı LED'in uzun bacağını (artı enerji) Arduino üzerindeki D13 numaralı dijital pine tak.",
                ipucu="Uzun bacak her zaman artı (+) enerjidir, unutma!",
                kaynak=ConnectionEndpoint(parca="LED_RED", pin="ANODE"),
                hedef=ConnectionEndpoint(parca="ARDUINO_UNO", pin="D13"),
                kablo_rengi="#EF4444"
            ),
            BaglantiAdimi(
                adim_no=2,
                talimat="Kırmızı LED'in kısa bacağını (eksi enerji) 220 Ohm direncin bir ucuna bağla.",
                ipucu="Direnç LED'e fazla elektrik akmasını önleyip onu korur!",
                kaynak=ConnectionEndpoint(parca="LED_RED", pin="CATHODE"),
                hedef=ConnectionEndpoint(parca="RESISTOR_220", pin="PIN1"),
                kablo_rengi="#3B82F6"
            ),
            BaglantiAdimi(
                adim_no=3,
                talimat="Direncin diğer boşta kalan ucunu Arduino'daki GND (Toprak/Eksi) pinine bağla.",
                ipucu="GND, devrelerin elektrik dönüş yoludur. Eksi (-) kutup burasıdır.",
                kaynak=ConnectionEndpoint(parca="RESISTOR_220", pin="PIN2"),
                hedef=ConnectionEndpoint(parca="ARDUINO_UNO", pin="GND"),
                kablo_rengi="#1F2937"
            ),
            BaglantiAdimi(
                adim_no=4,
                talimat="LDR ışık sensörünün bir bacağını Arduino'nun 5V (güç) pinine bağla.",
                ipucu="LDR çalışmak için 5 Volt enerjiye ihtiyaç duyar.",
                kaynak=ConnectionEndpoint(parca="LDR_SENSOR", pin="PIN1"),
                hedef=ConnectionEndpoint(parca="ARDUINO_UNO", pin="5V"),
                kablo_rengi="#EF4444"
            ),
            BaglantiAdimi(
                adim_no=5,
                talimat="LDR ışık sensörünün diğer bacağını Arduino üzerindeki A0 (Analog 0) bilgi pinine tak.",
                ipucu="A0 pini, odanın ne kadar aydınlık veya karanlık olduğunu sayı olarak dinler.",
                kaynak=ConnectionEndpoint(parca="LDR_SENSOR", pin="PIN2"),
                hedef=ConnectionEndpoint(parca="ARDUINO_UNO", pin="A0"),
                kablo_rengi="#10B981"
            )
        ],
        dusunme_adimlari=[
            DusunmeAdimi(
                tip="BASLANGIC",
                baslik="Hazırlık Yap (setup)",
                aciklama="Arduino uyandığında D13 pinini lamba çıkışı olarak ayarla ve sensörü dinlemeye başla."
            ),
            DusunmeAdimi(
                tip="DONGU",
                baslik="Sürekli Gözlemle (loop)",
                aciklama="Arduino durmaksızın A0 pininden odanın aydınlık seviyesini ölçer."
            ),
            DusunmeAdimi(
                tip="EGER",
                baslik="Eğer Oda Karardıysa",
                aciklama="Işık değeri 400'ün altına düştüğünde odanın karanlık olduğunu anla."
            ),
            DusunmeAdimi(
                tip="YAP",
                baslik="Lambayı Yak!",
                aciklama="D13 pinine elektrik vererek kırmızı LED lambayı yak. Hava aydınlanınca lambayı söndür."
            )
        ],
        arduino_kodu="""// Kid Arduino Studio - Akıllı Gece Lambası
const int LDR_PIN = A0;
const int LED_PIN = 13;
const int KARANLIK_ESIK = 400;

void setup() {
  pinMode(LED_PIN, OUTPUT);
  Serial.begin(9600);
  Serial.println("Gece Lambasi Sistemi Baslatildi!");
}

void loop() {
  int isik_degeri = analogRead(LDR_PIN);
  
  Serial.print("Isik Seviyesi: ");
  Serial.println(isik_degeri);
  
  if (isik_degeri < KARANLIK_ESIK) {
    digitalWrite(LED_PIN, HIGH);
  } else {
    digitalWrite(LED_PIN, LOW);
  }
  
  delay(100);
}
""",
        guvenlik_notu="LED'in fazla akımdan dolayı zarar görmemesi için araya mutlaka 220 Ohm direnç koyduk."
    ),

    "park_sensoru": ProjectResponse(
        proje_adi="Yarasa Kulaklı Akıllı Park Sensörü",
        karsilama_mesaji="Süper bir fikir! Tıpkı yarasalar gibi ses dalgaları fırlatarak yaklaşan nesneleri fark eden bir alarm yapıyoruz! 🦇🚗",
        gerekli_parcalar=["ARDUINO_UNO", "HCSR04", "BUZZER", "LED_RED"],
        baglanti_adimlari=[
            BaglantiAdimi(
                adim_no=1,
                talimat="Ultrasonik mesafe sensörünün VCC bacağını Arduino'nun 5V pinine bağla.",
                ipucu="VCC, sensörün 5 Volt enerji beslemesidir.",
                kaynak=ConnectionEndpoint(parca="HCSR04", pin="VCC"),
                hedef=ConnectionEndpoint(parca="ARDUINO_UNO", pin="5V"),
                kablo_rengi="#EF4444"
            ),
            BaglantiAdimi(
                adim_no=2,
                talimat="Ultrasonik mesafe sensörünün GND bacağını Arduino'nun GND pinine bağla.",
                ipucu="GND elektrik akımının dönüş yoludur.",
                kaynak=ConnectionEndpoint(parca="HCSR04", pin="GND"),
                hedef=ConnectionEndpoint(parca="ARDUINO_UNO", pin="GND"),
                kablo_rengi="#1F2937"
            ),
            BaglantiAdimi(
                adim_no=3,
                talimat="Sensörün TRIG (Tetik) bacağını Arduino D9 dijital pinine bağla.",
                ipucu="TRIG bacağı minik ses dalgalarını fırlatır.",
                kaynak=ConnectionEndpoint(parca="HCSR04", pin="TRIG"),
                hedef=ConnectionEndpoint(parca="ARDUINO_UNO", pin="D9"),
                kablo_rengi="#3B82F6"
            ),
            BaglantiAdimi(
                adim_no=4,
                talimat="Sensörün ECHO (Yankı) bacağını Arduino D10 dijital pinine bağla.",
                ipucu="ECHO bacağı geri dönen sesi dinler.",
                kaynak=ConnectionEndpoint(parca="HCSR04", pin="ECHO"),
                hedef=ConnectionEndpoint(parca="ARDUINO_UNO", pin="D10"),
                kablo_rengi="#10B981"
            ),
            BaglantiAdimi(
                adim_no=5,
                talimat="Buzzer'ın artı (+) bacağını Arduino'nun D8 dijital pinine bağla.",
                ipucu="Buzzer küçük bir kornadır; D8 pininden gelen sinyalle öter.",
                kaynak=ConnectionEndpoint(parca="BUZZER", pin="VCC"),
                hedef=ConnectionEndpoint(parca="ARDUINO_UNO", pin="D8"),
                kablo_rengi="#F59E0B"
            ),
            BaglantiAdimi(
                adim_no=6,
                talimat="Buzzer'ın eksi (-) bacağını Arduino'nun GND pinine bağla.",
                ipucu="Devreyi tamamlamak için eksi kutbu GND'ye bağlıyoruz.",
                kaynak=ConnectionEndpoint(parca="BUZZER", pin="GND"),
                hedef=ConnectionEndpoint(parca="ARDUINO_UNO", pin="GND"),
                kablo_rengi="#1F2937"
            )
        ],
        dusunme_adimlari=[
            DusunmeAdimi(
                tip="BASLANGIC",
                baslik="Sensör ve Kornayı Hazırla (setup)",
                aciklama="D9'u ses fırlatıcı, D10'u dinleyici ve D8'i korna olarak ayarla."
            ),
            DusunmeAdimi(
                tip="DONGU",
                baslik="Mesafeyi Ölç (loop)",
                aciklama="Sesin gidip gelme süresinden mesafeyi santimetreye çevir."
            ),
            DusunmeAdimi(
                tip="EGER",
                baslik="Eğer Cisim Çok Yakınsa",
                aciklama="Mesafe 15 santimetreden az ise tehlike var demektir!"
            ),
            DusunmeAdimi(
                tip="YAP",
                baslik="Kornayı Çal!",
                aciklama="Buzzer'ı bip bip öttürerek uyar, mesafe uzaktaysa sessiz kal."
            )
        ],
        arduino_kodu="""// Kid Arduino Studio - Akilli Park Sensoru
const int TRIG_PIN = 9;
const int ECHO_PIN = 10;
const int BUZZER_PIN = 8;

void setup() {
  pinMode(TRIG_PIN, OUTPUT);
  pinMode(ECHO_PIN, INPUT);
  pinMode(BUZZER_PIN, OUTPUT);
  Serial.begin(9600);
  Serial.println("Park Sensoru Sistemi Aktif!");
}

void loop() {
  digitalWrite(TRIG_PIN, LOW);
  delayMicroseconds(2);
  digitalWrite(TRIG_PIN, HIGH);
  delayMicroseconds(10);
  digitalWrite(TRIG_PIN, LOW);

  long sure = pulseIn(ECHO_PIN, HIGH);
  int mesafe = sure * 0.034 / 2;

  Serial.print("Mesafe: ");
  Serial.print(mesafe);
  Serial.println(" cm");

  if (mesafe > 0 && mesafe < 15) {
    digitalWrite(BUZZER_PIN, HIGH);
    delay(80);
    digitalWrite(BUZZER_PIN, LOW);
    delay(80);
  } else {
    digitalWrite(BUZZER_PIN, LOW);
    delay(100);
  }
}
""",
        guvenlik_notu="HC-SR04 sensörünün bacakları hassastır, nazikçe takmayı unutma."
    )
}


# ---------------------------------------------------------
# Pedagojik AI Sistem Promptu
# ---------------------------------------------------------

SYSTEM_PROMPT = """Sen 8-14 yaş arasındaki çocuklar için tasarlanmış bir 'Arduino Robot Arkadaşı'sın.
GÖREVİN: Çocuğun hayalindeki projeyi ve elindeki parçaları inceleyerek Arduino Uno projesini JSON olarak tasarlamak.

KURALLAR:
1. SADECE ÇOCUĞUN SEÇTİĞİ PARÇALARI KULLAN. (Arduino Uno her zaman vardır).
2. ÇOCUK DOSTU DİL KULLAN:
   - 'Anot/katot' yerine 'uzun bacak (+)', 'kısa bacak (-)'.
   - 'Pull-up/down' gibi karmaşık terimler kullanma.
3. KOD:
   - Harici kütüphane gerektirmeyen (Servo hariç) doğrudan arduino:avr:uno için geçerli C++ kodu üret.
   - Her zaman Serial.begin(9600); ekle.
4. KABLO RENKLERİ:
   - 5V/Güç: #EF4444 (Kırmızı)
   - GND/Toprak: #1F2937 (Füme/Siyah)
   - Sinyal: #3B82F6 (Mavi), #10B981 (Yeşil), #F59E0B (Sarı)

JSON ŞEMASI (KESİNLİKLE BU YAPIDA GEÇERLİ JSON DÖNDÜR):
{
  "proje_adi": "string",
  "karsilama_mesaji": "string",
  "gerekli_parcalar": ["ARDUINO_UNO", "LED_RED", ...],
  "baglanti_adimlari": [
    {
      "adim_no": 1,
      "talimat": "string",
      "ipucu": "string",
      "kaynak": { "parca": "LED_RED", "pin": "ANODE" },
      "hedef": { "parca": "ARDUINO_UNO", "pin": "D13" },
      "kablo_rengi": "#EF4444"
    }
  ],
  "dusunme_adimlari": [
    {
      "tip": "BASLANGIC" | "DONGU" | "EGER" | "YAP",
      "baslik": "string",
      "aciklama": "string"
    }
  ],
  "arduino_kodu": "void setup() { ... } void loop() { ... }",
  "guvenlik_notu": "string"
}
"""


# ---------------------------------------------------------
# Dinamik Model Listesi (Yerel Ollama + Cloud)
# ---------------------------------------------------------

def get_installed_ollama_models(ollama_url: str = "http://127.0.0.1:11434") -> List[Dict[str, Any]]:
    """Yerel Ollama sunucusundaki gerçek kurulu modelleri döner."""
    try:
        res = httpx.get(f"{ollama_url}/api/tags", timeout=3.0)
        if res.status_code == 200:
            data = res.json()
            models = []
            for m in data.get("models", []):
                name = m.get("name")
                if not name:
                    continue
                # Embed modellerini filtrele
                if "embed" in name:
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

    # Bulut Modelleri
    cloud_models = [
        # Google Gemini
        {"id": "gemini/gemini-2.0-flash", "name": "Gemini 2.0 Flash (Yeni & Çok Hızlı)", "provider": "gemini", "category": "Google Gemini", "badge": "☁️ Bulut"},
        {"id": "gemini/gemini-1.5-flash", "name": "Gemini 1.5 Flash (Dengeli)", "provider": "gemini", "category": "Google Gemini", "badge": "☁️ Bulut"},
        {"id": "gemini/gemini-1.5-pro", "name": "Gemini 1.5 Pro (Gelişmiş)", "provider": "gemini", "category": "Google Gemini", "badge": "☁️ Bulut"},
        
        # OpenAI
        {"id": "gpt-4o-mini", "name": "GPT-4o Mini (Hızlı & Yetenekli)", "provider": "openai", "category": "OpenAI", "badge": "☁️ Bulut"},
        {"id": "gpt-4o", "name": "GPT-4o (Amiral Gemisi)", "provider": "openai", "category": "OpenAI", "badge": "☁️ Bulut"},
        
        # Anthropic Claude
        {"id": "claude-3-5-haiku-20241022", "name": "Claude 3.5 Haiku (Ultra Hızlı)", "provider": "anthropic", "category": "Anthropic Claude", "badge": "☁️ Bulut"},
        {"id": "claude-3-5-sonnet-20241022", "name": "Claude 3.5 Sonnet (Üst Düzey Kodlama)", "provider": "anthropic", "category": "Anthropic Claude", "badge": "☁️ Bulut"},
    ]

    # Ortam değişkeni kontrolleri
    configured_keys = {
        "gemini": bool(os.getenv("GEMINI_API_KEY")),
        "openai": bool(os.getenv("OPENAI_API_KEY")),
        "anthropic": bool(os.getenv("ANTHROPIC_API_KEY")),
    }

    # Varsayılan önerilen model
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


def clean_llm_json_response(raw_text: str) -> str:
    """
    LLM çıktısından JSON'ı temiz bir şekilde ayıklar:
    - DeepSeek-R1 <think>...</think> etiketlerini kaldırır.
    - Markdown ```json bloklarını temizler.
    - Metin içindeki ilk { ve son } arasını yakalar.
    """
    text = raw_text.strip()
    
    # 1. <think> tag temizliği
    text = re.sub(r"<think>.*?</think>", "", text, flags=re.DOTALL).strip()
    
    # 2. Markdown blok temizliği
    text = re.sub(r"^```(?:json)?\s*", "", text).strip()
    text = re.sub(r"```$", "", text).strip()
    
    # 3. İlk { ve son } arasını bul
    start = text.find("{")
    end = text.rfind("}")
    if start != -1 and end != -1 and end > start:
        return text[start:end+1]
        
    return text


def generate_with_ollama(model_name: str, prompt: str, inventory: List[str], ollama_url: str = "http://127.0.0.1:11434") -> ProjectResponse:
    """Yerel Ollama örneğine doğrudan HTTP çağrısı yapar."""
    clean_model = model_name.replace("ollama/", "")
    
    user_prompt = f"""KULLANICI PROJE HAYALİ:
"{prompt}"

ÇOCUĞUN ELİNDEKİ PARÇALAR (ENVANTER):
{json.dumps(inventory, ensure_ascii=False)}

Lütfen belirtilen JSON şemasına harfiyen uygun bir Türkçe proje üret."""

    payload = {
        "model": clean_model,
        "prompt": f"{SYSTEM_PROMPT}\n\n{user_prompt}",
        "format": "json",
        "stream": False,
        "options": {
            "temperature": 0.2,
            "top_p": 0.9
        }
    }

    res = httpx.post(f"{ollama_url}/api/generate", json=payload, timeout=90.0)
    if res.status_code != 200:
        raise RuntimeError(f"Ollama hata döndürdü: {res.status_code} - {res.text}")

    resp_json = res.json()
    raw_content = resp_json.get("response", "")
    clean_json_str = clean_llm_json_response(raw_content)

    data = json.loads(clean_json_str)
    return ProjectResponse(**data)


def generate_with_litellm(model_name: str, prompt: str, inventory: List[str], api_key: Optional[str] = None) -> ProjectResponse:
    """LiteLLM üzerinden Gemini, OpenAI, Claude vb. çağrısı yapar."""
    import litellm

    # API Key ayarları
    if api_key and api_key.strip():
        if "gemini" in model_name.lower():
            os.environ["GEMINI_API_KEY"] = api_key.strip()
        elif "claude" in model_name.lower() or "anthropic" in model_name.lower():
            os.environ["ANTHROPIC_API_KEY"] = api_key.strip()
        else:
            os.environ["OPENAI_API_KEY"] = api_key.strip()

    user_content = f"""KULLANICI PROJE HAYALİ:
"{prompt}"

ÇOCUĞUN ELİNDEKİ PARÇALAR (ENVANTER):
{json.dumps(inventory, ensure_ascii=False)}

Lütfen bu hayali gerçekleştirecek projeyi tam JSON şemasına uygun olarak üret."""

    json_schema = ProjectResponse.model_json_schema()

    response = litellm.completion(
        model=model_name,
        messages=[
            {"role": "system", "content": SYSTEM_PROMPT},
            {"role": "user", "content": user_content}
        ],
        response_format={"type": "json_object", "schema": json_schema},
        temperature=0.2
    )

    content = response.choices[0].message.content
    clean_json_str = clean_llm_json_response(content)
    data = json.loads(clean_json_str)
    return ProjectResponse(**data)


def generate_project_with_ai(
    prompt: str,
    inventory: List[str],
    model: Optional[str] = None,
    api_key: Optional[str] = None,
    ollama_url: str = "http://127.0.0.1:11434"
) -> ProjectResponse:
    """
    Kullanıcının seçtiği modele (Yerel Ollama veya Gemini/OpenAI/Claude) göre projeyi üretir.
    Hata durumunda akıllı şablonlara güvenle fallback yapar.
    """
    chosen_model = model or "ollama/qwen2.5-coder:1.5b"
    print(f"[AI Service] Proje üretiliyor. Model: {chosen_model}")

    # 1. Yerel Ollama Modeli mi?
    if chosen_model.startswith("ollama/") or chosen_model in ["local", "qwen2.5-coder:1.5b", "qwen2.5-coder:3b"]:
        try:
            return generate_with_ollama(chosen_model, prompt, inventory, ollama_url)
        except Exception as e:
            print(f"[Ollama Hatası] Yerel model çağrısı başarısız oldu ({e}).")
            # Eğer bulut anahtarı varsa buluta geç, yoksa mock'a geç
            if not api_key and not os.getenv("GEMINI_API_KEY") and not os.getenv("OPENAI_API_KEY"):
                print("[AI Fallback] Mock şablona geçiliyor.")
                return MOCK_PROJECTS["park_sensoru"] if "park" in prompt.lower() or "mesafe" in prompt.lower() else MOCK_PROJECTS["gece_lambasi"]

    # 2. Bulut Modeli (Gemini / OpenAI / Claude)
    try:
        return generate_with_litellm(chosen_model, prompt, inventory, api_key)
    except Exception as e:
        print(f"[LiteLLM Hatası] Bulut model çağrısı başarısız oldu ({e}). Akıllı mock şablon dönülüyor.")
        if any(w in prompt.lower() for w in ["mesafe", "park", "engel", "yarasa", "hcsr04", "korna"]):
            return MOCK_PROJECTS["park_sensoru"]
        return MOCK_PROJECTS["gece_lambasi"]


def fix_arduino_code(code: str, error_message: str, project_context: str = "", model: Optional[str] = None) -> str:
    """
    Self-Healing mekanizması:
    Derleme hatasını yerel Ollama modeline veya bulut LLM'ine göndererek onarır.
    """
    repair_prompt = f"""Bir Arduino Uno C++ kodunu derlerken şu derleme hatasını aldık:
HATA:
{error_message}

KOD:
```cpp
{code}
```

Lütfen hatayı gider ve 'arduino:avr:uno' için harici kütüphane gerektirmeyen TAM ve HATASIZ C++ kodunu döndür.
SADECE C++ kodunu döndür."""

    # 1. Önce yerel model dene
    try:
        res = httpx.post(
            "http://127.0.0.1:11434/api/generate",
            json={"model": "qwen2.5-coder:1.5b", "prompt": repair_prompt, "stream": False},
            timeout=30.0
        )
        if res.status_code == 200:
            fixed = res.json().get("response", "").strip()
            fixed = re.sub(r"^```cpp\s*", "", fixed)
            fixed = re.sub(r"^```\s*", "", fixed)
            fixed = re.sub(r"```$", "", fixed).strip()
            if "void setup" in fixed and "void loop" in fixed:
                return fixed
    except Exception:
        pass

    return code

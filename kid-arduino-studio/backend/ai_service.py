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
    parca: str = Field(description="Bileşenin adı (örn: ARDUINO_UNO, BREADBOARD, LED_RED, HCSR04)")
    pin: str = Field(description="Pin adı veya Breadboard deliği (örn: D13, 5V, GND, A5, E5, J15, RAIL_5V, RAIL_GND)")

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
# Breadboard Fizik Kontrolcüsü (Deterministic Validator)
# ---------------------------------------------------------

def get_breadboard_net(pin: str) -> str:
    """Aynı elektrik hattına bağlı delikleri aynı 'net' ismine çevirir."""
    p = (pin or "").upper().strip()
    if "GND" in p or p.startswith("RAIL_GND") or p == "-":
        return "RAIL_GND"
    if "5V" in p or "3.3V" in p or p.startswith("RAIL_5V") or p == "+":
        return "RAIL_5V"
    
    match = re.match(r"^([A-J])(\d+)$", p)
    if not match:
        return p
    
    row, col = match.groups()
    half = "TOP" if row in "ABCDE" else "BOTTOM"
    return f"BB_{half}_{col}"  # Örn: A5 ve E5 ikisi de 'BB_TOP_5' döner!


def validate_breadboard_steps(steps: list) -> List[str]:
    """
    Breadboard üzerindeki adımları doğrular ve kısa devreleri tespit eder.
    """
    errors = []
    for s in steps:
        step_dict = s if isinstance(s, dict) else (s.model_dump() if hasattr(s, "model_dump") else s.__dict__)
        kaynak = step_dict.get("kaynak", {})
        hedef = step_dict.get("hedef", {})
        adim_no = step_dict.get("adim_no", "?")
        
        k_parca = (kaynak.get("parca") or "").upper().strip()
        h_parca = (hedef.get("parca") or "").upper().strip()
        k_pin = (kaynak.get("pin") or "").upper().strip()
        h_pin = (hedef.get("pin") or "").upper().strip()

        # Breadboard içi aynı sütun kısa devre kontrolü
        if (k_parca == "BREADBOARD" or "BB" in k_parca) and (h_parca == "BREADBOARD" or "BB" in h_parca):
            net1 = get_breadboard_net(k_pin)
            net2 = get_breadboard_net(h_pin)
            if net1 == net2:
                errors.append(
                    f"Adım {adim_no} HATALI: {k_pin} ve {h_pin} zaten breadboard içinde birbirine bağlı (Aynı hat: {net1}). Kısa devre oluşur! Farklı sütun numaraları kullan."
                )
    return errors


# ---------------------------------------------------------
# Hazır Mock Demo Projeler (Breadboard Standartlarına Tam Uyumlu)
# ---------------------------------------------------------

MOCK_PROJECTS = {
    "gece_lambasi": ProjectResponse(
        proje_adi="Akıllı Gece Bekçisi Lambası",
        karsilama_mesaji="Harika bir fikir! Odan karardığında sihir gibi kendiliğinden yanan akıllı bir gece lambası yapıyoruz. 🌙✨",
        gerekli_parcalar=["ARDUINO_UNO", "LDR_SENSOR", "LED_RED", "RESISTOR_220"],
        baglanti_adimlari=[
            BaglantiAdimi(
                adim_no=1,
                talimat="Arduino 5V pininden Breadboard Kırmızı Güç Hattına (RAIL_5V) kablo tak.",
                ipucu="Bu hat tüm devreye 5 Volt pozitif enerji dağıtacak.",
                kaynak=ConnectionEndpoint(parca="ARDUINO_UNO", pin="5V"),
                hedef=ConnectionEndpoint(parca="BREADBOARD", pin="RAIL_5V"),
                kablo_rengi="#EF4444"
            ),
            BaglantiAdimi(
                adim_no=2,
                talimat="Arduino GND pininden Breadboard Mavi Eksi Hattına (RAIL_GND) kablo tak.",
                ipucu="GND, devrenin elektrik dönüş (eksi) yoludur.",
                kaynak=ConnectionEndpoint(parca="ARDUINO_UNO", pin="GND"),
                hedef=ConnectionEndpoint(parca="BREADBOARD", pin="RAIL_GND"),
                kablo_rengi="#1F2937"
            ),
            BaglantiAdimi(
                adim_no=3,
                talimat="Kırmızı LED'in uzun bacağını E5'e, kısa bacağını E6'ya tak. Arduino D13 pininden A5 deliğine kablo çek.",
                ipucu="D13'ten gelen elektrik A5'e girer ve aynı 5. sütundaki E5 deliğinde duran LED uzun bacağına ulaşır!",
                kaynak=ConnectionEndpoint(parca="ARDUINO_UNO", pin="D13"),
                hedef=ConnectionEndpoint(parca="BREADBOARD", pin="A5"),
                kablo_rengi="#EF4444"
            ),
            BaglantiAdimi(
                adim_no=4,
                talimat="220Ω Direncin bir ucunu C6'ya (LED kısa bacağı ile aynı sütuna!), diğer ucunu RAIL_GND hattına bağla.",
                ipucu="6. sütundaki LED kısa bacağı ile direnç breadboard içinde buluşur ve eksi hatta güvenle akar.",
                kaynak=ConnectionEndpoint(parca="BREADBOARD", pin="C6"),
                hedef=ConnectionEndpoint(parca="BREADBOARD", pin="RAIL_GND"),
                kablo_rengi="#3B82F6"
            ),
            BaglantiAdimi(
                adim_no=5,
                talimat="LDR ışık sensörünün bacaklarını E12 ve E14 deliklerine tak. Arduino A0 pininden A12 deliğine kablo çek.",
                ipucu="A0 analog bilgi pini, odanın aydınlık seviyesini 12. sütundan dinler.",
                kaynak=ConnectionEndpoint(parca="ARDUINO_UNO", pin="A0"),
                hedef=ConnectionEndpoint(parca="BREADBOARD", pin="A12"),
                kablo_rengi="#10B981"
            ),
            BaglantiAdimi(
                adim_no=6,
                talimat="LDR'ın diğer bacağı için A14 deliğinden Kırmızı Güç Hattına (RAIL_5V) kablo tak.",
                ipucu="LDR çalışmak için 5 Volt elektrik enerjisine ihtiyaç duyar.",
                kaynak=ConnectionEndpoint(parca="BREADBOARD", pin="A14"),
                hedef=ConnectionEndpoint(parca="BREADBOARD", pin="RAIL_5V"),
                kablo_rengi="#EF4444"
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
                talimat="Arduino 5V pininden Breadboard Kırmızı Güç Hattına (RAIL_5V) kablo tak.",
                ipucu="Sensör ve korna enerjisini bu ortak hattan alacak.",
                kaynak=ConnectionEndpoint(parca="ARDUINO_UNO", pin="5V"),
                hedef=ConnectionEndpoint(parca="BREADBOARD", pin="RAIL_5V"),
                kablo_rengi="#EF4444"
            ),
            BaglantiAdimi(
                adim_no=2,
                talimat="Arduino GND pininden Breadboard Mavi Eksi Hattına (RAIL_GND) kablo tak.",
                ipucu="Ortak eksi kutbu sağlayarak devreyi güvenle tamamlarız.",
                kaynak=ConnectionEndpoint(parca="ARDUINO_UNO", pin="GND"),
                hedef=ConnectionEndpoint(parca="BREADBOARD", pin="RAIL_GND"),
                kablo_rengi="#1F2937"
            ),
            BaglantiAdimi(
                adim_no=3,
                talimat="HC-SR04 sensörünü F14, F15, F16, F17 deliklerine tak. Arduino D9 pininden J15 (TRIG) deliğine kablo çek.",
                ipucu="TRIG pini ses dalgalarını fırlatır.",
                kaynak=ConnectionEndpoint(parca="ARDUINO_UNO", pin="D9"),
                hedef=ConnectionEndpoint(parca="BREADBOARD", pin="J15"),
                kablo_rengi="#3B82F6"
            ),
            BaglantiAdimi(
                adim_no=4,
                talimat="Arduino D10 pininden J16 (ECHO) deliğine kablo çek.",
                ipucu="ECHO pini yankılanan ses dalgalarını dinler.",
                kaynak=ConnectionEndpoint(parca="ARDUINO_UNO", pin="D10"),
                hedef=ConnectionEndpoint(parca="BREADBOARD", pin="J16"),
                kablo_rengi="#10B981"
            ),
            BaglantiAdimi(
                adim_no=5,
                talimat="Sensörün VCC bacağı için J14 deliğinden Kırmızı Güç Hattına (RAIL_5V) kablo tak.",
                ipucu="Sensörün çalışması için 5V enerji verdik.",
                kaynak=ConnectionEndpoint(parca="BREADBOARD", pin="J14"),
                hedef=ConnectionEndpoint(parca="BREADBOARD", pin="RAIL_5V"),
                kablo_rengi="#EF4444"
            ),
            BaglantiAdimi(
                adim_no=6,
                talimat="Sensörün GND bacağı için J17 deliğinden Mavi Eksi Hattına (RAIL_GND) kablo tak.",
                ipucu="Sensörün elektrik devresi tamamlandı.",
                kaynak=ConnectionEndpoint(parca="BREADBOARD", pin="J17"),
                hedef=ConnectionEndpoint(parca="BREADBOARD", pin="RAIL_GND"),
                kablo_rengi="#1F2937"
            ),
            BaglantiAdimi(
                adim_no=7,
                talimat="Buzzer'ın artı bacağını F22'ye tak. Arduino D8 pininden J22 deliğine kablo çek.",
                ipucu="Buzzer korna gibi öterek yaklaşan nesneleri haber verir.",
                kaynak=ConnectionEndpoint(parca="ARDUINO_UNO", pin="D8"),
                hedef=ConnectionEndpoint(parca="BREADBOARD", pin="J22"),
                kablo_rengi="#F59E0B"
            ),
            BaglantiAdimi(
                adim_no=8,
                talimat="Buzzer'ın eksi bacağını F24'e tak ve J24 deliğinden Mavi Eksi Hattına (RAIL_GND) bağla.",
                ipucu="Kornanın devresini tamamladık.",
                kaynak=ConnectionEndpoint(parca="BREADBOARD", pin="J24"),
                hedef=ConnectionEndpoint(parca="BREADBOARD", pin="RAIL_GND"),
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
# Pedagojik AI Sistem Promptu (Katı Breadboard Kuralları ile)
# ---------------------------------------------------------

SYSTEM_PROMPT = """Sen 8-14 yaş arasındaki çocuklar için tasarlanmış bir 'Arduino Robot Arkadaşı'sın.
GÖREVİN: Çocuğun hayalindeki projeyi ve elindeki parçaları inceleyerek Arduino Uno projesini JSON olarak tasarlamak.

BREADBOARD PİN ADLANDIRMASI:
- Üst Yarı Delikleri: A1..E30 (Örn: A5, B10, E12)
- Alt Yarı Delikleri: F1..J30 (Örn: F14, J16, H22)
- Güç Hatları: RAIL_5V (Kırmızı Artı Hattı), RAIL_GND (Mavi Eksi Hattı)

BREADBOARD FİZİKSEL BAĞLANTI KURALLARI (KESİNLİKLE UYULACAK):
1. DİKEY İLETKENLİK (KISA DEVRE YASAĞI):
   - Breadboard üzerinde AYNI SÜTUN NUMARASINA sahip A-B-C-D-E delikleri birbirine içeriden bağlıdır (Örn: A5, B5, C5, D5, E5 tek bir iletkendir).
   - AYNI SÜTUN NUMARASINA sahip F-G-H-I-J delikleri de kendi içinde birbirine bağlıdır (Örn: F5, G5, H5, I5, J5 tek bir iletkendir).
   - Orta oluk (E ile F arası) yalıtkandır, birbirine bağlı DEĞİLDİR.
   - YASAK: Bir bileşenin (LED, Direnç, Buton) iki bacağını ASLA aynı sütun numarasına (Örn: A5 ve B5'e) takma! Bu kısa devre yapar.

2. BİLEŞEN YERLEŞİM FORMATI VE KABLO BAĞLANTISI:
   - LED Yerleşimi: Uzun bacak (ANODE) bir sütuna (örn: E5), kısa bacak (CATHODE) farklı bir sütuna (örn: E6) takılır.
   - Direnç Yerleşimi: Direncin bir ucu bileşenin olduğu sütuna (örn: C6), diğer ucu FARKLI bir sütuna veya doğrudan `RAIL_GND` hattına takılır. (Asla C6'dan D6'ya aynı sütun içinde bağlama!).
   - Sinyal Kablosu: Arduino'dan gelen sinyal kablosu, ilgili bileşenin bacağıyla AYNI SÜTUNDAKİ boş bir deliğe takılır (Örn: LED E5'teyse, D13 kablosu A5'e takılır).

3. GÜÇ HATLARI:
   - Arduino `GND` -> Breadboard `RAIL_GND` (Mavi eksi hattı).
   - Arduino `5V` -> Breadboard `RAIL_5V` (Kırmızı artı hattı).
   - Sensörler ve bileşenler güç ve toprağı doğrudan `RAIL_5V` ve `RAIL_GND` hatlarından alır.

4. HAZIR BREADBOARD BÖLGE SLOTLARI (KABLOLAR KARIŞMASIN DİYE):
   - Sol Bölge (Sütun 1–8): LED'ler ve Dirençler için.
   - Orta Bölge (Sütun 10–18): Butonlar ve Sensörler (LDR, HC-SR04) için.
   - Sağ Bölge (Sütun 20–28): Buzzer ve Servo motor için.

KOD KURALLARI:
- Harici kütüphane gerektirmeyen (Servo hariç) doğrudan arduino:avr:uno için geçerli C++ kodu üret.
- Her zaman Serial.begin(9600); ekle.

KABLO RENKLERİ:
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
      "kaynak": { "parca": "ARDUINO_UNO", "pin": "5V" },
      "hedef": { "parca": "BREADBOARD", "pin": "RAIL_5V" },
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

    cloud_models = [
        {"id": "gemini/gemini-2.0-flash", "name": "Gemini 2.0 Flash (Yeni & Çok Hızlı)", "provider": "gemini", "category": "Google Gemini", "badge": "☁️ Bulut"},
        {"id": "gemini/gemini-1.5-flash", "name": "Gemini 1.5 Flash (Dengeli)", "provider": "gemini", "category": "Google Gemini", "badge": "☁️ Bulut"},
        {"id": "gemini/gemini-1.5-pro", "name": "Gemini 1.5 Pro (Gelişmiş)", "provider": "gemini", "category": "Google Gemini", "badge": "☁️ Bulut"},
        {"id": "gpt-4o-mini", "name": "GPT-4o Mini (Hızlı & Yetenekli)", "provider": "openai", "category": "OpenAI", "badge": "☁️ Bulut"},
        {"id": "gpt-4o", "name": "GPT-4o (Amiral Gemisi)", "provider": "openai", "category": "OpenAI", "badge": "☁️ Bulut"},
        {"id": "claude-3-5-haiku-20241022", "name": "Claude 3.5 Haiku (Ultra Hızlı)", "provider": "anthropic", "category": "Anthropic Claude", "badge": "☁️ Bulut"},
        {"id": "claude-3-5-sonnet-20241022", "name": "Claude 3.5 Sonnet (Üst Düzey Kodlama)", "provider": "anthropic", "category": "Anthropic Claude", "badge": "☁️ Bulut"},
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


def generate_with_ollama(model_name: str, prompt: str, inventory: List[str], ollama_url: str = "http://127.0.0.1:11434") -> ProjectResponse:
    """Yerel Ollama örneğine doğrudan HTTP çağrısı yapar ve breadboard kurallarını doğrular."""
    clean_model = model_name.replace("ollama/", "")
    
    user_prompt = f"""KULLANICI PROJE HAYALİ:
"{prompt}"

ÇOCUĞUN ELİNDEKİ PARÇALAR (ENVANTER):
{json.dumps(inventory, ensure_ascii=False)}

Lütfen belirtilen Breadboard Fiziksel Kurallarına harfiyen uygun bir Türkçe proje üret."""

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
    proj = ProjectResponse(**data)

    # Breadboard Fizik Doğrulaması
    errors = validate_breadboard_steps(proj.baglanti_adimlari)
    if errors:
        print(f"[Breadboard Validator] Kısa devre hataları tespit edildi: {errors}")
        # Hata varsa güvenli akıllı şablona fallback yap
        return MOCK_PROJECTS["park_sensoru"] if any(k in prompt.lower() for k in ["park", "mesafe", "yarasa"]) else MOCK_PROJECTS["gece_lambasi"]

    return proj


def generate_with_litellm(model_name: str, prompt: str, inventory: List[str], api_key: Optional[str] = None) -> ProjectResponse:
    """LiteLLM üzerinden Gemini, OpenAI, Claude vb. çağrısı yapar ve breadboard kurallarını doğrular."""
    import litellm

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

Lütfen Breadboard Fiziksel Kurallarına (dikey iletkenlik, kısa devre yasağı, güç hatları) harfiyen uyarak tam JSON şemasına uygun olarak üret."""

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
    proj = ProjectResponse(**data)

    # Breadboard Fizik Doğrulaması
    errors = validate_breadboard_steps(proj.baglanti_adimlari)
    if errors:
        print(f"[Breadboard Validator] LiteLLM çıktısında kısa devre tespit edildi: {errors}")
        # Hatalı adımlarla çocuğu yanıltmamak için doğrulanmış şablona güvenle fallback yap
        return MOCK_PROJECTS["park_sensoru"] if any(k in prompt.lower() for k in ["park", "mesafe", "yarasa"]) else MOCK_PROJECTS["gece_lambasi"]

    return proj


def generate_project_with_ai(
    prompt: str,
    inventory: List[str],
    model: Optional[str] = None,
    api_key: Optional[str] = None,
    ollama_url: str = "http://127.0.0.1:11434"
) -> ProjectResponse:
    """Kullanıcının seçtiği modele göre projeyi üretir ve breadboard fizik kurallarını doğrular."""
    chosen_model = model or "ollama/qwen2.5-coder:1.5b"
    print(f"[AI Service] Proje üretiliyor. Model: {chosen_model}")

    if chosen_model.startswith("ollama/") or chosen_model in ["local", "qwen2.5-coder:1.5b", "qwen2.5-coder:3b"]:
        try:
            return generate_with_ollama(chosen_model, prompt, inventory, ollama_url)
        except Exception as e:
            print(f"[Ollama Hatası] Yerel model çağrısı başarısız oldu ({e}).")
            if not api_key and not os.getenv("GEMINI_API_KEY") and not os.getenv("OPENAI_API_KEY"):
                print("[AI Fallback] Mock şablona geçiliyor.")
                return MOCK_PROJECTS["park_sensoru"] if any(k in prompt.lower() for k in ["park", "mesafe", "yarasa"]) else MOCK_PROJECTS["gece_lambasi"]

    try:
        return generate_with_litellm(chosen_model, prompt, inventory, api_key)
    except Exception as e:
        print(f"[LiteLLM Hatası] Bulut model çağrısı başarısız oldu ({e}). Akıllı mock şablon dönülüyor.")
        if any(w in prompt.lower() for w in ["mesafe", "park", "engel", "yarasa", "hcsr04", "korna"]):
            return MOCK_PROJECTS["park_sensoru"]
        return MOCK_PROJECTS["gece_lambasi"]


def fix_arduino_code(code: str, error: str, project_context: str = "", model: Optional[str] = None) -> str:
    """Derleme veya yükleme hatasını analiz edip düzelten kendini iyileştirme (self-healing) fonksiyonu."""
    chosen_model = model or "gemini/gemini-1.5-flash"
    
    prompt = f"""Aşağıdaki Arduino Uno kodunda derleme/yükleme hatası oluştu.
LÜTFEN HATAYI DÜZELT VE SADECE DÜZELTİLMİŞ C++ ARDUINO KODUNU DÖNDÜR.
Açıklama, markdown veya fazladan metin ekleme.

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

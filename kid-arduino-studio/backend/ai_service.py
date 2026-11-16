import json
import os
import re
from typing import List, Optional, Literal
from pydantic import BaseModel, Field

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
# Hazır Mock Demo Projeler (API Key Yokken veya Test İçin)
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
                ipucu="Direnç tıpkı bir hız tümseği gibidir; LED'e fazla elektrik akmasını önleyip onu korur!",
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
                ipucu="LDR odadaki ışığı hisseden sihirli bir gözdür. Çalışmak için 5 Volt enerjiye ihtiyaç duyar.",
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
                aciklama="Arduino uyandığında D13 pinini lamba çıkışı olarak ayarla ve ışık sensörünü dinlemeye başla."
            ),
            DusunmeAdimi(
                tip="DONGU",
                baslik="Sürekli Gözlemle (loop)",
                aciklama="Arduino durmaksızın A0 pininden odanın aydınlık seviyesini saniyede defalarca okur."
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
    digitalWrite(LED_PIN, HIGH); // Karanlık: LED Yansın
  } else {
    digitalWrite(LED_PIN, LOW);  // Aydınlık: LED Sönsün
  }
  
  delay(100);
}
""",
        guvenlik_notu="LED'in fazla akımdan dolayı zarar görmemesi için araya mutlaka 220 Ohm direnç koyduk. Tebrikler, harika bir mühendissin!"
    ),

    "park_sensoru": ProjectResponse(
        proje_adi="Yarasa Kulaklı Akıllı Park Sensörü",
        karsilama_mesaji="Süper bir fikir! Tıpkı yarasalar gibi ses dalgaları fırlatarak yaklaşan nesneleri fark eden bir alarm yapıyoruz! 🦇🚗",
        gerekli_parcalar=["ARDUINO_UNO", "HCSR04", "BUZZER", "LED_RED"],
        baglanti_adimlari=[
            BaglantiAdimi(
                adim_no=1,
                talimat="Ultrasonik mesafe sensörünün VCC bacağını Arduino'nun 5V (Kırmızı Güç) pinine bağla.",
                ipucu="VCC, sensörün can damarıdır. 5 Volt enerji verir.",
                kaynak=ConnectionEndpoint(parca="HCSR04", pin="VCC"),
                hedef=ConnectionEndpoint(parca="ARDUINO_UNO", pin="5V"),
                kablo_rengi="#EF4444"
            ),
            BaglantiAdimi(
                adim_no=2,
                talimat="Ultrasonik mesafe sensörünün GND bacağını Arduino'nun GND (Siyah Toprak) pinine bağla.",
                ipucu="GND elektrik akımının dönüş yoludur.",
                kaynak=ConnectionEndpoint(parca="HCSR04", pin="GND"),
                hedef=ConnectionEndpoint(parca="ARDUINO_UNO", pin="GND"),
                kablo_rengi="#1F2937"
            ),
            BaglantiAdimi(
                adim_no=3,
                talimat="Sensörün TRIG (Tetik) bacağını Arduino üzerindeki D9 dijital pinine bağla.",
                ipucu="TRIG bacağı, gözle görülmeyen minik ses dalgalarını fırlatan bir mikrofondur.",
                kaynak=ConnectionEndpoint(parca="HCSR04", pin="TRIG"),
                hedef=ConnectionEndpoint(parca="ARDUINO_UNO", pin="D9"),
                kablo_rengi="#3B82F6"
            ),
            BaglantiAdimi(
                adim_no=4,
                talimat="Sensörün ECHO (Yankı) bacağını Arduino üzerindeki D10 dijital pinine bağla.",
                ipucu="ECHO bacağı, duvara çarpıp geri dönen sesi dinleyen dedektördür.",
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
                ipucu="Buzzer'ın devresini tamamlamak için eksi kutbu da toprağa (GND) bağlıyoruz.",
                kaynak=ConnectionEndpoint(parca="BUZZER", pin="GND"),
                hedef=ConnectionEndpoint(parca="ARDUINO_UNO", pin="GND"),
                kablo_rengi="#1F2937"
            )
        ],
        dusunme_adimlari=[
            DusunmeAdimi(
                tip="BASLANGIC",
                baslik="Sensör ve Kornayı Hazırla (setup)",
                aciklama="Arduino uyandığında D9'u ses fırlatıcı (TRIG), D10'u dinleyici (ECHO) ve D8'i korna olarak ayarla."
            ),
            DusunmeAdimi(
                tip="DONGU",
                baslik="Ses Dalgası Gönder ve Mesafeyi Ölç (loop)",
                aciklama="D9'dan 10 mikrosaniye ses fırlat, sesin nesneye çarpıp geri dönme süresinden mesafeyi santimetreye çevir."
            ),
            DusunmeAdimi(
                tip="EGER",
                baslik="Eğer Bir Cisim Çok Yaklaştıysa",
                aciklama="Ölçülen mesafe 15 santimetreden daha az ise tehlike var demektir!"
            ),
            DusunmeAdimi(
                tip="YAP",
                baslik="Kornayı Çal ve Uyar!",
                aciklama="Buzzer'ı bip bip öttürerek sürücüyü uyar, mesafe uzaktaysa sessiz kal."
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
  // Ses dalgası gönder
  digitalWrite(TRIG_PIN, LOW);
  delayMicroseconds(2);
  digitalWrite(TRIG_PIN, HIGH);
  delayMicroseconds(10);
  digitalWrite(TRIG_PIN, LOW);

  // Sesin geliş süresini ölç ve mesafeyi hesapla
  long sure = pulseIn(ECHO_PIN, HIGH);
  int mesafe = sure * 0.034 / 2;

  Serial.print("Mesafe: ");
  Serial.print(mesafe);
  Serial.println(" cm");

  // 15 cm'den yakınsa uyar
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
        guvenlik_notu="HC-SR04 sensörünün bacakları hassastır, nazikçe takmayı unutma. Mesafe 15 cm altına düşünce kornamız seni hemen uyaracak!"
    )
}


# ---------------------------------------------------------
# Pedagojik AI Sistem Promptu
# ---------------------------------------------------------

SYSTEM_PROMPT = """Sen 8-14 yaş arasındaki çocuklar için özel tasarlanmış, dünyanın en neşeli, teşvik edici ve bilge Arduino Öğretmenisin!
Adın 'Arduino Robot Arkadaşı'.

GÖREVİN:
Çocuğun Türkçe yazdığı hayalindeki projeyi ve elinde bulunduğunu belirttiği parçaları inceleyerek, tamamen derlenebilir ve adım adım kurulabilir bir Arduino projesi tasarlamak.

KURALLAR:
1. SADECE ÇOCUĞUN SEÇTİĞİ PARÇALARI KULLAN: Kullanıcının belirttiği parçalar dışındaki parçaları devreye dahil etme! (Arduino Uno her zaman mevcuttur).
2. ÇOCUK DOSTU DİL KULLAN:
   - Asla 'anot', 'katot', 'pull-up', 'pull-down', 'mikrodenetleyici registırları' gibi soyut/karmaşık terimler kullanma.
   - Bunun yerine: 'uzun bacak (artı enerji +)', 'kısa bacak (eksi dönüş yolu GND)', 'tetik pini', 'yankı pini', 'sinyal pini' gibi somut ve sevimli terimler kullan.
3. KOD MİMARİSİ:
   - Üretilen `arduino_kodu`, `arduino:avr:uno` kartı için standart Arduino çekirdeğinde harici kütüphane indirmeye gerek kalmadan doğrudan derlenebilir olmalıdır.
   - Sadece Servo motor varsa standart `<Servo.h>` kütüphanesini kullanabilirsin.
   - Koda her zaman `Serial.begin(9600);` ve döngüde sensör değerlerini anlaşılır Türkçe mesajlarla basan `Serial.println(...)` satırları ekle (örn: `Serial.print("Mesafe: "); Serial.println(mesafe);`).
4. KABLO RENKLERİ STANDARDI:
   - 5V veya Pozitif Güç: '#EF4444' (Kırmızı)
   - GND veya Toprak/Negatif: '#1F2937' (Koyu Füme/Siyah)
   - Bilgi / Sinyal / Sensör: '#3B82F6' (Mavi), '#10B981' (Yeşil), '#F59E0B' (Sarı/Turuncu)
5. ÇIKTI FORMATI:
   - Çıktın KESİNLİKLE belirtilen JSON şemasına uygun geçerli bir JSON nesnesi olmalıdır.
   - Markdown kod blokları (```json ... ```) olmadan veya temizlenebilir biçimde saf JSON döndür.
"""


def get_llm_model_and_key():
    """Çevre değişkenlerinden LLM modelini ve anahtarını alır."""
    gemini_key = os.getenv("GEMINI_API_KEY")
    openai_key = os.getenv("OPENAI_API_KEY")
    model = os.getenv("LLM_MODEL")

    if not model:
        if gemini_key:
            model = "gemini/gemini-1.5-flash"
        elif openai_key:
            model = "gpt-4o-mini"
        else:
            model = "gemini/gemini-1.5-flash"

    return model, gemini_key or openai_key


def generate_project_with_ai(prompt: str, inventory: List[str], api_key: Optional[str] = None, model_name: Optional[str] = None) -> ProjectResponse:
    """
    Kullanıcının isteği ve envanterine göre AI ile proje üretir.
    Eğer API anahtarı yoksa veya istek başarısız olursa pedagojik mock projelerden eşleştirir.
    """
    # 1. API anahtarı ve model belirleme
    env_model, env_key = get_llm_model_and_key()
    active_key = api_key or env_key
    active_model = model_name or env_model

    # Eğer API anahtarı girilmemişse zekice mock eşleştirme yap
    if not active_key or active_key.strip() == "your_gemini_api_key_here":
        lower_prompt = prompt.lower()
        if any(w in lower_prompt for w in ["mesafe", "park", "engel", "yarasa", "hcsr04", "korna", "buzzer"]):
            return MOCK_PROJECTS["park_sensoru"]
        else:
            return MOCK_PROJECTS["gece_lambasi"]

    # 2. LLM çağrısı (LiteLLM veya OpenAI uyumlu SDK)
    try:
        import litellm
        
        # API anahtarını ayarla
        if "gemini" in active_model.lower():
            os.environ["GEMINI_API_KEY"] = active_key
        else:
            os.environ["OPENAI_API_KEY"] = active_key

        user_content = f"""KULLANICI PROJE HAYALİ:
"{prompt}"

ÇOCUĞUN ELİNDEKİ PARÇALAR (ENVANTER):
{json.dumps(inventory, ensure_ascii=False)}

Lütfen bu hayali gerçekleştirecek projeyi tam JSON şemasına uygun olarak üret."""

        json_schema = ProjectResponse.model_json_schema()

        response = litellm.completion(
            model=active_model,
            messages=[
                {"role": "system", "content": SYSTEM_PROMPT},
                {"role": "user", "content": user_content}
            ],
            response_format={"type": "json_object", "schema": json_schema},
            temperature=0.3
        )

        content = response.choices[0].message.content
        # Markdown kod bloklarını temizle
        clean_content = re.sub(r"^```json\s*", "", content.strip())
        clean_content = re.sub(r"```$", "", clean_content).strip()

        data = json.loads(clean_content)
        return ProjectResponse(**data)

    except Exception as e:
        print(f"[AI Service Uyarı] LLM çağrısı başarısız oldu ({e}). Akıllı Mock Proje devreye alınıyor.")
        lower_prompt = prompt.lower()
        if any(w in lower_prompt for w in ["mesafe", "park", "engel", "yarasa", "hcsr04", "korna"]):
            return MOCK_PROJECTS["park_sensoru"]
        return MOCK_PROJECTS["gece_lambasi"]


def fix_arduino_code(code: str, error_message: str, project_context: str = "") -> str:
    """
    Self-Healing mekanizması:
    Eğer arduino-cli derleme hatası verirse, hatayı ve mevcut kodu LLM'e göndererek
    hatasız, doğrudan arduino:avr:uno kartında derlenebilen C++ kodunu geri alır.
    """
    env_model, env_key = get_llm_model_and_key()
    if not env_key or env_key == "your_gemini_api_key_here":
        # Temel otomatik düzeltmeler (eksik noktalı virgül veya include)
        return code

    try:
        import litellm
        
        prompt = f"""Bir Arduino Uno C++ kodunu derlerken şu derleme hatasını aldık:
HATA MESAJI:
{error_message}

HATALI KOD:
```cpp
{code}
```

PROJE AMACI:
{project_context}

Lütfen bu hatayı gider ve 'arduino:avr:uno' için harici kütüphane gerektirmeyen (Servo hariç) TAM ve HATASIZ C++ kodunu döndür.
SADECE ve SADECE C++ kodunu döndür, başka hiçbir açıklama yazma."""

        response = litellm.completion(
            model=env_model,
            messages=[
                {"role": "system", "content": "Sen kıdemli bir gömülü sistemler ve Arduino C++ uzmanısın. Sadece düzeltilmiş C++ kodunu saf metin olarak döndürürsün."},
                {"role": "user", "content": prompt}
            ],
            temperature=0.1
        )

        fixed = response.choices[0].message.content.strip()
        fixed = re.sub(r"^```cpp\s*", "", fixed)
        fixed = re.sub(r"^```\s*", "", fixed)
        fixed = re.sub(r"```$", "", fixed).strip()
        return fixed
    except Exception as e:
        print(f"[Self-Healing Hata] Otomatik kod tamiri başarısız: {e}")
        return code

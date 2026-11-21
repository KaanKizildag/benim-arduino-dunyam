from typing import List, Optional, Dict, Any
from pydantic import BaseModel, Field, ConfigDict

class NetlistComponent(BaseModel):
    id: str = Field(..., description="Bileşenin tekil kimliği, örn: led1, r1, ldr1, buzzer1, btn1, servo1, hcsr1, pot1")
    type: str = Field(
        ...,
        description="Wokwi eleman tipi: wokwi-led, wokwi-resistor, wokwi-photoresistor, wokwi-photoresistor-sensor, wokwi-buzzer, wokwi-pushbutton, wokwi-servo, wokwi-hc-sr04, wokwi-potentiometer"
    )
    props: Optional[Dict[string, Any] if False else Dict[str, Any]] = Field(
        default_factory=dict,
        description="Bileşen özellikleri, örn: {'color': 'red'}, {'value': '220'}"
    )
    label: str = Field(..., description="Çocuk dostu Türkçe etiket, örn: 'Kırmızı LED', '220Ω Direnç'")

class NetlistConnection(BaseModel):
    model_config = ConfigDict(populate_by_name=True)
    from_pin: str = Field(..., alias="from", description="Bağlantı başlangıç ucu: örn: uno.D13, r1.1, ldr1.VCC, btn1.1")
    to_pin: str = Field(..., alias="to", description="Bağlantı hedef ucu: örn: r1.1, led1.A, GND, 5V, uno.A0")
    color: Optional[str] = Field(default="orange", description="Kablo rengi, örn: red, orange, blue, green, yellow, black")

class CircuitNetlist(BaseModel):
    board: str = Field(default="arduino-uno", description="Ana kart tipi, örn: arduino-uno")
    components: List[NetlistComponent] = Field(..., description="Devredeki fiziksel bileşenlerin listesi")
    connections: List[NetlistConnection] = Field(
        ...,
        description="Bileşenler ve pinler arası mantıksal bağlantılar (ASLA BREADBOARD DELİĞİ VEYA KOORDİNAT İÇERMEZ)"
    )

class BaglantiAdimi(BaseModel):
    adim_no: int = Field(..., description="Bağlantı sırası (1, 2, 3...)")
    talimat: str = Field(..., description="Çocuğun anlayacağı dilde net talimat.")
    ipucu: str = Field(..., description="Eğlenceli veya koruyucu ipucu.")
    kaynak_parca: str = Field(..., description="Örn: ARDUINO_UNO, BREADBOARD, LED_RED, RESISTOR_220")
    kaynak_pin: str = Field(..., description="Örn: D13, GND, 5V")
    hedef_parca: str = Field(..., description="Bağlanacak hedef parça")
    hedef_pin: str = Field(..., description="Bağlanacak hedef pin")
    kablo_rengi: str = Field(default="#EF4444", description="Kablo rengi HEX kodu")

class AkisAdimi(BaseModel):
    gozlemle: str = Field(..., description="1. GÖZLEMLE: Sensörün neyi izlediğini anlatır.")
    karar_ver: str = Field(..., description="2. KARAR VER: Koşulu belirtir.")
    evet_sonucu: str = Field(..., description="3. EVET: Karar 'Evet' ise ne olacağını belirtir.")
    hayir_sonucu: str = Field(..., description="4. HAYIR: Karar 'Hayır' ise ne olacağını belirtir.")


class AkisDugumu(BaseModel):
    id: str = Field(..., description="Düğüm tekil kimliği, örn: n1, n2")
    tip: str = Field(
        ...,
        description="Düğüm tipi: baslangic | kurulum | oku | karar | eylem | bekle | dongu | bitis"
    )
    metin: str = Field(..., description="Çocuk dostu Türkçe adım açıklaması")
    parcalar: List[str] = Field(
        default_factory=list,
        description="Bu adımda kullanılan gerçek netlist bileşen id'leri, örn: ['led1', 'ldr1']"
    )


class AkisBaglantisi(BaseModel):
    kaynak: str = Field(..., description="Kaynak düğüm id'si")
    hedef: str = Field(..., description="Hedef düğüm id'si")
    etiket: Optional[str] = Field(
        default=None,
        description="Dal etiketi: 'Evet', 'Hayır', 'F (İleri)', 'Sol > Sağ' veya null"
    )


class AkisDiyagrami(BaseModel):
    dugumler: List[AkisDugumu] = Field(..., description="Akış diyagramı düğümleri (3-12 adet)")
    baglantilar: List[AkisBaglantisi] = Field(..., description="Düğümler arası yönlü bağlantılar")

class PinBindingInfo(BaseModel):
    uno_pin: str = Field(..., description="Arduino pini, örn: D13, A0, D9")
    component_id: str = Field(..., description="Bağlı olduğu bileşen kimliği, örn: led1, ldr1, servo1")
    component_label: str = Field(..., description="Bileşenin Türkçe adı, örn: Kırmızı LED")
    component_type: str = Field(..., description="Wokwi bileşen tipi")
    pin_name: str = Field(..., description="Bileşen pini, örn: A, AO, PWM, TRIG")
    via_component: Optional[str] = Field(default=None, description="Arada seri direnç varsa kimliği, örn: r1 (220Ω Direnç)")
    role: str = Field(default="OUTPUT", description="INPUT veya OUTPUT")

class LogicVerificationReport(BaseModel):
    is_valid: bool = Field(default=True, description="Kod ve akış diyagramı hatasız ve kablolamayla uyumlu mu?")
    syntax_ok: bool = Field(default=True, description="Arduino C++ kodu sözdizimi geçerli mi?")
    pins_matched: bool = Field(default=True, description="Koddaki pinler ile kablolamadaki (netlist) pinler birebir uyumlu mu?")
    flow_complete: bool = Field(default=True, description="Akış diyagramının 4 adımı da eksiksiz mi?")
    auto_repaired: bool = Field(default=False, description="Uyumsuzluk tespit edilip otomatik onarıldı mı?")
    pin_bindings: List[PinBindingInfo] = Field(default_factory=list, description="Netlist'ten çıkarılan ve kodla eşleştirilen pin tablosu")
    checks: List[str] = Field(default_factory=list, description="Yapılan doğrulama kontrollerinin çocuk dostu özeti")
    warnings: List[str] = Field(default_factory=list, description="Varsa uyarılar")

class WiringDesignResponse(BaseModel):
    proje_adi: str = Field(..., description="Çocuklar için heyecan verici proje adı")
    karsilama_mesaji: str = Field(..., description="AI asistanın çocuğu motive eden kısa ve sevimli karşılama mesajı")
    gerekli_parcalar: List[str] = Field(..., description="Kullanılacak parçaların envanter kodları")
    netlist: CircuitNetlist = Field(..., description="Hatasız ve doğrulanmış Netlist kablolama şeması")
    baglanti_adimlari: Optional[List[BaglantiAdimi]] = Field(default_factory=list, description="Adım adım bağlantı listesi")
    guvenlik_notu: Optional[str] = Field(default="Elektronik parçaları bağlarken nazik ol!", description="Çocuğa güvenlik hatırlatması")
    pin_bindings: List[PinBindingInfo] = Field(default_factory=list, description="Hangi Arduino pininin hangi parçaya bağlandığının özeti")
    uyarilar: Optional[List[str]] = Field(default_factory=list, description="Normalizasyon ve kablolama doğrulama notları")

class LogicDesignResponse(BaseModel):
    akis_adimlari: Optional[AkisAdimi] = Field(default=None, description="Geriye dönük uyumluluk için 4 alanlı özet")
    akis_diyagrami: Optional[AkisDiyagrami] = Field(default=None, description="Esnek düğüm/kenar akış diyagramı")
    arduino_kodu: str = Field(..., description="Kablolamadaki pinlerle %100 uyumlu Arduino C++ kodu")
    verification: LogicVerificationReport = Field(..., description="Kod ve akış diyagramının kablolama ile uyumluluk teyit raporu")

class ProjeTasarimi(BaseModel):
    proje_adi: str = Field(..., description="Çocuklar için heyecan verici proje adı")
    karsilama_mesaji: str = Field(..., description="AI asistanın çocuğu motive eden kısa ve sevimli karşılama mesajı")
    gerekli_parcalar: List[str] = Field(..., description="Kullanılacak parçaların envanter kodları")
    netlist: Optional[CircuitNetlist] = Field(
        default=None,
        description="Standart Netlist Şeması (LLM Koordinat Yasağı: Asla delik veya piksel içermez)"
    )
    baglanti_adimlari: Optional[List[BaglantiAdimi]] = Field(
        default_factory=list,
        description="Adım adım devre bağlantı kılavuzu"
    )
    akis_adimlari: Optional[AkisAdimi] = Field(default=None, description="Eski 4 alanlı akış özeti (geriye dönük uyumluluk)")
    akis_diyagrami: Optional[AkisDiyagrami] = Field(default=None, description="Esnek düğüm/kenar akış diyagramı")
    arduino_kodu: str = Field(..., description="Arka planda derlenecek Arduino C++ kodu")
    guvenlik_notu: Optional[str] = Field(
        default="Elektronik parçaları bağlarken nazik ol!",
        description="Çocuğa güvenlik hatırlatması"
    )
    uyarilar: Optional[List[str]] = Field(
        default_factory=list,
        description="Netlist normalizasyon ve kod-pin uyum uyarıları"
    )
    verification: Optional[LogicVerificationReport] = Field(
        default=None,
        description="Kablolama ve kod doğrulama raporu"
    )

class SavedProjectEntry(BaseModel):
    id: str = Field(..., description="Proje benzersiz kimliği")
    created_at: str = Field(..., description="Oluşturulma tarihi/saati")
    prompt: str = Field(default="", description="Çocuğun yazdığı proje hayali")
    is_preset: bool = Field(default=False, description="Hazır kurgulanmış örnek proje mi?")
    badge: Optional[str] = Field(default="AI Tasarımım ✨", description="Proje rozeti")
    difficulty: Optional[str] = Field(default="Kolay Seviye", description="Zorluk seviyesi")
    project: ProjeTasarimi = Field(..., description="Projenin tüm devre, akış ve kod verisi")

class AILogEntry(BaseModel):
    id: str = Field(..., description="Log benzersiz kimliği")
    timestamp: str = Field(..., description="İstek zamanı")
    stage: str = Field(..., description="Aşama adı: 1. Aşama (Kablolama), 2. Aşama (Akış & Kod), Repair vb.")
    model: str = Field(..., description="Kullanılan AI modeli")
    provider: str = Field(..., description="ollama veya litellm")
    duration_ms: int = Field(default=0, description="Yanıt süresi (milisaniye)")
    status: str = Field(default="SUCCESS", description="SUCCESS, REPAIRED, FALLBACK, ERROR")
    user_goal: str = Field(default="", description="Kullanıcının yazdığı orijinal proje fikri")
    system_prompt: str = Field(default="", description="Yapay zekaya gönderilen sistem talimatı")
    user_prompt: str = Field(default="", description="Yapay zekaya gönderilen kullanıcı isteği")
    raw_response: str = Field(default="", description="Yapay zekadan dönen ham yanıt")
    processed_output: Optional[Dict[str, Any]] = Field(default=None, description="Doğrulanmış ve normalize edilmiş çıktı")
    notes: List[str] = Field(default_factory=list, description="Normalizasyon, filtreleme veya hata notları")

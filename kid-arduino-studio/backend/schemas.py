from typing import List, Optional, Dict, Any
from pydantic import BaseModel, Field, ConfigDict

class NetlistComponent(BaseModel):
    id: str = Field(..., description="Bileşenin tekil kimliği, örn: led1, r1, ldr1, buzzer1, btn1, servo1")
    type: str = Field(..., description="Wokwi eleman tipi, örn: wokwi-led, wokwi-resistor, wokwi-photoresistor-sensor, wokwi-buzzer, wokwi-pushbutton, wokwi-servo, wokwi-hc-sr04, wokwi-potentiometer")
    props: Optional[Dict[str, Any]] = Field(default_factory=dict, description="Bileşen özellikleri, örn: {'color': 'red'}, {'value': '220'}")
    label: str = Field(..., description="Çocuk dostu Türkçe etiket, örn: 'Kırmızı LED', '220Ω Direnç'")

class NetlistConnection(BaseModel):
    model_config = ConfigDict(populate_by_name=True)
    from_pin: str = Field(..., alias="from", description="Bağlantı başlangıç ucu: örn: uno.D13, r1.1, ldr1.VCC, btn1.1")
    to_pin: str = Field(..., alias="to", description="Bağlantı hedef ucu: örn: r1.1, led1.A, GND, 5V, uno.A0")
    color: Optional[str] = Field(default="orange", description="Kablo rengi, örn: red, orange, blue, green, yellow, black")

class CircuitNetlist(BaseModel):
    board: str = Field(default="arduino-uno", description="Ana kart tipi, örn: arduino-uno")
    components: List[NetlistComponent] = Field(..., description="Devredeki fiziksel bileşenlerin listesi")
    connections: List[NetlistConnection] = Field(..., description="Bileşenler ve pinler arası mantıksal bağlantılar (ASLA BREADBOARD DELİĞİ VEYA KOORDİNAT İÇERMEZ)")

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

class ProjeTasarimi(BaseModel):
    proje_adi: str = Field(..., description="Çocuklar için heyecan verici proje adı")
    karsilama_mesaji: str = Field(..., description="AI asistanın çocuğu motive eden kısa ve sevimli karşılama mesajı")
    gerekli_parcalar: List[str] = Field(..., description="Kullanılacak parçaların envanter kodları")
    netlist: Optional[CircuitNetlist] = Field(default=None, description="Standart Netlist Şeması (LLM Koordinat Yasağı: Asla delik veya piksel içermez)")
    baglanti_adimlari: Optional[List[BaglantiAdimi]] = Field(default_factory=list, description="Adım adım devre bağlantı kılavuzu")
    akis_adimlari: AkisAdimi = Field(..., description="Sistemin mantıksal akış hikayesi")
    arduino_kodu: str = Field(..., description="Arka planda derlenecek Arduino C++ kodu")
    guvenlik_notu: Optional[str] = Field(default="Elektronik parçaları bağlarken nazik ol!", description="Çocuğa güvenlik hatırlatması")

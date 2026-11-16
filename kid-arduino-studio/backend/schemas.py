from typing import List, Optional
from pydantic import BaseModel, Field

class BaglantiAdimi(BaseModel):
    adim_no: int = Field(..., description="Bağlantı sırası (1, 2, 3...)")
    talimat: str = Field(..., description="Çocuğun anlayacağı dilde net talimat. Örn: 'Kırmızı LED'in uzun bacağını Arduino'daki D13 deliğine tak.'")
    ipucu: str = Field(..., description="Eğlenceli veya koruyucu ipucu. Örn: 'LED'in yanmaması için araya direnç koyalım!'")
    kaynak_parca: str = Field(..., description="Örn: ARDUINO_UNO, BREADBOARD, LED_RED, RESISTOR_220, BUZZER, LDR_SENSOR, HCSR04")
    kaynak_pin: str = Field(..., description="Örn: D13, GND, 5V, ANODE, CATHODE, PIN_1, PIN_2, VCC, TRIG, ECHO, A5, E5, RAIL_5V, RAIL_GND")
    hedef_parca: str = Field(..., description="Bağlanacak hedef parça (örn: BREADBOARD, ARDUINO_UNO)")
    hedef_pin: str = Field(..., description="Bağlanacak hedef pin (örn: A5, RAIL_GND, D13)")
    kablo_rengi: str = Field(..., description="Kablo rengi HEX kodu (Örn: #EF4444 (kırmızı), #3B82F6 (mavi), #10B981 (yeşil), #1F2937 (siyah/füme), #F59E0B (sarı))")

class AkisAdimi(BaseModel):
    gozlemle: str = Field(..., description="1. GÖZLEMLE: Sensörün neyi izlediğini anlatır. Örn: 'Odadaki ışığı her an takip et'")
    karar_ver: str = Field(..., description="2. KARAR VER: Koşulu belirtir. Örn: 'Hava karardı mı diye sor'")
    evet_sonucu: str = Field(..., description="3. EVET (Karanlık): Karar 'Evet' ise ne olacağını belirtir. Örn: 'Lambayı Yak!'")
    hayir_sonucu: str = Field(..., description="4. HAYIR (Aydınlık): Karar 'Hayır' ise ne olacağını belirtir. Örn: 'Lambayı Söndür!'")

class ProjeTasarimi(BaseModel):
    proje_adi: str = Field(..., description="Çocuklar için heyecan verici proje adı")
    karsilama_mesaji: str = Field(..., description="AI asistanın çocuğu motive eden kısa ve sevimli karşılama mesajı")
    gerekli_parcalar: List[str] = Field(..., description="Kullanılacak parçaların envanter kodları")
    baglanti_adimlari: List[BaglantiAdimi] = Field(..., description="Adım adım devre bağlantı kılavuzu")
    akis_adimlari: AkisAdimi = Field(..., description="Sistemin mantıksal, interaktif akış hikayesi")
    arduino_kodu: str = Field(..., description="Arka planda derlenecek, hiçbir harici kütüphaneye ihtiyaç duymayan tam Arduino C++ kodu")
    guvenlik_notu: Optional[str] = Field(default="Elektronik parçaları bağlarken nazik ol!", description="Çocuğa güvenlik hatırlatması")

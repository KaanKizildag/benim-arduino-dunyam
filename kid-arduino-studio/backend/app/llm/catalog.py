"""
Wokwi elektronik parça kataloğu, pin sözlükleri ve token tasarruflu dinamik parça filtreleme.
"""

from typing import Dict, Set, List, Tuple, Optional

# Desteklenen Standart Wokwi Bileşenleri ve Pin Sözlüğü
SUPPORTED_TYPES_AND_PINS: Dict[str, Set[str]] = {
    "wokwi-resistor": {"1", "2"},
    "wokwi-led": {"A", "C"},
    "wokwi-photoresistor": {"1", "2"},
    "wokwi-photoresistor-sensor": {"VCC", "GND", "AO", "DO"},
    "wokwi-potentiometer": {"GND", "SIG", "VCC"},
    "wokwi-buzzer": {"1", "2"},
    "wokwi-pushbutton": {"1", "2"},
    "wokwi-servo": {"V+", "GND", "PWM"},
    "wokwi-hc-sr04": {"VCC", "GND", "TRIG", "ECHO"},
    "wokwi-hc-05": {"VCC", "GND", "TXD", "RXD", "EN", "STATE"},
    "wokwi-hc-06": {"VCC", "GND", "TXD", "RXD"},
    "wokwi-l293d": {"VCC1", "VCC2", "GND", "EN1", "EN2", "IN1", "IN2", "IN3", "IN4", "OUT1", "OUT2", "OUT3", "OUT4"},
    "wokwi-l298n": {"VCC", "GND", "5V", "ENA", "ENB", "IN1", "IN2", "IN3", "IN4", "OUT1", "OUT2", "OUT3", "OUT4"},
    "wokwi-dc-motor": {"1", "2"},
    "wokwi-pir-motion-sensor": {"VCC", "GND", "OUT"},
    "wokwi-dht22": {"VCC", "GND", "SDA"},
    "wokwi-analog-joystick": {"VCC", "GND", "VERT", "HORZ", "SEL"},
    "wokwi-relay-module": {"VCC", "GND", "IN", "COM", "NO", "NC"},
    "wokwi-rgb-led": {"R", "G", "B", "COM"},
    "wokwi-lcd1602": {"VCC", "GND", "SDA", "SCL"},
    "wokwi-ssd1306": {"VCC", "GND", "SDA", "SCL"},
    "wokwi-soil-moisture-sensor": {"VCC", "GND", "AO", "DO"},
    "wokwi-rain-sensor": {"VCC", "GND", "AO", "DO"},
    "wokwi-water-sensor": {"VCC", "GND", "AO", "DO"},
    "wokwi-gas-sensor": {"VCC", "GND", "AO", "DO"},
    "wokwi-flame-sensor": {"VCC", "GND", "AO", "DO"},
    "wokwi-small-sound-sensor": {"VCC", "GND", "AO", "DO"},
    "wokwi-ir-receiver": {"VCC", "GND", "DAT"},
    "wokwi-ntc-temperature-sensor": {"VCC", "GND", "OUT"},
}

TYPE_ALIASES: Dict[str, str] = {
    "led": "wokwi-led",
    "led_red": "wokwi-led",
    "led-red": "wokwi-led",
    "red-led": "wokwi-led",
    "led_green": "wokwi-led",
    "led-green": "wokwi-led",
    "green-led": "wokwi-led",
    "led_yellow": "wokwi-led",
    "led-yellow": "wokwi-led",
    "yellow-led": "wokwi-led",
    "led_blue": "wokwi-led",
    "led-blue": "wokwi-led",
    "blue-led": "wokwi-led",
    "rgb-led": "wokwi-rgb-led",
    "rgb_led": "wokwi-rgb-led",
    "resistor": "wokwi-resistor",
    "resistor_220": "wokwi-resistor",
    "resistor_10k": "wokwi-resistor",
    "resistor-220": "wokwi-resistor",
    "resistor-10k": "wokwi-resistor",
    "photoresistor": "wokwi-photoresistor",
    "ldr": "wokwi-photoresistor",
    "ldr_discrete": "wokwi-photoresistor",
    "photoresistor_sensor": "wokwi-photoresistor-sensor",
    "ldr_module": "wokwi-photoresistor-sensor",
    "potentiometer": "wokwi-potentiometer",
    "pot": "wokwi-potentiometer",
    "buzzer": "wokwi-buzzer",
    "pushbutton": "wokwi-pushbutton",
    "button": "wokwi-pushbutton",
    "btn": "wokwi-pushbutton",
    "servo": "wokwi-servo",
    "sg90": "wokwi-servo",
    "servo_sg90": "wokwi-servo",
    "hc-sr04": "wokwi-hc-sr04",
    "hcsr04": "wokwi-hc-sr04",
    "ultrasonic": "wokwi-hc-sr04",
    "hc-05": "wokwi-hc-05",
    "hc05": "wokwi-hc-05",
    "bluetooth": "wokwi-hc-05",
    "hc-06": "wokwi-hc-06",
    "hc06": "wokwi-hc-06",
    "l293d": "wokwi-l293d",
    "l298n": "wokwi-l298n",
    "dc-motor": "wokwi-dc-motor",
    "dcmotor": "wokwi-dc-motor",
    "motor": "wokwi-dc-motor",
    "pir": "wokwi-pir-motion-sensor",
    "dht22": "wokwi-dht22",
    "dht11": "wokwi-dht22",
    "joystick": "wokwi-analog-joystick",
    "relay": "wokwi-relay-module",
    "lcd1602": "wokwi-lcd1602",
    "lcd": "wokwi-lcd1602",
    "ssd1306": "wokwi-ssd1306",
    "oled": "wokwi-ssd1306",
    "soil": "wokwi-soil-moisture-sensor",
    "rain": "wokwi-rain-sensor",
    "water": "wokwi-water-sensor",
    "gas": "wokwi-gas-sensor",
    "flame": "wokwi-flame-sensor",
    "sound": "wokwi-small-sound-sensor",
    "ntc": "wokwi-ntc-temperature-sensor",
}

COMPONENT_PROMPT_DOCS: Dict[str, str] = {
    "wokwi-resistor": "- wokwi-resistor: r1.1, r1.2 (props:{\"value\":\"220\"} veya {\"value\":\"10000\"})",
    "wokwi-led": "- wokwi-led: led1.A, led1.C (props:{\"color\":\"red\"|\"green\"|\"yellow\"|\"blue\"})",
    "wokwi-rgb-led": "- wokwi-rgb-led: rgb1.R, rgb1.G, rgb1.B, rgb1.COM",
    "wokwi-photoresistor": "- wokwi-photoresistor (2 bacaklı LDR): ldr1.1, ldr1.2 (mutlaka 10k dirençle gerilim bölücü kur)",
    "wokwi-photoresistor-sensor": "- wokwi-photoresistor-sensor (4 pinli LDR modülü): ldr1.VCC, ldr1.GND, ldr1.AO, ldr1.DO",
    "wokwi-potentiometer": "- wokwi-potentiometer: pot1.GND, pot1.SIG, pot1.VCC",
    "wokwi-buzzer": "- wokwi-buzzer: buzzer1.1, buzzer1.2",
    "wokwi-pushbutton": "- wokwi-pushbutton: btn1.1, btn1.2",
    "wokwi-servo": "- wokwi-servo: servo1.V+, servo1.GND, servo1.PWM",
    "wokwi-hc-sr04": "- wokwi-hc-sr04 (Mesafe Sensörü): hcsr1.VCC, hcsr1.GND, hcsr1.TRIG, hcsr1.ECHO",
    "wokwi-hc-05": "- wokwi-hc-05 (Bluetooth): hc05.VCC, hc05.GND, hc05.TXD, hc05.RXD",
    "wokwi-l293d": "- wokwi-l293d (Motor Sürücü): l293d.VCC1, l293d.VCC2, l293d.GND, l293d.EN1, l293d.EN2, l293d.IN1, l293d.IN2, l293d.IN3, l293d.IN4, l293d.OUT1, l293d.OUT2, l293d.OUT3, l293d.OUT4",
    "wokwi-l298n": "- wokwi-l298n (Motor Sürücü): l298n.VCC, l298n.GND, l298n.ENA, l298n.ENB, l298n.IN1, l298n.IN2, l298n.IN3, l298n.IN4, l298n.OUT1, l298n.OUT2, l298n.OUT3, l298n.OUT4",
    "wokwi-dc-motor": "- wokwi-dc-motor: motor1.1, motor1.2 (Sürücü OUT pinlerine bağlanır)",
    "wokwi-pir-motion-sensor": "- wokwi-pir-motion-sensor: pir1.VCC, pir1.GND, pir1.OUT",
    "wokwi-dht22": "- wokwi-dht22: dht1.VCC, dht1.GND, dht1.SDA",
    "wokwi-analog-joystick": "- wokwi-analog-joystick: joy1.VCC, joy1.GND, joy1.VERT, joy1.HORZ, joy1.SEL",
    "wokwi-relay-module": "- wokwi-relay-module: relay1.VCC, relay1.GND, relay1.IN",
    "wokwi-lcd1602": "- wokwi-lcd1602: lcd1.VCC, lcd1.GND, lcd1.SDA (uno.A4), lcd1.SCL (uno.A5)",
    "wokwi-ssd1306": "- wokwi-ssd1306: oled1.VCC, oled1.GND, oled1.SDA (uno.A4), oled1.SCL (uno.A5)",
    "wokwi-soil-moisture-sensor": "- wokwi-soil-moisture-sensor: soil1.VCC, soil1.GND, soil1.AO, soil1.DO",
    "wokwi-rain-sensor": "- wokwi-rain-sensor: rain1.VCC, rain1.GND, rain1.AO, rain1.DO",
    "wokwi-water-sensor": "- wokwi-water-sensor: water1.VCC, water1.GND, water1.AO, water1.DO",
    "wokwi-gas-sensor": "- wokwi-gas-sensor: gas1.VCC, gas1.GND, gas1.AO, gas1.DO",
    "wokwi-flame-sensor": "- wokwi-flame-sensor: flame1.VCC, flame1.GND, flame1.AO, flame1.DO",
    "wokwi-small-sound-sensor": "- wokwi-small-sound-sensor: sound1.VCC, sound1.GND, sound1.AO, sound1.DO",
    "wokwi-ir-receiver": "- wokwi-ir-receiver: ir1.VCC, ir1.GND, ir1.DAT",
    "wokwi-ntc-temperature-sensor": "- wokwi-ntc-temperature-sensor: ntc1.VCC, ntc1.GND, ntc1.OUT",
}

def resolve_component_type(raw_type: str) -> str:
    """Girilen ham komponent tipini standart Wokwi adına normalize eder."""
    cleaned = raw_type.strip().lower()
    if cleaned in SUPPORTED_TYPES_AND_PINS:
        return cleaned
    return TYPE_ALIASES.get(cleaned, cleaned)

def get_component_meta(comp_identifier: str, comp_type: str = "") -> Tuple[str, str]:
    """Bileşen ID veya tipine göre çocuk dostu Türkçe etiket ve emoji ikonu döner."""
    ctype = resolve_component_type(comp_type or comp_identifier)
    
    meta_map = {
        "wokwi-photoresistor": ("2 Bacaklı LDR (Işık Sensörü)", "☀️"),
        "wokwi-photoresistor-sensor": ("LDR Işık Sensör Modülü", "🎛️"),
        "wokwi-servo": ("SG90 Servo Motor", "🦾"),
        "wokwi-hc-sr04": ("HC-SR04 Mesafe Sensörü", "🦇"),
        "wokwi-led": ("LED Işık Lambası", "💡"),
        "wokwi-rgb-led": ("RGB Renkli LED", "🌈"),
        "wokwi-resistor": ("Direnç", "🟤"),
        "wokwi-hc-05": ("HC-05 Bluetooth Modülü", "📶"),
        "wokwi-hc-06": ("HC-06 Bluetooth Modülü", "📶"),
        "wokwi-l293d": ("L293D Motor Sürücü", "🚗"),
        "wokwi-l298n": ("L298N Motor Sürücü", "🏎️"),
        "wokwi-dc-motor": ("5V DC Motor", "🌀"),
        "wokwi-buzzer": ("Buzzer (Hoparlör)", "🔊"),
        "wokwi-pushbutton": ("Push Buton (Düğme)", "🔘"),
        "wokwi-potentiometer": ("10kΩ Potansiyometre", "🎚️"),
        "wokwi-relay-module": ("5V Röle Modülü", "⚡"),
        "wokwi-pir-motion-sensor": ("PIR Hareket Sensörü", "🚶"),
        "wokwi-dht22": ("DHT22 Sıcaklık & Nem", "🌡️"),
        "wokwi-lcd1602": ("16x2 I2C LCD Ekran", "📟"),
        "wokwi-ssd1306": ("I2C OLED Ekran", "📺"),
        "wokwi-soil-moisture-sensor": ("Toprak Nem Sensörü", "🌱"),
        "wokwi-rain-sensor": ("Yağmur Sensörü", "🌧️"),
        "wokwi-water-sensor": ("Su Seviye Sensörü", "💧"),
        "wokwi-gas-sensor": ("MQ-2 Gaz Sensörü", "🚨"),
        "wokwi-flame-sensor": ("Alev Sensörü", "🔥"),
        "wokwi-small-sound-sensor": ("Ses Algılayıcı Mikrofon", "🎙️"),
        "wokwi-ir-receiver": ("Kızılötesi (IR) Alıcı", "📡"),
        "wokwi-analog-joystick": ("Analog Joystick", "🕹️"),
        "wokwi-ntc-temperature-sensor": ("NTC Sıcaklık Sensörü", "🌡️"),
    }
    return meta_map.get(ctype, (f"Elektronik Modül ({comp_type or comp_identifier})", "🔌"))

def get_filtered_component_docs(inventory: Optional[List[str]], user_prompt: str) -> str:
    """
    TOKEN TASARRUFU: Kullanıcının envanterinde olan veya promptta adı geçen
    bileşenleri tespit eder ve sisteme yalnızca bu parçaların pin tanımlarını gönderir.
    Gereksiz 20+ parçayı prompttan çıkararak binlerce token tasarruf ettirir.
    """
    # En yaygın temel sensör ve eyleyiciler çantada olmasa bile her zaman promptta yer alır
    selected: Set[str] = {
        "wokwi-resistor",
        "wokwi-led",
        "wokwi-pushbutton",
        "wokwi-buzzer",
        "wokwi-photoresistor",
        "wokwi-servo",
        "wokwi-hc-sr04",
        "wokwi-potentiometer",
    }

    inv_tokens = " ".join((inventory or []) + [user_prompt]).lower()

    keyword_map = {
        "ldr": ["wokwi-photoresistor", "wokwi-photoresistor-sensor"],
        "ışık": ["wokwi-photoresistor", "wokwi-photoresistor-sensor"],
        "isik": ["wokwi-photoresistor", "wokwi-photoresistor-sensor"],
        "karanlık": ["wokwi-photoresistor"],
        "gece": ["wokwi-photoresistor"],
        "servo": ["wokwi-servo"],
        "mesafe": ["wokwi-hc-sr04"],
        "hcsr": ["wokwi-hc-sr04"],
        "ultrasonik": ["wokwi-hc-sr04"],
        "park": ["wokwi-hc-sr04"],
        "motor": ["wokwi-l293d", "wokwi-dc-motor"],
        "araba": ["wokwi-l293d", "wokwi-dc-motor"],
        "l293": ["wokwi-l293d", "wokwi-dc-motor"],
        "l298": ["wokwi-l298n", "wokwi-dc-motor"],
        "pot": ["wokwi-potentiometer"],
        "ayarlı": ["wokwi-potentiometer"],
        "sıcaklık": ["wokwi-dht22", "wokwi-ntc-temperature-sensor"],
        "nem": ["wokwi-dht22"],
        "dht": ["wokwi-dht22"],
        "hareket": ["wokwi-pir-motion-sensor"],
        "pir": ["wokwi-pir-motion-sensor"],
        "röle": ["wokwi-relay-module"],
        "relay": ["wokwi-relay-module"],
        "bluetooth": ["wokwi-hc-05"],
        "hc05": ["wokwi-hc-05"],
        "lcd": ["wokwi-lcd1602"],
        "oled": ["wokwi-ssd1306"],
        "ekran": ["wokwi-lcd1602", "wokwi-ssd1306"],
        "rgb": ["wokwi-rgb-led"],
        "joystick": ["wokwi-analog-joystick"],
        "toprak": ["wokwi-soil-moisture-sensor"],
        "yağmur": ["wokwi-rain-sensor"],
        "su": ["wokwi-water-sensor"],
        "gaz": ["wokwi-gas-sensor"],
        "duman": ["wokwi-gas-sensor"],
        "alev": ["wokwi-flame-sensor"],
        "yangın": ["wokwi-flame-sensor"],
        "ses": ["wokwi-small-sound-sensor"],
        "mikrofon": ["wokwi-small-sound-sensor"],
        "ir": ["wokwi-ir-receiver"],
        "kumanda": ["wokwi-ir-receiver"],
    }

    for kw, components in keyword_map.items():
        if kw in inv_tokens:
            for c in components:
                selected.add(c)

    # Seçilen bileşenlerin pin dökümünü oluştur
    lines = [COMPONENT_PROMPT_DOCS[c] for c in selected if c in COMPONENT_PROMPT_DOCS]
    return "\n".join(lines)


def build_one_shot_system_prompt(user_prompt: str, inventory: Optional[List[str]] = None) -> str:
    """
    Kullanıcının isteğine ve envanterine göre optimize edilmiş, gereksiz parça pinlerini
    içermeyen dinamik sistem promptu üretir. Token maliyetini %70+ oranında düşürür.
    """
    component_docs = get_filtered_component_docs(inventory, user_prompt)
    template = """Sen çocuklar için Arduino Uno devre ve C++ kodlama uzmanısın.
Kullanıcının proje isteğine göre TEK BİR JSON nesnesi içinde:
1. "netlist": Sadece kullanıcının istediği parçaları (components) ve eksiksiz pin bağlantılarını (connections)
2. "arduino_kodu": Netlist'teki pinlerle %100 aynı pin numaralarını kullanan, derlenebilir Arduino Uno C++ kodunu
üret. (Akış diyagramı ayrı aşamada koddan otomatik çıkarılacaktır; JSON'a akis_adimlari ekleme.)

KESİN KURALLAR:
1. SADECE İSTENEN PARÇALARI EKLE! Kullanıcının istemediği bileşenleri ekleme.
2. ÇOKLU PARÇA VE GERİLİM BÖLÜCÜ:
   - 2 bacaklı LDR (wokwi-photoresistor) için MUTLAKA 10kΩ dirençle gerilim bölücü kur (ldr.1 -> 5V, ldr.2 -> uno.A*, ldr.2 -> r.1, r.2 -> GND).
   - LED (wokwi-led) için seri 220Ω koruma direnci ekle.
3. Standart parça ve pin tanımları:
__COMPONENT_DOCS__
4. Güç bağlantıları: "to":"5V" veya "to":"GND". Arduino pinleri: "uno.D2".."uno.D13", "uno.A0".."uno.A5".
5. "arduino_kodu" içindeki pinler ile "connections" içindeki pinler BİREBİR AYNI olmalı.
6. C++ kodundaki değişken ve sabitlerde SADECE İngilizce ASCII karakterler kullan (ç, ğ, ı, ö, ş, ü YASAK).

JSON format örneği:
{"proje_adi":"Örnek Proje","karsilama_mesaji":"Harika bir devre!","gerekli_parcalar":["ARDUINO_UNO","LED_RED","RESISTOR_220"],"netlist":{"board":"arduino-uno","components":[{"id":"r1","type":"wokwi-resistor","props":{"value":"220"},"label":"220Ω Direnç"},{"id":"led1","type":"wokwi-led","props":{"color":"red"},"label":"Kırmızı LED"}],"connections":[{"from":"uno.D13","to":"r1.1","color":"orange"},{"from":"r1.2","to":"led1.A","color":"red"},{"from":"led1.C","to":"GND","color":"black"}]},"arduino_kodu":"const int LED = 13;\\nvoid setup() { pinMode(LED, OUTPUT); }\\nvoid loop() { digitalWrite(LED, HIGH); delay(500); digitalWrite(LED, LOW); delay(500); }","guvenlik_notu":"LED önüne koruma direnci bağladık."}
"""
    return template.replace("__COMPONENT_DOCS__", component_docs)


import json
import os
import re
from typing import List, Optional, Dict, Any, Set, Tuple, Callable
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
# Desteklenen Standart Wokwi Bileşenleri ve Pin Sözlüğü
# ---------------------------------------------------------

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
}

TYPE_ALIASES: Dict[str, str] = {
    "wokwi-led": "wokwi-led",
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
    "wokwi-resistor": "wokwi-resistor",
    "resistor": "wokwi-resistor",
    "res": "wokwi-resistor",
    "r": "wokwi-resistor",
    "resistor_220": "wokwi-resistor",
    "resistor_1k": "wokwi-resistor",
    "resistor_10k": "wokwi-resistor",
    "wokwi-photoresistor": "wokwi-photoresistor",
    "photoresistor": "wokwi-photoresistor",
    "ldr_discrete": "wokwi-photoresistor",
    "ldr-discrete": "wokwi-photoresistor",
    "wokwi-photoresistor-sensor": "wokwi-photoresistor-sensor",
    "photoresistor-sensor": "wokwi-photoresistor-sensor",
    "ldr_sensor": "wokwi-photoresistor-sensor",
    "ldr-sensor": "wokwi-photoresistor-sensor",
    "ldr_module": "wokwi-photoresistor-sensor",
    "ldr-module": "wokwi-photoresistor-sensor",
    "ldr": "wokwi-photoresistor",
    "wokwi-potentiometer": "wokwi-potentiometer",
    "potentiometer": "wokwi-potentiometer",
    "pot": "wokwi-potentiometer",
    "wokwi-buzzer": "wokwi-buzzer",
    "buzzer": "wokwi-buzzer",
    "piezo": "wokwi-buzzer",
    "active_buzzer": "wokwi-buzzer",
    "wokwi-pushbutton": "wokwi-pushbutton",
    "pushbutton": "wokwi-pushbutton",
    "push_button": "wokwi-pushbutton",
    "push-button": "wokwi-pushbutton",
    "button": "wokwi-pushbutton",
    "btn": "wokwi-pushbutton",
    "wokwi-servo": "wokwi-servo",
    "servo": "wokwi-servo",
    "servo_sg90": "wokwi-servo",
    "sg90": "wokwi-servo",
    "wokwi-hc-sr04": "wokwi-hc-sr04",
    "hc-sr04": "wokwi-hc-sr04",
    "hcsr04": "wokwi-hc-sr04",
    "ultrasonic": "wokwi-hc-sr04",
}

PIN_ALIASES: Dict[str, Dict[str, str]] = {
    "wokwi-led": {
        "A": "A", "ANODE": "A", "ANOT": "A", "+": "A", "POS": "A", "1": "A",
        "C": "C", "K": "C", "CATHODE": "C", "KATOT": "C", "-": "C", "NEG": "C", "2": "C", "GND": "C",
    },
    "wokwi-resistor": {
        "1": "1", "PIN1": "1", "PIN_1": "1", "P1": "1", "A": "1", "IN": "1", "+": "1",
        "2": "2", "PIN2": "2", "PIN_2": "2", "P2": "2", "B": "2", "OUT": "2", "-": "2",
    },
    "wokwi-photoresistor": {
        "1": "1", "PIN1": "1", "PIN_1": "1", "P1": "1", "A": "1", "VCC": "1", "+": "1",
        "2": "2", "PIN2": "2", "PIN_2": "2", "P2": "2", "B": "2", "GND": "2", "-": "2", "OUT": "2", "SIG": "2", "AO": "2",
    },
    "wokwi-photoresistor-sensor": {
        "VCC": "VCC", "5V": "VCC", "V+": "VCC", "+": "VCC", "1": "VCC",
        "GND": "GND", "-": "GND", "0V": "GND", "2": "GND",
        "DO": "DO", "D0": "DO", "DOUT": "DO", "3": "DO",
        "AO": "AO", "A0": "AO", "AOUT": "AO", "OUT": "AO", "SIG": "AO", "SIGNAL": "AO", "4": "AO",
    },
    "wokwi-potentiometer": {
        "GND": "GND", "1": "GND", "A": "GND", "-": "GND", "PIN1": "GND", "PIN_1": "GND",
        "SIG": "SIG", "2": "SIG", "B": "SIG", "OUT": "SIG", "WIPER": "SIG", "AO": "SIG", "A0": "SIG", "SIGNAL": "SIG", "PIN2": "SIG", "PIN_2": "SIG",
        "VCC": "VCC", "3": "VCC", "C": "VCC", "5V": "VCC", "V+": "VCC", "+": "VCC", "PIN3": "VCC", "PIN_3": "VCC",
    },
    "wokwi-buzzer": {
        "1": "1", "+": "1", "POS": "1", "SIG": "1", "SIGNAL": "1", "A": "1", "ANODE": "1", "VCC": "1", "PIN1": "1", "PIN_1": "1",
        "2": "2", "-": "2", "NEG": "2", "GND": "2", "C": "2", "CATHODE": "2", "B": "2", "PIN2": "2", "PIN_2": "2",
    },
    "wokwi-pushbutton": {
        "1": "1", "1.L": "1", "1.R": "1", "1A": "1", "1B": "1", "A": "1", "PIN1": "1", "PIN_1": "1", "IN": "1", "+": "1",
        "2": "2", "2.L": "2", "2.R": "2", "2A": "2", "2B": "2", "B": "2", "PIN2": "2", "PIN_2": "2", "OUT": "2", "SIG": "2", "-": "2", "3": "2", "4": "2",
    },
    "wokwi-servo": {
        "GND": "GND", "-": "GND", "GROUND": "GND", "1": "GND",
        "V+": "V+", "VCC": "V+", "5V": "V+", "+": "V+", "POWER": "V+", "2": "V+",
        "PWM": "PWM", "SIG": "PWM", "SIGNAL": "PWM", "OUT": "PWM", "IN": "PWM", "DATA": "PWM", "3": "PWM",
    },
    "wokwi-hc-sr04": {
        "VCC": "VCC", "5V": "VCC", "V+": "VCC", "+": "VCC", "1": "VCC",
        "TRIG": "TRIG", "TRIGGER": "TRIG", "TRG": "TRIG", "2": "TRIG",
        "ECHO": "ECHO", "ECH": "ECHO", "OUT": "ECHO", "SIG": "ECHO", "3": "ECHO",
        "GND": "GND", "-": "GND", "GROUND": "GND", "4": "GND",
    },
}

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
                hedef_pin="4C",
                kablo_rengi="#F97316"
            ),
            BaglantiAdimi(
                adim_no=2,
                talimat="220Ω Direnç ile Kırmızı LED anot bacağını breadboard üzerinde aynı sütunda buluştur.",
                ipucu="Breadboard dikey sütunu üzerinden kablosuz bağlanırlar!",
                kaynak_parca="BREADBOARD",
                kaynak_pin="8C",
                hedef_parca="BREADBOARD",
                hedef_pin="8E",
                kablo_rengi="#EF4444"
            ),
            BaglantiAdimi(
                adim_no=3,
                talimat="LED'in katot (kısa) bacağını GND hattına bağla.",
                ipucu="GND devreyi tamamlar.",
                kaynak_parca="BREADBOARD",
                kaynak_pin="9E",
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
# Pedagojik AI Sistem Promptu (Tam Pin Sözlüğü & Netlist Kuralları)
# ---------------------------------------------------------

SYSTEM_PROMPT = """Sen 8-14 yaş çocuklar için 'Arduino Robot Arkadaşı'sın. Görevin çocuğun fikrini ve envanterini kullanarak standart Netlist JSON üretmek.

KURALLAR:
1. KOORDİNAT YASAĞI: Asla breadboard deliği (5A, 12C, bn.1) veya piksel koordinatı üretme!
2. TAM PİN VE TİP SÖZLÜĞÜ (Sadece bu type ve pinleri kullan):
- wokwi-resistor: r1.1, r1.2 (props: {"value":"220"} veya {"value":"10000"})
- wokwi-led: led1.A (Anot), led1.C (Katot) (props: {"color":"red"|"green"|"yellow"|"blue"})
- wokwi-photoresistor (2 bacaklı LDR): ldr1.1, ldr1.2
- wokwi-photoresistor-sensor (4 pinli LDR modülü): ldr1.VCC, ldr1.GND, ldr1.AO, ldr1.DO
- wokwi-potentiometer (3 pinli potansiyometre): pot1.GND, pot1.SIG, pot1.VCC
- wokwi-buzzer: buzzer1.1 (+/Sinyal), buzzer1.2 (-/GND)
- wokwi-pushbutton: btn1.1, btn1.2 (props: {"color":"red"})
- wokwi-servo: servo1.V+, servo1.GND, servo1.PWM
- wokwi-hc-sr04: hcsr1.VCC, hcsr1.GND, hcsr1.TRIG, hcsr1.ECHO
3. BAĞLANTI KURALLARI:
- Her bağlantı tek bir {"from":"...", "to":"...", "color":"..."} nesnesidir.
- Güç her zaman "to" tarafında "5V" veya "GND" olarak yazılır (örn: {"from":"led1.C","to":"GND"}).
- Arduino sinyal pinleri "uno.D2".."uno.D13" veya "uno.A0".."uno.A5" yazılır.
- Bir pini birden çok yere bağlamak gerekirse ayrı satırlar yaz.
- arduino_kodu içindeki pin numaraları netlist'teki uno.* pinleriyle birebir aynı olmalıdır!

ÖRNEK 1 (Tek LED + 220Ω Direnç):
{"board":"arduino-uno","components":[{"id":"r1","type":"wokwi-resistor","props":{"value":"220"},"label":"220Ω Direnç"},{"id":"led1","type":"wokwi-led","props":{"color":"red"},"label":"Kırmızı LED"}],"connections":[{"from":"uno.D13","to":"r1.1","color":"orange"},{"from":"r1.2","to":"led1.A","color":"red"},{"from":"led1.C","to":"GND","color":"black"}]}

ÖRNEK 2 (Gerilim Bölücülü LDR + LED):
{"board":"arduino-uno","components":[{"id":"r1","type":"wokwi-resistor","props":{"value":"220"},"label":"220Ω Direnç"},{"id":"led1","type":"wokwi-led","props":{"color":"red"},"label":"Kırmızı LED"},{"id":"ldr1","type":"wokwi-photoresistor","label":"2 Bacaklı LDR"},{"id":"r2","type":"wokwi-resistor","props":{"value":"10000"},"label":"10kΩ Direnç"}],"connections":[{"from":"uno.D13","to":"r1.1","color":"orange"},{"from":"r1.2","to":"led1.A","color":"red"},{"from":"led1.C","to":"GND","color":"black"},{"from":"ldr1.1","to":"5V","color":"red"},{"from":"ldr1.2","to":"uno.A0","color":"green"},{"from":"ldr1.2","to":"r2.1","color":"green"},{"from":"r2.2","to":"GND","color":"black"}]}

ÖRNEK 3 (Buton + Pull-down Direnç + Servo):
{"board":"arduino-uno","components":[{"id":"btn1","type":"wokwi-pushbutton","props":{"color":"red"},"label":"Buton"},{"id":"r1","type":"wokwi-resistor","props":{"value":"10000"},"label":"10kΩ Direnç"},{"id":"servo1","type":"wokwi-servo","label":"Servo Motor"}],"connections":[{"from":"btn1.1","to":"5V","color":"red"},{"from":"btn1.2","to":"uno.D2","color":"blue"},{"from":"btn1.2","to":"r1.1","color":"blue"},{"from":"r1.2","to":"GND","color":"black"},{"from":"servo1.V+","to":"5V","color":"red"},{"from":"servo1.GND","to":"GND","color":"black"},{"from":"servo1.PWM","to":"uno.D9","color":"orange"}]}

JSON ÇIKTI ŞEMASI:
{"proje_adi":"...","karsilama_mesaji":"...","gerekli_parcalar":["ARDUINO_UNO","BREADBOARD"],"netlist":{"board":"arduino-uno","components":[...],"connections":[...]},"akis_adimlari":{"gozlemle":"...","karar_ver":"...","evet_sonucu":"...","hayir_sonucu":"..."},"arduino_kodu":"...","guvenlik_notu":"..."}
"""


def clean_llm_json_response(raw_text: str) -> str:
    """LLM çıktısından JSON'ı temiz bir şekilde ayıklar."""
    text = (raw_text or "").strip()
    text = re.sub(r"<think>.*?</think>", "", text, flags=re.DOTALL).strip()
    text = re.sub(r"^```(?:json)?\s*", "", text).strip()
    text = re.sub(r"```$", "", text).strip()

    start = text.find("{")
    end = text.rfind("}")
    if start != -1 and end != -1 and end > start:
        return text[start:end + 1]

    return text


# ---------------------------------------------------------
# Kod ↔ Netlist Pin Uyum Kontrolü (Madde 9)
# ---------------------------------------------------------

def extract_arduino_code_pins(code: str) -> Set[str]:
    """Arduino C++ kodu içindeki kullanılan pinleri (uno.D13, uno.A0 formatında) çıkarır."""
    if not code:
        return set()

    # Yorum satırlarını temizle
    clean_code = re.sub(r"//.*", "", code)
    clean_code = re.sub(r"/\*.*?\*/", "", clean_code, flags=re.DOTALL)

    # 1. Sabit/değişken tanımlarını yakala: const int LED_PIN = 13; veya #define TRIG 9
    var_to_pin: Dict[str, str] = {}
    for m in re.finditer(
        r"(?:const\s+int|int|uint8_t|byte|#define)\s+([A-Za-z_]\w*)\s*=?\s*(A[0-5]|D?(?:1[0-3]|[0-9]))\b",
        clean_code
    ):
        var_name = m.group(1)
        raw_val = m.group(2).upper()
        var_to_pin[var_name] = raw_val

    def resolve_token_to_uno_pin(token: str, is_analog_read: bool = False) -> Optional[str]:
        t = token.strip()
        if t in var_to_pin:
            t = var_to_pin[t]
        t_up = t.upper()
        if re.match(r"^A[0-5]$", t_up):
            return f"uno.{t_up}"
        if re.match(r"^D(1[0-3]|[0-9])$", t_up):
            return f"uno.{t_up}"
        if re.match(r"^(1[0-3]|[0-9])$", t_up):
            num = int(t_up)
            if is_analog_read and 0 <= num <= 5:
                return f"uno.A{num}"
            return f"uno.D{num}"
        return None

    used_pins: Set[str] = set()

    # 2. Fonksiyon çağrılarını tara: pinMode, digitalWrite, digitalRead, analogWrite, tone, noTone, pulseIn, attach
    for m in re.finditer(
        r"\b(pinMode|digitalWrite|digitalRead|analogRead|analogWrite|tone|noTone|pulseIn|attach)\s*\(\s*([A-Za-z0-9_]+)",
        clean_code
    ):
        fn_name = m.group(1)
        arg1 = m.group(2)
        resolved = resolve_token_to_uno_pin(arg1, is_analog_read=(fn_name == "analogRead"))
        if resolved:
            used_pins.add(resolved)

    return used_pins


def extract_netlist_uno_pins(netlist: Optional[CircuitNetlist]) -> Set[str]:
    """Netlist bağlantılarındaki uno.* sinyal pinlerini çıkarır."""
    if not netlist or not netlist.connections:
        return set()

    pins: Set[str] = set()
    for conn in netlist.connections:
        for ep in (conn.from_pin, conn.to_pin):
            ep_str = (ep or "").strip()
            if ep_str.startswith("uno.D") or ep_str.startswith("uno.A"):
                pins.add(ep_str)
    return pins


def check_code_netlist_pin_consistency(code: str, netlist: Optional[CircuitNetlist]) -> List[str]:
    """Arduino kodu ile netlist arasındaki pin uyumsuzluklarını kontrol eder ve uyarı döner."""
    warnings: List[str] = []
    code_pins = extract_arduino_code_pins(code)
    net_pins = extract_netlist_uno_pins(netlist)

    if not code_pins or not net_pins:
        return warnings

    only_in_code = sorted(code_pins - net_pins)
    only_in_net = sorted(net_pins - code_pins)

    if only_in_code or only_in_net:
        parts = []
        if only_in_code:
            parts.append(f"kodda kullanılan [{', '.join(only_in_code)}] netlist'te yok")
        if only_in_net:
            parts.append(f"netlist'te bağlı [{', '.join(only_in_net)}] kodda kullanılmıyor")
        warnings.append(f"Kod ↔ Netlist pin uyuşmazlığı: {'; '.join(parts)}.")

    return warnings


# ---------------------------------------------------------
# Backend Netlist Normalizasyonu ve Doğrulama (Madde 1, 2, 10)
# ---------------------------------------------------------

def validate_strict_raw_project_dict(data: Dict[str, Any]) -> List[str]:
    """
    Ham LLM JSON çıktısını katı kurallarla kontrol eder.
    Herhangi bir şema eksiği, alias kullanımı, ters yönlü güç, boşta bileşen veya kod-pin uyumsuzluğu varsa
    hata listesi döner (LLM'e 1 kez repair isteği göndermek için).
    """
    errors: List[str] = []

    try:
        proj = ProjeTasarimi(**data)
    except Exception as e:
        return [f"JSON şema doğrulama hatası: {e}"]

    if not proj.netlist or not proj.netlist.components:
        return ["Netlist içinde hiç bileşen (components) tanımlanmamış."]
    if not proj.netlist.connections:
        return ["Netlist içinde hiç bağlantı (connections) tanımlanmamış."]

    comp_map: Dict[str, str] = {}
    connected_pins: Dict[str, Set[str]] = {}

    for c in proj.netlist.components:
        if c.type not in SUPPORTED_TYPES_AND_PINS:
            errors.append(
                f"Geçersiz veya alias bileşen tipi: '{c.type}' (Bileşen: '{c.id}'). "
                f"Desteklenen tipler: {sorted(SUPPORTED_TYPES_AND_PINS.keys())}."
            )
        comp_map[c.id] = c.type
        connected_pins[c.id] = set()

    def check_strict_endpoint(ep: str, side: str) -> None:
        if ep in ("GND", "5V"):
            if side == "from":
                errors.append(f"Ters yönlü güç bağlantısı: '{ep}' her zaman 'to' tarafında olmalıdır.")
            return
        if re.match(r"^uno\.(D(?:1[0-3]|[0-9])|A[0-5])$", ep):
            return
        if "." in ep:
            part, pin = ep.split(".", 1)
            if part in comp_map:
                ctype = comp_map[part]
                valid_pins = SUPPORTED_TYPES_AND_PINS.get(ctype, set())
                if valid_pins and pin not in valid_pins:
                    errors.append(
                        f"Standart dışı pin adı: '{ep}'. '{ctype}' için geçerli pinler: {sorted(valid_pins)}."
                    )
                else:
                    connected_pins[part].add(pin)
                return
        errors.append(f"Standart dışı veya tanımsız bağlantı ucu: '{ep}'.")

    for conn in proj.netlist.connections:
        check_strict_endpoint(conn.from_pin, "from")
        check_strict_endpoint(conn.to_pin, "to")
        if "." in conn.from_pin and "." in conn.to_pin:
            p1 = conn.from_pin.split(".", 1)[0]
            p2 = conn.to_pin.split(".", 1)[0]
            if p1 == p2 and p1 in comp_map:
                errors.append(f"Kısa devre hatası: '{p1}' bileşeninin iki ucu birbirine bağlanmış.")

    for cid, pins in connected_pins.items():
        if len(pins) < 2 and cid in comp_map:
            errors.append(f"'{cid}' ({comp_map[cid]}) bileşeninin bağlantıları eksik (en az 2 uç bağlı olmalı).")

    # Kod ↔ Netlist pin uyumunu normalize edilmiş kopya üzerinden de denetle
    try:
        norm_copy, _ = normalize_project_dict(data)
        norm_proj = ProjeTasarimi(**norm_copy)
        pin_mismatches = check_code_netlist_pin_consistency(norm_proj.arduino_kodu, norm_proj.netlist)
    except Exception:
        pin_mismatches = check_code_netlist_pin_consistency(proj.arduino_kodu, proj.netlist)
    errors.extend(pin_mismatches)

    return errors


def normalize_project_dict(data: Dict[str, Any]) -> Tuple[Dict[str, Any], List[str]]:
    """
    LLM çıktısındaki netlist bileşen tiplerini, pin alias'larını ve güç yönlerini normalize eder.
    """
    warnings: List[str] = []
    if not isinstance(data, dict) or "netlist" not in data or not isinstance(data["netlist"], dict):
        return data, warnings

    netlist = data["netlist"]
    raw_comps = netlist.get("components") or []
    raw_conns = netlist.get("connections") or []

    comp_type_by_id: Dict[str, str] = {}
    comp_id_lower: Dict[str, str] = {}
    norm_comps = []

    for rc in raw_comps:
        if not isinstance(rc, dict):
            continue
        cid = str(rc.get("id") or "").strip()
        if not cid:
            continue
        raw_t = str(rc.get("type") or "").strip()
        if (
            cid.lower() in ("uno", "arduino", "board", "breadboard", "bb")
            or "arduino" in raw_t.lower()
            or "breadboard" in raw_t.lower()
        ):
            warnings.append(f"Ana kart/breadboard bileşen listesinden çıkarıldı: '{cid}' ({raw_t}).")
            continue
        canon_t = TYPE_ALIASES.get(raw_t.lower(), raw_t)

        # LDR tipini bağlantılardaki pinlere göre netleştir
        if raw_t.lower() == "ldr" or canon_t in ("wokwi-photoresistor", "wokwi-photoresistor-sensor"):
            used_pins = []
            for conn in raw_conns:
                if not isinstance(conn, dict):
                    continue
                for k in ("from", "to", "from_pin", "to_pin"):
                    v = str(conn.get(k) or "").strip()
                    if "." in v:
                        p, pin = v.split(".", 1)
                        if p.strip().lower() == cid.lower():
                            used_pins.append(pin.strip().upper())
            has_mod = any(p in ("VCC", "AO", "DO", "OUT", "SIG", "A0", "D0") for p in used_pins)
            only_two = len(used_pins) > 0 and all(p in ("1", "2", "A", "B", "PIN1", "PIN2", "PIN_1", "PIN_2") for p in used_pins)
            if raw_t.lower() == "ldr":
                canon_t = "wokwi-photoresistor-sensor" if has_mod else "wokwi-photoresistor"
            elif canon_t == "wokwi-photoresistor-sensor" and only_two:
                canon_t = "wokwi-photoresistor"
            elif canon_t == "wokwi-photoresistor" and has_mod and "GND" in used_pins:
                canon_t = "wokwi-photoresistor-sensor"

        if canon_t != raw_t:
            warnings.append(f"Bileşen tipi normalize edildi: '{cid}' ({raw_t} -> {canon_t}).")

        comp_type_by_id[cid] = canon_t
        comp_id_lower[cid.lower()] = cid
        norm_comps.append({
            "id": cid,
            "type": canon_t,
            "props": rc.get("props") or {},
            "label": rc.get("label") or cid,
        })

    def norm_ep(raw_ep: str) -> Optional[str]:
        ep = str(raw_ep or "").strip()
        if not ep:
            return None
        up = ep.upper()
        if up in ("GND", "GND.1", "GND.2", "GND.3", "0V", "-", "GROUND", "UNO.GND", "UNO.GND.1", "UNO.GND.2", "ARDUINO.GND"):
            return "GND"
        if up in ("5V", "+5V", "3.3V", "VCC", "V+", "+", "UNO.5V", "UNO.VCC", "UNO.3.3V", "ARDUINO.5V"):
            return "5V"

        if "." in ep:
            part_raw, pin_raw = ep.split(".", 1)
            part_l = part_raw.strip().lower()
            pin_u = pin_raw.strip().upper()

            if part_l in comp_id_lower:
                cid = comp_id_lower[part_l]
                ctype = comp_type_by_id[cid]
                pmap = PIN_ALIASES.get(ctype, {})
                mapped = pmap.get(pin_u)
                if mapped:
                    return f"{cid}.{mapped}"
                return None

            if part_l in ("uno", "arduino", "board", "arduino-uno", "arduino_uno"):
                m_dig = re.match(r"^(?:D|PIN_?)?(1[0-3]|[0-9])$", pin_u)
                if m_dig:
                    return f"uno.D{m_dig.group(1)}"
                m_ana = re.match(r"^(?:A|ANALOG_?)([0-5])$", pin_u)
                if m_ana:
                    return f"uno.A{m_ana.group(1)}"
                return None

        m_dig_bare = re.match(r"^(?:D|PIN_?)?(1[0-3]|[0-9])$", up)
        if m_dig_bare:
            return f"uno.D{m_dig_bare.group(1)}"
        m_ana_bare = re.match(r"^(?:A|ANALOG_?)([0-5])$", up)
        if m_ana_bare:
            return f"uno.A{m_ana_bare.group(1)}"
        return None

    norm_conns = []
    seen = set()
    for rc in raw_conns:
        if not isinstance(rc, dict):
            continue
        rf = str(rc.get("from") or rc.get("from_pin") or "").strip()
        rt = str(rc.get("to") or rc.get("to_pin") or "").strip()
        nf = norm_ep(rf)
        nt = norm_ep(rt)
        if not nf or not nt or nf == nt:
            warnings.append(f"Geçersiz bağlantı atlandı: '{rf} -> {rt}'.")
            continue
        if nf != rf:
            warnings.append(f"Pin normalize edildi: '{rf}' -> '{nf}'.")
        if nt != rt:
            warnings.append(f"Pin normalize edildi: '{rt}' -> '{nt}'.")

        if nf in ("GND", "5V") and nt not in ("GND", "5V"):
            nf, nt = nt, nf
            warnings.append(f"Güç bağlantısı yönü düzeltildi: '{nf} -> {nt}'.")

        key = f"{nf}=>{nt}" if nt in ("GND", "5V") else "<=>".join(sorted([nf, nt]))
        if key in seen:
            continue
        seen.add(key)
        norm_conns.append({
            "from": nf,
            "to": nt,
            "color": rc.get("color") or "orange"
        })

    new_data = dict(data)
    if not new_data.get("proje_adi"):
        new_data["proje_adi"] = "Eğlenceli Arduino Projem 🚀"
    if not new_data.get("karsilama_mesaji"):
        new_data["karsilama_mesaji"] = "Harika bir devre tasarladık! Adım adım kuralım."
    if not isinstance(new_data.get("gerekli_parcalar"), list) or not new_data.get("gerekli_parcalar"):
        new_data["gerekli_parcalar"] = ["ARDUINO_UNO", "BREADBOARD"]
    if not isinstance(new_data.get("akis_adimlari"), dict):
        new_data["akis_adimlari"] = {
            "gozlemle": "Devredeki sensör ve girişleri sürekli izle.",
            "karar_ver": "Koşul gerçekleşti mi kontrol et.",
            "evet_sonucu": "Çıkış elemanlarını (LED/Buzzer/Servo) çalıştır!",
            "hayir_sonucu": "Bekleme durumunda kal."
        }
    else:
        akis = dict(new_data["akis_adimlari"])
        akis.setdefault("gozlemle", "Devreyi gözlemle.")
        akis.setdefault("karar_ver", "Koşulu kontrol et.")
        akis.setdefault("evet_sonucu", "Aktif et!")
        akis.setdefault("hayir_sonucu", "Bekle.")
        new_data["akis_adimlari"] = akis
    if not new_data.get("arduino_kodu"):
        new_data["arduino_kodu"] = "void setup() {}\nvoid loop() {}\n"

    new_data["netlist"] = {
        "board": netlist.get("board") or "arduino-uno",
        "components": norm_comps,
        "connections": norm_conns,
    }
    return new_data, warnings


def validate_normalized_project(proj: ProjeTasarimi) -> List[str]:
    """Normalize edilmiş ProjeTasarimi'nin temel elektriksel geçerliliğini denetler."""
    errors: List[str] = []
    if not proj.netlist or not proj.netlist.components:
        errors.append("Netlist bileşen listesi boş.")
        return errors
    if not proj.netlist.connections:
        errors.append("Netlist bağlantı listesi boş.")
        return errors

    for c in proj.netlist.components:
        if c.type not in SUPPORTED_TYPES_AND_PINS:
            errors.append(f"Desteklenmeyen bileşen tipi: {c.type}")

    for conn in proj.netlist.connections:
        if (conn.from_pin == "5V" and conn.to_pin == "GND") or (conn.from_pin == "GND" and conn.to_pin == "5V"):
            errors.append("5V ve GND doğrudan kısa devre edilmiş.")
        if "." in conn.from_pin and "." in conn.to_pin:
            p1 = conn.from_pin.split(".", 1)[0]
            p2 = conn.to_pin.split(".", 1)[0]
            if p1 == p2 and p1 != "uno":
                errors.append(f"'{p1}' bileşeninin iki ucu doğrudan kısa devre edilmiş.")

    return errors


def build_repair_prompt(
    raw_output: str,
    errors: List[str],
    original_prompt: str,
    inventory: List[str]
) -> str:
    """Doğrulama hatalarını içeren tek seferlik düzeltme (repair) promptu oluşturur."""
    err_bullets = "\n".join(f"- {e}" for e in errors)
    return f"""Önceki ürettiğin JSON çıktısında aşağıdaki şema/netlist/kod hataları tespit edildi:
{err_bullets}

HATALI ÇIKTI:
{raw_output}

KULLANICI PROJE HAYALİ:
"{original_prompt}"

ENVANTER:
{json.dumps(inventory, ensure_ascii=False)}

LÜTFEN YUKARIDAKİ HATALARI DÜZELTEREK SADECE GEÇERLİ VE STANDART NETLIST FORMATINDA JSON DÖNDÜR:
- Bileşen tipleri yalnızca: wokwi-resistor, wokwi-led, wokwi-photoresistor, wokwi-photoresistor-sensor, wokwi-potentiometer, wokwi-buzzer, wokwi-pushbutton, wokwi-servo, wokwi-hc-sr04
- Pin isimleri tam sözlüğe uymalı (örn: uno.D13, uno.A0, r1.1, r1.2, led1.A, led1.C, ldr1.VCC, ldr1.GND, ldr1.AO, servo1.V+, servo1.GND, servo1.PWM)
- Güç her zaman "to": "GND" veya "to": "5V" olarak yazılmalı
- arduino_kodu içindeki pin numaraları netlist'teki uno.* pinleriyle birebir eşleşmeli!"""


def parse_validate_or_repair(
    raw_first_response: str,
    call_llm_fn: Callable[[str], str],
    user_prompt: str,
    inventory: List[str]
) -> Optional[ProjeTasarimi]:
    """
    1. İlk LLM cevabını parse eder ve katı doğrulamadan geçirir.
    2. Hata/alias/uyumsuzluk varsa LLM'e hata mesajlarıyla birlikte 1 kez 'repair' isteği gönderir.
    3. Sonucu normalize eder, kod-netlist pin uyumunu kontrol eder ve geçerliyse ProjeTasarimi döner.
    """
    first_data: Optional[Dict[str, Any]] = None
    norm_first_data: Optional[Dict[str, Any]] = None
    norm_first_warnings: List[str] = []
    strict_errors: List[str] = []

    try:
        cleaned = clean_llm_json_response(raw_first_response)
        first_data = json.loads(cleaned)
        if not isinstance(first_data, dict):
            strict_errors = ["LLM çıktısı bir JSON nesnesi değil."]
            first_data = None
        else:
            norm_first_data, norm_first_warnings = normalize_project_dict(first_data)
            strict_errors = validate_strict_raw_project_dict(norm_first_data)
    except Exception as e:
        strict_errors = [f"JSON ayrıştırma (parse) hatası: {e}"]

    # Eğer ilk çıktı (normalizasyon sonrası) tüm katı kuralları sağlıyorsa doğrudan döndür
    if norm_first_data is not None and len(strict_errors) == 0:
        proj = ProjeTasarimi(**norm_first_data)
        pin_warnings = check_code_netlist_pin_consistency(proj.arduino_kodu, proj.netlist)
        proj.uyarilar = norm_first_warnings + pin_warnings
        return proj

    # Hata varsa: 1 kez LLM'e repair isteği gönder!
    print(f"[AI Repair] Doğrulama hataları ({len(strict_errors)} adet), 1 kez repair deneniyor: {strict_errors}")
    repair_prompt = build_repair_prompt(raw_first_response, strict_errors, user_prompt, inventory)

    try:
        raw_repaired = call_llm_fn(repair_prompt)
        if raw_repaired:
            cleaned_rep = clean_llm_json_response(raw_repaired)
            rep_data = json.loads(cleaned_rep)
            if isinstance(rep_data, dict):
                norm_rep_data, norm_warnings = normalize_project_dict(rep_data)
                proj_rep = ProjeTasarimi(**norm_rep_data)
                struct_errors = validate_normalized_project(proj_rep)
                if not struct_errors:
                    pin_warnings = check_code_netlist_pin_consistency(proj_rep.arduino_kodu, proj_rep.netlist)
                    proj_rep.uyarilar = norm_warnings + pin_warnings
                    return proj_rep
    except Exception as e:
        print(f"[AI Repair] Repair denemesi başarısız oldu: {e}")

    # Eğer repair çağrısı başarısız olduysa ama ilk çıktı normalize edilerek kurtarılabiliyorsa kurtar
    if first_data is not None:
        try:
            norm_first, norm_warnings = normalize_project_dict(first_data)
            proj_first = ProjeTasarimi(**norm_first)
            if not validate_normalized_project(proj_first):
                pin_warnings = check_code_netlist_pin_consistency(proj_first.arduino_kodu, proj_first.netlist)
                proj_first.uyarilar = norm_warnings + pin_warnings
                return proj_first
        except Exception:
            pass

    return None


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

Yukarıdaki hayali ve envanteri kullanarak standart Netlist şeması ile tam bir Arduino projesi tasarla. Tek satır (minified, girintisiz) JSON döndür."""

    def call_ollama(custom_user_prompt: str) -> str:
        res = httpx.post(
            f"{ollama_url}/api/generate",
            json={
                "model": clean_model,
                "system": SYSTEM_PROMPT,
                "prompt": custom_user_prompt,
                "stream": False,
                "format": "json",
                "options": {
                    "temperature": 0.1,
                    "num_predict": 550
                }
            },
            timeout=120.0
        )
        if res.status_code == 200:
            return res.json().get("response", "")
        raise RuntimeError(f"Ollama HTTP {res.status_code}")

    try:
        raw_first = call_ollama(user_prompt)
        validated = parse_validate_or_repair(raw_first, call_ollama, prompt, inventory)
        if validated is not None:
            return validated
    except Exception as e:
        print(f"Ollama üretimi başarısız: {e}")

    return select_best_mock_project(prompt)


def generate_with_litellm(model_name: str, prompt: str, inventory: List[str], api_key: Optional[str] = None) -> ProjeTasarimi:
    from litellm import completion

    user_prompt = f"""KULLANICI PROJE HAYALİ:
"{prompt}"

KULLANICININ MALZEME ÇANTASI:
{json.dumps(inventory, ensure_ascii=False)}

Standart Netlist şeması ile tam bir Arduino projesi üret."""

    def call_litellm(custom_user_prompt: str) -> str:
        response = completion(
            model=model_name,
            messages=[
                {"role": "system", "content": SYSTEM_PROMPT},
                {"role": "user", "content": custom_user_prompt}
            ],
            response_format={"type": "json_object"},
            api_key=api_key,
            temperature=0.3
        )
        return response.choices[0].message.content

    try:
        raw_first = call_litellm(user_prompt)
        validated = parse_validate_or_repair(raw_first, call_litellm, prompt, inventory)
        if validated is not None:
            return validated
    except Exception as e:
        print(f"LiteLLM üretimi başarısız: {e}")

    return select_best_mock_project(prompt)


def select_best_mock_project(prompt: str) -> ProjeTasarimi:
    p = (prompt or "").lower()
    if any(k in p for k in ["trafik", "kirmizi sari", "kırmızı sarı", "3 led", "üç led"]):
        return MOCK_PROJECTS["trafik_isiklari"]
    if any(k in p for k in ["park", "mesafe", "yarasa", "hcsr04", "korna", "engel", "alarm", "buzzer"]):
        return MOCK_PROJECTS["park_sensoru"]
    if any(k in p for k in ["buton", "servo", "kapi", "kapı", "bariyer", "motor"]):
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
            local_ids = [m["id"] for m in models_info.get("local_models", [])]
            if chosen_model not in local_ids and models_info.get("default_model"):
                chosen_model = models_info["default_model"]
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

import json
import os
import re
import time
import uuid
from typing import List, Optional, Dict, Any, Set, Tuple, Callable, Generator
import httpx
from dotenv import load_dotenv

# LiteLLM'in internete erişmeye çalışıp beklemesini önlemek için yerel maliyet haritasını kullan
os.environ["LITELLM_LOCAL_MODEL_COST_MAP"] = "True"
import litellm

# Yeni nesil modeller (Gemini 3.8 vb.) temperature/top_p parametresi gönderildiğinde hata vermesin
litellm.drop_params = True

from schemas import (
    ProjeTasarimi,
    BaglantiAdimi,
    AkisAdimi,
    AkisDiyagrami,
    CircuitNetlist,
    NetlistComponent,
    NetlistConnection,
    PinBindingInfo,
    LogicVerificationReport,
    WiringDesignResponse,
    LogicDesignResponse,
    SavedProjectEntry,
    AILogEntry,
)
from arduino_code_utils import sanitize_arduino_identifiers
from flow_service import (
    legacy_akis_to_diyagram,
    validate_flow_diagram,
    build_deterministic_flow_from_code,
    generate_flow_from_code,
)
from prompt_filter import validate_project_prompt
from app.llm.catalog import (
    build_one_shot_system_prompt,
    get_filtered_component_docs,
)
from app.llm.cache import (
    get_cached_project,
    set_cached_project,
)
from app.repositories.projects_repo import (
    get_saved_projects,
    save_project_entry,
    delete_saved_project,
)
from app.repositories.ai_logs_repo import (
    get_ai_logs,
    record_ai_log,
    clear_ai_logs,
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
    "wokwi-rgb-led": "wokwi-rgb-led",
    "rgb-led": "wokwi-rgb-led",
    "rgb_led": "wokwi-rgb-led",
    "led_rgb": "wokwi-rgb-led",
    "rgb": "wokwi-rgb-led",
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
    # Bluetooth HC-05 / HC-06
    "wokwi-hc-05": "wokwi-hc-05",
    "wokwi-hc05": "wokwi-hc-05",
    "hc-05": "wokwi-hc-05",
    "hc05": "wokwi-hc-05",
    "bluetooth": "wokwi-hc-05",
    "bluetooth_hc05": "wokwi-hc-05",
    "bt": "wokwi-hc-05",
    "wokwi-hc-06": "wokwi-hc-06",
    "wokwi-hc06": "wokwi-hc-06",
    "hc-06": "wokwi-hc-06",
    "hc06": "wokwi-hc-06",
    "bluetooth_hc06": "wokwi-hc-06",
    # Motor Sürücü L293D / L298N
    "wokwi-l293d": "wokwi-l293d",
    "l293d": "wokwi-l293d",
    "l293": "wokwi-l293d",
    "motor_driver": "wokwi-l293d",
    "motor_driver_l293d": "wokwi-l293d",
    "motor-driver": "wokwi-l293d",
    "wokwi-l298n": "wokwi-l298n",
    "l298n": "wokwi-l298n",
    "l298": "wokwi-l298n",
    "motor_driver_l298n": "wokwi-l298n",
    # DC Motor
    "wokwi-dc-motor": "wokwi-dc-motor",
    "wokwi-dcmotor": "wokwi-dc-motor",
    "dc-motor": "wokwi-dc-motor",
    "dc_motor": "wokwi-dc-motor",
    "dcmotor": "wokwi-dc-motor",
    "dc_motor_5v": "wokwi-dc-motor",
    "motor": "wokwi-dc-motor",
    # PIR, DHT, Joystick, Relay, LCD, OLED ve diğer sensörler
    "wokwi-pir-motion-sensor": "wokwi-pir-motion-sensor",
    "pir": "wokwi-pir-motion-sensor",
    "pir_sensor": "wokwi-pir-motion-sensor",
    "pir-sensor": "wokwi-pir-motion-sensor",
    "motion_sensor": "wokwi-pir-motion-sensor",
    "wokwi-dht22": "wokwi-dht22",
    "wokwi-dht11": "wokwi-dht22",
    "dht11": "wokwi-dht22",
    "dht22": "wokwi-dht22",
    "dht": "wokwi-dht22",
    "wokwi-analog-joystick": "wokwi-analog-joystick",
    "joystick": "wokwi-analog-joystick",
    "joystick_module": "wokwi-analog-joystick",
    "analog-joystick": "wokwi-analog-joystick",
    "wokwi-relay-module": "wokwi-relay-module",
    "wokwi-relay": "wokwi-relay-module",
    "relay": "wokwi-relay-module",
    "relay_5v": "wokwi-relay-module",
    "relay-module": "wokwi-relay-module",
    "wokwi-lcd1602": "wokwi-lcd1602",
    "lcd1602": "wokwi-lcd1602",
    "lcd": "wokwi-lcd1602",
    "lcd_16x2_i2c": "wokwi-lcd1602",
    "wokwi-ssd1306": "wokwi-ssd1306",
    "ssd1306": "wokwi-ssd1306",
    "oled": "wokwi-ssd1306",
    "oled_096_i2c": "wokwi-ssd1306",
    "wokwi-soil-moisture-sensor": "wokwi-soil-moisture-sensor",
    "soil_moisture": "wokwi-soil-moisture-sensor",
    "soil-moisture": "wokwi-soil-moisture-sensor",
    "soil_sensor": "wokwi-soil-moisture-sensor",
    "wokwi-rain-sensor": "wokwi-rain-sensor",
    "rain_sensor": "wokwi-rain-sensor",
    "rain-sensor": "wokwi-rain-sensor",
    "wokwi-water-sensor": "wokwi-water-sensor",
    "water_sensor": "wokwi-water-sensor",
    "water-sensor": "wokwi-water-sensor",
    "wokwi-gas-sensor": "wokwi-gas-sensor",
    "gas_sensor": "wokwi-gas-sensor",
    "mq2": "wokwi-gas-sensor",
    "mq2_gas": "wokwi-gas-sensor",
    "wokwi-flame-sensor": "wokwi-flame-sensor",
    "flame_sensor": "wokwi-flame-sensor",
    "flame-sensor": "wokwi-flame-sensor",
    "wokwi-small-sound-sensor": "wokwi-small-sound-sensor",
    "wokwi-big-sound-sensor": "wokwi-small-sound-sensor",
    "sound_sensor": "wokwi-small-sound-sensor",
    "sound-sensor": "wokwi-small-sound-sensor",
    "microphone": "wokwi-small-sound-sensor",
    "wokwi-ir-receiver": "wokwi-ir-receiver",
    "ir_receiver": "wokwi-ir-receiver",
    "ir-receiver": "wokwi-ir-receiver",
    "wokwi-ntc-temperature-sensor": "wokwi-ntc-temperature-sensor",
    "ntc": "wokwi-ntc-temperature-sensor",
    "temperature_sensor": "wokwi-ntc-temperature-sensor",
}

_ANALOG_4PIN_ALIASES: Dict[str, str] = {
    "VCC": "VCC", "5V": "VCC", "3.3V": "VCC", "V+": "VCC", "+": "VCC", "1": "VCC",
    "GND": "GND", "-": "GND", "0V": "GND", "GROUND": "GND", "2": "GND",
    "DO": "DO", "D0": "DO", "DOUT": "DO", "DIGITAL": "DO", "3": "DO",
    "AO": "AO", "A0": "AO", "AOUT": "AO", "OUT": "AO", "SIG": "AO", "SIGNAL": "AO", "S": "AO", "4": "AO",
}

_BLUETOOTH_PIN_ALIASES: Dict[str, str] = {
    "VCC": "VCC", "5V": "VCC", "+5V": "VCC", "3.3V": "VCC", "V+": "VCC", "+": "VCC",
    "GND": "GND", "-": "GND", "0V": "GND", "GROUND": "GND",
    "TXD": "TXD", "TX": "TXD", "DOUT": "TXD", "OUT": "TXD",
    "RXD": "RXD", "RX": "RXD", "DIN": "RXD", "IN": "RXD",
    "EN": "EN", "KEY": "EN", "ENABLE": "EN",
    "STATE": "STATE", "STAT": "STATE",
}

_MOTOR_DRIVER_PIN_ALIASES: Dict[str, str] = {
    "VCC1": "VCC1", "VCC": "VCC1", "5V": "VCC1", "VSS": "VCC1", "LOGIC_VCC": "VCC1",
    "VCC2": "VCC2", "12V": "VCC2", "VM": "VCC2", "VMOT": "VCC2", "VS": "VCC2", "V+": "VCC2",
    "GND": "GND", "GND1": "GND", "GND2": "GND", "GND3": "GND", "GND4": "GND", "-": "GND", "0V": "GND",
    "EN1": "EN1", "ENA": "EN1", "EN1,2": "EN1", "1,2EN": "EN1", "ENABLE1": "EN1", "ENABLEA": "EN1",
    "EN2": "EN2", "ENB": "EN2", "EN3,4": "EN2", "3,4EN": "EN2", "ENABLE2": "EN2", "ENABLEB": "EN2",
    "IN1": "IN1", "1A": "IN1", "INPUT1": "IN1", "A1": "IN1",
    "IN2": "IN2", "2A": "IN2", "INPUT2": "IN2", "A2": "IN2",
    "IN3": "IN3", "3A": "IN3", "INPUT3": "IN3", "B1": "IN3",
    "IN4": "IN4", "4A": "IN4", "INPUT4": "IN4", "B2": "IN4",
    "OUT1": "OUT1", "1Y": "OUT1", "OUTPUT1": "OUT1", "M1A": "OUT1", "MOTOR1_A": "OUT1",
    "OUT2": "OUT2", "2Y": "OUT2", "OUTPUT2": "OUT2", "M1B": "OUT2", "MOTOR1_B": "OUT2",
    "OUT3": "OUT3", "3Y": "OUT3", "OUTPUT3": "OUT3", "M2A": "OUT3", "MOTOR2_A": "OUT3",
    "OUT4": "OUT4", "4Y": "OUT4", "OUTPUT4": "OUT4", "M2B": "OUT4", "MOTOR2_B": "OUT4",
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
    "wokwi-photoresistor-sensor": _ANALOG_4PIN_ALIASES,
    "wokwi-soil-moisture-sensor": _ANALOG_4PIN_ALIASES,
    "wokwi-rain-sensor": _ANALOG_4PIN_ALIASES,
    "wokwi-water-sensor": _ANALOG_4PIN_ALIASES,
    "wokwi-gas-sensor": _ANALOG_4PIN_ALIASES,
    "wokwi-flame-sensor": _ANALOG_4PIN_ALIASES,
    "wokwi-small-sound-sensor": _ANALOG_4PIN_ALIASES,
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
    "wokwi-hc-05": _BLUETOOTH_PIN_ALIASES,
    "wokwi-hc-06": _BLUETOOTH_PIN_ALIASES,
    "wokwi-l293d": _MOTOR_DRIVER_PIN_ALIASES,
    "wokwi-l298n": _MOTOR_DRIVER_PIN_ALIASES,
    "wokwi-dc-motor": {
        "1": "1", "+": "1", "POS": "1", "A": "1", "M+": "1", "IN1": "1", "PIN1": "1", "PIN_1": "1", "RED": "1", "VCC": "1",
        "2": "2", "-": "2", "NEG": "2", "B": "2", "M-": "2", "IN2": "2", "PIN2": "2", "PIN_2": "2", "BLACK": "2", "GND": "2",
    },
    "wokwi-pir-motion-sensor": {
        "VCC": "VCC", "5V": "VCC", "V+": "VCC", "+": "VCC", "1": "VCC",
        "GND": "GND", "-": "GND", "0V": "GND", "GROUND": "GND", "2": "GND",
        "OUT": "OUT", "SIG": "OUT", "SIGNAL": "OUT", "D0": "OUT", "DO": "OUT", "DATA": "OUT", "3": "OUT",
    },
    "wokwi-dht22": {
        "VCC": "VCC", "5V": "VCC", "3.3V": "VCC", "V+": "VCC", "+": "VCC", "1": "VCC",
        "SDA": "SDA", "DATA": "SDA", "OUT": "SDA", "SIG": "SDA", "SIGNAL": "SDA", "DAT": "SDA", "2": "SDA",
        "GND": "GND", "-": "GND", "0V": "GND", "GROUND": "GND", "4": "GND", "3": "GND",
    },
    "wokwi-analog-joystick": {
        "VCC": "VCC", "5V": "VCC", "+5V": "VCC", "V+": "VCC",
        "GND": "GND", "-": "GND", "0V": "GND",
        "VERT": "VERT", "VRX": "VERT", "X": "VERT", "Y": "VERT", "VRY": "VERT",
        "HORZ": "HORZ", "H": "HORZ",
        "SEL": "SEL", "SW": "SEL", "BTN": "SEL", "BUTTON": "SEL",
    },
    "wokwi-relay-module": {
        "VCC": "VCC", "5V": "VCC", "V+": "VCC", "+": "VCC",
        "GND": "GND", "-": "GND", "0V": "GND",
        "IN": "IN", "SIG": "IN", "SIGNAL": "IN", "S": "IN", "IN1": "IN",
        "COM": "COM", "COMMON": "COM",
        "NO": "NO",
        "NC": "NC",
    },
    "wokwi-rgb-led": {
        "R": "R", "RED": "R", "1": "R",
        "G": "G", "GREEN": "G", "3": "G",
        "B": "B", "BLUE": "B", "4": "B",
        "COM": "COM", "C": "COM", "GND": "COM", "VCC": "COM", "CATHODE": "COM", "ANODE": "COM", "2": "COM",
    },
    "wokwi-lcd1602": {
        "VCC": "VCC", "5V": "VCC", "VDD": "VCC",
        "GND": "GND", "VSS": "GND", "-": "GND",
        "SDA": "SDA", "DATA": "SDA",
        "SCL": "SCL", "CLK": "SCL",
    },
    "wokwi-ssd1306": {
        "VCC": "VCC", "5V": "VCC", "3.3V": "VCC", "VDD": "VCC",
        "GND": "GND", "-": "GND",
        "SDA": "SDA", "DATA": "SDA",
        "SCL": "SCL", "CLK": "SCL",
    },
    "wokwi-ir-receiver": {
        "VCC": "VCC", "5V": "VCC", "V+": "VCC",
        "GND": "GND", "-": "GND",
        "DAT": "DAT", "OUT": "DAT", "SIG": "DAT", "DATA": "DAT", "S": "DAT",
    },
    "wokwi-ntc-temperature-sensor": {
        "VCC": "VCC", "5V": "VCC",
        "GND": "GND", "-": "GND",
        "OUT": "OUT", "AO": "OUT", "SIG": "OUT", "A0": "OUT",
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
1. KOORDİNAT YASAĞI: Asla breadboard pini koordinatı (5A, 12C, bn.1) veya piksel koordinatı üretme!
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


def safe_parse_llm_json(raw_text: str) -> Dict[str, Any]:
    """
    LLM tarafından üretilen JSON metinlerini toleranslı ve güvenli bir şekilde ayrıştırır.
    - Markdown bloklarını (```json ... ```) ve düşünce etiketlerini (<think>...</think>) temizler.
    - strict=False ile literal satır sonları ve kontrol karakterlerine izin verir.
    - Sondaki gereksiz virgülleri (trailing commas) temizler.
    - Kapanmamış tırnak ve parantezleri (unterminated string / truncated JSON) onarır.
    """
    text = clean_llm_json_response(raw_text)

    # 1. Deneme: strict=False ile doğrudan çözümleme
    try:
        return json.loads(text, strict=False)
    except Exception:
        pass

    # 2. Deneme: Sondaki sarkan virgülleri temizle (Örn: [1, 2, ], veya {"a": 1, })
    fixed = re.sub(r",\s*([}\]])", r"\1", text)
    try:
        return json.loads(fixed, strict=False)
    except Exception:
        pass

    # 3. Deneme: Kapanmamış tırnak veya parantez tamamlama (Unterminated string / Truncated JSON)
    unescaped_quotes = len(re.findall(r'(?<!\\)"', fixed))
    cand = fixed
    if unescaped_quotes % 2 != 0:
        cand += '"'

    # Açık kalan parantezleri sırayla kapat (yalnızca tırnak dışındakiler)
    in_str = False
    escape = False
    open_curly = 0
    open_square = 0
    for ch in cand:
        if escape:
            escape = False
            continue
        if ch == '\\':
            escape = True
            continue
        if ch == '"':
            in_str = not in_str
            continue
        if not in_str:
            if ch == '{':
                open_curly += 1
            elif ch == '}':
                open_curly = max(0, open_curly - 1)
            elif ch == '[':
                open_square += 1
            elif ch == ']':
                open_square = max(0, open_square - 1)

    if open_square > 0:
        cand += "]" * open_square
    if open_curly > 0:
        cand += "}" * open_curly

    try:
        return json.loads(cand, strict=False)
    except Exception:
        pass

    # 4. Deneme: Alan bazlı acil durum çıkarımı
    recovered: Dict[str, Any] = {}
    m_proj = re.search(r'"proje_adi"\s*:\s*"([^"\\]*(?:\\.[^"\\]*)*)"', text)
    if m_proj:
        recovered["proje_adi"] = m_proj.group(1)

    m_msg = re.search(r'"karsilama_mesaji"\s*:\s*"([^"\\]*(?:\\.[^"\\]*)*)"', text)
    if m_msg:
        recovered["karsilama_mesaji"] = m_msg.group(1)

    m_code = re.search(r'"arduino_kodu"\s*:\s*"((?:[^"\\]|\\.)*)', text, re.DOTALL)
    if m_code:
        raw_c = m_code.group(1)
        if raw_c.endswith('"'):
            raw_c = raw_c[:-1]
        try:
            recovered["arduino_kodu"] = raw_c.encode('utf-8').decode('unicode_escape')
        except Exception:
            recovered["arduino_kodu"] = raw_c.replace(r'\n', '\n').replace(r'\"', '"')

    m_net = re.search(r'"netlist"\s*:\s*(\{.*?\})\s*,\s*"(?:arduino_kodu|guvenlik|akis)', text, re.DOTALL)
    if m_net:
        try:
            recovered["netlist"] = json.loads(m_net.group(1), strict=False)
        except Exception:
            pass

    if "netlist" not in recovered:
        recovered["netlist"] = {"board": "arduino-uno", "components": [], "connections": []}

    if recovered.get("arduino_kodu"):
        return recovered

    return json.loads(text, strict=False)


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

    # 3. SoftwareSerial, DHT, Ultrasonic vb. kurucu çağrılarını tara: SoftwareSerial bt(RX_PIN, TX_PIN); veya DHT dht(DHT_PIN, DHT22);
    for m in re.finditer(
        r"\b(?:SoftwareSerial|DHT|Ultrasonic)\s+[A-Za-z_]\w*\s*\(\s*([A-Za-z0-9_]+)(?:\s*,\s*([A-Za-z0-9_]+))?",
        clean_code
    ):
        for grp in (m.group(1), m.group(2)):
            if grp:
                resolved = resolve_token_to_uno_pin(grp)
                if resolved:
                    used_pins.add(resolved)

    # 4. I2C modülleri (Wire.h, LiquidCrystal_I2C, Adafruit_SSD1306) varsa uno.A4 ve uno.A5 pinlerini de kullanılan pinlere dahil et
    if any(k in clean_code for k in ("Wire.h", "LiquidCrystal_I2C", "Adafruit_SSD1306", "SSD1306")):
        used_pins.add("uno.A4")
        used_pins.add("uno.A5")

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

    # Geriye dönük uyumluluk: Eski 4 alanlı akis_adimlari gelmişse ve yeni akis_diyagrami yoksa adaptörden geçir.
    # Generic sabit metin doldurma kaldırıldı; yeni projelerde akış doğrudan son Arduino kodundan üretilir.
    if isinstance(new_data.get("akis_diyagrami"), dict):
        pass
    elif isinstance(new_data.get("akis_adimlari"), dict):
        raw_akis = new_data["akis_adimlari"]
        if any(str(raw_akis.get(k) or "").strip() for k in ("gozlemle", "karar_ver", "evet_sonucu", "hayir_sonucu")):
            adapted = legacy_akis_to_diyagram(raw_akis, norm_comps)
            new_data["akis_diyagrami"] = adapted.model_dump()
    else:
        new_data["akis_adimlari"] = None

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


def build_token_safe_circuit_repair_prompt(
    errors: List[str],
    current_output: str,
    user_prompt: str,
    inventory: Optional[List[str]] = None
) -> str:
    """
    Token korumalı ve hedef odaklı devre onarım promptu:
    Gereksiz token tüketimini önlemek için hatalı çıktının sadece gerekli bölümlerini kırpar
    ve modele tam olarak hangi bağlantıların ve komponentlerin hatalı olduğunu bildirir.
    Maksimum token tasarrufu sağlar.
    """
    err_bullets = "\n".join(f"- {e}" for e in errors[:8])
    truncated_output = (current_output or "").strip()
    if len(truncated_output) > 3500:
        truncated_output = truncated_output[:3500] + "\n... [kalan JSON kırpıldı]"

    inv_str = f"\nENVANTER:\n{json.dumps(inventory, ensure_ascii=False)}" if inventory else ""

    return f"""DİKKAT: Önceki ürettiğin devre ve kod çıktısında aşağıdaki bağlantı/komponent hataları tespit edildi:
{err_bullets}

KULLANICI PROJE İSTEĞİ:
"{user_prompt}"{inv_str}

HATALI ÇIKTI ÖZETİ:
{truncated_output}

GÖREV (TOKEN KORUMALI DÜZELTME):
Lütfen projeyi baştan üretmeden, SADECE yukarıdaki bağlantı/komponent hatalarını ve pin uyumsuzluklarını düzelterek geçerli bir JSON nesnesi üret:
- Devre şemasında (netlist.components) tanımlanan her bileşenin en az 2 pini doğru yerlere bağlanmalı (boşta bacak kalmamalı).
- Aktif parçalar (LED, Servo, Buzzer, Sensör) mutlaka Arduino'nun ilgili sinyal pinine (uno.D* veya uno.A*) bağlanmalı.
- Kısa devre yapılmamalı (5V ile GND veya aynı parçanın iki ucu birleştirilemez).
- arduino_kodu içindeki pinler devredeki uno.* pinleriyle %100 birebir uyuşmalı.
Sadece geçerli JSON nesnesi döndür."""


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


def get_gemini_available_models(api_key: Optional[str] = None) -> List[Dict[str, Any]]:
    """
    Google Gemini API üzerinden (eğer geçerli bir API key / token verilmişse gerçek zamanlı sorgulayarak,
    verilmemişse varsayılan güncel Gemini modellerini kullanarak) seçilebilir Gemini modellerini döner.
    """
    default_gemini_models = [
        {"id": "gemini/gemini-3.8-flash", "name": "Gemini 3.8 Flash (En Yeni & Önerilen)", "raw_name": "gemini-3.8-flash", "provider": "gemini", "category": "Google Gemini", "badge": "☁️ Bulut"},
        {"id": "gemini/gemini-3.5-flash-lite", "name": "Gemini 3.5 Flash Lite (Hızlı & Ekonomik)", "raw_name": "gemini-3.5-flash-lite", "provider": "gemini", "category": "Google Gemini", "badge": "☁️ Bulut"},
        {"id": "gemini/gemini-2.5-flash", "name": "Gemini 2.5 Flash (Legacy)", "raw_name": "gemini-2.5-flash", "provider": "gemini", "category": "Google Gemini", "badge": "☁️ Bulut"},
        {"id": "gemini/gemini-2.5-pro", "name": "Gemini 2.5 Pro (Legacy)", "raw_name": "gemini-2.5-pro", "provider": "gemini", "category": "Google Gemini", "badge": "☁️ Bulut"},
    ]

    effective_key = (api_key or os.getenv("GEMINI_API_KEY") or "").strip()
    if not effective_key:
        return default_gemini_models

    try:
        res = httpx.get(
            f"https://generativelanguage.googleapis.com/v1beta/models?key={effective_key}",
            timeout=5.0
        )
        if res.status_code == 200:
            data = res.json()
            fetched: List[Dict[str, Any]] = []
            seen_ids: Set[str] = set()
            for m in data.get("models", []):
                methods = m.get("supportedGenerationMethods") or []
                if "generateContent" not in methods:
                    continue
                raw_name = str(m.get("name") or "").replace("models/", "").strip()
                if not raw_name.startswith("gemini-"):
                    continue
                # Sadece metin/kod üretim modellerini al (vision/embedding/tts/imagen hariç)
                if any(skip in raw_name for skip in ("embedding", "aqa", "imagen", "veo", "tts", "audio", "live")):
                    continue
                full_id = f"gemini/{raw_name}"
                if full_id in seen_ids:
                    continue
                seen_ids.add(full_id)
                display_name = str(m.get("displayName") or raw_name).strip()
                fetched.append({
                    "id": full_id,
                    "name": f"{display_name} ({raw_name})",
                    "raw_name": raw_name,
                    "provider": "gemini",
                    "category": "Google Gemini",
                    "badge": "☁️ Bulut"
                })
            if fetched:
                # Önemli modelleri (3.8-flash, 3.5-flash-lite, 2.5-flash, 2.5-pro) üstte sırala
                priority = [
                    "gemini-3.8-flash", "gemini-3.5-flash-lite",
                    "gemini-2.5-flash", "gemini-2.5-pro"
                ]
                fetched.sort(key=lambda x: (
                    priority.index(x["raw_name"]) if x["raw_name"] in priority else 99,
                    x["raw_name"]
                ))
                return fetched
    except Exception as e:
        print(f"[Gemini Models] API'den model listesi çekilemedi, varsayılan liste kullanılıyor: {e}")

    return default_gemini_models


def get_all_available_models(
    ollama_url: str = "http://127.0.0.1:11434",
    gemini_api_key: Optional[str] = None
) -> Dict[str, Any]:
    """Tüm yerel ve bulut modelleri ve yapılandırma durumlarını listeler."""
    local_models = get_installed_ollama_models(ollama_url)
    ollama_running = len(local_models) > 0

    gemini_models = get_gemini_available_models(gemini_api_key)

    other_cloud_models = [
        {"id": "gpt-4o-mini", "name": "GPT-4o Mini (Hızlı & Ekonomik)", "raw_name": "gpt-4o-mini", "provider": "openai", "category": "OpenAI", "badge": "☁️ Bulut"},
        {"id": "gpt-4o", "name": "GPT-4o (Amiral Gemisi)", "raw_name": "gpt-4o", "provider": "openai", "category": "OpenAI", "badge": "☁️ Bulut"},
        {"id": "gpt-4.1-mini", "name": "GPT-4.1 Mini (Yeni Nesil Kodlama)", "raw_name": "gpt-4.1-mini", "provider": "openai", "category": "OpenAI", "badge": "☁️ Bulut"},
        {"id": "claude-3-5-haiku-20241022", "name": "Claude 3.5 Haiku (Hızlı & Canlı)", "raw_name": "claude-3-5-haiku-20241022", "provider": "anthropic", "category": "Anthropic Claude", "badge": "☁️ Bulut"},
        {"id": "claude-3-5-sonnet-20241022", "name": "Claude 3.5 Sonnet (Kodlama Uzmanı)", "raw_name": "claude-3-5-sonnet-20241022", "provider": "anthropic", "category": "Anthropic Claude", "badge": "☁️ Bulut"},
    ]

    cloud_models = gemini_models + other_cloud_models

    configured_keys = {
        "gemini": bool(gemini_api_key or os.getenv("GEMINI_API_KEY")),
        "openai": bool(os.getenv("OPENAI_API_KEY")),
        "anthropic": bool(os.getenv("ANTHROPIC_API_KEY")),
    }

    default_model = "ollama/qwen2.5-coder:1.5b" if any(m["id"] == "ollama/qwen2.5-coder:1.5b" for m in local_models) else (
        local_models[0]["id"] if local_models else "gemini/gemini-2.5-flash"
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
    chosen_model = model or "gemini/gemini-2.5-flash"
    prompt = f"""Aşağıdaki Arduino Uno kodunda derleme/yükleme hatası oluştu.
LÜTFEN HATAYI DÜZELT VE SADECE DÜZELTİLMİŞ C++ ARDUINO KODUNU DÖNDÜR.
Değişken, sabit ve fonksiyon adlarında Türkçe harf (ç, ğ, ı, İ, ö, ş, ü) KULLANMA; sadece İngilizce harf, rakam ve alt çizgi kullan.

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
        return sanitize_arduino_identifiers(out)
    except Exception as e:
        print(f"[Self-Healing Hatası] Kod düzeltilemedi ({e}). Orijinal kod korunuyor.")
        return code


# =========================================================
# ADMIN AI LOG KAYIT SİSTEMİ (İSTEK & CEVAP İZLEYİCİ)
# =========================================================

AI_LOGS_FILE = os.path.join(os.path.dirname(__file__), "ai_logs.json")
AI_LOGS_MEMORY: List[AILogEntry] = []


def _load_ai_logs_from_disk() -> None:
    global AI_LOGS_MEMORY
    if AI_LOGS_MEMORY:
        return
    if os.path.isfile(AI_LOGS_FILE):
        try:
            with open(AI_LOGS_FILE, "r", encoding="utf-8") as f:
                raw_list = json.load(f)
            if isinstance(raw_list, list):
                AI_LOGS_MEMORY = [AILogEntry(**item) for item in raw_list[:100]]
        except Exception:
            AI_LOGS_MEMORY = []


def record_ai_log(
    stage: str,
    model: str,
    provider: str,
    duration_ms: int,
    status: str,
    user_goal: str,
    system_prompt: str,
    user_prompt: str,
    raw_response: str,
    processed_output: Optional[Dict[str, Any]] = None,
    notes: Optional[List[str]] = None,
    prompt_tokens: Optional[int] = None,
    completion_tokens: Optional[int] = None,
    total_tokens: Optional[int] = None
) -> AILogEntry:
    """Yapay zekaya gönderilen her isteği ve alınan her cevabı Admin ekranı için kaydeder."""
    _load_ai_logs_from_disk()
    tot = total_tokens
    if tot is None and (prompt_tokens is not None or completion_tokens is not None):
        tot = (prompt_tokens or 0) + (completion_tokens or 0)

    entry = AILogEntry(
        id=f"log_{int(time.time() * 1000)}_{uuid.uuid4().hex[:4]}",
        timestamp=time.strftime("%d.%m.%Y %H:%M:%S"),
        stage=stage,
        model=model,
        provider=provider,
        duration_ms=duration_ms,
        status=status,
        user_goal=user_goal,
        system_prompt=system_prompt,
        user_prompt=user_prompt,
        raw_response=raw_response,
        processed_output=processed_output,
        notes=notes or [],
        prompt_tokens=prompt_tokens,
        completion_tokens=completion_tokens,
        total_tokens=tot
    )
    AI_LOGS_MEMORY.insert(0, entry)
    del AI_LOGS_MEMORY[100:]
    try:
        with open(AI_LOGS_FILE, "w", encoding="utf-8") as f:
            json.dump([e.model_dump() for e in AI_LOGS_MEMORY], f, ensure_ascii=False, indent=2)
    except Exception as e:
        print(f"[AI Log] Disk yazma hatası: {e}")
    return entry


def get_ai_logs() -> List[AILogEntry]:
    _load_ai_logs_from_disk()
    return AI_LOGS_MEMORY


def clear_ai_logs() -> bool:
    global AI_LOGS_MEMORY
    AI_LOGS_MEMORY = []
    if os.path.isfile(AI_LOGS_FILE):
        try:
            os.remove(AI_LOGS_FILE)
        except Exception:
            pass
    return True


# =========================================================
# TEK SORGU (ONE-SHOT) TAM PROJE ÜRETİMİ VE DOĞRULAMA
# (Devre Şeması + Akış Diyagramı + Arduino C++ Kodu Tek Seferde)
# =========================================================

ONE_SHOT_SYSTEM_PROMPT = """Sen çocuklar için Arduino Uno devre ve C++ kodlama uzmanısın.
Kullanıcının proje isteğine göre TEK BİR JSON nesnesi içinde:
1. "netlist": Sadece kullanıcının istediği parçaları (components) ve eksiksiz pin bağlantılarını (connections)
2. "arduino_kodu": Netlist'teki pinlerle %100 aynı pin numaralarını kullanan, derlenebilir Arduino Uno C++ kodunu
üret. (Akış diyagramı ayrı aşamada koddan otomatik çıkarılacaktır; JSON'a akis_adimlari ekleme.)

KESİN KURALLAR:
1. SADECE İSTENEN PARÇALARI EKLE! Kullanıcının istemediği buton, buzzer, servo veya sensörü ASLA ekleme.
   - ÖNEMLİ: Eğer kullanıcı "araba", "DC motor", "tekerlek" istiyorsa `wokwi-l293d` (veya `wokwi-l298n`) motor sürücü ve `wokwi-dc-motor` kullan; kullanıcı açıkça "servo" istemedikçe araba projesine `wokwi-servo` EKLEME!
   - Kullanıcı açıkça "servo motor" veya "günebakan / bariyer / robot kol" isterse `wokwi-servo` ekle.
2. ÇOKLU PARÇA VE GERİLİM BÖLÜCÜ KURALI:
   - Kullanıcı "2 tane LDR", "çift LDR", "2 motorlu araba" gibi birden fazla parça isterse istenen sayıda ayrı bileşen ekle (`ldr1`, `ldr2` veya `motor1`, `motor2` vb.).
   - Her 2 bacaklı LDR (`wokwi-photoresistor`) için MUTLAKA ayrı bir `10kΩ` direnç (`r1`, `r2` vb.) ekle ve gerilim bölücü kur (`ldr1.1 -> 5V`, `ldr1.2 -> uno.A0`, `ldr1.2 -> r1.1`, `r1.2 -> GND`).
   - Her LED (`wokwi-led`) için seri bir `220Ω` koruma direnci ekle.
3. Asla breadboard pin koordinatı (5A, 12C vb.) yazma. Sadece şu standart tipleri ve pinleri kullan:
- wokwi-resistor: r1.1, r1.2 (props:{"value":"220"} veya {"value":"10000"})
- wokwi-led: led1.A, led1.C (props:{"color":"red"|"green"|"yellow"|"blue"})
- wokwi-rgb-led: rgb1.R, rgb1.G, rgb1.B, rgb1.COM
- wokwi-photoresistor (2 bacaklı LDR): ldr1.1, ldr1.2
- wokwi-photoresistor-sensor (4 pinli modül LDR): ldr1.VCC, ldr1.GND, ldr1.AO, ldr1.DO
- wokwi-potentiometer: pot1.GND, pot1.SIG, pot1.VCC
- wokwi-buzzer: buzzer1.1, buzzer1.2
- wokwi-pushbutton: btn1.1, btn1.2
- wokwi-servo: servo1.V+, servo1.GND, servo1.PWM
- wokwi-hc-sr04 (Ultrasonik Mesafe): hcsr1.VCC, hcsr1.GND, hcsr1.TRIG, hcsr1.ECHO
- wokwi-hc-05 (Bluetooth HC-05): hc05.VCC, hc05.GND, hc05.TXD, hc05.RXD
- wokwi-hc-06 (Bluetooth HC-06): hc06.VCC, hc06.GND, hc06.TXD, hc06.RXD
- wokwi-l293d (Motor Sürücü L293D): l293d.VCC1, l293d.VCC2, l293d.GND, l293d.EN1, l293d.EN2, l293d.IN1, l293d.IN2, l293d.IN3, l293d.IN4, l293d.OUT1, l293d.OUT2, l293d.OUT3, l293d.OUT4
- wokwi-l298n (Motor Sürücü L298N): l298n.VCC, l298n.GND, l298n.ENA, l298n.ENB, l298n.IN1, l298n.IN2, l298n.IN3, l298n.IN4, l298n.OUT1, l298n.OUT2, l298n.OUT3, l298n.OUT4
- wokwi-dc-motor (DC Motor): motor1.1, motor1.2 (L293D/L298N OUT1-OUT2 veya OUT3-OUT4 pinlerine ya da röleye bağlanır)
- wokwi-pir-motion-sensor (PIR Hareket): pir1.VCC, pir1.GND, pir1.OUT
- wokwi-dht22 (DHT11/DHT22 Sıcaklık & Nem): dht1.VCC, dht1.GND, dht1.SDA
- wokwi-analog-joystick (Joystick): joy1.VCC, joy1.GND, joy1.VERT, joy1.HORZ, joy1.SEL
- wokwi-relay-module (5V Röle): relay1.VCC, relay1.GND, relay1.IN
- wokwi-lcd1602 (I2C 16x2 LCD): lcd1.VCC, lcd1.GND, lcd1.SDA (uno.A4), lcd1.SCL (uno.A5)
- wokwi-ssd1306 (I2C OLED Ekran): oled1.VCC, oled1.GND, oled1.SDA (uno.A4), oled1.SCL (uno.A5)
- wokwi-soil-moisture-sensor (Toprak Nem): soil1.VCC, soil1.GND, soil1.AO, soil1.DO
- wokwi-rain-sensor (Yağmur Sensörü): rain1.VCC, rain1.GND, rain1.AO, rain1.DO
- wokwi-water-sensor (Su Seviye Sensörü): water1.VCC, water1.GND, water1.AO, water1.DO
- wokwi-gas-sensor (MQ-2 Gaz/Duman): gas1.VCC, gas1.GND, gas1.AO, gas1.DO
- wokwi-flame-sensor (Alev Sensörü): flame1.VCC, flame1.GND, flame1.AO, flame1.DO
- wokwi-small-sound-sensor (Ses/Mikrofon): sound1.VCC, sound1.GND, sound1.AO, sound1.DO
- wokwi-ir-receiver (IR Alıcı): ir1.VCC, ir1.GND, ir1.DAT
4. Güç bağlantılarını her zaman "to":"5V" veya "to":"GND" yönünde yaz. Arduino pinlerini "uno.D2".."uno.D13", "uno.A0".."uno.A5" yaz.
5. "arduino_kodu" içindeki pinler ile "connections" içindeki "uno.*" pinleri BİREBİR AYNI olmalı.
6. "arduino_kodu" içindeki değişken, sabit ve fonksiyon adlarında SADECE İngilizce harf, rakam ve alt çizgi kullan (ç, ğ, ı, İ, ö, ş, ü YASAK; örn: ESIK_DEGER, isikDegeri). Arduino derleyicisi Türkçe harfli adları derleyemez. Türkçe karakter sadece yorumlarda ve tırnak içindeki metinlerde olabilir.

ÖRNEK 1 (2 Adet 2 Bacaklı LDR + 2 Adet 10k Direnç + Servo ile Günebakan):
{"proje_adi":"Çift LDR ile Günebakan Servo Projesi","karsilama_mesaji":"İki LDR sensöründen hangisine daha çok ışık geliyorsa servo motoru o yöne çeviren günebakan devresi!","gerekli_parcalar":["ARDUINO_UNO","BREADBOARD","LDR_DISCRETE","RESISTOR_10K","SERVO_SG90"],"netlist":{"board":"arduino-uno","components":[{"id":"ldr1","type":"wokwi-photoresistor","props":{},"label":"Sol LDR (2 Bacaklı)"},{"id":"r1","type":"wokwi-resistor","props":{"value":"10000"},"label":"Sol 10kΩ Direnç"},{"id":"ldr2","type":"wokwi-photoresistor","props":{},"label":"Sağ LDR (2 Bacaklı)"},{"id":"r2","type":"wokwi-resistor","props":{"value":"10000"},"label":"Sağ 10kΩ Direnç"},{"id":"servo1","type":"wokwi-servo","props":{},"label":"SG90 Servo Motor"}],"connections":[{"from":"ldr1.1","to":"5V","color":"red"},{"from":"ldr1.2","to":"uno.A0","color":"green"},{"from":"ldr1.2","to":"r1.1","color":"green"},{"from":"r1.2","to":"GND","color":"black"},{"from":"ldr2.1","to":"5V","color":"red"},{"from":"ldr2.2","to":"uno.A1","color":"blue"},{"from":"ldr2.2","to":"r2.1","color":"blue"},{"from":"r2.2","to":"GND","color":"black"},{"from":"servo1.V+","to":"5V","color":"red"},{"from":"servo1.GND","to":"GND","color":"black"},{"from":"uno.D9","to":"servo1.PWM","color":"orange"}]},"arduino_kodu":"#include <Servo.h>\\n\\nconst int LDR_SOL = A0;\\nconst int LDR_SAG = A1;\\nconst int SERVO_PIN = 9;\\nServo gunebakanServo;\\n\\nvoid setup() {\\n  Serial.begin(9600);\\n  gunebakanServo.attach(SERVO_PIN);\\n  gunebakanServo.write(90);\\n}\\n\\nvoid loop() {\\n  int isikSol = analogRead(LDR_SOL);\\n  int isikSag = analogRead(LDR_SAG);\\n  if (isikSol > isikSag + 30) {\\n    gunebakanServo.write(135);\\n  } else if (isikSag > isikSol + 30) {\\n    gunebakanServo.write(45);\\n  } else {\\n    gunebakanServo.write(90);\\n  }\\n  delay(100);\\n}","guvenlik_notu":"Her iki 2 bacaklı LDR için ayrı 10kΩ dirençlerle iki adet gerilim bölücü kurduk."}

ÖRNEK 2 (Bluetooth HC-05 + L293D Motor Sürücü + 2x DC Motor ile Akıllı Araba):
{"proje_adi":"Bluetooth Kontrollü Akıllı Araba","karsilama_mesaji":"HC-05 Bluetooth modülü ve L293D motor sürücü ile telefondan kontrol edilen 2 motorlu araba devresi!","gerekli_parcalar":["ARDUINO_UNO","BREADBOARD","BLUETOOTH_HC05","MOTOR_DRIVER_L293D","DC_MOTOR_5V"],"netlist":{"board":"arduino-uno","components":[{"id":"hc05","type":"wokwi-hc-05","props":{},"label":"HC-05 Bluetooth Modülü"},{"id":"l293d","type":"wokwi-l293d","props":{},"label":"L293D Motor Sürücü"},{"id":"motor1","type":"wokwi-dc-motor","props":{},"label":"Sol DC Motor"},{"id":"motor2","type":"wokwi-dc-motor","props":{},"label":"Sağ DC Motor"}],"connections":[{"from":"hc05.VCC","to":"5V","color":"red"},{"from":"hc05.GND","to":"GND","color":"black"},{"from":"hc05.TXD","to":"uno.D10","color":"green"},{"from":"hc05.RXD","to":"uno.D11","color":"blue"},{"from":"l293d.VCC1","to":"5V","color":"red"},{"from":"l293d.VCC2","to":"5V","color":"red"},{"from":"l293d.GND","to":"GND","color":"black"},{"from":"l293d.EN1","to":"5V","color":"red"},{"from":"l293d.EN2","to":"5V","color":"red"},{"from":"l293d.IN1","to":"uno.D2","color":"orange"},{"from":"l293d.IN2","to":"uno.D3","color":"yellow"},{"from":"l293d.IN3","to":"uno.D4","color":"green"},{"from":"l293d.IN4","to":"uno.D5","color":"blue"},{"from":"l293d.OUT1","to":"motor1.1","color":"orange"},{"from":"l293d.OUT2","to":"motor1.2","color":"black"},{"from":"l293d.OUT3","to":"motor2.1","color":"green"},{"from":"l293d.OUT4","to":"motor2.2","color":"black"}]},"arduino_kodu":"#include <SoftwareSerial.h>\\n\\nconst int BT_RX = 10;\\nconst int BT_TX = 11;\\nSoftwareSerial bt(BT_RX, BT_TX);\\n\\nconst int IN1 = 2;\\nconst int IN2 = 3;\\nconst int IN3 = 4;\\nconst int IN4 = 5;\\n\\nvoid setup() {\\n  Serial.begin(9600);\\n  bt.begin(9600);\\n  pinMode(IN1, OUTPUT);\\n  pinMode(IN2, OUTPUT);\\n  pinMode(IN3, OUTPUT);\\n  pinMode(IN4, OUTPUT);\\n}\\n\\nvoid loop() {\\n  if (bt.available()) {\\n    char c = bt.read();\\n    if (c == 'F') {\\n      digitalWrite(IN1, HIGH); digitalWrite(IN2, LOW);\\n      digitalWrite(IN3, HIGH); digitalWrite(IN4, LOW);\\n    } else if (c == 'B') {\\n      digitalWrite(IN1, LOW); digitalWrite(IN2, HIGH);\\n      digitalWrite(IN3, LOW); digitalWrite(IN4, HIGH);\\n    } else if (c == 'L') {\\n      digitalWrite(IN1, LOW); digitalWrite(IN2, HIGH);\\n      digitalWrite(IN3, HIGH); digitalWrite(IN4, LOW);\\n    } else if (c == 'R') {\\n      digitalWrite(IN1, HIGH); digitalWrite(IN2, LOW);\\n      digitalWrite(IN3, LOW); digitalWrite(IN4, HIGH);\\n    } else {\\n      digitalWrite(IN1, LOW); digitalWrite(IN2, LOW);\\n      digitalWrite(IN3, LOW); digitalWrite(IN4, LOW);\\n    }\\n  }\\n}","guvenlik_notu":"DC motorlar yüksek akım çektiği için Arduino pinlerine doğrudan değil, L293D motor sürücü üzerinden bağlanır."}
"""

REVISION_SYSTEM_PROMPT = """Sen çocuklar için Arduino devre ve C++ kodu geliştirme ve revizyon uzmanısın.
Sana MEVCUT PROJE (devre şeması netlist, akış adımları ve Arduino C++ kodu) ile kullanıcının İSTEDİĞİ DEĞİŞİKLİK / REVİZYON verilecek.
Görevin mevcut projeyi kullanıcının isteği doğrultusunda GÜNCELLEMEK ve TEK BİR JSON nesnesi olarak döndürmektir.

KESİN REVİZYON KURALLARI:
1. MEVCUT ÇALIŞAN DEVREYİ VE KODU KORU:
   - Halihazırda çalışan pin bağlantılarını gereksiz yere değiştirme veya silme.
   - Sadece kullanıcının talep ettiği yeni sensör, buton, motor veya LED'leri ekle ya da istenen davranışı değiştir.
2. NETLİST VE KOD SENKRONİZASYONU:
   - Yeni bir parça ekleniyorsa `netlist.components` ve `netlist.connections` içine eksiksiz ekle.
   - Arduino C++ kodunda tanımlanan tüm pinler netlist'teki `uno.D*` ve `uno.A*` pinleriyle %100 birebir uyuşmalıdır!
   - Çıkış parçalarını (LED'ler 220Ω dirençle, butonlar 10kΩ dirençle veya INPUT_PULLUP ile) standart Wokwi kurallarına uygun bağla.
3. AKIŞ VE KARŞILAMA:
   - `proje_adi`: Güncellenen projeyi yansıtacak sevimli bir başlık.
   - `karsilama_mesaji`: Yapılan revizyonu çocuğa özetleyen neşeli bir cümle (örn: "Harika fikir! Devrene sarı ikaz lambası ve mesafe uyarısı ekledik! 🚀").
   - `akis_adimlari`: Güncel devrenin çalışma mantığını anlatan (gozlemle, karar_ver, evet_sonucu, hayir_sonucu) adımları.
4. SADECE GEÇERLİ JSON DÖNDÜR:
   Markdown kod blokları veya fazladan açıklama yazma. Sadece {"proje_adi":"...","karsilama_mesaji":"...","gerekli_parcalar":[...],"netlist":{...},"akis_adimlari":{...},"arduino_kodu":"...","guvenlik_notu":"..."} JSON nesnesi döndür.
"""


def auto_complete_electrical_topology(netlist_dict: Dict[str, Any]) -> Tuple[Dict[str, Any], List[str]]:
    """
    Küçük yerel LLM modellerinin (örn. 1.5b) sık yaptığı iki elektriksel ihmali otomatik tamamlar:
    1) 2 bacaklı LDR (`wokwi-photoresistor`) `5V` ve `uno.A*` pinine bağlanmış ama GND'ye giden 10kΩ gerilim bölücü direnci unutulmuşsa,
       otomatik olarak `10kΩ Direnç` (`r_ldr1`, `r_ldr2`...) ekler ve `ldr.2 -> r.1`, `r.2 -> GND` bağlantısını kurar.
    2) LED (`wokwi-led`) doğrudan `uno.D*` ve `GND` arasına dirençsiz bağlanmışsa, araya `220Ω Direnç` ekler.
    """
    notes: List[str] = []
    comps: List[Dict[str, Any]] = list(netlist_dict.get("components") or [])
    conns: List[Dict[str, Any]] = list(netlist_dict.get("connections") or [])

    comp_by_id: Dict[str, Dict[str, Any]] = {c["id"]: c for c in comps if isinstance(c, dict) and c.get("id")}
    existing_ids: Set[str] = set(comp_by_id.keys())

    # 1. Her bileşen pininin nelere bağlı olduğunu çıkar
    adj: Dict[str, Set[str]] = {}
    for c in conns:
        f = str(c.get("from") or "").strip()
        t = str(c.get("to") or "").strip()
        if f and t:
            adj.setdefault(f, set()).add(t)
            adj.setdefault(t, set()).add(f)

    def next_resistor_id(prefix: str = "r") -> str:
        idx = 1
        while f"{prefix}{idx}" in existing_ids:
            idx += 1
        rid = f"{prefix}{idx}"
        existing_ids.add(rid)
        return rid

    # 2. 2-Bacaklı LDR (`wokwi-photoresistor`) gerilim bölücü direnç kontrolü
    ldr_list = [c for c in comps if c.get("type") == "wokwi-photoresistor"]
    for idx, ldr in enumerate(ldr_list, start=1):
        lid = ldr["id"]
        # Eğer etiketi sadece 'ldr1'/'ldr2' kalmışsa çocuk dostu isim ver
        if ldr.get("label") in (None, "", lid):
            ldr["label"] = f"{idx}. LDR Işık Sensörü (2 Bacaklı)" if len(ldr_list) > 1 else "2 Bacaklı LDR Sensörü"

        p1 = f"{lid}.1"
        p2 = f"{lid}.2"
        n1 = adj.get(p1, set())
        n2 = adj.get(p2, set())

        # Hangi bacak analog pine bağlı?
        sig_pin = p2 if any(nb.startswith("uno.A") or nb.startswith("uno.D") for nb in n2) else (
            p1 if any(nb.startswith("uno.A") or nb.startswith("uno.D") for nb in n1) else p2
        )
        pwr_pin = p1 if sig_pin == p2 else p2

        sig_neighbors = adj.get(sig_pin, set())
        has_resistor_on_sig = any(
            "." in nb and comp_by_id.get(nb.split(".", 1)[0], {}).get("type") == "wokwi-resistor"
            for nb in sig_neighbors
        )

        # Eğer diğer bacak hiçbir şeye bağlı değilse 5V'a bağla
        if not adj.get(pwr_pin):
            conns.append({"from": pwr_pin, "to": "5V", "color": "red"})
            adj.setdefault(pwr_pin, set()).add("5V")
            notes.append(f"'{ldr['label']}' ({pwr_pin}) için eksik 5V güç bağlantısı tamamlandı.")

        # Eğer sinyal bacağında 10kΩ gerilim bölücü direnç yoksa otomatik ekle!
        if not has_resistor_on_sig:
            rid = next_resistor_id("r")
            r_label = f"{idx}. 10kΩ Direnç (LDR Bölücü)" if len(ldr_list) > 1 else "10kΩ Direnç"
            new_r = {
                "id": rid,
                "type": "wokwi-resistor",
                "props": {"value": "10000"},
                "label": r_label
            }
            comps.append(new_r)
            comp_by_id[rid] = new_r
            conns.append({"from": sig_pin, "to": f"{rid}.1", "color": "green"})
            conns.append({"from": f"{rid}.2", "to": "GND", "color": "black"})
            notes.append(
                f"2 bacaklı '{ldr['label']}' ({lid}) için unutulan 10kΩ gerilim bölücü direnç ({rid} -> GND) otomatik eklendi."
            )

    netlist_dict["components"] = comps
    netlist_dict["connections"] = conns
    return netlist_dict, notes


def ensure_code_actuators_in_netlist(
    netlist_dict: Dict[str, Any],
    code: str,
    prompt: str
) -> Tuple[Dict[str, Any], List[str]]:
    """
    Eğer LLM Arduino C++ kodunda veya kullanıcı isteminde Servo / Buzzer / 2. LDR kullanmış
    fakat netlist.components içine eklemeyi unutmuşsa, koddaki gerçek pinlere bağlayarak netlist'i tamamlar.
    """
    notes: List[str] = []
    comps: List[Dict[str, Any]] = list(netlist_dict.get("components") or [])
    conns: List[Dict[str, Any]] = list(netlist_dict.get("connections") or [])
    existing_types = {c.get("type") for c in comps}
    existing_ids = {c.get("id") for c in comps}

    clean_code = re.sub(r"//.*", "", code or "")
    p_low = (prompt or "").lower()

    # 1. Kodda Servo.h / .attach(...) var ama netlist'te wokwi-servo yoksa
    if "wokwi-servo" not in existing_types and ("Servo.h" in clean_code or ".attach(" in clean_code or "servo" in p_low):
        # Koddaki servo pinini bul
        servo_pin = "D9"
        var_map: Dict[str, str] = {}
        for m in re.finditer(r"(?:const\s+int|int|#define)\s+([A-Za-z_]\w*)\s*=?\s*(D?(?:1[0-3]|[0-9]))\b", clean_code):
            var_map[m.group(1)] = m.group(2).upper()
        m_att = re.search(r"\.attach\s*\(\s*([A-Za-z0-9_]+)\s*\)", clean_code)
        if m_att:
            tok = m_att.group(1).strip()
            resolved = var_map.get(tok, tok).upper()
            if re.match(r"^D?(1[0-3]|[0-9])$", resolved):
                servo_pin = resolved if resolved.startswith("D") else f"D{resolved}"

        sid = "servo1" if "servo1" not in existing_ids else f"servo_{len(existing_ids)+1}"
        existing_ids.add(sid)
        comps.append({
            "id": sid,
            "type": "wokwi-servo",
            "props": {},
            "label": "SG90 Servo Motor"
        })
        conns.extend([
            {"from": f"{sid}.V+", "to": "5V", "color": "red"},
            {"from": f"{sid}.GND", "to": "GND", "color": "black"},
            {"from": f"uno.{servo_pin}", "to": f"{sid}.PWM", "color": "orange"},
        ])
        notes.append(f"Arduino kodunda kullanılan SG90 Servo Motor ({sid} -> Pin {servo_pin}) devre şemasına eklendi.")

    # 2. Kullanıcı 2 adet LDR istemiş ("2 tane ldr", "2 adet ldr", "iki ldr", "çift ldr") veya kodda 2 farklı analogRead(A0/A1) var ama netlist'te 1 LDR varsa
    ldr_comps = [c for c in comps if c.get("type") in ("wokwi-photoresistor", "wokwi-photoresistor-sensor")]
    wants_two_ldrs = any(k in p_low for k in ("2 tane ldr", "2 adet ldr", "iki ldr", "iki tane ldr", "çift ldr", "2 ldr"))
    analog_pins_in_code = sorted( [p for p in extract_arduino_code_pins(code) if p.startswith("uno.A")] )
    if (wants_two_ldrs or len(analog_pins_in_code) >= 2) and len(ldr_comps) == 1:
        first_ldr = ldr_comps[0]
        ldr_type = first_ldr.get("type", "wokwi-photoresistor")
        # 1. LDR'nin bağlı olduğu analog pini bul
        used_analog = {
            ep for c in conns for ep in (c.get("from"), c.get("to"))
            if isinstance(ep, str) and ep.startswith("uno.A")
        }
        second_analog = next((p for p in analog_pins_in_code if p not in used_analog), None)
        if not second_analog:
            second_analog = "uno.A1" if "uno.A0" in used_analog else "uno.A0"

        lid2 = "ldr2" if "ldr2" not in existing_ids else f"ldr_{len(existing_ids)+1}"
        existing_ids.add(lid2)
        first_ldr["label"] = "Sol LDR Sensörü"
        comps.append({
            "id": lid2,
            "type": ldr_type,
            "props": {},
            "label": "Sağ LDR Sensörü"
        })
        if ldr_type == "wokwi-photoresistor":
            conns.extend([
                {"from": f"{lid2}.1", "to": "5V", "color": "red"},
                {"from": f"{lid2}.2", "to": second_analog, "color": "blue"},
            ])
        else:
            conns.extend([
                {"from": f"{lid2}.VCC", "to": "5V", "color": "red"},
                {"from": f"{lid2}.GND", "to": "GND", "color": "black"},
                {"from": f"{lid2}.AO", "to": second_analog, "color": "blue"},
            ])
        notes.append(f"İkinci LDR sensörü ({lid2} -> {second_analog.replace('uno.', '')}) devre şemasına eklendi.")

    netlist_dict["components"] = comps
    netlist_dict["connections"] = conns
    return netlist_dict, notes


def validate_one_shot_topology_and_code(
    netlist: CircuitNetlist,
    akis: Optional[Any],
    code: str
) -> Tuple[List[str], LogicVerificationReport]:
    """
    Tek sorgudan (One-Shot) dönen Netlist, Akış Diyagramı ve Arduino Kodunu birbiriyle doğrular:
    - Netlist içinde boşta (bağlantısız) bileşen olup olmadığını
    - Kısa devre (5V-GND veya aynı parçanın iki ucu) olup olmadığını
    - Aktif parçaların (LED/Servo/Buzzer/Sensör) en az bir Arduino sinyal pinine (doğrudan veya direnç üzerinden) bağlı olup olmadığını
    - Akış diyagramının 4 adımının dolu olup olmadığını
    - Arduino C++ kodunun setup/loop içerdiğini ve Netlist'teki uno.* pinleriyle uyuştuğunu
    kontrol eder.
    Kritik hataları `blocking_errors` listesinde döner.
    """
    blocking_errors: List[str] = []
    checks: List[str] = []
    warnings: List[str] = []

    # Harici devre elemanı gerektirmeyen dahili Seri Port veya dahili LED projelerini tanı
    clean_code_lower = (code or "").lower()
    is_internal_only = (
        not netlist.components
        and any(k in clean_code_lower for k in ("serial.", "led_builtin", "random(", "millis(", "setup()"))
    )

    if not netlist.components:
        if is_internal_only:
            checks.append("✓ Harici bileşen gerektirmeyen dahili Arduino Uno (Seri Port / Dahili Mantık) devresi onaylandı.")
        else:
            blocking_errors.append("Devre şemasında (netlist.components) hiçbir bileşen yok.")

    if not netlist.connections and not is_internal_only:
        blocking_errors.append("Devre şemasında (netlist.connections) hiçbir kablo bağlantısı yok.")

    # Her bileşenin kaç pini bağlanmış kontrol et
    comp_pins_used: Dict[str, Set[str]] = {c.id: set() for c in netlist.components}
    for conn in netlist.connections:
        if (conn.from_pin == "5V" and conn.to_pin == "GND") or (conn.from_pin == "GND" and conn.to_pin == "5V"):
            blocking_errors.append("5V ve GND doğrudan kısa devre edilmiş.")
        if "." in conn.from_pin and "." in conn.to_pin:
            p1 = conn.from_pin.split(".", 1)[0]
            p2 = conn.to_pin.split(".", 1)[0]
            if p1 == p2 and p1 != "uno":
                blocking_errors.append(f"'{p1}' bileşeninin iki ucu doğrudan birbirine kısa devre edilmiş.")
        for ep in (conn.from_pin, conn.to_pin):
            if "." in ep:
                cid, cpin = ep.split(".", 1)
                if cid in comp_pins_used:
                    comp_pins_used[cid].add(cpin)

    for c in netlist.components:
        used = comp_pins_used.get(c.id, set())
        if len(used) == 0:
            blocking_errors.append(f"'{c.label}' ({c.id}) devreye eklenmiş ama hiçbir kablosu bağlanmamış.")
        elif len(used) < 2:
            blocking_errors.append(f"'{c.label}' ({c.id}) bileşeninin yalnızca 1 ucu ({', '.join(used)}) bağlanmış, devresi tamamlanmamış.")

    bindings = extract_netlist_pin_bindings(netlist)
    bound_comp_ids = {b.component_id for b in bindings}
    # Dolaylı sürülen parçalar (örn. L293D / L298N / Röle çıkışına bağlı DC Motorlar)
    driver_ids = {
        c.id for c in netlist.components
        if c.type in ("wokwi-l293d", "wokwi-l298n", "wokwi-relay-module") and c.id in bound_comp_ids
    }
    indirectly_driven_ids: Set[str] = set()
    for conn in netlist.connections:
        if "." in conn.from_pin and "." in conn.to_pin:
            p1 = conn.from_pin.split(".", 1)[0]
            p2 = conn.to_pin.split(".", 1)[0]
            if p1 in driver_ids:
                indirectly_driven_ids.add(p2)
            elif p2 in driver_ids:
                indirectly_driven_ids.add(p1)

    non_resistor_comps = [c for c in netlist.components if c.type != "wokwi-resistor"]
    for c in non_resistor_comps:
        if c.id not in bound_comp_ids and c.id not in indirectly_driven_ids:
            blocking_errors.append(
                f"'{c.label}' ({c.id}) hiçbir Arduino Uno sinyal pinine (D2..D13 veya A0..A5) veya motor sürücüye bağlanmamış."
            )

    if not blocking_errors:
        checks.append(
            f"✓ Devredeki tüm parçalar ({', '.join(c.label for c in netlist.components)}) eksiksiz bağlandı."
        )

    flow_complete = False
    if isinstance(akis, AkisDiyagrami):
        flow_complete = len(akis.dugumler) >= 3 and len(akis.baglantilar) >= 1
        if flow_complete:
            checks.append(
                f"✓ Akış diyagramı ({len(akis.dugumler)} adım, {len(akis.baglantilar)} bağlantı) koddan türetilip doğrulandı."
            )
        else:
            blocking_errors.append("Akış diyagramı ('akis_diyagrami') geçerli düğüm/bağlantı içermiyor.")
    elif isinstance(akis, AkisAdimi):
        flow_complete = all([
            bool(akis.gozlemle.strip()),
            bool(akis.karar_ver.strip()),
            bool(akis.evet_sonucu.strip()),
            bool(akis.hayir_sonucu.strip()),
        ])
        if flow_complete:
            checks.append("✓ Akış diyagramı eksiksiz üretildi.")
        else:
            blocking_errors.append("Akış diyagramı ('akis_adimlari') adımlarından biri veya birkaçı boş döndü.")
    else:
        blocking_errors.append("Akış diyagramı eksik.")

    code_candidate = (code or "").strip()
    has_setup = "void setup" in code_candidate
    has_loop = "void loop" in code_candidate
    braces_balanced = code_candidate.count("{") > 0 and (code_candidate.count("{") == code_candidate.count("}"))
    syntax_ok = bool(code_candidate and has_setup and has_loop and braces_balanced)
    if not syntax_ok:
        blocking_errors.append("Üretilen 'arduino_kodu' geçerli bir setup()/loop() C++ yapısı içermiyor.")
    else:
        checks.append("✓ Arduino C++ kodu sözdizimi (setup, loop, parantez dengesi) doğrulandı.")

    pin_mismatches = check_code_netlist_pin_consistency(code_candidate, netlist)
    pins_matched = len(pin_mismatches) == 0
    if pins_matched and bindings:
        checks.append(
            f"✓ Kablolama ve Arduino kodu pinleri %100 uyumlu ({', '.join(f'{b.uno_pin} → {b.component_label}' for b in bindings)})."
        )
    elif pin_mismatches:
        warnings.extend(pin_mismatches)

    report = LogicVerificationReport(
        is_valid=(len(blocking_errors) == 0 and syntax_ok and flow_complete),
        syntax_ok=syntax_ok,
        pins_matched=pins_matched,
        flow_complete=flow_complete,
        auto_repaired=False,
        pin_bindings=bindings,
        checks=checks,
        warnings=warnings
    )
    return blocking_errors, report


def repair_circuit_with_llm(
    current_text: str,
    prompt: str,
    inventory: List[str],
    chosen_model: str,
    provider_used: str,
    ollama_url: str = "http://127.0.0.1:11434",
    api_key: Optional[str] = None,
    max_attempts: int = 2,
    progress_callback: Optional[Callable[[int, int, List[str]], None]] = None
) -> Tuple[Optional[Dict[str, Any]], str, List[str], List[str], bool]:
    """
    Token korumalı AI Devre Onarım Döngüsü:
    Modelin ilk çıktısındaki bileşen, pin, kısa devre ve kod uyumsuzluğu hatalarını inceler.
    Hata varsa modeli en fazla `max_attempts` kez arayarak hataların düzeltilmesini sağlar.
    Token tasarrufu için prompt kırpılır ve num_predict/max_tokens sınırlandırılır.

    Dönüş:
    (norm_data, raw_code, blocking_errors, warnings, was_repaired)
    """
    attempt = 0
    was_repaired = False
    all_warnings: List[str] = []
    latest_text = current_text
    last_blocking_errors: List[str] = []
    last_norm_data: Optional[Dict[str, Any]] = None
    last_raw_code: str = ""

    while True:
        parse_errors: List[str] = []
        parsed = None
        try:
            parsed = safe_parse_llm_json(latest_text)
            if not isinstance(parsed, dict) or not isinstance(parsed.get("netlist"), dict):
                parse_errors.append("AI yanıtında geçerli bir 'netlist' nesnesi bulunamadı.")
        except Exception as e:
            parse_errors.append(f"JSON ayrıştırma hatası: {e}")

        norm_data: Optional[Dict[str, Any]] = None
        raw_code = ""
        blocking_errors: List[str] = []

        if parsed and isinstance(parsed, dict) and not parse_errors:
            raw_code = sanitize_arduino_identifiers(str(parsed.get("arduino_kodu") or "").strip())
            if not raw_code:
                parse_errors.append("AI yanıtında 'arduino_kodu' alanı eksik veya boş.")

            norm_data, norm_warnings = normalize_project_dict(parsed)
            all_warnings.extend(norm_warnings)

            # 1) Kodda/istemde kullanılıp netlist'te unutulan bileşenleri tamamla
            completed_netlist, actuator_notes = ensure_code_actuators_in_netlist(
                netlist_dict=norm_data["netlist"],
                code=raw_code,
                prompt=prompt
            )
            # 2) 2 bacaklı LDR gerilim bölücü dirençleri tamamla
            completed_netlist, topo_notes = auto_complete_electrical_topology(completed_netlist)
            norm_data["netlist"] = completed_netlist
            all_warnings.extend(actuator_notes + topo_notes)

            try:
                netlist_obj = CircuitNetlist(**norm_data["netlist"])
                crit_errors, _ = validate_one_shot_topology_and_code(
                    netlist=netlist_obj,
                    akis=None,
                    code=raw_code
                )
                # Akış diyagramı eksik uyarısını bu aşamada blocking_errors'dan filtrele (akış henüz oluşturulmadı)
                filtered_crit = [e for e in crit_errors if "akış diyagramı" not in e.lower() and "akis_" not in e.lower()]
                blocking_errors.extend(filtered_crit)
            except Exception as e:
                blocking_errors.append(f"Netlist şema hatası: {e}")
        else:
            blocking_errors.extend(parse_errors)

        # Başarılı bir parse varsa en son geçerli durumu koru; hatalı repair cevabı geçerliyi ezmesin
        if norm_data is not None and raw_code:
            last_norm_data = norm_data
            last_raw_code = raw_code
            last_blocking_errors = blocking_errors
        elif last_norm_data is None:
            last_blocking_errors = blocking_errors

        # Eğer hiç bloklayan devre/komponent hatası kalmadıysa onarım tamam!
        if not blocking_errors and norm_data is not None and raw_code:
            return norm_data, raw_code, [], all_warnings, was_repaired

        # Eğer hata varsa ve henüz onarım hakkımız varsa (Token Korumalı Sınır):
        if attempt < max_attempts:
            attempt += 1
            print(f"[Circuit Repair AI] Bağlantı/bileşen hataları tespit edildi ({len(blocking_errors)} adet), onarım denemesi {attempt}/{max_attempts}: {blocking_errors}")
            if progress_callback:
                progress_callback(attempt, max_attempts, blocking_errors)

            repair_prompt = build_token_safe_circuit_repair_prompt(
                errors=blocking_errors,
                current_output=latest_text,
                user_prompt=prompt,
                inventory=inventory
            )

            repaired_text: Optional[str] = None
            if provider_used == "ollama":
                clean_model = chosen_model.replace("ollama/", "")
                payload = {
                    "model": clean_model,
                    "system": ONE_SHOT_SYSTEM_PROMPT,
                    "prompt": repair_prompt,
                    "stream": False,
                    "options": {
                        "temperature": 0.1,
                        "num_predict": 2500
                    }
                }
                if not any(k in clean_model.lower() for k in ("deepseek-r1", "qwq", "r1")):
                    payload["format"] = "json"
                try:
                    res = httpx.post(f"{ollama_url}/api/generate", json=payload, timeout=90.0)
                    if res.status_code == 200:
                        repaired_text = res.json().get("response", "")
                except Exception as e:
                    print(f"[Circuit Repair AI] Ollama repair çağrısı hatası: {e}")
            else:
                try:
                    from litellm import completion
                    resp = completion(
                        model=chosen_model,
                        messages=[
                            {"role": "system", "content": ONE_SHOT_SYSTEM_PROMPT},
                            {"role": "user", "content": repair_prompt}
                        ],
                        response_format={"type": "json_object"},
                        api_key=api_key,
                        temperature=0.1,
                        max_tokens=2500
                    )
                    repaired_text = resp.choices[0].message.content
                except Exception as e:
                    print(f"[Circuit Repair AI] Cloud AI repair çağrısı hatası: {e}")

            if repaired_text and repaired_text.strip():
                latest_text = repaired_text
                was_repaired = True
                continue
            else:
                # LLM'den yanıt alınamadıysa daha fazla token harcamadan dur
                break
        else:
            # Token koruma sınırı doldu
            print(f"[Circuit Repair AI] Token koruma sınırı doldu ({max_attempts} deneme yapıldı). Sonuçlar finalize ediliyor.")
            break

    return last_norm_data, last_raw_code, last_blocking_errors, all_warnings, was_repaired


def generate_full_project_one_shot(
    prompt: str,
    inventory: List[str],
    model: str = "default",
    ollama_url: str = "http://127.0.0.1:11434",
    api_key: Optional[str] = None
) -> ProjeTasarimi:
    """
    Tek Sorgu (One-Shot) AI Çağrısı:
    Hem devre kablolamasını (netlist), hem akış diyagramını (akis_adimlari), hem de Arduino C++ kodunu (arduino_kodu)
    tek bir LLM çağrısında alır, birbiriyle doğrular ve döner.
    Yanıt alınamazsa veya doğrulama başarısız olursa HİÇBİR ŞEY SENTETİK ÜRETMEZ, doğrudan hata fırlatır.
    """
    # 0. Prompt Güvenlik ve Proje Uygunluğu Denetimi
    val = validate_project_prompt(prompt)
    if not val.is_valid:
        raise RuntimeError(val.user_message)

    models_info = get_all_available_models(ollama_url)
    chosen_model = model if model != "default" and model is not None else models_info["default_model"]

    user_prompt = f"""KULLANICI PROJE İSTEĞİ: "{prompt}"
Yukarıdaki isteğe göre SADECE istenen parçaları içeren `netlist` (components + connections) ve aynı pinleri kullanan `arduino_kodu` alanlarını içeren tek bir geçerli JSON nesnesi üret. Sadece JSON döndür."""

    raw_text: Optional[str] = None
    provider_used = "ollama" if (chosen_model.startswith("ollama/") or chosen_model == "local") else "litellm"
    t0 = time.time()
    error_note: Optional[str] = None

    if provider_used == "ollama":
        if models_info["ollama_active"]:
            local_ids = [m["id"] for m in models_info.get("local_models", [])]
            if chosen_model not in local_ids and models_info.get("default_model"):
                chosen_model = models_info["default_model"]
            clean_model = chosen_model.replace("ollama/", "")
            is_reasoning_model = any(k in clean_model.lower() for k in ("deepseek-r1", "qwq", "r1"))
            ollama_payload: Dict[str, Any] = {
                "model": clean_model,
                "system": ONE_SHOT_SYSTEM_PROMPT,
                "prompt": user_prompt,
                "stream": False,
                "options": {
                    "temperature": 0.1,
                    "num_predict": 2500 if is_reasoning_model else 1200
                }
            }
            # Reasoning modelleri (<think>...</think>) format="json" zorlandığında boş "{}" döndürebildiği için
            # yalnızca standart modellerde format="json" kullanıyoruz; clean_llm_json_response <think> bloğunu temizler.
            if not is_reasoning_model:
                ollama_payload["format"] = "json"

            try:
                res = httpx.post(
                    f"{ollama_url}/api/generate",
                    json=ollama_payload,
                    timeout=180.0
                )
                if res.status_code == 200:
                    raw_text = res.json().get("response", "")
                else:
                    error_note = f"Ollama HTTP {res.status_code}: {res.text[:200]}"
            except Exception as e:
                error_note = f"Ollama bağlantı/zaman aşımı hatası: {e}"
                print(f"[One-Shot AI] {error_note}")
        else:
            error_note = f"Yerel Ollama servisi ({ollama_url}) çalışmıyor veya ulaşılamıyor."
    else:
        if not api_key:
            if "gemini" in chosen_model:
                api_key = os.getenv("GEMINI_API_KEY")
            elif "gpt" in chosen_model:
                api_key = os.getenv("OPENAI_API_KEY")
            elif "claude" in chosen_model:
                api_key = os.getenv("ANTHROPIC_API_KEY")
        if api_key:
            try:
                from litellm import completion
                response = completion(
                    model=chosen_model,
                    messages=[
                        {"role": "system", "content": ONE_SHOT_SYSTEM_PROMPT},
                        {"role": "user", "content": user_prompt}
                    ],
                    response_format={"type": "json_object"},
                    api_key=api_key,
                    temperature=0.2
                )
                raw_text = response.choices[0].message.content
            except Exception as e:
                error_note = f"Bulut AI ({chosen_model}) hatası: {e}"
                print(f"[One-Shot AI] {error_note}")
        else:
            error_note = f"Seçilen bulut modeli ('{chosen_model}') için API anahtarı girilmemiş."

    duration_ms = int((time.time() - t0) * 1000)

    if not raw_text or not raw_text.strip():
        msg = error_note or f"Yapay zeka modelinden ('{chosen_model}') yanıt alınamadı."
        record_ai_log(
            stage="Tek Sorgu (One-Shot): Devre + Akış + Kod",
            model=chosen_model,
            provider=provider_used,
            duration_ms=duration_ms,
            status="ERROR",
            user_goal=prompt,
            system_prompt=ONE_SHOT_SYSTEM_PROMPT,
            user_prompt=user_prompt,
            raw_response=f"[HATA: {msg}]",
            processed_output=None,
            notes=[msg]
        )
        raise RuntimeError(msg)

    try:
        # Token korumalı AI Devre Onarım Döngüsü (Bağlantı/komponent hatalarında modele gidip düzelttirme):
        norm_data, raw_code, circuit_errors, circuit_warnings, was_repaired = repair_circuit_with_llm(
            current_text=raw_text,
            prompt=prompt,
            inventory=inventory,
            chosen_model=chosen_model,
            provider_used=provider_used,
            ollama_url=ollama_url,
            api_key=api_key,
            max_attempts=2
        )
        if not norm_data or not raw_code:
            raise ValueError(" | ".join(circuit_errors) or "AI yanıtı geçerli devre ve koda dönüştürülemedi.")

        netlist_obj = CircuitNetlist(**norm_data["netlist"])

        # Kesinleşmiş netlist ve son Arduino kodundan odaklanmış çağrıyla AkisDiyagrami üret
        flow_obj, flow_warnings, flow_status = generate_flow_from_code(
            prompt=prompt,
            netlist=netlist_obj,
            arduino_kodu=raw_code,
            chosen_model=chosen_model,
            provider_used=provider_used,
            ollama_url=ollama_url,
            api_key=api_key,
            clean_json_fn=clean_llm_json_response
        )

        blocking_errors, report = validate_one_shot_topology_and_code(
            netlist=netlist_obj,
            akis=flow_obj,
            code=raw_code
        )
        if was_repaired or flow_status == "REPAIRED":
            report.auto_repaired = True
        if flow_warnings:
            report.warnings.extend(flow_warnings)
        if blocking_errors:
            raise ValueError(" | ".join(blocking_errors))

        steps = build_baglanti_adimlari_from_netlist(netlist_obj)
        norm_warnings = circuit_warnings

        # Çantada (Inventory) olmayan parçalar kullanılmışsa devre kurulumunu engelleme, uyarı olarak bildir
        bag_warnings = []
        if inventory:
            from app.llm.catalog import resolve_component_type
            inv_types = {resolve_component_type(item) for item in inventory}
            missing_bag_items = []
            for comp in netlist_obj.components:
                c_type = resolve_component_type(comp.type)
                # Standart parçaları (direnç, led) çantada olmasa bile uyarı vermeden kabul et
                if c_type not in inv_types and c_type not in ("wokwi-resistor", "wokwi-led", "arduino-uno", "breadboard"):
                    label, icon = get_component_meta(c_type)
                    if f"{icon} {label}" not in missing_bag_items:
                        missing_bag_items.append(f"{icon} {label}")
            if missing_bag_items:
                bag_warnings.append(
                    f"🎒 Çanta Hatırlatması: Bu projede çantanda işaretli olmayan ({', '.join(missing_bag_items)}) kullanıldı. Devreyi gerçek hayatta kurmak için bu parçaları temin etmen gerekebilir."
                )

        project = ProjeTasarimi(
            proje_adi=(prompt.strip()[:42] or "Arduino Projem"),
            karsilama_mesaji="Devren, akış şeman ve Arduino kodun hazır!",
            gerekli_parcalar=norm_data.get("gerekli_parcalar") or ["ARDUINO_UNO", "BREADBOARD"],
            netlist=netlist_obj,
            baglanti_adimlari=steps,
            akis_adimlari=None,
            akis_diyagrami=flow_obj,
            arduino_kodu=raw_code,
            guvenlik_notu="Parçaları breadboard pinlerine dikkatlice yerleştir.",
            uyarilar=circuit_warnings + list(report.warnings) + bag_warnings,
            verification=report
        )

        record_ai_log(
            stage="Tek Sorgu (One-Shot): Devre + Akış + Kod",
            model=chosen_model,
            provider=provider_used,
            duration_ms=duration_ms,
            status="SUCCESS" if report.is_valid else "VALIDATION_WARNING",
            user_goal=prompt,
            system_prompt=ONE_SHOT_SYSTEM_PROMPT,
            user_prompt=user_prompt,
            raw_response=raw_text,
            processed_output=project.model_dump(by_alias=True),
            notes=list(report.checks) + circuit_warnings + list(report.warnings)
        )
        return project
    except Exception as e:
        err_msg = f"Yapay zeka yanıtı doğrulanamadı: {e}"
        record_ai_log(
            stage="Tek Sorgu (One-Shot): Devre + Akış + Kod",
            model=chosen_model,
            provider=provider_used,
            duration_ms=duration_ms,
            status="ERROR",
            user_goal=prompt,
            system_prompt=ONE_SHOT_SYSTEM_PROMPT,
            user_prompt=user_prompt,
            raw_response=raw_text,
            processed_output=None,
            notes=[err_msg]
        )
        raise RuntimeError(err_msg)


def get_component_meta(comp_identifier: str, comp_type: str = "") -> Tuple[str, str]:
    """Bileşen ID veya tipine göre çocuk dostu Türkçe etiket ve emoji ikonu döner."""
    cid = comp_identifier.upper()
    ctype = comp_type.lower()

    if ctype in ("wokwi-photoresistor", "ldr_discrete", "discrete-ldr"):
        return ("2 Bacaklı LDR (Işık Sensörü)", "☀️")
    if ctype in ("wokwi-photoresistor-sensor", "ldr_module", "ldr-module"):
        return ("LDR Işık Sensör Modülü", "🎛️")
    if ctype in ("wokwi-servo", "servo_sg90", "sg90"):
        return ("SG90 Servo Motor", "🦾")
    if ctype in ("wokwi-hc-sr04", "hcsr04", "ultrasonic"):
        return ("HC-SR04 Mesafe Sensörü", "🦇")
    if ctype in ("wokwi-led", "led"):
        return ("LED Işık Lambası", "💡")
    if ctype in ("wokwi-resistor", "resistor"):
        return ("Direnç", "🟤")
    if ctype in ("wokwi-hc-05", "wokwi-hc05", "hc-05", "hc05"):
        return ("HC-05 Bluetooth Modülü", "📶")
    if ctype in ("wokwi-hc-06", "wokwi-hc06", "hc-06", "hc06"):
        return ("HC-06 Bluetooth Modülü", "📶")
    if ctype in ("wokwi-l293d", "l293d"):
        return ("L293D Motor Sürücü", "🚗")
    if ctype in ("wokwi-l298n", "l298n"):
        return ("L298N Motor Sürücü", "🏎️")
    if ctype in ("wokwi-dc-motor", "wokwi-dcmotor", "dc-motor", "dcmotor"):
        return ("5V DC Motor", "🌀")
    if ctype in ("wokwi-buzzer", "buzzer"):
        return ("Buzzer (Hoparlör)", "🔊")
    if ctype in ("wokwi-pushbutton", "pushbutton", "button"):
        return ("Push Buton (Düğme)", "🔘")
    if ctype in ("wokwi-potentiometer", "potentiometer"):
        return ("10kΩ Potansiyometre", "🎚️")
    if ctype in ("wokwi-relay-module", "relay"):
        return ("5V Röle Modülü", "⚡")
    if ctype in ("wokwi-pir-motion-sensor", "pir"):
        return ("PIR Hareket Sensörü", "🚶")
    if ctype in ("wokwi-dht22", "dht22", "dht11"):
        return ("DHT22 Sıcaklık & Nem", "🌡️")
    if ctype in ("wokwi-soil-moisture-sensor", "soil"):
        return ("Toprak Nem Sensörü", "🌱")
    if ctype in ("wokwi-rain-sensor", "rain"):
        return ("Yağmur Sensörü", "🌧️")
    if ctype in ("wokwi-water-sensor", "water"):
        return ("Su Seviye Sensörü", "💧")

    INVENTORY_DICT = {
        "ARDUINO_UNO": ("Arduino Uno R3 (Beyin)", "🟦"),
        "ARDUINO_NANO": ("Arduino Nano", "🎛️"),
        "ARDUINO_MEGA": ("Arduino Mega", "🏢"),
        "BREADBOARD": ("Breadboard (Devre Tahtası)", "🍞"),
        "LED_RED": ("Kırmızı LED Lambası", "🔴"),
        "LED_GREEN": ("Yeşil LED Lambası", "🟢"),
        "LED_BLUE": ("Mavi LED Lambası", "🔵"),
        "LED_YELLOW": ("Sarı LED Lambası", "🟡"),
        "LED_RGB": ("RGB Çok Renkli LED", "🌈"),
        "RESISTOR_220": ("220Ω Koruma Direnci", "🟤"),
        "RESISTOR_1K": ("1kΩ Direnç", "🟤"),
        "RESISTOR_10K": ("10kΩ Direnç", "🟤"),
        "POTENTIOMETER": ("10kΩ Potansiyometre", "🎚️"),
        "PUSH_BUTTON": ("Push Buton (Düğme)", "🔘"),
        "LDR_DISCRETE": ("2 Bacaklı LDR (Işık Sensörü)", "☀️"),
        "LDR_MODULE": ("4 Pin LDR Sensör Modülü", "🎛️"),
        "LDR_SENSOR": ("LDR Işık Sensörü", "☀️"),
        "HCSR04": ("HC-SR04 Mesafe Sensörü", "🦇"),
        "PIR_SENSOR": ("PIR Hareket Sensörü", "🚶"),
        "DHT11": ("DHT22 Sıcaklık & Nem", "🌡️"),
        "DHT22": ("DHT22 Sıcaklık & Nem", "🌡️"),
        "JOYSTICK_MODULE": ("Analog Joystick", "🕹️"),
        "BUZZER": ("Piezo Buzzer (Hoparlör)", "🔊"),
        "ACTIVE_BUZZER": ("Aktif Buzzer", "📢"),
        "SERVO_SG90": ("SG90 Servo Motor", "🦾"),
        "DC_MOTOR_5V": ("5V DC Motor", "🌀"),
        "DC_MOTOR": ("5V DC Motor", "🌀"),
        "BLUETOOTH_HC05": ("HC-05 Bluetooth Modülü", "📶"),
        "BLUETOOTH_HC06": ("HC-06 Bluetooth Modülü", "📶"),
        "MOTOR_DRIVER_L293D": ("L293D Motor Sürücü", "🚗"),
        "MOTOR_DRIVER_L298N": ("L298N Motor Sürücü", "🏎️"),
        "RELAY_5V": ("5V Röle Modülü", "⚡"),
        "RELAY_MODULE": ("5V Röle Modülü", "⚡"),
        "SOIL_MOISTURE": ("Toprak Nem Sensörü", "🌱"),
        "RAIN_SENSOR": ("Yağmur Sensörü", "🌧️"),
        "WATER_SENSOR": ("Su Seviye Sensörü", "💧"),
        "SOUND_SENSOR": ("Ses Sensörü", "🎤"),
        "MQ2_GAS": ("MQ-2 Gaz Sensörü", "💨"),
        "LCD_16X2_I2C": ("16x2 LCD Ekran", "📟"),
        "OLED_096_I2C": ("0.96 OLED Ekran", "📺")
    }

    if cid in INVENTORY_DICT:
        return INVENTORY_DICT[cid]

    clean_label = comp_identifier.replace("_", " ").title()
    return (clean_label, "🧩")


def generate_full_project_stream(
    prompt: str,
    inventory: List[str],
    model: str = "default",
    ollama_url: str = "http://127.0.0.1:11434",
    api_key: Optional[str] = None
) -> Generator[str, None, None]:
    """
    Streaming (Server-Sent Events) AI Çağrısı:
    Yapay zekanın ürettiği bileşenleri, kabloları, akış adımlarını ve C++ kodunu
    canlı olarak istemciye (frontend) akar.
    """
    def format_sse(data: Dict[str, Any]) -> str:
        return f"data: {json.dumps(data, ensure_ascii=False)}\n\n"

    # 0. Prompt Güvenlik ve Proje Uygunluğu Denetimi (Ön Filtreleme)
    val = validate_project_prompt(prompt)
    if not val.is_valid:
        yield format_sse({
            "type": "error",
            "error_type": val.filter_type,
            "message": val.user_message,
            "suggestions": val.suggested_prompts
        })
        return

    models_info = get_all_available_models(ollama_url)
    chosen_model = model if model != "default" and model is not None else models_info["default_model"]

    # 0.5. Token Tasarrufu & Hızlı Yanıt: Önbellek (Cache) Kontrolü
    cached = get_cached_project(prompt, inventory, chosen_model)
    if cached:
        yield format_sse({
            "type": "stage",
            "stageIndex": 0,
            "title": "1. Proje Fikrin Analiz Ediliyor",
            "subtitle": "Önbellekten anında yüklendi ⚡",
            "progressPercent": 50
        })
        yield format_sse({
            "type": "stage",
            "stageIndex": 1,
            "title": "2. Devre ve Kod Hazır",
            "subtitle": "Tüm bağlantılar ve kod hazır!",
            "progressPercent": 100
        })
        yield format_sse({
            "type": "complete",
            "project": cached,
            "progressPercent": 100
        })
        record_ai_log(
            stage="Tek Sorgu (One-Shot): Devre + Akış + Kod (Stream)",
            model=chosen_model,
            provider="cache",
            duration_ms=5,
            status="SUCCESS",
            user_goal=prompt,
            system_prompt="(Cache Hit - 0 Tokens)",
            user_prompt=f"KULLANICI PROJE İSTEĞİ: \"{prompt}\"",
            raw_response="[CACHED RESULT]",
            processed_output=cached,
            notes=["Önbellekten (Cache) 0 token ve 0ms ile yüklendi ⚡"],
            prompt_tokens=0,
            completion_tokens=0,
            total_tokens=0
        )
        return

    # Dinamik sistem promptu: yalnızca gereken parçaların pinlerini içerir (%70 token tasarrufu)
    dynamic_system_prompt = build_one_shot_system_prompt(prompt, inventory)

    # Akış diyagramı AI'dan istenmez; aşağıda kesinleşen koddan ayrı bir adımda üretilir
    user_prompt = f"""KULLANICI PROJE İSTEĞİ: "{prompt}"
Yukarıdaki isteğe göre SADECE istenen parçaları içeren `netlist` (components + connections) ve aynı pinleri kullanan `arduino_kodu` alanlarını içeren tek bir geçerli JSON nesnesi üret. Sadece JSON döndür."""

    yield format_sse({
        "type": "stage",
        "stageIndex": 0,
        "title": "1. Proje Fikrin Analiz Ediliyor",
        "subtitle": f"AI Mucit ({chosen_model}) devreni kurgulamaya başladı...",
        "progressPercent": 15
    })

    provider_used = "ollama" if (chosen_model.startswith("ollama/") or chosen_model == "local") else "litellm"
    t0 = time.time()
    accumulated_text = ""
    error_note: Optional[str] = None

    project_name_found = False
    seen_component_keys: Set[str] = set()
    discovered_components: List[Dict[str, Any]] = []
    seen_wire_count = 0
    current_stage = 0

    def parse_incremental_stream(text: str) -> List[Dict[str, Any]]:
        nonlocal project_name_found, seen_wire_count, current_stage
        events = []

        # 1. Proje Adı Tespiti
        if not project_name_found:
            m_name = re.search(r'"proje_adi"\s*:\s*"([^"]+)"', text)
            if m_name:
                p_name = m_name.group(1).strip()
                project_name_found = True
                events.append({
                    "type": "project_name",
                    "name": p_name
                })

        # 2. Gerekli Parçalar Dizisi Tespiti
        m_parts_block = re.search(r'"gerekli_parcalar"\s*:\s*\[(.*?)\]', text, re.DOTALL)
        if m_parts_block:
            found_parts = re.findall(r'"([A-Za-z0-9_]+)"', m_parts_block.group(1))
            for p in found_parts:
                k = f"inv_{p.upper()}"
                if k not in seen_component_keys:
                    seen_component_keys.add(k)
                    label, icon = get_component_meta(p)
                    discovered_components.append({
                        "id": p,
                        "label": label,
                        "icon": icon,
                        "kind": "inventory"
                    })
                    events.append({
                        "type": "component_discovered",
                        "id": p,
                        "label": label,
                        "icon": icon,
                        "totalCount": len(discovered_components)
                    })

        # 3. Components Nesneleri Tespiti
        found_comps = re.findall(r'\{\s*"id"\s*:\s*"([^"]+)"\s*,\s*"type"\s*:\s*"([^"]+)"', text)
        for cid, ctype in found_comps:
            k = f"comp_{cid.lower()}"
            if k not in seen_component_keys:
                seen_component_keys.add(k)
                label, icon = get_component_meta(cid, ctype)
                discovered_components.append({
                    "id": cid,
                    "label": label,
                    "icon": icon,
                    "componentType": ctype,
                    "kind": "circuit"
                })
                events.append({
                    "type": "component_discovered",
                    "id": cid,
                    "label": label,
                    "icon": icon,
                    "componentType": ctype,
                    "totalCount": len(discovered_components)
                })

        # Aşama 1: Parçalar tespit edilmeye başlandıysa
        if discovered_components and current_stage < 1:
            current_stage = 1
            events.append({
                "type": "stage",
                "stageIndex": 1,
                "title": "2. Elektronik Parçalar Seçiliyor",
                "subtitle": f"{len(discovered_components)} parça tespit edildi ({discovered_components[-1]['label']})...",
                "progressPercent": 40
            })

        # 4. Connections (Kablo Bağlantıları) Tespiti
        found_wires = re.findall(r'\{\s*"from"\s*:\s*"([^"]+)"\s*,\s*"to"\s*:\s*"([^"]+)"', text)
        if len(found_wires) > seen_wire_count:
            seen_wire_count = len(found_wires)
            last_from, last_to = found_wires[-1]
            if current_stage < 2:
                current_stage = 2
                events.append({
                    "type": "stage",
                    "stageIndex": 2,
                    "title": "3. Breadboard ve Arduino Pinleri Bağlanıyor",
                    "subtitle": f"{seen_wire_count} kablo bağlandı ({last_from} ➔ {last_to})...",
                    "progressPercent": 65
                })
            else:
                events.append({
                    "type": "wires_progress",
                    "count": seen_wire_count,
                    "latestWire": f"{last_from} ➔ {last_to}"
                })

        # 5. Arduino C++ Kodu Tespiti
        # (Akış diyagramı 5. aşamada, akış bittikten sonra koddan çıkarılır.)
        if '"arduino_kodu"' in text and current_stage < 3:
            current_stage = 3
            code_lines = max(5, text.count('\\n'))
            events.append({
                "type": "stage",
                "stageIndex": 3,
                "title": "4. Arduino C++ Kodu Yazılıyor",
                "subtitle": f"Arduino C++ kodu yazılıyor (~{code_lines} satır)...",
                "progressPercent": 80
            })
            events.append({
                "type": "code_progress",
                "lines": code_lines
            })

        return events

    try:
        if provider_used == "ollama":
            if not models_info["ollama_active"]:
                raise RuntimeError(f"Yerel Ollama servisi ({ollama_url}) çalışmıyor veya ulaşılamıyor.")

            local_ids = [m["id"] for m in models_info.get("local_models", [])]
            if chosen_model not in local_ids and models_info.get("default_model"):
                chosen_model = models_info["default_model"]
            clean_model = chosen_model.replace("ollama/", "")
            is_reasoning_model = any(k in clean_model.lower() for k in ("deepseek-r1", "qwq", "r1"))

            ollama_payload: Dict[str, Any] = {
                "model": clean_model,
                "system": dynamic_system_prompt,
                "prompt": user_prompt,
                "stream": True,
                "options": {
                    "temperature": 0.1,
                    "num_predict": 2500 if is_reasoning_model else 1500
                }
            }
            if not is_reasoning_model:
                ollama_payload["format"] = "json"

            with httpx.Client(timeout=180.0) as client:
                with client.stream("POST", f"{ollama_url}/api/generate", json=ollama_payload) as response:
                    if response.status_code != 200:
                        raise RuntimeError(f"Ollama HTTP {response.status_code}")
                    for line in response.iter_lines():
                        if not line:
                            continue
                        try:
                            item = json.loads(line)
                            chunk = item.get("response", "")
                            if chunk:
                                accumulated_text += chunk
                                for ev in parse_incremental_stream(accumulated_text):
                                    yield format_sse(ev)
                        except json.JSONDecodeError:
                            continue
        else:
            if not api_key:
                if "gemini" in chosen_model:
                    api_key = os.getenv("GEMINI_API_KEY")
                elif "gpt" in chosen_model:
                    api_key = os.getenv("OPENAI_API_KEY")
                elif "claude" in chosen_model:
                    api_key = os.getenv("ANTHROPIC_API_KEY")

            if not api_key:
                raise RuntimeError(f"Seçilen bulut modeli ('{chosen_model}') için API anahtarı girilmemiş.")

            from litellm import completion
            stream_resp = completion(
                model=chosen_model,
                messages=[
                    {"role": "system", "content": dynamic_system_prompt},
                    {"role": "user", "content": user_prompt}
                ],
                stream=True,
                api_key=api_key,
                temperature=0.2,
                max_tokens=2500
            )
            for chunk_obj in stream_resp:
                if chunk_obj.choices and chunk_obj.choices[0].delta:
                    delta = chunk_obj.choices[0].delta.content or ""
                    if delta:
                        accumulated_text += delta
                        for ev in parse_incremental_stream(accumulated_text):
                            yield format_sse(ev)

        duration_ms = int((time.time() - t0) * 1000)

        if not accumulated_text or not accumulated_text.strip():
            raise RuntimeError(f"Yapay zeka modelinden ('{chosen_model}') yanıt alınamadı.")

        yield format_sse({
            "type": "validating",
            "message": "Kablolama, akış adımları ve Arduino C++ kodu doğrulanıyor...",
            "progressPercent": 94
        })

        # Token korumalı AI Devre Onarım Döngüsü (Bağlantı/komponent hatalarında modele gidip düzelttirme):
        repair_events = []
        def on_repair_progress(attempt_idx: int, max_att: int, errs: List[str]):
            repair_events.append({
                "type": "stage",
                "stageIndex": 2,
                "title": f"Devre Bağlantıları Onarılıyor ({attempt_idx}/{max_att})",
                "subtitle": f"Bileşen bağlantılarındaki {len(errs)} tutarsızlık yapay zekaya iletildi, düzeltiliyor...",
                "progressPercent": 65 + (attempt_idx * 10)
            })

        norm_data, raw_code, circuit_errors, circuit_warnings, was_repaired = repair_circuit_with_llm(
            current_text=accumulated_text,
            prompt=prompt,
            inventory=inventory,
            chosen_model=chosen_model,
            provider_used=provider_used,
            ollama_url=ollama_url,
            api_key=api_key,
            max_attempts=2,
            progress_callback=on_repair_progress
        )
        for ev in repair_events:
            yield format_sse(ev)

        if not norm_data or not raw_code:
            raise ValueError(" | ".join(circuit_errors) or "AI yanıtı geçerli devre ve koda dönüştürülemedi.")

        netlist_obj = CircuitNetlist(**norm_data["netlist"])

        # Kesinleşmiş netlist ve son Arduino kodundan ayrı, odaklanmış çağrıyla AkisDiyagrami üret
        yield format_sse({
            "type": "stage",
            "stageIndex": 4,
            "title": "5. Sebep-Sonuç Akış Diyagramı Çiziliyor",
            "subtitle": "Arduino kodundan adım adım akış diyagramı çıkarılıyor...",
            "progressPercent": 92
        })
        flow_obj, flow_warnings, flow_status = generate_flow_from_code(
            prompt=prompt,
            netlist=netlist_obj,
            arduino_kodu=raw_code,
            chosen_model=chosen_model,
            provider_used=provider_used,
            ollama_url=ollama_url,
            api_key=api_key,
            clean_json_fn=clean_llm_json_response
        )
        circuit_warnings.extend(flow_warnings)

        blocking_errors, report = validate_one_shot_topology_and_code(
            netlist=netlist_obj,
            akis=flow_obj,
            code=raw_code
        )
        if was_repaired or flow_status == "REPAIRED":
            report.auto_repaired = True
        if blocking_errors:
            raise ValueError(" | ".join(blocking_errors))

        steps = build_baglanti_adimlari_from_netlist(netlist_obj)
        norm_warnings = circuit_warnings

        # Çantada (Inventory) olmayan parçalar kullanılmışsa devre kurulumunu engelleme, uyarı olarak bildir
        bag_warnings = []
        if inventory:
            from app.llm.catalog import resolve_component_type
            inv_types = {resolve_component_type(item) for item in inventory}
            missing_bag_items = []
            for comp in netlist_obj.components:
                c_type = resolve_component_type(comp.type)
                # Standart parçaları (direnç, led) çantada olmasa bile uyarı vermeden kabul et
                if c_type not in inv_types and c_type not in ("wokwi-resistor", "wokwi-led", "arduino-uno", "breadboard"):
                    label, icon = get_component_meta(c_type)
                    if f"{icon} {label}" not in missing_bag_items:
                        missing_bag_items.append(f"{icon} {label}")
            if missing_bag_items:
                bag_warnings.append(
                    f"🎒 Çanta Hatırlatması: Bu projede çantanda işaretli olmayan ({', '.join(missing_bag_items)}) kullanıldı. Devreyi gerçek hayatta kurmak için bu parçaları temin etmen gerekebilir."
                )

        project = ProjeTasarimi(
            proje_adi=(prompt.strip()[:42] or "Arduino Projem"),
            karsilama_mesaji="Devren, akış şeman ve Arduino kodun hazır!",
            gerekli_parcalar=norm_data.get("gerekli_parcalar") or ["ARDUINO_UNO", "BREADBOARD"],
            netlist=netlist_obj,
            baglanti_adimlari=steps,
            akis_adimlari=None,
            akis_diyagrami=flow_obj,
            arduino_kodu=raw_code,
            guvenlik_notu="Parçaları breadboard pinlerine dikkatlice yerleştir.",
            uyarilar=circuit_warnings + list(report.warnings) + bag_warnings,
            verification=report
        )

        # Token sayılarını hesapla ve önbelleğe al
        prompt_tokens_est = max(1, len(dynamic_system_prompt + user_prompt) // 4)
        comp_tokens_est = max(1, len(accumulated_text) // 4)
        total_tokens_est = prompt_tokens_est + comp_tokens_est

        set_cached_project(prompt, inventory, chosen_model, project.model_dump(by_alias=True))

        record_ai_log(
            stage="Tek Sorgu (One-Shot): Devre + Akış + Kod (Stream)",
            model=chosen_model,
            provider=provider_used,
            duration_ms=duration_ms,
            status="SUCCESS" if report.is_valid else "VALIDATION_WARNING",
            user_goal=prompt,
            system_prompt=dynamic_system_prompt,
            user_prompt=user_prompt,
            raw_response=accumulated_text,
            processed_output=project.model_dump(by_alias=True),
            notes=list(report.checks) + circuit_warnings + list(report.warnings),
            prompt_tokens=prompt_tokens_est,
            completion_tokens=comp_tokens_est,
            total_tokens=total_tokens_est
        )

        yield format_sse({
            "type": "complete",
            "project": project.model_dump(by_alias=True),
            "progressPercent": 100
        })

    except Exception as e:
        duration_ms = int((time.time() - t0) * 1000)
        err_msg = f"Yapay zeka yanıtı doğrulanamadı: {e}"
        prompt_tokens_est = max(1, len(dynamic_system_prompt + user_prompt) // 4)
        comp_tokens_est = max(1, len(accumulated_text) // 4) if accumulated_text else 0
        record_ai_log(
            stage="Tek Sorgu (One-Shot): Devre + Akış + Kod (Stream)",
            model=chosen_model,
            provider=provider_used,
            duration_ms=duration_ms,
            status="ERROR",
            user_goal=prompt,
            system_prompt=dynamic_system_prompt,
            user_prompt=user_prompt,
            raw_response=accumulated_text,
            processed_output=None,
            notes=[err_msg],
            prompt_tokens=prompt_tokens_est,
            completion_tokens=comp_tokens_est,
            total_tokens=prompt_tokens_est + comp_tokens_est
        )
        yield format_sse({
            "type": "error",
            "message": err_msg
        })



def generate_revised_project_stream(
    current_project: Dict[str, Any],
    revision_prompt: str,
    inventory: List[str],
    model: str = "default",
    ollama_url: str = "http://127.0.0.1:11434",
    api_key: Optional[str] = None
) -> Generator[str, None, None]:
    """
    Streaming (SSE) Proje Revizyon AI Çağrısı:
    Mevcut devreyi ve kodu kullanıcının revizyon isteğine göre günceller ve
    canlı olarak istemciye (frontend) akar.
    """
    def format_sse(data: Dict[str, Any]) -> str:
        return f"data: {json.dumps(data, ensure_ascii=False)}\n\n"

    # 0. Revizyon Prompt Güvenlik ve Uygunluk Denetimi
    val = validate_project_prompt(revision_prompt)
    if not val.is_valid:
        yield format_sse({
            "type": "error",
            "error_type": val.filter_type,
            "message": val.user_message,
            "suggestions": val.suggested_prompts
        })
        return

    models_info = get_all_available_models(ollama_url)
    chosen_model = model if model != "default" and model is not None else models_info["default_model"]

    user_prompt = f"""MEVCUT PROJE BİLGİSİ:
- Proje Adı: {current_project.get('proje_adi', 'Arduino Projesi')}
- Mevcut Netlist (Bileşenler ve Bağlantılar):
{json.dumps(current_project.get('netlist', {}), ensure_ascii=False)}
- Mevcut Akış Adımları:
{json.dumps(current_project.get('akis_adimlari', {}), ensure_ascii=False)}
- Mevcut Arduino C++ Kodu:
{current_project.get('arduino_kodu', '')}

KULLANICININ İSTEDİĞİ DEĞİŞİKLİK / REVİZYON:
"{revision_prompt}"

KULLANILABİLİR ELEKTRONİK ENVANTERİ:
{json.dumps(inventory, ensure_ascii=False)}

Yukarıdaki mevcut projeyi, kullanıcının revizyon isteğine göre güncelle. Halihazırdaki çalışan pinleri gereksiz yere bozma, sadece istenen ekleme/düzeltmeleri yap. Çıktı olarak sadece tek bir geçerli JSON nesnesi döndür."""

    def format_sse(data: Dict[str, Any]) -> str:
        return f"data: {json.dumps(data, ensure_ascii=False)}\n\n"

    yield format_sse({
        "type": "stage",
        "stageIndex": 0,
        "title": "1. Revizyon İsteğin İnceleniyor",
        "subtitle": f"AI Mucit ({chosen_model}) mevcut devreni ve isteğini analiz ediyor...",
        "progressPercent": 15
    })

    provider_used = "ollama" if (chosen_model.startswith("ollama/") or chosen_model == "local") else "litellm"
    t0 = time.time()
    accumulated_text = ""
    error_note: Optional[str] = None

    project_name_found = False
    seen_component_keys: Set[str] = set()
    discovered_components: List[Dict[str, Any]] = []
    seen_wire_count = 0
    current_stage = 0

    def parse_incremental_stream(text: str) -> List[Dict[str, Any]]:
        nonlocal project_name_found, seen_wire_count, current_stage
        events = []

        if not project_name_found:
            m_name = re.search(r'"proje_adi"\s*:\s*"([^"]+)"', text)
            if m_name:
                p_name = m_name.group(1).strip()
                project_name_found = True
                events.append({
                    "type": "project_name",
                    "name": p_name
                })

        m_parts_block = re.search(r'"gerekli_parcalar"\s*:\s*\[(.*?)\]', text, re.DOTALL)
        if m_parts_block:
            found_parts = re.findall(r'"([A-Za-z0-9_]+)"', m_parts_block.group(1))
            for p in found_parts:
                k = f"inv_{p.upper()}"
                if k not in seen_component_keys:
                    seen_component_keys.add(k)
                    label, icon = get_component_meta(p)
                    discovered_components.append({
                        "id": p,
                        "label": label,
                        "icon": icon,
                        "kind": "inventory"
                    })
                    events.append({
                        "type": "component_discovered",
                        "id": p,
                        "label": label,
                        "icon": icon,
                        "totalCount": len(discovered_components)
                    })

        found_comps = re.findall(r'\{\s*"id"\s*:\s*"([^"]+)"\s*,\s*"type"\s*:\s*"([^"]+)"', text)
        for cid, ctype in found_comps:
            k = f"comp_{cid.lower()}"
            if k not in seen_component_keys:
                seen_component_keys.add(k)
                label, icon = get_component_meta(cid, ctype)
                discovered_components.append({
                    "id": cid,
                    "label": label,
                    "icon": icon,
                    "componentType": ctype,
                    "kind": "circuit"
                })
                events.append({
                    "type": "component_discovered",
                    "id": cid,
                    "label": label,
                    "icon": icon,
                    "componentType": ctype,
                    "totalCount": len(discovered_components)
                })

        if discovered_components and current_stage < 1:
            current_stage = 1
            events.append({
                "type": "stage",
                "stageIndex": 1,
                "title": "2. Parçalar Güncelleniyor",
                "subtitle": f"{len(discovered_components)} parça devrene entegre ediliyor...",
                "progressPercent": 40
            })

        found_wires = re.findall(r'\{\s*"from"\s*:\s*"([^"]+)"\s*,\s*"to"\s*:\s*"([^"]+)"', text)
        if len(found_wires) > seen_wire_count:
            seen_wire_count = len(found_wires)
            last_from, last_to = found_wires[-1]
            if current_stage < 2:
                current_stage = 2
                events.append({
                    "type": "stage",
                    "stageIndex": 2,
                    "title": "3. Kablo Bağlantıları Yeniden Düzenleniyor",
                    "subtitle": f"{seen_wire_count} kablo bağlandı ({last_from} ➔ {last_to})...",
                    "progressPercent": 65
                })
            else:
                events.append({
                    "type": "wires_progress",
                    "count": seen_wire_count,
                    "latestWire": f"{last_from} ➔ {last_to}"
                })

        if '"akis_adimlari"' in text and current_stage < 3:
            current_stage = 3
            events.append({
                "type": "stage",
                "stageIndex": 3,
                "title": "4. Akış Şeması Revize Ediliyor",
                "subtitle": "Gözlemle ➔ Karar Ver ➔ Evet/Hayır adımları yeni parçalarla güncelleniyor...",
                "progressPercent": 80
            })

        if '"arduino_kodu"' in text and current_stage < 4:
            current_stage = 4
            code_lines = max(5, text.count('\\n'))
            events.append({
                "type": "stage",
                "stageIndex": 4,
                "title": "5. Arduino Kodu Yenileniyor ve Doğrulanıyor",
                "subtitle": f"Arduino C++ kodu güncelleniyor (~{code_lines} satır)...",
                "progressPercent": 90
            })
            events.append({
                "type": "code_progress",
                "lines": code_lines
            })

        return events

    try:
        if provider_used == "ollama":
            if not models_info["ollama_active"]:
                raise RuntimeError(f"Yerel Ollama servisi ({ollama_url}) çalışmıyor veya ulaşılamıyor.")

            local_ids = [m["id"] for m in models_info.get("local_models", [])]
            if chosen_model not in local_ids and models_info.get("default_model"):
                chosen_model = models_info["default_model"]
            clean_model = chosen_model.replace("ollama/", "")
            is_reasoning_model = any(k in clean_model.lower() for k in ("deepseek-r1", "qwq", "r1"))

            ollama_payload: Dict[str, Any] = {
                "model": clean_model,
                "system": REVISION_SYSTEM_PROMPT,
                "prompt": user_prompt,
                "stream": True,
                "options": {
                    "temperature": 0.1,
                    "num_predict": 2500 if is_reasoning_model else 1500
                }
            }
            if not is_reasoning_model:
                ollama_payload["format"] = "json"

            client_timeout = httpx.Timeout(120.0, connect=10.0)
            with httpx.Client(timeout=client_timeout) as client:
                with client.stream("POST", f"{ollama_url}/api/generate", json=ollama_payload) as resp:
                    if resp.status_code != 200:
                        raise RuntimeError(f"Ollama stream hatası: HTTP {resp.status_code}")
                    for line in resp.iter_lines():
                        if not line:
                            continue
                        try:
                            chunk = json.loads(line)
                            token = chunk.get("response", "")
                            accumulated_text += token
                            sub_events = parse_incremental_stream(accumulated_text)
                            for sev in sub_events:
                                yield format_sse(sev)
                        except Exception:
                            continue
        else:
            stream_resp = litellm.completion(
                model=chosen_model,
                messages=[
                    {"role": "system", "content": REVISION_SYSTEM_PROMPT},
                    {"role": "user", "content": user_prompt}
                ],
                stream=True,
                api_key=api_key,
                temperature=0.2
            )
            for chunk_obj in stream_resp:
                if chunk_obj.choices and chunk_obj.choices[0].delta:
                    delta = chunk_obj.choices[0].delta.content or ""
                    if delta:
                        accumulated_text += delta
                        sub_events = parse_incremental_stream(accumulated_text)
                        for sev in sub_events:
                            yield format_sse(sev)

        duration_ms = int((time.time() - t0) * 1000)
        parsed = safe_parse_llm_json(accumulated_text)

        if not isinstance(parsed, dict):
            raise ValueError("AI revizyon yanıtı geçerli bir JSON nesnesi değil.")
        if not parsed.get("netlist") or not isinstance(parsed.get("netlist"), dict):
            raise ValueError("AI revizyon yanıtında 'netlist' alanı eksik.")
        if not parsed.get("akis_adimlari") or not isinstance(parsed.get("akis_adimlari"), dict):
            raise ValueError("AI revizyon yanıtında 'akis_adimlari' alanı eksik.")
        raw_code = sanitize_arduino_identifiers(str(parsed.get("arduino_kodu") or "").strip())
        if not raw_code:
            raise ValueError("AI revizyon yanıtında 'arduino_kodu' alanı eksik veya boş.")

        norm_data, norm_warnings = normalize_project_dict(parsed)

        completed_netlist, actuator_notes = ensure_code_actuators_in_netlist(
            netlist_dict=norm_data["netlist"],
            code=raw_code,
            prompt=revision_prompt
        )
        completed_netlist, topo_notes = auto_complete_electrical_topology(completed_netlist)
        norm_data["netlist"] = completed_netlist
        norm_warnings.extend(actuator_notes + topo_notes)

        netlist_obj = CircuitNetlist(**norm_data["netlist"])
        akis_obj = AkisAdimi(**norm_data["akis_adimlari"])

        blocking_errors, report = validate_one_shot_topology_and_code(
            netlist=netlist_obj,
            akis=akis_obj,
            code=raw_code
        )
        if blocking_errors:
            raise ValueError(" | ".join(blocking_errors))

        steps = build_baglanti_adimlari_from_netlist(netlist_obj)
        project = ProjeTasarimi(
            proje_adi=str(parsed.get("proje_adi") or "").strip() or current_project.get("proje_adi", "Revize Edilen Proje"),
            karsilama_mesaji=str(parsed.get("karsilama_mesaji") or "").strip() or "Devren ve kodun revizyon isteğine göre başarıyla güncellendi! 🚀",
            gerekli_parcalar=norm_data.get("gerekli_parcalar") or ["ARDUINO_UNO", "BREADBOARD"],
            netlist=netlist_obj,
            baglanti_adimlari=steps,
            akis_adimlari=akis_obj,
            arduino_kodu=raw_code,
            guvenlik_notu=str(parsed.get("guvenlik_notu") or "").strip() or "Parçaları breadboard pinlerine dikkatlice yerleştir.",
            uyarilar=norm_warnings + list(report.warnings),
            verification=report
        )

        record_ai_log(
            stage="Proje Revizyonu: Devre + Akış + Kod (Stream)",
            model=chosen_model,
            provider=provider_used,
            duration_ms=duration_ms,
            status="SUCCESS" if report.is_valid else "VALIDATION_WARNING",
            user_goal=revision_prompt,
            system_prompt=REVISION_SYSTEM_PROMPT,
            user_prompt=user_prompt,
            raw_response=accumulated_text,
            processed_output=project.model_dump(by_alias=True),
            notes=list(report.checks) + norm_warnings + list(report.warnings)
        )

        yield format_sse({
            "type": "complete",
            "project": project.model_dump(by_alias=True),
            "progressPercent": 100
        })

    except Exception as e:
        duration_ms = int((time.time() - t0) * 1000)
        err_msg = f"Revizyon yanıtı doğrulanamadı: {e}"
        record_ai_log(
            stage="Proje Revizyonu: Devre + Akış + Kod (Stream)",
            model=chosen_model,
            provider=provider_used,
            duration_ms=duration_ms,
            status="ERROR",
            user_goal=revision_prompt,
            system_prompt=REVISION_SYSTEM_PROMPT,
            user_prompt=user_prompt,
            raw_response=accumulated_text,
            processed_output=None,
            notes=[err_msg]
        )
        yield format_sse({
            "type": "error",
            "message": err_msg
        })



def extract_netlist_pin_bindings(netlist: Optional[CircuitNetlist]) -> List[PinBindingInfo]:
    """
    Netlist grafiğini tarayarak her Arduino pininin (uno.D*, uno.A*) hangi bileşeni
    (doğrudan veya seri bir direnç üzerinden) kontrol ettiğini çıkarır.
    """
    if not netlist or not netlist.components or not netlist.connections:
        return []

    comp_map: Dict[str, NetlistComponent] = {c.id: c for c in netlist.components}
    adj: Dict[str, Set[str]] = {}
    for conn in netlist.connections:
        f = conn.from_pin.strip()
        t = conn.to_pin.strip()
        adj.setdefault(f, set()).add(t)
        adj.setdefault(t, set()).add(f)

    bindings: List[PinBindingInfo] = []
    seen_pairs: Set[Tuple[str, str]] = set()

    def get_role(ctype: str, pin_name: str) -> str:
        if ctype in ("wokwi-led", "wokwi-buzzer", "wokwi-servo"):
            return "OUTPUT"
        if ctype in ("wokwi-photoresistor", "wokwi-photoresistor-sensor", "wokwi-potentiometer", "wokwi-pushbutton"):
            return "INPUT"
        if ctype == "wokwi-hc-sr04":
            return "OUTPUT" if pin_name.upper() == "TRIG" else "INPUT"
        return "OUTPUT"

    uno_endpoints = sorted([ep for ep in adj.keys() if ep.startswith("uno.D") or ep.startswith("uno.A")])

    for uno_ep in uno_endpoints:
        short_uno = uno_ep.replace("uno.", "")
        neighbors = adj.get(uno_ep, set())

        for nb in sorted(neighbors):
            if "." not in nb:
                continue
            cid, cpin = nb.split(".", 1)
            comp = comp_map.get(cid)
            if not comp:
                continue

            if comp.type != "wokwi-resistor":
                if (short_uno, cid) not in seen_pairs:
                    seen_pairs.add((short_uno, cid))
                    bindings.append(PinBindingInfo(
                        uno_pin=short_uno,
                        component_id=cid,
                        component_label=comp.label or cid,
                        component_type=comp.type,
                        pin_name=cpin,
                        via_component=None,
                        role=get_role(comp.type, cpin)
                    ))
            else:
                other_r_pin = f"{cid}.2" if cpin == "1" else f"{cid}.1"
                for nb2 in sorted(adj.get(other_r_pin, set())):
                    if "." not in nb2:
                        continue
                    cid2, cpin2 = nb2.split(".", 1)
                    comp2 = comp_map.get(cid2)
                    if comp2 and comp2.type != "wokwi-resistor":
                        if (short_uno, cid2) not in seen_pairs:
                            seen_pairs.add((short_uno, cid2))
                            bindings.append(PinBindingInfo(
                                uno_pin=short_uno,
                                component_id=cid2,
                                component_label=comp2.label or cid2,
                                component_type=comp2.type,
                                pin_name=cpin2,
                                via_component=f"{cid} ({comp.label or 'Direnç'})",
                                role=get_role(comp2.type, cpin2)
                            ))

    return bindings


def build_baglanti_adimlari_from_netlist(netlist: CircuitNetlist) -> List[BaglantiAdimi]:
    """Netlist bağlantılarından çocuk dostu adım adım bağlantı listesi üretir."""
    comp_labels = {c.id: c.label for c in netlist.components}
    steps: List[BaglantiAdimi] = []
    for idx, conn in enumerate(netlist.connections, start=1):
        f = conn.from_pin
        t = conn.to_pin
        f_label = f.replace("uno.", "Arduino ")
        if "." in f and not f.startswith("uno."):
            p, pin = f.split(".", 1)
            f_label = f"{comp_labels.get(p, p)} ({pin} pini)"
        t_label = "Breadboard GND (-) Hattı" if t == "GND" else ("Breadboard 5V (+) Hattı" if t == "5V" else t.replace("uno.", "Arduino "))
        if "." in t and not t.startswith("uno."):
            p, pin = t.split(".", 1)
            t_label = f"{comp_labels.get(p, p)} ({pin} pini)"

        steps.append(BaglantiAdimi(
            adim_no=idx,
            talimat=f"{f_label} ucundan {t_label} noktasına kablo bağla.",
            ipucu="Kabloları breadboard üzerindeki ilgili pinlere dikkatlice yerleştir.",
            kaynak_parca=f.split(".")[0].upper() if "." in f else f,
            kaynak_pin=f.split(".")[1] if "." in f else f,
            hedef_parca=t.split(".")[0].upper() if "." in t else t,
            hedef_pin=t.split(".")[1] if "." in t else t,
            kablo_rengi=conn.color or "#3b82f6"
        ))
    return steps


def generate_wiring_only(
    prompt: str,
    inventory: List[str],
    model: str = "default",
    ollama_url: str = "http://127.0.0.1:11434",
    api_key: Optional[str] = None
) -> WiringDesignResponse:
    """
    1. AI Çağrısı: Çocuğun hayalinden YALNIZCA kablolama (components + connections) üretir.
    Yapay zekadan yanıt alınamazsa veya geçersiz çıktı dönerse HATA fırlatır (asla sahte/fallback devre üretmez).
    """
    # 0. Prompt Güvenlik ve Uygunluk Denetimi
    val = validate_project_prompt(prompt)
    if not val.is_valid:
        raise RuntimeError(val.user_message)

    models_info = get_all_available_models(ollama_url)
    chosen_model = model if model != "default" and model is not None else models_info["default_model"]

    user_prompt = f"""KULLANICI PROJE İSTEĞİ: "{prompt}"
Sadece yukarıdaki istekte belirtilen parçaları kullanarak Netlist JSON üret. Tek satır (minified) JSON döndür."""

    raw_text: Optional[str] = None
    provider_used = "ollama" if (chosen_model.startswith("ollama/") or chosen_model == "local") else "litellm"
    t0 = time.time()
    error_note: Optional[str] = None

    if provider_used == "ollama":
        if models_info["ollama_active"]:
            local_ids = [m["id"] for m in models_info.get("local_models", [])]
            if chosen_model not in local_ids and models_info.get("default_model"):
                chosen_model = models_info["default_model"]
            clean_model = chosen_model.replace("ollama/", "")
            try:
                res = httpx.post(
                    f"{ollama_url}/api/generate",
                    json={
                        "model": clean_model,
                        "system": WIRING_ONLY_SYSTEM_PROMPT,
                        "prompt": user_prompt,
                        "stream": False,
                        "format": "json",
                        "options": {"temperature": 0.1, "num_predict": 420}
                    },
                    timeout=120.0
                )
                if res.status_code == 200:
                    raw_text = res.json().get("response", "")
                else:
                    error_note = f"Ollama HTTP {res.status_code}: {res.text[:200]}"
            except Exception as e:
                error_note = f"Ollama bağlantı/zaman aşımı hatası: {e}"
                print(f"[Stage 1 Wiring] {error_note}")
        else:
            error_note = f"Yerel Ollama servisi ({ollama_url}) çalışmıyor veya ulaşılamıyor."
    else:
        if not api_key:
            if "gemini" in chosen_model:
                api_key = os.getenv("GEMINI_API_KEY")
            elif "gpt" in chosen_model:
                api_key = os.getenv("OPENAI_API_KEY")
            elif "claude" in chosen_model:
                api_key = os.getenv("ANTHROPIC_API_KEY")
        if api_key:
            try:
                from litellm import completion
                response = completion(
                    model=chosen_model,
                    messages=[
                        {"role": "system", "content": WIRING_ONLY_SYSTEM_PROMPT},
                        {"role": "user", "content": user_prompt}
                    ],
                    response_format={"type": "json_object"},
                    api_key=api_key,
                    temperature=0.2
                )
                raw_text = response.choices[0].message.content
            except Exception as e:
                error_note = f"Bulut AI ({chosen_model}) hatası: {e}"
                print(f"[Stage 1 Wiring] {error_note}")
        else:
            error_note = f"Seçilen bulut modeli ('{chosen_model}') için API anahtarı girilmemiş."

    duration_ms = int((time.time() - t0) * 1000)

    if not raw_text:
        msg = error_note or f"Yapay zeka modelinden ('{chosen_model}') yanıt alınamadı."
        record_ai_log(
            stage="1. Aşama: Kablolama (Wiring JSON)",
            model=chosen_model,
            provider=provider_used,
            duration_ms=duration_ms,
            status="ERROR",
            user_goal=prompt,
            system_prompt=WIRING_ONLY_SYSTEM_PROMPT,
            user_prompt=user_prompt,
            raw_response=f"[HATA: {msg}]",
            processed_output=None,
            notes=[msg]
        )
        raise RuntimeError(msg)

    try:
        parsed = safe_parse_llm_json(raw_text)
        if not isinstance(parsed, dict) or not isinstance(parsed.get("netlist"), dict):
            raise ValueError("AI çıktısında geçerli bir 'netlist' alanı bulunamadı.")

        norm_data, norm_warnings = normalize_project_dict(parsed)
        netlist_obj = CircuitNetlist(**norm_data["netlist"])

        if len(netlist_obj.components) == 0 or len(netlist_obj.connections) == 0:
            raise ValueError("AI tarafından üretilen netlist içerisinde bileşen (components) veya bağlantı (connections) boş döndü.")

        pin_bindings = extract_netlist_pin_bindings(netlist_obj)
        steps = build_baglanti_adimlari_from_netlist(netlist_obj)
        resp = WiringDesignResponse(
            proje_adi=norm_data.get("proje_adi") or (prompt.strip()[:40] or "Arduino Projem"),
            karsilama_mesaji=norm_data.get("karsilama_mesaji") or "Devre kablolaman hazır! Adım adım kabloları takalım.",
            gerekli_parcalar=norm_data.get("gerekli_parcalar") or ["ARDUINO_UNO", "BREADBOARD"],
            netlist=netlist_obj,
            baglanti_adimlari=steps,
            guvenlik_notu=norm_data.get("guvenlik_notu") or "Parçaları breadboard pinlerine dikkatlice yerleştir.",
            pin_bindings=pin_bindings,
            uyarilar=norm_warnings
        )
        record_ai_log(
            stage="1. Aşama: Kablolama (Wiring JSON)",
            model=chosen_model,
            provider=provider_used,
            duration_ms=duration_ms,
            status="SUCCESS",
            user_goal=prompt,
            system_prompt=WIRING_ONLY_SYSTEM_PROMPT,
            user_prompt=user_prompt,
            raw_response=raw_text,
            processed_output=resp.model_dump(by_alias=True),
            notes=norm_warnings
        )
        return resp
    except Exception as e:
        err_msg = f"Yapay zeka yanıtı geçerli bir devre şemasına dönüştürülemedi: {e}"
        record_ai_log(
            stage="1. Aşama: Kablolama (Wiring JSON)",
            model=chosen_model,
            provider=provider_used,
            duration_ms=duration_ms,
            status="ERROR",
            user_goal=prompt,
            system_prompt=WIRING_ONLY_SYSTEM_PROMPT,
            user_prompt=user_prompt,
            raw_response=raw_text,
            processed_output=None,
            notes=[err_msg]
        )
        raise RuntimeError(err_msg)


# =========================================================
# AŞAMA 2 (STAGE 2): KABLOLAMAYA UYGUN AKIŞ DİYAGRAMI VE ARDUINO KODU + TEYİT
# =========================================================

LOGIC_ONLY_SYSTEM_PROMPT = """Sen Arduino kodlama öğretmenisin. Verilen kablolama (Netlist ve Pin Tablosu) ile kullanıcı isteğine birebir uyan:
1. "akis_adimlari": {"gozlemle":"...","karar_ver":"...","evet_sonucu":"...","hayir_sonucu":"..."}
2. "arduino_kodu": Derlenebilir Arduino Uno C++ kodu (setup ve loop içeren, servo varsa #include <Servo.h> ekleyen)
üret.
KURALLAR:
1. Sadece verilen pin tablosundaki pinleri kullan.
2. Akış diyagramında sadece devredeki gerçek parçalardan bahset.
3. Koddaki değişken, sabit ve fonksiyon adlarında SADECE İngilizce harf, rakam ve alt çizgi kullan (ç, ğ, ı, İ, ö, ş, ü YASAK; örn: ESIK_DEGER). Türkçe karakter sadece yorumlarda ve tırnak içindeki metinlerde olabilir.
Tek satır (minified) JSON döndür."""


def verify_logic_against_wiring(
    netlist: CircuitNetlist,
    raw_akis: Dict[str, Any],
    raw_code: str
) -> Tuple[AkisAdimi, str, LogicVerificationReport]:
    """
    2. AI çağrısından dönen akış diyagramını ve Arduino C++ kodunu kablolama (netlist) ile karşılaştırır.
    Sahte/sentetik kod üretmez; gerçek AI çıktısının doğrulama raporunu döner.
    """
    bindings = extract_netlist_pin_bindings(netlist)
    checks: List[str] = []
    warnings: List[str] = []

    final_akis = AkisAdimi(
        gozlemle=str(raw_akis.get("gozlemle") or "").strip(),
        karar_ver=str(raw_akis.get("karar_ver") or "").strip(),
        evet_sonucu=str(raw_akis.get("evet_sonucu") or "").strip(),
        hayir_sonucu=str(raw_akis.get("hayir_sonucu") or "").strip()
    )
    flow_complete = all([final_akis.gozlemle, final_akis.karar_ver, final_akis.evet_sonucu, final_akis.hayir_sonucu])
    if flow_complete:
        checks.append("✓ Akış diyagramı (Gözlemle → Karar Ver → Evet/Hayır) eksiksiz.")
    else:
        warnings.append("Akış diyagramında bazı adımlar boş döndü.")

    code_candidate = (raw_code or "").strip()
    has_setup = "void setup" in code_candidate
    has_loop = "void loop" in code_candidate
    braces_balanced = code_candidate.count("{") > 0 and (code_candidate.count("{") == code_candidate.count("}"))
    needs_servo = any(b.component_type == "wokwi-servo" for b in bindings)
    has_servo_header = (not needs_servo) or ("Servo.h" in code_candidate)

    syntax_ok = bool(code_candidate and has_setup and has_loop and braces_balanced and has_servo_header)
    if syntax_ok:
        checks.append("✓ Arduino C++ kodu sözdizimi (setup, loop, parantez dengesi) doğrulandı.")
    else:
        warnings.append("Arduino C++ kodunda setup/loop veya parantez dengesi uyarısı var.")

    pin_mismatches = check_code_netlist_pin_consistency(code_candidate, netlist)
    pins_matched = len(pin_mismatches) == 0
    if pins_matched:
        checks.append(f"✓ Koddaki pinler devre kablolamasıyla uyumlu ({', '.join(f'{b.uno_pin} → {b.component_label}' for b in bindings)}).")
    else:
        warnings.extend(pin_mismatches)

    report = LogicVerificationReport(
        is_valid=syntax_ok and pins_matched and flow_complete,
        syntax_ok=syntax_ok,
        pins_matched=pins_matched,
        flow_complete=flow_complete,
        auto_repaired=False,
        pin_bindings=bindings,
        checks=checks,
        warnings=warnings
    )
    return final_akis, code_candidate, report


def generate_logic_and_code_for_wiring(
    prompt: str,
    proje_adi: str,
    netlist: CircuitNetlist,
    model: str = "default",
    ollama_url: str = "http://127.0.0.1:11434",
    api_key: Optional[str] = None
) -> LogicDesignResponse:
    """
    2. AI Çağrısı: Render edilen kablolamaya (netlist) birebir uygun Akış Diyagramı ve Arduino Kodu üretir.
    Yapay zekadan yanıt alınamazsa HATA fırlatır (asla sahte kod sentezlemez).
    """
    norm_wrapper, _ = normalize_project_dict({
        "proje_adi": proje_adi,
        "netlist": netlist.model_dump(by_alias=True)
    })
    clean_netlist = CircuitNetlist(**norm_wrapper["netlist"])
    bindings = extract_netlist_pin_bindings(clean_netlist)

    pin_table_lines = [
        f"- Arduino Pin {b.uno_pin} (kodda `{b.uno_pin if b.uno_pin.startswith('A') else b.uno_pin.replace('D', '')}` kullan) "
        f"-> {b.component_label} (`{b.component_id}.{b.pin_name}`) [{b.role}]"
        + (f" (Arada {b.via_component} var)" if b.via_component else "")
        for b in bindings
    ]
    pin_table_str = "\n".join(pin_table_lines) if pin_table_lines else "- Standart Arduino Uno bağlantısı"
    comp_summary = ", ".join(c.label for c in clean_netlist.components)

    user_prompt = f"""PROJE ADI: "{proje_adi}"
KULLANICI İSTEĞİ: "{prompt}"
DEVREDEKİ PARÇALAR: {comp_summary}
KABLOLAMA PİN TABLOSU:
{pin_table_str}

Yukarıdaki kablolamaya uygun `akis_adimlari` ve `arduino_kodu` alanlarını içeren tek satır JSON üret."""

    models_info = get_all_available_models(ollama_url)
    chosen_model = model if model != "default" and model is not None else models_info["default_model"]

    raw_text: Optional[str] = None
    provider_used = "ollama" if (chosen_model.startswith("ollama/") or chosen_model == "local") else "litellm"
    t0 = time.time()
    error_note: Optional[str] = None

    if provider_used == "ollama":
        if models_info["ollama_active"]:
            local_ids = [m["id"] for m in models_info.get("local_models", [])]
            if chosen_model not in local_ids and models_info.get("default_model"):
                chosen_model = models_info["default_model"]
            clean_model = chosen_model.replace("ollama/", "")
            try:
                res = httpx.post(
                    f"{ollama_url}/api/generate",
                    json={
                        "model": clean_model,
                        "system": LOGIC_ONLY_SYSTEM_PROMPT,
                        "prompt": user_prompt,
                        "stream": False,
                        "format": "json",
                        "options": {"temperature": 0.1, "num_predict": 550}
                    },
                    timeout=120.0
                )
                if res.status_code == 200:
                    raw_text = res.json().get("response", "")
                else:
                    error_note = f"Ollama HTTP {res.status_code}: {res.text[:200]}"
            except Exception as e:
                error_note = f"Ollama bağlantı/zaman aşımı hatası: {e}"
                print(f"[Stage 2 Logic] {error_note}")
        else:
            error_note = f"Yerel Ollama servisi ({ollama_url}) çalışmıyor veya ulaşılamıyor."
    else:
        if not api_key:
            if "gemini" in chosen_model:
                api_key = os.getenv("GEMINI_API_KEY")
            elif "gpt" in chosen_model:
                api_key = os.getenv("OPENAI_API_KEY")
            elif "claude" in chosen_model:
                api_key = os.getenv("ANTHROPIC_API_KEY")
        if api_key:
            try:
                from litellm import completion
                response = completion(
                    model=chosen_model,
                    messages=[
                        {"role": "system", "content": LOGIC_ONLY_SYSTEM_PROMPT},
                        {"role": "user", "content": user_prompt}
                    ],
                    response_format={"type": "json_object"},
                    api_key=api_key,
                    temperature=0.2
                )
                raw_text = response.choices[0].message.content
            except Exception as e:
                error_note = f"Bulut AI ({chosen_model}) hatası: {e}"
                print(f"[Stage 2 Logic] {error_note}")
        else:
            error_note = f"Seçilen bulut modeli ('{chosen_model}') için API anahtarı girilmemiş."

    duration_ms = int((time.time() - t0) * 1000)

    if not raw_text:
        msg = error_note or f"2. Aşama (Akış & Kod) için yapay zekadan ('{chosen_model}') yanıt alınamadı."
        record_ai_log(
            stage="2. Aşama: Akış Diyagramı & Arduino Kodu",
            model=chosen_model,
            provider=provider_used,
            duration_ms=duration_ms,
            status="ERROR",
            user_goal=prompt,
            system_prompt=LOGIC_ONLY_SYSTEM_PROMPT,
            user_prompt=user_prompt,
            raw_response=f"[HATA: {msg}]",
            processed_output=None,
            notes=[msg]
        )
        raise RuntimeError(msg)

    try:
        parsed = safe_parse_llm_json(raw_text)
        if not isinstance(parsed, dict):
            raise ValueError("AI yanıtı bir JSON nesnesi değil.")
        raw_akis = parsed.get("akis_adimlari")
        raw_code = sanitize_arduino_identifiers(str(parsed.get("arduino_kodu") or "").strip())
        if not isinstance(raw_akis, dict) or not raw_code:
            raise ValueError("AI yanıtında 'akis_adimlari' veya 'arduino_kodu' alanı eksik.")

        final_akis, final_code, report = verify_logic_against_wiring(
            netlist=clean_netlist,
            raw_akis=raw_akis,
            raw_code=raw_code
        )

        resp = LogicDesignResponse(
            akis_adimlari=final_akis,
            arduino_kodu=final_code,
            verification=report
        )

        log_notes = list(report.checks) + list(report.warnings)
        record_ai_log(
            stage="2. Aşama: Akış Diyagramı & Arduino Kodu",
            model=chosen_model,
            provider=provider_used,
            duration_ms=duration_ms,
            status="SUCCESS" if report.is_valid else "VALIDATION_WARNING",
            user_goal=prompt,
            system_prompt=LOGIC_ONLY_SYSTEM_PROMPT,
            user_prompt=user_prompt,
            raw_response=raw_text,
            processed_output=resp.model_dump(),
            notes=log_notes
        )
        return resp
    except Exception as e:
        err_msg = f"2. Aşama AI yanıtı ayrıştırılamadı: {e}"
        record_ai_log(
            stage="2. Aşama: Akış Diyagramı & Arduino Kodu",
            model=chosen_model,
            provider=provider_used,
            duration_ms=duration_ms,
            status="ERROR",
            user_goal=prompt,
            system_prompt=LOGIC_ONLY_SYSTEM_PROMPT,
            user_prompt=user_prompt,
            raw_response=raw_text,
            processed_output=None,
            notes=[err_msg]
        )
        raise RuntimeError(err_msg)


# =========================================================
# PROJELERİM (YALNIZCA KULLANICININ KURGULADIĞI PROJELER)
# =========================================================

SAVED_PROJECTS_FILE = os.path.join(os.path.dirname(__file__), "saved_projects.json")
PRESET_IDS_TO_EXCLUDE = {"gece_lambasi", "park_sensoru", "trafik_isiklari", "buton_servo"}


def get_saved_projects() -> List[SavedProjectEntry]:
    """Yalnızca kullanıcının kurguladığı kayıtlı projeleri döner (Örnek projeler kaldırıldı)."""
    user_entries: List[SavedProjectEntry] = []

    if os.path.isfile(SAVED_PROJECTS_FILE):
        try:
            with open(SAVED_PROJECTS_FILE, "r", encoding="utf-8") as f:
                raw_list = json.load(f)
            if isinstance(raw_list, list):
                for item in raw_list:
                    try:
                        entry = SavedProjectEntry(**item)
                        # Geriye uyumluluk: eski 4 alanlı akis_adimlari'yı AkisDiyagrami'na çevir
                        if entry.project.akis_diyagrami is None and entry.project.akis_adimlari is not None:
                            comps = (
                                [c.model_dump() for c in entry.project.netlist.components]
                                if entry.project.netlist
                                else []
                            )
                            entry.project.akis_diyagrami = legacy_akis_to_diyagram(
                                entry.project.akis_adimlari.model_dump(), comps
                            )
                        if not entry.is_preset and entry.id not in PRESET_IDS_TO_EXCLUDE:
                            user_entries.append(entry)
                    except Exception:
                        continue
        except Exception as e:
            print(f"[Projelerim] Kayıtlı projeler okunamadı: {e}")

    return user_entries


def save_project_entry(
    project: ProjeTasarimi,
    prompt: str = "",
    project_id: Optional[str] = None,
    badge: str = "AI Tasarımım ✨"
) -> SavedProjectEntry:
    """Yeni kurgulanan veya güncellenen bir projeyi Projelerim listesine kaydeder."""
    existing = get_saved_projects()
    pid = project_id or f"proj_{int(time.time() * 1000)}_{uuid.uuid4().hex[:4]}"

    if project.netlist and not project.verification:
        _, _, report = verify_logic_against_wiring(
            netlist=project.netlist,
            raw_akis=project.akis_adimlari.model_dump() if project.akis_adimlari else {},
            raw_code=project.arduino_kodu
        )
        project.verification = report

    new_entry = SavedProjectEntry(
        id=pid,
        created_at=time.strftime("%d.%m.%Y %H:%M"),
        prompt=prompt or project.proje_adi,
        is_preset=False,
        badge=badge,
        difficulty="Özel Kurgu",
        project=project
    )

    updated_user_list = [new_entry] + [e for e in existing if e.id != pid]
    try:
        with open(SAVED_PROJECTS_FILE, "w", encoding="utf-8") as f:
            json.dump([e.model_dump(by_alias=True) for e in updated_user_list[:50]], f, ensure_ascii=False, indent=2)
    except Exception as e:
        print(f"[Projelerim] Proje kaydedilemedi: {e}")

    return new_entry


def delete_saved_project(project_id: str) -> bool:
    """Kullanıcının kaydettiği bir projeyi siler."""
    existing = get_saved_projects()
    filtered = [e for e in existing if e.id != project_id]
    if len(filtered) == len(existing):
        return False
    try:
        with open(SAVED_PROJECTS_FILE, "w", encoding="utf-8") as f:
            json.dump([e.model_dump(by_alias=True) for e in filtered], f, ensure_ascii=False, indent=2)
        return True
    except Exception:
        return False

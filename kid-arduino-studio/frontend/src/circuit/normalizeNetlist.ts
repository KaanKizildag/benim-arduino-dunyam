/**
 * Katman 0: Netlist Normalizasyonu ve Düğüm (Net) Çıkarımı (Union-Find)
 * - Bileşen tipi alias'larını standart Wokwi tiplerine dönüştürür.
 * - Arduino pinlerini (uno.13, D13, arduino.D13 -> uno.D13) normalize eder.
 * - Güç hatlarını (uno.GND, GND.1, uno.5V, VCC -> GND / 5V) normalize eder.
 * - Bileşen pin varyantlarını (led1.anode, led1.+, r1.A, servo1.SIG, ldr1.OUT vb.) standartlaştırır.
 * - Ters yönlü güç bağlantılarını ({from:'GND', to:'led1.C'} -> {from:'led1.C', to:'GND'}) düzeltir.
 * - Union-Find ile elektriksel düğümleri (ElectricalNet) çıkarır.
 */

import type {
  CircuitNetlist,
  NetlistComponent,
  NetlistConnection,
  ElectricalNet
} from './types';

export const SUPPORTED_COMPONENT_TYPES = new Set<string>([
  'wokwi-led',
  'wokwi-rgb-led',
  'wokwi-resistor',
  'wokwi-photoresistor',
  'wokwi-photoresistor-sensor',
  'wokwi-buzzer',
  'wokwi-pushbutton',
  'wokwi-servo',
  'wokwi-hc-sr04',
  'wokwi-potentiometer',
  'wokwi-hc-05',
  'wokwi-hc-06',
  'wokwi-l293d',
  'wokwi-l298n',
  'wokwi-dc-motor',
  'wokwi-pir-motion-sensor',
  'wokwi-dht22',
  'wokwi-analog-joystick',
  'wokwi-relay-module',
  'wokwi-lcd1602',
  'wokwi-ssd1306',
  'wokwi-soil-moisture-sensor',
  'wokwi-rain-sensor',
  'wokwi-water-sensor',
  'wokwi-gas-sensor',
  'wokwi-flame-sensor',
  'wokwi-small-sound-sensor',
  'wokwi-ir-receiver',
  'wokwi-ntc-temperature-sensor'
]);

export interface NormalizationResult {
  netlist: CircuitNetlist;
  nets: ElectricalNet[];
  warnings: string[];
  errors: string[];
}

// Bileşen tipi alias haritası
const COMPONENT_TYPE_ALIASES: Record<string, { type: string; defaultProps?: Record<string, any> }> = {
  'wokwi-led': { type: 'wokwi-led' },
  'led': { type: 'wokwi-led' },
  'led_red': { type: 'wokwi-led', defaultProps: { color: 'red' } },
  'led-red': { type: 'wokwi-led', defaultProps: { color: 'red' } },
  'red-led': { type: 'wokwi-led', defaultProps: { color: 'red' } },
  'led_green': { type: 'wokwi-led', defaultProps: { color: 'green' } },
  'led-green': { type: 'wokwi-led', defaultProps: { color: 'green' } },
  'green-led': { type: 'wokwi-led', defaultProps: { color: 'green' } },
  'led_yellow': { type: 'wokwi-led', defaultProps: { color: 'yellow' } },
  'led-yellow': { type: 'wokwi-led', defaultProps: { color: 'yellow' } },
  'yellow-led': { type: 'wokwi-led', defaultProps: { color: 'yellow' } },
  'led_blue': { type: 'wokwi-led', defaultProps: { color: 'blue' } },
  'led-blue': { type: 'wokwi-led', defaultProps: { color: 'blue' } },
  'blue-led': { type: 'wokwi-led', defaultProps: { color: 'blue' } },

  'wokwi-resistor': { type: 'wokwi-resistor' },
  'resistor': { type: 'wokwi-resistor' },
  'res': { type: 'wokwi-resistor' },
  'r': { type: 'wokwi-resistor' },
  'direnc': { type: 'wokwi-resistor' },
  'direnç': { type: 'wokwi-resistor' },
  'resistor_220': { type: 'wokwi-resistor', defaultProps: { value: '220' } },
  'resistor-220': { type: 'wokwi-resistor', defaultProps: { value: '220' } },
  'resistor_1k': { type: 'wokwi-resistor', defaultProps: { value: '1000' } },
  'resistor-1k': { type: 'wokwi-resistor', defaultProps: { value: '1000' } },
  'resistor_10k': { type: 'wokwi-resistor', defaultProps: { value: '10000' } },
  'resistor-10k': { type: 'wokwi-resistor', defaultProps: { value: '10000' } },

  'wokwi-photoresistor': { type: 'wokwi-photoresistor' },
  'photoresistor': { type: 'wokwi-photoresistor' },
  'ldr_discrete': { type: 'wokwi-photoresistor' },
  'ldr-discrete': { type: 'wokwi-photoresistor' },
  'discrete-ldr': { type: 'wokwi-photoresistor' },
  'ldr2': { type: 'wokwi-photoresistor' },

  'wokwi-photoresistor-sensor': { type: 'wokwi-photoresistor-sensor' },
  'photoresistor-sensor': { type: 'wokwi-photoresistor-sensor' },
  'ldr_sensor': { type: 'wokwi-photoresistor-sensor' },
  'ldr-sensor': { type: 'wokwi-photoresistor-sensor' },
  'ldr_module': { type: 'wokwi-photoresistor-sensor' },
  'ldr-module': { type: 'wokwi-photoresistor-sensor' },
  'ky-018': { type: 'wokwi-photoresistor-sensor' },
  'ky018': { type: 'wokwi-photoresistor-sensor' },
  'ldr': { type: 'wokwi-photoresistor' }, // Bağlantı pinlerine göre aşağıda netleştirilir

  'wokwi-buzzer': { type: 'wokwi-buzzer' },
  'buzzer': { type: 'wokwi-buzzer' },
  'piezo': { type: 'wokwi-buzzer' },
  'active_buzzer': { type: 'wokwi-buzzer' },
  'active-buzzer': { type: 'wokwi-buzzer' },
  'passive_buzzer': { type: 'wokwi-buzzer' },
  'passive-buzzer': { type: 'wokwi-buzzer' },

  'wokwi-pushbutton': { type: 'wokwi-pushbutton' },
  'pushbutton': { type: 'wokwi-pushbutton' },
  'push_button': { type: 'wokwi-pushbutton' },
  'push-button': { type: 'wokwi-pushbutton' },
  'button': { type: 'wokwi-pushbutton' },
  'btn': { type: 'wokwi-pushbutton' },
  'buton': { type: 'wokwi-pushbutton' },

  'wokwi-servo': { type: 'wokwi-servo' },
  'servo': { type: 'wokwi-servo' },
  'servo_sg90': { type: 'wokwi-servo' },
  'servo-sg90': { type: 'wokwi-servo' },
  'sg90': { type: 'wokwi-servo' },
  'servomotor': { type: 'wokwi-servo' },
  'servo-motor': { type: 'wokwi-servo' },

  'wokwi-hc-sr04': { type: 'wokwi-hc-sr04' },
  'hc-sr04': { type: 'wokwi-hc-sr04' },
  'hc_sr04': { type: 'wokwi-hc-sr04' },
  'hcsr04': { type: 'wokwi-hc-sr04' },
  'ultrasonic': { type: 'wokwi-hc-sr04' },
  'ultrasonic-sensor': { type: 'wokwi-hc-sr04' },
  'distance-sensor': { type: 'wokwi-hc-sr04' },

  'wokwi-potentiometer': { type: 'wokwi-potentiometer' },
  'potentiometer': { type: 'wokwi-potentiometer' },
  'pot': { type: 'wokwi-potentiometer' },
  'potans': { type: 'wokwi-potentiometer' },
  'potansiyometre': { type: 'wokwi-potentiometer' },

  'wokwi-rgb-led': { type: 'wokwi-rgb-led' },
  'rgb-led': { type: 'wokwi-rgb-led' },
  'rgb_led': { type: 'wokwi-rgb-led' },
  'led_rgb': { type: 'wokwi-rgb-led' },

  'wokwi-hc-05': { type: 'wokwi-hc-05' },
  'wokwi-hc05': { type: 'wokwi-hc-05' },
  'hc-05': { type: 'wokwi-hc-05' },
  'hc05': { type: 'wokwi-hc-05' },
  'bluetooth': { type: 'wokwi-hc-05' },
  'bluetooth_hc05': { type: 'wokwi-hc-05' },

  'wokwi-hc-06': { type: 'wokwi-hc-06' },
  'wokwi-hc06': { type: 'wokwi-hc-06' },
  'hc-06': { type: 'wokwi-hc-06' },
  'hc06': { type: 'wokwi-hc-06' },
  'bluetooth_hc06': { type: 'wokwi-hc-06' },

  'wokwi-l293d': { type: 'wokwi-l293d' },
  'l293d': { type: 'wokwi-l293d' },
  'l293': { type: 'wokwi-l293d' },
  'motor_driver': { type: 'wokwi-l293d' },
  'motor_driver_l293d': { type: 'wokwi-l293d' },

  'wokwi-l298n': { type: 'wokwi-l298n' },
  'l298n': { type: 'wokwi-l298n' },
  'l298': { type: 'wokwi-l298n' },
  'motor_driver_l298n': { type: 'wokwi-l298n' },

  'wokwi-dc-motor': { type: 'wokwi-dc-motor' },
  'wokwi-dcmotor': { type: 'wokwi-dc-motor' },
  'dc-motor': { type: 'wokwi-dc-motor' },
  'dc_motor': { type: 'wokwi-dc-motor' },
  'dcmotor': { type: 'wokwi-dc-motor' },
  'dc_motor_5v': { type: 'wokwi-dc-motor' },
  'motor': { type: 'wokwi-dc-motor' },

  'wokwi-pir-motion-sensor': { type: 'wokwi-pir-motion-sensor' },
  'pir': { type: 'wokwi-pir-motion-sensor' },
  'pir_sensor': { type: 'wokwi-pir-motion-sensor' },
  'pir-sensor': { type: 'wokwi-pir-motion-sensor' },

  'wokwi-dht22': { type: 'wokwi-dht22' },
  'wokwi-dht11': { type: 'wokwi-dht22' },
  'dht11': { type: 'wokwi-dht22' },
  'dht22': { type: 'wokwi-dht22' },

  'wokwi-analog-joystick': { type: 'wokwi-analog-joystick' },
  'joystick': { type: 'wokwi-analog-joystick' },
  'joystick_module': { type: 'wokwi-analog-joystick' },

  'wokwi-relay-module': { type: 'wokwi-relay-module' },
  'wokwi-relay': { type: 'wokwi-relay-module' },
  'relay': { type: 'wokwi-relay-module' },
  'relay_5v': { type: 'wokwi-relay-module' },

  'wokwi-lcd1602': { type: 'wokwi-lcd1602' },
  'lcd1602': { type: 'wokwi-lcd1602' },
  'lcd': { type: 'wokwi-lcd1602' },
  'lcd_16x2_i2c': { type: 'wokwi-lcd1602' },

  'wokwi-ssd1306': { type: 'wokwi-ssd1306' },
  'ssd1306': { type: 'wokwi-ssd1306' },
  'oled': { type: 'wokwi-ssd1306' },
  'oled_096_i2c': { type: 'wokwi-ssd1306' },

  'wokwi-soil-moisture-sensor': { type: 'wokwi-soil-moisture-sensor' },
  'soil_moisture': { type: 'wokwi-soil-moisture-sensor' },
  'soil-moisture': { type: 'wokwi-soil-moisture-sensor' },

  'wokwi-rain-sensor': { type: 'wokwi-rain-sensor' },
  'rain_sensor': { type: 'wokwi-rain-sensor' },
  'rain-sensor': { type: 'wokwi-rain-sensor' },

  'wokwi-water-sensor': { type: 'wokwi-water-sensor' },
  'water_sensor': { type: 'wokwi-water-sensor' },
  'water-sensor': { type: 'wokwi-water-sensor' },

  'wokwi-gas-sensor': { type: 'wokwi-gas-sensor' },
  'gas_sensor': { type: 'wokwi-gas-sensor' },
  'mq2': { type: 'wokwi-gas-sensor' },
  'mq2_gas': { type: 'wokwi-gas-sensor' },

  'wokwi-flame-sensor': { type: 'wokwi-flame-sensor' },
  'flame_sensor': { type: 'wokwi-flame-sensor' },
  'flame-sensor': { type: 'wokwi-flame-sensor' },

  'wokwi-small-sound-sensor': { type: 'wokwi-small-sound-sensor' },
  'sound_sensor': { type: 'wokwi-small-sound-sensor' },
  'sound-sensor': { type: 'wokwi-small-sound-sensor' },

  'wokwi-ir-receiver': { type: 'wokwi-ir-receiver' },
  'ir_receiver': { type: 'wokwi-ir-receiver' },
  'ir-receiver': { type: 'wokwi-ir-receiver' },

  'wokwi-ntc-temperature-sensor': { type: 'wokwi-ntc-temperature-sensor' },
  'ntc': { type: 'wokwi-ntc-temperature-sensor' }
};

// Her bileşen tipi için pin alias tablosu
const PIN_ALIASES_BY_TYPE: Record<string, Record<string, string>> = {
  'wokwi-led': {
    'A': 'A',
    'ANODE': 'A',
    'ANOT': 'A',
    '+': 'A',
    'POS': 'A',
    'POSITIVE': 'A',
    '1': 'A',
    'UZUN': 'A',
    'LONG': 'A',
    'VCC': 'A',
    'IN': 'A',
    'C': 'C',
    'K': 'C',
    'CATHODE': 'C',
    'KATOT': 'C',
    '-': 'C',
    'NEG': 'C',
    'NEGATIVE': 'C',
    '2': 'C',
    'GND': 'C',
    'KISA': 'C',
    'SHORT': 'C',
    'OUT': 'C'
  },
  'wokwi-resistor': {
    '1': '1',
    'PIN1': '1',
    'PIN_1': '1',
    'P1': '1',
    'A': '1',
    'IN': '1',
    'LEFT': '1',
    '+': '1',
    '2': '2',
    'PIN2': '2',
    'PIN_2': '2',
    'P2': '2',
    'B': '2',
    'OUT': '2',
    'RIGHT': '2',
    '-': '2'
  },
  'wokwi-photoresistor': {
    '1': '1',
    'PIN1': '1',
    'PIN_1': '1',
    'P1': '1',
    'A': '1',
    'VCC': '1',
    '+': '1',
    'IN': '1',
    'LEFT': '1',
    '2': '2',
    'PIN2': '2',
    'PIN_2': '2',
    'P2': '2',
    'B': '2',
    'GND': '2',
    '-': '2',
    'OUT': '2',
    'SIG': '2',
    'AO': '2',
    'A0': '2',
    'RIGHT': '2'
  },
  'wokwi-photoresistor-sensor': {
    'VCC': 'VCC',
    '5V': 'VCC',
    '3.3V': 'VCC',
    'V+': 'VCC',
    '+': 'VCC',
    'POWER': 'VCC',
    '1': 'VCC',
    'GND': 'GND',
    '-': 'GND',
    '0V': 'GND',
    'GROUND': 'GND',
    '2': 'GND',
    'DO': 'DO',
    'D0': 'DO',
    'DOUT': 'DO',
    'DIGITAL': 'DO',
    '3': 'DO',
    'AO': 'AO',
    'A0': 'AO',
    'AOUT': 'AO',
    'OUT': 'AO',
    'SIG': 'AO',
    'SIGNAL': 'AO',
    'ANALOG': 'AO',
    '4': 'AO'
  },
  'wokwi-buzzer': {
    '1': '1',
    '+': '1',
    'POS': '1',
    'POSITIVE': '1',
    'SIG': '1',
    'SIGNAL': '1',
    'A': '1',
    'ANODE': '1',
    'VCC': '1',
    'IN': '1',
    'PIN1': '1',
    'PIN_1': '1',
    'P1': '1',
    'RED': '1',
    '2': '2',
    '-': '2',
    'NEG': '2',
    'NEGATIVE': '2',
    'GND': '2',
    'GROUND': '2',
    'C': '2',
    'CATHODE': '2',
    'B': '2',
    'OUT': '2',
    'PIN2': '2',
    'PIN_2': '2',
    'P2': '2',
    'BLACK': '2'
  },
  'wokwi-pushbutton': {
    '1': '1',
    '1.L': '1',
    '1.R': '1',
    '1A': '1',
    '1B': '1',
    'A': '1',
    'PIN1': '1',
    'PIN_1': '1',
    'P1': '1',
    'IN': '1',
    'LEFT': '1',
    '+': '1',
    'VCC': '1',
    '2': '2',
    '2.L': '2',
    '2.R': '2',
    '2A': '2',
    '2B': '2',
    'B': '2',
    'PIN2': '2',
    'PIN_2': '2',
    'P2': '2',
    'OUT': '2',
    'SIG': '2',
    'RIGHT': '2',
    '-': '2',
    'GND': '2',
    '3': '2',
    '4': '2'
  },
  'wokwi-servo': {
    'GND': 'GND',
    '-': 'GND',
    'GROUND': 'GND',
    '0V': 'GND',
    '1': 'GND',
    'BROWN': 'GND',
    'BLACK': 'GND',
    'V+': 'V+',
    'VCC': 'V+',
    '5V': 'V+',
    '+': 'V+',
    'POWER': 'V+',
    'V': 'V+',
    'VIN': 'V+',
    '2': 'V+',
    'RED': 'V+',
    'PWM': 'PWM',
    'SIG': 'PWM',
    'SIGNAL': 'PWM',
    'OUT': 'PWM',
    'IN': 'PWM',
    'DATA': 'PWM',
    'PULSE': 'PWM',
    'CTRL': 'PWM',
    '3': 'PWM',
    'ORANGE': 'PWM',
    'YELLOW': 'PWM'
  },
  'wokwi-hc-sr04': {
    'VCC': 'VCC',
    '5V': 'VCC',
    'V+': 'VCC',
    '+': 'VCC',
    'POWER': 'VCC',
    '1': 'VCC',
    'TRIG': 'TRIG',
    'TRIGGER': 'TRIG',
    'TRG': 'TRIG',
    'T': 'TRIG',
    '2': 'TRIG',
    'ECHO': 'ECHO',
    'ECH': 'ECHO',
    'E': 'ECHO',
    'OUT': 'ECHO',
    'SIG': 'ECHO',
    '3': 'ECHO',
    'GND': 'GND',
    '-': 'GND',
    'GROUND': 'GND',
    '0V': 'GND',
    '4': 'GND'
  },
  'wokwi-potentiometer': {
    'GND': 'GND',
    '1': 'GND',
    'A': 'GND',
    '-': 'GND',
    'PIN1': 'GND',
    'PIN_1': 'GND',
    'P1': 'GND',
    'LEFT': 'GND',
    'GROUND': 'GND',
    'SIG': 'SIG',
    '2': 'SIG',
    'B': 'SIG',
    'OUT': 'SIG',
    'WIPER': 'SIG',
    'AO': 'SIG',
    'A0': 'SIG',
    'SIGNAL': 'SIG',
    'IN': 'SIG',
    'PIN2': 'SIG',
    'PIN_2': 'SIG',
    'P2': 'SIG',
    'MIDDLE': 'SIG',
    'CENTER': 'SIG',
    'VCC': 'VCC',
    '3': 'VCC',
    'C': 'VCC',
    '5V': 'VCC',
    'V+': 'VCC',
    '+': 'VCC',
    'PIN3': 'VCC',
    'PIN_3': 'VCC',
    'P3': 'VCC',
    'RIGHT': 'VCC',
    'POWER': 'VCC'
  },
  'wokwi-hc-05': {
    'VCC': 'VCC', '5V': 'VCC', '+': 'VCC', 'POWER': 'VCC', '1': 'VCC',
    'GND': 'GND', '-': 'GND', '0V': 'GND', 'GROUND': 'GND', '2': 'GND',
    'TXD': 'TXD', 'TX': 'TXD', 'T': 'TXD', 'TXO': 'TXD', 'DOUT': 'TXD', '3': 'TXD',
    'RXD': 'RXD', 'RX': 'RXD', 'R': 'RXD', 'RXI': 'RXD', 'DIN': 'RXD', '4': 'RXD',
    'STATE': 'STATE', 'ST': 'STATE', '5': 'STATE',
    'EN': 'EN', 'ENABLE': 'EN', 'KEY': 'EN', '6': 'EN'
  },
  'wokwi-hc-06': {
    'VCC': 'VCC', '5V': 'VCC', '+': 'VCC', 'POWER': 'VCC', '1': 'VCC',
    'GND': 'GND', '-': 'GND', '0V': 'GND', 'GROUND': 'GND', '2': 'GND',
    'TXD': 'TXD', 'TX': 'TXD', 'T': 'TXD', 'TXO': 'TXD', 'DOUT': 'TXD', '3': 'TXD',
    'RXD': 'RXD', 'RX': 'RXD', 'R': 'RXD', 'RXI': 'RXD', 'DIN': 'RXD', '4': 'RXD'
  },
  'wokwi-l293d': {
    'EN1': 'EN1', 'ENABLE1': 'EN1', 'EN12': 'EN1', '1,2EN': 'EN1', '1-2EN': 'EN1', '1': 'EN1',
    'IN1': 'IN1', 'INPUT1': 'IN1', '1A': 'IN1', '2': 'IN1',
    'OUT1': 'OUT1', 'OUTPUT1': 'OUT1', '1Y': 'OUT1', '3': 'OUT1',
    'GND': 'GND', 'GND1': 'GND', 'GND2': 'GND', 'GND3': 'GND', 'GND4': 'GND', '4': 'GND', '5': 'GND', '12': 'GND', '13': 'GND',
    'OUT2': 'OUT2', 'OUTPUT2': 'OUT2', '2Y': 'OUT2', '6': 'OUT2',
    'IN2': 'IN2', 'INPUT2': 'IN2', '2A': 'IN2', '7': 'IN2',
    'VCC2': 'VCC2', 'VC2': 'VCC2', 'VIN': 'VCC2', 'VM': 'VCC2', 'VS': 'VCC2', 'MOTOR_VCC': 'VCC2', '12V': 'VCC2', '9V': 'VCC2', '8': 'VCC2',
    'EN2': 'EN2', 'ENABLE2': 'EN2', 'EN34': 'EN2', '3,4EN': 'EN2', '3-4EN': 'EN2', '9': 'EN2',
    'IN3': 'IN3', 'INPUT3': 'IN3', '3A': 'IN3', '10': 'IN3',
    'OUT3': 'OUT3', 'OUTPUT3': 'OUT3', '3Y': 'OUT3', '11': 'OUT3',
    'OUT4': 'OUT4', 'OUTPUT4': 'OUT4', '4Y': 'OUT4', '14': 'OUT4',
    'IN4': 'IN4', 'INPUT4': 'IN4', '4A': 'IN4', '15': 'IN4',
    'VCC1': 'VCC1', 'VC1': 'VCC1', 'VCC': 'VCC1', '5V': 'VCC1', 'LOGIC_VCC': 'VCC1', '16': 'VCC1'
  },
  'wokwi-l298n': {
    'VCC': 'VCC', '12V': 'VCC', 'VIN': 'VCC', 'V+': 'VCC', 'POWER': 'VCC', '1': 'VCC',
    'GND': 'GND', '-': 'GND', '0V': 'GND', 'GROUND': 'GND', '2': 'GND',
    '5V': '5V', 'VCC_5V': '5V', 'LOGIC_5V': '5V', '3': '5V',
    'ENA': 'ENA', 'EN1': 'ENA', 'ENABLE_A': 'ENA',
    'IN1': 'IN1', 'IN2': 'IN2', 'IN3': 'IN3', 'IN4': 'IN4',
    'ENB': 'ENB', 'EN2': 'ENB', 'ENABLE_B': 'ENB',
    'OUT1': 'OUT1', 'OUT2': 'OUT2', 'OUT3': 'OUT3', 'OUT4': 'OUT4'
  },
  'wokwi-dc-motor': {
    '1': '1', '+': '1', 'POS': '1', 'PIN1': '1', 'IN1': '1', 'A': '1', 'RED': '1',
    '2': '2', '-': '2', 'NEG': '2', 'PIN2': '2', 'IN2': '2', 'B': '2', 'BLACK': '2', 'GND': '2'
  },
  'wokwi-rgb-led': {
    'R': 'R', 'RED': 'R', '1': 'R', 'ANODE_RED': 'R',
    'COM': 'COM', 'COMMON': 'COM', 'C': 'COM', 'A': 'COM', 'CATHODE': 'COM', 'KATOT': 'COM', 'GND': 'COM', '2': 'COM', '-': 'COM',
    'G': 'G', 'GREEN': 'G', '3': 'G', 'ANODE_GREEN': 'G',
    'B': 'B', 'BLUE': 'B', '4': 'B', 'ANODE_BLUE': 'B'
  },
  'wokwi-pir-motion-sensor': {
    'VCC': 'VCC', '5V': 'VCC', '+': 'VCC', 'POWER': 'VCC', '1': 'VCC',
    'OUT': 'OUT', 'SIG': 'OUT', 'SIGNAL': 'OUT', 'D': 'OUT', '2': 'OUT',
    'GND': 'GND', '-': 'GND', '0V': 'GND', 'GROUND': 'GND', '3': 'GND'
  },
  'wokwi-dht22': {
    'VCC': 'VCC', '5V': 'VCC', '+': 'VCC', 'POWER': 'VCC', '1': 'VCC',
    'SDA': 'SDA', 'DATA': 'SDA', 'SIG': 'SDA', 'OUT': 'SDA', '2': 'SDA',
    'NC': 'NC', '3': 'NC',
    'GND': 'GND', '-': 'GND', 'GROUND': 'GND', '4': 'GND'
  },
  'wokwi-analog-joystick': {
    'GND': 'GND', '-': 'GND', 'GROUND': 'GND', '1': 'GND',
    '5V': 'VCC', 'VCC': 'VCC', '+': 'VCC', '2': 'VCC',
    'HORZ': 'HORZ', 'VRX': 'HORZ', 'X': 'HORZ', '3': 'HORZ',
    'VERT': 'VERT', 'VRY': 'VERT', 'Y': 'VERT', '4': 'VERT',
    'SEL': 'SEL', 'SW': 'SEL', 'KEY': 'SEL', 'BTN': 'SEL', 'BUTTON': 'SEL', '5': 'SEL'
  },
  'wokwi-relay-module': {
    'VCC': 'VCC', '5V': 'VCC', '+': 'VCC', 'POWER': 'VCC', '1': 'VCC',
    'GND': 'GND', '-': 'GND', 'GROUND': 'GND', '2': 'GND',
    'IN': 'IN', 'SIG': 'IN', 'SIGNAL': 'IN', 'CTRL': 'IN', 'DATA': 'IN', '3': 'IN',
    'NO': 'NO', 'COM': 'COM', 'NC': 'NC'
  },
  'wokwi-lcd1602': {
    'GND': 'GND', '-': 'GND', '1': 'GND',
    'VCC': 'VCC', '5V': 'VCC', '+': 'VCC', '2': 'VCC',
    'SDA': 'SDA', '3': 'SDA',
    'SCL': 'SCL', '4': 'SCL'
  },
  'wokwi-ssd1306': {
    'GND': 'GND', '-': 'GND', '1': 'GND',
    'VCC': 'VCC', '5V': 'VCC', '3.3V': 'VCC', '+': 'VCC', '2': 'VCC',
    'SCL': 'SCL', 'SCK': 'SCL', 'CLK': 'SCL', '3': 'SCL',
    'SDA': 'SDA', 'MOSI': 'SDA', 'DATA': 'SDA', '4': 'SDA'
  },
  'wokwi-soil-moisture-sensor': {
    'VCC': 'VCC', '5V': 'VCC', '+': 'VCC', '1': 'VCC',
    'GND': 'GND', '-': 'GND', '2': 'GND',
    'DO': 'DO', 'D0': 'DO', 'DIGITAL': 'DO', '3': 'DO',
    'AO': 'AO', 'A0': 'AO', 'SIG': 'AO', 'OUT': 'AO', 'ANALOG': 'AO', '4': 'AO'
  },
  'wokwi-rain-sensor': {
    'VCC': 'VCC', '5V': 'VCC', '+': 'VCC', '1': 'VCC',
    'GND': 'GND', '-': 'GND', '2': 'GND',
    'DO': 'DO', 'D0': 'DO', 'DIGITAL': 'DO', '3': 'DO',
    'AO': 'AO', 'A0': 'AO', 'SIG': 'AO', 'OUT': 'AO', 'ANALOG': 'AO', '4': 'AO'
  },
  'wokwi-water-sensor': {
    'VCC': 'VCC', '5V': 'VCC', '+': 'VCC', '1': 'VCC',
    'GND': 'GND', '-': 'GND', '2': 'GND',
    'AO': 'AO', 'A0': 'AO', 'SIG': 'AO', 'OUT': 'AO', 'ANALOG': 'AO', '3': 'AO'
  },
  'wokwi-gas-sensor': {
    'VCC': 'VCC', '5V': 'VCC', '+': 'VCC', '1': 'VCC',
    'GND': 'GND', '-': 'GND', '2': 'GND',
    'DO': 'DO', 'D0': 'DO', '3': 'DO',
    'AO': 'AO', 'A0': 'AO', 'SIG': 'AO', 'OUT': 'AO', '4': 'AO'
  },
  'wokwi-flame-sensor': {
    'VCC': 'VCC', '5V': 'VCC', '+': 'VCC', '1': 'VCC',
    'GND': 'GND', '-': 'GND', '2': 'GND',
    'DO': 'DO', 'D0': 'DO', '3': 'DO',
    'AO': 'AO', 'A0': 'AO', 'SIG': 'AO', 'OUT': 'AO', '4': 'AO'
  },
  'wokwi-small-sound-sensor': {
    'VCC': 'VCC', '5V': 'VCC', '+': 'VCC', '1': 'VCC',
    'GND': 'GND', '-': 'GND', '2': 'GND',
    'DO': 'DO', 'D0': 'DO', '3': 'DO',
    'AO': 'AO', 'A0': 'AO', 'SIG': 'AO', 'OUT': 'AO', '4': 'AO'
  },
  'wokwi-ir-receiver': {
    'OUT': 'OUT', 'SIG': 'OUT', 'DATA': 'OUT', 'DAT': 'OUT', '1': 'OUT',
    'GND': 'GND', '-': 'GND', '2': 'GND',
    'VCC': 'VCC', '5V': 'VCC', '+': 'VCC', '3': 'VCC'
  },
  'wokwi-ntc-temperature-sensor': {
    '1': '1', 'A': '1', 'VCC': '1',
    '2': '2', 'B': '2', 'GND': '2', 'SIG': '2'
  }
};

const GND_ALIASES = new Set([
  'GND',
  'GND.1',
  'GND.2',
  'GND.3',
  'GND1',
  'GND2',
  'GND3',
  'GROUND',
  '0V',
  '-',
  'VSS',
  'BN',
  'BP.-',
  'TOP--',
  'BOTTOM--'
]);

const POWER_5V_ALIASES = new Set([
  '5V',
  '+5V',
  '3.3V',
  '3V3',
  '+3.3V',
  'VCC',
  'V+',
  'VDD',
  '+',
  'VIN',
  'BP',
  'BP.+',
  'TOP-+',
  'BOTTOM-+'
]);

const BOARD_PREFIXES = new Set([
  'uno',
  'arduino',
  'board',
  'arduino-uno',
  'arduino_uno',
  'nano',
  'arduino-nano',
  'mega',
  'esp32',
  'breadboard',
  'bb'
]);

class UnionFind {
  private parent = new Map<string, string>();

  public add(x: string): void {
    if (!this.parent.has(x)) {
      this.parent.set(x, x);
    }
  }

  public find(x: string): string {
    if (!this.parent.has(x)) {
      this.parent.set(x, x);
      return x;
    }
    let root = this.parent.get(x)!;
    if (root !== x) {
      root = this.find(root);
      this.parent.set(x, root);
    }
    return root;
  }

  public union(a: string, b: string): void {
    const rootA = this.find(a);
    const rootB = this.find(b);
    if (rootA !== rootB) {
      this.parent.set(rootB, rootA);
    }
  }

  public getAllElements(): string[] {
    return Array.from(this.parent.keys());
  }
}

/**
 * Ham bağlantılarda bir bileşenin hangi pin isimleriyle kullanıldığını toplar.
 */
function collectRawPinsForComponent(compId: string, connections: NetlistConnection[]): string[] {
  const lowerId = compId.toLowerCase();
  const pins: string[] = [];
  for (const conn of connections) {
    const rawFrom = String((conn as any).from || (conn as any).from_pin || '').trim();
    const rawTo = String((conn as any).to || (conn as any).to_pin || '').trim();
    for (const ep of [rawFrom, rawTo]) {
      const dotIdx = ep.indexOf('.');
      if (dotIdx !== -1) {
        const part = ep.slice(0, dotIdx).trim().toLowerCase();
        const pin = ep.slice(dotIdx + 1).trim().toUpperCase();
        if (part === lowerId) {
          pins.push(pin);
        }
      }
    }
  }
  return pins;
}

/**
 * Netlist'i normalize eder ve Union-Find ile elektriksel net'leri çıkarır.
 */
export function normalizeNetlist(rawNetlist: CircuitNetlist): NormalizationResult {
  const warnings: string[] = [];
  const errors: string[] = [];

  if (!rawNetlist || !Array.isArray(rawNetlist.components)) {
    return {
      netlist: { board: 'arduino-uno', components: [], connections: [] },
      nets: [],
      warnings: [],
      errors: ['Geçersiz netlist şeması: components dizisi bulunamadı.']
    };
  }

  const rawConnections = Array.isArray(rawNetlist.connections) ? rawNetlist.connections : [];

  // 1. Bileşenleri normalize et
  const normalizedComponents: NetlistComponent[] = [];
  const compById = new Map<string, NetlistComponent>();
  const compIdLowerMap = new Map<string, string>();

  for (const rawComp of rawNetlist.components) {
    const id = String(rawComp.id || '').trim();
    if (!id) {
      warnings.push('Kimliği (id) boş olan bir bileşen atlandı.');
      continue;
    }

    const rawType = String(rawComp.type || '').trim();
    const lowerType = rawType.toLowerCase();
    const lowerId = id.toLowerCase();

    // LLM yanlışlıkla Arduino kartını veya Breadboard'u components listesine eklediyse atla
    if (
      BOARD_PREFIXES.has(lowerId) ||
      lowerType.includes('arduino') ||
      lowerType.includes('breadboard') ||
      lowerType === 'esp32'
    ) {
      warnings.push(`Ana kart/breadboard bileşen listesinden çıkarıldı: '${id}' (${rawType}).`);
      continue;
    }

    const aliasEntry = COMPONENT_TYPE_ALIASES[lowerType];

    let canonicalType = aliasEntry ? aliasEntry.type : rawType;
    const props: Record<string, any> = {
      ...(aliasEntry?.defaultProps || {}),
      ...(rawComp.props || {})
    };

    // LDR için akıllı tip netleştirmesi (2 bacaklı vs 4 pinli modül)
    if (
      lowerType === 'ldr' ||
      canonicalType === 'wokwi-photoresistor' ||
      canonicalType === 'wokwi-photoresistor-sensor'
    ) {
      const usedPins = collectRawPinsForComponent(id, rawConnections);
      const hasModulePins = usedPins.some(p =>
        ['VCC', 'AO', 'DO', 'OUT', 'SIG', 'A0', 'D0', 'AOUT', 'DOUT'].includes(p)
      );
      const hasOnlyTwoPinTerms =
        usedPins.length > 0 &&
        usedPins.every(p => ['1', '2', 'A', 'B', 'PIN1', 'PIN2', 'PIN_1', 'PIN_2'].includes(p));

      if (lowerType === 'ldr') {
        canonicalType = hasModulePins ? 'wokwi-photoresistor-sensor' : 'wokwi-photoresistor';
        warnings.push(`Bileşen tipi normalize edildi: '${id}' (${rawType} → ${canonicalType}).`);
      } else if (canonicalType === 'wokwi-photoresistor-sensor' && hasOnlyTwoPinTerms) {
        canonicalType = 'wokwi-photoresistor';
        warnings.push(
          `'${id}' bileşeni 2 bacaklı (1/2) bağlandığı için tipi 'wokwi-photoresistor' olarak normalize edildi.`
        );
      } else if (canonicalType === 'wokwi-photoresistor' && hasModulePins && usedPins.includes('GND')) {
        canonicalType = 'wokwi-photoresistor-sensor';
        warnings.push(
          `'${id}' bileşeni modül pinleri (VCC/GND/AO) kullandığı için tipi 'wokwi-photoresistor-sensor' olarak normalize edildi.`
        );
      }
    } else if (aliasEntry && rawType !== canonicalType) {
      warnings.push(`Bileşen tipi normalize edildi: '${id}' (${rawType} → ${canonicalType}).`);
    }

    const comp: NetlistComponent = {
      id,
      type: canonicalType,
      props,
      label: rawComp.label || id
    };

    normalizedComponents.push(comp);
    compById.set(id, comp);
    compIdLowerMap.set(id.toLowerCase(), id);
  }

  // Yardımcı: Bileşen ID çözümleme (birebir, küçük harf veya tekil tip eşleşmesi)
  function resolveComponent(partRaw: string): NetlistComponent | undefined {
    const clean = partRaw.trim();
    if (compById.has(clean)) return compById.get(clean);
    const lower = clean.toLowerCase();
    if (compIdLowerMap.has(lower)) {
      return compById.get(compIdLowerMap.get(lower)!);
    }
    // Eğer LLM 'servo.PWM' yazdıysa ve devrede tek bir 'servo1' varsa
    const prefixMatches = normalizedComponents.filter(
      c => c.id.toLowerCase().startsWith(lower) || lower.startsWith(c.id.toLowerCase())
    );
    if (prefixMatches.length === 1) {
      return prefixMatches[0];
    }
    const aliasType = COMPONENT_TYPE_ALIASES[lower]?.type;
    if (aliasType) {
      const typeMatches = normalizedComponents.filter(c => c.type === aliasType);
      if (typeMatches.length === 1) {
        return typeMatches[0];
      }
    }
    return undefined;
  }

  // Yardımcı: Tek bir uç noktayı (endpoint) normalize et
  function normalizeEndpoint(rawEp: string): {
    valid: boolean;
    canonical: string;
    kind: 'power' | 'arduino' | 'component';
    reason?: string;
  } {
    const ep = String(rawEp || '').trim();
    if (!ep) {
      return { valid: false, canonical: '', kind: 'component', reason: 'Boş bağlantı ucu.' };
    }

    const upperEp = ep.toUpperCase();

    // Doğrudan güç hattı kontrolü (örn: GND, 5V, GND.1, VCC)
    if (GND_ALIASES.has(upperEp)) {
      return { valid: true, canonical: 'GND', kind: 'power' };
    }
    if (POWER_5V_ALIASES.has(upperEp)) {
      return { valid: true, canonical: '5V', kind: 'power' };
    }

    const dotIdx = ep.indexOf('.');
    if (dotIdx !== -1) {
      const partRaw = ep.slice(0, dotIdx).trim();
      const pinRaw = ep.slice(dotIdx + 1).trim();
      const partLower = partRaw.toLowerCase();
      const pinUpper = pinRaw.toUpperCase();

      // 1) Önce bilinen bir bileşen ID'si mi kontrol et (BOARD_PREFIXES değilse)
      if (!BOARD_PREFIXES.has(partLower)) {
        const comp = resolveComponent(partRaw);
        if (comp) {
          const pinMap = PIN_ALIASES_BY_TYPE[comp.type];
          if (!pinMap) {
            // Desteklenmeyen bileşen tipi
            return {
              valid: true,
              canonical: `${comp.id}.${pinUpper}`,
              kind: 'component'
            };
          }
          const mappedPin = pinMap[pinUpper];
          if (mappedPin) {
            return {
              valid: true,
              canonical: `${comp.id}.${mappedPin}`,
              kind: 'component'
            };
          }
          return {
            valid: false,
            canonical: ep,
            kind: 'component',
            reason: `'${comp.id}' (${comp.type}) bileşeninde geçersiz pin adı: '${pinRaw}'.`
          };
        }
      }

      // 2) Arduino / Board öneki (uno.13, arduino.D13, uno.GND, uno.5V vb.)
      if (BOARD_PREFIXES.has(partLower)) {
        if (GND_ALIASES.has(pinUpper)) {
          return { valid: true, canonical: 'GND', kind: 'power' };
        }
        if (POWER_5V_ALIASES.has(pinUpper)) {
          return { valid: true, canonical: '5V', kind: 'power' };
        }

        const digMatch = pinUpper.match(/^(?:D|PIN_?|DIGITAL_?|GPIO_?)?([0-9]|1[0-3])$/);
        if (digMatch) {
          return { valid: true, canonical: `uno.D${digMatch[1]}`, kind: 'arduino' };
        }

        const anaMatch = pinUpper.match(/^(?:A|ANALOG_?|ADC_?)([0-5])$/);
        if (anaMatch) {
          return { valid: true, canonical: `uno.A${anaMatch[1]}`, kind: 'arduino' };
        }

        const numVal = parseInt(pinUpper, 10);
        if (!isNaN(numVal) && numVal >= 14 && numVal <= 19) {
          return { valid: true, canonical: `uno.A${numVal - 14}`, kind: 'arduino' };
        }

        return {
          valid: false,
          canonical: ep,
          kind: 'arduino',
          reason: `Geçersiz Arduino pini: '${ep}'.`
        };
      }

      return {
        valid: false,
        canonical: ep,
        kind: 'component',
        reason: `Bilinmeyen bileşen veya pin: '${ep}'.`
      };
    }

    // Nokta içermeyen tekil ifadeler: D13, 13, A0, PIN13 vb.
    const digBare = upperEp.match(/^(?:D|PIN_?|DIGITAL_?|GPIO_?)?([0-9]|1[0-3])$/);
    if (digBare) {
      return { valid: true, canonical: `uno.D${digBare[1]}`, kind: 'arduino' };
    }

    const anaBare = upperEp.match(/^(?:A|ANALOG_?|ADC_?)([0-5])$/);
    if (anaBare) {
      return { valid: true, canonical: `uno.A${anaBare[1]}`, kind: 'arduino' };
    }

    return {
      valid: false,
      canonical: ep,
      kind: 'component',
      reason: `Tanınmayan bağlantı ucu: '${ep}'.`
    };
  }

  // 2. Bağlantıları normalize et
  const normalizedConnections: NetlistConnection[] = [];
  const seenConnections = new Set<string>();

  for (const rawConn of rawConnections) {
    const rawFrom = String((rawConn as any).from || (rawConn as any).from_pin || '').trim();
    const rawTo = String((rawConn as any).to || (rawConn as any).to_pin || '').trim();

    const normFrom = normalizeEndpoint(rawFrom);
    const normTo = normalizeEndpoint(rawTo);

    if (!normFrom.valid) {
      warnings.push(`Geçersiz bağlantı atlandı (${rawFrom} -> ${rawTo}): ${normFrom.reason}`);
      continue;
    }
    if (!normTo.valid) {
      warnings.push(`Geçersiz bağlantı atlandı (${rawFrom} -> ${rawTo}): ${normTo.reason}`);
      continue;
    }

    let finalFrom = normFrom.canonical;
    let finalTo = normTo.canonical;
    let fromKind = normFrom.kind;
    let toKind = normTo.kind;

    if (rawFrom !== finalFrom) {
      warnings.push(`Pin/uç normalize edildi: '${rawFrom}' → '${finalFrom}'.`);
    }
    if (rawTo !== finalTo) {
      warnings.push(`Pin/uç normalize edildi: '${rawTo}' → '${finalTo}'.`);
    }

    // Aynı uca kendi kendine bağlantı kontrolü
    if (finalFrom === finalTo) {
      warnings.push(`Kendi kendine bağlantı atlandı: '${finalFrom} -> ${finalTo}'.`);
      continue;
    }

    // 5V <-> GND doğrudan kısa devre kontrolü
    if (
      (finalFrom === '5V' && finalTo === 'GND') ||
      (finalFrom === 'GND' && finalTo === '5V')
    ) {
      errors.push('Kritik Kısa Devre Hatası: 5V ve GND doğrudan birbirine bağlanmış!');
      continue;
    }

    // Yön normalizasyonu: Güç (GND / 5V) her zaman 'to' tarafında olmalı
    if (fromKind === 'power' && toKind !== 'power') {
      const temp = finalFrom;
      finalFrom = finalTo;
      finalTo = temp;
      const tempKind = fromKind;
      fromKind = toKind;
      toKind = tempKind;
      warnings.push(`Güç bağlantısı yönü normalize edildi: '${rawFrom} -> ${rawTo}' → '${finalFrom} -> ${finalTo}'.`);
    }

    // Tekrarlanan bağlantıları ele
    const pairKey =
      finalTo === 'GND' || finalTo === '5V'
        ? `${finalFrom}=>${finalTo}`
        : [finalFrom, finalTo].sort().join('<=>');

    if (seenConnections.has(pairKey)) {
      warnings.push(`Tekrarlanan bağlantı atlandı: '${finalFrom} -> ${finalTo}'.`);
      continue;
    }
    seenConnections.add(pairKey);

    normalizedConnections.push({
      from: finalFrom,
      to: finalTo,
      color: rawConn.color
    });
  }

  // 3. Union-Find ile Elektriksel Düğümleri (ElectricalNet) Çıkar
  const uf = new UnionFind();
  const netColors = new Map<string, string>();
  const powerByEndpoint = new Map<string, Set<'GND' | '5V'>>();

  for (const conn of normalizedConnections) {
    const { from, to, color } = conn;
    const isToPower = to === 'GND' || to === '5V';

    if (isToPower) {
      uf.add(from);
      if (!powerByEndpoint.has(from)) {
        powerByEndpoint.set(from, new Set());
      }
      powerByEndpoint.get(from)!.add(to as 'GND' | '5V');
      if (color && !netColors.has(from)) {
        netColors.set(from, color);
      }
    } else {
      uf.add(from);
      uf.add(to);
      uf.union(from, to);
      if (color) {
        if (!netColors.has(from)) netColors.set(from, color);
        if (!netColors.has(to)) netColors.set(to, color);
      }
    }
  }

  // Kök düğümlere göre grupla
  const groups = new Map<
    string,
    {
      componentPins: string[];
      arduinoPins: string[];
      powerRails: Set<'GND' | '5V'>;
      color?: string;
    }
  >();

  for (const ep of uf.getAllElements()) {
    const root = uf.find(ep);
    if (!groups.has(root)) {
      groups.set(root, {
        componentPins: [],
        arduinoPins: [],
        powerRails: new Set(),
        color: undefined
      });
    }
    const g = groups.get(root)!;
    if (ep.startsWith('uno.')) {
      if (!g.arduinoPins.includes(ep)) g.arduinoPins.push(ep);
    } else if (ep !== 'GND' && ep !== '5V') {
      if (!g.componentPins.includes(ep)) g.componentPins.push(ep);
    }

    const pSet = powerByEndpoint.get(ep);
    if (pSet) {
      for (const p of pSet) g.powerRails.add(p);
    }

    if (!g.color && netColors.has(ep)) {
      g.color = netColors.get(ep);
    }
  }

  const nets: ElectricalNet[] = [];
  let netCounter = 1;

  for (const g of groups.values()) {
    if (g.powerRails.has('GND') && g.powerRails.has('5V')) {
      errors.push(
        `Kısa Devre Hatası: [${g.componentPins.concat(g.arduinoPins).join(', ')}] düğümü üzerinden 5V ve GND birbirine bağlanmış!`
      );
    }

    let powerRail: 'GND' | '5V' | undefined;
    if (g.powerRails.has('GND')) powerRail = 'GND';
    else if (g.powerRails.has('5V')) powerRail = '5V';

    nets.push({
      id: `net-${netCounter++}`,
      componentPins: g.componentPins,
      arduinoPins: g.arduinoPins,
      powerRail,
      color: g.color
    });
  }

  const normalizedNetlist: CircuitNetlist = {
    board: rawNetlist.board || 'arduino-uno',
    components: normalizedComponents,
    connections: normalizedConnections
  };

  return {
    netlist: normalizedNetlist,
    nets,
    warnings,
    errors
  };
}

/**
 * Standart ve "Kötü LLM Çıktısı" Test Senaryoları:
 * - scenarioA: 4 Pinli LDR Modülü (KY-018) + LED + Direnç
 * - scenarioA_discrete: 2 Bacaklı Klasik Foto-direnç + LED + Dirençler (Gerilim Bölücü)
 * - scenarioB: 3 LED'li Trafik Lambası
 * - scenarioC: Buton + Servo Motor Devresi
 * - scenarioD_messyAliasesAndReverseGnd: Ters yönlü GND/5V, uno.13 / led1.anode / r1.A / ldr1.OUT alias'ları
 * - scenarioE_cathodeResistor: Direnç LED'in katot (C) tarafında (led1.C -> r1.1 ve led2.C -> r2.2)
 * - scenarioF_voltageDividerAliases: 3 uçlu gerilim bölücü net (ldr1.2 + r1.A + A0)
 * - scenarioG_trafficLightWithButtonOverflow: 3 LED Trafik Lambası + Buton + Pull-down (Üst yarıdan alt yarıya F-J geçiş)
 * - scenarioH_servoAndUltrasonic: Servo + HC-SR04 birlikte (Off-board dikey dock sıralaması ve ray sütunu tahsisi)
 * - scenarioI_potentiometerAndLed: 3 Pinli Potansiyometre (GND, SIG, VCC) + LED + Direnç
 */

import type { CircuitNetlist } from './types';
import { compileNetlistToBreadboard } from './index';

// Senaryo A1: 4 Pinli LDR Modülü (KY-018) + LED + Direnç
export const scenarioA: CircuitNetlist = {
  board: 'arduino-uno',
  components: [
    { id: 'r1', type: 'wokwi-resistor', props: { value: '220' }, label: '220Ω Direnç' },
    { id: 'led1', type: 'wokwi-led', props: { color: 'red' }, label: 'Kırmızı LED' },
    { id: 'ldr1', type: 'wokwi-photoresistor-sensor', label: '4 Pin LDR Modülü' }
  ],
  connections: [
    { from: 'uno.D13', to: 'r1.1', color: 'orange' },
    { from: 'r1.2', to: 'led1.A', color: 'red' },
    { from: 'led1.C', to: 'GND', color: 'black' },
    { from: 'ldr1.VCC', to: '5V', color: 'red' },
    { from: 'ldr1.GND', to: 'GND', color: 'black' },
    { from: 'ldr1.AO', to: 'uno.A0', color: 'green' }
  ]
};

// Senaryo A2: 2 Bacaklı Klasik Foto-direnç + LED + Dirençler (Gerilim Bölücü)
export const scenarioA_discrete: CircuitNetlist = {
  board: 'arduino-uno',
  components: [
    { id: 'r1', type: 'wokwi-resistor', props: { value: '220' }, label: '220Ω Direnç' },
    { id: 'led1', type: 'wokwi-led', props: { color: 'red' }, label: 'Kırmızı LED' },
    { id: 'ldr1', type: 'wokwi-photoresistor', label: '2 Bacaklı LDR' },
    { id: 'r2', type: 'wokwi-resistor', props: { value: '10000' }, label: '10kΩ Direnç' }
  ],
  connections: [
    { from: 'uno.D13', to: 'r1.1', color: 'orange' },
    { from: 'r1.2', to: 'led1.A', color: 'red' },
    { from: 'led1.C', to: 'GND', color: 'black' },
    { from: 'ldr1.1', to: '5V', color: 'red' },
    { from: 'ldr1.2', to: 'uno.A0', color: 'green' },
    { from: 'ldr1.2', to: 'r2.1', color: 'green' },
    { from: 'r2.2', to: 'GND', color: 'black' }
  ]
};

// Senaryo B: 3 LED'li Trafik Lambası
export const scenarioB: CircuitNetlist = {
  board: 'arduino-uno',
  components: [
    { id: 'r1', type: 'wokwi-resistor', props: { value: '220' }, label: 'Kırmızı Direnç' },
    { id: 'led1', type: 'wokwi-led', props: { color: 'red' }, label: 'Kırmızı LED' },
    { id: 'r2', type: 'wokwi-resistor', props: { value: '220' }, label: 'Sarı Direnç' },
    { id: 'led2', type: 'wokwi-led', props: { color: 'yellow' }, label: 'Sarı LED' },
    { id: 'r3', type: 'wokwi-resistor', props: { value: '220' }, label: 'Yeşil Direnç' },
    { id: 'led3', type: 'wokwi-led', props: { color: 'green' }, label: 'Yeşil LED' }
  ],
  connections: [
    { from: 'uno.D12', to: 'r1.1', color: 'red' },
    { from: 'r1.2', to: 'led1.A', color: 'red' },
    { from: 'led1.C', to: 'GND', color: 'black' },
    { from: 'uno.D11', to: 'r2.1', color: 'yellow' },
    { from: 'r2.2', to: 'led2.A', color: 'yellow' },
    { from: 'led2.C', to: 'GND', color: 'black' },
    { from: 'uno.D10', to: 'r3.1', color: 'green' },
    { from: 'r3.2', to: 'led3.A', color: 'green' },
    { from: 'led3.C', to: 'GND', color: 'black' }
  ]
};

// Senaryo C: Buton + Servo Motor Devresi
export const scenarioC: CircuitNetlist = {
  board: 'arduino-uno',
  components: [
    { id: 'btn1', type: 'wokwi-pushbutton', props: { color: 'red' }, label: 'Başlat Butonu' },
    { id: 'r1', type: 'wokwi-resistor', props: { value: '10000' }, label: '10kΩ Pull-down Direnç' },
    { id: 'servo1', type: 'wokwi-servo', label: 'SG90 Servo Motor' }
  ],
  connections: [
    { from: 'btn1.1', to: '5V', color: 'red' },
    { from: 'btn1.2', to: 'uno.D2', color: 'blue' },
    { from: 'btn1.2', to: 'r1.1', color: 'blue' },
    { from: 'r1.2', to: 'GND', color: 'black' },
    { from: 'servo1.V+', to: '5V', color: 'red' },
    { from: 'servo1.GND', to: 'GND', color: 'black' },
    { from: 'servo1.PWM', to: 'uno.D9', color: 'orange' }
  ]
};

// Senaryo D (Kötü LLM Çıktısı 1): Ters yönlü GND/5V ve zengin pin/tip alias'ları
export const scenarioD_messyAliasesAndReverseGnd: CircuitNetlist = {
  board: 'arduino-uno',
  components: [
    { id: 'r1', type: 'resistor', props: { value: '220' }, label: '220Ω Direnç' },
    { id: 'led1', type: 'led', props: { color: 'red' }, label: 'Kırmızı LED' },
    { id: 'ldr1', type: 'ldr-sensor', label: 'Işık Modülü' }
  ],
  connections: [
    { from: 'uno.13', to: 'r1.A', color: 'orange' },
    { from: 'r1.B', to: 'led1.anode', color: 'red' },
    { from: 'GND', to: 'led1.cathode', color: 'black' },
    { from: 'uno.5V', to: 'ldr1.+', color: 'red' },
    { from: 'GND.1', to: 'ldr1.-', color: 'black' },
    { from: 'arduino.A0', to: 'ldr1.OUT', color: 'green' }
  ]
};

// Senaryo E (Kötü LLM Çıktısı 2): Direnç LED'in katot (C) tarafında ve r1.1/r1.2 ters
export const scenarioE_cathodeResistor: CircuitNetlist = {
  board: 'arduino-uno',
  components: [
    { id: 'led1', type: 'wokwi-led', props: { color: 'red' }, label: 'Kırmızı LED' },
    { id: 'r1', type: 'wokwi-resistor', props: { value: '220' }, label: 'Kırmızı Koruyucu Direnç' },
    { id: 'led2', type: 'wokwi-led', props: { color: 'green' }, label: 'Yeşil LED' },
    { id: 'r2', type: 'wokwi-resistor', props: { value: '220' }, label: 'Yeşil Koruyucu Direnç' }
  ],
  connections: [
    { from: 'D12', to: 'led1.+', color: 'red' },
    { from: 'led1.-', to: 'r1.1', color: 'orange' },
    { from: 'r1.2', to: 'uno.GND', color: 'black' },
    { from: 'r2.1', to: 'D11', color: 'green' },
    { from: 'r2.1', to: 'led2.anode', color: 'green' },
    { from: 'GND', to: 'r2.2', color: 'black' },
    { from: 'led2.cathode', to: 'GND', color: 'black' }
  ]
};

// Senaryo F (Kötü LLM Çıktısı 3): Gerilim bölücü 3 uçlu net (farklı yazımlarla)
export const scenarioF_voltageDividerAliases: CircuitNetlist = {
  board: 'arduino-uno',
  components: [
    { id: 'ldr1', type: 'ldr', label: 'Klasik LDR' },
    { id: 'r1', type: 'resistor_10k', label: '10kΩ Direnç' },
    { id: 'r2', type: 'resistor_220', label: '220Ω Direnç' },
    { id: 'led1', type: 'led_yellow', label: 'Sarı Gece Lambası' }
  ],
  connections: [
    { from: '5V', to: 'ldr1.1', color: 'red' },
    { from: 'ldr1.2', to: 'r1.A', color: 'green' },
    { from: 'r1.A', to: 'A0', color: 'green' },
    { from: 'GND', to: 'r1.B', color: 'black' },
    { from: 'arduino.13', to: 'r2.1', color: 'orange' },
    { from: 'led1.A', to: 'r2.2', color: 'yellow' },
    { from: 'uno.GND', to: 'led1.C', color: 'black' }
  ]
};

// Senaryo G (Kötü LLM Çıktısı 4): 3 LED Trafik Lambası + Yaya Butonu + Pull-down Direnç (Taşma -> Alt Yarı F-J)
export const scenarioG_trafficLightWithButtonOverflow: CircuitNetlist = {
  board: 'arduino-uno',
  components: [
    { id: 'r1', type: 'wokwi-resistor', props: { value: '220' }, label: 'Kırmızı Direnç' },
    { id: 'led1', type: 'wokwi-led', props: { color: 'red' }, label: 'Kırmızı LED' },
    { id: 'r2', type: 'wokwi-resistor', props: { value: '220' }, label: 'Sarı Direnç' },
    { id: 'led2', type: 'wokwi-led', props: { color: 'yellow' }, label: 'Sarı LED' },
    { id: 'r3', type: 'wokwi-resistor', props: { value: '220' }, label: 'Yeşil Direnç' },
    { id: 'led3', type: 'wokwi-led', props: { color: 'green' }, label: 'Yeşil LED' },
    { id: 'btn1', type: 'button', props: { color: 'blue' }, label: 'Yaya Butonu' },
    { id: 'r4', type: 'resistor_10k', label: '10kΩ Pull-down' }
  ],
  connections: [
    { from: 'uno.D12', to: 'r1.1', color: 'red' },
    { from: 'r1.2', to: 'led1.A', color: 'red' },
    { from: 'led1.C', to: 'GND', color: 'black' },
    { from: 'uno.D11', to: 'r2.1', color: 'yellow' },
    { from: 'r2.2', to: 'led2.A', color: 'yellow' },
    { from: 'led2.C', to: 'GND', color: 'black' },
    { from: 'uno.D10', to: 'r3.1', color: 'green' },
    { from: 'r3.2', to: 'led3.A', color: 'green' },
    { from: 'led3.C', to: 'GND', color: 'black' },
    { from: '5V', to: 'btn1.1.l', color: 'red' },
    { from: 'btn1.2.r', to: 'D2', color: 'blue' },
    { from: 'r4.1', to: 'btn1.2.r', color: 'blue' },
    { from: 'GND', to: 'r4.2', color: 'black' }
  ]
};

// Senaryo H (Kötü LLM Çıktısı 5): Servo + HC-SR04 Birlikte + Buzzer (Çoklu Off-Board Modül)
export const scenarioH_servoAndUltrasonic: CircuitNetlist = {
  board: 'arduino-uno',
  components: [
    { id: 'servo1', type: 'servo', label: 'Kapı Servosu' },
    { id: 'hcsr1', type: 'hc-sr04', label: 'Mesafe Radarı' },
    { id: 'buzzer1', type: 'buzzer', label: 'Alarm Buzzer' }
  ],
  connections: [
    { from: 'servo1.VCC', to: 'uno.5V', color: 'red' },
    { from: 'GND', to: 'servo1.GND', color: 'black' },
    { from: 'servo1.SIG', to: 'uno.9', color: 'orange' },
    { from: '5V', to: 'hcsr1.VCC', color: 'red' },
    { from: 'hcsr1.GND', to: 'uno.GND.1', color: 'black' },
    { from: 'hcsr1.TRIG', to: 'D10', color: 'blue' },
    { from: 'arduino.D11', to: 'hcsr1.ECHO', color: 'green' },
    { from: 'buzzer1.+', to: 'D8', color: 'purple' },
    { from: 'buzzer1.-', to: 'GND', color: 'black' }
  ]
};

// Senaryo I (Kötü LLM Çıktısı 6): 3 Pinli Potansiyometre + LED + Direnç
export const scenarioI_potentiometerAndLed: CircuitNetlist = {
  board: 'arduino-uno',
  components: [
    { id: 'pot1', type: 'potentiometer', label: '10kΩ Potansiyometre' },
    { id: 'r1', type: 'wokwi-resistor', props: { value: '220' }, label: '220Ω Direnç' },
    { id: 'led1', type: 'wokwi-led', props: { color: 'blue' }, label: 'Mavi LED' }
  ],
  connections: [
    { from: 'pot1.1', to: 'GND', color: 'black' },
    { from: 'pot1.2', to: 'A1', color: 'green' },
    { from: '5V', to: 'pot1.3', color: 'red' },
    { from: 'uno.6', to: 'r1.1', color: 'blue' },
    { from: 'r1.2', to: 'led1.A', color: 'blue' },
    { from: 'led1.C', to: 'GND', color: 'black' }
  ]
};

export const ALL_TEST_SCENARIOS: Record<string, CircuitNetlist> = {
  scenarioA,
  scenarioA_discrete,
  scenarioB,
  scenarioC,
  scenarioD_messyAliasesAndReverseGnd,
  scenarioE_cathodeResistor,
  scenarioF_voltageDividerAliases,
  scenarioG_trafficLightWithButtonOverflow,
  scenarioH_servoAndUltrasonic,
  scenarioI_potentiometerAndLed
};

export function runAllCircuitTests() {
  const results: Record<string, ReturnType<typeof compileNetlistToBreadboard>> = {};

  for (const [name, netlist] of Object.entries(ALL_TEST_SCENARIOS)) {
    const res = compileNetlistToBreadboard(netlist);
    results[name] = res;
    console.log(`=== ${name} ===`);
    console.log(
      'Bileşenler:',
      res.components.map(c =>
        c.isBreadboardMounted
          ? `${c.label} (Sütun ${c.startCol}..${c.endCol})`
          : `${c.label} (Off-board Dock @ ${c.left},${c.top})`
      )
    );
    console.log('Kablolar:', res.wires.length, 'adet');
    console.log('Hatalar:', res.errors);
    console.log('Uyarılar:', res.warnings);
  }

  return results;
}

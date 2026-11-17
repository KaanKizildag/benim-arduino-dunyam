/**
 * 3 Test Senaryosunun Otomatik Doğrulanması:
 * (a) Tek LED + Direnç + LDR
 * (b) 3 LED'li Trafik Lambası
 * (c) Buton + Servo Motor Devresi
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

export function runAllCircuitTests() {
  console.log('=== SENARYO A1: 4 Pinli LDR Modülü + LED + Direnç ===');
  const resA1 = compileNetlistToBreadboard(scenarioA);
  console.log('Bileşenler:', resA1.components.map(c => `${c.label} (Sütun ${c.startCol}..${c.endCol})`));
  console.log('Kablolar:', resA1.wires.length, 'adet kablo oluşturuldu.');
  console.log('Hatalar:', resA1.errors);
  console.log('Uyarılar:', resA1.warnings);

  console.log('\n=== SENARYO A2: 2 Bacaklı Klasik LDR (Foto-direnç) + Gerilim Bölücü ===');
  const resA2 = compileNetlistToBreadboard(scenarioA_discrete);
  console.log('Bileşenler:', resA2.components.map(c => `${c.label} (Sütun ${c.startCol}..${c.endCol})`));
  console.log('Kablolar:', resA2.wires.length, 'adet kablo oluşturuldu.');
  console.log('Hatalar:', resA2.errors);
  console.log('Uyarılar:', resA2.warnings);

  console.log('\n=== SENARYO B: 3 LED Trafik Lambası ===');
  const resB = compileNetlistToBreadboard(scenarioB);
  console.log('Bileşenler:', resB.components.map(c => `${c.label} (Sütun ${c.startCol}..${c.endCol})`));
  console.log('Kablolar:', resB.wires.length, 'adet kablo oluşturuldu.');
  console.log('Hatalar:', resB.errors);

  console.log('\n=== SENARYO C: Buton + Servo Motor ===');
  const resC = compileNetlistToBreadboard(scenarioC);
  console.log('Bileşenler:', resC.components.map(c => `${c.label} (Sütun ${c.startCol}..${c.endCol})`));
  console.log('Kablolar:', resC.wires.length, 'adet kablo oluşturuldu.');
  console.log('Hatalar:', resC.errors);

  return { resA1, resA2, resB, resC };
}

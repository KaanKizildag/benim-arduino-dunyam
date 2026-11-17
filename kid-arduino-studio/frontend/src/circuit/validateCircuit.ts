/**
 * Katman 4: Elektriksel ve Görsel Doğrulama Motoru (validateCircuit)
 * 1. Kısa Devre Kontrolü
 * 2. Açık Uç (Floating Pin) Kontrolü
 * 3. Etiket Çakışma Önleme (Label Staggering)
 */

import type { CircuitNetlist, PlacedComponent } from './types';

export interface ValidationReport {
  isValid: boolean;
  errors: string[];
  warnings: string[];
}

export function validateNetlist(netlist: CircuitNetlist): ValidationReport {
  const errors: string[] = [];
  const warnings: string[] = [];

  if (!netlist || !Array.isArray(netlist.components)) {
    return { isValid: false, errors: ['Geçersiz netlist şeması.'], warnings: [] };
  }

  // 1. Bileşen Pinlerinin Bağlantı Haritasını Çıkar
  const pinConnectedMap: Record<string, Set<string>> = {};
  for (const c of netlist.components) {
    pinConnectedMap[c.id] = new Set<string>();
  }

  const connections = netlist.connections || [];

  for (const conn of connections) {
    const [fromPart, fromPin] = conn.from.split('.');
    const [toPart, toPin] = conn.to.split('.');

    if (fromPart && fromPin && pinConnectedMap[fromPart]) {
      pinConnectedMap[fromPart].add(fromPin.toUpperCase());
    }
    if (toPart && toPin && pinConnectedMap[toPart]) {
      pinConnectedMap[toPart].add(toPin.toUpperCase());
    }

    // Kısa devre kontrolü: Bir bileşenin iki bacağı doğrudan tek kabloyla birbirine bağlanmış mı?
    if (fromPart && toPart && fromPart === toPart) {
      errors.push(`Kısa Devre Uyarısı: '${fromPart}' bileşeninin iki ucu (${fromPin} -> ${toPin}) doğrudan birbirine bağlanarak bypass edilmiş!`);
    }
  }

  // 2. Açık Uç (Floating Pin) Kontrolü
  for (const comp of netlist.components) {
    const connectedPins = pinConnectedMap[comp.id] || new Set();

    switch (comp.type) {
      case 'wokwi-led': {
        const hasAnode = connectedPins.has('A') || connectedPins.has('ANODE') || connectedPins.has('1');
        const hasCathode = connectedPins.has('C') || connectedPins.has('CATHODE') || connectedPins.has('2');
        if (!hasAnode) warnings.push(`'${comp.label || comp.id}' LED'in Anot (A) bacağı boşta!`);
        if (!hasCathode) warnings.push(`'${comp.label || comp.id}' LED'in Katot (C) bacağı boşta!`);
        break;
      }
      case 'wokwi-resistor': {
        const hasP1 = connectedPins.has('1') || connectedPins.has('PIN_1') || connectedPins.has('A');
        const hasP2 = connectedPins.has('2') || connectedPins.has('PIN_2') || connectedPins.has('B');
        if (!hasP1 || !hasP2) {
          warnings.push(`'${comp.label || comp.id}' Direncin iki ucu da bağlı olmalıdır.`);
        }
        break;
      }
      case 'wokwi-photoresistor': {
        const hasP1 = connectedPins.has('1') || connectedPins.has('PIN_1');
        const hasP2 = connectedPins.has('2') || connectedPins.has('PIN_2');
        if (!hasP1 || !hasP2) {
          warnings.push(`'${comp.label || comp.id}' 2 bacaklı LDR'ın iki ucu da bağlı olmalıdır.`);
        }
        break;
      }
      case 'wokwi-photoresistor-sensor': {
        const hasGnd = connectedPins.has('GND');
        const hasVcc = connectedPins.has('VCC');
        const hasSignal = connectedPins.has('AO') || connectedPins.has('DO') || connectedPins.has('SIG');
        if (!hasGnd || !hasVcc) warnings.push(`'${comp.label || comp.id}' LDR Sensörün güç pinleri (VCC/GND) eksik!`);
        if (!hasSignal) warnings.push(`'${comp.label || comp.id}' LDR Sensörün analog okuma pini (AO) bağlı değil!`);
        break;
      }
      case 'wokwi-servo': {
        if (!connectedPins.has('PWM') && !connectedPins.has('SIG')) {
          warnings.push(`'${comp.label || comp.id}' Servo sinyal pini (PWM) bağlı değil!`);
        }
        break;
      }
      case 'wokwi-pushbutton': {
        if (connectedPins.size < 2) {
          warnings.push(`'${comp.label || comp.id}' Butonun en az iki bacağı bağlı olmalıdır.`);
        }
        break;
      }
    }
  }

  return {
    isValid: errors.length === 0,
    errors,
    warnings
  };
}

/**
 * Etiket Çakışma Önleme (Label Staggering)
 * Yan yana gelen bileşen etiketlerini dikey olarak kademelendirir.
 */
export function applyLabelStaggering(components: PlacedComponent[]): void {
  // Soldan sağa sırala
  const sorted = [...components].sort((a, b) => a.left - b.left);

  const STAGGER_LEVELS = [-24, -42, -60];
  let lastX = -999;
  let currentLevel = 0;

  for (const comp of sorted) {
    if (Math.abs(comp.left - lastX) < 48) {
      // Çakışma var: Bir üst kademeye taşı
      currentLevel = (currentLevel + 1) % STAGGER_LEVELS.length;
    } else {
      currentLevel = 0;
    }

    comp.labelY = STAGGER_LEVELS[currentLevel];
    lastX = comp.left;
  }
}

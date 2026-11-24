/**
 * Katman 4: Elektriksel ve Görsel Doğrulama Motoru (validateCircuit)
 * 1. Kısa Devre ve Desteklenmeyen Tip Kontrolü
 * 2. Açık Uç (Floating Pin) Kontrolü
 * 3. Yerleşimden (Layout + Wires) Elektriksel Bağlantı Geri Çıkarımı ve Orijinal Netlist ile Karşılaştırma
 * 4. Etiket Çakışma Önleme (Label Staggering)
 */

import type {
  CircuitNetlist,
  PlacedComponent,
  RoutedWire,
  ElectricalNet
} from './types';
import { SUPPORTED_COMPONENT_TYPES } from './normalizeNetlist';
import { BREADBOARD_GEOMETRY, getStripKey } from './BreadboardAllocator';

export interface ValidationReport {
  isValid: boolean;
  errors: string[];
  warnings: string[];
}

class LayoutUnionFind {
  private parent = new Map<string, string>();

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
    const rA = this.find(a);
    const rB = this.find(b);
    if (rA !== rB) {
      this.parent.set(rB, rA);
    }
  }

  public connected(a: string, b: string): boolean {
    return this.find(a) === this.find(b);
  }
}

export function validateNetlist(netlist: CircuitNetlist): ValidationReport {
  const errors: string[] = [];
  const warnings: string[] = [];

  if (!netlist || !Array.isArray(netlist.components)) {
    return { isValid: false, errors: ['Geçersiz netlist şeması.'], warnings: [] };
  }

  // 1. Bileşen Pinlerinin Bağlantı Haritasını Çıkar ve Tip Kontrolü Yap
  const pinConnectedMap: Record<string, Set<string>> = {};
  for (const c of netlist.components) {
    pinConnectedMap[c.id] = new Set<string>();
    if (!SUPPORTED_COMPONENT_TYPES.has(c.type)) {
      errors.push(`Desteklenmeyen bileşen tipi: '${c.type}' (${c.label || c.id}).`);
    }
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
    if (fromPart && toPart && fromPart === toPart && fromPart !== 'uno') {
      errors.push(
        `Kısa Devre Hatası: '${fromPart}' bileşeninin iki ucu (${fromPin} -> ${toPin}) doğrudan birbirine bağlanarak kısa devre edilmiş!`
      );
    }
  }

  // 2. Açık Uç (Floating Pin) Kontrolü
  for (const comp of netlist.components) {
    const connectedPins = pinConnectedMap[comp.id] || new Set();

    switch (comp.type) {
      case 'wokwi-led': {
        const hasAnode = connectedPins.has('A');
        const hasCathode = connectedPins.has('C');
        if (!hasAnode) warnings.push(`'${comp.label || comp.id}' LED'in Anot (A) bacağı boşta!`);
        if (!hasCathode) warnings.push(`'${comp.label || comp.id}' LED'in Katot (C) bacağı boşta!`);
        break;
      }
      case 'wokwi-resistor': {
        const hasP1 = connectedPins.has('1');
        const hasP2 = connectedPins.has('2');
        if (!hasP1 || !hasP2) {
          warnings.push(`'${comp.label || comp.id}' Direncin iki ucu da bağlı olmalıdır.`);
        }
        break;
      }
      case 'wokwi-photoresistor': {
        const hasP1 = connectedPins.has('1');
        const hasP2 = connectedPins.has('2');
        if (!hasP1 || !hasP2) {
          warnings.push(`'${comp.label || comp.id}' 2 bacaklı LDR'ın iki ucu da bağlı olmalıdır.`);
        }
        break;
      }
      case 'wokwi-photoresistor-sensor': {
        const hasGnd = connectedPins.has('GND');
        const hasVcc = connectedPins.has('VCC');
        const hasSignal = connectedPins.has('AO') || connectedPins.has('DO');
        if (!hasGnd || !hasVcc) {
          warnings.push(`'${comp.label || comp.id}' LDR Sensörün güç pinleri (VCC/GND) eksik!`);
        }
        if (!hasSignal) {
          warnings.push(`'${comp.label || comp.id}' LDR Sensörün sinyal pini (AO/DO) bağlı değil!`);
        }
        break;
      }
      case 'wokwi-servo': {
        if (!connectedPins.has('PWM')) {
          warnings.push(`'${comp.label || comp.id}' Servo sinyal pini (PWM) bağlı değil!`);
        }
        if (!connectedPins.has('GND') || !connectedPins.has('V+')) {
          warnings.push(`'${comp.label || comp.id}' Servo güç pinleri (V+/GND) bağlı değil!`);
        }
        break;
      }
      case 'wokwi-pushbutton': {
        if (connectedPins.size < 2) {
          warnings.push(`'${comp.label || comp.id}' Butonun en az iki bacağı bağlı olmalıdır.`);
        }
        break;
      }
      case 'wokwi-buzzer': {
        if (!connectedPins.has('1') || !connectedPins.has('2')) {
          warnings.push(`'${comp.label || comp.id}' Buzzer'ın iki ucu da bağlı olmalıdır.`);
        }
        break;
      }
      case 'wokwi-hc-sr04': {
        if (!connectedPins.has('VCC') || !connectedPins.has('GND')) {
          warnings.push(`'${comp.label || comp.id}' HC-SR04 güç pinleri (VCC/GND) eksik!`);
        }
        if (!connectedPins.has('TRIG') || !connectedPins.has('ECHO')) {
          warnings.push(`'${comp.label || comp.id}' HC-SR04 sinyal pinleri (TRIG/ECHO) eksik!`);
        }
        break;
      }
      case 'wokwi-potentiometer': {
        if (!connectedPins.has('GND') || !connectedPins.has('SIG') || !connectedPins.has('VCC')) {
          warnings.push(`'${comp.label || comp.id}' Potansiyometrenin 3 pini (GND, SIG, VCC) bağlı olmalıdır.`);
        }
        break;
      }
      case 'wokwi-hc-05':
      case 'wokwi-hc-06': {
        if (!connectedPins.has('VCC') || !connectedPins.has('GND')) {
          warnings.push(`'${comp.label || comp.id}' Bluetooth modülünün güç pinleri (VCC/GND) eksik!`);
        }
        if (!connectedPins.has('TXD') && !connectedPins.has('RXD') && !connectedPins.has('TX') && !connectedPins.has('RX')) {
          warnings.push(`'${comp.label || comp.id}' Bluetooth modülünün haberleşme pinleri (TX/RX) eksik!`);
        }
        break;
      }
      case 'wokwi-l293d':
      case 'wokwi-l298n': {
        if (connectedPins.size < 4) {
          warnings.push(`'${comp.label || comp.id}' Motor sürücünün güç ve kontrol pinleri eksik!`);
        }
        break;
      }
      case 'wokwi-dc-motor': {
        if (connectedPins.size < 2) {
          warnings.push(`'${comp.label || comp.id}' DC motorun iki kutbu da bağlı olmalıdır.`);
        }
        break;
      }
      case 'wokwi-relay-module': {
        if (!connectedPins.has('VCC') || !connectedPins.has('GND') || !connectedPins.has('IN')) {
          warnings.push(`'${comp.label || comp.id}' Röle modülünün VCC, GND ve IN pinleri bağlı olmalıdır.`);
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
 * Bir breadboard delik ismini ("5C", "14E", "6J", "bn.5", "bp.1") fiziksel iletken şerit düğümüne çevirir.
 */
function holeNameToStripNode(
  holeName?: string,
  maxCols: number = BREADBOARD_GEOMETRY.maxCols
): { node: string | null; error?: string } {
  if (!holeName) return { node: null };
  const h = holeName.trim();

  // Güç rayı delikleri: bn.<col>, bp.<col>
  const railMatch = h.match(/^(bn|bp)\.(-?\d+)$/i);
  if (railMatch) {
    const prefix = railMatch[1].toLowerCase();
    const col = parseInt(railMatch[2], 10);
    if (col < 1 || col > maxCols) {
      return {
        node: prefix === 'bn' ? 'bb:rail:gnd' : 'bb:rail:5v',
        error: `Geçersiz güç rayı sütunu: '${h}' (Sütun 1..${maxCols} aralığında olmalı).`
      };
    }
    return { node: prefix === 'bn' ? 'bb:rail:gnd' : 'bb:rail:5v' };
  }

  if (h === 'bp.-' || h === 'GND') return { node: 'bb:rail:gnd' };
  if (h === 'bp.+' || h === '5V') return { node: 'bb:rail:5v' };

  // Terminal delikleri: <col><row> (örn: 4C, 12E, 6J)
  const termMatch = h.match(/^(\d+)([A-J])$/i);
  if (termMatch) {
    const col = parseInt(termMatch[1], 10);
    const row = termMatch[2].toUpperCase();
    if (col < 1 || col > maxCols) {
      return {
        node: null,
        error: `Delik sütunu sınır dışında: '${h}' (1..${maxCols} olmalı).`
      };
    }
    const stripKey = getStripKey(col, row, maxCols);
    return { node: `bb:strip:${stripKey}` };
  }

  return { node: null };
}

/**
 * Yerleşimden (PlacedComponent[] ve RoutedWire[]) fiziksel elektriksel bağlantıları geri çıkarır
 * ve normalize edilmiş netlist'teki her bağlantının karşılandığını doğrular.
 */
export function validateCompiledLayout(
  netlist: CircuitNetlist,
  nets: ElectricalNet[],
  components: PlacedComponent[],
  wires: RoutedWire[],
  maxCols: number = BREADBOARD_GEOMETRY.maxCols
): string[] {
  const errors: string[] = [];
  const uf = new LayoutUnionFind();
  const occupiedHoles = new Map<string, string>(); // holeName -> compId.pinName
  const stripOwnerNet = new Map<string, string>(); // stripKey -> netId

  // Pin -> NetId haritası
  const pinToNetId = new Map<string, string>();
  for (const net of nets) {
    for (const p of net.componentPins) {
      pinToNetId.set(p, net.id);
    }
  }

  // 1. Yerleştirilmiş bileşenlerin bacaklarını ve delik çakışmalarını kontrol et
  for (const comp of components) {
    if (comp.isBreadboardMounted) {
      if (
        comp.startCol < 1 ||
        comp.endCol > maxCols ||
        comp.startCol > comp.endCol
      ) {
        errors.push(
          `Sütun sınır hatası: '${comp.id}' bileşeni geçersiz sütun aralığında (${comp.startCol}..${comp.endCol}).`
        );
      }

      const compStrips = new Set<string>();

      for (const [pinName, pin] of Object.entries(comp.pins)) {
        const fullPinKey = `${comp.id}.${pinName}`;

        if (pin.col < 1 || pin.col > maxCols) {
          errors.push(
            `Sütun sınır hatası: '${fullPinKey}' bacağı geçersiz sütunda (${pin.col}).`
          );
        }

        // Aynı deliğe iki bileşen bacağı takılmış mı?
        if (occupiedHoles.has(pin.holeName)) {
          errors.push(
            `Delik çakışması: '${pin.holeName}' deliğine hem '${occupiedHoles.get(pin.holeName)}' hem de '${fullPinKey}' bacağı yerleştirilmiş!`
          );
        } else {
          occupiedHoles.set(pin.holeName, fullPinKey);
        }

        // Aynı bileşenin iki bacağı aynı sütun şeridinde mi?
        const sKey = getStripKey(pin.col, pin.row, maxCols);
        if (compStrips.has(sKey)) {
          errors.push(
            `Fiziksel Kısa Devre: '${comp.id}' bileşeninin iki bacağı aynı breadboard şeridine (${sKey}) takılmış!`
          );
        }
        compStrips.add(sKey);

        // Farklı net'ler aynı sütun şeridini paylaşıyor mu?
        const netId = pinToNetId.get(fullPinKey);
        if (netId) {
          const existingOwner = stripOwnerNet.get(sKey);
          if (existingOwner && existingOwner !== netId) {
            errors.push(
              `Sütun Çakışması: Breadboard şeridi (${sKey}) üzerinde iki farklı elektriksel net ('${existingOwner}' ve '${netId}') çakışıyor!`
            );
          } else {
            stripOwnerNet.set(sKey, netId);
          }
        }

        // Bileşen bacağını bulunduğu breadboard şeridine elektriksel olarak bağla
        const stripNode = `bb:strip:${sKey}`;
        uf.union(fullPinKey, stripNode);
      }
    }
  }

  // 2. Kabloların elektriksel bağlantılarını Union-Find'a ekle
  function resolveWireEndpointNode(ep: RoutedWire['from']): string {
    if (ep.holeName) {
      const { node, error } = holeNameToStripNode(ep.holeName, maxCols);
      if (error) errors.push(error);
      if (node) return node;
    }

    if (ep.part === 'uno') {
      const p = ep.pin.toUpperCase();
      if (p === 'GND' || p.startsWith('GND.')) return 'GND';
      if (p === '5V' || p === '3.3V') return '5V';
      return `uno.${p}`;
    }

    if (ep.part.includes('.')) {
      return ep.part;
    }

    return `${ep.part}.${ep.pin}`;
  }

  for (const wire of wires) {
    const nodeFrom = resolveWireEndpointNode(wire.from);
    const nodeTo = resolveWireEndpointNode(wire.to);
    uf.union(nodeFrom, nodeTo);

    // Eğer kablo bir bileşen bacağına doğrudan referans veriyorsa onu da birleştir
    if (wire.from.part && wire.from.part.includes('.')) {
      uf.union(wire.from.part, nodeFrom);
    }
    if (wire.to.part && wire.to.part.includes('.')) {
      uf.union(wire.to.part, nodeTo);
    }
  }

  // 3. 5V ve GND kısa devre kontrolü
  if (uf.connected('5V', 'GND')) {
    errors.push('Kritik Kısa Devre: Yerleşimde 5V ve GND hatları birbirine kısa devre olmuş!');
  }

  // 4. Netlist'teki her bağlantının yerleşimde (ortak sütun veya kabloyla) karşılandığını doğrula
  for (const conn of netlist.connections || []) {
    if (!uf.connected(conn.from, conn.to)) {
      errors.push(
        `Karşılanmayan Bağlantı Hatası: Netlist'teki '${conn.from} → ${conn.to}' bağlantısı breadboard yerleşiminde veya kablolarda bulunamadı!`
      );
    }
  }

  return errors;
}

/**
 * Etiket Çakışma Önleme (Label Staggering)
 * Yan yana gelen bileşen etiketlerini dikey olarak kademelendirir.
 */
export function applyLabelStaggering(components: PlacedComponent[]): void {
  const mounted = components.filter(c => c.isBreadboardMounted);
  const sorted = [...mounted].sort((a, b) => a.left - b.left);

  const STAGGER_LEVELS = [-24, -42, -60];
  let lastX = -999;
  let currentLevel = 0;

  for (const comp of sorted) {
    if (Math.abs(comp.left - lastX) < 48) {
      currentLevel = (currentLevel + 1) % STAGGER_LEVELS.length;
    } else {
      currentLevel = 0;
    }

    comp.labelY = STAGGER_LEVELS[currentLevel];
    lastX = comp.left;
  }
}

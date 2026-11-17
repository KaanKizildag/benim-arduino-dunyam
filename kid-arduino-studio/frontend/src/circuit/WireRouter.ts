/**
 * Katman 3: Akıllı Kablo Yönlendirme (WireRouter)
 * 1. Bus Routing (Tek GND / 5V Ana Hat + Kısa Jumper'lar)
 * 2. Deterministik Lane Allocation (Şerit Yönlendirme ile Sıfır Çakışma)
 * 3. Yumuşatılmış Bezier & Kanal SVG Yolları
 */

import type { CircuitNetlist, NetlistConnection, AllocatedPin, RoutedWire } from './types';
import { getHoleCoords } from './BreadboardAllocator';

export interface RouterOffsets {
  uno: { x: number; y: number };
  bb: { x: number; y: number };
}

// Arduino Uno Pin Koordinatları (Wokwi uno-element standart ofsetleri)
const UNO_PINS: Record<string, { x: number; y: number }> = {
  '13': { x: 125, y: 9 },
  'D13': { x: 125, y: 9 },
  '12': { x: 134.5, y: 9 },
  'D12': { x: 134.5, y: 9 },
  '11': { x: 144, y: 9 },
  'D11': { x: 144, y: 9 },
  '10': { x: 153.5, y: 9 },
  'D10': { x: 153.5, y: 9 },
  '9': { x: 163, y: 9 },
  'D9': { x: 163, y: 9 },
  '8': { x: 173, y: 9 },
  'D8': { x: 173, y: 9 },
  '7': { x: 189, y: 9 },
  'D7': { x: 189, y: 9 },
  '6': { x: 198.5, y: 9 },
  'D6': { x: 198.5, y: 9 },
  '5': { x: 208, y: 9 },
  'D5': { x: 208, y: 9 },
  '4': { x: 217.5, y: 9 },
  'D4': { x: 217.5, y: 9 },
  '3': { x: 227, y: 9 },
  'D3': { x: 227, y: 9 },
  '2': { x: 236.5, y: 9 },
  'D2': { x: 236.5, y: 9 },
  '1': { x: 246, y: 9 },
  'D1': { x: 246, y: 9 },
  '0': { x: 255.5, y: 9 },
  'D0': { x: 255.5, y: 9 },
  // Bottom Header
  'RESET': { x: 140.5, y: 191.5 },
  '3.3V': { x: 150, y: 191.5 },
  '5V': { x: 160, y: 191.5 },
  'GND': { x: 169.5, y: 191.5 },
  'GND.1': { x: 115.5, y: 9 },
  'GND.2': { x: 169.5, y: 191.5 },
  'GND.3': { x: 179, y: 191.5 },
  'VIN': { x: 188.5, y: 191.5 },
  'A0': { x: 208, y: 191.5 },
  'A1': { x: 217.5, y: 191.5 },
  'A2': { x: 227, y: 191.5 },
  'A3': { x: 236.5, y: 191.5 },
  'A4': { x: 246, y: 191.5 },
  'A5': { x: 255.5, y: 191.5 }
};

export class WireRouter {
  private offsets: RouterOffsets;

  constructor(offsets: RouterOffsets) {
    this.offsets = offsets;
  }

  public route(
    netlist: CircuitNetlist,
    allocatedPins: Record<string, AllocatedPin>
  ): RoutedWire[] {
    const wires: RoutedWire[] = [];
    const connections = netlist.connections || [];

    let hasGndBus = false;
    let has5vBus = false;

    // Bağlantılarda GND veya 5V var mı kontrol et
    for (const conn of connections) {
      if (conn.to === 'GND' || conn.from === 'GND') hasGndBus = true;
      if (conn.to === '5V' || conn.from === '5V') has5vBus = true;
    }

    // 1. ANA GÜÇ RAYI HATLARI (Arduino ➔ Breadboard)
    if (hasGndBus) {
      const unoGnd = this.getUnoPinPos('GND.2');
      const bbGnd = this.getBreadboardPos(1, 'bp.-');
      wires.push({
        id: 'main-gnd-bus',
        from: { part: 'uno', pin: 'GND', ...unoGnd },
        to: { part: 'breadboard', pin: 'bn.1', holeName: 'bn.1', ...bbGnd },
        color: '#1e293b',
        laneIndex: 0,
        path: this.buildPowerBusPath(unoGnd, bbGnd, 'bottom'),
        isPowerBus: true,
        description: "Arduino GND ➔ Breadboard Mavi Eksi (-) Rayı Ana Hattı"
      });
    }

    if (has5vBus) {
      const uno5v = this.getUnoPinPos('5V');
      const bb5v = this.getBreadboardPos(1, 'bp.+');
      wires.push({
        id: 'main-5v-bus',
        from: { part: 'uno', pin: '5V', ...uno5v },
        to: { part: 'breadboard', pin: 'bp.1', holeName: 'bp.1', ...bb5v },
        color: '#ef4444',
        laneIndex: 1,
        path: this.buildPowerBusPath(uno5v, bb5v, 'bottom'),
        isPowerBus: true,
        description: "Arduino 5V ➔ Breadboard Kırmızı Artı (+) Rayı Ana Hattı"
      });
    }

    // 2. DEVRE BAĞLANTILARI
    let topLaneIndex = 0;
    let bottomLaneIndex = 2; // 0 ve 1 güç raylarına ait

    for (let i = 0; i < connections.length; i++) {
      const conn = connections[i];
      const fromStr = conn.from;
      const toStr = conn.to;

      // Durum A: GND'ye Bağlantı (Kısa Jumper ile en yakın alt ray deliğine)
      if (toStr === 'GND') {
        const pin = allocatedPins[fromStr];
        if (pin) {
          const col = pin.col;
          const fromCoords = this.getBreadboardHolePos(col, pin.row);
          // Doğrudan aynı sütunun alt eksi rayına (bn.col) kısa kavisli jumper
          const toCoords = this.getBreadboardPos(col, 'bp.-');
          wires.push({
            id: `wire-${i}`,
            from: { part: fromStr, pin: pin.pinName, holeName: pin.holeName, ...fromCoords },
            to: { part: 'breadboard', pin: `bn.${col}`, holeName: `bn.${col}`, ...toCoords },
            color: conn.color || '#1e293b',
            laneIndex: 0,
            path: this.buildLocalJumperPath(fromCoords, toCoords, 'down'),
            isPowerBus: false,
            description: `${fromStr} ➔ GND Rayı (Sütun ${col})`
          });
        }
        continue;
      }

      // Durum B: 5V'a Bağlantı (Kısa Jumper ile en yakın alt artı ray deliğine)
      if (toStr === '5V') {
        const pin = allocatedPins[fromStr];
        if (pin) {
          const col = pin.col;
          const fromCoords = this.getBreadboardHolePos(col, pin.row);
          const toCoords = this.getBreadboardPos(col, 'bp.+');
          wires.push({
            id: `wire-${i}`,
            from: { part: fromStr, pin: pin.pinName, holeName: pin.holeName, ...fromCoords },
            to: { part: 'breadboard', pin: `bp.${col}`, holeName: `bp.${col}`, ...toCoords },
            color: conn.color || '#ef4444',
            laneIndex: 0,
            path: this.buildLocalJumperPath(fromCoords, toCoords, 'down'),
            isPowerBus: false,
            description: `${fromStr} ➔ 5V Güç Rayı (Sütun ${col})`
          });
        }
        continue;
      }

      // Durum C: İki Eleman Arası İç Bağlantı (Aynı sütunsa kablo çekme!)
      const pinA = allocatedPins[fromStr];
      const pinB = allocatedPins[toStr];
      if (pinA && pinB) {
        if (pinA.col === pinB.col) {
          // Zaten breadboard dikey sütunu üzerinden bağlı! Kablo gerekmez.
          continue;
        } else {
          // Farklı sütunlardaysa yatay jumper kablosu
          const fromCoords = this.getBreadboardHolePos(pinA.col, pinA.row);
          const toCoords = this.getBreadboardHolePos(pinB.col, pinB.row);
          wires.push({
            id: `wire-${i}`,
            from: { part: fromStr, pin: pinA.pinName, holeName: pinA.holeName, ...fromCoords },
            to: { part: toStr, pin: pinB.pinName, holeName: pinB.holeName, ...toCoords },
            color: conn.color || '#f59e0b',
            laneIndex: topLaneIndex++,
            path: this.buildLocalJumperPath(fromCoords, toCoords, 'up'),
            isPowerBus: false,
            description: `${pinA.holeName} ➔ ${pinB.holeName}`
          });
        }
        continue;
      }

      // Durum D: Arduino ➔ Breadboard Sinyal Kablosu (Örn: uno.D13 -> r1.1)
      let unoPinName: string | null = null;
      let targetPin: AllocatedPin | null = null;

      if (fromStr.startsWith('uno.')) {
        unoPinName = fromStr.replace('uno.', '');
        targetPin = allocatedPins[toStr] || null;
      } else if (toStr.startsWith('uno.')) {
        unoPinName = toStr.replace('uno.', '');
        targetPin = allocatedPins[fromStr] || null;
      }

      if (unoPinName && targetPin) {
        const unoPos = this.getUnoPinPos(unoPinName);
        const targetRow = targetPin.row || 'A';
        const bbPos = this.getBreadboardHolePos(targetPin.col, targetRow);

        const isTopHeader = unoPos.y < this.offsets.uno.y + 100;
        const lane = isTopHeader ? topLaneIndex++ : bottomLaneIndex++;
        const path = isTopHeader
          ? this.buildHighwayPath(unoPos, bbPos, 'top', lane)
          : this.buildHighwayPath(unoPos, bbPos, 'bottom', lane);

        wires.push({
          id: `wire-${i}`,
          from: { part: 'uno', pin: unoPinName, ...unoPos },
          to: { part: targetPin.componentId, pin: targetPin.pinName, holeName: `${targetPin.col}${targetRow}`, ...bbPos },
          color: conn.color || '#3b82f6',
          laneIndex: lane,
          path,
          isPowerBus: false,
          description: `Arduino ${unoPinName} ➔ Breadboard ${targetPin.col}${targetRow} (${targetPin.componentId})`
        });
      }
    }

    return wires;
  }

  private getUnoPinPos(pin: string): { x: number; y: number } {
    const p = (pin || '').toUpperCase();
    const local = UNO_PINS[p] || UNO_PINS[p.replace('D', '')] || { x: 125, y: 9 };
    return {
      x: this.offsets.uno.x + local.x,
      y: this.offsets.uno.y + local.y
    };
  }

  private getBreadboardHolePos(col: number, row: string): { x: number; y: number } {
    const local = getHoleCoords(col, row);
    return {
      x: this.offsets.bb.x + local.x,
      y: this.offsets.bb.y + local.y
    };
  }

  private getBreadboardPos(col: number, row: string): { x: number; y: number } {
    return this.getBreadboardHolePos(col, row);
  }

  /**
   * Kademeli Şerit (Highway Lane) Yolu: Wires asla üst üste binmez!
   */
  private buildHighwayPath(
    from: { x: number; y: number },
    to: { x: number; y: number },
    side: 'top' | 'bottom',
    laneIndex: number
  ): string {
    const laneOffset = 18 + laneIndex * 14;

    if (side === 'top') {
      const channelY = Math.min(from.y, to.y) - laneOffset;
      const r = 8;
      return `M ${from.x} ${from.y} ` +
             `L ${from.x} ${channelY + r} ` +
             `Q ${from.x} ${channelY} ${from.x + r} ${channelY} ` +
             `L ${to.x - r} ${channelY} ` +
             `Q ${to.x} ${channelY} ${to.x} ${channelY + r} ` +
             `L ${to.x} ${to.y}`;
    } else {
      const channelY = Math.max(from.y, to.y) + laneOffset;
      const r = 8;
      return `M ${from.x} ${from.y} ` +
             `L ${from.x} ${channelY - r} ` +
             `Q ${from.x} ${channelY} ${from.x + r} ${channelY} ` +
             `L ${to.x - r} ${channelY} ` +
             `Q ${to.x} ${channelY} ${to.x} ${channelY - r} ` +
             `L ${to.x} ${to.y}`;
    }
  }

  /**
   * Güç Rayı Ana Hat Yolu
   */
  private buildPowerBusPath(
    from: { x: number; y: number },
    to: { x: number; y: number },
    side: 'bottom'
  ): string {
    const channelY = to.y + 18;
    return `M ${from.x} ${from.y} ` +
           `C ${from.x} ${channelY}, ${to.x - 20} ${channelY}, ${to.x} ${to.y}`;
  }

  /**
   * Breadboard içi kısa jumper kavis yolu
   */
  private buildLocalJumperPath(
    from: { x: number; y: number },
    to: { x: number; y: number },
    arcDir: 'up' | 'down'
  ): string {
    const dx = to.x - from.x;
    const dy = to.y - from.y;
    const offset = arcDir === 'down' ? 14 : -16;
    const cx = from.x + dx * 0.5 + 4;
    const cy = from.y + dy * 0.5 + offset;
    return `M ${from.x} ${from.y} Q ${cx} ${cy} ${to.x} ${to.y}`;
  }
}

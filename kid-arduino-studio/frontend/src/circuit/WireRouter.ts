/**
 * Katman 3: Akıllı ve Net Tabanlı Kablo Yönlendirme (WireRouter)
 * 1. Bus Routing (Tek GND / 5V Ana Hat + Kısa Jumper'lar)
 * 2. Net (Düğüm) Başına Minimum Kablo Üretimi (Union-Find net'leri üzerinden)
 * 3. Simetrik from/to ve Off-Board Modül Desteği (bn.0 hatası olmadan boş ray sütunu tahsisi)
 * 4. Çocuk dostu Türkçe ve delik isimli açıklamalar ("Arduino D13 → 4C deliği")
 */

import type {
  CircuitNetlist,
  AllocatedPin,
  RoutedWire,
  ElectricalNet
} from './types';
import { getHoleCoords, getStripKey, BREADBOARD_GEOMETRY } from './BreadboardAllocator';
import { normalizeNetlist } from './normalizeNetlist';

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
    allocatedPins: Record<string, AllocatedPin>,
    providedNets?: ElectricalNet[]
  ): RoutedWire[] {
    const wires: RoutedWire[] = [];
    const nets = providedNets ?? normalizeNetlist(netlist).nets;

    const compLabelMap = new Map<string, string>();
    for (const c of netlist.components || []) {
      compLabelMap.set(c.id, c.label || c.id);
    }

    const hasGndBus = nets.some(n => n.powerRail === 'GND');
    const has5vBus = nets.some(n => n.powerRail === '5V');

    const usedGndRailCols = new Set<number>();
    const used5vRailCols = new Set<number>();
    const usedBreadboardHoles = new Set<string>();

    for (const p of Object.values(allocatedPins)) {
      if (p.col >= 1 && p.col <= BREADBOARD_GEOMETRY.maxCols && p.holeName) {
        usedBreadboardHoles.add(p.holeName.toUpperCase());
      }
    }

    // 1. ANA GÜÇ RAYI HATLARI (Arduino ➔ Breadboard)
    // Görsel olarak kabloların üst üste binmemesi için GND rayı 1. sütuna (bn.1, y=188),
    // 5V rayı ise 2. sütuna (bp.2, y=176) ve farklı kavis kanalından bağlanır.
    if (hasGndBus) {
      usedGndRailCols.add(1);
      const unoGnd = this.getUnoPinPos('GND.2');
      const bbGnd = this.getBreadboardPos(1, 'bp.-');
      wires.push({
        id: 'main-gnd-bus',
        from: { part: 'uno', pin: 'GND', ...unoGnd },
        to: { part: 'breadboard', pin: 'bn.1', holeName: 'bn.1', ...bbGnd },
        color: '#1e293b',
        laneIndex: 0,
        path: this.buildPowerBusPath(unoGnd, bbGnd, 28),
        isPowerBus: true,
        description: 'Arduino GND → Breadboard Mavi Eksi (-) Rayı (bn.1 pini)'
      });
    }

    if (has5vBus) {
      used5vRailCols.add(2);
      const uno5v = this.getUnoPinPos('5V');
      const bb5v = this.getBreadboardPos(2, 'bp.+');
      wires.push({
        id: 'main-5v-bus',
        from: { part: 'uno', pin: '5V', ...uno5v },
        to: { part: 'breadboard', pin: 'bp.2', holeName: 'bp.2', ...bb5v },
        color: '#ef4444',
        laneIndex: 1,
        path: this.buildPowerBusPath(uno5v, bb5v, 14),
        isPowerBus: true,
        description: 'Arduino 5V → Breadboard Kırmızı Artı (+) Rayı (bp.2 pini)'
      });
    }

    // 2. NET BAZLI DEVRE BAĞLANTILARI
    let topLaneIndex = 0;
    let bottomLaneIndex = 2;
    let wireCounter = 1;

    for (const net of nets) {
      const resolvedPins = net.componentPins
        .map(key => ({ key, pin: allocatedPins[key] }))
        .filter((item): item is { key: string; pin: AllocatedPin } => Boolean(item.pin));

      const bbPins = resolvedPins.filter(
        item => item.pin.col >= 1 && item.pin.col <= BREADBOARD_GEOMETRY.maxCols && item.pin.row !== 'offboard'
      );
      const offBoardPins = resolvedPins.filter(
        item => item.pin.col === 0 || item.pin.row === 'offboard'
      );

      // Breadboard üzerindeki pinleri fiziksel sütun şeridine (col + yarı) göre grupla
      const stripMap = new Map<string, Array<{ key: string; pin: AllocatedPin }>>();
      for (const item of bbPins) {
        const sKey = getStripKey(item.pin.col, item.pin.row);
        if (!stripMap.has(sKey)) {
          stripMap.set(sKey, []);
        }
        stripMap.get(sKey)!.push(item);
      }

      const stripGroups = Array.from(stripMap.entries()).map(([stripKey, items]) => ({
        stripKey,
        items,
        repPin: items[0].pin,
        label: items
          .map(i => compLabelMap.get(i.pin.componentId) || i.pin.componentId)
          .filter((v, idx, arr) => arr.indexOf(v) === idx)
          .join(' & ')
      }));

      // 2a. Aynı net içinde birden fazla breadboard sütun şeridi varsa birbirine jumper ile bağla
      for (let i = 0; i < stripGroups.length - 1; i++) {
        const groupA = stripGroups[i];
        const groupB = stripGroups[i + 1];
        const pinA = groupA.repPin;
        const pinB = groupB.repPin;
        const freeA = this.pickFreeStripHole(pinA, 'top', usedBreadboardHoles);
        const freeB = this.pickFreeStripHole(pinB, 'top', usedBreadboardHoles);

        wires.push({
          id: `wire-${wireCounter++}`,
          from: {
            part: `${pinA.componentId}.${pinA.pinName}`,
            pin: pinA.pinName,
            holeName: freeA.holeName,
            x: freeA.x,
            y: freeA.y
          },
          to: {
            part: `${pinB.componentId}.${pinB.pinName}`,
            pin: pinB.pinName,
            holeName: freeB.holeName,
            x: freeB.x,
            y: freeB.y
          },
          color: net.color || '#f59e0b',
          laneIndex: topLaneIndex++,
          path: this.buildLocalJumperPath(freeA, freeB, 'up'),
          isPowerBus: false,
          description: `${freeA.holeName} pini (${groupA.label}) → ${freeB.holeName} pini (${groupB.label})`
        });
      }

      // 2b. Off-board pinleri varsa ve aynı net'te breadboard sütunu da varsa birbirine bağla
      if (offBoardPins.length > 0 && stripGroups.length > 0) {
        const targetGroup = stripGroups[0];
        const targetPin = targetGroup.repPin;
        const freeTarget = this.pickFreeStripHole(targetPin, 'bottom', usedBreadboardHoles);

        for (const offItem of offBoardPins) {
          const offPin = offItem.pin;
          const fromCoords = this.getPinCanvasPos(offPin);
          const offLabel = compLabelMap.get(offPin.componentId) || offPin.componentId;
          const lane = bottomLaneIndex++;

          wires.push({
            id: `wire-${wireCounter++}`,
            from: {
              part: `${offPin.componentId}.${offPin.pinName}`,
              pin: offPin.pinName,
              holeName: offPin.holeName,
              ...fromCoords
            },
            to: {
              part: `${targetPin.componentId}.${targetPin.pinName}`,
              pin: targetPin.pinName,
              holeName: freeTarget.holeName,
              x: freeTarget.x,
              y: freeTarget.y
            },
            color: net.color || '#10b981',
            laneIndex: lane,
            path: this.buildHighwayPath(fromCoords, freeTarget, 'bottom', lane),
            isPowerBus: false,
            description: `${offLabel} (${offPin.pinName}) → ${freeTarget.holeName} pini (${targetGroup.label})`
          });
        }
      } else if (offBoardPins.length > 1) {
        // Sadece off-board pinleri kendi aralarında bağlıysa zincirle
        for (let i = 0; i < offBoardPins.length - 1; i++) {
          const pinA = offBoardPins[i].pin;
          const pinB = offBoardPins[i + 1].pin;
          const fromCoords = this.getPinCanvasPos(pinA);
          const toCoords = this.getPinCanvasPos(pinB);
          const labelA = compLabelMap.get(pinA.componentId) || pinA.componentId;
          const labelB = compLabelMap.get(pinB.componentId) || pinB.componentId;

          wires.push({
            id: `wire-${wireCounter++}`,
            from: {
              part: `${pinA.componentId}.${pinA.pinName}`,
              pin: pinA.pinName,
              holeName: pinA.holeName,
              ...fromCoords
            },
            to: {
              part: `${pinB.componentId}.${pinB.pinName}`,
              pin: pinB.pinName,
              holeName: pinB.holeName,
              ...toCoords
            },
            color: net.color || '#10b981',
            laneIndex: topLaneIndex++,
            path: this.buildLocalJumperPath(fromCoords, toCoords, 'up'),
            isPowerBus: false,
            description: `${labelA} (${pinA.pinName}) → ${labelB} (${pinB.pinName})`
          });
        }
      }

      // 2c. Arduino Sinyal Bağlantıları (Net başına 1 kablo ile aynı sütundaki boş pine bağlanır)
      for (const unoPinFull of net.arduinoPins) {
        const unoPinName = unoPinFull.replace(/^uno\./i, '');
        const unoPos = this.getUnoPinPos(unoPinName);
        const isTopHeader = unoPos.y < this.offsets.uno.y + 100;
        const lane = isTopHeader ? topLaneIndex++ : bottomLaneIndex++;
        const side = isTopHeader ? 'top' : 'bottom';

        if (stripGroups.length > 0) {
          const targetGroup = stripGroups[0];
          const targetPin = targetGroup.repPin;
          const freeHole = this.pickFreeStripHole(targetPin, side, usedBreadboardHoles);
          const path = this.buildHighwayPath(unoPos, freeHole, side, lane);

          wires.push({
            id: `wire-${wireCounter++}`,
            from: { part: 'uno', pin: unoPinName, ...unoPos },
            to: {
              part: `${targetPin.componentId}.${targetPin.pinName}`,
              pin: targetPin.pinName,
              holeName: freeHole.holeName,
              x: freeHole.x,
              y: freeHole.y
            },
            color: net.color || '#3b82f6',
            laneIndex: lane,
            path,
            isPowerBus: false,
            description: `Arduino ${unoPinName} → Breadboard ${freeHole.holeName} pini (${targetGroup.label} ile aynı sütun)`
          });
        } else if (offBoardPins.length > 0) {
          const targetPin = offBoardPins[0].pin;
          const offPos = this.getPinCanvasPos(targetPin);
          const offLabel = compLabelMap.get(targetPin.componentId) || targetPin.componentId;
          const path = this.buildHighwayPath(unoPos, offPos, side, lane);

          wires.push({
            id: `wire-${wireCounter++}`,
            from: { part: 'uno', pin: unoPinName, ...unoPos },
            to: {
              part: `${targetPin.componentId}.${targetPin.pinName}`,
              pin: targetPin.pinName,
              holeName: targetPin.holeName,
              ...offPos
            },
            color: net.color || '#3b82f6',
            laneIndex: lane,
            path,
            isPowerBus: false,
            description: `Arduino ${unoPinName} → ${offLabel} (${targetPin.pinName} pini)`
          });
        }
      }

      // 2d. Güç Rayı (GND / 5V) Bağlantısı
      if (net.powerRail === 'GND' || net.powerRail === '5V') {
        const isGnd = net.powerRail === 'GND';
        const usedSet = isGnd ? usedGndRailCols : used5vRailCols;
        const railRow = isGnd ? 'bp.-' : 'bp.+';
        const railPrefix = isGnd ? 'bn' : 'bp';
        const defaultColor = isGnd ? '#1e293b' : '#ef4444';
        const railTitle = isGnd ? 'Mavi GND (-) Rayı' : 'Kırmızı 5V (+) Rayı';

        if (stripGroups.length > 0) {
          const targetGroup = stripGroups[stripGroups.length - 1];
          const pin = targetGroup.repPin;
          const freeFrom = this.pickFreeStripHole(pin, 'bottom', usedBreadboardHoles);
          const railCol = this.pickFreeRailCol(pin.col, usedSet);
          const railHole = `${railPrefix}.${railCol}`;
          const toCoords = this.getBreadboardPos(railCol, railRow);

          wires.push({
            id: `wire-${wireCounter++}`,
            from: {
              part: `${pin.componentId}.${pin.pinName}`,
              pin: pin.pinName,
              holeName: freeFrom.holeName,
              x: freeFrom.x,
              y: freeFrom.y
            },
            to: {
              part: 'breadboard',
              pin: railHole,
              holeName: railHole,
              ...toCoords
            },
            color: net.color || defaultColor,
            laneIndex: 0,
            path: this.buildLocalJumperPath(freeFrom, toCoords, 'down'),
            isPowerBus: false,
            description: `Breadboard ${freeFrom.holeName} pini (${targetGroup.label} ile aynı sütun) → ${railTitle} (${railHole} pini)`
          });
        } else if (offBoardPins.length > 0) {
          const pin = offBoardPins[0].pin;
          const offLabel = compLabelMap.get(pin.componentId) || pin.componentId;
          const railCol = this.pickFreeRailCol(0, usedSet);
          const railHole = `${railPrefix}.${railCol}`;
          const fromCoords = this.getPinCanvasPos(pin);
          const toCoords = this.getBreadboardPos(railCol, railRow);
          const lane = bottomLaneIndex++;

          wires.push({
            id: `wire-${wireCounter++}`,
            from: {
              part: `${pin.componentId}.${pin.pinName}`,
              pin: pin.pinName,
              holeName: pin.holeName,
              ...fromCoords
            },
            to: {
              part: 'breadboard',
              pin: railHole,
              holeName: railHole,
              ...toCoords
            },
            color: net.color || defaultColor,
            laneIndex: lane,
            path: this.buildHighwayPath(fromCoords, toCoords, 'bottom', lane),
            isPowerBus: false,
            description: `${offLabel} (${pin.pinName} pini) → ${railTitle} (${railHole} pini)`
          });
        }
      }
    }

    return wires;
  }

  /**
   * Aynı breadboard sütun şeridi (A-E veya F-J) üzerinde bileşen bacağının takılı olduğu deliğin
   * üstüne binmeyecek boş bir jumper deliği (örn: 4C doluysa 4A veya 4D) seçer.
   */
  private pickFreeStripHole(
    pin: AllocatedPin,
    preferSide: 'top' | 'bottom',
    usedHoles: Set<string>
  ): { holeName: string; x: number; y: number } {
    const col = pin.col;
    const rUp = (pin.row || 'C').toUpperCase();
    const isUpper = ['A', 'B', 'C', 'D', 'E'].includes(rUp);

    const candidateRows = isUpper
      ? preferSide === 'top'
        ? ['A', 'B', 'D', 'C', 'E']
        : ['D', 'B', 'A', 'C', 'E']
      : preferSide === 'top'
        ? ['F', 'G', 'I', 'H', 'J']
        : ['I', 'G', 'F', 'H', 'J'];

    for (const row of candidateRows) {
      const candidateHole = `${col}${row}`;
      if (!usedHoles.has(candidateHole)) {
        usedHoles.add(candidateHole);
        const pos = this.getBreadboardHolePos(col, row);
        return {
          holeName: candidateHole,
          x: pos.x,
          y: pos.y
        };
      }
    }

    const fallbackPos = this.getBreadboardHolePos(col, rUp);
    return {
      holeName: `${col}${rUp}`,
      x: fallbackPos.x,
      y: fallbackPos.y
    };
  }

  /**
   * Güç rayı üzerinde 1..30 aralığında boş bir sütun seçer (Asla 0 döndürmez).
   */
  private pickFreeRailCol(preferredCol: number, usedCols: Set<number>): number {
    const maxCols = BREADBOARD_GEOMETRY.maxCols;

    if (preferredCol >= 1 && preferredCol <= maxCols && !usedCols.has(preferredCol)) {
      usedCols.add(preferredCol);
      return preferredCol;
    }

    if (preferredCol >= 1 && preferredCol <= maxCols) {
      for (let delta = 1; delta <= maxCols; delta++) {
        const right = preferredCol + delta;
        if (right <= maxCols && !usedCols.has(right)) {
          usedCols.add(right);
          return right;
        }
        const left = preferredCol - delta;
        if (left >= 1 && !usedCols.has(left)) {
          usedCols.add(left);
          return left;
        }
      }
    }

    // Off-board bileşenler (preferredCol === 0) için sağ uçtan (30'dan geriye) boş sütun tahsis et
    for (let c = maxCols; c >= 2; c--) {
      if (!usedCols.has(c)) {
        usedCols.add(c);
        return c;
      }
    }

    return maxCols;
  }

  private getPinCanvasPos(pin: AllocatedPin): { x: number; y: number } {
    if (pin.col === 0 || pin.row === 'offboard') {
      return {
        x: this.offsets.bb.x + pin.x,
        y: this.offsets.bb.y + pin.y
      };
    }
    return this.getBreadboardHolePos(pin.col, pin.row);
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
   * Kademeli Şerit (Highway Lane) Yolu: Kablolar üst üste binmez.
   */
  private buildHighwayPath(
    from: { x: number; y: number },
    to: { x: number; y: number },
    side: 'top' | 'bottom',
    laneIndex: number
  ): string {
    const laneOffset = 18 + laneIndex * 12;

    if (side === 'top') {
      const channelY = Math.min(from.y, to.y) - laneOffset;
      const r = 8;
      const dirX = to.x >= from.x ? 1 : -1;
      return (
        `M ${from.x} ${from.y} ` +
        `L ${from.x} ${channelY + r} ` +
        `Q ${from.x} ${channelY} ${from.x + dirX * r} ${channelY} ` +
        `L ${to.x - dirX * r} ${channelY} ` +
        `Q ${to.x} ${channelY} ${to.x} ${channelY + r} ` +
        `L ${to.x} ${to.y}`
      );
    } else {
      const channelY = Math.max(from.y, to.y) + laneOffset;
      const r = 8;
      const dirX = to.x >= from.x ? 1 : -1;
      return (
        `M ${from.x} ${from.y} ` +
        `L ${from.x} ${channelY - r} ` +
        `Q ${from.x} ${channelY} ${from.x + dirX * r} ${channelY} ` +
        `L ${to.x - dirX * r} ${channelY} ` +
        `Q ${to.x} ${channelY} ${to.x} ${channelY - r} ` +
        `L ${to.x} ${to.y}`
      );
    }
  }

  /**
   * Güç Rayı Ana Hat Yolu (5V ve GND ayrı kanallardan geçer)
   */
  private buildPowerBusPath(
    from: { x: number; y: number },
    to: { x: number; y: number },
    dropOffset = 18
  ): string {
    const channelY = Math.max(from.y, to.y) + dropOffset;
    return (
      `M ${from.x} ${from.y} ` +
      `C ${from.x} ${channelY}, ${to.x - 16} ${channelY}, ${to.x} ${to.y}`
    );
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

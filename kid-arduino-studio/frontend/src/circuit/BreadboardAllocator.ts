/**
 * Katman 2: Dinamik Sütun Tahsis Algoritması (BreadboardAllocator)
 * Fiziksel Kurallar:
 * 1. Bir bileşenin iki farklı pini ASLA aynı sütuna bağlanamaz (Kısa Devre Yasağı).
 * 2. Breadboard üzerinde her sütundaki 5 dikey delik (A-B-C-D-E) içeriden birbirine bağlıdır.
 * 3. Seri bağlı elemanlar (LED Katot + Direnç, LDR + 10k Direnç) aynı sütunu paylaşarak içeriden bağlanır.
 * 4. Kart/Modül bileşenleri (4 Pin LDR, Servo, HC-SR04) breadboard'u tıkamaz; modül dock'una oturur ve jumper kablolarla bağlanır.
 * 5. Ayrılmış ferah bölgeler (Zone 1: Kolon 4-10, Zone 2: Kolon 15-21, Zone 3: Kolon 25-28).
 */

import type { CircuitNetlist, NetlistComponent, PlacedComponent, AllocatedPin } from './types';

export const BREADBOARD_GEOMETRY = {
  startX: 38,
  colPitch: 9.5,
  maxCols: 30,
  rowY: {
    A: 48,
    B: 57.5,
    C: 67,
    D: 76.5,
    E: 86,
    F: 118,
    G: 127.5,
    H: 137,
    I: 146.5,
    J: 156,
    // Power rails
    'tp.+': 16,
    'tp.-': 28,
    'bp.+': 176,
    'bp.-': 188
  }
};

export function getHoleCoords(col: number, row: string): { x: number; y: number } {
  const clampedCol = Math.max(1, Math.min(BREADBOARD_GEOMETRY.maxCols, col));
  const x = BREADBOARD_GEOMETRY.startX + (clampedCol - 1) * BREADBOARD_GEOMETRY.colPitch;
  
  let y = BREADBOARD_GEOMETRY.rowY.A;
  const upperRow = row.toUpperCase();
  if (upperRow in BREADBOARD_GEOMETRY.rowY) {
    y = (BREADBOARD_GEOMETRY.rowY as any)[upperRow];
  } else if (upperRow.startsWith('BN') || upperRow === 'GND' || upperRow === '-') {
    y = BREADBOARD_GEOMETRY.rowY['bp.-'];
  } else if (upperRow.startsWith('BP') || upperRow === '5V' || upperRow === '+') {
    y = BREADBOARD_GEOMETRY.rowY['bp.+'];
  }

  return { x, y };
}

export class BreadboardAllocator {
  private currentCol = 4; // Soldan ferah başla
  private placedComponents: PlacedComponent[] = [];
  private allocatedPins: Record<string, AllocatedPin> = {};
  private internalSharedNodes: Array<{ col: number; components: string[]; label: string }> = [];

  public allocate(netlist: CircuitNetlist): {
    components: PlacedComponent[];
    allocatedPins: Record<string, AllocatedPin>;
    internalSharedNodes: Array<{ col: number; components: string[]; label: string }>;
  } {
    this.currentCol = 4;
    this.placedComponents = [];
    this.allocatedPins = {};
    this.internalSharedNodes = [];

    const components = [...netlist.components];
    const connections = netlist.connections || [];
    const processedComponentIds = new Set<string>();

    // 1. Seri bağlı Resistor + LED çiftlerini bul (Örn: r1.2 -> led1.A)
    for (const comp of components) {
      if (processedComponentIds.has(comp.id)) continue;

      if (this.isOffBoardComponent(comp.type)) {
        this.allocateOffBoardComponent(comp);
        processedComponentIds.add(comp.id);
        continue;
      }

      const seriesPartner = this.findSeriesPartner(comp, components, connections, processedComponentIds);
      if (seriesPartner) {
        this.allocateSeriesPair(comp, seriesPartner.component, seriesPartner.connection);
        processedComponentIds.add(comp.id);
        processedComponentIds.add(seriesPartner.component.id);
      } else {
        this.allocateSingleComponent(comp);
        processedComponentIds.add(comp.id);
      }
    }

    return {
      components: this.placedComponents,
      allocatedPins: this.allocatedPins,
      internalSharedNodes: this.internalSharedNodes
    };
  }

  public isOffBoardComponent(type: string): boolean {
    return type === 'wokwi-servo' || type === 'wokwi-hc-sr04' || type === 'wokwi-photoresistor-sensor';
  }

  private findSeriesPartner(
    comp: NetlistComponent,
    allComps: NetlistComponent[],
    connections: any[],
    processed: Set<string>
  ): { component: NetlistComponent; connection: any } | null {
    if (comp.type !== 'wokwi-resistor' && comp.type !== 'wokwi-led') {
      return null;
    }

    for (const conn of connections) {
      const [fromPart, fromPin] = conn.from.split('.');
      const [toPart, toPin] = conn.to.split('.');

      let partnerId: string | null = null;
      if (fromPart === comp.id && toPart && toPart !== 'GND' && toPart !== '5V' && !toPart.startsWith('uno')) {
        partnerId = toPart;
      } else if (toPart === comp.id && fromPart && fromPart !== 'GND' && fromPart !== '5V' && !fromPart.startsWith('uno')) {
        partnerId = fromPart;
      }

      if (partnerId && !processed.has(partnerId)) {
        const partner = allComps.find(c => c.id === partnerId);
        if (partner && (partner.type === 'wokwi-led' || partner.type === 'wokwi-resistor')) {
          return { component: partner, connection: conn };
        }
      }
    }
    return null;
  }

  /**
   * Seri bağlı çift: Resistor (Col X -> X+4) ve LED (Col X+4 -> X+5)
   * Sütun X+4'te direnç ucu 2 ile LED anodu içeriden buluşur!
   */
  private allocateSeriesPair(compA: NetlistComponent, compB: NetlistComponent, conn: any) {
    const resistor = compA.type === 'wokwi-resistor' ? compA : compB;
    const led = compA.type === 'wokwi-led' ? compA : compB;

    const startCol = this.currentCol;
    const sharedCol = startCol + 4; // Direnç 4 sütun kaplar
    const ledEndCol = sharedCol + 1; // LED 1 sütun kaplar

    // 1. Direnç: Sütun startCol (Pin 1) -> sharedCol (Pin 2), Satır C
    const rPin1Coords = getHoleCoords(startCol, 'C');
    const rPin2Coords = getHoleCoords(sharedCol, 'C');

    const rPins: Record<string, AllocatedPin> = {
      '1': { componentId: resistor.id, pinName: '1', col: startCol, row: 'C', holeName: `${startCol}C`, ...rPin1Coords },
      '2': { componentId: resistor.id, pinName: '2', col: sharedCol, row: 'C', holeName: `${sharedCol}C`, ...rPin2Coords }
    };

    this.placedComponents.push({
      id: resistor.id,
      type: resistor.type,
      props: resistor.props || {},
      label: resistor.label || '220Ω Direnç',
      isBreadboardMounted: true,
      left: rPin1Coords.x + 8,
      top: rPin1Coords.y - 6,
      labelX: rPin1Coords.x + 15,
      labelY: -25,
      startCol,
      endCol: sharedCol,
      pins: rPins
    });

    this.allocatedPins[`${resistor.id}.1`] = rPins['1'];
    this.allocatedPins[`${resistor.id}.2`] = rPins['2'];

    // 2. LED: Sütun sharedCol (Anot) -> ledEndCol (Katot), Satır E
    const ledAnodeCoords = getHoleCoords(sharedCol, 'E');
    const ledCathodeCoords = getHoleCoords(ledEndCol, 'E');

    const ledPins: Record<string, AllocatedPin> = {
      'A': { componentId: led.id, pinName: 'A', col: sharedCol, row: 'E', holeName: `${sharedCol}E`, ...ledAnodeCoords },
      'C': { componentId: led.id, pinName: 'C', col: ledEndCol, row: 'E', holeName: `${ledEndCol}E`, ...ledCathodeCoords }
    };

    this.placedComponents.push({
      id: led.id,
      type: led.type,
      props: led.props || {},
      label: led.label || 'LED',
      isBreadboardMounted: true,
      left: ledAnodeCoords.x - 22,
      top: ledAnodeCoords.y - 36,
      labelX: ledAnodeCoords.x,
      labelY: -25,
      startCol: sharedCol,
      endCol: ledEndCol,
      pins: ledPins
    });

    this.allocatedPins[`${led.id}.A`] = ledPins['A'];
    this.allocatedPins[`${led.id}.C`] = ledPins['C'];

    this.internalSharedNodes.push({
      col: sharedCol,
      components: [resistor.id, led.id],
      label: `Sütun ${sharedCol}: ${resistor.label} ➔ ${led.label} İç İletkenlik`
    });

    // Sonraki bileşene 4 sütun boşluk bırak (ferah yerleşim)
    this.currentCol = ledEndCol + 4;
  }

  /**
   * Tekil Through-Hole bileşenler (Doğrudan Breadboard Deliklerine Takılır)
   */
  private allocateSingleComponent(comp: NetlistComponent) {
    const col = this.currentCol;

    switch (comp.type) {
      case 'wokwi-photoresistor': {
        // 2 Bacaklı Klasik LDR: 1. Bacak colE, 2. Bacak (col+2)E
        const p1 = getHoleCoords(col, 'E');
        const p2 = getHoleCoords(col + 2, 'E');
        const pins = {
          '1': { componentId: comp.id, pinName: '1', col, row: 'E', holeName: `${col}E`, ...p1 },
          '2': { componentId: comp.id, pinName: '2', col: col + 2, row: 'E', holeName: `${col + 2}E`, ...p2 }
        };
        this.placedComponents.push({
          id: comp.id,
          type: comp.type,
          props: comp.props || {},
          label: comp.label || '2 Bacaklı LDR',
          isBreadboardMounted: true,
          left: p1.x - 8.5,
          top: p1.y - 42,
          labelX: p1.x + 9.5,
          labelY: -25,
          startCol: col,
          endCol: col + 2,
          pins
        });
        this.allocatedPins[`${comp.id}.1`] = pins['1'];
        this.allocatedPins[`${comp.id}.2`] = pins['2'];
        this.currentCol += 5;
        break;
      }

      case 'wokwi-led': {
        const anodeCoords = getHoleCoords(col, 'E');
        const cathodeCoords = getHoleCoords(col + 1, 'E');
        const pins = {
          'A': { componentId: comp.id, pinName: 'A', col, row: 'E', holeName: `${col}E`, ...anodeCoords },
          'C': { componentId: comp.id, pinName: 'C', col: col + 1, row: 'E', holeName: `${col + 1}E`, ...cathodeCoords }
        };
        this.placedComponents.push({
          id: comp.id,
          type: comp.type,
          props: comp.props || {},
          label: comp.label,
          isBreadboardMounted: true,
          left: anodeCoords.x - 22,
          top: anodeCoords.y - 36,
          labelX: anodeCoords.x,
          labelY: -25,
          startCol: col,
          endCol: col + 1,
          pins
        });
        this.allocatedPins[`${comp.id}.A`] = pins['A'];
        this.allocatedPins[`${comp.id}.C`] = pins['C'];
        this.currentCol += 4;
        break;
      }

      case 'wokwi-resistor': {
        const p1 = getHoleCoords(col, 'C');
        const p2 = getHoleCoords(col + 4, 'C');
        const pins = {
          '1': { componentId: comp.id, pinName: '1', col, row: 'C', holeName: `${col}C`, ...p1 },
          '2': { componentId: comp.id, pinName: '2', col: col + 4, row: 'C', holeName: `${col + 4}C`, ...p2 }
        };
        this.placedComponents.push({
          id: comp.id,
          type: comp.type,
          props: comp.props || {},
          label: comp.label,
          isBreadboardMounted: true,
          left: p1.x + 8,
          top: p1.y - 6,
          labelX: p1.x + 15,
          labelY: -25,
          startCol: col,
          endCol: col + 4,
          pins
        });
        this.allocatedPins[`${comp.id}.1`] = pins['1'];
        this.allocatedPins[`${comp.id}.2`] = pins['2'];
        this.currentCol += 6;
        break;
      }

      case 'wokwi-buzzer': {
        const p1 = getHoleCoords(col, 'F');
        const p2 = getHoleCoords(col + 2, 'F');
        const pins = {
          '1': { componentId: comp.id, pinName: '1', col, row: 'F', holeName: `${col}F`, ...p1 },
          '2': { componentId: comp.id, pinName: '2', col: col + 2, row: 'F', holeName: `${col + 2}F`, ...p2 }
        };
        this.placedComponents.push({
          id: comp.id,
          type: comp.type,
          props: comp.props || {},
          label: comp.label || 'Buzzer',
          isBreadboardMounted: true,
          left: p1.x - 14,
          top: p1.y - 10,
          labelX: p1.x + 8,
          labelY: -25,
          startCol: col,
          endCol: col + 2,
          pins
        });
        this.allocatedPins[`${comp.id}.1`] = pins['1'];
        this.allocatedPins[`${comp.id}.2`] = pins['2'];
        this.currentCol += 5;
        break;
      }

      case 'wokwi-pushbutton': {
        const p1 = getHoleCoords(col, 'E');
        const p2 = getHoleCoords(col + 2, 'E');
        const pins = {
          '1': { componentId: comp.id, pinName: '1', col, row: 'E', holeName: `${col}E`, ...p1 },
          '2': { componentId: comp.id, pinName: '2', col: col + 2, row: 'E', holeName: `${col + 2}E`, ...p2 }
        };
        this.placedComponents.push({
          id: comp.id,
          type: comp.type,
          props: comp.props || {},
          label: comp.label || 'Buton',
          isBreadboardMounted: true,
          left: p1.x - 10,
          top: p1.y - 20,
          labelX: p1.x + 8,
          labelY: -25,
          startCol: col,
          endCol: col + 2,
          pins
        });
        this.allocatedPins[`${comp.id}.1`] = pins['1'];
        this.allocatedPins[`${comp.id}.2`] = pins['2'];
        this.currentCol += 5;
        break;
      }

      default: {
        const p1 = getHoleCoords(col, 'E');
        const pins = {
          '1': { componentId: comp.id, pinName: '1', col, row: 'E', holeName: `${col}E`, ...p1 }
        };
        this.placedComponents.push({
          id: comp.id,
          type: comp.type,
          props: comp.props || {},
          label: comp.label,
          isBreadboardMounted: true,
          left: p1.x - 10,
          top: p1.y - 20,
          labelX: p1.x,
          labelY: -25,
          startCol: col,
          endCol: col + 1,
          pins
        });
        this.allocatedPins[`${comp.id}.1`] = pins['1'];
        this.currentCol += 4;
        break;
      }
    }
  }

  /**
   * Modül / Harici Bileşenler (4 Pin LDR, Servo, HC-SR04)
   * Breadboard'u tıkamaz; sağdaki modül dock'unda ferahça durur ve jumper kablolarla bağlanır.
   */
  private allocateOffBoardComponent(comp: NetlistComponent) {
    const dockLeft = 810;
    const dockTop = 130;

    if (comp.type === 'wokwi-photoresistor-sensor') {
      // 4 Pinli LDR Modülü (KY-018)
      // Wokwi elemanı sağ kenarında pinInfo: x=172, y=16(VCC), y=26(GND), y=36(DO), y=46(AO)
      // Scale 0.7 ile: pin x = dockLeft + 120, pin y = dockTop + offset
      const pinX = dockLeft + 120 - 448; // relative to breadboard origin
      const pins: Record<string, AllocatedPin> = {
        'VCC': { componentId: comp.id, pinName: 'VCC', col: 0, row: 'offboard', holeName: 'VCC', x: pinX, y: dockTop + 16 * 0.7 - 108 },
        'GND': { componentId: comp.id, pinName: 'GND', col: 0, row: 'offboard', holeName: 'GND', x: pinX, y: dockTop + 26 * 0.7 - 108 },
        'DO': { componentId: comp.id, pinName: 'DO', col: 0, row: 'offboard', holeName: 'DO', x: pinX, y: dockTop + 36 * 0.7 - 108 },
        'AO': { componentId: comp.id, pinName: 'AO', col: 0, row: 'offboard', holeName: 'AO', x: pinX, y: dockTop + 46 * 0.7 - 108 }
      };

      this.placedComponents.push({
        id: comp.id,
        type: comp.type,
        props: comp.props || {},
        label: comp.label || '4 Pin LDR Modülü (KY-018)',
        isBreadboardMounted: false,
        left: dockLeft,
        top: dockTop,
        labelX: dockLeft + 50,
        labelY: -20,
        startCol: 0,
        endCol: 0,
        pins
      });

      for (const [k, v] of Object.entries(pins)) {
        this.allocatedPins[`${comp.id}.${k}`] = v;
      }
    } else if (comp.type === 'wokwi-servo') {
      const pinX = dockLeft + 40 - 448;
      const pins: Record<string, AllocatedPin> = {
        'GND': { componentId: comp.id, pinName: 'GND', col: 0, row: 'offboard', holeName: 'GND', x: pinX, y: dockTop + 30 - 108 },
        'V+': { componentId: comp.id, pinName: 'V+', col: 0, row: 'offboard', holeName: 'V+', x: pinX, y: dockTop + 45 - 108 },
        'PWM': { componentId: comp.id, pinName: 'PWM', col: 0, row: 'offboard', holeName: 'PWM', x: pinX, y: dockTop + 60 - 108 }
      };

      this.placedComponents.push({
        id: comp.id,
        type: comp.type,
        props: comp.props || {},
        label: comp.label || 'SG90 Servo',
        isBreadboardMounted: false,
        left: dockLeft,
        top: dockTop,
        labelX: dockLeft + 40,
        labelY: -20,
        startCol: 0,
        endCol: 0,
        pins
      });

      for (const [k, v] of Object.entries(pins)) {
        this.allocatedPins[`${comp.id}.${k}`] = v;
      }
    } else if (comp.type === 'wokwi-hc-sr04') {
      const pinX = dockLeft + 50 - 448;
      const pins: Record<string, AllocatedPin> = {
        'VCC': { componentId: comp.id, pinName: 'VCC', col: 0, row: 'offboard', holeName: 'VCC', x: pinX, y: dockTop + 40 - 108 },
        'TRIG': { componentId: comp.id, pinName: 'TRIG', col: 0, row: 'offboard', holeName: 'TRIG', x: pinX, y: dockTop + 50 - 108 },
        'ECHO': { componentId: comp.id, pinName: 'ECHO', col: 0, row: 'offboard', holeName: 'ECHO', x: pinX, y: dockTop + 60 - 108 },
        'GND': { componentId: comp.id, pinName: 'GND', col: 0, row: 'offboard', holeName: 'GND', x: pinX, y: dockTop + 70 - 108 }
      };

      this.placedComponents.push({
        id: comp.id,
        type: comp.type,
        props: comp.props || {},
        label: comp.label || 'HC-SR04 Mesafe Sensörü',
        isBreadboardMounted: false,
        left: dockLeft,
        top: dockTop,
        labelX: dockLeft + 40,
        labelY: -20,
        startCol: 0,
        endCol: 0,
        pins
      });

      for (const [k, v] of Object.entries(pins)) {
        this.allocatedPins[`${comp.id}.${k}`] = v;
      }
    }
  }
}

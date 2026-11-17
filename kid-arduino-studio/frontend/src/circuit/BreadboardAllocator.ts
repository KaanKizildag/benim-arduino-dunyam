/**
 * Katman 2: Dinamik Sütun Tahsis Algoritması (BreadboardAllocator)
 * 1. Güç Rayı Yönetimi (Bus Routing)
 * 2. Çakışmasız Bölge Ayırma (Cursor-Based Packing)
 * 3. Seri Bağlantı Çözücü (Direnç + LED / Buton Zinciri)
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
  private currentCol = 2; // Soldan sağa 2. sütundan başla (1. sütun marjindir)
  private placedComponents: PlacedComponent[] = [];
  private allocatedPins: Record<string, AllocatedPin> = {}; // key: "componentId.pinName"
  private internalSharedNodes: Array<{ col: number; components: string[]; label: string }> = [];

  public allocate(netlist: CircuitNetlist): {
    components: PlacedComponent[];
    allocatedPins: Record<string, AllocatedPin>;
    internalSharedNodes: Array<{ col: number; components: string[]; label: string }>;
  } {
    this.currentCol = 2;
    this.placedComponents = [];
    this.allocatedPins = {};
    this.internalSharedNodes = [];

    const components = [...netlist.components];
    const connections = netlist.connections || [];

    // 1. Seri bağlı Resistor + LED çiftlerini bul (Örn: r1.2 -> led1.A)
    const processedComponentIds = new Set<string>();

    for (const comp of components) {
      if (processedComponentIds.has(comp.id)) continue;

      // Seri bağlantı kontrolü: Eğer comp bir direnç veya buton ise ve doğrudan bir LED'e bağlıysa
      const seriesPartner = this.findSeriesPartner(comp, components, connections, processedComponentIds);

      if (seriesPartner) {
        // İki elemanı seri zincir olarak birlikte yerleştir (aynı sütunu paylaşacaklar)
        this.allocateSeriesPair(comp, seriesPartner.component, seriesPartner.connection);
        processedComponentIds.add(comp.id);
        processedComponentIds.add(seriesPartner.component.id);
      } else if (this.isOffBoardComponent(comp.type)) {
        // Harici elemanlar (Servo, HC-SR04) breadboard dışında durur
        this.allocateOffBoardComponent(comp);
        processedComponentIds.add(comp.id);
      } else {
        // Tekil elemanı breadboard üzerine yerleştir
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

  private isOffBoardComponent(type: string): boolean {
    return type === 'wokwi-servo' || type === 'wokwi-hc-sr04';
  }

  /**
   * Seri bağlı bir partner bulur (Örn: r1.2 -> led1.A)
   */
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
   * Seri bağlı çifti (Resistor + LED) tek bir sütun düğümünde çakışmasız yerleştirir.
   */
  private allocateSeriesPair(compA: NetlistComponent, compB: NetlistComponent, conn: any) {
    // Hangisi direnç, hangisi LED?
    const resistor = compA.type === 'wokwi-resistor' ? compA : compB;
    const led = compA.type === 'wokwi-led' ? compA : compB;

    const startCol = this.currentCol;
    const sharedCol = startCol + 4; // Direnç 4 sütun kaplar, sağ ucu sharedCol'a gelir
    const ledEndCol = sharedCol + 1; // LED anotu sharedCol'da, katotu sharedCol+1'de

    // 1. Direnç Yerleşimi (startCol -> sharedCol, Satır C)
    const rPin1Coords = getHoleCoords(startCol, 'C');
    const rPin2Coords = getHoleCoords(sharedCol, 'C');

    const rPins: Record<string, AllocatedPin> = {
      '1': { componentId: resistor.id, pinName: '1', col: startCol, row: 'C', holeName: `${startCol}C`, ...rPin1Coords },
      '2': { componentId: resistor.id, pinName: '2', col: sharedCol, row: 'C', holeName: `${sharedCol}C`, ...rPin2Coords }
    };

    // Direnç DOM görsel pozisyonu
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

    // 2. LED Yerleşimi (sharedCol -> ledEndCol, Satır E)
    // LED Anot (A) sharedCol'da, LED Katot (C) ledEndCol'da!
    const ledAnodeCoords = getHoleCoords(sharedCol, 'E');
    const ledCathodeCoords = getHoleCoords(ledEndCol, 'E');

    const ledPins: Record<string, AllocatedPin> = {
      'A': { componentId: led.id, pinName: 'A', col: sharedCol, row: 'E', holeName: `${sharedCol}E`, ...ledAnodeCoords },
      'C': { componentId: led.id, pinName: 'C', col: ledEndCol, row: 'E', holeName: `${ledEndCol}E`, ...ledCathodeCoords }
    };

    // Wokwi LED web component ofseti: Anot yerel x=25, Katot yerel x=15
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

    // İç paylaşımlı sütunu kaydet (Sütun sharedCol: Direnç bacağı 2 ve LED Anot)
    this.internalSharedNodes.push({
      col: sharedCol,
      components: [resistor.id, led.id],
      label: `Sütun ${sharedCol}: ${resistor.label} ➔ ${led.label} İç İletkenlik`
    });

    // Cursor'ı ilerlet: kaplanan alan (startCol -> ledEndCol) + 2 güvenlik boşluğu
    this.currentCol = ledEndCol + 2;
  }

  /**
   * Tekil bileşen yerleşimi (LED, Direnç, LDR, Buton, Buzzer, Potansiyometre)
   */
  private allocateSingleComponent(comp: NetlistComponent) {
    const col = this.currentCol;

    switch (comp.type) {
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
        this.currentCol += 3;
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

      case 'wokwi-photoresistor': {
        // 2 Bacaklı Klasik LDR (Foto-direnç): Sütun col ve col+2, Satır E
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
          label: comp.label || 'LDR Foto-direnç',
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
        this.currentCol += 4;
        break;
      }

      case 'wokwi-photoresistor-sensor': {
        // 4 Pinli Kart LDR Sensör Modülü (KY-018):
        // Wokwi elemanında 4 pin dikey olarak sağ kenardadır (x=172, y=16, 26, 35.8, 45.5).
        // Bu pinler breadboard'un tek bir sütunundaki A, B, C, D deliklerine doğrudan oturur!
        const vcc = getHoleCoords(col, 'A');
        const gnd = getHoleCoords(col, 'B');
        const doPin = getHoleCoords(col, 'C');
        const ao = getHoleCoords(col, 'D');

        const pins = {
          'VCC': { componentId: comp.id, pinName: 'VCC', col, row: 'A', holeName: `${col}A`, ...vcc },
          'GND': { componentId: comp.id, pinName: 'GND', col, row: 'B', holeName: `${col}B`, ...gnd },
          'DO': { componentId: comp.id, pinName: 'DO', col, row: 'C', holeName: `${col}C`, ...doPin },
          'AO': { componentId: comp.id, pinName: 'AO', col, row: 'D', holeName: `${col}D`, ...ao }
        };

        this.placedComponents.push({
          id: comp.id,
          type: comp.type,
          props: comp.props || {},
          label: comp.label || '4 Pin LDR Modülü',
          isBreadboardMounted: true,
          left: vcc.x - 172,
          top: 32, // 32 + 16 = 48 (Satır A tam hizası)
          labelX: vcc.x - 40,
          labelY: -25,
          startCol: col,
          endCol: col,
          pins
        });

        for (const [k, v] of Object.entries(pins)) {
          this.allocatedPins[`${comp.id}.${k}`] = v;
        }
        this.currentCol += 2;
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
          label: comp.label,
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
        this.currentCol += 4;
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
          label: comp.label,
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
        this.currentCol += 4;
        break;
      }

      case 'wokwi-potentiometer': {
        const gnd = getHoleCoords(col, 'E');
        const sig = getHoleCoords(col + 1, 'E');
        const vcc = getHoleCoords(col + 2, 'E');
        const pins = {
          'GND': { componentId: comp.id, pinName: 'GND', col, row: 'E', holeName: `${col}E`, ...gnd },
          'SIG': { componentId: comp.id, pinName: 'SIG', col: col + 1, row: 'E', holeName: `${col + 1}E`, ...sig },
          'VCC': { componentId: comp.id, pinName: 'VCC', col: col + 2, row: 'E', holeName: `${col + 2}E`, ...vcc }
        };
        this.placedComponents.push({
          id: comp.id,
          type: comp.type,
          props: comp.props || {},
          label: comp.label,
          isBreadboardMounted: true,
          left: gnd.x - 10,
          top: gnd.y - 25,
          labelX: gnd.x + 8,
          labelY: -25,
          startCol: col,
          endCol: col + 2,
          pins
        });
        this.allocatedPins[`${comp.id}.GND`] = pins['GND'];
        this.allocatedPins[`${comp.id}.SIG`] = pins['SIG'];
        this.allocatedPins[`${comp.id}.VCC`] = pins['VCC'];
        this.currentCol += 4;
        break;
      }

      default: {
        // Genel yedek
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
        this.currentCol += 3;
        break;
      }
    }
  }

  /**
   * Breadboard dışındaki harici bileşenler (Servo, HC-SR04)
   */
  private allocateOffBoardComponent(comp: NetlistComponent) {
    if (comp.type === 'wokwi-servo') {
      const pins: Record<string, AllocatedPin> = {
        'GND': { componentId: comp.id, pinName: 'GND', col: 28, row: 'bn', holeName: 'bn.28', ...getHoleCoords(28, 'bp.-') },
        'V+': { componentId: comp.id, pinName: 'V+', col: 28, row: 'bp', holeName: 'bp.28', ...getHoleCoords(28, 'bp.+') },
        'PWM': { componentId: comp.id, pinName: 'PWM', col: 27, row: 'A', holeName: '27A', ...getHoleCoords(27, 'A') }
      };
      this.placedComponents.push({
        id: comp.id,
        type: comp.type,
        props: comp.props || {},
        label: comp.label,
        isBreadboardMounted: false,
        left: 360,
        top: 24,
        labelX: 380,
        labelY: -20,
        startCol: 27,
        endCol: 28,
        pins
      });
      for (const [k, v] of Object.entries(pins)) {
        this.allocatedPins[`${comp.id}.${k}`] = v;
      }
    } else if (comp.type === 'wokwi-hc-sr04') {
      const pins: Record<string, AllocatedPin> = {
        'VCC': { componentId: comp.id, pinName: 'VCC', col: 25, row: 'bp', holeName: 'bp.25', ...getHoleCoords(25, 'bp.+') },
        'TRIG': { componentId: comp.id, pinName: 'TRIG', col: 24, row: 'A', holeName: '24A', ...getHoleCoords(24, 'A') },
        'ECHO': { componentId: comp.id, pinName: 'ECHO', col: 25, row: 'A', holeName: '25A', ...getHoleCoords(25, 'A') },
        'GND': { componentId: comp.id, pinName: 'GND', col: 26, row: 'bn', holeName: 'bn.26', ...getHoleCoords(26, 'bp.-') }
      };
      this.placedComponents.push({
        id: comp.id,
        type: comp.type,
        props: comp.props || {},
        label: comp.label,
        isBreadboardMounted: false,
        left: 360,
        top: 24,
        labelX: 380,
        labelY: -20,
        startCol: 24,
        endCol: 26,
        pins
      });
      for (const [k, v] of Object.entries(pins)) {
        this.allocatedPins[`${comp.id}.${k}`] = v;
      }
    }
  }
}

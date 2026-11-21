/**
 * Katman 2: Dinamik Sütun ve Net Tabanlı Tahsis Algoritması (BreadboardAllocator)
 * Fiziksel Kurallar:
 * 1. Bir bileşenin iki farklı pini ASLA aynı sütuna bağlanamaz (Kısa Devre Yasağı).
 * 2. Farklı elektriksel net'ler ASLA aynı breadboard sütun şeridini (col + yarı) paylaşamaz.
 * 3. Breadboard üzerinde üst yarıdaki 5 delik (A-B-C-D-E) kendi içinde, alt yarıdaki 5 delik (F-G-H-I-J) kendi içinde bağlıdır.
 * 4. Seri bağlı elemanlar (LED + Direnç, LDR + Direnç, Buton + Pull-down Direnç) bağlantının gerçekten birleştirdiği iki pini ortak sütunda buluşturur.
 * 5. Üst yarı (A–E, sütun 1..30) dolduğunda kalan bileşenler alt yarıya (F–J, sütun 1..30) geçer; yine sığmazsa açık hata üretilir.
 * 6. Modül bileşenleri (4 Pin LDR, Servo, HC-SR04) sağdaki modül dock'unda dikey olarak sıralanır.
 */

import type {
  CircuitNetlist,
  NetlistComponent,
  PlacedComponent,
  AllocatedPin,
  ElectricalNet
} from './types';
import {
  computeOffBoardCardMetrics,
  resolveModulePinInfo
} from './moduleGeometry';

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

export function isUpperHalfRow(row: string): boolean {
  const r = (row || '').toUpperCase();
  return r === 'A' || r === 'B' || r === 'C' || r === 'D' || r === 'E';
}

export function isLowerHalfRow(row: string): boolean {
  const r = (row || '').toUpperCase();
  return r === 'F' || r === 'G' || r === 'H' || r === 'I' || r === 'J';
}

export function getStripKey(col: number, row: string): string {
  if (col < 1 || col > BREADBOARD_GEOMETRY.maxCols) return `offboard:${col}:${row}`;
  if (isUpperHalfRow(row)) return `${col}:upper`;
  if (isLowerHalfRow(row)) return `${col}:lower`;
  return `rail:${row}`;
}

export function getHoleCoords(col: number, row: string): { x: number; y: number } {
  const clampedCol = Math.max(1, Math.min(BREADBOARD_GEOMETRY.maxCols, col));
  const x = BREADBOARD_GEOMETRY.startX + (clampedCol - 1) * BREADBOARD_GEOMETRY.colPitch;

  let y = BREADBOARD_GEOMETRY.rowY.A;
  const rawTrimmed = (row || '').trim();
  const lowerRow = rawTrimmed.toLowerCase();
  const upperRow = rawTrimmed.toUpperCase();

  if (lowerRow in BREADBOARD_GEOMETRY.rowY) {
    y = (BREADBOARD_GEOMETRY.rowY as Record<string, number>)[lowerRow];
  } else if (upperRow in BREADBOARD_GEOMETRY.rowY) {
    y = (BREADBOARD_GEOMETRY.rowY as Record<string, number>)[upperRow];
  } else if (upperRow.startsWith('TN') || upperRow === 'TP.-' || upperRow === 'TOP--') {
    y = BREADBOARD_GEOMETRY.rowY['tp.-'];
  } else if (upperRow.startsWith('TP') || upperRow === 'TP.+' || upperRow === 'TOP-+') {
    y = BREADBOARD_GEOMETRY.rowY['tp.+'];
  } else if (upperRow.startsWith('BN') || upperRow === 'BP.-' || upperRow === 'BOTTOM--' || upperRow === 'GND' || upperRow === '-') {
    y = BREADBOARD_GEOMETRY.rowY['bp.-'];
  } else if (upperRow.startsWith('BP') || upperRow === 'BP.+' || upperRow === 'BOTTOM-+' || upperRow === '5V' || upperRow === '+') {
    y = BREADBOARD_GEOMETRY.rowY['bp.+'];
  }

  return { x, y };
}

interface SeriesPartnerMatch {
  partner: NetlistComponent;
  net: ElectricalNet;
  compPin: string;
  partnerPin: string;
}

export const OFF_BOARD_PIN_DEFS: Record<string, { label: string; pins: string[] }> = {
  'wokwi-servo': { label: 'SG90 Servo Motor', pins: ['PWM', 'V+', 'GND'] },
  'wokwi-hc-sr04': { label: 'HC-SR04 Mesafe Sensörü', pins: ['VCC', 'TRIG', 'ECHO', 'GND'] },
  'wokwi-photoresistor-sensor': { label: 'LDR Işık Sensörü', pins: ['VCC', 'GND', 'DO', 'AO'] },
  'wokwi-hc-05': { label: 'HC-05 Bluetooth Modülü', pins: ['VCC', 'GND', 'TXD', 'RXD'] },
  'wokwi-hc-06': { label: 'HC-06 Bluetooth Modülü', pins: ['VCC', 'GND', 'TXD', 'RXD'] },
  'wokwi-l293d': {
    label: 'L293D Motor Sürücü',
    pins: ['VCC1', 'VCC2', 'GND', 'IN1', 'IN2', 'IN3', 'IN4', 'OUT1', 'OUT2', 'OUT3', 'OUT4', 'EN1', 'EN2']
  },
  'wokwi-l298n': {
    label: 'L298N Motor Sürücü',
    pins: ['VCC', 'GND', '5V', 'IN1', 'IN2', 'IN3', 'IN4', 'OUT1', 'OUT2', 'OUT3', 'OUT4', 'ENA', 'ENB']
  },
  'wokwi-dc-motor': { label: 'DC Motor', pins: ['1', '2'] },
  'wokwi-relay-module': { label: '5V Röle Modülü', pins: ['VCC', 'GND', 'IN'] },
  'wokwi-pir-motion-sensor': { label: 'PIR Hareket Sensörü', pins: ['VCC', 'OUT', 'GND'] },
  'wokwi-dht22': { label: 'DHT22 Sıcaklık/Nem Sensörü', pins: ['VCC', 'SDA', 'GND'] },
  'wokwi-analog-joystick': { label: 'Analog Joystick', pins: ['GND', 'VCC', 'HORZ', 'VERT', 'SEL'] },
  'wokwi-lcd1602': { label: '16x2 LCD Ekran', pins: ['GND', 'VCC', 'SDA', 'SCL'] },
  'wokwi-ssd1306': { label: '0.96 OLED Ekran', pins: ['GND', 'VCC', 'SCL', 'SDA'] },
  'wokwi-soil-moisture-sensor': { label: 'Toprak Nem Sensörü', pins: ['VCC', 'GND', 'DO', 'AO'] },
  'wokwi-rain-sensor': { label: 'Yağmur Sensörü', pins: ['VCC', 'GND', 'DO', 'AO'] },
  'wokwi-water-sensor': { label: 'Su Seviye Sensörü', pins: ['VCC', 'GND', 'AO'] },
  'wokwi-gas-sensor': { label: 'MQ-2 Gaz Sensörü', pins: ['VCC', 'GND', 'DO', 'AO'] },
  'wokwi-flame-sensor': { label: 'Alev Sensörü', pins: ['VCC', 'GND', 'DO', 'AO'] },
  'wokwi-small-sound-sensor': { label: 'Ses Sensörü', pins: ['VCC', 'GND', 'DO', 'AO'] },
  'wokwi-ir-receiver': { label: 'IR Kızılötesi Alıcı', pins: ['OUT', 'GND', 'VCC'] },
  'wokwi-ntc-temperature-sensor': { label: 'NTC Sıcaklık Sensörü', pins: ['VCC', 'GND', 'OUT'] }
};

export class BreadboardAllocator {
  private currentCol = 4;
  private currentHalf: 'upper' | 'lower' = 'upper';
  private offBoardIndex = 0;
  private placedComponents: PlacedComponent[] = [];
  private allocatedPins: Record<string, AllocatedPin> = {};
  private internalSharedNodes: Array<{ col: number; half: 'upper' | 'lower'; components: string[]; label: string }> = [];
  private errors: string[] = [];
  private warnings: string[] = [];

  public allocate(
    netlist: CircuitNetlist,
    nets: ElectricalNet[] = []
  ): {
    components: PlacedComponent[];
    allocatedPins: Record<string, AllocatedPin>;
    internalSharedNodes: Array<{ col: number; half: 'upper' | 'lower'; components: string[]; label: string }>;
    errors: string[];
    warnings: string[];
  } {
    this.currentCol = 4;
    this.currentHalf = 'upper';
    this.offBoardIndex = 0;
    this.placedComponents = [];
    this.allocatedPins = {};
    this.internalSharedNodes = [];
    this.errors = [];
    this.warnings = [];

    const components = [...(netlist.components || [])];
    const processedComponentIds = new Set<string>();

    for (const comp of components) {
      if (processedComponentIds.has(comp.id)) continue;

      if (this.isOffBoardComponent(comp.type)) {
        this.allocateOffBoardComponent(comp);
        processedComponentIds.add(comp.id);
        continue;
      }

      const partnerMatch = this.findSeriesPartner(comp, components, nets, processedComponentIds);
      if (partnerMatch) {
        this.allocateSeriesPair(
          comp,
          partnerMatch.partner,
          partnerMatch.compPin,
          partnerMatch.partnerPin
        );
        processedComponentIds.add(comp.id);
        processedComponentIds.add(partnerMatch.partner.id);
      } else {
        this.allocateSingleComponent(comp);
        processedComponentIds.add(comp.id);
      }
    }

    return {
      components: this.placedComponents,
      allocatedPins: this.allocatedPins,
      internalSharedNodes: this.internalSharedNodes,
      errors: this.errors,
      warnings: this.warnings
    };
  }

  public isOffBoardComponent(type: string): boolean {
    return Boolean(OFF_BOARD_PIN_DEFS[type]);
  }

  private isTwoPinPairable(type: string): boolean {
    return (
      type === 'wokwi-resistor' ||
      type === 'wokwi-led' ||
      type === 'wokwi-photoresistor' ||
      type === 'wokwi-pushbutton' ||
      type === 'wokwi-buzzer'
    );
  }

  private getResistorRow(): string {
    return this.currentHalf === 'upper' ? 'C' : 'H';
  }

  private getComponentRow(): string {
    return this.currentHalf === 'upper' ? 'E' : 'J';
  }

  /**
   * Mevcut yarıda yeterli sütun var mı kontrol eder; üst yarı dolduysa alt yarıya (F–J) geçer.
   */
  private ensureSpace(spanCols: number, labelForError: string): boolean {
    if (this.currentCol + spanCols <= BREADBOARD_GEOMETRY.maxCols) {
      return true;
    }

    if (this.currentHalf === 'upper') {
      this.currentHalf = 'lower';
      this.currentCol = 4;
      this.warnings.push(
        `Breadboard üst yarı (A–E) dolduğu için '${labelForError}' ve sonraki bileşenler alt yarıya (F–J) yerleştirildi.`
      );
      if (this.currentCol + spanCols <= BREADBOARD_GEOMETRY.maxCols) {
        return true;
      }
    }

    this.errors.push(
      `Breadboard kapasitesi aşıldı: '${labelForError}' bileşeni için breadboard üzerinde boş sütun kalmadı (1..30 üst ve alt yarı dolu).`
    );
    return false;
  }

  /**
   * Net tablosuna bakarak bir bileşenin direnç ile seri/ortak düğüm ortağı olup olmadığını bulur.
   */
  private findSeriesPartner(
    comp: NetlistComponent,
    allComps: NetlistComponent[],
    nets: ElectricalNet[],
    processed: Set<string>
  ): SeriesPartnerMatch | null {
    if (!this.isTwoPinPairable(comp.type)) {
      return null;
    }

    for (const net of nets) {
      // Bu net içinde comp'a ait bir pin var mı?
      const compPinFull = net.componentPins.find(p => p.startsWith(`${comp.id}.`));
      if (!compPinFull) continue;
      const compPin = compPinFull.slice(comp.id.length + 1);

      for (const otherPinFull of net.componentPins) {
        if (otherPinFull === compPinFull) continue;
        const dotIdx = otherPinFull.indexOf('.');
        if (dotIdx === -1) continue;
        const partnerId = otherPinFull.slice(0, dotIdx);
        const partnerPin = otherPinFull.slice(dotIdx + 1);

        if (partnerId === comp.id || processed.has(partnerId)) continue;
        const partner = allComps.find(c => c.id === partnerId);
        if (!partner || !this.isTwoPinPairable(partner.type)) continue;

        // Çiftten en az biri direnç olmalı (LED+Direnç, LDR+Direnç, Buton+Direnç vb.)
        if (comp.type !== 'wokwi-resistor' && partner.type !== 'wokwi-resistor') {
          continue;
        }

        // İki bileşenin diğer bacakları da aynı net içinde mi? (Paralel kısa devre ise ortak tek sütuna konamaz)
        const otherCompPin = this.getOtherPinName(comp.type, compPin);
        const otherPartnerPin = this.getOtherPinName(partner.type, partnerPin);
        const bothPinsInSameNet =
          net.componentPins.includes(`${comp.id}.${otherCompPin}`) ||
          net.componentPins.includes(`${partner.id}.${otherPartnerPin}`);
        if (bothPinsInSameNet) continue;

        return {
          partner,
          net,
          compPin,
          partnerPin
        };
      }
    }

    return null;
  }

  private getOtherPinName(type: string, pinName: string): string {
    if (type === 'wokwi-led') {
      return pinName === 'A' ? 'C' : 'A';
    }
    return pinName === '1' ? '2' : '1';
  }

  /**
   * Seri bağlı veya ortak düğümlü çifti (Direnç + LED / LDR / Buton / Buzzer)
   * bağlantının gerçekten birleştirdiği iki pini ortak sütuna (sharedCol) koyarak yerleştirir.
   */
  private allocateSeriesPair(
    compA: NetlistComponent,
    compB: NetlistComponent,
    pinA: string,
    pinB: string
  ): void {
    const isAResistor = compA.type === 'wokwi-resistor' && compB.type !== 'wokwi-resistor';
    const resistor = isAResistor ? compA : compB;
    const otherComp = isAResistor ? compB : compA;
    const resSharedPin = isAResistor ? pinA : pinB;
    const resOtherPin = this.getOtherPinName('wokwi-resistor', resSharedPin);
    const otherSharedPin = isAResistor ? pinB : pinA;
    const otherNonSharedPin = this.getOtherPinName(otherComp.type, otherSharedPin);

    // Durum 1: Direnç + LED Çifti (Direnç 6 sütun = 57px, LED 1 sütun = 9.5px)
    if (otherComp.type === 'wokwi-led') {
      if (!this.ensureSpace(7, `${resistor.label} + ${otherComp.label}`)) return;

      const resRow = this.getResistorRow();
      const ledRow = this.getComponentRow();
      const half = this.currentHalf;

      if (otherSharedPin === 'A') {
        // Direnç solda (startCol .. sharedCol), LED sağda (sharedCol=A .. ledEndCol=C)
        const startCol = this.currentCol;
        const sharedCol = startCol + 6;
        const ledEndCol = sharedCol + 1;

        this.placeResistorAt(resistor, startCol, sharedCol, resRow, resOtherPin, resSharedPin);
        this.placeLedAt(otherComp, sharedCol, ledEndCol, ledRow);

        this.internalSharedNodes.push({
          col: sharedCol,
          half,
          components: [resistor.id, otherComp.id],
          label: `Sütun ${sharedCol}: ${resistor.label} (${resSharedPin}) ➔ ${otherComp.label} (A) İç İletkenlik`
        });

        this.currentCol = ledEndCol + 2;
      } else {
        // Direnç katot (C) tarafında! LED solda (startCol=A .. sharedCol=C), Direnç sağda (sharedCol .. resEndCol)
        const startCol = this.currentCol;
        const sharedCol = startCol + 1;
        const resEndCol = sharedCol + 6;

        this.placeLedAt(otherComp, startCol, sharedCol, ledRow);
        this.placeResistorAt(resistor, sharedCol, resEndCol, resRow, resSharedPin, resOtherPin);

        this.internalSharedNodes.push({
          col: sharedCol,
          half,
          components: [otherComp.id, resistor.id],
          label: `Sütun ${sharedCol}: ${otherComp.label} (C) ➔ ${resistor.label} (${resSharedPin}) İç İletkenlik`
        });

        this.currentCol = resEndCol + 2;
      }
      return;
    }

    // Durum 2: 2 Bacaklı LDR / Buton / Buzzer + Direnç (Gerilim Bölücü veya Pull-down/up)
    if (
      otherComp.type === 'wokwi-photoresistor' ||
      otherComp.type === 'wokwi-pushbutton' ||
      otherComp.type === 'wokwi-buzzer'
    ) {
      const compSpan = otherComp.type === 'wokwi-buzzer' ? 1 : otherComp.type === 'wokwi-pushbutton' ? 7 : 2;
      if (!this.ensureSpace(compSpan + 6, `${otherComp.label} + ${resistor.label}`)) return;

      const startCol = this.currentCol;
      const sharedCol = startCol + compSpan;
      const resEndCol = sharedCol + 6;
      const compRow = this.getComponentRow();
      const resRow = this.getResistorRow();
      const half = this.currentHalf;

      // Diğer bileşen solda (startCol .. sharedCol), ortak pini sharedCol'da
      this.placeTwoPinSpan2At(otherComp, startCol, sharedCol, compRow, otherNonSharedPin, otherSharedPin);
      // Direnç sağda (sharedCol .. resEndCol), ortak pini sharedCol'da
      this.placeResistorAt(resistor, sharedCol, resEndCol, resRow, resSharedPin, resOtherPin);

      this.internalSharedNodes.push({
        col: sharedCol,
        half,
        components: [otherComp.id, resistor.id],
        label: `Sütun ${sharedCol}: ${otherComp.label} (${otherSharedPin}) ➔ ${resistor.label} (${resSharedPin}) İç İletkenlik`
      });

      this.currentCol = resEndCol + 2;
      return;
    }

    // Durum 3: İki Direnç Seri
    if (otherComp.type === 'wokwi-resistor') {
      if (!this.ensureSpace(12, `${otherComp.label} + ${resistor.label}`)) return;

      const startCol = this.currentCol;
      const sharedCol = startCol + 6;
      const endCol = sharedCol + 6;
      const row1 = this.currentHalf === 'upper' ? 'C' : 'H';
      const row2 = this.currentHalf === 'upper' ? 'D' : 'I';
      const half = this.currentHalf;

      this.placeResistorAt(otherComp, startCol, sharedCol, row1, otherNonSharedPin, otherSharedPin);
      this.placeResistorAt(resistor, sharedCol, endCol, row2, resSharedPin, resOtherPin);

      this.internalSharedNodes.push({
        col: sharedCol,
        half,
        components: [otherComp.id, resistor.id],
        label: `Sütun ${sharedCol}: ${otherComp.label} ➔ ${resistor.label} İç İletkenlik`
      });

      this.currentCol = endCol + 2;
    }
  }

  private placeResistorAt(
    resistor: NetlistComponent,
    leftCol: number,
    rightCol: number,
    row: string,
    leftPinName: string,
    rightPinName: string
  ): void {
    const leftCoords = getHoleCoords(leftCol, row);
    const rightCoords = getHoleCoords(rightCol, row);

    const rPins: Record<string, AllocatedPin> = {
      [leftPinName]: {
        componentId: resistor.id,
        pinName: leftPinName,
        col: leftCol,
        row,
        holeName: `${leftCol}${row}`,
        ...leftCoords
      },
      [rightPinName]: {
        componentId: resistor.id,
        pinName: rightPinName,
        col: rightCol,
        row,
        holeName: `${rightCol}${row}`,
        ...rightCoords
      }
    };

    // Wokwi resistor-element pinInfo: Pin 1 = (0, 5.65), Pin 2 = (58.8, 5.65)
    this.placedComponents.push({
      id: resistor.id,
      type: resistor.type,
      props: resistor.props || {},
      label: resistor.label || '220Ω Direnç',
      isBreadboardMounted: true,
      left: leftCoords.x - 1,
      top: leftCoords.y - 5.65,
      labelX: (leftCoords.x + rightCoords.x) / 2,
      labelY: -25,
      startCol: leftCol,
      endCol: rightCol,
      pins: rPins
    });

    this.allocatedPins[`${resistor.id}.${leftPinName}`] = rPins[leftPinName];
    this.allocatedPins[`${resistor.id}.${rightPinName}`] = rPins[rightPinName];
  }

  private placeLedAt(
    led: NetlistComponent,
    anodeCol: number,
    cathodeCol: number,
    row: string
  ): void {
    const anodeCoords = getHoleCoords(anodeCol, row);
    const cathodeCoords = getHoleCoords(cathodeCol, row);
    const isAnodeLeft = anodeCol < cathodeCol;
    const leftPinX = Math.min(anodeCoords.x, cathodeCoords.x);

    const ledPins: Record<string, AllocatedPin> = {
      A: {
        componentId: led.id,
        pinName: 'A',
        col: anodeCol,
        row,
        holeName: `${anodeCol}${row}`,
        ...anodeCoords
      },
      C: {
        componentId: led.id,
        pinName: 'C',
        col: cathodeCol,
        row,
        holeName: `${cathodeCol}${row}`,
        ...cathodeCoords
      }
    };

    // Wokwi led-element pinInfo: flip=true -> A=(15, 42), C=(25, 42); flip=false -> C=(15, 42), A=(25, 42)
    this.placedComponents.push({
      id: led.id,
      type: led.type,
      props: { ...(led.props || {}), flip: isAnodeLeft },
      label: led.label || 'LED',
      isBreadboardMounted: true,
      left: leftPinX - 15,
      top: anodeCoords.y - 42,
      labelX: (anodeCoords.x + cathodeCoords.x) / 2,
      labelY: -25,
      startCol: Math.min(anodeCol, cathodeCol),
      endCol: Math.max(anodeCol, cathodeCol),
      pins: ledPins
    });

    this.allocatedPins[`${led.id}.A`] = ledPins.A;
    this.allocatedPins[`${led.id}.C`] = ledPins.C;
  }

  private placeTwoPinSpan2At(
    comp: NetlistComponent,
    leftCol: number,
    rightCol: number,
    row: string,
    leftPinName: string,
    rightPinName: string
  ): void {
    const pLeft = getHoleCoords(leftCol, row);
    const pRight = getHoleCoords(rightCol, row);
    const pins: Record<string, AllocatedPin> = {
      [leftPinName]: {
        componentId: comp.id,
        pinName: leftPinName,
        col: leftCol,
        row,
        holeName: `${leftCol}${row}`,
        ...pLeft
      },
      [rightPinName]: {
        componentId: comp.id,
        pinName: rightPinName,
        col: rightCol,
        row,
        holeName: `${rightCol}${row}`,
        ...pRight
      }
    };

    let offsetLeft = 0;
    let offsetTop = -32;

    if (comp.type === 'wokwi-photoresistor') {
      // wokwi-photoresistor pinInfo: 1=(8.5, 42), 2=(27.5, 42)
      offsetLeft = -8.5;
      offsetTop = -42;
    } else if (comp.type === 'wokwi-buzzer') {
      // wokwi-buzzer pinInfo: 1=(27, 84), 2=(37, 84)
      offsetLeft = -27;
      offsetTop = -84;
    } else if (comp.type === 'wokwi-pushbutton') {
      // wokwi-pushbutton pinInfo: 2.l=(0, 32), 2.r=(67, 32)
      offsetLeft = 0;
      offsetTop = -32;
    }

    this.placedComponents.push({
      id: comp.id,
      type: comp.type,
      props: comp.props || {},
      label: comp.label || comp.id,
      isBreadboardMounted: true,
      left: pLeft.x + offsetLeft,
      top: pLeft.y + offsetTop,
      labelX: (pLeft.x + pRight.x) / 2,
      labelY: -25,
      startCol: leftCol,
      endCol: rightCol,
      pins
    });

    this.allocatedPins[`${comp.id}.${leftPinName}`] = pins[leftPinName];
    this.allocatedPins[`${comp.id}.${rightPinName}`] = pins[rightPinName];
  }

  /**
   * Tekil Through-Hole bileşenler (Doğrudan Breadboard Deliklerine Takılır)
   */
  private allocateSingleComponent(comp: NetlistComponent): void {
    switch (comp.type) {
      case 'wokwi-photoresistor':
      case 'wokwi-pushbutton':
      case 'wokwi-buzzer': {
        const span = comp.type === 'wokwi-buzzer' ? 1 : comp.type === 'wokwi-pushbutton' ? 7 : 2;
        if (!this.ensureSpace(span, comp.label || comp.id)) return;
        const col = this.currentCol;
        const row = this.getComponentRow();
        this.placeTwoPinSpan2At(comp, col, col + span, row, '1', '2');
        this.currentCol = col + span + 2;
        break;
      }

      case 'wokwi-led': {
        if (!this.ensureSpace(1, comp.label || comp.id)) return;
        const col = this.currentCol;
        const row = this.getComponentRow();
        this.placeLedAt(comp, col, col + 1, row);
        this.currentCol = col + 1 + 2;
        break;
      }

      case 'wokwi-resistor': {
        if (!this.ensureSpace(6, comp.label || comp.id)) return;
        const col = this.currentCol;
        const row = this.getResistorRow();
        this.placeResistorAt(comp, col, col + 6, row, '1', '2');
        this.currentCol = col + 6 + 2;
        break;
      }

      case 'wokwi-potentiometer': {
        // 3 Pinli Potansiyometre: GND (col), SIG (col+1), VCC (col+2)
        if (!this.ensureSpace(2, comp.label || comp.id)) return;
        const col = this.currentCol;
        const row = this.getComponentRow();
        const pGnd = getHoleCoords(col, row);
        const pSig = getHoleCoords(col + 1, row);
        const pVcc = getHoleCoords(col + 2, row);

        const pins: Record<string, AllocatedPin> = {
          GND: {
            componentId: comp.id,
            pinName: 'GND',
            col,
            row,
            holeName: `${col}${row}`,
            ...pGnd
          },
          SIG: {
            componentId: comp.id,
            pinName: 'SIG',
            col: col + 1,
            row,
            holeName: `${col + 1}${row}`,
            ...pSig
          },
          VCC: {
            componentId: comp.id,
            pinName: 'VCC',
            col: col + 2,
            row,
            holeName: `${col + 2}${row}`,
            ...pVcc
          }
        };

        this.placedComponents.push({
          id: comp.id,
          type: comp.type,
          props: comp.props || {},
          label: comp.label || 'Potansiyometre',
          isBreadboardMounted: true,
          left: pGnd.x - 29,
          top: pGnd.y - 68.5,
          labelX: pSig.x,
          labelY: -25,
          startCol: col,
          endCol: col + 2,
          pins
        });

        this.allocatedPins[`${comp.id}.GND`] = pins.GND;
        this.allocatedPins[`${comp.id}.SIG`] = pins.SIG;
        this.allocatedPins[`${comp.id}.VCC`] = pins.VCC;
        this.currentCol = col + 2 + 3;
        break;
      }

      default: {
        // Bilinmeyen / desteklenmeyen tipler için açık hata üret
        this.errors.push(
          `Desteklenmeyen bileşen tipi: '${comp.type}' (${comp.label || comp.id}).`
        );
        break;
      }
    }
  }

  /**
   * Modül / Harici Bileşenler (Bluetooth, Motor Sürücü, DC Motor, Servo, Sensörler vs.)
   * Sağdaki modül dock'unda düzenli olarak sıralanır.
   * Pin soket koordinatları modülün gerçek element pinInfo verisinden deterministik hesaplanır.
   */
  private allocateOffBoardComponent(comp: NetlistComponent): void {
    const colIndex = Math.floor(this.offBoardIndex / 4);
    const rowIndex = this.offBoardIndex % 4;
    const dockLeft = 815 + colIndex * 185;
    const dockTop = 76 + rowIndex * 140;
    this.offBoardIndex++;

    const def = OFF_BOARD_PIN_DEFS[comp.type] || {
      label: comp.label || comp.id,
      pins: ['1', '2']
    };

    const metrics = computeOffBoardCardMetrics(comp.type);
    const pinNames = [...def.pins];
    const totalPins = pinNames.length;

    const cardWidth = metrics ? metrics.cardWidth : Math.max(140, (totalPins - 1) * 22 + 24);
    const cardHeight = metrics ? metrics.cardHeight : 96;
    const elementOffsetX = metrics ? metrics.elementOffsetX : 14;
    const elementOffsetY = metrics ? metrics.elementOffsetY : 28;
    const elementScale = metrics ? metrics.elementScale : 0.7;
    const elementNaturalWidth = metrics ? metrics.elementNaturalWidth : 80;
    const elementNaturalHeight = metrics ? metrics.elementNaturalHeight : 78;

    const fallbackPitch = totalPins > 8 ? 14 : totalPins > 5 ? 18 : totalPins > 3 ? 22 : 28;
    const fallbackSpan = (totalPins - 1) * fallbackPitch;
    const fallbackStartX = Math.round((cardWidth - fallbackSpan) / 2);

    const pins: Record<string, AllocatedPin> = {};
    for (let i = 0; i < pinNames.length; i++) {
      const pName = pinNames[i];
      const pinGeo = resolveModulePinInfo(comp.type, pName);

      let canvasX: number;
      let canvasY: number;
      let side: 'top' | 'bottom' | 'left' | 'right' = 'bottom';

      if (pinGeo && metrics) {
        canvasX = dockLeft + elementOffsetX + pinGeo.x * elementScale;
        canvasY = dockTop + elementOffsetY + pinGeo.y * elementScale;
        side = pinGeo.side;
      } else {
        console.warn(
          `[BreadboardAllocator] '${comp.type}' için '${pName}' pin geometrisi bulunamadı, kart altına fallback uygulanıyor.`
        );
        canvasX = dockLeft + fallbackStartX + i * fallbackPitch;
        canvasY = dockTop + cardHeight - 8;
        side = 'bottom';
      }

      pins[pName] = {
        componentId: comp.id,
        pinName: pName,
        col: 0,
        row: 'offboard',
        holeName: `${comp.id}.${pName}`,
        x: canvasX - 448,
        y: canvasY - 108,
        side
      };
    }

    const mergedProps = {
      ...(metrics?.spec.defaultProps || {}),
      ...(comp.props || {})
    };

    this.placedComponents.push({
      id: comp.id,
      type: comp.type,
      props: mergedProps,
      label: comp.label || def.label,
      isBreadboardMounted: false,
      left: dockLeft,
      top: dockTop,
      width: cardWidth,
      height: cardHeight,
      elementOffsetX,
      elementOffsetY,
      elementScale,
      elementNaturalWidth,
      elementNaturalHeight,
      labelX: dockLeft + Math.round(cardWidth / 2),
      labelY: -20,
      startCol: 0,
      endCol: 0,
      pins
    });

    for (const [k, v] of Object.entries(pins)) {
      this.allocatedPins[`${comp.id}.${k}`] = v;
    }

    // Ek koruma: yaygın pin isim varyasyonları için alias kayıtları
    if (comp.type === 'wokwi-l293d') {
      const gndPin = pins['GND'];
      if (gndPin) {
        this.allocatedPins[`${comp.id}.GND1`] = gndPin;
        this.allocatedPins[`${comp.id}.GND2`] = gndPin;
        this.allocatedPins[`${comp.id}.GND3`] = gndPin;
        this.allocatedPins[`${comp.id}.GND4`] = gndPin;
      }
      if (pins['VCC1']) {
        this.allocatedPins[`${comp.id}.VCC`] = pins['VCC1'];
        this.allocatedPins[`${comp.id}.5V`] = pins['VCC1'];
      }
      if (pins['VCC2']) {
        this.allocatedPins[`${comp.id}.VIN`] = pins['VCC2'];
        this.allocatedPins[`${comp.id}.VM`] = pins['VCC2'];
      }
    } else if (comp.type === 'wokwi-hc-05' || comp.type === 'wokwi-hc-06') {
      if (pins['TXD']) this.allocatedPins[`${comp.id}.TX`] = pins['TXD'];
      if (pins['RXD']) this.allocatedPins[`${comp.id}.RX`] = pins['RXD'];
    } else if (comp.type === 'wokwi-ntc-temperature-sensor') {
      if (pins['OUT']) this.allocatedPins[`${comp.id}.1`] = pins['OUT'];
      if (pins['GND']) this.allocatedPins[`${comp.id}.2`] = pins['GND'];
    }
  }
}

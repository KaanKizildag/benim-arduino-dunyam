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

interface SeriesPartnerMatch {
  partner: NetlistComponent;
  net: ElectricalNet;
  compPin: string;
  partnerPin: string;
}

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
    return (
      type === 'wokwi-servo' ||
      type === 'wokwi-hc-sr04' ||
      type === 'wokwi-photoresistor-sensor'
    );
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

    // Durum 1: Direnç + LED Çifti
    if (otherComp.type === 'wokwi-led') {
      if (!this.ensureSpace(5, `${resistor.label} + ${otherComp.label}`)) return;

      const resRow = this.getResistorRow();
      const ledRow = this.getComponentRow();
      const half = this.currentHalf;

      if (otherSharedPin === 'A') {
        // Direnç solda (startCol .. sharedCol), LED sağda (sharedCol=A .. ledEndCol=C)
        const startCol = this.currentCol;
        const sharedCol = startCol + 4;
        const ledEndCol = sharedCol + 1;

        this.placeResistorAt(resistor, startCol, sharedCol, resRow, resOtherPin, resSharedPin);
        this.placeLedAt(otherComp, sharedCol, ledEndCol, ledRow);

        this.internalSharedNodes.push({
          col: sharedCol,
          half,
          components: [resistor.id, otherComp.id],
          label: `Sütun ${sharedCol}: ${resistor.label} (${resSharedPin}) ➔ ${otherComp.label} (A) İç İletkenlik`
        });

        this.currentCol = ledEndCol + 3;
      } else {
        // Direnç katot (C) tarafında! LED solda (startCol=A .. sharedCol=C), Direnç sağda (sharedCol .. resEndCol)
        const startCol = this.currentCol;
        const sharedCol = startCol + 1;
        const resEndCol = sharedCol + 4;

        this.placeLedAt(otherComp, startCol, sharedCol, ledRow);
        this.placeResistorAt(resistor, sharedCol, resEndCol, resRow, resSharedPin, resOtherPin);

        this.internalSharedNodes.push({
          col: sharedCol,
          half,
          components: [otherComp.id, resistor.id],
          label: `Sütun ${sharedCol}: ${otherComp.label} (C) ➔ ${resistor.label} (${resSharedPin}) İç İletkenlik`
        });

        this.currentCol = resEndCol + 3;
      }
      return;
    }

    // Durum 2: 2 Bacaklı LDR / Buton / Buzzer + Direnç (Gerilim Bölücü veya Pull-down/up)
    if (
      otherComp.type === 'wokwi-photoresistor' ||
      otherComp.type === 'wokwi-pushbutton' ||
      otherComp.type === 'wokwi-buzzer'
    ) {
      if (!this.ensureSpace(6, `${otherComp.label} + ${resistor.label}`)) return;

      const startCol = this.currentCol;
      const sharedCol = startCol + 2;
      const resEndCol = sharedCol + 4;
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

      this.currentCol = resEndCol + 3;
      return;
    }

    // Durum 3: İki Direnç Seri
    if (otherComp.type === 'wokwi-resistor') {
      if (!this.ensureSpace(8, `${otherComp.label} + ${resistor.label}`)) return;

      const startCol = this.currentCol;
      const sharedCol = startCol + 4;
      const endCol = sharedCol + 4;
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

      this.currentCol = endCol + 3;
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

    this.placedComponents.push({
      id: resistor.id,
      type: resistor.type,
      props: resistor.props || {},
      label: resistor.label || '220Ω Direnç',
      isBreadboardMounted: true,
      left: leftCoords.x + 8,
      top: leftCoords.y - 6,
      labelX: leftCoords.x + 15,
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

    this.placedComponents.push({
      id: led.id,
      type: led.type,
      props: led.props || {},
      label: led.label || 'LED',
      isBreadboardMounted: true,
      left: anodeCoords.x - 22,
      top: anodeCoords.y - 36,
      labelX: anodeCoords.x,
      labelY: -25,
      startCol: anodeCol,
      endCol: cathodeCol,
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

    let offsetLeft = -10;
    let offsetTop = -20;
    let labelOffset = 8;

    if (comp.type === 'wokwi-photoresistor') {
      offsetLeft = -8.5;
      offsetTop = -42;
      labelOffset = 9.5;
    } else if (comp.type === 'wokwi-buzzer') {
      offsetLeft = -14;
      offsetTop = -10;
      labelOffset = 8;
    }

    this.placedComponents.push({
      id: comp.id,
      type: comp.type,
      props: comp.props || {},
      label: comp.label || comp.id,
      isBreadboardMounted: true,
      left: pLeft.x + offsetLeft,
      top: pLeft.y + offsetTop,
      labelX: pLeft.x + labelOffset,
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
        if (!this.ensureSpace(2, comp.label || comp.id)) return;
        const col = this.currentCol;
        const row = this.getComponentRow();
        this.placeTwoPinSpan2At(comp, col, col + 2, row, '1', '2');
        this.currentCol = col + 2 + 3;
        break;
      }

      case 'wokwi-led': {
        if (!this.ensureSpace(1, comp.label || comp.id)) return;
        const col = this.currentCol;
        const row = this.getComponentRow();
        this.placeLedAt(comp, col, col + 1, row);
        this.currentCol = col + 1 + 3;
        break;
      }

      case 'wokwi-resistor': {
        if (!this.ensureSpace(4, comp.label || comp.id)) return;
        const col = this.currentCol;
        const row = this.getResistorRow();
        this.placeResistorAt(comp, col, col + 4, row, '1', '2');
        this.currentCol = col + 4 + 3;
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
   * Modül / Harici Bileşenler (4 Pin LDR, Servo, HC-SR04)
   * Sağdaki modül dock'unda dikey olarak sıralanır (üst üste binmez).
   */
  private allocateOffBoardComponent(comp: NetlistComponent): void {
    const dockLeft = 810;
    const dockTop = 80 + this.offBoardIndex * 115;
    this.offBoardIndex++;

    if (comp.type === 'wokwi-photoresistor-sensor') {
      const pinX = dockLeft + 120 - 448; // breadboard orijinine (448, 108) göre
      const pins: Record<string, AllocatedPin> = {
        VCC: {
          componentId: comp.id,
          pinName: 'VCC',
          col: 0,
          row: 'offboard',
          holeName: `${comp.id}.VCC`,
          x: pinX,
          y: dockTop + 16 * 0.75 - 108
        },
        GND: {
          componentId: comp.id,
          pinName: 'GND',
          col: 0,
          row: 'offboard',
          holeName: `${comp.id}.GND`,
          x: pinX,
          y: dockTop + 26 * 0.75 - 108
        },
        DO: {
          componentId: comp.id,
          pinName: 'DO',
          col: 0,
          row: 'offboard',
          holeName: `${comp.id}.DO`,
          x: pinX,
          y: dockTop + 36 * 0.75 - 108
        },
        AO: {
          componentId: comp.id,
          pinName: 'AO',
          col: 0,
          row: 'offboard',
          holeName: `${comp.id}.AO`,
          x: pinX,
          y: dockTop + 46 * 0.75 - 108
        }
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
      const pinX = dockLeft + 16 - 448;
      const pins: Record<string, AllocatedPin> = {
        GND: {
          componentId: comp.id,
          pinName: 'GND',
          col: 0,
          row: 'offboard',
          holeName: `${comp.id}.GND`,
          x: pinX,
          y: dockTop + 38 - 108
        },
        'V+': {
          componentId: comp.id,
          pinName: 'V+',
          col: 0,
          row: 'offboard',
          holeName: `${comp.id}.V+`,
          x: pinX,
          y: dockTop + 46 - 108
        },
        PWM: {
          componentId: comp.id,
          pinName: 'PWM',
          col: 0,
          row: 'offboard',
          holeName: `${comp.id}.PWM`,
          x: pinX,
          y: dockTop + 54 - 108
        }
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
      const basePinX = dockLeft + 54 - 448;
      const pinY = dockTop + 72 - 108;
      const pins: Record<string, AllocatedPin> = {
        VCC: {
          componentId: comp.id,
          pinName: 'VCC',
          col: 0,
          row: 'offboard',
          holeName: `${comp.id}.VCC`,
          x: basePinX,
          y: pinY
        },
        TRIG: {
          componentId: comp.id,
          pinName: 'TRIG',
          col: 0,
          row: 'offboard',
          holeName: `${comp.id}.TRIG`,
          x: basePinX + 8,
          y: pinY
        },
        ECHO: {
          componentId: comp.id,
          pinName: 'ECHO',
          col: 0,
          row: 'offboard',
          holeName: `${comp.id}.ECHO`,
          x: basePinX + 16,
          y: pinY
        },
        GND: {
          componentId: comp.id,
          pinName: 'GND',
          col: 0,
          row: 'offboard',
          holeName: `${comp.id}.GND`,
          x: basePinX + 24,
          y: pinY
        }
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

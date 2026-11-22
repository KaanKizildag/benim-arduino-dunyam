/**
 * Off-Board Modül Geometrisi ve Pin Doğruluk Kaynağı (moduleGeometry.ts)
 *
 * - Özel (custom) modüllerin pinInfo ve boyutları doğrudan wokwi-custom-modules.ts'den import edilir.
 * - Gerçek @wokwi/elements modüllerinin doğal boyutları (96dpi, 1mm = 3.7795275591px) ve pinInfo koordinatları
 *   node_modules/@wokwi/elements kaynaklarıyla birebir eşleştirilmiştir.
 * - Her off-board kartın boyutu, iç element ofseti (origin: top left) ve soket koordinatları
 *   bu tek kaynaktan deterministik olarak hesaplanır.
 */

import { CUSTOM_MODULE_METADATA, type CustomPinInfo } from '../components/wokwi-custom-modules';

export type PinSide = 'top' | 'bottom' | 'left' | 'right';

export interface ModulePinGeometry {
  name: string;
  x: number;
  y: number;
  side: PinSide;
}

export interface ModuleGeometrySpec {
  width: number;
  height: number;
  scale: number;
  defaultProps?: Record<string, any>;
  pins: ModulePinGeometry[];
}

export interface OffBoardCardMetrics {
  cardWidth: number;
  cardHeight: number;
  elementOffsetX: number;
  elementOffsetY: number;
  elementScale: number;
  elementNaturalWidth: number;
  elementNaturalHeight: number;
  spec: ModuleGeometrySpec;
}

const MM_TO_PX = 96 / 25.4; // 3.7795275590551185

export function inferPinSide(x: number, y: number, width: number, height: number): PinSide {
  const distLeft = x;
  const distRight = width - x;
  const distTop = y;
  const distBottom = height - y;
  const minDist = Math.min(distLeft, distRight, distTop, distBottom);

  if (minDist === distLeft) return 'left';
  if (minDist === distRight) return 'right';
  if (minDist === distTop) return 'top';
  return 'bottom';
}

function buildPins(rawPins: CustomPinInfo[], width: number, height: number): ModulePinGeometry[] {
  return rawPins.map(p => ({
    name: p.name,
    x: p.x,
    y: p.y,
    side: inferPinSide(p.x, p.y, width, height)
  }));
}

function fromCustomMeta(type: string, scale: number): ModuleGeometrySpec {
  const meta = CUSTOM_MODULE_METADATA[type];
  return {
    width: meta.width,
    height: meta.height,
    scale,
    pins: buildPins(meta.pinInfo, meta.width, meta.height)
  };
}

/**
 * Tüm desteklenen off-board modüllerin gerçek doğal boyut, ölçek ve pinInfo tablosu.
 */
export const MODULE_GEOMETRY: Record<string, ModuleGeometrySpec> = {
  // ---- Custom Wokwi Modülleri (wokwi-custom-modules.ts'den import edilir) ----
  'wokwi-hc-05': fromCustomMeta('wokwi-hc-05', 0.85),
  'wokwi-hc-06': fromCustomMeta('wokwi-hc-06', 0.85),
  'wokwi-l293d': fromCustomMeta('wokwi-l293d', 0.92),
  'wokwi-l298n': fromCustomMeta('wokwi-l298n', 0.92),
  'wokwi-dc-motor': fromCustomMeta('wokwi-dc-motor', 0.85),
  'wokwi-relay-module': fromCustomMeta('wokwi-relay-module', 0.85),
  'wokwi-soil-moisture-sensor': fromCustomMeta('wokwi-soil-moisture-sensor', 0.85),
  'wokwi-rain-sensor': fromCustomMeta('wokwi-rain-sensor', 0.85),
  'wokwi-water-sensor': fromCustomMeta('wokwi-water-sensor', 0.85),

  // ---- Resmi @wokwi/elements Modülleri ----
  'wokwi-servo': (() => {
    const width = 45 * MM_TO_PX; // ~170.08px
    const height = 31.63 * MM_TO_PX; // ~119.55px
    return {
      width,
      height,
      scale: 0.62,
      pins: buildPins(
        [
          { name: 'GND', x: 0, y: 50 },
          { name: 'V+', x: 0, y: 59.5 },
          { name: 'PWM', x: 0, y: 69 }
        ],
        width,
        height
      )
    };
  })(),

  'wokwi-hc-sr04': (() => {
    const width = 45 * MM_TO_PX; // ~170.08px
    const height = 25 * MM_TO_PX; // ~94.49px
    return {
      width,
      height,
      scale: 0.68,
      pins: buildPins(
        [
          { name: 'VCC', x: 71.3, y: 94.5 },
          { name: 'TRIG', x: 81.3, y: 94.5 },
          { name: 'ECHO', x: 91.3, y: 94.5 },
          { name: 'GND', x: 101.3, y: 94.5 }
        ],
        width,
        height
      )
    };
  })(),

  'wokwi-photoresistor-sensor': (() => {
    const width = 45.95 * MM_TO_PX; // ~173.67px
    const height = 16.267 * MM_TO_PX; // ~61.48px
    return {
      width,
      height,
      scale: 0.68,
      pins: buildPins(
        [
          { name: 'VCC', x: 172, y: 16 },
          { name: 'GND', x: 172, y: 26 },
          { name: 'DO', x: 172, y: 35.8 },
          { name: 'AO', x: 172, y: 45.5 }
        ],
        width,
        height
      )
    };
  })(),

  'wokwi-pir-motion-sensor': (() => {
    const width = 24 * MM_TO_PX; // ~90.71px
    const height = 24.448 * MM_TO_PX; // ~92.40px
    return {
      width,
      height,
      scale: 0.78,
      pins: buildPins(
        [
          { name: 'VCC', x: 36.178, y: 92 },
          { name: 'OUT', x: 45.9175, y: 92 },
          { name: 'GND', x: 55.6415, y: 92 }
        ],
        width,
        height
      )
    };
  })(),

  'wokwi-dht22': (() => {
    const width = 15.1 * MM_TO_PX; // ~57.07px
    const height = 30.885 * MM_TO_PX; // ~116.73px
    return {
      width,
      height,
      scale: 0.72,
      pins: buildPins(
        [
          { name: 'VCC', x: 15, y: 114.9 },
          { name: 'SDA', x: 24.5, y: 114.9 },
          { name: 'NC', x: 34.1, y: 114.9 },
          { name: 'GND', x: 43.8, y: 114.9 }
        ],
        width,
        height
      )
    };
  })(),

  'wokwi-analog-joystick': (() => {
    const width = 27.2 * MM_TO_PX; // ~102.80px
    const height = 31.8 * MM_TO_PX; // ~120.19px
    return {
      width,
      height,
      scale: 0.68,
      pins: buildPins(
        [
          { name: 'VCC', x: 33, y: 115.8 },
          { name: 'VERT', x: 42.6012, y: 115.8 },
          { name: 'HORZ', x: 52.2024, y: 115.8 },
          { name: 'SEL', x: 61.8036, y: 115.8 },
          { name: 'GND', x: 71.4048, y: 115.8 }
        ],
        width,
        height
      )
    };
  })(),

  'wokwi-lcd1602': (() => {
    // 16x2 LCD: panelWidth=56.2mm, width=80mm, height=36mm; I2C pinleri sol kenarda
    const width = 80 * MM_TO_PX; // ~302.36px
    const height = 36 * MM_TO_PX; // ~136.06px
    return {
      width,
      height,
      scale: 0.5,
      defaultProps: { pins: 'i2c' },
      pins: buildPins(
        [
          { name: 'GND', x: 4, y: 32 },
          { name: 'VCC', x: 4, y: 41.5 },
          { name: 'SDA', x: 4, y: 51 },
          { name: 'SCL', x: 4, y: 60.5 }
        ],
        width,
        height
      )
    };
  })(),

  'wokwi-ssd1306': (() => {
    const width = 150;
    const height = 116;
    return {
      width,
      height,
      scale: 0.65,
      pins: buildPins(
        [
          { name: 'DATA', x: 36.5, y: 12.5 },
          { name: 'CLK', x: 45.5, y: 12.5 },
          { name: 'DC', x: 54.5, y: 12.5 },
          { name: 'RST', x: 64.5, y: 12.5 },
          { name: 'CS', x: 74.5, y: 12.5 },
          { name: '3V3', x: 83.5, y: 12.5 },
          { name: 'VIN', x: 93.5, y: 12.5 },
          { name: 'GND', x: 103.5, y: 12 }
        ],
        width,
        height
      )
    };
  })(),

  'wokwi-gas-sensor': (() => {
    const width = 36.232 * MM_TO_PX; // ~136.94px
    const height = 16.617 * MM_TO_PX; // ~62.80px
    return {
      width,
      height,
      scale: 0.72,
      pins: buildPins(
        [
          { name: 'AOUT', x: 137, y: 16.5 },
          { name: 'DOUT', x: 137, y: 26.4 },
          { name: 'GND', x: 137, y: 36.5 },
          { name: 'VCC', x: 137, y: 46.2 }
        ],
        width,
        height
      )
    };
  })(),

  'wokwi-flame-sensor': (() => {
    const width = 52.904 * MM_TO_PX; // ~199.95px
    const height = 16.267 * MM_TO_PX; // ~61.48px
    return {
      width,
      height,
      scale: 0.58,
      pins: buildPins(
        [
          { name: 'VCC', x: 199, y: 14.6 },
          { name: 'GND', x: 199, y: 24.3 },
          { name: 'DOUT', x: 199, y: 34 },
          { name: 'AOUT', x: 199, y: 43.7 }
        ],
        width,
        height
      )
    };
  })(),

  'wokwi-small-sound-sensor': (() => {
    const width = 35.211 * MM_TO_PX; // ~133.08px
    const height = 13.346 * MM_TO_PX; // ~50.44px
    return {
      width,
      height,
      scale: 0.72,
      pins: buildPins(
        [
          { name: 'AOUT', x: 0, y: 11 },
          { name: 'GND', x: 0, y: 20.5 },
          { name: 'VCC', x: 0, y: 30.5 },
          { name: 'DOUT', x: 0, y: 40.5 }
        ],
        width,
        height
      )
    };
  })(),

  'wokwi-ir-receiver': (() => {
    const width = 16.178 * MM_TO_PX; // ~61.15px
    const height = 23.482 * MM_TO_PX; // ~88.75px
    return {
      width,
      height,
      scale: 0.8,
      pins: buildPins(
        [
          { name: 'GND', x: 20.977, y: 87.75 },
          { name: 'VCC', x: 30.578, y: 87.75 },
          { name: 'DAT', x: 40.18, y: 87.75 }
        ],
        width,
        height
      )
    };
  })(),

  'wokwi-ntc-temperature-sensor': (() => {
    const width = 35.826 * MM_TO_PX; // ~135.41px
    const height = 19 * MM_TO_PX; // ~71.81px
    return {
      width,
      height,
      scale: 0.7,
      pins: buildPins(
        [
          { name: 'GND', x: 135, y: 26.2 },
          { name: 'VCC', x: 135, y: 35.8 },
          { name: 'OUT', x: 135, y: 45.5 }
        ],
        width,
        height
      )
    };
  })()
};

const PIN_ALIAS_MAP: Record<string, string[]> = {
  TX: ['TXD'],
  TXD: ['TX'],
  RX: ['RXD'],
  RXD: ['RX'],
  AO: ['AOUT', 'OUT'],
  AOUT: ['AO', 'OUT'],
  DO: ['DOUT'],
  DOUT: ['DO'],
  OUT: ['DAT', 'AOUT', 'AO', 'SDA'],
  DAT: ['OUT', 'DATA'],
  DATA: ['SDA', 'DAT'],
  SDA: ['DATA', 'DAT'],
  SCL: ['CLK'],
  CLK: ['SCL'],
  VCC: ['V+', 'VIN', 'VCC1', 'VDD', '5V', '3V3'],
  'V+': ['VCC', '5V', 'VIN'],
  '5V': ['VCC', 'V+', 'VIN', 'VCC1'],
  VIN: ['VCC', 'VCC2', 'V+'],
  GND: ['VSS', 'GND1', 'GND2', 'GND3', 'GND4'],
  SIG: ['PWM', 'OUT', 'IN', 'DAT'],
  PWM: ['SIG', 'IN'],
  '1': ['OUT', 'VCC', '1'],
  '2': ['GND', '2']
};

/**
 * Bir netlist pin adını (örn. "TX", "AO", "SDA", "VCC") ilgili modülün gerçek pinInfo girdisiyle eşler.
 */
export function resolveModulePinInfo(
  type: string,
  netlistPinName: string
): ModulePinGeometry | undefined {
  const spec = MODULE_GEOMETRY[type];
  if (!spec) return undefined;

  const target = (netlistPinName || '').trim().toUpperCase();
  const exact = spec.pins.find(p => p.name.toUpperCase() === target);
  if (exact) return exact;

  const aliases = PIN_ALIAS_MAP[target] || [];
  for (const alias of aliases) {
    const match = spec.pins.find(p => p.name.toUpperCase() === alias);
    if (match) return match;
  }

  return undefined;
}

/**
 * Off-board modül kartının boyutunu ve elementin kart içi (top-left) ofsetini deterministik olarak hesaplar.
 */
export function computeOffBoardCardMetrics(type: string): OffBoardCardMetrics | undefined {
  const spec = MODULE_GEOMETRY[type];
  if (!spec) return undefined;

  const scaledW = spec.width * spec.scale;
  const scaledH = spec.height * spec.scale;

  const hasLeftPins = spec.pins.some(p => p.side === 'left');
  const hasRightPins = spec.pins.some(p => p.side === 'right');
  const hasTopPins = spec.pins.some(p => p.side === 'top');
  const hasBottomPins = spec.pins.some(p => p.side === 'bottom');

  const headerH = 22;
  const padLeft = hasLeftPins ? 26 : 14;
  const padRight = hasRightPins ? 26 : 14;
  const padTop = hasTopPins ? headerH + 16 : headerH + 6;
  const padBottom = hasBottomPins ? 20 : 12;

  const rawWidth = Math.ceil(padLeft + scaledW + padRight);
  const cardWidth = Math.max(118, rawWidth);
  const cardHeight = Math.ceil(padTop + scaledH + padBottom);

  // Dar modüllerde elementi yatayda ortala ama sol/sağ pin boşluğunu koru
  const extraX = cardWidth - rawWidth;
  const elementOffsetX = Math.round(padLeft + extraX / 2);
  const elementOffsetY = padTop;

  return {
    cardWidth,
    cardHeight,
    elementOffsetX,
    elementOffsetY,
    elementScale: spec.scale,
    elementNaturalWidth: spec.width,
    elementNaturalHeight: spec.height,
    spec
  };
}

/**
 * Custom Web Components for Extended KidArduino Studio Hardware Catalog:
 * - wokwi-hc-05 & wokwi-hc-06 (Bluetooth Serial Modules)
 * - wokwi-l293d & wokwi-l298n (Dual H-Bridge Motor Driver Modules)
 * - wokwi-dc-motor (5V Toy Car DC Gear Motor)
 * - wokwi-relay-module (5V Single Channel Relay Module)
 * - wokwi-soil-moisture-sensor (Capacitive/Resistive Soil Moisture Probe)
 * - wokwi-rain-sensor (Raindrop Detection Board)
 * - wokwi-water-sensor (Water Level Sensor)
 */

export interface CustomPinInfo {
  name: string;
  x: number;
  y: number;
}

export interface CustomModuleMeta {
  width: number;
  height: number;
  pinInfo: CustomPinInfo[];
}

// Node.js test ortamında (verifyScenarios.ts) güvenle import edilebilmesi için koruma
const BaseHTMLElement: typeof HTMLElement =
  typeof HTMLElement !== 'undefined'
    ? HTMLElement
    : (class {} as unknown as typeof HTMLElement);

// ---------------------------------------------------------------------------
// Tek Doğruluk Kaynağı: Statik Boyut ve Pin Koordinatları (SVG ile birebir)
// ---------------------------------------------------------------------------

export const HC05_META: CustomModuleMeta = {
  width: 80,
  height: 78,
  pinInfo: [
    { name: 'VCC', x: 16, y: 75 },
    { name: 'GND', x: 32, y: 75 },
    { name: 'TXD', x: 48, y: 75 },
    { name: 'RXD', x: 64, y: 75 }
  ]
};

export const L293D_META: CustomModuleMeta = {
  width: 140,
  height: 84,
  pinInfo: [
    { name: 'OUT1', x: 4, y: 28 },
    { name: 'OUT2', x: 4, y: 46 },
    { name: 'OUT3', x: 136, y: 28 },
    { name: 'OUT4', x: 136, y: 46 },
    { name: 'VCC1', x: 14, y: 80 },
    { name: 'VCC2', x: 28, y: 80 },
    { name: 'GND', x: 42, y: 80 },
    { name: 'EN1', x: 56, y: 80 },
    { name: 'IN1', x: 70, y: 80 },
    { name: 'IN2', x: 84, y: 80 },
    { name: 'IN3', x: 98, y: 80 },
    { name: 'IN4', x: 112, y: 80 },
    { name: 'EN2', x: 126, y: 80 }
  ]
};

export const L298N_META: CustomModuleMeta = {
  width: 140,
  height: 84,
  pinInfo: [
    { name: 'OUT1', x: 4, y: 28 },
    { name: 'OUT2', x: 4, y: 46 },
    { name: 'OUT3', x: 136, y: 28 },
    { name: 'OUT4', x: 136, y: 46 },
    { name: 'VCC', x: 14, y: 80 },
    { name: 'GND', x: 28, y: 80 },
    { name: '5V', x: 42, y: 80 },
    { name: 'ENA', x: 56, y: 80 },
    { name: 'IN1', x: 70, y: 80 },
    { name: 'IN2', x: 84, y: 80 },
    { name: 'IN3', x: 98, y: 80 },
    { name: 'IN4', x: 112, y: 80 },
    { name: 'ENB', x: 126, y: 80 }
  ]
};

export const DC_MOTOR_META: CustomModuleMeta = {
  width: 80,
  height: 78,
  pinInfo: [
    { name: '1', x: 26, y: 75 },
    { name: '2', x: 54, y: 75 }
  ]
};

export const RELAY_MODULE_META: CustomModuleMeta = {
  width: 80,
  height: 78,
  pinInfo: [
    { name: 'VCC', x: 22, y: 75 },
    { name: 'GND', x: 40, y: 75 },
    { name: 'IN', x: 58, y: 75 }
  ]
};

export const PROBE_4PIN_META: CustomModuleMeta = {
  width: 80,
  height: 78,
  pinInfo: [
    { name: 'VCC', x: 16, y: 75 },
    { name: 'GND', x: 32, y: 75 },
    { name: 'DO', x: 48, y: 75 },
    { name: 'AO', x: 64, y: 75 }
  ]
};

export const WATER_SENSOR_META: CustomModuleMeta = {
  width: 80,
  height: 78,
  pinInfo: [
    { name: 'VCC', x: 22, y: 75 },
    { name: 'GND', x: 40, y: 75 },
    { name: 'AO', x: 58, y: 75 }
  ]
};

export const CUSTOM_MODULE_METADATA: Record<string, CustomModuleMeta> = {
  'wokwi-hc-05': HC05_META,
  'wokwi-hc05': HC05_META,
  'wokwi-hc-06': HC05_META,
  'wokwi-hc06': HC05_META,
  'wokwi-l293d': L293D_META,
  'wokwi-l298n': L298N_META,
  'wokwi-dc-motor': DC_MOTOR_META,
  'wokwi-dcmotor': DC_MOTOR_META,
  'wokwi-relay-module': RELAY_MODULE_META,
  'wokwi-soil-moisture-sensor': PROBE_4PIN_META,
  'wokwi-rain-sensor': PROBE_4PIN_META,
  'wokwi-water-sensor': WATER_SENSOR_META
};

/**
 * 1. Bluetooth Modülü (HC-05 / HC-06)
 */
export class WokwiBluetoothModuleElement extends BaseHTMLElement {
  public pinInfo: CustomPinInfo[] = HC05_META.pinInfo;
  private shadow: ShadowRoot;
  private modelLabel: string;

  constructor(modelLabel = 'HC-05') {
    super();
    this.modelLabel = modelLabel;
    this.shadow = this.attachShadow({ mode: 'open' });
    this.render();
  }

  private render() {
    this.shadow.innerHTML = `
      <style>
        :host { display: inline-block; width: 80px; height: 78px; user-select: none; }
        svg { width: 100%; height: 100%; display: block; filter: drop-shadow(0 4px 6px rgba(15,23,42,0.3)); }
      </style>
      <svg viewBox="0 0 80 78" xmlns="http://www.w3.org/2000/svg">
        <!-- Blue PCB Base -->
        <rect x="6" y="4" width="68" height="62" rx="6" fill="#1d4ed8" stroke="#1e3a8a" stroke-width="2" />
        <!-- Gold ZigZag Bluetooth Antenna -->
        <path d="M 16 12 L 26 12 L 26 17 L 16 17 L 16 22 L 28 22" fill="none" stroke="#facc15" stroke-width="2" stroke-linecap="round" />
        <!-- Green Daughterboard IC -->
        <rect x="32" y="10" width="36" height="36" rx="3" fill="#047857" stroke="#34d399" stroke-width="1.2" />
        <rect x="40" y="17" width="20" height="20" rx="2" fill="#0f172a" />
        <!-- Bluetooth Symbol & Label -->
        <text x="50" y="30" font-size="9" font-weight="900" fill="#38bdf8" text-anchor="middle">ᛒ</text>
        <text x="40" y="57" font-size="9" font-weight="900" fill="#ffffff" text-anchor="middle">${this.modelLabel} BT</text>
        <!-- Status LED -->
        <circle cx="18" cy="36" r="3" fill="#ef4444" stroke="#fca5a5" stroke-width="1" />
        <!-- 4 Header Pins (tam x=16, 32, 48, 64, uç y=75) -->
        <line x1="16" y1="66" x2="16" y2="75" stroke="#94a3b8" stroke-width="3" stroke-linecap="round" />
        <line x1="32" y1="66" x2="32" y2="75" stroke="#94a3b8" stroke-width="3" stroke-linecap="round" />
        <line x1="48" y1="66" x2="48" y2="75" stroke="#94a3b8" stroke-width="3" stroke-linecap="round" />
        <line x1="64" y1="66" x2="64" y2="75" stroke="#94a3b8" stroke-width="3" stroke-linecap="round" />
      </svg>
    `;
  }
}

export class WokwiHC05Element extends WokwiBluetoothModuleElement {
  constructor() {
    super('HC-05');
  }
}

export class WokwiHC06Element extends WokwiBluetoothModuleElement {
  constructor() {
    super('HC-06');
  }
}

/**
 * 2. Motor Sürücü Modülü (L293D / L298N Dual H-Bridge)
 * Sol klemens: OUT1, OUT2 | Sağ klemens: OUT3, OUT4 | Alt header: 9 kontrol/güç pini (toplam 13 pin)
 */
export class WokwiMotorDriverElement extends BaseHTMLElement {
  public pinInfo: CustomPinInfo[];
  private shadow: ShadowRoot;
  private chipTitle: string;

  constructor(chipTitle = 'L293D') {
    super();
    this.chipTitle = chipTitle;
    this.pinInfo = chipTitle === 'L298N' ? L298N_META.pinInfo : L293D_META.pinInfo;
    this.shadow = this.attachShadow({ mode: 'open' });
    this.render();
  }

  private render() {
    const isL298 = this.chipTitle === 'L298N';
    const boardColor = isL298 ? '#b91c1c' : '#0f172a';
    const borderColor = isL298 ? '#7f1d1d' : '#334155';
    const bottomPins = [14, 28, 42, 56, 70, 84, 98, 112, 126];
    this.shadow.innerHTML = `
      <style>
        :host { display: inline-block; width: 140px; height: 84px; user-select: none; }
        svg { width: 100%; height: 100%; display: block; filter: drop-shadow(0 4px 6px rgba(15,23,42,0.35)); }
      </style>
      <svg viewBox="0 0 140 84" xmlns="http://www.w3.org/2000/svg">
        <!-- PCB / IC Body -->
        <rect x="12" y="6" width="116" height="64" rx="7" fill="${boardColor}" stroke="${borderColor}" stroke-width="2.5" />
        <!-- Heatsink / DIP-16 IC Package -->
        <rect x="34" y="16" width="72" height="36" rx="4" fill="#1e293b" stroke="#64748b" stroke-width="1.5" />
        <circle cx="42" cy="34" r="3" fill="#475569" />
        <!-- Left Blue Terminal Block (OUT1, OUT2) -->
        <rect x="10" y="20" width="14" height="34" rx="2" fill="#2563eb" stroke="#93c5fd" stroke-width="1.2" />
        <line x1="4" y1="28" x2="12" y2="28" stroke="#94a3b8" stroke-width="3" stroke-linecap="round" />
        <line x1="4" y1="46" x2="12" y2="46" stroke="#94a3b8" stroke-width="3" stroke-linecap="round" />
        <circle cx="17" cy="28" r="2.2" fill="#cbd5e1" />
        <circle cx="17" cy="46" r="2.2" fill="#cbd5e1" />
        <!-- Right Blue Terminal Block (OUT3, OUT4) -->
        <rect x="116" y="20" width="14" height="34" rx="2" fill="#2563eb" stroke="#93c5fd" stroke-width="1.2" />
        <line x1="128" y1="28" x2="136" y2="28" stroke="#94a3b8" stroke-width="3" stroke-linecap="round" />
        <line x1="128" y1="46" x2="136" y2="46" stroke="#94a3b8" stroke-width="3" stroke-linecap="round" />
        <circle cx="123" cy="28" r="2.2" fill="#cbd5e1" />
        <circle cx="123" cy="46" r="2.2" fill="#cbd5e1" />
        <!-- Title -->
        <text x="70" y="34" font-size="11" font-weight="900" fill="#fde047" text-anchor="middle">${this.chipTitle}</text>
        <text x="70" y="45" font-size="6.8" font-weight="bold" fill="#cbd5e1" text-anchor="middle">MOTOR SÜRÜCÜ</text>
        <!-- Bottom Header Pins (9 pin, uç y=80) -->
        <g stroke="#facc15" stroke-width="2.6" stroke-linecap="round">
          ${bottomPins.map(x => `<line x1="${x}" y1="70" x2="${x}" y2="80" />`).join('\n          ')}
        </g>
      </svg>
    `;
  }
}

export class WokwiL293DElement extends WokwiMotorDriverElement {
  constructor() {
    super('L293D');
  }
}

export class WokwiL298NElement extends WokwiMotorDriverElement {
  constructor() {
    super('L298N');
  }
}

/**
 * 3. 5V DC Motor + Sarı Tekerlek/Pervane (wokwi-dc-motor)
 */
export class WokwiDCMotorElement extends BaseHTMLElement {
  public pinInfo: CustomPinInfo[] = DC_MOTOR_META.pinInfo;
  private shadow: ShadowRoot;

  constructor() {
    super();
    this.shadow = this.attachShadow({ mode: 'open' });
    this.render();
  }

  private render() {
    this.shadow.innerHTML = `
      <style>
        :host { display: inline-block; width: 80px; height: 78px; user-select: none; }
        svg { width: 100%; height: 100%; display: block; filter: drop-shadow(0 4px 6px rgba(15,23,42,0.3)); }
      </style>
      <svg viewBox="0 0 80 78" xmlns="http://www.w3.org/2000/svg">
        <!-- Yellow Gearbox Housing -->
        <rect x="14" y="18" width="52" height="44" rx="10" fill="#facc15" stroke="#ca8a04" stroke-width="2" />
        <!-- Metallic Motor Cylinder -->
        <circle cx="40" cy="40" r="16" fill="#cbd5e1" stroke="#475569" stroke-width="2" />
        <!-- Rotor / Wheel Spokes -->
        <circle cx="40" cy="40" r="5" fill="#1e293b" />
        <line x1="40" y1="24" x2="40" y2="56" stroke="#64748b" stroke-width="2" />
        <line x1="24" y1="40" x2="56" y2="40" stroke="#64748b" stroke-width="2" />
        <!-- Top Axle -->
        <rect x="37" y="6" width="6" height="12" rx="2" fill="#94a3b8" stroke="#475569" stroke-width="1" />
        <!-- 2 Power Leads (Red/Black Terminals, uç y=75) -->
        <circle cx="26" cy="62" r="3.5" fill="#ef4444" stroke="#0f172a" stroke-width="1" />
        <circle cx="54" cy="62" r="3.5" fill="#1e293b" stroke="#ffffff" stroke-width="1" />
        <line x1="26" y1="65" x2="26" y2="75" stroke="#ef4444" stroke-width="3" stroke-linecap="round" />
        <line x1="54" y1="65" x2="54" y2="75" stroke="#334155" stroke-width="3" stroke-linecap="round" />
      </svg>
    `;
  }
}

/**
 * 4. 5V Röle Modülü (wokwi-relay-module)
 */
export class WokwiRelayModuleElement extends BaseHTMLElement {
  public pinInfo: CustomPinInfo[] = RELAY_MODULE_META.pinInfo;
  private shadow: ShadowRoot;

  constructor() {
    super();
    this.shadow = this.attachShadow({ mode: 'open' });
    this.render();
  }

  private render() {
    this.shadow.innerHTML = `
      <style>
        :host { display: inline-block; width: 80px; height: 78px; user-select: none; }
        svg { width: 100%; height: 100%; display: block; filter: drop-shadow(0 4px 6px rgba(15,23,42,0.3)); }
      </style>
      <svg viewBox="0 0 80 78" xmlns="http://www.w3.org/2000/svg">
        <rect x="8" y="6" width="64" height="60" rx="6" fill="#991b1b" stroke="#7f1d1d" stroke-width="2" />
        <!-- Blue Relay Cube -->
        <rect x="16" y="14" width="48" height="34" rx="4" fill="#2563eb" stroke="#1d4ed8" stroke-width="1.5" />
        <text x="40" y="30" font-size="8.5" font-weight="900" fill="#ffffff" text-anchor="middle">5V RELAY</text>
        <text x="40" y="41" font-size="6.5" font-weight="bold" fill="#bfdbfe" text-anchor="middle">10A 250VAC</text>
        <!-- Pins (tam x=22, 40, 58, uç y=75) -->
        <line x1="22" y1="66" x2="22" y2="75" stroke="#facc15" stroke-width="3" stroke-linecap="round" />
        <line x1="40" y1="66" x2="40" y2="75" stroke="#facc15" stroke-width="3" stroke-linecap="round" />
        <line x1="58" y1="66" x2="58" y2="75" stroke="#facc15" stroke-width="3" stroke-linecap="round" />
      </svg>
    `;
  }
}

/**
 * 5. Toprak Nem / Yağmur / Su Seviye Sensörü (wokwi-soil-moisture-sensor, wokwi-rain-sensor, wokwi-water-sensor)
 */
export class WokwiProbeSensorElement extends BaseHTMLElement {
  public pinInfo: CustomPinInfo[];
  private shadow: ShadowRoot;
  private titleText: string;
  private accentColor: string;

  constructor(
    titleText = 'TOPRAK NEM',
    accentColor = '#16a34a',
    meta: CustomModuleMeta = PROBE_4PIN_META
  ) {
    super();
    this.titleText = titleText;
    this.accentColor = accentColor;
    this.pinInfo = meta.pinInfo;
    this.shadow = this.attachShadow({ mode: 'open' });
    this.render();
  }

  private render() {
    const pinLines = this.pinInfo
      .map(
        p =>
          `<line x1="${p.x}" y1="66" x2="${p.x}" y2="${p.y}" stroke="#94a3b8" stroke-width="3" stroke-linecap="round" />`
      )
      .join('\n        ');
    this.shadow.innerHTML = `
      <style>
        :host { display: inline-block; width: 80px; height: 78px; user-select: none; }
        svg { width: 100%; height: 100%; display: block; filter: drop-shadow(0 4px 6px rgba(15,23,42,0.3)); }
      </style>
      <svg viewBox="0 0 80 78" xmlns="http://www.w3.org/2000/svg">
        <!-- Upper PCB Bridge -->
        <rect x="10" y="6" width="60" height="24" rx="5" fill="${this.accentColor}" stroke="#0f172a" stroke-width="2" />
        <text x="40" y="21" font-size="7.5" font-weight="900" fill="#ffffff" text-anchor="middle">${this.titleText}</text>
        <!-- Two Gold Fork Probes -->
        <rect x="16" y="30" width="16" height="36" rx="4" fill="#ca8a04" stroke="#facc15" stroke-width="1.5" />
        <rect x="48" y="30" width="16" height="36" rx="4" fill="#ca8a04" stroke="#facc15" stroke-width="1.5" />
        <!-- Pins (pinInfo ile birebir aynı koordinatlar) -->
        ${pinLines}
      </svg>
    `;
  }
}

export class WokwiSoilMoistureElement extends WokwiProbeSensorElement {
  constructor() {
    super('TOPRAK NEM', '#15803d', PROBE_4PIN_META);
  }
}

export class WokwiRainSensorElement extends WokwiProbeSensorElement {
  constructor() {
    super('YAĞMUR', '#0284c7', PROBE_4PIN_META);
  }
}

export class WokwiWaterSensorElement extends WokwiProbeSensorElement {
  constructor() {
    super('SU SEVİYE', '#0369a1', WATER_SENSOR_META);
  }
}

// Web Component Kayıtları (Her etiket için ayrı sınıf türetilir - DOM kuralı)
const CUSTOM_ELEMENTS: Array<[string, () => CustomElementConstructor]> = [
  ['wokwi-hc-05', () => class extends WokwiHC05Element {}],
  ['wokwi-hc05', () => class extends WokwiHC05Element {}],
  ['wokwi-hc-06', () => class extends WokwiHC06Element {}],
  ['wokwi-hc06', () => class extends WokwiHC06Element {}],
  ['wokwi-l293d', () => class extends WokwiL293DElement {}],
  ['wokwi-l298n', () => class extends WokwiL298NElement {}],
  ['wokwi-dc-motor', () => class extends WokwiDCMotorElement {}],
  ['wokwi-dcmotor', () => class extends WokwiDCMotorElement {}],
  ['wokwi-relay-module', () => class extends WokwiRelayModuleElement {}],
  ['wokwi-soil-moisture-sensor', () => class extends WokwiSoilMoistureElement {}],
  ['wokwi-rain-sensor', () => class extends WokwiRainSensorElement {}],
  ['wokwi-water-sensor', () => class extends WokwiWaterSensorElement {}]
];

for (const [tag, getCtor] of CUSTOM_ELEMENTS) {
  if (typeof window !== 'undefined' && 'customElements' in window) {
    if (!customElements.get(tag)) {
      try {
        customElements.define(tag, getCtor());
      } catch (e) {
        // HMR esnasında tekrar register edilmesini engelle
      }
    }
  }
}

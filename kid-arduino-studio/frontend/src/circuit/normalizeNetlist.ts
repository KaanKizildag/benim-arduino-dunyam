/**
 * Katman 0: Netlist Normalizasyonu ve Düğüm (Net) Çıkarımı (Union-Find)
 * - Bileşen tipi alias'larını standart Wokwi tiplerine dönüştürür.
 * - Arduino pinlerini (uno.13, D13, arduino.D13 -> uno.D13) normalize eder.
 * - Güç hatlarını (uno.GND, GND.1, uno.5V, VCC -> GND / 5V) normalize eder.
 * - Bileşen pin varyantlarını (led1.anode, led1.+, r1.A, servo1.SIG, ldr1.OUT vb.) standartlaştırır.
 * - Ters yönlü güç bağlantılarını ({from:'GND', to:'led1.C'} -> {from:'led1.C', to:'GND'}) düzeltir.
 * - Union-Find ile elektriksel düğümleri (ElectricalNet) çıkarır.
 */

import type {
  CircuitNetlist,
  NetlistComponent,
  NetlistConnection,
  ElectricalNet
} from './types';

export const SUPPORTED_COMPONENT_TYPES = new Set<string>([
  'wokwi-led',
  'wokwi-resistor',
  'wokwi-photoresistor',
  'wokwi-photoresistor-sensor',
  'wokwi-buzzer',
  'wokwi-pushbutton',
  'wokwi-servo',
  'wokwi-hc-sr04',
  'wokwi-potentiometer'
]);

export interface NormalizationResult {
  netlist: CircuitNetlist;
  nets: ElectricalNet[];
  warnings: string[];
  errors: string[];
}

// Bileşen tipi alias haritası
const COMPONENT_TYPE_ALIASES: Record<string, { type: string; defaultProps?: Record<string, any> }> = {
  'wokwi-led': { type: 'wokwi-led' },
  'led': { type: 'wokwi-led' },
  'led_red': { type: 'wokwi-led', defaultProps: { color: 'red' } },
  'led-red': { type: 'wokwi-led', defaultProps: { color: 'red' } },
  'red-led': { type: 'wokwi-led', defaultProps: { color: 'red' } },
  'led_green': { type: 'wokwi-led', defaultProps: { color: 'green' } },
  'led-green': { type: 'wokwi-led', defaultProps: { color: 'green' } },
  'green-led': { type: 'wokwi-led', defaultProps: { color: 'green' } },
  'led_yellow': { type: 'wokwi-led', defaultProps: { color: 'yellow' } },
  'led-yellow': { type: 'wokwi-led', defaultProps: { color: 'yellow' } },
  'yellow-led': { type: 'wokwi-led', defaultProps: { color: 'yellow' } },
  'led_blue': { type: 'wokwi-led', defaultProps: { color: 'blue' } },
  'led-blue': { type: 'wokwi-led', defaultProps: { color: 'blue' } },
  'blue-led': { type: 'wokwi-led', defaultProps: { color: 'blue' } },

  'wokwi-resistor': { type: 'wokwi-resistor' },
  'resistor': { type: 'wokwi-resistor' },
  'res': { type: 'wokwi-resistor' },
  'r': { type: 'wokwi-resistor' },
  'direnc': { type: 'wokwi-resistor' },
  'direnç': { type: 'wokwi-resistor' },
  'resistor_220': { type: 'wokwi-resistor', defaultProps: { value: '220' } },
  'resistor-220': { type: 'wokwi-resistor', defaultProps: { value: '220' } },
  'resistor_1k': { type: 'wokwi-resistor', defaultProps: { value: '1000' } },
  'resistor-1k': { type: 'wokwi-resistor', defaultProps: { value: '1000' } },
  'resistor_10k': { type: 'wokwi-resistor', defaultProps: { value: '10000' } },
  'resistor-10k': { type: 'wokwi-resistor', defaultProps: { value: '10000' } },

  'wokwi-photoresistor': { type: 'wokwi-photoresistor' },
  'photoresistor': { type: 'wokwi-photoresistor' },
  'ldr_discrete': { type: 'wokwi-photoresistor' },
  'ldr-discrete': { type: 'wokwi-photoresistor' },
  'discrete-ldr': { type: 'wokwi-photoresistor' },
  'ldr2': { type: 'wokwi-photoresistor' },

  'wokwi-photoresistor-sensor': { type: 'wokwi-photoresistor-sensor' },
  'photoresistor-sensor': { type: 'wokwi-photoresistor-sensor' },
  'ldr_sensor': { type: 'wokwi-photoresistor-sensor' },
  'ldr-sensor': { type: 'wokwi-photoresistor-sensor' },
  'ldr_module': { type: 'wokwi-photoresistor-sensor' },
  'ldr-module': { type: 'wokwi-photoresistor-sensor' },
  'ky-018': { type: 'wokwi-photoresistor-sensor' },
  'ky018': { type: 'wokwi-photoresistor-sensor' },
  'ldr': { type: 'wokwi-photoresistor' }, // Bağlantı pinlerine göre aşağıda netleştirilir

  'wokwi-buzzer': { type: 'wokwi-buzzer' },
  'buzzer': { type: 'wokwi-buzzer' },
  'piezo': { type: 'wokwi-buzzer' },
  'active_buzzer': { type: 'wokwi-buzzer' },
  'active-buzzer': { type: 'wokwi-buzzer' },
  'passive_buzzer': { type: 'wokwi-buzzer' },
  'passive-buzzer': { type: 'wokwi-buzzer' },

  'wokwi-pushbutton': { type: 'wokwi-pushbutton' },
  'pushbutton': { type: 'wokwi-pushbutton' },
  'push_button': { type: 'wokwi-pushbutton' },
  'push-button': { type: 'wokwi-pushbutton' },
  'button': { type: 'wokwi-pushbutton' },
  'btn': { type: 'wokwi-pushbutton' },
  'buton': { type: 'wokwi-pushbutton' },

  'wokwi-servo': { type: 'wokwi-servo' },
  'servo': { type: 'wokwi-servo' },
  'servo_sg90': { type: 'wokwi-servo' },
  'servo-sg90': { type: 'wokwi-servo' },
  'sg90': { type: 'wokwi-servo' },
  'servomotor': { type: 'wokwi-servo' },
  'servo-motor': { type: 'wokwi-servo' },

  'wokwi-hc-sr04': { type: 'wokwi-hc-sr04' },
  'hc-sr04': { type: 'wokwi-hc-sr04' },
  'hc_sr04': { type: 'wokwi-hc-sr04' },
  'hcsr04': { type: 'wokwi-hc-sr04' },
  'ultrasonic': { type: 'wokwi-hc-sr04' },
  'ultrasonic-sensor': { type: 'wokwi-hc-sr04' },
  'distance-sensor': { type: 'wokwi-hc-sr04' },

  'wokwi-potentiometer': { type: 'wokwi-potentiometer' },
  'potentiometer': { type: 'wokwi-potentiometer' },
  'pot': { type: 'wokwi-potentiometer' },
  'potans': { type: 'wokwi-potentiometer' },
  'potansiyometre': { type: 'wokwi-potentiometer' }
};

// Her bileşen tipi için pin alias tablosu
const PIN_ALIASES_BY_TYPE: Record<string, Record<string, string>> = {
  'wokwi-led': {
    'A': 'A',
    'ANODE': 'A',
    'ANOT': 'A',
    '+': 'A',
    'POS': 'A',
    'POSITIVE': 'A',
    '1': 'A',
    'UZUN': 'A',
    'LONG': 'A',
    'VCC': 'A',
    'IN': 'A',
    'C': 'C',
    'K': 'C',
    'CATHODE': 'C',
    'KATOT': 'C',
    '-': 'C',
    'NEG': 'C',
    'NEGATIVE': 'C',
    '2': 'C',
    'GND': 'C',
    'KISA': 'C',
    'SHORT': 'C',
    'OUT': 'C'
  },
  'wokwi-resistor': {
    '1': '1',
    'PIN1': '1',
    'PIN_1': '1',
    'P1': '1',
    'A': '1',
    'IN': '1',
    'LEFT': '1',
    '+': '1',
    '2': '2',
    'PIN2': '2',
    'PIN_2': '2',
    'P2': '2',
    'B': '2',
    'OUT': '2',
    'RIGHT': '2',
    '-': '2'
  },
  'wokwi-photoresistor': {
    '1': '1',
    'PIN1': '1',
    'PIN_1': '1',
    'P1': '1',
    'A': '1',
    'VCC': '1',
    '+': '1',
    'IN': '1',
    'LEFT': '1',
    '2': '2',
    'PIN2': '2',
    'PIN_2': '2',
    'P2': '2',
    'B': '2',
    'GND': '2',
    '-': '2',
    'OUT': '2',
    'SIG': '2',
    'AO': '2',
    'A0': '2',
    'RIGHT': '2'
  },
  'wokwi-photoresistor-sensor': {
    'VCC': 'VCC',
    '5V': 'VCC',
    '3.3V': 'VCC',
    'V+': 'VCC',
    '+': 'VCC',
    'POWER': 'VCC',
    '1': 'VCC',
    'GND': 'GND',
    '-': 'GND',
    '0V': 'GND',
    'GROUND': 'GND',
    '2': 'GND',
    'DO': 'DO',
    'D0': 'DO',
    'DOUT': 'DO',
    'DIGITAL': 'DO',
    '3': 'DO',
    'AO': 'AO',
    'A0': 'AO',
    'AOUT': 'AO',
    'OUT': 'AO',
    'SIG': 'AO',
    'SIGNAL': 'AO',
    'ANALOG': 'AO',
    '4': 'AO'
  },
  'wokwi-buzzer': {
    '1': '1',
    '+': '1',
    'POS': '1',
    'POSITIVE': '1',
    'SIG': '1',
    'SIGNAL': '1',
    'A': '1',
    'ANODE': '1',
    'VCC': '1',
    'IN': '1',
    'PIN1': '1',
    'PIN_1': '1',
    'P1': '1',
    'RED': '1',
    '2': '2',
    '-': '2',
    'NEG': '2',
    'NEGATIVE': '2',
    'GND': '2',
    'GROUND': '2',
    'C': '2',
    'CATHODE': '2',
    'B': '2',
    'OUT': '2',
    'PIN2': '2',
    'PIN_2': '2',
    'P2': '2',
    'BLACK': '2'
  },
  'wokwi-pushbutton': {
    '1': '1',
    '1.L': '1',
    '1.R': '1',
    '1A': '1',
    '1B': '1',
    'A': '1',
    'PIN1': '1',
    'PIN_1': '1',
    'P1': '1',
    'IN': '1',
    'LEFT': '1',
    '+': '1',
    'VCC': '1',
    '2': '2',
    '2.L': '2',
    '2.R': '2',
    '2A': '2',
    '2B': '2',
    'B': '2',
    'PIN2': '2',
    'PIN_2': '2',
    'P2': '2',
    'OUT': '2',
    'SIG': '2',
    'RIGHT': '2',
    '-': '2',
    'GND': '2',
    '3': '2',
    '4': '2'
  },
  'wokwi-servo': {
    'GND': 'GND',
    '-': 'GND',
    'GROUND': 'GND',
    '0V': 'GND',
    '1': 'GND',
    'BROWN': 'GND',
    'BLACK': 'GND',
    'V+': 'V+',
    'VCC': 'V+',
    '5V': 'V+',
    '+': 'V+',
    'POWER': 'V+',
    'V': 'V+',
    'VIN': 'V+',
    '2': 'V+',
    'RED': 'V+',
    'PWM': 'PWM',
    'SIG': 'PWM',
    'SIGNAL': 'PWM',
    'OUT': 'PWM',
    'IN': 'PWM',
    'DATA': 'PWM',
    'PULSE': 'PWM',
    'CTRL': 'PWM',
    '3': 'PWM',
    'ORANGE': 'PWM',
    'YELLOW': 'PWM'
  },
  'wokwi-hc-sr04': {
    'VCC': 'VCC',
    '5V': 'VCC',
    'V+': 'VCC',
    '+': 'VCC',
    'POWER': 'VCC',
    '1': 'VCC',
    'TRIG': 'TRIG',
    'TRIGGER': 'TRIG',
    'TRG': 'TRIG',
    'T': 'TRIG',
    '2': 'TRIG',
    'ECHO': 'ECHO',
    'ECH': 'ECHO',
    'E': 'ECHO',
    'OUT': 'ECHO',
    'SIG': 'ECHO',
    '3': 'ECHO',
    'GND': 'GND',
    '-': 'GND',
    'GROUND': 'GND',
    '0V': 'GND',
    '4': 'GND'
  },
  'wokwi-potentiometer': {
    'GND': 'GND',
    '1': 'GND',
    'A': 'GND',
    '-': 'GND',
    'PIN1': 'GND',
    'PIN_1': 'GND',
    'P1': 'GND',
    'LEFT': 'GND',
    'GROUND': 'GND',
    'SIG': 'SIG',
    '2': 'SIG',
    'B': 'SIG',
    'OUT': 'SIG',
    'WIPER': 'SIG',
    'AO': 'SIG',
    'A0': 'SIG',
    'SIGNAL': 'SIG',
    'IN': 'SIG',
    'PIN2': 'SIG',
    'PIN_2': 'SIG',
    'P2': 'SIG',
    'MIDDLE': 'SIG',
    'CENTER': 'SIG',
    'VCC': 'VCC',
    '3': 'VCC',
    'C': 'VCC',
    '5V': 'VCC',
    'V+': 'VCC',
    '+': 'VCC',
    'PIN3': 'VCC',
    'PIN_3': 'VCC',
    'P3': 'VCC',
    'RIGHT': 'VCC',
    'POWER': 'VCC'
  }
};

const GND_ALIASES = new Set([
  'GND',
  'GND.1',
  'GND.2',
  'GND.3',
  'GND1',
  'GND2',
  'GND3',
  'GROUND',
  '0V',
  '-',
  'VSS',
  'BN',
  'BP.-',
  'TOP--',
  'BOTTOM--'
]);

const POWER_5V_ALIASES = new Set([
  '5V',
  '+5V',
  '3.3V',
  '3V3',
  '+3.3V',
  'VCC',
  'V+',
  'VDD',
  '+',
  'VIN',
  'BP',
  'BP.+',
  'TOP-+',
  'BOTTOM-+'
]);

const BOARD_PREFIXES = new Set([
  'uno',
  'arduino',
  'board',
  'arduino-uno',
  'arduino_uno',
  'nano',
  'arduino-nano',
  'mega',
  'esp32',
  'breadboard',
  'bb'
]);

class UnionFind {
  private parent = new Map<string, string>();

  public add(x: string): void {
    if (!this.parent.has(x)) {
      this.parent.set(x, x);
    }
  }

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
    const rootA = this.find(a);
    const rootB = this.find(b);
    if (rootA !== rootB) {
      this.parent.set(rootB, rootA);
    }
  }

  public getAllElements(): string[] {
    return Array.from(this.parent.keys());
  }
}

/**
 * Ham bağlantılarda bir bileşenin hangi pin isimleriyle kullanıldığını toplar.
 */
function collectRawPinsForComponent(compId: string, connections: NetlistConnection[]): string[] {
  const lowerId = compId.toLowerCase();
  const pins: string[] = [];
  for (const conn of connections) {
    const rawFrom = String((conn as any).from || (conn as any).from_pin || '').trim();
    const rawTo = String((conn as any).to || (conn as any).to_pin || '').trim();
    for (const ep of [rawFrom, rawTo]) {
      const dotIdx = ep.indexOf('.');
      if (dotIdx !== -1) {
        const part = ep.slice(0, dotIdx).trim().toLowerCase();
        const pin = ep.slice(dotIdx + 1).trim().toUpperCase();
        if (part === lowerId) {
          pins.push(pin);
        }
      }
    }
  }
  return pins;
}

/**
 * Netlist'i normalize eder ve Union-Find ile elektriksel net'leri çıkarır.
 */
export function normalizeNetlist(rawNetlist: CircuitNetlist): NormalizationResult {
  const warnings: string[] = [];
  const errors: string[] = [];

  if (!rawNetlist || !Array.isArray(rawNetlist.components)) {
    return {
      netlist: { board: 'arduino-uno', components: [], connections: [] },
      nets: [],
      warnings: [],
      errors: ['Geçersiz netlist şeması: components dizisi bulunamadı.']
    };
  }

  const rawConnections = Array.isArray(rawNetlist.connections) ? rawNetlist.connections : [];

  // 1. Bileşenleri normalize et
  const normalizedComponents: NetlistComponent[] = [];
  const compById = new Map<string, NetlistComponent>();
  const compIdLowerMap = new Map<string, string>();

  for (const rawComp of rawNetlist.components) {
    const id = String(rawComp.id || '').trim();
    if (!id) {
      warnings.push('Kimliği (id) boş olan bir bileşen atlandı.');
      continue;
    }

    const rawType = String(rawComp.type || '').trim();
    const lowerType = rawType.toLowerCase();
    const lowerId = id.toLowerCase();

    // LLM yanlışlıkla Arduino kartını veya Breadboard'u components listesine eklediyse atla
    if (
      BOARD_PREFIXES.has(lowerId) ||
      lowerType.includes('arduino') ||
      lowerType.includes('breadboard') ||
      lowerType === 'esp32'
    ) {
      warnings.push(`Ana kart/breadboard bileşen listesinden çıkarıldı: '${id}' (${rawType}).`);
      continue;
    }

    const aliasEntry = COMPONENT_TYPE_ALIASES[lowerType];

    let canonicalType = aliasEntry ? aliasEntry.type : rawType;
    const props: Record<string, any> = {
      ...(aliasEntry?.defaultProps || {}),
      ...(rawComp.props || {})
    };

    // LDR için akıllı tip netleştirmesi (2 bacaklı vs 4 pinli modül)
    if (
      lowerType === 'ldr' ||
      canonicalType === 'wokwi-photoresistor' ||
      canonicalType === 'wokwi-photoresistor-sensor'
    ) {
      const usedPins = collectRawPinsForComponent(id, rawConnections);
      const hasModulePins = usedPins.some(p =>
        ['VCC', 'AO', 'DO', 'OUT', 'SIG', 'A0', 'D0', 'AOUT', 'DOUT'].includes(p)
      );
      const hasOnlyTwoPinTerms =
        usedPins.length > 0 &&
        usedPins.every(p => ['1', '2', 'A', 'B', 'PIN1', 'PIN2', 'PIN_1', 'PIN_2'].includes(p));

      if (lowerType === 'ldr') {
        canonicalType = hasModulePins ? 'wokwi-photoresistor-sensor' : 'wokwi-photoresistor';
        warnings.push(`Bileşen tipi normalize edildi: '${id}' (${rawType} → ${canonicalType}).`);
      } else if (canonicalType === 'wokwi-photoresistor-sensor' && hasOnlyTwoPinTerms) {
        canonicalType = 'wokwi-photoresistor';
        warnings.push(
          `'${id}' bileşeni 2 bacaklı (1/2) bağlandığı için tipi 'wokwi-photoresistor' olarak normalize edildi.`
        );
      } else if (canonicalType === 'wokwi-photoresistor' && hasModulePins && usedPins.includes('GND')) {
        canonicalType = 'wokwi-photoresistor-sensor';
        warnings.push(
          `'${id}' bileşeni modül pinleri (VCC/GND/AO) kullandığı için tipi 'wokwi-photoresistor-sensor' olarak normalize edildi.`
        );
      }
    } else if (aliasEntry && rawType !== canonicalType) {
      warnings.push(`Bileşen tipi normalize edildi: '${id}' (${rawType} → ${canonicalType}).`);
    }

    const comp: NetlistComponent = {
      id,
      type: canonicalType,
      props,
      label: rawComp.label || id
    };

    normalizedComponents.push(comp);
    compById.set(id, comp);
    compIdLowerMap.set(id.toLowerCase(), id);
  }

  // Yardımcı: Bileşen ID çözümleme (birebir, küçük harf veya tekil tip eşleşmesi)
  function resolveComponent(partRaw: string): NetlistComponent | undefined {
    const clean = partRaw.trim();
    if (compById.has(clean)) return compById.get(clean);
    const lower = clean.toLowerCase();
    if (compIdLowerMap.has(lower)) {
      return compById.get(compIdLowerMap.get(lower)!);
    }
    // Eğer LLM 'servo.PWM' yazdıysa ve devrede tek bir 'servo1' varsa
    const prefixMatches = normalizedComponents.filter(
      c => c.id.toLowerCase().startsWith(lower) || lower.startsWith(c.id.toLowerCase())
    );
    if (prefixMatches.length === 1) {
      return prefixMatches[0];
    }
    const aliasType = COMPONENT_TYPE_ALIASES[lower]?.type;
    if (aliasType) {
      const typeMatches = normalizedComponents.filter(c => c.type === aliasType);
      if (typeMatches.length === 1) {
        return typeMatches[0];
      }
    }
    return undefined;
  }

  // Yardımcı: Tek bir uç noktayı (endpoint) normalize et
  function normalizeEndpoint(rawEp: string): {
    valid: boolean;
    canonical: string;
    kind: 'power' | 'arduino' | 'component';
    reason?: string;
  } {
    const ep = String(rawEp || '').trim();
    if (!ep) {
      return { valid: false, canonical: '', kind: 'component', reason: 'Boş bağlantı ucu.' };
    }

    const upperEp = ep.toUpperCase();

    // Doğrudan güç hattı kontrolü (örn: GND, 5V, GND.1, VCC)
    if (GND_ALIASES.has(upperEp)) {
      return { valid: true, canonical: 'GND', kind: 'power' };
    }
    if (POWER_5V_ALIASES.has(upperEp)) {
      return { valid: true, canonical: '5V', kind: 'power' };
    }

    const dotIdx = ep.indexOf('.');
    if (dotIdx !== -1) {
      const partRaw = ep.slice(0, dotIdx).trim();
      const pinRaw = ep.slice(dotIdx + 1).trim();
      const partLower = partRaw.toLowerCase();
      const pinUpper = pinRaw.toUpperCase();

      // 1) Önce bilinen bir bileşen ID'si mi kontrol et (BOARD_PREFIXES değilse)
      if (!BOARD_PREFIXES.has(partLower)) {
        const comp = resolveComponent(partRaw);
        if (comp) {
          const pinMap = PIN_ALIASES_BY_TYPE[comp.type];
          if (!pinMap) {
            // Desteklenmeyen bileşen tipi
            return {
              valid: true,
              canonical: `${comp.id}.${pinUpper}`,
              kind: 'component'
            };
          }
          const mappedPin = pinMap[pinUpper];
          if (mappedPin) {
            return {
              valid: true,
              canonical: `${comp.id}.${mappedPin}`,
              kind: 'component'
            };
          }
          return {
            valid: false,
            canonical: ep,
            kind: 'component',
            reason: `'${comp.id}' (${comp.type}) bileşeninde geçersiz pin adı: '${pinRaw}'.`
          };
        }
      }

      // 2) Arduino / Board öneki (uno.13, arduino.D13, uno.GND, uno.5V vb.)
      if (BOARD_PREFIXES.has(partLower)) {
        if (GND_ALIASES.has(pinUpper)) {
          return { valid: true, canonical: 'GND', kind: 'power' };
        }
        if (POWER_5V_ALIASES.has(pinUpper)) {
          return { valid: true, canonical: '5V', kind: 'power' };
        }

        const digMatch = pinUpper.match(/^(?:D|PIN_?|DIGITAL_?|GPIO_?)?([0-9]|1[0-3])$/);
        if (digMatch) {
          return { valid: true, canonical: `uno.D${digMatch[1]}`, kind: 'arduino' };
        }

        const anaMatch = pinUpper.match(/^(?:A|ANALOG_?|ADC_?)([0-5])$/);
        if (anaMatch) {
          return { valid: true, canonical: `uno.A${anaMatch[1]}`, kind: 'arduino' };
        }

        const numVal = parseInt(pinUpper, 10);
        if (!isNaN(numVal) && numVal >= 14 && numVal <= 19) {
          return { valid: true, canonical: `uno.A${numVal - 14}`, kind: 'arduino' };
        }

        return {
          valid: false,
          canonical: ep,
          kind: 'arduino',
          reason: `Geçersiz Arduino pini: '${ep}'.`
        };
      }

      return {
        valid: false,
        canonical: ep,
        kind: 'component',
        reason: `Bilinmeyen bileşen veya pin: '${ep}'.`
      };
    }

    // Nokta içermeyen tekil ifadeler: D13, 13, A0, PIN13 vb.
    const digBare = upperEp.match(/^(?:D|PIN_?|DIGITAL_?|GPIO_?)?([0-9]|1[0-3])$/);
    if (digBare) {
      return { valid: true, canonical: `uno.D${digBare[1]}`, kind: 'arduino' };
    }

    const anaBare = upperEp.match(/^(?:A|ANALOG_?|ADC_?)([0-5])$/);
    if (anaBare) {
      return { valid: true, canonical: `uno.A${anaBare[1]}`, kind: 'arduino' };
    }

    return {
      valid: false,
      canonical: ep,
      kind: 'component',
      reason: `Tanınmayan bağlantı ucu: '${ep}'.`
    };
  }

  // 2. Bağlantıları normalize et
  const normalizedConnections: NetlistConnection[] = [];
  const seenConnections = new Set<string>();

  for (const rawConn of rawConnections) {
    const rawFrom = String((rawConn as any).from || (rawConn as any).from_pin || '').trim();
    const rawTo = String((rawConn as any).to || (rawConn as any).to_pin || '').trim();

    const normFrom = normalizeEndpoint(rawFrom);
    const normTo = normalizeEndpoint(rawTo);

    if (!normFrom.valid) {
      warnings.push(`Geçersiz bağlantı atlandı (${rawFrom} -> ${rawTo}): ${normFrom.reason}`);
      continue;
    }
    if (!normTo.valid) {
      warnings.push(`Geçersiz bağlantı atlandı (${rawFrom} -> ${rawTo}): ${normTo.reason}`);
      continue;
    }

    let finalFrom = normFrom.canonical;
    let finalTo = normTo.canonical;
    let fromKind = normFrom.kind;
    let toKind = normTo.kind;

    if (rawFrom !== finalFrom) {
      warnings.push(`Pin/uç normalize edildi: '${rawFrom}' → '${finalFrom}'.`);
    }
    if (rawTo !== finalTo) {
      warnings.push(`Pin/uç normalize edildi: '${rawTo}' → '${finalTo}'.`);
    }

    // Aynı uca kendi kendine bağlantı kontrolü
    if (finalFrom === finalTo) {
      warnings.push(`Kendi kendine bağlantı atlandı: '${finalFrom} -> ${finalTo}'.`);
      continue;
    }

    // 5V <-> GND doğrudan kısa devre kontrolü
    if (
      (finalFrom === '5V' && finalTo === 'GND') ||
      (finalFrom === 'GND' && finalTo === '5V')
    ) {
      errors.push('Kritik Kısa Devre Hatası: 5V ve GND doğrudan birbirine bağlanmış!');
      continue;
    }

    // Yön normalizasyonu: Güç (GND / 5V) her zaman 'to' tarafında olmalı
    if (fromKind === 'power' && toKind !== 'power') {
      const temp = finalFrom;
      finalFrom = finalTo;
      finalTo = temp;
      const tempKind = fromKind;
      fromKind = toKind;
      toKind = tempKind;
      warnings.push(`Güç bağlantısı yönü normalize edildi: '${rawFrom} -> ${rawTo}' → '${finalFrom} -> ${finalTo}'.`);
    }

    // Tekrarlanan bağlantıları ele
    const pairKey =
      finalTo === 'GND' || finalTo === '5V'
        ? `${finalFrom}=>${finalTo}`
        : [finalFrom, finalTo].sort().join('<=>');

    if (seenConnections.has(pairKey)) {
      warnings.push(`Tekrarlanan bağlantı atlandı: '${finalFrom} -> ${finalTo}'.`);
      continue;
    }
    seenConnections.add(pairKey);

    normalizedConnections.push({
      from: finalFrom,
      to: finalTo,
      color: rawConn.color
    });
  }

  // 3. Union-Find ile Elektriksel Düğümleri (ElectricalNet) Çıkar
  const uf = new UnionFind();
  const netColors = new Map<string, string>();
  const powerByEndpoint = new Map<string, Set<'GND' | '5V'>>();

  for (const conn of normalizedConnections) {
    const { from, to, color } = conn;
    const isToPower = to === 'GND' || to === '5V';

    if (isToPower) {
      uf.add(from);
      if (!powerByEndpoint.has(from)) {
        powerByEndpoint.set(from, new Set());
      }
      powerByEndpoint.get(from)!.add(to as 'GND' | '5V');
      if (color && !netColors.has(from)) {
        netColors.set(from, color);
      }
    } else {
      uf.add(from);
      uf.add(to);
      uf.union(from, to);
      if (color) {
        if (!netColors.has(from)) netColors.set(from, color);
        if (!netColors.has(to)) netColors.set(to, color);
      }
    }
  }

  // Kök düğümlere göre grupla
  const groups = new Map<
    string,
    {
      componentPins: string[];
      arduinoPins: string[];
      powerRails: Set<'GND' | '5V'>;
      color?: string;
    }
  >();

  for (const ep of uf.getAllElements()) {
    const root = uf.find(ep);
    if (!groups.has(root)) {
      groups.set(root, {
        componentPins: [],
        arduinoPins: [],
        powerRails: new Set(),
        color: undefined
      });
    }
    const g = groups.get(root)!;
    if (ep.startsWith('uno.')) {
      if (!g.arduinoPins.includes(ep)) g.arduinoPins.push(ep);
    } else if (ep !== 'GND' && ep !== '5V') {
      if (!g.componentPins.includes(ep)) g.componentPins.push(ep);
    }

    const pSet = powerByEndpoint.get(ep);
    if (pSet) {
      for (const p of pSet) g.powerRails.add(p);
    }

    if (!g.color && netColors.has(ep)) {
      g.color = netColors.get(ep);
    }
  }

  const nets: ElectricalNet[] = [];
  let netCounter = 1;

  for (const g of groups.values()) {
    if (g.powerRails.has('GND') && g.powerRails.has('5V')) {
      errors.push(
        `Kısa Devre Hatası: [${g.componentPins.concat(g.arduinoPins).join(', ')}] düğümü üzerinden 5V ve GND birbirine bağlanmış!`
      );
    }

    let powerRail: 'GND' | '5V' | undefined;
    if (g.powerRails.has('GND')) powerRail = 'GND';
    else if (g.powerRails.has('5V')) powerRail = '5V';

    nets.push({
      id: `net-${netCounter++}`,
      componentPins: g.componentPins,
      arduinoPins: g.arduinoPins,
      powerRail,
      color: g.color
    });
  }

  const normalizedNetlist: CircuitNetlist = {
    board: rawNetlist.board || 'arduino-uno',
    components: normalizedComponents,
    connections: normalizedConnections
  };

  return {
    netlist: normalizedNetlist,
    nets,
    warnings,
    errors
  };
}

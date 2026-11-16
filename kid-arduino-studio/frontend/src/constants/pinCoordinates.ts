export interface PinPosition {
  x: number;
  y: number;
  label: string;
}

export interface ComponentLayout {
  id: string;
  name: string;
  x: number;
  y: number;
  width: number;
  height: number;
  pins: Record<string, PinPosition>;
}

export const PIN_COORDINATES: Record<string, ComponentLayout> = {
  ARDUINO_UNO: {
    id: 'ARDUINO_UNO',
    name: 'Arduino Uno R3',
    x: 460,
    y: 130,
    width: 440,
    height: 310,
    pins: {
      // Üst Dijital Pinler (Sağdan Sola)
      D0: { x: 846, y: 148, label: '0 (RX)' },
      D1: { x: 829, y: 148, label: '1 (TX)' },
      D2: { x: 812, y: 148, label: '2' },
      D3: { x: 795, y: 148, label: '~3' },
      D4: { x: 778, y: 148, label: '4' },
      D5: { x: 761, y: 148, label: '~5' },
      D6: { x: 744, y: 148, label: '~6' },
      D7: { x: 727, y: 148, label: '7' },
      D8: { x: 700, y: 148, label: '8' },
      D9: { x: 683, y: 148, label: '~9' },
      D10: { x: 666, y: 148, label: '~10' },
      D11: { x: 649, y: 148, label: '~11' },
      D12: { x: 632, y: 148, label: '12' },
      D13: { x: 615, y: 148, label: '13' },
      GND_TOP: { x: 598, y: 148, label: 'GND' },
      AREF: { x: 581, y: 148, label: 'AREF' },

      // Alt Güç ve Analog Pinler
      IOREF: { x: 586, y: 422, label: 'IOREF' },
      RESET: { x: 603, y: 422, label: 'RESET' },
      '3.3V': { x: 620, y: 422, label: '3.3V' },
      '5V': { x: 637, y: 422, label: '5V' },
      GND: { x: 654, y: 422, label: 'GND' },
      GND_2: { x: 671, y: 422, label: 'GND' },
      VIN: { x: 688, y: 422, label: 'VIN' },
      A0: { x: 728, y: 422, label: 'A0' },
      A1: { x: 745, y: 422, label: 'A1' },
      A2: { x: 762, y: 422, label: 'A2' },
      A3: { x: 779, y: 422, label: 'A3' },
      A4: { x: 796, y: 422, label: 'A4' },
      A5: { x: 813, y: 422, label: 'A5' },
    }
  },

  LED_RED: {
    id: 'LED_RED',
    name: 'Kırmızı LED',
    x: 100,
    y: 80,
    width: 90,
    height: 120,
    pins: {
      ANODE: { x: 130, y: 200, label: 'Uzun Bacak (+)' },
      CATHODE: { x: 160, y: 190, label: 'Kısa Bacak (-)' },
      PLUS: { x: 130, y: 200, label: 'Uzun Bacak (+)' },
      MINUS: { x: 160, y: 190, label: 'Kısa Bacak (-)' },
    }
  },

  RESISTOR_220: {
    id: 'RESISTOR_220',
    name: '220Ω Direnç',
    x: 240,
    y: 110,
    width: 130,
    height: 60,
    pins: {
      PIN1: { x: 250, y: 140, label: 'Uç 1' },
      PIN2: { x: 360, y: 140, label: 'Uç 2' },
      A: { x: 250, y: 140, label: 'Uç 1' },
      B: { x: 360, y: 140, label: 'Uç 2' },
    }
  },

  LDR_SENSOR: {
    id: 'LDR_SENSOR',
    name: 'LDR Işık Sensörü',
    x: 100,
    y: 250,
    width: 90,
    height: 110,
    pins: {
      PIN1: { x: 130, y: 350, label: 'Bacak 1' },
      PIN2: { x: 160, y: 350, label: 'Bacak 2' },
      VCC: { x: 130, y: 350, label: 'Güç / Bacak 1' },
      GND: { x: 160, y: 350, label: 'Sinyal / Bacak 2' },
    }
  },

  HCSR04: {
    id: 'HCSR04',
    name: 'Mesafe Sensörü (HC-SR04)',
    x: 80,
    y: 440,
    width: 150,
    height: 90,
    pins: {
      VCC: { x: 110, y: 535, label: 'VCC (+5V)' },
      TRIG: { x: 135, y: 535, label: 'TRIG (Tetik)' },
      ECHO: { x: 160, y: 535, label: 'ECHO (Yankı)' },
      GND: { x: 185, y: 535, label: 'GND (- Toprak)' },
    }
  },

  BUZZER: {
    id: 'BUZZER',
    name: 'Ses Çıkarıcı (Buzzer)',
    x: 270,
    y: 260,
    width: 100,
    height: 110,
    pins: {
      PLUS: { x: 300, y: 360, label: 'Artı (+)' },
      VCC: { x: 300, y: 360, label: 'Artı (+)' },
      GND: { x: 335, y: 360, label: 'Eksi (-)' },
      MINUS: { x: 335, y: 360, label: 'Eksi (-)' },
    }
  },

  BUTTON: {
    id: 'BUTTON',
    name: 'Tıklama Butonu',
    x: 280,
    y: 440,
    width: 90,
    height: 90,
    pins: {
      PIN1: { x: 295, y: 525, label: 'Bacak 1' },
      PIN2: { x: 345, y: 525, label: 'Bacak 2' },
      VCC: { x: 295, y: 525, label: 'Giriş' },
      GND: { x: 345, y: 525, label: 'Çıkış' },
    }
  },

  SERVO: {
    id: 'SERVO',
    name: 'Mini Servo Motor',
    x: 180,
    y: 560,
    width: 120,
    height: 80,
    pins: {
      GND: { x: 210, y: 640, label: 'Kahverengi (GND)' },
      VCC: { x: 235, y: 640, label: 'Kırmızı (+5V)' },
      SIGNAL: { x: 260, y: 640, label: 'Turuncu (Sinyal)' },
      PWM: { x: 260, y: 640, label: 'Turuncu (Sinyal)' },
    }
  }
};

/**
 * Parça ve pin adına göre SVG koordinatını bulur.
 * Esnek takma ad (alias) desteği sunar.
 */
export function getPinCoordinates(parca: string, pin: string): { x: number; y: number } | null {
  const compKey = parca.toUpperCase().trim();
  const component = PIN_COORDINATES[compKey];
  
  if (!component) {
    // Arduino Uno pini doğrudan gelmiş olabilir
    if (PIN_COORDINATES.ARDUINO_UNO.pins[pin.toUpperCase()]) {
      return PIN_COORDINATES.ARDUINO_UNO.pins[pin.toUpperCase()];
    }
    return null;
  }

  const cleanPin = pin.toUpperCase().trim();

  // 1. Doğrudan eşleşme
  if (component.pins[cleanPin]) {
    return component.pins[cleanPin];
  }

  // 2. Arduino için "13" -> "D13" dönüşümü
  if (compKey === 'ARDUINO_UNO') {
    const withD = `D${cleanPin}`;
    if (component.pins[withD]) {
      return component.pins[withD];
    }
    if (cleanPin.includes('GND')) {
      return component.pins.GND;
    }
    if (cleanPin.includes('5V')) {
      return component.pins['5V'];
    }
  }

  // 3. Genel takma adlar
  const aliases: Record<string, string[]> = {
    ANODE: ['PLUS', 'VCC', 'ART', '+', 'UZUN'],
    CATHODE: ['MINUS', 'GND', 'EKSI', '-', 'KISA'],
    PIN1: ['VCC', 'PLUS', 'A', '1'],
    PIN2: ['GND', 'MINUS', 'B', '2', 'SIGNAL'],
    PLUS: ['VCC', 'ANODE', '+'],
    MINUS: ['GND', 'CATHODE', '-'],
    SIGNAL: ['SIG', 'DATA', 'PWM', 'ECHO', 'TRIG', 'PIN2'],
  };

  for (const [canonical, syns] of Object.entries(aliases)) {
    if (cleanPin === canonical || syns.includes(cleanPin)) {
      if (component.pins[canonical]) return component.pins[canonical];
      for (const s of syns) {
        if (component.pins[s]) return component.pins[s];
      }
    }
  }

  // İlk mevcut pini döndür
  const firstPin = Object.values(component.pins)[0];
  return firstPin || null;
}

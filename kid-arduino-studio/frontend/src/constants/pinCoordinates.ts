export interface PinPosition {
  x: number;
  y: number;
  label: string;
  row?: string; // Satır harfi (A-J, veya RAIL)
  col?: number; // Sütun numarası (1-30)
  net?: string; // Elektrik hattı (örn: BB_TOP_5, RAIL_GND, RAIL_5V)
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

// ========================================================
// 1. SABİT ARDUINO UNO PİN KOORDİNATLARI (Canvas: 1000x680)
// Arduino Uno breadboard'un hemen altında x=280, y=390'da durur.
// Dijital pinler doğrudan breadboard'a doğru yukarı bakar!
// ========================================================
export const ARDUINO_UNO_PINS: Record<string, PinPosition> = {
  // Üst Dijital Header (y = 405, Breadboard'a doğru yukarı bakar)
  AREF: { x: 400, y: 405, label: 'AREF' },
  GND_TOP: { x: 417, y: 405, label: 'GND' },
  D13: { x: 434, y: 405, label: '13' },
  D12: { x: 451, y: 405, label: '12' },
  D11: { x: 468, y: 405, label: '~11' },
  D10: { x: 485, y: 405, label: '~10' },
  D9: { x: 502, y: 405, label: '~9' },
  D8: { x: 519, y: 405, label: '8' },
  D7: { x: 546, y: 405, label: '7' },
  D6: { x: 563, y: 405, label: '~6' },
  D5: { x: 580, y: 405, label: '~5' },
  D4: { x: 597, y: 405, label: '4' },
  D3: { x: 614, y: 405, label: '~3' },
  D2: { x: 631, y: 405, label: '2' },
  D1: { x: 648, y: 405, label: '1' },
  D0: { x: 665, y: 405, label: '0' },

  // Alt Güç ve Analog Header (y = 638)
  IOREF: { x: 405, y: 638, label: 'IOREF' },
  RESET: { x: 422, y: 638, label: 'RST' },
  '3.3V': { x: 439, y: 638, label: '3.3V' },
  '5V': { x: 456, y: 638, label: '5V' },
  GND: { x: 473, y: 638, label: 'GND' },
  GND_2: { x: 490, y: 638, label: 'GND' },
  VIN: { x: 507, y: 638, label: 'VIN' },
  A0: { x: 547, y: 638, label: 'A0' },
  A1: { x: 564, y: 638, label: 'A1' },
  A2: { x: 581, y: 638, label: 'A2' },
  A3: { x: 598, y: 638, label: 'A3' },
  A4: { x: 615, y: 638, label: 'A4' },
  A5: { x: 632, y: 638, label: 'A5' },
};


// ========================================================
// 2. STANDART 30 SÜTUN BREADBOARD GEOMETRİSİ
// Breadboard Boyutu: x=40, y=50, w=920, h=320
// Sütunlar: 1'den 30'a kadar (x = 65 + col * 28)
// Üst Yarı: A(120), B(138), C(156), D(174), E(192)
// Orta Oluk: y=202..210 (Yalıtkan)
// Alt Yarı: F(220), G(238), H(256), I(274), J(292)
// Güç Rayları:
//   Üst: RAIL_5V(y=74), RAIL_GND(y=92)
//   Alt: RAIL_5V(y=320), RAIL_GND(y=338)
// ========================================================

export const BREADBOARD_GRID = {
  x: 40,
  y: 50,
  width: 920,
  height: 320,
  totalCols: 30,
  getColX: (col: number) => 65 + col * 28,
  rows: {
    // Üst Raylar
    RAIL_TOP_5V: 74,
    RAIL_TOP_GND: 92,
    // Üst Terminal Grubu
    A: 120,
    B: 138,
    C: 156,
    D: 174,
    E: 192,
    // Alt Terminal Grubu
    F: 220,
    G: 238,
    H: 256,
    I: 274,
    J: 292,
    // Alt Raylar
    RAIL_BOTTOM_5V: 320,
    RAIL_BOTTOM_GND: 338,
  },
  zones: [
    { id: 'zone1', name: 'Sol Bölge (Sütun 1–8)', tag: 'LED & Direnç', startCol: 1, endCol: 8, color: '#38bdf8' },
    { id: 'zone2', name: 'Orta Bölge (Sütun 10–18)', tag: 'Sensörler & Buton', startCol: 10, endCol: 18, color: '#a855f7' },
    { id: 'zone3', name: 'Sağ Bölge (Sütun 20–28)', tag: 'Buzzer & Servo', startCol: 20, endCol: 28, color: '#f59e0b' },
  ]
};

/**
 * Belirtilen Breadboard pin adını (örn: A5, E10, J16, RAIL_GND, RAIL_5V)
 * deterministik olarak SVG koordinatına çevirir.
 */
export function getBreadboardHoleCoord(pinName: string, hintCol?: number): PinPosition {
  const p = (pinName || '').toUpperCase().trim();

  // 1. Güç Rayları
  if (p.includes('GND') || p.includes('RAIL_GND') || p === '-') {
    const col = hintCol && hintCol >= 1 && hintCol <= 30 ? hintCol : 10;
    const x = BREADBOARD_GRID.getColX(col);
    // Alt raya yakınsa alt ray, değilse üst ray
    return {
      x,
      y: BREADBOARD_GRID.rows.RAIL_BOTTOM_GND,
      label: 'RAIL_GND (-)',
      row: 'RAIL',
      col,
      net: 'RAIL_GND'
    };
  }

  if (p.includes('5V') || p.includes('RAIL_5V') || p === '+') {
    const col = hintCol && hintCol >= 1 && hintCol <= 30 ? hintCol : 8;
    const x = BREADBOARD_GRID.getColX(col);
    return {
      x,
      y: BREADBOARD_GRID.rows.RAIL_BOTTOM_5V,
      label: 'RAIL_5V (+)',
      row: 'RAIL',
      col,
      net: 'RAIL_5V'
    };
  }

  // 2. Standart Hücre: A1..J30 formatı
  const match = p.match(/^([A-J])(\d+)$/);
  if (match) {
    const rowChar = match[1] as keyof typeof BREADBOARD_GRID.rows;
    const colNum = parseInt(match[2], 10);
    const validCol = Math.max(1, Math.min(30, colNum));
    const x = BREADBOARD_GRID.getColX(validCol);
    const y = BREADBOARD_GRID.rows[rowChar] || BREADBOARD_GRID.rows.A;
    const half = 'ABCDE'.includes(rowChar) ? 'TOP' : 'BOTTOM';

    return {
      x,
      y,
      label: `${rowChar}${validCol}`,
      row: rowChar,
      col: validCol,
      net: `BB_${half}_${validCol}`
    };
  }

  // Fallback: Orta delik
  return {
    x: BREADBOARD_GRID.getColX(15),
    y: BREADBOARD_GRID.rows.E,
    label: p,
    row: 'E',
    col: 15,
    net: 'BB_TOP_15'
  };
}


// ========================================================
// 3. DOĞRUDAN BAĞLANTI MODU KOORDİNATLARI (DIRECT VIEW)
// Parçalar kartlar halinde düzenlenmiştir.
// ========================================================
export const PIN_COORDINATES: Record<string, ComponentLayout> = {
  ARDUINO_UNO: {
    id: 'ARDUINO_UNO',
    name: 'Arduino Uno R3',
    x: 280,
    y: 390,
    width: 440,
    height: 270,
    pins: ARDUINO_UNO_PINS,
  },

  LED_RED: {
    id: 'LED_RED',
    name: 'Kırmızı LED',
    x: 80,
    y: 80,
    width: 110,
    height: 150,
    pins: {
      ANODE: { x: 120, y: 200, label: 'Uzun (+)' },
      CATHODE: { x: 155, y: 200, label: 'Kısa (-)' },
      PLUS: { x: 120, y: 200, label: 'Uzun (+)' },
      MINUS: { x: 155, y: 200, label: 'Kısa (-)' },
    }
  },

  RESISTOR_220: {
    id: 'RESISTOR_220',
    name: '220Ω Direnç',
    x: 230,
    y: 80,
    width: 140,
    height: 90,
    pins: {
      PIN1: { x: 250, y: 130, label: 'Uç 1' },
      PIN2: { x: 350, y: 130, label: 'Uç 2' },
      A: { x: 250, y: 130, label: 'Uç 1' },
      B: { x: 350, y: 130, label: 'Uç 2' },
    }
  },

  LDR_SENSOR: {
    id: 'LDR_SENSOR',
    name: 'LDR Işık Sensörü',
    x: 400,
    y: 80,
    width: 120,
    height: 140,
    pins: {
      PIN1: { x: 430, y: 180, label: '5V' },
      PIN2: { x: 480, y: 180, label: 'A0' },
      VCC: { x: 430, y: 180, label: '5V' },
      GND: { x: 480, y: 180, label: 'A0' },
    }
  },

  HCSR04: {
    id: 'HCSR04',
    name: 'Mesafe Sensörü (HC-SR04)',
    x: 550,
    y: 80,
    width: 170,
    height: 140,
    pins: {
      VCC: { x: 580, y: 180, label: 'VCC' },
      TRIG: { x: 610, y: 180, label: 'TRIG' },
      ECHO: { x: 640, y: 180, label: 'ECHO' },
      GND: { x: 670, y: 180, label: 'GND' },
    }
  },

  BUZZER: {
    id: 'BUZZER',
    name: 'Buzzer (Ses Çıkarıcı)',
    x: 750,
    y: 80,
    width: 120,
    height: 140,
    pins: {
      PLUS: { x: 785, y: 180, label: 'ART (+)' },
      VCC: { x: 785, y: 180, label: 'ART (+)' },
      GND: { x: 835, y: 180, label: 'GND (-)' },
      MINUS: { x: 835, y: 180, label: 'GND (-)' },
    }
  },

  BUTTON: {
    id: 'BUTTON',
    name: 'Buton',
    x: 100,
    y: 260,
    width: 110,
    height: 110,
    pins: {
      PIN1: { x: 130, y: 340, label: 'Giriş' },
      PIN2: { x: 180, y: 340, label: 'GND' },
      VCC: { x: 130, y: 340, label: 'Giriş' },
      GND: { x: 180, y: 340, label: 'GND' },
    }
  },

  SERVO: {
    id: 'SERVO',
    name: 'Servo Motor',
    x: 750,
    y: 260,
    width: 140,
    height: 100,
    pins: {
      GND: { x: 780, y: 340, label: 'GND' },
      VCC: { x: 810, y: 340, label: '5V' },
      SIGNAL: { x: 840, y: 340, label: 'Sinyal' },
      PWM: { x: 840, y: 340, label: 'Sinyal' },
    }
  }
};


// ========================================================
// 4. BREADBOARD MODUNDA BİLEŞEN SLOTLARI
// Bileşen bacaklarının takıldığı delikler:
// - LED_RED: Anot E5, Katot E6 (Jumper A5'e takılır)
// - RESISTOR_220: Pin 1 C6 (LED katot ile aynı sütunda!), Pin 2 RAIL_GND
// - LDR_SENSOR: Pin 1 E12, Pin 2 E14 (Jumper A12'ye takılır)
// - HCSR04: VCC F14, TRIG F15, ECHO F16, GND F17 (Jumperlar J14..J17'ye takılır)
// - BUZZER: Plus F22, Minus F24 (Jumperlar J22, J24'e takılır)
// ========================================================
export const BREADBOARD_COMPONENT_SLOTS = {
  LED_RED: {
    anode: { row: 'E', col: 5 },
    cathode: { row: 'E', col: 6 },
    jumperHole: { row: 'A', col: 5 },
  },
  RESISTOR_220: {
    pin1: { row: 'C', col: 6 },
    pin2: { row: 'RAIL_GND', col: 6 },
  },
  LDR_SENSOR: {
    pin1: { row: 'E', col: 12 },
    pin2: { row: 'E', col: 14 },
    jumperHole: { row: 'A', col: 12 },
  },
  HCSR04: {
    vcc: { row: 'F', col: 14 },
    trig: { row: 'F', col: 15 },
    echo: { row: 'F', col: 16 },
    gnd: { row: 'F', col: 17 },
  },
  BUZZER: {
    plus: { row: 'F', col: 22 },
    minus: { row: 'F', col: 24 },
  }
};


/**
 * Parça ve pin adına göre SVG koordinatını döner.
 * mode: 'direct' veya 'breadboard'
 */
export function getPinCoordinates(
  parca: string,
  pin: string,
  mode: 'direct' | 'breadboard' = 'breadboard'
): PinPosition | null {
  const compKey = (parca || '').toUpperCase().trim();
  const cleanPin = (pin || '').toUpperCase().trim();

  // 1. Arduino Pin Kontrolleri
  if (compKey === 'ARDUINO_UNO') {
    const uno = ARDUINO_UNO_PINS;
    if (uno[cleanPin]) return uno[cleanPin];
    
    // "13" -> "D13", "8" -> "D8"
    const withD = `D${cleanPin}`;
    if (uno[withD]) return uno[withD];
    
    if (cleanPin.includes('5V')) return uno['5V'];
    if (cleanPin.includes('3.3')) return uno['3.3V'];
    if (cleanPin.includes('GND')) return uno.GND;
    if (cleanPin.startsWith('A') && uno[cleanPin]) return uno[cleanPin];

    return null;
  }

  // 2. Doğrudan Breadboard Deliği veya Güç Hattı (Örn: A5, E6, C6, J15, RAIL_GND, RAIL_5V)
  if (compKey === 'BREADBOARD' || compKey === 'BB' || /^[A-J]\d+$/.test(cleanPin) || cleanPin.startsWith('RAIL_')) {
    return getBreadboardHoleCoord(cleanPin);
  }

  // 3. Breadboard Modunda Parça Eşleştirmesi (Otomatik Slot Çözücü)
  if (mode === 'breadboard') {
    if (compKey.includes('LED')) {
      if (['ANODE', 'PLUS', 'ART', '+', 'UZUN'].some(k => cleanPin.includes(k))) {
        return getBreadboardHoleCoord('A5'); // Jumper A5'e gelir
      }
      return getBreadboardHoleCoord('E6'); // Katot E6'dadır
    }

    if (compKey.includes('RESISTOR')) {
      if (cleanPin.includes('2') || cleanPin.includes('GND') || cleanPin.includes('B')) {
        return getBreadboardHoleCoord('RAIL_GND', 6);
      }
      return getBreadboardHoleCoord('C6');
    }

    if (compKey.includes('LDR')) {
      if (cleanPin.includes('2') || cleanPin.includes('A0') || cleanPin.includes('SIGNAL')) {
        return getBreadboardHoleCoord('A12');
      }
      return getBreadboardHoleCoord('A14');
    }

    if (compKey === 'HCSR04') {
      if (cleanPin.includes('TRIG')) return getBreadboardHoleCoord('J15');
      if (cleanPin.includes('ECHO')) return getBreadboardHoleCoord('J16');
      if (cleanPin.includes('VCC') || cleanPin.includes('5V')) return getBreadboardHoleCoord('J14');
      if (cleanPin.includes('GND')) return getBreadboardHoleCoord('J17');
    }

    if (compKey === 'BUZZER') {
      if (cleanPin.includes('PLUS') || cleanPin.includes('VCC') || cleanPin.includes('ART') || cleanPin.includes('+')) {
        return getBreadboardHoleCoord('J22');
      }
      return getBreadboardHoleCoord('J24');
    }

    // Bilinmeyen pin için delik çözümleyiciye gönder
    return getBreadboardHoleCoord(cleanPin);
  }

  // 4. Doğrudan Bağlantı Modu (Direct Mode Card Layout)
  const directComp = PIN_COORDINATES[compKey];
  if (directComp) {
    if (directComp.pins[cleanPin]) return directComp.pins[cleanPin];

    if (compKey === 'HCSR04') {
      if (cleanPin.includes('TRIG')) return directComp.pins.TRIG;
      if (cleanPin.includes('ECHO')) return directComp.pins.ECHO;
      if (cleanPin.includes('VCC') || cleanPin.includes('5V')) return directComp.pins.VCC;
      if (cleanPin.includes('GND')) return directComp.pins.GND;
    }

    if (compKey.includes('LED')) {
      if (['ANODE', 'PLUS', 'ART', '+', 'UZUN'].some(k => cleanPin.includes(k))) return directComp.pins.ANODE;
      return directComp.pins.CATHODE;
    }

    if (compKey.includes('RESISTOR')) {
      if (cleanPin.includes('2') || cleanPin.includes('B')) return directComp.pins.PIN2;
      return directComp.pins.PIN1;
    }

    if (compKey.includes('LDR')) {
      if (cleanPin.includes('2') || cleanPin.includes('A0')) return directComp.pins.PIN2;
      return directComp.pins.PIN1;
    }

    if (compKey === 'BUZZER') {
      if (cleanPin.includes('PLUS') || cleanPin.includes('VCC') || cleanPin.includes('+')) return directComp.pins.PLUS;
      return directComp.pins.GND;
    }

    return Object.values(directComp.pins)[0] || null;
  }

  return null;
}

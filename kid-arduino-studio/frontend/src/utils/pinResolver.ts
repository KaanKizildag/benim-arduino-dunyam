/**
 * Universal Pin Resolver for Wokwi Elements (.pinInfo API)
 * Deterministik pin eşleştirme ve koordinat hesaplama motoru.
 */

export interface PinCoord {
  x: number;
  y: number;
}

export interface WokwiPin {
  name: string;
  x: number;
  y: number;
  signals?: any[];
  description?: string;
}

/**
 * Given a DOM element and a requested pin name, returns the {x, y} offset
 * relative to the element's top-left origin.
 */
export function resolveElementPin(el: HTMLElement, rawPinName: string): PinCoord {
  if (!el) {
    return { x: 0, y: 0 };
  }

  const pinInfo: WokwiPin[] = (el as any).pinInfo || [];
  const query = (rawPinName || '').trim().toLowerCase();

  // If no pinInfo available yet, return element center as safe fallback
  if (!Array.isArray(pinInfo) || pinInfo.length === 0) {
    const rect = el.getBoundingClientRect();
    return { x: rect.width / 2 || 15, y: rect.height / 2 || 15 };
  }

  // 1. Direct case-insensitive match
  const exact = pinInfo.find(p => p.name.toLowerCase() === query);
  if (exact) {
    return { x: exact.x, y: exact.y };
  }

  // 2. Arduino Uno / Nano / Mega aliases:
  // e.g. "D13" -> "13", "D2" -> "2", "PIN13" -> "13"
  const dMatch = query.match(/^d(\d+)$/);
  if (dMatch) {
    const num = dMatch[1];
    const matchNum = pinInfo.find(p => p.name.toLowerCase() === num);
    if (matchNum) return { x: matchNum.x, y: matchNum.y };
  }

  // GND variations: "GND", "GND.1", "GND.2", "GND.3"
  if (query.includes('gnd') || query === 'ground' || query === 'neg') {
    const gnd = pinInfo.find(p => p.name.toLowerCase().startsWith('gnd'));
    if (gnd) return { x: gnd.x, y: gnd.y };
  }

  // 5V / VCC variations: "5V", "VCC", "VIN"
  if (query === '5v' || query === 'vcc' || query === 'power') {
    const v5 = pinInfo.find(p => p.name.toLowerCase() === '5v' || p.name.toLowerCase() === 'vcc');
    if (v5) return { x: v5.x, y: v5.y };
  }

  // 3.3V
  if (query === '3.3v' || query === '3v3') {
    const v3 = pinInfo.find(p => p.name.toLowerCase() === '3.3v');
    if (v3) return { x: v3.x, y: v3.y };
  }

  // LED aliases: ANODE -> 'A', CATHODE -> 'C'
  if (query === 'anode' || query === 'uzun_bacak' || query === 'plus' || query === '+') {
    const a = pinInfo.find(p => p.name.toUpperCase() === 'A');
    if (a) return { x: a.x, y: a.y };
  }
  if (query === 'cathode' || query === 'kisa_bacak' || query === 'minus' || query === '-') {
    const c = pinInfo.find(p => p.name.toUpperCase() === 'C');
    if (c) return { x: c.x, y: c.y };
  }

  // Resistor / Buzzer aliases: PIN_1, PIN_2, 1, 2
  if (query === 'pin_1' || query === 'bacak_1') {
    const p1 = pinInfo.find(p => p.name === '1');
    if (p1) return { x: p1.x, y: p1.y };
  }
  if (query === 'pin_2' || query === 'bacak_2') {
    const p2 = pinInfo.find(p => p.name === '2');
    if (p2) return { x: p2.x, y: p2.y };
  }

  // Breadboard aliases: "E5" -> "5e" or "e5", "RAIL_5V" -> "top-+", "RAIL_GND" -> "top--"
  if (query.includes('rail') || query.includes('power')) {
    if (query.includes('gnd') || query.includes('-')) {
      const gndRail = pinInfo.find(p => p.name.toLowerCase() === 'top--' || p.name.toLowerCase() === 'gnd');
      if (gndRail) return { x: gndRail.x, y: gndRail.y };
    }
    const pRail = pinInfo.find(p => p.name.toLowerCase() === 'top-+' || p.name.toLowerCase() === '5v');
    if (pRail) return { x: pRail.x, y: pRail.y };
  }

  // Breadboard coordinate flip: e.g. "e5" -> "5e" or vice versa
  const colRowMatch = query.match(/^([a-j])(\d{1,2})$/);
  if (colRowMatch) {
    const flipped = `${colRowMatch[2]}${colRowMatch[1]}`;
    const foundFlipped = pinInfo.find(p => p.name.toLowerCase() === flipped);
    if (foundFlipped) return { x: foundFlipped.x, y: foundFlipped.y };
  }

  // Substring match
  const sub = pinInfo.find(p => p.name.toLowerCase().includes(query) || query.includes(p.name.toLowerCase()));
  if (sub) {
    return { x: sub.x, y: sub.y };
  }

  // Final fallback: first pin or middle of element
  if (pinInfo.length > 0) {
    return { x: pinInfo[0].x, y: pinInfo[0].y };
  }

  return { x: 10, y: 10 };
}

/**
 * Calculates absolute coordinate on the canvas for a component's pin.
 * Formula:
 * pinCanvasX = bilesenCanvasX + pinInfo.x
 * pinCanvasY = bilesenCanvasY + pinInfo.y
 */
export function calculateCanvasPinPosition(
  componentPosition: { x: number; y: number },
  pinOffset: PinCoord
): PinCoord {
  return {
    x: componentPosition.x + pinOffset.x,
    y: componentPosition.y + pinOffset.y
  };
}

/**
 * Generates an organic, natural bezier curve connecting two pin coordinates.
 */
export function createWirePath(p1: PinCoord, p2: PinCoord): string {
  const dx = p2.x - p1.x;
  const dy = p2.y - p1.y;
  const dist = Math.sqrt(dx * dx + dy * dy);

  // Curvature increases with distance to simulate cable gravity slack
  const curvature = Math.min(100, Math.max(35, dist * 0.28));

  // Control points curve downwards
  const cx1 = p1.x + dx * 0.25;
  const cy1 = p1.y + curvature;
  const cx2 = p2.x - dx * 0.25;
  const cy2 = p2.y + curvature;

  return `M ${p1.x.toFixed(1)} ${p1.y.toFixed(1)} C ${cx1.toFixed(1)} ${cy1.toFixed(1)}, ${cx2.toFixed(1)} ${cy2.toFixed(1)}, ${p2.x.toFixed(1)} ${p2.y.toFixed(1)}`;
}

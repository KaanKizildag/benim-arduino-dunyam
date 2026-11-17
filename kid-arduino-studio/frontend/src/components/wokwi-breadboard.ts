/**
 * Custom Web Component for Breadboard implementing Wokwi .pinInfo API.
 * Provides standard 30-column half-size breadboard with metallic holes and power rails.
 */

export interface BreadboardPin {
  name: string;
  x: number;
  y: number;
}

export class WokwiBreadboardHalfElement extends HTMLElement {
  public pinInfo: BreadboardPin[] = [];
  private shadow: ShadowRoot;

  constructor() {
    super();
    this.shadow = this.attachShadow({ mode: 'open' });
    this.generatePinInfo();
    this.render();
  }

  private generatePinInfo() {
    const pins: BreadboardPin[] = [];
    const startX = 38;
    const colPitch = 9.5;
    const cols = 30;

    const rowYMap: Record<string, number> = {
      a: 48,
      b: 57.5,
      c: 67,
      d: 76.5,
      e: 86,
      f: 118,
      g: 127.5,
      h: 137,
      i: 146.5,
      j: 156,
    };

    // Terminal holes: 1a..30j
    for (let col = 1; col <= cols; col++) {
      const cx = startX + (col - 1) * colPitch;
      for (const [row, cy] of Object.entries(rowYMap)) {
        const pinName = `${col}${row}`;
        pins.push({ name: pinName, x: cx, y: cy });
        // Also add row+col alias (e.g. 'e5' -> same hole as '5e')
        pins.push({ name: `${row}${col}`, x: cx, y: cy });
      }

      // Top power rails: + (16), - (28)
      pins.push({ name: `top-+.${col}`, x: cx, y: 16 });
      pins.push({ name: `top--.${col}`, x: cx, y: 28 });
      // Bottom power rails: + (176), - (188)
      pins.push({ name: `bottom-+.${col}`, x: cx, y: 176 });
      pins.push({ name: `bottom--.${col}`, x: cx, y: 188 });
    }

    // Generic power rail names pointing to representative center holes
    pins.push({ name: 'top-+', x: startX + 14 * colPitch, y: 16 });
    pins.push({ name: 'top--', x: startX + 14 * colPitch, y: 28 });
    pins.push({ name: 'bottom-+', x: startX + 14 * colPitch, y: 176 });
    pins.push({ name: 'bottom--', x: startX + 14 * colPitch, y: 188 });
    pins.push({ name: 'power-+', x: startX + 14 * colPitch, y: 16 });
    pins.push({ name: 'power--', x: startX + 14 * colPitch, y: 28 });
    pins.push({ name: '5V', x: startX + 14 * colPitch, y: 16 });
    pins.push({ name: 'GND', x: startX + 14 * colPitch, y: 28 });

    this.pinInfo = pins;
  }

  private render() {
    const width = 352;
    const height = 206;
    const startX = 38;
    const colPitch = 9.5;
    const cols = 30;

    let holesSvg = '';

    // Draw top & bottom power rail holes
    for (let c = 1; c <= cols; c++) {
      const cx = startX + (c - 1) * colPitch;
      holesSvg += `
        <rect x="${cx - 2}" y="14" width="4" height="4" rx="1" fill="#1e293b" stroke="#64748b" stroke-width="0.5" />
        <rect x="${cx - 2}" y="26" width="4" height="4" rx="1" fill="#1e293b" stroke="#64748b" stroke-width="0.5" />
        <rect x="${cx - 2}" y="174" width="4" height="4" rx="1" fill="#1e293b" stroke="#64748b" stroke-width="0.5" />
        <rect x="${cx - 2}" y="186" width="4" height="4" rx="1" fill="#1e293b" stroke="#64748b" stroke-width="0.5" />
      `;
    }

    // Draw terminal holes (a-e and f-j)
    const rowsUpper = [48, 57.5, 67, 76.5, 86];
    const rowsLower = [118, 127.5, 137, 146.5, 156];

    for (let c = 1; c <= cols; c++) {
      const cx = startX + (c - 1) * colPitch;
      for (const cy of rowsUpper) {
        holesSvg += `<rect x="${cx - 2.2}" y="${cy - 2.2}" width="4.4" height="4.4" rx="1" fill="#1e293b" stroke="#64748b" stroke-width="0.5" />`;
      }
      for (const cy of rowsLower) {
        holesSvg += `<rect x="${cx - 2.2}" y="${cy - 2.2}" width="4.4" height="4.4" rx="1" fill="#1e293b" stroke="#64748b" stroke-width="0.5" />`;
      }
    }

    // Column numbers labels
    let colNumbersSvg = '';
    for (let c = 1; c <= cols; c++) {
      if (c === 1 || c % 5 === 0) {
        const cx = startX + (c - 1) * colPitch;
        colNumbersSvg += `
          <text x="${cx}" y="42" font-size="6.5" font-weight="bold" fill="#64748b" text-anchor="middle">${c}</text>
          <text x="${cx}" y="112" font-size="6.5" font-weight="bold" fill="#64748b" text-anchor="middle">${c}</text>
        `;
      }
    }

    this.shadow.innerHTML = `
      <style>
        :host {
          display: inline-block;
          width: ${width}px;
          height: ${height}px;
          user-select: none;
        }
        svg {
          width: 100%;
          height: 100%;
          filter: drop-shadow(0 6px 12px rgba(15, 23, 42, 0.25));
        }
      </style>
      <svg viewBox="0 0 ${width} ${height}" xmlns="http://www.w3.org/2000/svg">
        <!-- Main Board Body -->
        <rect x="0" y="0" width="${width}" height="${height}" rx="12" fill="#f8fafc" stroke="#cbd5e1" stroke-width="2" />
        
        <!-- Subtle Inner Highlight & Texture -->
        <rect x="3" y="3" width="${width - 6}" height="${height - 6}" rx="10" fill="none" stroke="#ffffff" stroke-width="1.5" />

        <!-- Power Rails Colored Stripes -->
        <!-- Top + (Red) -->
        <line x1="28" y1="16" x2="330" y2="16" stroke="#ef4444" stroke-width="1" stroke-dasharray="2 3" opacity="0.4" />
        <line x1="22" y1="16" x2="26" y2="16" stroke="#ef4444" stroke-width="2" />
        <text x="14" y="19" font-size="9" font-weight="900" fill="#ef4444" text-anchor="middle">+</text>

        <!-- Top - (Blue) -->
        <line x1="28" y1="28" x2="330" y2="28" stroke="#3b82f6" stroke-width="1" stroke-dasharray="2 3" opacity="0.4" />
        <line x1="22" y1="28" x2="26" y2="28" stroke="#3b82f6" stroke-width="2" />
        <text x="14" y="30" font-size="11" font-weight="900" fill="#3b82f6" text-anchor="middle">-</text>

        <!-- Bottom + (Red) -->
        <line x1="28" y1="176" x2="330" y2="176" stroke="#ef4444" stroke-width="1" stroke-dasharray="2 3" opacity="0.4" />
        <line x1="22" y1="176" x2="26" y2="176" stroke="#ef4444" stroke-width="2" />
        <text x="14" y="179" font-size="9" font-weight="900" fill="#ef4444" text-anchor="middle">+</text>

        <!-- Bottom - (Blue) -->
        <line x1="28" y1="188" x2="330" y2="188" stroke="#3b82f6" stroke-width="1" stroke-dasharray="2 3" opacity="0.4" />
        <line x1="22" y1="188" x2="26" y2="188" stroke="#3b82f6" stroke-width="2" />
        <text x="14" y="190" font-size="11" font-weight="900" fill="#3b82f6" text-anchor="middle">-</text>

        <!-- Middle Divider Groove -->
        <rect x="18" y="98" width="${width - 36}" height="7" rx="3.5" fill="#e2e8f0" stroke="#cbd5e1" stroke-width="1" />

        <!-- Row Letters (A, B, C, D, E) -->
        <g font-size="6.5" font-weight="bold" fill="#64748b" text-anchor="middle">
          <text x="24" y="50">A</text>
          <text x="24" y="60">B</text>
          <text x="24" y="69">C</text>
          <text x="24" y="79">D</text>
          <text x="24" y="88">E</text>
          <text x="328" y="50">A</text>
          <text x="328" y="60">B</text>
          <text x="328" y="69">C</text>
          <text x="328" y="79">D</text>
          <text x="328" y="88">E</text>

          <!-- Row Letters (F, G, H, I, J) -->
          <text x="24" y="120">F</text>
          <text x="24" y="130">G</text>
          <text x="24" y="139">H</text>
          <text x="24" y="149">I</text>
          <text x="24" y="158">J</text>
          <text x="328" y="120">F</text>
          <text x="328" y="130">G</text>
          <text x="328" y="139">H</text>
          <text x="328" y="149">I</text>
          <text x="328" y="158">J</text>
        </g>

        <!-- Column Numbers -->
        ${colNumbersSvg}

        <!-- All Holes -->
        ${holesSvg}
      </svg>
    `;
  }
}

export class WokwiBreadboardElement extends WokwiBreadboardHalfElement {}

// Register both names if not already defined
if (!customElements.get('wokwi-breadboard-half')) {
  customElements.define('wokwi-breadboard-half', WokwiBreadboardHalfElement);
}
if (!customElements.get('wokwi-breadboard')) {
  customElements.define('wokwi-breadboard', WokwiBreadboardElement);
}

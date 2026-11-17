/**
 * Custom Web Component for Breadboard implementing Wokwi .pinInfo API.
 * Provides standard 30-column half-size breadboard with metallic holes, power rails,
 * and visual internal conductivity indicators.
 */

export interface BreadboardPin {
  name: string;
  x: number;
  y: number;
}

export class WokwiBreadboardHalfElement extends HTMLElement {
  public pinInfo: BreadboardPin[] = [];
  private shadow: ShadowRoot;

  static get observedAttributes() {
    return ['highlighted-columns', 'highlighted-rails'];
  }

  constructor() {
    super();
    this.shadow = this.attachShadow({ mode: 'open' });
    this.generatePinInfo();
    this.render();
  }

  attributeChangedCallback() {
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
        pins.push({ name: `${col}${row}`, x: cx, y: cy });
        pins.push({ name: `${col}${row.toUpperCase()}`, x: cx, y: cy });
        pins.push({ name: `${row}${col}`, x: cx, y: cy });
        pins.push({ name: `${row.toUpperCase()}${col}`, x: cx, y: cy });
      }

      // Top power rails: + (16), - (28)
      pins.push({ name: `top-+.${col}`, x: cx, y: 16 });
      pins.push({ name: `top--.${col}`, x: cx, y: 28 });
      // Bottom power rails: + (176), - (188)
      pins.push({ name: `bottom-+.${col}`, x: cx, y: 176 });
      pins.push({ name: `bottom--.${col}`, x: cx, y: 188 });
    }

    // Generic power rail names pointing to representative holes
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

    const rawCols = this.getAttribute('highlighted-columns') || '';
    const activeCols = rawCols.split(',').map(s => parseInt(s.trim(), 10)).filter(n => !isNaN(n));

    const rawRails = (this.getAttribute('highlighted-rails') || '').toLowerCase();
    const highlightTopPlus = rawRails.includes('top-+') || rawRails.includes('5v');
    const highlightTopMinus = rawRails.includes('top--') || rawRails.includes('gnd');

    // 1. Column Conductivity Glow Strips (İç İletkenlik Bakır Şeritleri)
    let conductivityGlowSvg = '';
    for (const c of activeCols) {
      if (c >= 1 && c <= cols) {
        const cx = startX + (c - 1) * colPitch;
        // Upper section (A-E)
        conductivityGlowSvg += `
          <rect x="${cx - 3.5}" y="44" width="7" height="46" rx="3.5" fill="#facc15" fill-opacity="0.35" stroke="#eab308" stroke-width="1.2" />
        `;
      }
    }

    // 2. Power Rail Glow Strips
    let railGlowSvg = '';
    if (highlightTopPlus) {
      railGlowSvg += `
        <rect x="24" y="12" width="304" height="8" rx="4" fill="#ef4444" fill-opacity="0.25" stroke="#ef4444" stroke-width="1" />
      `;
    }
    if (highlightTopMinus) {
      railGlowSvg += `
        <rect x="24" y="24" width="304" height="8" rx="4" fill="#3b82f6" fill-opacity="0.25" stroke="#3b82f6" stroke-width="1" />
      `;
    }

    // 3. Holes Svg
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
      const isColActive = activeCols.includes(c);
      const holeBorder = isColActive ? '#ca8a04' : '#64748b';
      const holeFill = isColActive ? '#0f172a' : '#1e293b';

      for (const cy of rowsUpper) {
        holesSvg += `<rect x="${cx - 2.2}" y="${cy - 2.2}" width="4.4" height="4.4" rx="1" fill="${holeFill}" stroke="${holeBorder}" stroke-width="${isColActive ? '1' : '0.5'}" />`;
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
        const isColActive = activeCols.includes(c);
        const colColor = isColActive ? '#eab308' : '#64748b';
        colNumbersSvg += `
          <text x="${cx}" y="42" font-size="6.5" font-weight="${isColActive ? '900' : 'bold'}" fill="${colColor}" text-anchor="middle">${c}</text>
          <text x="${cx}" y="112" font-size="6.5" font-weight="${isColActive ? '900' : 'bold'}" fill="${colColor}" text-anchor="middle">${c}</text>
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
          position: relative;
        }
        svg {
          width: 100%;
          height: 100%;
          filter: drop-shadow(0 6px 14px rgba(15, 23, 42, 0.3));
        }
      </style>
      <svg viewBox="0 0 ${width} ${height}" xmlns="http://www.w3.org/2000/svg">
        <!-- Main Board Body -->
        <rect x="0" y="0" width="${width}" height="${height}" rx="14" fill="#f8fafc" stroke="#cbd5e1" stroke-width="2.5" />
        
        <!-- Inner Board Highlight -->
        <rect x="3" y="3" width="${width - 6}" height="${height - 6}" rx="11" fill="none" stroke="#ffffff" stroke-width="1.5" />

        <!-- Power Rails Glow Strips -->
        ${railGlowSvg}

        <!-- Top Power Rail Lines -->
        <line x1="28" y1="16" x2="330" y2="16" stroke="#ef4444" stroke-width="1.2" stroke-dasharray="2 3" opacity="0.5" />
        <line x1="20" y1="16" x2="25" y2="16" stroke="#ef4444" stroke-width="2" />
        <text x="13" y="19.5" font-size="10" font-weight="900" fill="#ef4444" text-anchor="middle">+</text>

        <line x1="28" y1="28" x2="330" y2="28" stroke="#3b82f6" stroke-width="1.2" stroke-dasharray="2 3" opacity="0.5" />
        <line x1="20" y1="28" x2="25" y2="28" stroke="#3b82f6" stroke-width="2" />
        <text x="13" y="30.5" font-size="12" font-weight="900" fill="#3b82f6" text-anchor="middle">-</text>

        <!-- Bottom Power Rail Lines -->
        <line x1="28" y1="176" x2="330" y2="176" stroke="#ef4444" stroke-width="1.2" stroke-dasharray="2 3" opacity="0.5" />
        <line x1="20" y1="176" x2="25" y2="176" stroke="#ef4444" stroke-width="2" />
        <text x="13" y="179.5" font-size="10" font-weight="900" fill="#ef4444" text-anchor="middle">+</text>

        <line x1="28" y1="188" x2="330" y2="188" stroke="#3b82f6" stroke-width="1.2" stroke-dasharray="2 3" opacity="0.5" />
        <line x1="20" y1="188" x2="25" y2="188" stroke="#3b82f6" stroke-width="2" />
        <text x="13" y="190.5" font-size="12" font-weight="900" fill="#3b82f6" text-anchor="middle">-</text>

        <!-- Middle Divider Groove -->
        <rect x="16" y="98" width="${width - 32}" height="7" rx="3.5" fill="#e2e8f0" stroke="#cbd5e1" stroke-width="1" />

        <!-- Row Letters (A, B, C, D, E) -->
        <g font-size="6.5" font-weight="bold" fill="#64748b" text-anchor="middle">
          <text x="23" y="50.5">A</text>
          <text x="23" y="60">B</text>
          <text x="23" y="69.5">C</text>
          <text x="23" y="79">D</text>
          <text x="23" y="88.5">E</text>
          <text x="329" y="50.5">A</text>
          <text x="329" y="60">B</text>
          <text x="329" y="69.5">C</text>
          <text x="329" y="79">D</text>
          <text x="329" y="88.5">E</text>

          <!-- Row Letters (F, G, H, I, J) -->
          <text x="23" y="120.5">F</text>
          <text x="23" y="130">G</text>
          <text x="23" y="139.5">H</text>
          <text x="23" y="149">I</text>
          <text x="23" y="158.5">J</text>
          <text x="329" y="120.5">F</text>
          <text x="329" y="130">G</text>
          <text x="329" y="139.5">H</text>
          <text x="329" y="149">I</text>
          <text x="329" y="158.5">J</text>
        </g>

        <!-- Column Numbers -->
        ${colNumbersSvg}

        <!-- Active Column Vertical Conductivity Metal Strips -->
        ${conductivityGlowSvg}

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

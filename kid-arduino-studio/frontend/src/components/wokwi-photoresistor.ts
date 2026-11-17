/**
 * Custom Web Component for 2-Pin Classic Photoresistor (Discrete LDR)
 * Standard 2-legged CdS light-dependent resistor implementing Wokwi .pinInfo API.
 */

export interface WokwiPinInfo {
  name: string;
  x: number;
  y: number;
  signals?: any[];
}

export class WokwiPhotoresistorElement extends HTMLElement {
  public pinInfo: WokwiPinInfo[] = [];
  private shadow: ShadowRoot;

  constructor() {
    super();
    this.shadow = this.attachShadow({ mode: 'open' });
    this.pinInfo = [
      { name: '1', x: 8.5, y: 42 },
      { name: '2', x: 27.5, y: 42 }
    ];
    this.render();
  }

  private render() {
    const width = 36;
    const height = 46;

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
          filter: drop-shadow(0 4px 6px rgba(15, 23, 42, 0.25));
        }
      </style>
      <svg viewBox="0 0 ${width} ${height}" xmlns="http://www.w3.org/2000/svg">
        <!-- 2 Metalik Bacak (Pins: x=8.5 ve x=27.5, y=42) -->
        <line x1="8.5" y1="20" x2="8.5" y2="42" stroke="#94a3b8" stroke-width="2" stroke-linecap="round" />
        <line x1="27.5" y1="20" x2="27.5" y2="42" stroke="#94a3b8" stroke-width="2" stroke-linecap="round" />
        
        <!-- Bacak Bağlantı Lehimleri -->
        <circle cx="8.5" cy="20" r="2" fill="#64748b" />
        <circle cx="27.5" cy="20" r="2" fill="#64748b" />

        <!-- LDR Seramik Gövde (Disk) -->
        <circle cx="18" cy="13" r="12" fill="#fde68a" stroke="#d97706" stroke-width="1.8" />
        <circle cx="18" cy="13" r="10.5" fill="#fef08a" stroke="#f59e0b" stroke-width="1" />

        <!-- Klasik CdS Kıvrımlı Işığa Duyarlı Serantin Yolu (Zig-Zag) -->
        <path
          d="M 11 9 C 14 7, 22 7, 25 9
             C 25 11, 23 12, 13 12
             C 13 14, 23 15, 25 15
             C 25 17, 23 18, 11 18"
          fill="none"
          stroke="#b91c1c"
          stroke-width="1.8"
          stroke-linecap="round"
          stroke-linejoin="round"
        />

        <!-- Şeffaf Reçine Parlaması -->
        <ellipse cx="14" cy="9" rx="3" ry="1.8" fill="#ffffff" opacity="0.6" />
      </svg>
    `;
  }
}

if (!customElements.get('wokwi-photoresistor')) {
  customElements.define('wokwi-photoresistor', WokwiPhotoresistorElement);
}

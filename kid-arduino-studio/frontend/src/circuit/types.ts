/**
 * Netlist and Auto-Layout Engine Types
 */

export interface NetlistComponent {
  id: string;
  type: string; // 'wokwi-led' | 'wokwi-resistor' | 'wokwi-photoresistor' | 'wokwi-photoresistor-sensor' | 'wokwi-buzzer' | 'wokwi-pushbutton' | 'wokwi-servo' | 'wokwi-hc-sr04' | 'wokwi-potentiometer'
  props?: Record<string, any>; // e.g. { color: 'red' }, { value: '220' }
  label: string; // User-facing Turkish label, e.g. "Kırmızı LED"
}

export interface NetlistConnection {
  from: string; // e.g. "uno.D13", "r1.1", "ldr1.VCC"
  to: string;   // e.g. "r1.1", "led1.A", "GND", "5V", "uno.A0"
  color?: string; // e.g. "orange", "red", "black", "green", "#3b82f6"
}

export interface CircuitNetlist {
  board: string; // "arduino-uno" | "arduino-nano" | "esp32"
  components: NetlistComponent[];
  connections: NetlistConnection[];
}

export interface ElectricalNet {
  id: string;
  componentPins: string[]; // e.g. ["r1.2", "led1.A"]
  arduinoPins: string[];   // e.g. ["uno.D13"]
  powerRail?: 'GND' | '5V';
  color?: string;
}

export interface AllocatedPin {
  componentId: string;
  pinName: string;
  col: number;      // 1..30 (or 0 for off-board module pins)
  row: string;      // 'A'..'J' or 'offboard'
  holeName: string; // e.g. "5E", "6C", "bn.5"
  x: number;        // Relative to breadboard (px)
  y: number;        // Relative to breadboard (px)
}

export interface PlacedComponent {
  id: string;
  type: string;
  props: Record<string, any>;
  label: string;
  isBreadboardMounted: boolean;
  left: number;     // px
  top: number;      // px
  width?: number;
  height?: number;
  labelX: number;
  labelY: number;
  startCol: number;
  endCol: number;
  pins: Record<string, AllocatedPin>;
}

export interface RoutedWire {
  id: string;
  from: {
    part: string;
    pin: string;
    x: number;
    y: number;
    holeName?: string;
  };
  to: {
    part: string;
    pin: string;
    x: number;
    y: number;
    holeName?: string;
  };
  color: string;
  laneIndex: number;
  path: string;
  isPowerBus: boolean;
  description: string;
}

export interface AutoLayoutResult {
  netlist: CircuitNetlist;
  nets?: ElectricalNet[];
  components: PlacedComponent[];
  wires: RoutedWire[];
  highlightedColumns: number[];
  highlightedRails: string;
  errors: string[];
  warnings: string[];
}

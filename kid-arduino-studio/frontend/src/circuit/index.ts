/**
 * Unified Netlist-to-Breadboard Auto-Layout Engine
 */

import {
  SCENE_LAYOUT,
  type CircuitNetlist,
  type AutoLayoutResult,
  type PlacedComponent,
  type RoutedWire,
  type SceneBounds
} from './types';
import { normalizeNetlist } from './normalizeNetlist';
import { BreadboardAllocator } from './BreadboardAllocator';
import { WireRouter, type RouterOffsets } from './WireRouter';
import {
  validateNetlist,
  validateCompiledLayout,
  applyLabelStaggering
} from './validateCircuit';

export * from './types';
export * from './moduleGeometry';
export * from './normalizeNetlist';
export * from './BreadboardAllocator';
export * from './WireRouter';
export * from './validateCircuit';

export const DEFAULT_ROUTER_OFFSETS: RouterOffsets = {
  uno: { x: SCENE_LAYOUT.uno.x, y: SCENE_LAYOUT.uno.y },
  bb: { x: SCENE_LAYOUT.bb.x, y: SCENE_LAYOUT.bb.y }
};

function computeSceneBounds(
  components: PlacedComponent[],
  wires: RoutedWire[],
  offsets: RouterOffsets
): SceneBounds {
  const unoPad = SCENE_LAYOUT.uno.cardPad;
  const bbPad = SCENE_LAYOUT.bb.cardPad;

  let minX = offsets.uno.x - unoPad;
  let minY = offsets.uno.y - unoPad;
  let maxX = offsets.uno.x + SCENE_LAYOUT.uno.width + unoPad;
  let maxY = offsets.uno.y + SCENE_LAYOUT.uno.height + unoPad + SCENE_LAYOUT.uno.captionHeight;

  const includePoint = (x: number, y: number) => {
    if (Number.isFinite(x)) {
      if (x < minX) minX = x;
      if (x > maxX) maxX = x;
    }
    if (Number.isFinite(y)) {
      if (y < minY) minY = y;
      if (y > maxY) maxY = y;
    }
  };

  // Breadboard kartı
  includePoint(offsets.bb.x - bbPad, offsets.bb.y - bbPad);
  includePoint(
    offsets.bb.x + SCENE_LAYOUT.bb.width + bbPad,
    offsets.bb.y + SCENE_LAYOUT.bb.height + bbPad + SCENE_LAYOUT.bb.captionHeight
  );

  // Tüm bileşenler (breadboard üstü + off-board kartlar ve pin etiket payları)
  for (const comp of components) {
    if (comp.isBreadboardMounted) {
      const labelTop = offsets.bb.y + comp.top + comp.labelY - 14;
      includePoint(offsets.bb.x + comp.left, labelTop);
      includePoint(offsets.bb.x + comp.labelX + 40, offsets.bb.y + comp.top + 40);
    } else {
      const w = comp.width || 140;
      const h = comp.height || 96;
      // Yan ve alt/üst pin etiketleri için 26px/18px güvenlik marjı
      includePoint(comp.left - 26, comp.top - 16);
      includePoint(comp.left + w + 26, comp.top + h + 20);
    }
  }

  // Tüm kablo noktaları (highway lane channelY değerleri dahil)
  for (const wire of wires) {
    includePoint(wire.from.x, wire.from.y);
    includePoint(wire.to.x, wire.to.y);
    if (wire.points) {
      for (const pt of wire.points) {
        includePoint(pt.x, pt.y);
      }
    }
  }

  const pad = SCENE_LAYOUT.scenePadding;
  minX = Math.floor(minX - pad);
  minY = Math.floor(minY - pad);
  maxX = Math.ceil(maxX + pad);
  maxY = Math.ceil(maxY + pad);

  return {
    minX,
    minY,
    maxX,
    maxY,
    width: Math.max(1, maxX - minX),
    height: Math.max(1, maxY - minY)
  };
}

export function compileNetlistToBreadboard(
  rawNetlist: CircuitNetlist,
  offsets: RouterOffsets = DEFAULT_ROUTER_OFFSETS
): AutoLayoutResult {
  // 0. Pin/İsim Normalizasyonu ve Union-Find Düğüm (Net) Çıkarımı
  const norm = normalizeNetlist(rawNetlist);
  const netlist = norm.netlist;
  const nets = norm.nets;

  // 1. Elektriksel Doğrulama (Netlist Şema, Kısa Devre ve Açık Uç Kontrolü)
  const validation = validateNetlist(netlist);

  // 2. Dinamik Sütun, Yarı (A-E / F-J) ve Bölge Tahsisi (BreadboardAllocator)
  const allocator = new BreadboardAllocator();
  const allocation = allocator.allocate(netlist, nets);

  // 3. Etiket Çakışma Kademelendirmesi (Label Staggering)
  applyLabelStaggering(allocation.components);

  // 4. Net Tabanlı Kablo ve Şerit Yönlendirmesi (WireRouter)
  const router = new WireRouter(offsets);
  const wires = router.route(netlist, allocation.allocatedPins, nets);

  // 5. Son Fiziksel Yerleşim ve Elektriksel Bütünlük Doğrulaması
  const layoutErrors = validateCompiledLayout(
    netlist,
    nets,
    allocation.components,
    wires
  );

  // 6. Aktif Sütunlar ve Raylar
  const highlightedCols = new Set<number>();
  for (const comp of allocation.components) {
    if (comp.isBreadboardMounted) {
      for (const pin of Object.values(comp.pins)) {
        if (pin.col >= 1 && pin.col <= 30) {
          highlightedCols.add(pin.col);
        }
      }
    }
  }

  for (const node of allocation.internalSharedNodes) {
    highlightedCols.add(node.col);
  }

  const allErrors = [
    ...norm.errors,
    ...validation.errors,
    ...allocation.errors,
    ...layoutErrors
  ];
  const allWarnings = [
    ...norm.warnings,
    ...validation.warnings,
    ...allocation.warnings
  ];

  const bounds = computeSceneBounds(allocation.components, wires, offsets);

  return {
    netlist,
    nets,
    components: allocation.components,
    wires,
    bounds,
    highlightedColumns: Array.from(highlightedCols).sort((a, b) => a - b),
    highlightedRails: 'bp.+,bp.-',
    errors: allErrors,
    warnings: allWarnings
  };
}

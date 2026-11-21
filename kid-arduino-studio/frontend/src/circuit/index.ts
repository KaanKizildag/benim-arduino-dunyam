/**
 * Unified Netlist-to-Breadboard Auto-Layout Engine
 */

import type { CircuitNetlist, AutoLayoutResult } from './types';
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

export function compileNetlistToBreadboard(
  rawNetlist: CircuitNetlist,
  offsets: RouterOffsets = {
    uno: { x: 48, y: 108 },
    bb: { x: 448, y: 108 }
  }
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

  return {
    netlist,
    nets,
    components: allocation.components,
    wires,
    highlightedColumns: Array.from(highlightedCols).sort((a, b) => a - b),
    highlightedRails: 'bp.+,bp.-',
    errors: allErrors,
    warnings: allWarnings
  };
}

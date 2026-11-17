/**
 * Unified Netlist-to-Breadboard Auto-Layout Engine
 */

import type { CircuitNetlist, AutoLayoutResult } from './types';
import { BreadboardAllocator } from './BreadboardAllocator';
import { WireRouter, type RouterOffsets } from './WireRouter';
import { validateNetlist, applyLabelStaggering } from './validateCircuit';

export * from './types';
export * from './BreadboardAllocator';
export * from './WireRouter';
export * from './validateCircuit';

export function compileNetlistToBreadboard(
  netlist: CircuitNetlist,
  offsets: RouterOffsets = {
    uno: { x: 48, y: 108 },
    bb: { x: 448, y: 108 }
  }
): AutoLayoutResult {
  // 1. Elektriksel Doğrulama
  const validation = validateNetlist(netlist);

  // 2. Dinamik Sütun ve Bölge Tahsisi (BreadboardAllocator)
  const allocator = new BreadboardAllocator();
  const allocation = allocator.allocate(netlist);

  // 3. Etiket Çakışma Kademelendirmesi (Label Staggering)
  applyLabelStaggering(allocation.components);

  // 4. Akıllı Kablo ve Şerit Yönlendirmesi (WireRouter)
  const router = new WireRouter(offsets);
  const wires = router.route(netlist, allocation.allocatedPins);

  // 5. Aktif Sütunlar ve Raylar
  const highlightedCols = new Set<number>();
  for (const comp of allocation.components) {
    for (let c = comp.startCol; c <= comp.endCol; c++) {
      highlightedCols.add(c);
    }
  }

  // Seri bağlı paylaşımlı sütunları da ekle
  for (const node of allocation.internalSharedNodes) {
    highlightedCols.add(node.col);
  }

  return {
    netlist,
    components: allocation.components,
    wires,
    highlightedColumns: Array.from(highlightedCols).sort((a, b) => a - b),
    highlightedRails: 'bp.+,bp.-',
    errors: validation.errors,
    warnings: validation.warnings
  };
}

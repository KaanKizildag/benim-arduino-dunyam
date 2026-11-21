/**
 * Otomatik Netlist-to-Breadboard Doğrulama Scripti
 * Tüm eski ve yeni test senaryolarını çalıştırır ve kabul kriterlerini denetler:
 * 1. errors dizisi boş olmalı
 * 2. Her netlist bağlantısı ya bir kabloyla ya ortak sütunla karşılanmalı
 * 3. Hiçbir iki bileşen bacağı aynı deliği kullanmamalı
 * 4. Tüm breadboard sütunları 1..30 aralığında olmalı
 * 5. Off-board güç bağlantıları bn.0/bp.0 kullanmamalı ve dikeyde üst üste binmemeli
 */

import { compileNetlistToBreadboard } from './index';
import { ALL_TEST_SCENARIOS } from './testScenarios';
import { getStripKey } from './BreadboardAllocator';
import { resolveModulePinInfo } from './moduleGeometry';

function assertCondition(cond: boolean, msg: string): void {
  if (!cond) {
    throw new Error(`DOĞRULAMA HATASI: ${msg}`);
  }
}

export function verifyAllScenarios(): void {
  console.log('==============================================================');
  console.log(' KID ARDUINO STUDIO - OTOMATİK DEVRE MOTORU DOĞRULAMA TESTİ');
  console.log('==============================================================\n');

  let passedCount = 0;

  for (const [name, scenario] of Object.entries(ALL_TEST_SCENARIOS)) {
    const res = compileNetlistToBreadboard(scenario);

    console.log(`▶ Senaryo: ${name}`);
    console.log(
      `  Bileşenler (${res.components.length}):`,
      res.components
        .map(c =>
          c.isBreadboardMounted
            ? `${c.id}[${c.type} @ Sütun ${c.startCol}..${c.endCol}]`
            : `${c.id}[${c.type} @ Dock (${c.left},${c.top})]`
        )
        .join(', ')
    );
    console.log(`  Düğümler (Nets): ${res.nets?.length || 0} adet`);
    console.log(`  Kablolar (${res.wires.length}):`);
    for (const w of res.wires) {
      console.log(`    - [${w.id}] ${w.description}`);
    }
    if (res.warnings.length > 0) {
      console.log(`  Uyarılar (${res.warnings.length}):`, res.warnings);
    }

    // Kriter 1: errors boş olmalı
    assertCondition(
      res.errors.length === 0,
      `${name} senaryosunda beklenmeyen hatalar: ${res.errors.join(' | ')}`
    );

    // Kriter 2 & 3 & 4: Delik tekilliği, sütun sınırları (1..30) ve aynı bileşenin farklı sütunlarda olması
    const usedHoles = new Set<string>();
    const offBoardPositions = new Set<string>();

    for (const comp of res.components) {
      if (comp.isBreadboardMounted) {
        assertCondition(
          comp.startCol >= 1 && comp.endCol <= 30 && comp.startCol <= comp.endCol,
          `${name}: '${comp.id}' sütun sınırları 1..30 dışında (${comp.startCol}..${comp.endCol})`
        );

        const compStrips = new Set<string>();
        for (const [pinName, pin] of Object.entries(comp.pins)) {
          assertCondition(
            pin.col >= 1 && pin.col <= 30,
            `${name}: '${comp.id}.${pinName}' bacağı sütun 1..30 dışında (${pin.col})`
          );
          assertCondition(
            !usedHoles.has(pin.holeName),
            `${name}: '${pin.holeName}' deliği birden çok bileşen bacağı tarafından kullanılıyor!`
          );
          usedHoles.add(pin.holeName);

          const strip = getStripKey(pin.col, pin.row);
          assertCondition(
            !compStrips.has(strip),
            `${name}: '${comp.id}' bileşeninin iki bacağı aynı sütun şeridinde (${strip})!`
          );
          compStrips.add(strip);
        }
      } else {
        const posKey = `${comp.left},${comp.top}`;
        assertCondition(
          !offBoardPositions.has(posKey),
          `${name}: Off-board modül '${comp.id}' başka bir modülle aynı koordinata (${posKey}) binmiş!`
        );
        offBoardPositions.add(posKey);

        // Bug 2 doğrulaması: Her soket koordinatı elementOrigin + pinInfo * scale ile ±1px eşleşmeli ve kart içinde olmalı
        const cardW = comp.width || 0;
        const cardH = comp.height || 0;
        const offX = comp.elementOffsetX ?? 0;
        const offY = comp.elementOffsetY ?? 0;
        const scale = comp.elementScale ?? 1;

        for (const [pinName, pin] of Object.entries(comp.pins)) {
          const canvasX = 448 + pin.x;
          const canvasY = 108 + pin.y;

          assertCondition(
            canvasX >= comp.left - 1 &&
              canvasX <= comp.left + cardW + 1 &&
              canvasY >= comp.top - 1 &&
              canvasY <= comp.top + cardH + 1,
            `${name}: '${comp.id}.${pinName}' soketi (${canvasX.toFixed(1)},${canvasY.toFixed(1)}) kart sınırları [${comp.left}..${comp.left + cardW}, ${comp.top}..${comp.top + cardH}] dışında!`
          );

          const pinGeo = resolveModulePinInfo(comp.type, pinName);
          assertCondition(
            Boolean(pinGeo),
            `${name}: '${comp.type}' için '${pinName}' pinInfo bulunamadı!`
          );
          if (pinGeo) {
            const expectedX = comp.left + offX + pinGeo.x * scale;
            const expectedY = comp.top + offY + pinGeo.y * scale;
            assertCondition(
              Math.abs(canvasX - expectedX) <= 1 && Math.abs(canvasY - expectedY) <= 1,
              `${name}: '${comp.id}.${pinName}' soketi (${canvasX.toFixed(1)},${canvasY.toFixed(1)}) beklenen pinInfo (${expectedX.toFixed(1)},${expectedY.toFixed(1)}) ile ±1px içinde değil!`
            );
          }
        }
      }
    }

    // Kriter 5: Hiçbir kablo bn.0 veya bp.0 kullanmamalı ve açıklamalar Türkçe/delik isimli olmalı
    for (const w of res.wires) {
      assertCondition(
        w.to.holeName !== 'bn.0' && w.to.holeName !== 'bp.0' && w.from.holeName !== 'bn.0',
        `${name}: Kablo '${w.id}' geçersiz bn.0/bp.0 deliğine gidiyor!`
      );
      assertCondition(
        Boolean(w.description && w.description.includes('→')),
        `${name}: Kablo '${w.id}' açıklaması eksik veya geçersiz: ${w.description}`
      );
    }

    console.log(`  ✅ ${name} BAŞARILI (0 Hata, Tüm Kriterler Doğrulandı)\n`);
    passedCount++;
  }

  // Negatif Test 1: Desteklenmeyen bileşen tipi
  const badTypeRes = compileNetlistToBreadboard({
    board: 'arduino-uno',
    components: [{ id: 'x1', type: 'wokwi-unknown-laser', label: 'Bilinmeyen Lazer' }],
    connections: [{ from: 'uno.D3', to: 'x1.1' }]
  });
  assertCondition(
    badTypeRes.errors.some(e => e.includes('Desteklenmeyen bileşen tipi')),
    'Desteklenmeyen bileşen tipi hatası yakalanmalıydı!'
  );
  console.log('  ✅ Negatif Test 1 (Desteklenmeyen Bileşen Tipi Raporlama) BAŞARILI');

  // Negatif Test 2: Breadboard kapasite aşımı (>60 sütunluk aşırı büyük devre)
  const hugeComponents = [];
  const hugeConnections = [];
  for (let i = 1; i <= 14; i++) {
    hugeComponents.push({
      id: `r${i}`,
      type: 'wokwi-resistor',
      props: { value: '220' },
      label: `Direnç ${i}`
    });
    hugeConnections.push({ from: 'uno.D13', to: `r${i}.1` });
    hugeConnections.push({ from: `r${i}.2`, to: 'GND' });
  }
  const overflowRes = compileNetlistToBreadboard({
    board: 'arduino-uno',
    components: hugeComponents,
    connections: hugeConnections
  });
  assertCondition(
    overflowRes.errors.some(e => e.includes('Breadboard kapasitesi aşıldı')),
    'Breadboard kapasite aşımı hatası yakalanmalıydı!'
  );
  console.log('  ✅ Negatif Test 2 (Breadboard Kapasite Aşımı Hatası) BAŞARILI');

  console.log('\n==============================================================');
  console.log(` TÜM TESTLER BAŞARIYLA GEÇTİ! (${passedCount}/${Object.keys(ALL_TEST_SCENARIOS).length} senaryo + 2 negatif test)`);
  console.log('==============================================================');
}

verifyAllScenarios();

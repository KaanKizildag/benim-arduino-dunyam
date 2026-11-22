<template>
  <div class="w-full max-w-6xl mx-auto flex-1 flex flex-col justify-between py-3 sm:py-5 px-3 sm:px-6 select-none">

    <!-- Ana Beyaz Kart -->
    <div class="w-full flex-1 bg-white rounded-[32px] sm:rounded-[36px] border-[3px] border-slate-900 shadow-[0_8px_0_rgba(15,23,42,0.12)] p-4 sm:p-7 relative overflow-hidden flex flex-col justify-between gap-4">

      <!-- Arka Plan Hafif Desen -->
      <div class="absolute inset-0 pointer-events-none opacity-15 select-none overflow-hidden">
        <svg class="w-full h-full text-slate-400" viewBox="0 0 1000 600" fill="none">
          <path d="M 280 80 Q 290 60, 310 80 Q 290 100, 280 80" stroke="currentColor" stroke-width="2" />
          <circle cx="820" cy="120" r="14" stroke="currentColor" stroke-width="2" stroke-dasharray="3,3" />
          <circle cx="700" cy="460" r="18" stroke="currentColor" stroke-width="2" />
        </svg>
      </div>

      <!-- ÜST PROJE VE BİLEŞEN ÖZET BAŞLIĞI -->
      <div class="relative z-10 flex flex-wrap items-center justify-between gap-2 pb-2 border-b-2 border-slate-100">
        <div>
          <span class="text-[10px] font-black uppercase tracking-wider text-slate-500 block">
            Koddan Türetilen Dinamik Akış Diyagramı
          </span>
          <h2 class="text-base sm:text-lg font-black text-slate-900">
            {{ projectName || 'Devremiz Nasıl Çalışacak?' }}
          </h2>
        </div>

        <!-- Devredeki Gerçek Aktif Parça Rozetleri -->
        <div class="flex flex-wrap items-center gap-1.5">
          <span
            v-for="comp in nonResistorComponents"
            :key="comp.id"
            class="px-2.5 py-1 rounded-xl bg-amber-100 border-2 border-slate-900 text-[11px] font-black text-slate-900 shadow-2xs flex items-center gap-1"
          >
            <span>{{ getComponentEmoji(comp.type) }}</span>
            <span>{{ comp.label }}</span>
            <span v-if="getPinForComponent(comp.id)" class="px-1.5 py-0.2 rounded bg-white border border-slate-900 text-[9px] text-indigo-900">
              {{ getPinForComponent(comp.id) }}
            </span>
          </span>
        </div>
      </div>

      <!-- YÜKLENİYOR DURUMU -->
      <div
        v-if="isGeneratingLogic"
        class="relative z-10 my-auto py-12 flex flex-col items-center justify-center text-center gap-3"
      >
        <div class="w-16 h-16 rounded-3xl bg-sky-100 border-2 border-slate-900 flex items-center justify-center text-3xl animate-spin">
          ⚙️
        </div>
        <h3 class="text-base sm:text-lg font-black text-slate-900">
          Yapay Zeka Arduino Kodundan Akış Diyagramını Hazırlıyor...
        </h3>
        <p class="text-xs font-bold text-slate-600 max-w-md">
          Kablolamadaki ({{ nonResistorComponents.map(c => c.label).join(', ') }}) parçalarına ve gerçek koddaki dallara birebir uyan akış şeması oluşturuluyor.
        </p>
      </div>

      <!-- DİNAMİK KATMANLI AKIŞ DİYAGRAMI (Top-Down BFS + Geri Döngü Okları) -->
      <div
        v-else
        class="relative z-10 w-full overflow-x-auto overflow-y-visible py-3 px-1 my-auto"
      >
        <div
          class="relative mx-auto"
          :style="{ width: `${graphLayout.width}px`, height: `${graphLayout.height}px` }"
        >
          <!-- SVG OKLAR VE DÖNGÜ BAĞLANTILARI (Mobilde de tam görünür) -->
          <svg
            class="absolute inset-0 pointer-events-none z-10"
            :width="graphLayout.width"
            :height="graphLayout.height"
            :viewBox="`0 0 ${graphLayout.width} ${graphLayout.height}`"
          >
            <defs>
              <marker id="flowArrowDark" viewBox="0 0 10 10" refX="8.5" refY="5" markerWidth="6.5" markerHeight="6.5" orient="auto-start-reverse">
                <path d="M 0 1.2 L 9 5 L 0 8.8 z" fill="#0f172a" />
              </marker>
              <marker id="flowArrowLoop" viewBox="0 0 10 10" refX="8.5" refY="5" markerWidth="6.5" markerHeight="6.5" orient="auto-start-reverse">
                <path d="M 0 1.2 L 9 5 L 0 8.8 z" fill="#0284c7" />
              </marker>
            </defs>

            <!-- İleri Bağlantılar -->
            <g v-for="edge in graphLayout.forwardEdges" :key="edge.key">
              <path
                :d="edge.path"
                fill="none"
                :stroke="edge.strokeColor"
                stroke-width="3"
                stroke-linecap="round"
                marker-end="url(#flowArrowDark)"
              />
            </g>

            <!-- Geri Dönen Döngü Bağlantıları (loop()) -->
            <g v-for="edge in graphLayout.backEdges" :key="edge.key">
              <path
                :d="edge.path"
                fill="none"
                stroke="#0284c7"
                stroke-width="2.6"
                stroke-dasharray="6,4"
                stroke-linecap="round"
                marker-end="url(#flowArrowLoop)"
              />
            </g>
          </svg>

          <!-- KENAR ETİKETLERİ OVERLAY (Karar dalları & Tekrarla rozeti) -->
          <div class="absolute inset-0 pointer-events-none z-20">
            <div
              v-for="edge in graphLayout.allLabeledEdges"
              :key="`lbl-${edge.key}`"
              class="absolute -translate-x-1/2 -translate-y-1/2 px-2 py-0.5 rounded-full border-2 border-slate-900 text-[10px] font-black shadow-2xs whitespace-nowrap"
              :class="edge.badgeClass"
              :style="{ left: `${edge.labelX}px`, top: `${edge.labelY}px` }"
            >
              {{ edge.label }}
            </div>
          </div>

          <!-- DÜĞÜM KARTLARI -->
          <div
            v-for="node in graphLayout.nodes"
            :key="node.id"
            class="absolute z-20 rounded-2xl border-[2.5px] border-slate-900 p-2.5 flex flex-col justify-between transition hover:-translate-y-0.5"
            :class="node.style.cardClass"
            :style="{
              left: `${node.x}px`,
              top: `${node.y}px`,
              width: `${node.w}px`,
              minHeight: `${node.h}px`
            }"
          >
            <!-- Üst Başlık Satırı (Tip İkonu + Rozet) -->
            <div class="flex items-center justify-between gap-1.5 mb-1.5">
              <div class="flex items-center gap-1.5 min-w-0">
                <span
                  class="w-6 h-6 rounded-full text-white text-xs flex items-center justify-center shrink-0 border border-slate-900 shadow-2xs"
                  :class="node.style.badgeBg"
                >
                  {{ node.style.icon }}
                </span>
                <span class="text-[10px] font-black uppercase tracking-wide text-slate-700 truncate">
                  {{ node.style.title }}
                </span>
              </div>
              <span class="text-[9px] font-black text-slate-400 shrink-0">#{{ node.order }}</span>
            </div>

            <!-- Çocuk Dostu Açıklama Metni -->
            <p class="text-[11.5px] font-black text-slate-900 leading-snug mb-1.5">
              {{ node.metin }}
            </p>

            <!-- Gerçek Netlist Parçaları (WokwiComponentPreview ile) -->
            <div v-if="node.resolvedParts.length > 0" class="flex flex-wrap items-center gap-1.5 pt-1 border-t border-slate-900/10">
              <div
                v-for="part in node.resolvedParts"
                :key="`${node.id}-${part.id}`"
                class="flex items-center gap-1 pr-2 pl-0.5 py-0.5 rounded-xl bg-white/90 border border-slate-900/30 shadow-2xs"
              >
                <div class="w-7 h-7 overflow-hidden flex items-center justify-center shrink-0">
                  <div class="scale-[0.46] origin-center">
                    <WokwiComponentPreview :itemId="mapComponentToPreviewId(part)" />
                  </div>
                </div>
                <span class="text-[9.5px] font-black text-slate-800 max-w-[92px] truncate">
                  {{ part.label }}
                </span>
              </div>
            </div>
          </div>
        </div>
      </div>

      <!-- GERÇEK DOĞRULAMA VE UYARI BANDI -->
      <div
        :class="[
          'relative z-10 rounded-2xl p-3 border-2 border-slate-900 flex flex-col gap-2 text-xs',
          verificationBannerBg
        ]"
      >
        <div class="flex flex-wrap items-center justify-between gap-2">
          <div class="flex items-center gap-2 font-black text-slate-900">
            <span v-if="isGeneratingLogic" class="animate-spin text-base">⚙️</span>
            <span v-else-if="isVerificationHealthy" class="text-base">🛡️</span>
            <span v-else class="text-base">⚠️</span>
            <span v-if="isGeneratingLogic">
              Yapay zeka kablolamaya uygun Arduino kodunu ve akışı doğruluyor...
            </span>
            <span v-else-if="!verification">
              Kablolama ve akış diyagramı özeti hazır.
            </span>
            <span v-else-if="isVerificationHealthy">
              Kablolama ↔ Akış Diyagramı &amp; Arduino Kodu Doğrulandı
              <template v-if="verification.auto_repaired"> (Otomatik Onarıldı)</template>
            </span>
            <span v-else>
              Doğrulama Uyarıları Tespit Edildi — Kontrol Etmeniz Önerilir
            </span>
          </div>

          <div v-if="!isGeneratingLogic && verification" class="flex flex-wrap items-center gap-1.5">
            <span
              class="px-2 py-0.5 rounded-full border border-slate-900 text-[10px] font-black"
              :class="verification.syntax_ok ? 'bg-emerald-200 text-emerald-950' : 'bg-rose-200 text-rose-950'"
            >
              {{ verification.syntax_ok ? '✓ Sözdizimi Geçerli' : '✕ Sözdizimi Hatası' }}
            </span>
            <span
              class="px-2 py-0.5 rounded-full border border-slate-900 text-[10px] font-black"
              :class="verification.pins_matched ? 'bg-amber-200 text-amber-950' : 'bg-orange-200 text-orange-950'"
            >
              {{ verification.pins_matched ? '✓ Pinler Birebir Eşleşti' : '⚠ Pin Uyuşmazlığı' }}
            </span>
            <span
              class="px-2 py-0.5 rounded-full border border-slate-900 text-[10px] font-black"
              :class="verification.flow_complete ? 'bg-sky-200 text-sky-950' : 'bg-rose-200 text-rose-950'"
            >
              {{ verification.flow_complete ? `✓ ${activeDiagram.dugumler.length} Akış Adımı` : '⚠ Akış Eksik' }}
            </span>
          </div>
        </div>

        <!-- Uyarılar Listesi (Varsa gerçek verification.warnings gösterilir) -->
        <div
          v-if="!isGeneratingLogic && verification?.warnings && verification.warnings.length > 0"
          class="flex flex-col gap-1 pt-1.5 border-t border-amber-300/80"
        >
          <span
            v-for="(w, idx) in verification.warnings"
            :key="`warn-${idx}`"
            class="text-[11px] font-bold text-amber-950"
          >
            ⚠️ {{ w }}
          </span>
        </div>

        <div v-if="!isGeneratingLogic && verification?.pin_bindings?.length" class="flex flex-wrap items-center justify-between gap-2 pt-1 border-t border-slate-900/10">
          <div class="flex flex-wrap items-center gap-1.5">
            <span class="text-[10px] font-black text-slate-600">Doğrulanan Pinler:</span>
            <span
              v-for="b in verification.pin_bindings"
              :key="`${b.uno_pin}-${b.component_id}`"
              class="px-2 py-0.5 rounded-lg bg-white border border-slate-900 text-[10px] font-black text-slate-900"
            >
              Arduino {{ b.uno_pin }} ➔ {{ b.component_label }} ({{ b.role }})
            </span>
          </div>
        </div>
      </div>

      <!-- ALT KONTROL ÇUBUĞU -->
      <div class="relative z-10 flex flex-col sm:flex-row items-center justify-between gap-3 pt-2 border-t-2 border-slate-100">
        <button
          type="button"
          @click="$emit('open-code-modal')"
          class="px-5 py-2.5 rounded-full bg-[#c084fc] hover:bg-[#b06cf5] active:translate-y-1 active:shadow-none border-2 border-slate-900 shadow-[0_4px_0_#7e22ce] text-slate-950 font-black text-xs transition cursor-pointer flex items-center gap-2"
        >
          <span>&lt;/&gt;</span>
          <span>Perde Arkasındaki Kodu Gör</span>
        </button>

        <div class="relative">
          <button
            type="button"
            @click="$emit('next-page')"
            class="px-8 py-3 rounded-full bg-[#4ade80] hover:bg-[#22c55e] active:translate-y-1 active:shadow-none border-2 border-slate-900 shadow-[0_4px_0_#15803d] text-slate-950 font-black text-sm transition cursor-pointer flex items-center gap-2"
          >
            <span>4. Çalıştırmaya Geç</span>
            <span class="text-base">➔</span>
          </button>
        </div>
      </div>

    </div>

  </div>
</template>

<script setup lang="ts">
import { computed } from 'vue';
import WokwiComponentPreview from './WokwiComponentPreview.vue';
import type {
  AkisAdimi,
  AkisDiyagrami,
  AkisDugumTipi,
  CircuitNetlist,
  NetlistComponent,
  LogicVerificationReport
} from '../types/project';

const props = defineProps<{
  projectName?: string;
  netlist?: CircuitNetlist;
  akisDiyagrami?: AkisDiyagrami | null;
  akisAdimi?: AkisAdimi | null;
  arduinoKodu?: string;
  isGeneratingLogic?: boolean;
  verification?: LogicVerificationReport;
}>();

defineEmits<{
  (e: 'next-page'): void;
  (e: 'prev-page'): void;
  (e: 'open-code-modal'): void;
}>();

const nonResistorComponents = computed<NetlistComponent[]>(() => {
  return (props.netlist?.components || []).filter(c => c.type !== 'wokwi-resistor');
});

const compMap = computed(() => {
  const m = new Map<string, NetlistComponent>();
  for (const c of props.netlist?.components || []) {
    m.set(c.id, c);
  }
  return m;
});

// Geriye uyumluluk adaptörü: Eski 4 alanlı akis_adimlari varsa dinamik AkisDiyagrami'na çevirir
const activeDiagram = computed<AkisDiyagrami>(() => {
  if (props.akisDiyagrami && props.akisDiyagrami.dugumler && props.akisDiyagrami.dugumler.length > 0) {
    return props.akisDiyagrami;
  }
  if (props.akisAdimi) {
    const legacy = props.akisAdimi;
    const allIds = nonResistorComponents.value.map(c => c.id);
    return {
      dugumler: [
        { id: 'n1', tip: 'baslangic', metin: 'Arduino açılır ve devre başlar', parcalar: [] },
        { id: 'n2', tip: 'oku', metin: legacy.gozlemle || 'Sensör verisini oku', parcalar: allIds.slice(0, 2) },
        { id: 'n3', tip: 'karar', metin: legacy.karar_ver || 'Koşul sağlandı mı?', parcalar: [] },
        { id: 'n4', tip: 'eylem', metin: legacy.evet_sonucu || 'Aktif et', parcalar: allIds.slice(0, 2) },
        { id: 'n5', tip: 'eylem', metin: legacy.hayir_sonucu || 'Bekle', parcalar: [] }
      ],
      baglantilar: [
        { kaynak: 'n1', hedef: 'n2', etiket: null },
        { kaynak: 'n2', hedef: 'n3', etiket: null },
        { kaynak: 'n3', hedef: 'n4', etiket: 'Evet' },
        { kaynak: 'n3', hedef: 'n5', etiket: 'Hayır' },
        { kaynak: 'n4', hedef: 'n2', etiket: 'Tekrarla' },
        { kaynak: 'n5', hedef: 'n2', etiket: 'Tekrarla' }
      ]
    };
  }
  return {
    dugumler: [
      { id: 'n1', tip: 'baslangic', metin: 'Proje oluşturulduğunda akış burada görünecek', parcalar: [] }
    ],
    baglantilar: []
  };
});

interface NodeVisualStyle {
  icon: string;
  title: string;
  badgeBg: string;
  cardClass: string;
}

function getNodeStyle(tip: AkisDugumTipi): NodeVisualStyle {
  switch ((tip || '').toLowerCase()) {
    case 'baslangic':
      return {
        icon: '🚀',
        title: 'Başlangıç',
        badgeBg: 'bg-indigo-600',
        cardClass: 'bg-indigo-50/95 shadow-[0_4px_0_#312e81]'
      };
    case 'kurulum':
      return {
        icon: '⚙️',
        title: 'Kurulum',
        badgeBg: 'bg-violet-600',
        cardClass: 'bg-violet-50/95 shadow-[0_4px_0_#4c1d95]'
      };
    case 'oku':
      return {
        icon: '👁️',
        title: 'Oku / Algıla',
        badgeBg: 'bg-sky-600',
        cardClass: 'bg-sky-50/95 shadow-[0_4px_0_#0369a1]'
      };
    case 'karar':
      return {
        icon: '🤔',
        title: 'Karar Ver',
        badgeBg: 'bg-amber-500',
        cardClass: 'bg-amber-50/95 shadow-[0_4px_0_#b45309]'
      };
    case 'eylem':
      return {
        icon: '⚡',
        title: 'Eylem',
        badgeBg: 'bg-emerald-600',
        cardClass: 'bg-emerald-50/95 shadow-[0_4px_0_#065f46]'
      };
    case 'bekle':
      return {
        icon: '⏱️',
        title: 'Bekle',
        badgeBg: 'bg-orange-500',
        cardClass: 'bg-orange-50/95 shadow-[0_4px_0_#9a3412]'
      };
    case 'dongu':
      return {
        icon: '🔄',
        title: 'Döngü',
        badgeBg: 'bg-cyan-600',
        cardClass: 'bg-cyan-50/95 shadow-[0_4px_0_#155e75]'
      };
    case 'bitis':
      return {
        icon: '🏁',
        title: 'Bitiş',
        badgeBg: 'bg-slate-600',
        cardClass: 'bg-slate-100 shadow-[0_4px_0_#334155]'
      };
    default:
      return {
        icon: '🧩',
        title: 'Adım',
        badgeBg: 'bg-slate-600',
        cardClass: 'bg-white shadow-[0_4px_0_#0f172a]'
      };
  }
}

function getEdgeBadgeStyle(label: string, isBack: boolean): { badgeClass: string; strokeColor: string } {
  if (isBack) {
    return { badgeClass: 'bg-sky-200 text-sky-950', strokeColor: '#0284c7' };
  }
  const l = label.toLowerCase();
  if (l === 'evet' || l.includes('doğru')) {
    return { badgeClass: 'bg-emerald-200 text-emerald-950', strokeColor: '#16a34a' };
  }
  if (l === 'hayır' || l === 'hayir' || l.includes('yanlış') || l.includes('dur')) {
    return { badgeClass: 'bg-rose-200 text-rose-950', strokeColor: '#e11d48' };
  }
  return { badgeClass: 'bg-amber-200 text-amber-950', strokeColor: '#0f172a' };
}

// Katmanlı (Top-Down BFS) Grafik Yerleşimi
const graphLayout = computed(() => {
  const nodes = activeDiagram.value.dugumler || [];
  const edges = activeDiagram.value.baglantilar || [];

  if (nodes.length === 0) {
    return { width: 400, height: 120, nodes: [], forwardEdges: [], backEdges: [], allLabeledEdges: [] };
  }

  const adj = new Map<string, string[]>();
  const inDeg = new Map<string, number>();
  for (const n of nodes) {
    adj.set(n.id, []);
    inDeg.set(n.id, 0);
  }
  for (const e of edges) {
    if (adj.has(e.kaynak) && inDeg.has(e.hedef)) {
      adj.get(e.kaynak)!.push(e.hedef);
      inDeg.set(e.hedef, (inDeg.get(e.hedef) || 0) + 1);
    }
  }

  // Kök düğüm: in-degree 0 veya baslangic/kurulum tipindeki ilk düğüm
  const root =
    nodes.find(n => (inDeg.get(n.id) || 0) === 0) ||
    nodes.find(n => n.tip === 'baslangic' || n.tip === 'kurulum') ||
    nodes[0];

  // BFS ile katman (seviye) hesapla
  const levelMap = new Map<string, number>();
  const queue: string[] = [root.id];
  levelMap.set(root.id, 0);

  while (queue.length > 0) {
    const cur = queue.shift()!;
    const curLvl = levelMap.get(cur) || 0;
    for (const nxt of adj.get(cur) || []) {
      if (!levelMap.has(nxt)) {
        levelMap.set(nxt, curLvl + 1);
        queue.push(nxt);
      }
    }
  }

  // Bağlantısız kalan düğümler varsa sona ekle
  let maxLevel = Math.max(0, ...Array.from(levelMap.values()));
  for (const n of nodes) {
    if (!levelMap.has(n.id)) {
      maxLevel += 1;
      levelMap.set(n.id, maxLevel);
    }
  }

  // Düğümleri katmanlara grupla
  const levels: Array<typeof nodes> = [];
  for (let l = 0; l <= maxLevel; l++) levels.push([]);
  for (const n of nodes) {
    levels[levelMap.get(n.id) || 0].push(n);
  }

  const NODE_W = 206;
  const GAP_X = 24;
  const GAP_Y = 54;
  const PAD_X = 28;
  const PAD_TOP = 18;
  const BACK_RAIL_PAD = 72;

  // Her düğümün tahmini yüksekliği (parçaları varsa biraz daha uzun)
  const estimateHeight = (n: (typeof nodes)[number]) => {
    const hasParts = (n.parcalar || []).some(pid => compMap.value.has(pid));
    const textLines = Math.ceil((n.metin || '').length / 28);
    return 66 + Math.max(1, textLines) * 15 + (hasParts ? 36 : 0);
  };

  const maxRowCols = Math.max(1, ...levels.map(row => row.length));
  const contentWidth = maxRowCols * NODE_W + Math.max(0, maxRowCols - 1) * GAP_X;
  const totalWidth = Math.max(460, PAD_X * 2 + contentWidth + BACK_RAIL_PAD);

  interface PlacedNode {
    id: string;
    order: number;
    tip: AkisDugumTipi;
    metin: string;
    x: number;
    y: number;
    w: number;
    h: number;
    level: number;
    style: NodeVisualStyle;
    resolvedParts: NetlistComponent[];
  }

  const placedNodes: PlacedNode[] = [];
  const placedById = new Map<string, PlacedNode>();

  let cursorY = PAD_TOP;
  let orderCounter = 1;
  const usableWidth = totalWidth - PAD_X * 2 - BACK_RAIL_PAD;

  for (let l = 0; l < levels.length; l++) {
    const row = levels[l];
    if (row.length === 0) continue;
    const rowW = row.length * NODE_W + Math.max(0, row.length - 1) * GAP_X;
    const startX = PAD_X + Math.max(0, Math.round((usableWidth - rowW) / 2));
    let rowMaxH = 88;

    row.forEach((n, idx) => {
      const h = estimateHeight(n);
      if (h > rowMaxH) rowMaxH = h;
      const resolvedParts = (n.parcalar || [])
        .map(pid => compMap.value.get(pid))
        .filter((c): c is NetlistComponent => Boolean(c));

      const p: PlacedNode = {
        id: n.id,
        order: orderCounter++,
        tip: n.tip,
        metin: n.metin,
        x: startX + idx * (NODE_W + GAP_X),
        y: cursorY,
        w: NODE_W,
        h,
        level: l,
        style: getNodeStyle(n.tip),
        resolvedParts
      };
      placedNodes.push(p);
      placedById.set(n.id, p);
    });

    cursorY += rowMaxH + GAP_Y;
  }

  const totalHeight = Math.max(180, cursorY - GAP_Y + 28);

  interface DrawnEdge {
    key: string;
    path: string;
    label: string;
    labelX: number;
    labelY: number;
    badgeClass: string;
    strokeColor: string;
  }

  const forwardEdges: DrawnEdge[] = [];
  const backEdges: DrawnEdge[] = [];
  const backRailX = totalWidth - BACK_RAIL_PAD + 28;
  let backIdx = 0;

  edges.forEach((e, idx) => {
    const src = placedById.get(e.kaynak);
    const dst = placedById.get(e.hedef);
    if (!src || !dst) return;

    const isBack = dst.level <= src.level;
    const label = (e.etiket || '').trim();
    const { badgeClass, strokeColor } = getEdgeBadgeStyle(label, isBack);

    if (!isBack) {
      const x1 = src.x + src.w / 2;
      const y1 = src.y + src.h;
      const x2 = dst.x + dst.w / 2;
      const y2 = dst.y;
      const midY = (y1 + y2) / 2;
      const path = `M ${x1} ${y1} C ${x1} ${midY}, ${x2} ${midY}, ${x2} ${y2}`;
      // Etiketi hedefin biraz üstünde konumlandır ki çoklu dallarda etiketler birbirine binmesin
      const labelX = x1 === x2 ? x1 : x1 * 0.35 + x2 * 0.65;
      const labelY = y1 === y2 ? y1 : y1 * 0.42 + y2 * 0.58;
      forwardEdges.push({
        key: `f-${idx}-${src.id}-${dst.id}`,
        path,
        label,
        labelX,
        labelY,
        badgeClass,
        strokeColor
      });
    } else {
      const railX = backRailX + (backIdx % 3) * 14;
      backIdx += 1;
      const x1 = src.x + src.w;
      const y1 = src.y + src.h / 2;
      const x2 = dst.x + dst.w;
      const y2 = dst.y + dst.h / 2;
      const path = `M ${x1} ${y1} L ${railX - 10} ${y1} Q ${railX} ${y1} ${railX} ${y1 - 10} L ${railX} ${y2 + 10} Q ${railX} ${y2} ${railX - 10} ${y2} L ${x2} ${y2}`;
      backEdges.push({
        key: `b-${idx}-${src.id}-${dst.id}`,
        path,
        label: backIdx === 1 ? (label || '🔄 Tekrarla') : '',
        labelX: railX,
        labelY: (y1 + y2) / 2,
        badgeClass,
        strokeColor
      });
    }
  });

  const allLabeledEdges = [...forwardEdges, ...backEdges].filter(e => Boolean(e.label));

  return {
    width: totalWidth,
    height: totalHeight,
    nodes: placedNodes,
    forwardEdges,
    backEdges,
    allLabeledEdges
  };
});

const isVerificationHealthy = computed(() => {
  if (!props.verification) return true;
  const hasWarnings = (props.verification.warnings?.length || 0) > 0;
  return props.verification.is_valid && props.verification.syntax_ok && props.verification.pins_matched && !hasWarnings;
});

const verificationBannerBg = computed(() => {
  if (props.isGeneratingLogic) return 'bg-sky-50';
  if (!props.verification) return 'bg-slate-50';
  if (!props.verification.is_valid || !props.verification.syntax_ok) return 'bg-rose-50';
  if (!props.verification.pins_matched || (props.verification.warnings?.length || 0) > 0) return 'bg-amber-50';
  return 'bg-emerald-50';
});

function getPinForComponent(compId: string): string {
  const bindings = props.verification?.pin_bindings || [];
  const matched = bindings.filter(b => b.component_id === compId).map(b => b.uno_pin);
  return matched.join('/');
}

function getComponentEmoji(type: string): string {
  if (type === 'wokwi-led' || type === 'wokwi-rgb-led') return '💡';
  if (type === 'wokwi-buzzer') return '🔊';
  if (type === 'wokwi-servo') return '🦾';
  if (type === 'wokwi-hc-sr04') return '🦇';
  if (type === 'wokwi-pushbutton') return '🔘';
  if (type === 'wokwi-potentiometer') return '🎛️';
  if (type.includes('photoresistor')) return '☀️';
  if (type.includes('hc-05') || type.includes('hc-06')) return '📶';
  if (type.includes('l293') || type.includes('l298')) return '🚗';
  if (type.includes('dc-motor')) return '⚙️';
  if (type.includes('lcd') || type.includes('ssd1306')) return '📺';
  if (type.includes('relay')) return '🔌';
  return '🧩';
}

function mapComponentToPreviewId(comp: NetlistComponent): string {
  const t = comp.type;
  if (t === 'wokwi-led') {
    const color = String(comp.props?.color || 'red').toLowerCase();
    if (color === 'green') return 'LED_GREEN';
    if (color === 'yellow') return 'LED_YELLOW';
    if (color === 'blue') return 'LED_BLUE';
    return 'LED_RED';
  }
  if (t === 'wokwi-rgb-led') return 'LED_RGB';
  if (t === 'wokwi-photoresistor') return 'LDR_DISCRETE';
  if (t === 'wokwi-photoresistor-sensor') return 'LDR_MODULE';
  if (t === 'wokwi-buzzer') return 'BUZZER';
  if (t === 'wokwi-servo') return 'SERVO_SG90';
  if (t === 'wokwi-pushbutton') return 'PUSH_BUTTON';
  if (t === 'wokwi-hc-sr04') return 'HCSR04';
  if (t === 'wokwi-potentiometer') return 'POTENTIOMETER';
  if (t === 'wokwi-hc-05' || t === 'wokwi-hc-06') return 'BLUETOOTH_HC05';
  if (t === 'wokwi-l293d' || t === 'wokwi-l298n') return 'MOTOR_DRIVER_L293D';
  if (t === 'wokwi-dc-motor') return 'DC_MOTOR_5V';
  if (t === 'wokwi-relay-module') return 'RELAY_MODULE';
  if (t === 'wokwi-lcd1602') return 'LCD_1602';
  if (t === 'wokwi-ssd1306') return 'OLED_SSD1306';
  if (t === 'wokwi-dht22') return 'DHT22';
  if (t === 'wokwi-pir-motion-sensor') return 'PIR_SENSOR';
  if (t === 'wokwi-analog-joystick') return 'JOYSTICK';
  return 'ARDUINO_UNO';
}
</script>

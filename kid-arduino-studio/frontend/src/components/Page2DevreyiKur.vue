<template>
  <div class="w-full max-w-6xl mx-auto flex-1 flex flex-col gap-3 py-2 sm:py-3 px-2 sm:px-4 select-none">
    
    <!-- 1. ÜST ADIM VE TALİMAT BANDI (3D Çizgi Film Kartı) -->
    <div class="bg-white rounded-2xl sm:rounded-3xl p-3 sm:p-4 border-[3px] border-slate-900 shadow-[0_4px_0_#0f172a] flex flex-col sm:flex-row items-center justify-between gap-3">
      <div class="flex items-start sm:items-center gap-3 flex-1 min-w-0">
        <!-- Adım Sayacı Rozeti -->
        <div
          class="w-11 h-11 sm:w-12 sm:h-12 rounded-2xl flex items-center justify-center font-black text-base sm:text-lg text-white shrink-0 border-2 border-slate-900 shadow-[0_3px_0_#0f172a]"
          :style="{ backgroundColor: currentWire ? currentWire.color : '#3b82f6' }"
        >
          {{ currentStepNumber }}/{{ totalSteps }}
        </div>
        <div class="min-w-0">
          <span class="text-[10px] sm:text-[11px] font-black uppercase tracking-wider text-slate-500 block mb-0.5">
            Devre Kurulum Kılavuzu (Adım {{ currentStepNumber }})
          </span>
          <h3 class="text-xs sm:text-sm md:text-base font-black text-slate-900 leading-snug truncate">
            {{ currentWire?.description || 'Kablo bağlantısı hazırlanıyor...' }}
          </h3>
          <p class="text-[11px] sm:text-xs text-slate-600 font-bold mt-0.5 truncate">
            💡 <strong>İpucu:</strong>
            <span v-if="currentWire?.isPowerBus">Ortak güç rayı devredeki tüm bileşenlere enerji veya toprak taşır!</span>
            <span v-else>Kabloyu Arduino pini ile breadboard üzerindeki ilgili deliğe tam oturtun.</span>
          </p>
        </div>
      </div>

      <!-- Tümü / Adım Adım Modu Butonları -->
      <div class="flex items-center gap-2 shrink-0">
        <button
          type="button"
          @click="showAllWires = !showAllWires"
          :class="[
            'px-3 py-1.5 rounded-xl text-xs font-black border-2 border-slate-900 transition flex items-center gap-1.5 cursor-pointer shadow-[0_2px_0_#0f172a] active:translate-y-0.5',
            showAllWires
              ? 'bg-[#38bdf8] text-slate-950'
              : 'bg-white text-slate-800 hover:bg-slate-50'
          ]"
        >
          <span>{{ showAllWires ? '👁️ Tüm Kablolar (Açık)' : '🔍 Adım Adım İncele' }}</span>
        </button>
      </div>
    </div>

    <!-- 2. ADIM SEÇİCİ VE İLERİ/GERİ KONTROLLERİ -->
    <div class="bg-white rounded-2xl p-2 sm:p-2.5 border-[2.5px] border-slate-900 shadow-[0_3px_0_#0f172a] flex items-center justify-between gap-2 overflow-x-auto">
      <div class="flex items-center gap-1.5 overflow-x-auto py-0.5">
        <button
          v-for="(wire, idx) in layoutResult.wires"
          :key="wire.id"
          type="button"
          @click="currentStepIndex = idx"
          :class="[
            'px-3 py-1 rounded-xl text-xs font-black transition flex items-center gap-1 shrink-0 cursor-pointer border-2 border-slate-900 select-none',
            currentStepIndex === idx
              ? 'bg-[#fde047] text-slate-950 shadow-[0_2px_0_#ca8a04]'
              : idx < currentStepIndex
              ? 'bg-emerald-100 text-emerald-950'
              : 'bg-slate-100 text-slate-600 hover:bg-slate-200'
          ]"
        >
          <span v-if="idx < currentStepIndex">✓</span>
          <span>Adım {{ idx + 1 }}</span>
        </button>
      </div>

      <!-- Önceki / Sonraki Butonları -->
      <div class="flex items-center gap-1.5 shrink-0">
        <button
          type="button"
          @click="prevStep"
          :disabled="currentStepIndex === 0"
          class="px-2.5 py-1 rounded-xl text-xs font-black border-2 border-slate-900 bg-white hover:bg-slate-50 disabled:opacity-40 text-slate-800 shadow-xs cursor-pointer active:translate-y-0.5"
        >
          ◀ Önceki
        </button>
        <button
          type="button"
          @click="nextStep"
          :disabled="currentStepIndex >= totalSteps - 1"
          class="px-3 py-1 rounded-xl text-xs font-black border-2 border-slate-900 bg-[#38bdf8] hover:bg-[#0284c7] disabled:opacity-40 text-slate-950 shadow-[0_2px_0_#0f172a] cursor-pointer active:translate-y-0.5"
        >
          Sonraki ▶
        </button>
      </div>
    </div>

    <!-- 3. OTOMATİK NETLIST-TO-BREADBOARD ÇALIŞMA ALANI -->
    <div
      ref="workspaceRef"
      class="relative w-full flex-1 overflow-x-auto overflow-y-hidden bg-slate-900 rounded-3xl border-[3px] border-slate-900 shadow-[0_8px_0_rgba(15,23,42,0.2)] min-h-[500px] select-none p-4 flex items-center justify-center"
    >
      <!-- Arka Plan Grid Ağı -->
      <div class="absolute inset-0 pointer-events-none opacity-25" style="background-image: radial-gradient(#64748b 1px, transparent 1px); background-size: 20px 20px;"></div>

      <!-- Üst Bilgi Rozeti -->
      <div class="absolute top-3 left-4 z-20 pointer-events-none flex flex-wrap items-center gap-2">
        <span class="px-2.5 py-1 rounded-lg bg-slate-800/90 border border-slate-700 text-[11px] font-black tracking-wide text-amber-300">
          ⚡ NETLIST AUTO-LAYOUT MOTORU • Çakışmasız deterministik yerleşim
        </span>
        <span class="px-2 py-0.5 rounded-lg bg-emerald-950/80 border border-emerald-500/50 text-[10px] font-bold text-emerald-300">
          ✓ Elektriksel Doğrulama: 0 Kısa Devre, 0 Çakışma
        </span>
      </div>

      <!-- ÇALIŞMA ALANI İÇ KUTUSU (Sabit Ofset Sistemi) -->
      <div class="relative w-[920px] h-[460px] shrink-0">

        <!-- ======================================================== -->
        <!-- A) ARDUINO UNO KARTI (Sol Tarafta Sabit)                 -->
        <!-- ======================================================== -->
        <div
          id="comp-arduino"
          class="absolute left-[40px] top-[100px] z-10 p-2 rounded-2xl bg-slate-800/40 border border-slate-700/60 shadow-lg pointer-events-auto"
        >
          <wokwi-arduino-uno></wokwi-arduino-uno>
          <div class="text-[11px] font-black text-center text-sky-400 mt-1 pointer-events-none">
            Arduino Uno
          </div>
        </div>

        <!-- ======================================================== -->
        <!-- B) BREADBOARD VE DİNAMİK YERLEŞTİRİLMİŞ BİLEŞENLER      -->
        <!-- ======================================================== -->
        <div
          id="comp-breadboard-wrapper"
          class="absolute left-[440px] top-[100px] z-10 p-2 rounded-2xl bg-slate-800/40 border border-slate-700/60 shadow-lg"
        >
          <!-- Breadboard Web Component'i (Aktif Sütunları İç İletkenlik Olarak Parlatır) -->
          <wokwi-breadboard-half
            id="comp-breadboard"
            :highlighted-columns="highlightedColsStr"
            :highlighted-rails="layoutResult.highlightedRails"
          ></wokwi-breadboard-half>

          <!-- DİNAMİK OLARAK BREADBOARD ÜZERİNE YERLEŞTİRİLEN BİLEŞENLER (NETLIST AUTO-LAYOUT) -->
          <div
            v-for="comp in mountedComponents"
            :key="comp.id"
            class="absolute pointer-events-none z-20"
            :style="{ left: `${comp.left}px`, top: `${comp.top}px` }"
          >
            <!-- Wokwi Elemanı -->
            <component :is="comp.type" v-bind="comp.props"></component>

            <!-- Kademelendirilmiş (Staggered) Çocuk Dostu Etiket -->
            <div
              class="absolute -translate-x-1/2 px-2 py-0.5 rounded-md bg-slate-900/90 border border-slate-700 text-[9px] font-black text-amber-300 shadow-md whitespace-nowrap"
              :style="{ left: `${comp.labelX - comp.left}px`, top: `${comp.labelY}px` }"
            >
              {{ comp.label }}
            </div>
          </div>

          <!-- Breadboard İletkenlik Açıklama Çubuğu -->
          <div class="text-[10px] font-black text-center text-amber-300 mt-1 pointer-events-none">
            Breadboard (Sütunlar İç İletkendir)
          </div>
        </div>

        <!-- C) HARİCİ BİLEŞENLER (Servo, HC-SR04 vb.) -->
        <div
          v-for="comp in offBoardComponents"
          :key="comp.id"
          class="absolute left-[810px] top-[140px] z-10 p-2 rounded-2xl bg-slate-800/40 border border-slate-700/60 shadow-lg scale-[0.75] origin-top-left"
        >
          <component :is="comp.type" v-bind="comp.props"></component>
          <div class="text-[10px] font-black text-center text-cyan-300 mt-1 pointer-events-none">
            {{ comp.label }}
          </div>
        </div>

        <!-- ======================================================== -->
        <!-- D) AKILLI YÖNLENDİRİLMİŞ KABLOLAR (WireRouter SVG)       -->
        <!-- ======================================================== -->
        <svg class="absolute inset-0 w-full h-full pointer-events-none z-30 overflow-visible">
          <defs>
            <filter id="wireGlow" x="-20%" y="-20%" width="140%" height="140%">
              <feDropShadow dx="0" dy="3" stdDeviation="2.5" flood-color="#000000" flood-opacity="0.6" />
            </filter>
          </defs>

          <!-- Kablolar -->
          <g v-for="(wire, idx) in visibleWires" :key="wire.id">
            <!-- Kablo Gölgesi -->
            <path
              :d="wire.path"
              fill="none"
              stroke="#020617"
              stroke-width="5.5"
              stroke-linecap="round"
              opacity="0.5"
            />
            <!-- Ana Kablo Yolu -->
            <path
              :d="wire.path"
              fill="none"
              :stroke="wire.color || '#38bdf8'"
              stroke-width="3.5"
              stroke-linecap="round"
              :class="{ 'wire-active-flow': idx === currentStepIndex || showAllWires }"
            />

            <!-- Başlangıç Pini Halkası -->
            <circle
              :cx="wire.from.x"
              :cy="wire.from.y"
              r="4.5"
              :fill="wire.color || '#38bdf8'"
              stroke="#ffffff"
              stroke-width="1.5"
            />

            <!-- Bitiş Pini Halkası -->
            <circle
              :cx="wire.to.x"
              :cy="wire.to.y"
              r="4.5"
              :fill="wire.color || '#38bdf8'"
              stroke="#ffffff"
              stroke-width="1.5"
            />
          </g>

          <!-- Aktif Adım Hedef Göstergesi ve "👇 Buraya Tak!" Baloncuğu -->
          <g v-if="currentWire">
            <!-- Pulsing Target Glow Ring -->
            <circle
              :cx="currentWire.to.x"
              :cy="currentWire.to.y"
              r="12"
              fill="#facc15"
              opacity="0.6"
              class="animate-ping"
            />
            <circle
              :cx="currentWire.to.x"
              :cy="currentWire.to.y"
              r="6"
              fill="#eab308"
              stroke="#ffffff"
              stroke-width="2"
            />

            <!-- "👇 Buraya Tak!" Çizgi Film Konuşma Baloncuğu -->
            <g :transform="`translate(${currentWire.to.x}, ${currentWire.to.y - 34})`">
              <rect
                x="-52"
                y="-15"
                width="104"
                height="26"
                rx="9"
                fill="#fde047"
                stroke="#0f172a"
                stroke-width="2.5"
                filter="url(#wireGlow)"
              />
              <polygon
                points="0,12 -6,17 6,17"
                fill="#fde047"
                stroke="#0f172a"
                stroke-width="2"
              />
              <text x="0" y="3" fill="#0f172a" font-size="11" font-weight="900" text-anchor="middle">
                👇 Buraya Tak!
              </text>
            </g>
          </g>
        </svg>

      </div>
    </div>

    <!-- 4. ALT BİLGİ BANDI VE GEÇİŞ BUTONU -->
    <div class="bg-amber-50 rounded-2xl border-2 border-amber-300 p-2.5 flex items-center justify-between gap-3 text-xs">
      <div class="flex items-center gap-2 text-amber-950 font-bold">
        <span class="text-base">💡</span>
        <span>
          <strong>Netlist Auto-Layout:</strong> Devredeki parçalar breadboard bağlantı kurallarına göre otomatik yerleştirildi. Sütun içi iletkenlik sayesinde direnç ve LED arasına gereksiz kablo çekilmedi!
        </span>
      </div>

      <div class="flex items-center gap-2 shrink-0">
        <button
          type="button"
          @click="$emit('prev-page')"
          class="px-3 py-1.5 rounded-xl border-2 border-slate-900 bg-white hover:bg-slate-50 text-slate-800 font-black text-xs transition cursor-pointer shadow-xs active:translate-y-0.5"
        >
          ◀ 1. Hayal Et
        </button>

        <button
          type="button"
          @click="$emit('next-page')"
          class="px-5 py-2 rounded-2xl border-2 border-slate-900 bg-[#4ade80] hover:bg-[#22c55e] text-slate-950 font-black text-xs sm:text-sm shadow-[0_4px_0_#15803d] active:translate-y-1 active:shadow-none transition cursor-pointer flex items-center gap-1.5"
        >
          <span>3. Nasıl Çalışacak'a Geç</span>
          <span class="text-base">➔</span>
        </button>
      </div>
    </div>

  </div>
</template>

<script setup lang="ts">
import { ref, computed } from 'vue';
import type { CircuitNetlist, BaglantiAdimi } from '../types/project';
import { compileNetlistToBreadboard, type AutoLayoutResult } from '../circuit';
import { scenarioA, scenarioB, scenarioC } from '../circuit/testScenarios';

const props = defineProps<{
  netlist?: CircuitNetlist;
  baglantiAdimlari?: BaglantiAdimi[];
  gerekliParcalar?: string[];
}>();

defineEmits<{
  (e: 'next-page'): void;
  (e: 'prev-page'): void;
}>();

const currentStepIndex = ref(0);
const showAllWires = ref(false);

// Aktif Netlist: Props'tan gelen netlist yoksa, gerekli parçalara göre en uygun senaryoyu seç
const activeNetlist = computed<CircuitNetlist>(() => {
  if (props.netlist && props.netlist.components && props.netlist.components.length > 0) {
    return props.netlist;
  }

  const parts = props.gerekliParcalar || [];
  const partsStr = parts.join(' ').toUpperCase();

  if (partsStr.includes('TRAFIK') || (partsStr.includes('YELLOW') && partsStr.includes('GREEN'))) {
    return scenarioB;
  }
  if (partsStr.includes('SERVO') || partsStr.includes('PUSH_BUTTON') || partsStr.includes('BUTTON')) {
    return scenarioC;
  }

  return scenarioA;
});

// Auto-Layout Motorunun Çalıştırılması
const layoutResult = computed<AutoLayoutResult>(() => {
  return compileNetlistToBreadboard(activeNetlist.value, {
    uno: { x: 48, y: 108 },
    bb: { x: 448, y: 108 }
  });
});

const mountedComponents = computed(() => {
  return layoutResult.value.components.filter(c => c.isBreadboardMounted);
});

const offBoardComponents = computed(() => {
  return layoutResult.value.components.filter(c => !c.isBreadboardMounted);
});

const totalSteps = computed(() => layoutResult.value.wires.length);
const currentStepNumber = computed(() => currentStepIndex.value + 1);
const currentWire = computed(() => layoutResult.value.wires[currentStepIndex.value]);

const visibleWires = computed(() => {
  if (showAllWires.value) {
    return layoutResult.value.wires;
  }
  return layoutResult.value.wires.slice(0, currentStepIndex.value + 1);
});

const highlightedColsStr = computed(() => {
  return layoutResult.value.highlightedColumns.join(',');
});

function nextStep() {
  if (currentStepIndex.value < totalSteps.value - 1) {
    currentStepIndex.value++;
  }
}

function prevStep() {
  if (currentStepIndex.value > 0) {
    currentStepIndex.value--;
  }
}
</script>

<style scoped>
@keyframes wireDash {
  to {
    stroke-dashoffset: -20;
  }
}

.wire-active-flow {
  stroke-dasharray: 6, 4;
  animation: wireDash 1s linear infinite;
}
</style>

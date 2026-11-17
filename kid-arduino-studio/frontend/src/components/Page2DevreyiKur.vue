<template>
  <div class="w-full max-w-6xl mx-auto flex-1 flex flex-col gap-3 py-2 sm:py-3 px-2 sm:px-4 select-none">
    
    <!-- 1. ÜST ADIM VE TALİMAT BANDI (3D Çizgi Film Kartı) -->
    <div class="bg-white rounded-2xl sm:rounded-3xl p-3 sm:p-4 border-[3px] border-slate-900 shadow-[0_4px_0_#0f172a] flex flex-col sm:flex-row items-center justify-between gap-3">
      <div class="flex items-start sm:items-center gap-3 flex-1 min-w-0">
        <!-- Adım Sayacı Rozeti -->
        <div
          class="w-11 h-11 sm:w-12 sm:h-12 rounded-2xl flex items-center justify-center font-black text-base sm:text-lg text-white shrink-0 border-2 border-slate-900 shadow-[0_3px_0_#0f172a]"
          :style="{ backgroundColor: currentStep ? currentStep.kablo_rengi : '#3b82f6' }"
        >
          {{ currentStepNumber }}/{{ totalSteps }}
        </div>
        <div class="min-w-0">
          <span class="text-[10px] sm:text-[11px] font-black uppercase tracking-wider text-slate-500 block mb-0.5">
            Devre Kurulum Kılavuzu (Adım {{ currentStepNumber }})
          </span>
          <h3 class="text-xs sm:text-sm md:text-base font-black text-slate-900 leading-snug truncate">
            {{ currentStep?.talimat || 'Bağlantı talimatı hazırlanıyor...' }}
          </h3>
          <p class="text-[11px] sm:text-xs text-slate-600 font-bold mt-0.5 truncate">
            💡 <strong>İpucu:</strong> {{ currentStep?.ipucu }}
          </p>
        </div>
      </div>

      <!-- Tümü / Adım Adım Modu & Sıfırla Butonları -->
      <div class="flex items-center gap-2 shrink-0">
        <button
          type="button"
          @click="resetComponentPositions"
          class="px-2.5 py-1.5 rounded-xl text-xs font-black border-2 border-slate-900 bg-slate-100 hover:bg-slate-200 text-slate-700 transition flex items-center gap-1 cursor-pointer shadow-xs active:translate-y-0.5"
          title="Parçaları varsayılan konuma getir"
        >
          <span>🔄 Konumları Sıfırla</span>
        </button>

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
          v-for="(step, idx) in effectiveSteps"
          :key="idx"
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

    <!-- 3. @WOKWI/ELEMENTS İNTERAKTİF ÇALIŞMA ALANI (DRAGGABLE & DYNAMIC WIRING) -->
    <div
      ref="workspaceRef"
      class="relative w-full flex-1 overflow-hidden bg-slate-900 rounded-3xl border-[3px] border-slate-900 shadow-[0_8px_0_rgba(15,23,42,0.2)] min-h-[520px] select-none"
      @mousemove="handleDragMove"
      @mouseup="handleDragEnd"
      @mouseleave="handleDragEnd"
    >
      <!-- Arka Plan Grid Ağı -->
      <div class="absolute inset-0 pointer-events-none opacity-25" style="background-image: radial-gradient(#64748b 1px, transparent 1px); background-size: 20px 20px;"></div>

      <!-- Bilgi Başlığı -->
      <div class="absolute top-3 left-4 z-20 pointer-events-none flex items-center gap-2">
        <span class="px-2.5 py-1 rounded-lg bg-slate-800/80 border border-slate-700 text-[11px] font-black tracking-wide text-slate-300">
          ⚡ WOKWI SİMÜLATÖR MOTORU • Parçaları fareyle tutup sürükleyebilirsin!
        </span>
      </div>

      <!-- ======================================================== -->
      <!-- A) BİLEŞENLER KATMANI (@wokwi/elements Web Components)     -->
      <!-- ======================================================== -->

      <!-- 1. ARDUINO KARTI (Varsayılan Uno) -->
      <div
        id="comp-arduino"
        class="absolute cursor-move select-none z-10 p-1 rounded-2xl hover:ring-2 hover:ring-sky-400/80 transition-shadow duration-150"
        :style="{ left: `${positions.arduino.x}px`, top: `${positions.arduino.y}px` }"
        @mousedown.stop="handleDragStart('arduino', $event)"
      >
        <wokwi-arduino-uno></wokwi-arduino-uno>
        <div class="text-[10px] font-black text-center text-sky-400 mt-1 pointer-events-none">
          Arduino Uno (D13, 5V, GND)
        </div>
      </div>

      <!-- 2. BREADBOARD (Yarım Boy 30 Sütun) -->
      <div
        id="comp-breadboard"
        class="absolute cursor-move select-none z-10 p-1 rounded-2xl hover:ring-2 hover:ring-amber-400/80 transition-shadow duration-150"
        :style="{ left: `${positions.breadboard.x}px`, top: `${positions.breadboard.y}px` }"
        @mousedown.stop="handleDragStart('breadboard', $event)"
      >
        <wokwi-breadboard-half></wokwi-breadboard-half>
        <div class="text-[10px] font-black text-center text-amber-300 mt-1 pointer-events-none">
          Breadboard (1A - 30J, +/ - Güç Hatları)
        </div>
      </div>

      <!-- 3. KIRMIZI LED -->
      <div
        v-if="hasComponent('LED')"
        id="comp-led"
        class="absolute cursor-move select-none z-20 p-1 rounded-xl hover:ring-2 hover:ring-rose-400"
        :style="{ left: `${positions.led.x}px`, top: `${positions.led.y}px` }"
        @mousedown.stop="handleDragStart('led', $event)"
      >
        <wokwi-led color="red" value="1"></wokwi-led>
        <div class="text-[9px] font-black text-center text-rose-300 pointer-events-none whitespace-nowrap">
          Kırmızı LED
        </div>
      </div>

      <!-- 4. 220 OHM DİRENÇ -->
      <div
        v-if="hasComponent('RESISTOR')"
        id="comp-resistor"
        class="absolute cursor-move select-none z-20 p-1 rounded-xl hover:ring-2 hover:ring-amber-400"
        :style="{ left: `${positions.resistor.x}px`, top: `${positions.resistor.y}px` }"
        @mousedown.stop="handleDragStart('resistor', $event)"
      >
        <wokwi-resistor value="220"></wokwi-resistor>
        <div class="text-[9px] font-black text-center text-amber-300 pointer-events-none whitespace-nowrap">
          220Ω Direnç
        </div>
      </div>

      <!-- 5. LDR IŞIK SENSÖRÜ -->
      <div
        v-if="hasComponent('LDR')"
        id="comp-ldr"
        class="absolute cursor-move select-none z-20 p-1 rounded-xl hover:ring-2 hover:ring-emerald-400"
        :style="{ left: `${positions.ldr.x}px`, top: `${positions.ldr.y}px` }"
        @mousedown.stop="handleDragStart('ldr', $event)"
      >
        <wokwi-photoresistor-sensor></wokwi-photoresistor-sensor>
        <div class="text-[9px] font-black text-center text-emerald-300 pointer-events-none whitespace-nowrap">
          LDR Işık Sensörü
        </div>
      </div>

      <!-- 6. BUZZER -->
      <div
        v-if="hasComponent('BUZZER')"
        id="comp-buzzer"
        class="absolute cursor-move select-none z-20 p-1 rounded-xl hover:ring-2 hover:ring-yellow-400"
        :style="{ left: `${positions.buzzer.x}px`, top: `${positions.buzzer.y}px` }"
        @mousedown.stop="handleDragStart('buzzer', $event)"
      >
        <wokwi-buzzer></wokwi-buzzer>
        <div class="text-[9px] font-black text-center text-yellow-300 pointer-events-none whitespace-nowrap">
          Buzzer
        </div>
      </div>

      <!-- 7. HC-SR04 ULTRASONİK MESAFE SENSÖRÜ -->
      <div
        v-if="hasComponent('HCSR') || hasComponent('MESAFE')"
        id="comp-hcsr04"
        class="absolute cursor-move select-none z-20 p-1 rounded-xl hover:ring-2 hover:ring-cyan-400"
        :style="{ left: `${positions.hcsr04.x}px`, top: `${positions.hcsr04.y}px` }"
        @mousedown.stop="handleDragStart('hcsr04', $event)"
      >
        <wokwi-hc-sr04></wokwi-hc-sr04>
        <div class="text-[9px] font-black text-center text-cyan-300 pointer-events-none whitespace-nowrap">
          HC-SR04 Mesafe Sensörü
        </div>
      </div>

      <!-- 8. SG90 SERVO MOTOR -->
      <div
        v-if="hasComponent('SERVO')"
        id="comp-servo"
        class="absolute cursor-move select-none z-20 p-1 rounded-xl hover:ring-2 hover:ring-blue-400"
        :style="{ left: `${positions.servo.x}px`, top: `${positions.servo.y}px` }"
        @mousedown.stop="handleDragStart('servo', $event)"
      >
        <wokwi-servo></wokwi-servo>
        <div class="text-[9px] font-black text-center text-blue-300 pointer-events-none whitespace-nowrap">
          SG90 Servo
        </div>
      </div>

      <!-- ======================================================== -->
      <!-- B) KABLO BAĞLANTILARI VE PİN İŞARETÇİLERİ SVG KATMANI     -->
      <!-- ======================================================== -->
      <svg class="absolute inset-0 w-full h-full pointer-events-none z-30 overflow-visible">
        <defs>
          <filter id="wireShadow" x="-20%" y="-20%" width="140%" height="140%">
            <feDropShadow dx="0" dy="4" stdDeviation="3" flood-color="#000000" flood-opacity="0.6" />
          </filter>
        </defs>

        <!-- Kablolar -->
        <g v-for="(wire, idx) in computedWires" :key="idx">
          <!-- Kablo Gölgesi -->
          <path
            :d="wire.path"
            fill="none"
            stroke="#020617"
            stroke-width="6"
            stroke-linecap="round"
            opacity="0.5"
          />
          <!-- Kablo Gövdesi -->
          <path
            :d="wire.path"
            fill="none"
            :stroke="wire.step.kablo_rengi || '#38bdf8'"
            stroke-width="3.5"
            stroke-linecap="round"
            :class="{ 'wire-active-flow': idx === currentStepIndex || showAllWires }"
          />

          <!-- Başlangıç Ucu Pini (Küçük Halka) -->
          <circle
            :cx="wire.from.x"
            :cy="wire.from.y"
            r="4.5"
            :fill="wire.step.kablo_rengi || '#38bdf8'"
            stroke="#ffffff"
            stroke-width="1.5"
          />

          <!-- Bitiş Ucu Pini (Küçük Halka) -->
          <circle
            :cx="wire.to.x"
            :cy="wire.to.y"
            r="4.5"
            :fill="wire.step.kablo_rengi || '#38bdf8'"
            stroke="#ffffff"
            stroke-width="1.5"
          />
        </g>

        <!-- Aktif Adım İçin Parlayan Pin Göstergesi ve "👇 Buraya Tak!" Balonu -->
        <g v-if="activeTargetCoord">
          <!-- Pulsing Target Glow Ring -->
          <circle
            :cx="activeTargetCoord.x"
            :cy="activeTargetCoord.y"
            r="12"
            fill="#facc15"
            opacity="0.6"
            class="animate-ping"
          />
          <circle
            :cx="activeTargetCoord.x"
            :cy="activeTargetCoord.y"
            r="6"
            fill="#eab308"
            stroke="#ffffff"
            stroke-width="2"
          />

          <!-- "👇 Buraya Tak!" Çizgi Film Konuşma Baloncuğu -->
          <g :transform="`translate(${activeTargetCoord.x}, ${activeTargetCoord.y - 34})`">
            <rect
              x="-52"
              y="-15"
              width="104"
              height="26"
              rx="9"
              fill="#fde047"
              stroke="#0f172a"
              stroke-width="2.5"
              filter="url(#wireShadow)"
            />
            <!-- Balon İğnesi -->
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

    <!-- 4. ALT DEVAM ET BUTONU -->
    <div class="flex items-center justify-between pt-1">
      <button
        type="button"
        @click="$emit('prev-page')"
        class="px-4 py-2 rounded-xl border-2 border-slate-900 bg-white hover:bg-slate-50 text-slate-800 font-black text-xs transition cursor-pointer shadow-xs active:translate-y-0.5"
      >
        ◀ 1. Hayal Et'e Dön
      </button>

      <button
        type="button"
        @click="$emit('next-page')"
        class="px-6 py-2.5 rounded-2xl border-2 border-slate-900 bg-[#4ade80] hover:bg-[#22c55e] text-slate-950 font-black text-xs sm:text-sm shadow-[0_4px_0_#15803d] active:translate-y-1 active:shadow-none transition cursor-pointer flex items-center gap-1.5"
      >
        <span>3. Nasıl Çalışacak'a Geç</span>
        <span class="text-base">➔</span>
      </button>
    </div>

  </div>
</template>

<script setup lang="ts">
import { ref, reactive, computed, onMounted, nextTick, watch } from 'vue';
import type { BaglantiAdimi } from '../types/project';
import { resolveElementPin, createWirePath, type PinCoord } from '../utils/pinResolver';

const props = defineProps<{
  baglantiAdimlari?: BaglantiAdimi[];
  gerekliParcalar?: string[];
}>();

defineEmits<{
  (e: 'next-page'): void;
  (e: 'prev-page'): void;
}>();

const workspaceRef = ref<HTMLElement | null>(null);
const currentStepIndex = ref(0);
const showAllWires = ref(false);

// Varsayılan bağlantı adımları (props boş gelse dahi devreyi kur ekranının boş çıkmaması için koruma)
const defaultAdimlar: BaglantiAdimi[] = [
  {
    adim_no: 1,
    talimat: "Kırmızı LED'in uzun bacağını Breadboard'un 5E deliğine tak.",
    ipucu: "Uzun bacak (+) yani anot ucudur!",
    kaynak_parca: "ARDUINO_UNO",
    kaynak_pin: "D13",
    hedef_parca: "BREADBOARD",
    hedef_pin: "5E",
    kablo_rengi: "#ef4444"
  },
  {
    adim_no: 2,
    talimat: "220Ω Direncin bir ucunu LED'in kısa bacağının olduğu 5C deliğine tak.",
    ipucu: "Direnç LED'imizin fazla akımdan yanmasını önler!",
    kaynak_parca: "BREADBOARD",
    kaynak_pin: "5C",
    hedef_parca: "BREADBOARD",
    hedef_pin: "9C",
    kablo_rengi: "#f59e0b"
  },
  {
    adim_no: 3,
    talimat: "Direncin diğer ucunu (9A) Arduino'nun GND (Toprak) pinine bağla.",
    ipucu: "GND devreyi tamamlar ve akımın toprağa akmasını sağlar.",
    kaynak_parca: "BREADBOARD",
    kaynak_pin: "9A",
    hedef_parca: "ARDUINO_UNO",
    hedef_pin: "GND",
    kablo_rengi: "#3b82f6"
  }
];

const effectiveSteps = computed<BaglantiAdimi[]>(() => {
  if (props.baglantiAdimlari && props.baglantiAdimlari.length > 0) {
    return props.baglantiAdimlari;
  }
  return defaultAdimlar;
});

const totalSteps = computed(() => effectiveSteps.value.length);
const currentStepNumber = computed(() => currentStepIndex.value + 1);
const currentStep = computed(() => effectiveSteps.value[currentStepIndex.value]);

function hasComponent(keyword: string): boolean {
  const kw = keyword.toUpperCase();
  if (kw === 'LED' || kw === 'RESISTOR') return true; // Temel parçalar her zaman mevcuttur
  return props.gerekliParcalar?.some(p => p.toUpperCase().includes(kw)) ?? false;
}

// Bileşenlerin Çalışma Alanındaki (x, y) Konumları
const defaultPositions = {
  arduino: { x: 30, y: 160 },
  breadboard: { x: 340, y: 160 },
  led: { x: 410, y: 65 },
  resistor: { x: 490, y: 75 },
  ldr: { x: 580, y: 65 },
  buzzer: { x: 710, y: 140 },
  hcsr04: { x: 710, y: 280 },
  servo: { x: 120, y: 400 },
  pot: { x: 580, y: 390 }
};

const positions = reactive({ ...defaultPositions });

function resetComponentPositions() {
  Object.assign(positions, defaultPositions);
  updateWires();
}

// DRAGGING STATE
let activeDragTarget: string | null = null;
let dragStartMouse = { x: 0, y: 0 };
let dragStartPos = { x: 0, y: 0 };

function handleDragStart(compKey: string, e: MouseEvent) {
  activeDragTarget = compKey;
  dragStartMouse = { x: e.clientX, y: e.clientY };
  const current = (positions as any)[compKey] || { x: 0, y: 0 };
  dragStartPos = { x: current.x, y: current.y };
}

function handleDragMove(e: MouseEvent) {
  if (!activeDragTarget) return;
  const dx = e.clientX - dragStartMouse.x;
  const dy = e.clientY - dragStartMouse.y;

  const target = (positions as any)[activeDragTarget];
  if (target) {
    target.x = Math.max(0, dragStartPos.x + dx);
    target.y = Math.max(0, dragStartPos.y + dy);
    // Real-time wire recalculation
    updateWires();
  }
}

function handleDragEnd() {
  activeDragTarget = null;
}

function nextStep() {
  if (currentStepIndex.value < totalSteps.value - 1) {
    currentStepIndex.value++;
    updateWires();
  }
}

function prevStep() {
  if (currentStepIndex.value > 0) {
    currentStepIndex.value--;
    updateWires();
  }
}

// DİNAMİK KABLO VE PİN HESAPLAMA MOTORU (.pinInfo üzerinden)
interface WireData {
  step: BaglantiAdimi;
  from: PinCoord;
  to: PinCoord;
  path: string;
}

const computedWires = ref<WireData[]>([]);
const activeTargetCoord = ref<PinCoord | null>(null);

/**
 * Parça adı veya ID'sinden ilgili HTML/DOM elementini ve konumunu çözer.
 */
function resolveComponentElement(partIdentifier: string): { el: HTMLElement | null; pos: { x: number; y: number } } {
  const query = (partIdentifier || '').toUpperCase();

  if (query.includes('ARDUINO') || query.includes('UNO') || query.includes('NANO') || query.includes('MEGA') || query.includes('ESP32')) {
    const el = document.getElementById('comp-arduino');
    return { el: (el?.firstElementChild as HTMLElement) || el, pos: positions.arduino };
  }
  if (query.includes('BREADBOARD')) {
    const el = document.getElementById('comp-breadboard');
    return { el: (el?.firstElementChild as HTMLElement) || el, pos: positions.breadboard };
  }
  if (query.includes('LED')) {
    const el = document.getElementById('comp-led');
    return { el: (el?.firstElementChild as HTMLElement) || el, pos: positions.led };
  }
  if (query.includes('RESISTOR') || query.includes('DIRENC')) {
    const el = document.getElementById('comp-resistor');
    return { el: (el?.firstElementChild as HTMLElement) || el, pos: positions.resistor };
  }
  if (query.includes('LDR')) {
    const el = document.getElementById('comp-ldr');
    return { el: (el?.firstElementChild as HTMLElement) || el, pos: positions.ldr };
  }
  if (query.includes('BUZZER')) {
    const el = document.getElementById('comp-buzzer');
    return { el: (el?.firstElementChild as HTMLElement) || el, pos: positions.buzzer };
  }
  if (query.includes('HCSR') || query.includes('MESAFE')) {
    const el = document.getElementById('comp-hcsr04');
    return { el: (el?.firstElementChild as HTMLElement) || el, pos: positions.hcsr04 };
  }
  if (query.includes('SERVO')) {
    const el = document.getElementById('comp-servo');
    return { el: (el?.firstElementChild as HTMLElement) || el, pos: positions.servo };
  }

  // Fallback to breadboard
  const el = document.getElementById('comp-breadboard');
  return { el: (el?.firstElementChild as HTMLElement) || el, pos: positions.breadboard };
}

function updateWires() {
  const wires: WireData[] = [];
  const steps = effectiveSteps.value;
  const count = showAllWires.value ? steps.length : currentStepIndex.value + 1;

  for (let i = 0; i < count; i++) {
    const s = steps[i];
    if (!s) continue;

    const source = resolveComponentElement(s.kaynak_parca);
    const target = resolveComponentElement(s.hedef_parca);

    if (source.el && target.el) {
      const p1Offset = resolveElementPin(source.el, s.kaynak_pin);
      const p2Offset = resolveElementPin(target.el, s.hedef_pin);

      const p1Canvas: PinCoord = {
        x: source.pos.x + p1Offset.x,
        y: source.pos.y + p1Offset.y
      };
      const p2Canvas: PinCoord = {
        x: target.pos.x + p2Offset.x,
        y: target.pos.y + p2Offset.y
      };

      wires.push({
        step: s,
        from: p1Canvas,
        to: p2Canvas,
        path: createWirePath(p1Canvas, p2Canvas)
      });
    }
  }

  computedWires.value = wires;

  // Aktif adımın hedef pin koordinatı
  if (currentStep.value) {
    const target = resolveComponentElement(currentStep.value.hedef_parca);
    if (target.el) {
      const p2Offset = resolveElementPin(target.el, currentStep.value.hedef_pin);
      activeTargetCoord.value = {
        x: target.pos.x + p2Offset.x,
        y: target.pos.y + p2Offset.y
      };
    } else {
      activeTargetCoord.value = null;
    }
  } else {
    activeTargetCoord.value = null;
  }
}

watch(() => props.baglantiAdimlari, () => {
  currentStepIndex.value = 0;
  nextTick(() => updateWires());
}, { deep: true });

onMounted(() => {
  // custom elements ve shadow DOM tanımlandığında kabloları bağla
  nextTick(() => {
    setTimeout(() => {
      updateWires();
    }, 150);
  });
});
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

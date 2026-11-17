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

    <!-- 3. SABİT VE DOĞRU BREADBOARD MİMARİSİ ÇALIŞMA ALANI -->
    <div
      ref="workspaceRef"
      class="relative w-full flex-1 overflow-x-auto overflow-y-hidden bg-slate-900 rounded-3xl border-[3px] border-slate-900 shadow-[0_8px_0_rgba(15,23,42,0.2)] min-h-[500px] select-none p-4 flex items-center justify-center"
    >
      <!-- Arka Plan Grid Ağı -->
      <div class="absolute inset-0 pointer-events-none opacity-25" style="background-image: radial-gradient(#64748b 1px, transparent 1px); background-size: 20px 20px;"></div>

      <!-- Üst Bilgi Rozeti -->
      <div class="absolute top-3 left-4 z-20 pointer-events-none flex flex-wrap items-center gap-2">
        <span class="px-2.5 py-1 rounded-lg bg-slate-800/90 border border-slate-700 text-[11px] font-black tracking-wide text-amber-300">
          ⚡ BREADBOARD İLETKENLİK MOTORU • Parçalar breadboard deliklerine takılıdır!
        </span>
        <span class="px-2 py-0.5 rounded-lg bg-emerald-950/80 border border-emerald-500/50 text-[10px] font-bold text-emerald-300">
          Dikey Sütunlar (A-E) içeriden iletkendir
        </span>
      </div>

      <!-- ÇALIŞMA ALANI İÇ KUTUSU (Genişlik ve Yükseklik Sabitlenmiş Doğru Yerleşim) -->
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
            Arduino Uno (D13, 5V, GND)
          </div>
        </div>

        <!-- ======================================================== -->
        <!-- B) BREADBOARD VE ÜZERİNE TAKILI BİLEŞENLER (Sağ Tarafta) -->
        <!-- ======================================================== -->
        <div
          id="comp-breadboard-wrapper"
          class="absolute left-[440px] top-[100px] z-10 p-2 rounded-2xl bg-slate-800/40 border border-slate-700/60 shadow-lg"
        >
          <!-- Breadboard Web Component'i (Aktif Sütunları İç İletkenlik Olarak Parlatır) -->
          <wokwi-breadboard-half
            id="comp-breadboard"
            :highlighted-columns="activeColumnsStr"
            :highlighted-rails="activeRailsStr"
          ></wokwi-breadboard-half>

          <!-- BREADBOARD ÜZERİNE TAKILI BİLEŞENLER (DELİKLERE HİZALANMIŞ) -->
          
          <!-- 1. Kırmızı LED (Kolon 5E ve Kolon 6E Deliklerine Takılı) -->
          <div
            v-if="hasComponent('LED')"
            id="comp-led"
            class="absolute pointer-events-none z-20"
            style="left: 69px; top: 52px;"
          >
            <wokwi-led color="red" value="1"></wokwi-led>
            <!-- LED İsim Rozeti -->
            <div class="absolute -top-4 left-1/2 -translate-x-1/2 px-1.5 py-0.2 rounded-md bg-rose-600 text-[8px] font-black text-white shadow-xs whitespace-nowrap">
              LED (5E ➔ 6E)
            </div>
          </div>

          <!-- 2. 220Ω Direnç (Kolon 6C ve Kolon 12C Deliklerine Takılı) -->
          <!-- Kolon 6: LED'in kısa bacağı ile direncin bacağı BREADBOARD İÇİNDEN BAĞLANIR! -->
          <div
            v-if="hasComponent('RESISTOR')"
            id="comp-resistor"
            class="absolute pointer-events-none z-20"
            style="left: 93px; top: 70px;"
          >
            <wokwi-resistor value="220"></wokwi-resistor>
            <!-- Direnç İsim Rozeti -->
            <div class="absolute -top-4 left-1/2 -translate-x-1/2 px-1.5 py-0.2 rounded-md bg-amber-600 text-[8px] font-black text-white shadow-xs whitespace-nowrap">
              220Ω (6C ➔ 12C)
            </div>
          </div>

          <!-- 3. LDR Işık Sensörü (Kolon 18E ve Kolon 20E Deliklerine Takılı) -->
          <div
            v-if="hasComponent('LDR')"
            id="comp-ldr"
            class="absolute pointer-events-none z-20 scale-[0.6] origin-top-left"
            style="left: 200px; top: 48px;"
          >
            <wokwi-photoresistor-sensor></wokwi-photoresistor-sensor>
            <div class="absolute -top-4 left-1/2 -translate-x-1/2 px-1.5 py-0.2 rounded-md bg-emerald-600 text-[10px] font-black text-white shadow-xs whitespace-nowrap">
              LDR Sensör
            </div>
          </div>

          <!-- 4. Buzzer (Kolon 24F ve Kolon 26F Deliklerine Takılı) -->
          <div
            v-if="hasComponent('BUZZER')"
            id="comp-buzzer"
            class="absolute pointer-events-none z-20 scale-[0.65] origin-top-left"
            style="left: 250px; top: 120px;"
          >
            <wokwi-buzzer></wokwi-buzzer>
            <div class="absolute -top-3 left-1/2 -translate-x-1/2 px-1.5 py-0.2 rounded-md bg-yellow-500 text-[10px] font-black text-slate-950 shadow-xs whitespace-nowrap">
              Buzzer (24F-26F)
            </div>
          </div>

          <!-- Breadboard İletkenlik Açıklama Çubuğu -->
          <div class="text-[10px] font-black text-center text-amber-300 mt-1 pointer-events-none">
            Breadboard (Sütun 5, 6, 12 Devre İçi İletkendir)
          </div>
        </div>

        <!-- 5. Harici Sensörler (HC-SR04 Mesafe Sensörü Sağ Tarafta) -->
        <div
          v-if="hasComponent('HCSR') || hasComponent('MESAFE')"
          id="comp-hcsr04"
          class="absolute left-[810px] top-[140px] z-10 p-2 rounded-2xl bg-slate-800/40 border border-slate-700/60 shadow-lg scale-[0.7] origin-top-left"
        >
          <wokwi-hc-sr04></wokwi-hc-sr04>
          <div class="text-[10px] font-black text-center text-cyan-300 mt-1 pointer-events-none">
            HC-SR04 Sensör
          </div>
        </div>

        <!-- ======================================================== -->
        <!-- C) KABLO BAĞLANTILARI VE PİN İŞARETÇİLERİ SVG KATMANI     -->
        <!-- ======================================================== -->
        <svg class="absolute inset-0 w-full h-full pointer-events-none z-30 overflow-visible">
          <defs>
            <filter id="wireShadow2" x="-20%" y="-20%" width="140%" height="140%">
              <feDropShadow dx="0" dy="4" stdDeviation="3" flood-color="#000000" flood-opacity="0.6" />
            </filter>
          </defs>

          <!-- 1. Breadboard İçi İletkenlik Bağlantı Hattı (Sütun 6: LED Katot ➔ Direnç) -->
          <g v-if="hasComponent('LED') && hasComponent('RESISTOR')" opacity="0.8">
            <line
              x1="533"
              y1="194"
              x2="533"
              y2="175"
              stroke="#22c55e"
              stroke-width="3"
              stroke-dasharray="2,2"
            />
            <circle cx="533" cy="194" r="3" fill="#22c55e" />
            <circle cx="533" cy="175" r="3" fill="#22c55e" />
          </g>

          <!-- 2. Dinamik Jumper Kablolar (Arduino ➔ Breadboard Delikleri) -->
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

          <!-- 3. Aktif Adım Hedef Göstergesi ve "👇 Buraya Tak!" Baloncuğu -->
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
                filter="url(#wireShadow2)"
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
    </div>

    <!-- 4. ALT DEVAM ET VE BİLGİ BANDI -->
    <div class="bg-amber-50 rounded-2xl border-2 border-amber-300 p-2.5 flex items-center justify-between gap-3 text-xs">
      <div class="flex items-center gap-2 text-amber-950 font-bold">
        <span class="text-base">💡</span>
        <span>
          <strong>Breadboard Nasıl Çalışır?</strong> Aynı sütundaki dikey delikler (A, B, C, D, E) içeriden bağlıdır! Bu yüzden LED'in bacağı ile direnç 6. sütunda kablosuz buluşur.
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
import { ref, computed, onMounted, nextTick, watch } from 'vue';
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

// Varsayılan bağlantı adımları (tamamen Breadboard mimarisine uygun)
const defaultAdimlar: BaglantiAdimi[] = [
  {
    adim_no: 1,
    talimat: "Kırmızı kabloyu Arduino D13 pininden Breadboard'un 5A deliğine tak.",
    ipucu: "5A deliği içeriden LED'in uzun anot bacağına (5E) bağlıdır!",
    kaynak_parca: "ARDUINO_UNO",
    kaynak_pin: "D13",
    hedef_parca: "BREADBOARD",
    hedef_pin: "5A",
    kablo_rengi: "#ef4444"
  },
  {
    adim_no: 2,
    talimat: "Mavi kabloyu Breadboard'un 12A deliğinden Arduino'nun GND pinine bağla.",
    ipucu: "12A deliği içeriden 220Ω direncin diğer bacağına bağlıdır, devreyi tamamlar!",
    kaynak_parca: "BREADBOARD",
    kaynak_pin: "12A",
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
  if (kw === 'LED' || kw === 'RESISTOR') return true;
  return props.gerekliParcalar?.some(p => p.toUpperCase().includes(kw)) ?? false;
}

// Sabit Konum Koordinatları (Piksel cinsinden)
// comp-arduino wrapper: left: 40px, top: 100px (içindeki uno: p-2 ile ~8px ofset)
const UNO_OFFSET = { x: 48, y: 108 };
// comp-breadboard-wrapper: left: 440px, top: 100px (içindeki breadboard: p-2 ile ~8px ofset)
const BB_OFFSET = { x: 448, y: 108 };

// Aktif Parıldayan Sütunlar ve Güç Hatları
const activeColumnsStr = computed(() => {
  const cols = new Set<number>([5, 6, 12]);
  if (hasComponent('LDR')) {
    cols.add(18);
    cols.add(20);
  }
  if (hasComponent('BUZZER')) {
    cols.add(24);
    cols.add(26);
  }
  return Array.from(cols).join(',');
});

const activeRailsStr = computed(() => {
  return 'top-+,top--';
});

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

interface WireData {
  step: BaglantiAdimi;
  from: PinCoord;
  to: PinCoord;
  path: string;
}

const computedWires = ref<WireData[]>([]);
const activeTargetCoord = ref<PinCoord | null>(null);

/**
 * Parça ve pin sorgusundan tam tuval (x, y) koordinatını deterministik olarak hesaplar.
 */
function getCanvasPin(part: string, pin: string): PinCoord {
  const qPart = (part || '').toUpperCase();
  const qPin = (pin || '').trim();

  // 1. Arduino Pini
  if (qPart.includes('ARDUINO') || qPart.includes('UNO')) {
    const unoEl = document.querySelector('wokwi-arduino-uno') as HTMLElement;
    if (unoEl) {
      const p = resolveElementPin(unoEl, qPin);
      return { x: UNO_OFFSET.x + p.x, y: UNO_OFFSET.y + p.y };
    }
    // Fallback: D13 pini
    return { x: UNO_OFFSET.x + 125, y: UNO_OFFSET.y + 9 };
  }

  // 2. Breadboard Deliği veya Breadboard üzerindeki eleman
  const bbEl = document.querySelector('wokwi-breadboard-half') as HTMLElement;
  if (bbEl) {
    // Eğer hedef pin "LED" veya "ANODE" denmişse breadboard 5A deliğine eşleştir
    let mappedPin = qPin;
    if (qPart.includes('LED') || qPin.toUpperCase().includes('ANODE')) {
      mappedPin = '5A';
    } else if (qPart.includes('RESISTOR') || qPin.toUpperCase().includes('DIRENC')) {
      mappedPin = '12A';
    } else if (qPart.includes('LDR')) {
      mappedPin = '20A';
    } else if (qPart.includes('BUZZER')) {
      mappedPin = '24F';
    }

    const p = resolveElementPin(bbEl, mappedPin);
    return { x: BB_OFFSET.x + p.x, y: BB_OFFSET.y + p.y };
  }

  // Fallback
  return { x: BB_OFFSET.x + 76, y: BB_OFFSET.y + 48 };
}

function updateWires() {
  const wires: WireData[] = [];
  const steps = effectiveSteps.value;
  const count = showAllWires.value ? steps.length : currentStepIndex.value + 1;

  for (let i = 0; i < count; i++) {
    const s = steps[i];
    if (!s) continue;

    const fromCoord = getCanvasPin(s.kaynak_parca, s.kaynak_pin);
    const toCoord = getCanvasPin(s.hedef_parca, s.hedef_pin);

    wires.push({
      step: s,
      from: fromCoord,
      to: toCoord,
      path: createWirePath(fromCoord, toCoord)
    });
  }

  computedWires.value = wires;

  // Aktif adımın hedef ucu
  if (currentStep.value) {
    activeTargetCoord.value = getCanvasPin(currentStep.value.hedef_parca, currentStep.value.hedef_pin);
  } else {
    activeTargetCoord.value = null;
  }
}

watch(() => props.baglantiAdimlari, () => {
  currentStepIndex.value = 0;
  nextTick(() => updateWires());
}, { deep: true });

onMounted(() => {
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

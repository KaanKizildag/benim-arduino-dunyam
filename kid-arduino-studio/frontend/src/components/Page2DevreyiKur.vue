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

      <!-- Tümü / Adım Adım Modu Butonu -->
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
          v-for="(step, idx) in baglantiAdimlari"
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

    <!-- 3. RESMİ FRITZING PARÇALARI DEVRE ÇALIŞMA ALANI -->
    <div class="relative w-full flex-1 overflow-hidden bg-slate-900 rounded-3xl border-[3px] border-slate-900 shadow-[0_8px_0_rgba(15,23,42,0.2)] flex items-center justify-center p-2 min-h-[460px]">
      
      <svg
        viewBox="0 0 1000 720"
        class="w-full h-full select-none"
        preserveAspectRatio="xMidYMid meet"
      >
        <!-- Arka Plan Grid Ağı -->
        <defs>
          <pattern id="fritzingGrid" width="20" height="20" patternUnits="userSpaceOnUse">
            <circle cx="2" cy="2" r="1" fill="#334155" opacity="0.4" />
          </pattern>
        </defs>
        <rect width="1000" height="720" fill="#0f172a" />
        <rect width="1000" height="720" fill="url(#fritzingGrid)" />

        <!-- Bilgi Başlığı -->
        <text x="30" y="24" fill="#94a3b8" font-size="11" font-weight="900" letter-spacing="1">
          RESMİ FRITZING DEVRE GÖRÜNÜMÜ • ADIM {{ currentStepNumber }}: {{ currentStep?.kaynak_parca }} ({{ currentStep?.kaynak_pin }}) ➔ {{ currentStep?.hedef_parca }} ({{ currentStep?.hedef_pin }})
        </text>

        <!-- ======================================================== -->
        <!-- A) RESMİ FRITZING HALF BREADBOARD                        -->
        <!-- ======================================================== -->
        <g id="fritzing-breadboard-group">
          <!-- Orijinal Fritzing SVG Dosyası -->
          <image
            href="/fritzing/halfBreadboard.svg"
            :x="FRITZING_CONFIG.BB_X"
            :y="FRITZING_CONFIG.BB_Y"
            :width="FRITZING_CONFIG.BB_WIDTH"
            :height="FRITZING_CONFIG.BB_HEIGHT"
          />

          <!-- Bölge Göstergeleri (Sol Sütun 1-8: Mavi, Orta Sütun 10-18: Sarı, Sağ Sütun 20-28: Kırmızı) -->
          <rect
            :x="FRITZING_CONFIG.BB_X + 50"
            :y="FRITZING_CONFIG.BB_Y + 70"
            width="130"
            height="185"
            rx="6"
            fill="#38bdf8"
            fill-opacity="0.14"
            stroke="#0284c7"
            stroke-width="1.5"
            stroke-dasharray="4,4"
          />
          <text :x="FRITZING_CONFIG.BB_X + 115" :y="FRITZING_CONFIG.BB_Y + 65" fill="#38bdf8" font-size="9" font-weight="900" text-anchor="middle">
            SOL BÖLGE (LED & DİRENÇ)
          </text>

          <rect
            :x="FRITZING_CONFIG.BB_X + 195"
            :y="FRITZING_CONFIG.BB_Y + 70"
            width="145"
            height="185"
            rx="6"
            fill="#fde047"
            fill-opacity="0.16"
            stroke="#ca8a04"
            stroke-width="1.5"
            stroke-dasharray="4,4"
          />
          <text :x="FRITZING_CONFIG.BB_X + 267" :y="FRITZING_CONFIG.BB_Y + 65" fill="#fde047" font-size="9" font-weight="900" text-anchor="middle">
            ORTA BÖLGE (SENSÖRLER)
          </text>

          <rect
            :x="FRITZING_CONFIG.BB_X + 355"
            :y="FRITZING_CONFIG.BB_Y + 70"
            width="135"
            height="185"
            rx="6"
            fill="#f87171"
            fill-opacity="0.14"
            stroke="#ef4444"
            stroke-width="1.5"
            stroke-dasharray="4,4"
          />
          <text :x="FRITZING_CONFIG.BB_X + 422" :y="FRITZING_CONFIG.BB_Y + 65" fill="#f87171" font-size="9" font-weight="900" text-anchor="middle">
            SAĞ BÖLGE (BUZZER)
          </text>

          <!-- BİLEŞENLER (Resmi Fritzing Görselleri) -->
          <!-- 1. Kırmızı LED (Sol Bölge: E5, E6) -->
          <g v-if="hasComponent('LED')" :transform="`translate(${pinCoords.E5?.x - 12 || 337}, ${pinCoords.E5?.y - 38 || 124})`">
            <image href="/fritzing/led_red.svg" width="36" height="68" />
            <text x="18" y="-5" fill="#f87171" font-size="9" font-weight="900" text-anchor="middle">Kırmızı LED</text>
          </g>

          <!-- 2. 220 Ohm Direnç (C6 -> C10) -->
          <g v-if="hasComponent('RESISTOR')" :transform="`translate(${pinCoords.C6?.x - 5 || 359}, ${pinCoords.C6?.y - 10 || 120})`">
            <image href="/fritzing/resistor_220.svg" width="70" height="20" />
            <text x="35" y="-5" fill="#f59e0b" font-size="9" font-weight="900" text-anchor="middle">220Ω Direnç</text>
          </g>

          <!-- 3. LDR Işık Sensörü (Orta Bölge: E12, E14) -->
          <g v-if="hasComponent('LDR')" :transform="`translate(${pinCoords.E12?.x - 10 || 450}, ${pinCoords.E12?.y - 25 || 135})`">
            <image href="/fritzing/ldr.svg" width="48" height="32" />
            <text x="24" y="-5" fill="#34d399" font-size="9" font-weight="900" text-anchor="middle">LDR Sensörü</text>
          </g>

          <!-- 4. Buzzer (Sağ Bölge: F22, F24) -->
          <g v-if="hasComponent('BUZZER')" :transform="`translate(${pinCoords.F22?.x - 20 || 600}, ${pinCoords.F22?.y - 45 || 165})`">
            <image href="/fritzing/piezo_sensor.svg" width="60" height="60" />
            <text x="30" y="-5" fill="#fde047" font-size="9" font-weight="900" text-anchor="middle">Buzzer</text>
          </g>
        </g>

        <!-- ======================================================== -->
        <!-- B) RESMİ FRITZING ARDUINO UNO REV3                       -->
        <!-- ======================================================== -->
        <g id="fritzing-arduino-group">
          <!-- Orijinal Fritzing Arduino Uno SVG Dosyası -->
          <image
            href="/fritzing/arduino_uno.svg"
            :x="FRITZING_CONFIG.UNO_X"
            :y="FRITZING_CONFIG.UNO_Y"
            :width="FRITZING_CONFIG.UNO_WIDTH"
            :height="FRITZING_CONFIG.UNO_HEIGHT"
          />
        </g>

        <!-- ======================================================== -->
        <!-- C) KABLO BAĞLANTILARI (Gerçek Fritzing Pinleri Arası)     -->
        <!-- ======================================================== -->
        <g id="wires-layer">
          <template v-for="(wire, index) in visibleWires" :key="'wire-' + index">
            <!-- Arka Gölge Çizgisi -->
            <path
              :d="wire.path"
              fill="none"
              stroke="#000000"
              stroke-width="5"
              stroke-linecap="round"
              opacity="0.4"
            />
            <!-- Ana Renkli Kablo -->
            <path
              :d="wire.path"
              fill="none"
              :stroke="wire.step.kablo_rengi"
              stroke-width="3.5"
              stroke-linecap="round"
              :class="{ 'wire-flowing': index === currentStepIndex || showAllWires }"
            />
          </template>
        </g>

        <!-- ======================================================== -->
        <!-- D) AKTİF PİN PARLAMA VE ÇAĞRI BALONCUĞU ("BURAYA TAK!")   -->
        <!-- ======================================================== -->
        <!-- 1. Kaynak Pin Halkası -->
        <g v-if="activeStepCoordinates.from">
          <circle
            :cx="activeStepCoordinates.from.x"
            :cy="activeStepCoordinates.from.y"
            r="8"
            fill="#38bdf8"
            stroke="#ffffff"
            stroke-width="2"
            class="animate-ping opacity-75"
          />
          <circle
            :cx="activeStepCoordinates.from.x"
            :cy="activeStepCoordinates.from.y"
            r="4.5"
            fill="#0284c7"
            stroke="#ffffff"
            stroke-width="1.5"
          />
        </g>

        <!-- 2. Hedef Pin Halkası -->
        <g v-if="activeStepCoordinates.to">
          <circle
            :cx="activeStepCoordinates.to.x"
            :cy="activeStepCoordinates.to.y"
            r="9"
            fill="#facc15"
            stroke="#ffffff"
            stroke-width="2"
            class="animate-ping opacity-75"
          />
          <circle
            :cx="activeStepCoordinates.to.x"
            :cy="activeStepCoordinates.to.y"
            r="5"
            fill="#eab308"
            stroke="#ffffff"
            stroke-width="1.5"
          />

          <!-- "👇 Buraya Tak!" Çizgi Film Konuşma Baloncuğu -->
          <g :transform="`translate(${activeStepCoordinates.to.x}, ${activeStepCoordinates.to.y - 32})`">
            <rect
              x="-48"
              y="-14"
              width="96"
              height="24"
              rx="8"
              fill="#fde047"
              stroke="#0f172a"
              stroke-width="2"
              class="drop-shadow-md"
            />
            <!-- Balon İğnesi -->
            <polygon
              points="0,10 -5,14 5,14"
              fill="#fde047"
              stroke="#0f172a"
              stroke-width="2"
            />
            <text x="0" y="2" fill="#0f172a" font-size="10" font-weight="900" text-anchor="middle">
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
import { ref, computed } from 'vue';
import type { BaglantiAdimi } from '../types/project';
import {
  FRITZING_CONFIG,
  FRITZING_BB_PINS,
  FRITZING_UNO_PINS,
  getFritzingPinCoordinate
} from '../constants/fritzingPinMap';

const props = defineProps<{
  baglantiAdimlari: BaglantiAdimi[];
  gerekliParcalar: string[];
}>();

defineEmits<{
  (e: 'next-page'): void;
  (e: 'prev-page'): void;
}>();

const currentStepIndex = ref(0);
const showAllWires = ref(false);

const totalSteps = computed(() => props.baglantiAdimlari.length);
const currentStepNumber = computed(() => currentStepIndex.value + 1);
const currentStep = computed(() => props.baglantiAdimlari[currentStepIndex.value]);

const pinCoords = FRITZING_BB_PINS;

function hasComponent(compKeyword: string): boolean {
  return props.gerekliParcalar?.some(p => p.toUpperCase().includes(compKeyword.toUpperCase())) ?? false;
}

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

// Aktif Adımın Pin Koordinatları
const activeStepCoordinates = computed(() => {
  if (!currentStep.value) return { from: null, to: null };
  const from = getFritzingPinCoordinate(currentStep.value.kaynak_parca, currentStep.value.kaynak_pin);
  const to = getFritzingPinCoordinate(currentStep.value.hedef_parca, currentStep.value.hedef_pin);
  return { from, to };
});

// Kablo Eğrileri (Doğal Bezier Eğrileri)
function buildCurvePath(from: { x: number; y: number }, to: { x: number; y: number }): string {
  const dx = to.x - from.x;
  const dy = to.y - from.y;
  const dist = Math.sqrt(dx * dx + dy * dy);
  const curvature = Math.min(80, Math.max(30, dist * 0.25));

  // Orta kontrol noktası: kablonun aşağı doğru sarkması için
  const cx1 = from.x + dx * 0.25;
  const cy1 = from.y + curvature;
  const cx2 = to.x - dx * 0.25;
  const cy2 = to.y + curvature;

  return `M ${from.x} ${from.y} C ${cx1} ${cy1}, ${cx2} ${cy2}, ${to.x} ${to.y}`;
}

const visibleWires = computed(() => {
  const list = [];
  const count = showAllWires.value ? totalSteps.value : currentStepIndex.value + 1;

  for (let i = 0; i < count; i++) {
    const s = props.baglantiAdimlari[i];
    if (!s) continue;
    const p1 = getFritzingPinCoordinate(s.kaynak_parca, s.kaynak_pin);
    const p2 = getFritzingPinCoordinate(s.hedef_parca, s.hedef_pin);
    if (p1 && p2) {
      list.push({
        step: s,
        from: p1,
        to: p2,
        path: buildCurvePath(p1, p2)
      });
    }
  }
  return list;
});
</script>
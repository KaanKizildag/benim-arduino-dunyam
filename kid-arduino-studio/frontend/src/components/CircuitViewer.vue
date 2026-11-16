<template>
  <div class="flex flex-col gap-4">
    <!-- Adım Talimat Başlığı ve Kontroller -->
    <div class="bg-white rounded-2xl p-4 sm:p-5 border border-slate-200 shadow-sm flex flex-col md:flex-row items-center justify-between gap-4">
      <!-- Sol: Büyük Talimat -->
      <div class="flex items-start gap-3.5 flex-1 w-full">
        <div class="w-10 h-10 rounded-xl bg-indigo-600 text-white font-extrabold text-base flex items-center justify-center shrink-0 shadow-sm">
          {{ currentStepNumber }}/{{ totalSteps }}
        </div>
        <div class="flex-1">
          <div class="flex flex-wrap items-center gap-2 mb-1">
            <h3 class="font-extrabold text-slate-900 text-base sm:text-lg leading-snug">
              {{ currentStep ? currentStep.talimat : 'Tüm bağlantılar tamamlandı!' }}
            </h3>
            <span
              v-if="currentStep"
              class="inline-flex items-center gap-1.5 px-2.5 py-0.5 rounded-full text-xs font-bold text-white shadow-xs"
              :style="{ backgroundColor: currentStep.kablo_rengi }"
            >
              <span class="w-2 h-2 rounded-full bg-white"></span>
              Bu Kabloyu Tak
            </span>
          </div>
          <p v-if="currentStep" class="text-xs sm:text-sm text-slate-500 font-medium">
            💡 <strong>İpucu:</strong> {{ currentStep.ipucu }}
          </p>
        </div>
      </div>

      <!-- Sağ: Adım Değiştirme Butonları -->
      <div class="flex items-center gap-2 shrink-0">
        <button
          @click="prevStep"
          :disabled="currentStepIndex <= 0"
          class="px-4 py-2.5 rounded-xl border border-slate-300 bg-white hover:bg-slate-50 disabled:opacity-30 disabled:cursor-not-allowed font-bold text-sm text-slate-700 transition shadow-xs flex items-center gap-1.5"
        >
          <span>◀</span>
          <span>Önceki</span>
        </button>

        <button
          @click="nextStep"
          :disabled="currentStepIndex >= totalSteps - 1"
          class="px-5 py-2.5 rounded-xl bg-indigo-600 hover:bg-indigo-700 disabled:opacity-30 disabled:cursor-not-allowed font-bold text-sm text-white transition shadow-sm flex items-center gap-1.5"
        >
          <span>Sonraki</span>
          <span>▶</span>
        </button>

        <button
          @click="showAllWires = !showAllWires"
          :class="[
            'px-3 py-2.5 rounded-xl text-xs font-bold border transition',
            showAllWires
              ? 'bg-amber-50 text-amber-800 border-amber-300'
              : 'bg-slate-50 text-slate-600 border-slate-200 hover:bg-slate-100'
          ]"
        >
          {{ showAllWires ? '🔍 Adım Adım' : '👁️ Tümü' }}
        </button>
      </div>
    </div>

    <!-- SVG Devre Görselleştirme Motoru -->
    <div class="relative w-full overflow-hidden bg-slate-900 rounded-2xl border border-slate-800 shadow-md flex items-center justify-center p-2">
      <svg
        viewBox="0 0 1000 680"
        class="w-full h-auto select-none max-h-[600px]"
        xmlns="http://www.w3.org/2000/svg"
      >
        <defs>
          <pattern id="cleanGrid" width="25" height="25" patternUnits="userSpaceOnUse">
            <circle cx="2" cy="2" r="1" fill="#334155" opacity="0.3" />
          </pattern>
        </defs>

        <!-- Arka Plan -->
        <rect width="1000" height="680" fill="#0f172a" />
        <rect width="1000" height="680" fill="url(#cleanGrid)" />

        <!-- ============================================== -->
        <!-- ARDUINO UNO R3 GÖVDESİ                         -->
        <!-- ============================================== -->
        <g id="arduino-uno-clean">
          <!-- PCB -->
          <rect x="460" y="130" width="440" height="310" rx="12" fill="#0284c7" stroke="#0369a1" stroke-width="2" />

          <!-- USB Portu -->
          <rect x="430" y="150" width="60" height="55" rx="3" fill="#94a3b8" stroke="#475569" stroke-width="1.5" />
          <rect x="435" y="160" width="20" height="35" rx="2" fill="#334155" />
          <text x="440" y="220" fill="#cbd5e1" font-size="9" font-weight="700">USB</text>

          <!-- Güç Jakı -->
          <rect x="435" y="340" width="55" height="70" rx="4" fill="#1e293b" stroke="#0f172a" stroke-width="2" />
          <circle cx="462" cy="375" r="8" fill="#475569" />

          <!-- Reset Butonu -->
          <circle cx="506" cy="156" r="6" fill="#ef4444" />
          <text x="495" y="176" fill="#e0f2fe" font-size="8" font-weight="700">RESET</text>

          <!-- ATmega Çipi -->
          <rect x="630" y="240" width="170" height="45" rx="4" fill="#1e293b" stroke="#334155" stroke-width="1.5" />
          <circle cx="640" cy="262" r="3" fill="#475569" />
          <text x="665" y="268" fill="#94a3b8" font-size="12" font-weight="800" font-family="monospace">ATmega328P</text>

          <!-- Kart Yazısı -->
          <text x="530" y="330" fill="#ffffff" font-size="18" font-weight="900">Arduino</text>
          <text x="610" y="330" fill="#38bdf8" font-size="14" font-weight="800">UNO</text>

          <!-- Üst Header (Dijital Pinler) -->
          <rect x="570" y="136" width="290" height="24" rx="3" fill="#0f172a" stroke="#1e293b" />
          <g v-for="(pin, key) in upperArduinoPins" :key="key">
            <rect :x="pin.x - 5" :y="pin.y - 5" width="10" height="10" rx="2" fill="#1e293b" stroke="#475569" />
            <circle :cx="pin.x" :cy="pin.y" r="2.5" fill="#f8fafc" />
            <text :x="pin.x" :y="pin.y + 18" fill="#bae6fd" font-size="8" font-weight="800" text-anchor="middle">
              {{ pin.label }}
            </text>
          </g>

          <!-- Alt Header (Güç ve Analog) -->
          <rect x="575" y="410" width="250" height="24" rx="3" fill="#0f172a" stroke="#1e293b" />
          <g v-for="(pin, key) in lowerArduinoPins" :key="key">
            <rect :x="pin.x - 5" :y="pin.y - 5" width="10" height="10" rx="2" fill="#1e293b" stroke="#475569" />
            <circle :cx="pin.x" :cy="pin.y" r="2.5" fill="#f8fafc" />
            <text :x="pin.x" :y="pin.y - 10" fill="#bae6fd" font-size="8" font-weight="800" text-anchor="middle">
              {{ pin.label }}
            </text>
          </g>
          <text x="620" y="445" fill="#facc15" font-size="9" font-weight="800">GÜÇ (POWER)</text>
          <text x="745" y="445" fill="#38bdf8" font-size="9" font-weight="800">ANALOG (GİRİŞ)</text>
          <text x="730" y="126" fill="#ffffff" font-size="9" font-weight="800">DİJİTAL PİNLER</text>
        </g>

        <!-- ============================================== -->
        <!-- SENSÖRLER VE ÇIKIŞ BİLEŞENLERİ                 -->
        <!-- ============================================== -->
        <!-- 1. Kırmızı LED -->
        <g id="comp-led" v-if="isComponentNeeded('LED_RED')">
          <rect x="95" y="70" width="105" height="145" rx="10" fill="#1e293b" opacity="0.6" stroke="#334155" />
          <text x="147" y="90" fill="#f87171" font-size="11" font-weight="800" text-anchor="middle">Kırmızı LED</text>
          <path d="M 125 150 C 125 110, 170 110, 170 150 Z" fill="#ef4444" stroke="#dc2626" stroke-width="2" />
          <ellipse cx="147" cy="150" rx="23" ry="5" fill="#b91c1c" />
          <path d="M 135 155 L 135 175 L 130 185 L 130 200" fill="none" stroke="#cbd5e1" stroke-width="3" />
          <circle cx="130" cy="200" r="4" fill="#ef4444" />
          <text x="110" y="215" fill="#ef4444" font-size="9" font-weight="800">UZUN (+)</text>

          <line x1="160" y1="155" x2="160" y2="190" stroke="#94a3b8" stroke-width="3" />
          <circle cx="160" cy="190" r="4" fill="#3b82f6" />
          <text x="175" y="205" fill="#93c5fd" font-size="9" font-weight="800">KISA (-)</text>
        </g>

        <!-- 2. 220 Ohm Direnç -->
        <g id="comp-resistor" v-if="isComponentNeeded('RESISTOR_220')">
          <rect x="230" y="100" width="150" height="70" rx="10" fill="#1e293b" opacity="0.6" stroke="#334155" />
          <text x="305" y="120" fill="#fde047" font-size="11" font-weight="800" text-anchor="middle">220Ω Direnç</text>
          <line x1="250" y1="140" x2="275" y2="140" stroke="#cbd5e1" stroke-width="3" />
          <line x1="335" y1="140" x2="360" y2="140" stroke="#cbd5e1" stroke-width="3" />
          <rect x="275" y="130" width="60" height="20" rx="8" fill="#d97706" />
          <rect x="285" y="130" width="4" height="20" fill="#ef4444" />
          <rect x="295" y="130" width="4" height="20" fill="#ef4444" />
          <rect x="305" y="130" width="4" height="20" fill="#78350f" />
          <circle cx="250" cy="140" r="4" fill="#f59e0b" />
          <circle cx="360" cy="140" r="4" fill="#f59e0b" />
        </g>

        <!-- 3. LDR Işık Sensörü -->
        <g id="comp-ldr" v-if="isComponentNeeded('LDR_SENSOR')">
          <rect x="95" y="240" width="105" height="135" rx="10" fill="#1e293b" opacity="0.6" stroke="#334155" />
          <text x="147" y="260" fill="#34d399" font-size="11" font-weight="800" text-anchor="middle">Işık Sensörü (LDR)</text>
          <circle cx="145" cy="295" r="22" fill="#f59e0b" stroke="#b45309" stroke-width="2" />
          <path d="M 132 290 Q 145 285, 158 290 Q 145 300, 132 305" fill="none" stroke="#78350f" stroke-width="2.5" />
          <line x1="135" y1="317" x2="130" y2="350" stroke="#cbd5e1" stroke-width="3" />
          <line x1="155" y1="317" x2="160" y2="350" stroke="#cbd5e1" stroke-width="3" />
          <circle cx="130" cy="350" r="4" fill="#10b981" />
          <circle cx="160" cy="350" r="4" fill="#10b981" />
          <text x="120" y="368" fill="#6ee7b7" font-size="8" font-weight="800">5V</text>
          <text x="165" y="368" fill="#6ee7b7" font-size="8" font-weight="800">A0</text>
        </g>

        <!-- 4. Buzzer Korna -->
        <g id="comp-buzzer" v-if="isComponentNeeded('BUZZER')">
          <rect x="255" y="240" width="125" height="145" rx="10" fill="#1e293b" opacity="0.6" stroke="#334155" />
          <text x="317" y="260" fill="#c084fc" font-size="11" font-weight="800" text-anchor="middle">Buzzer (Korna)</text>
          <circle cx="317" cy="300" r="28" fill="#0f172a" stroke="#475569" stroke-width="3" />
          <circle cx="317" cy="300" r="9" fill="#1e293b" />
          <text x="295" y="295" fill="#a855f7" font-size="12" font-weight="900">+</text>
          <line x1="305" y1="328" x2="300" y2="360" stroke="#cbd5e1" stroke-width="3" />
          <line x1="330" y1="328" x2="335" y2="360" stroke="#94a3b8" stroke-width="3" />
          <circle cx="300" cy="360" r="4" fill="#a855f7" />
          <text x="285" y="378" fill="#c084fc" font-size="8" font-weight="800">ART (+)</text>
          <circle cx="335" cy="360" r="4" fill="#64748b" />
          <text x="330" y="378" fill="#94a3b8" font-size="8" font-weight="800">GND (-)</text>
        </g>

        <!-- 5. HC-SR04 Mesafe Sensörü -->
        <g id="comp-hcsr04" v-if="isComponentNeeded('HCSR04')">
          <rect x="75" y="420" width="160" height="135" rx="10" fill="#1e293b" opacity="0.6" stroke="#334155" />
          <text x="155" y="440" fill="#38bdf8" font-size="11" font-weight="800" text-anchor="middle">Mesafe Sensörü</text>
          <rect x="85" y="450" width="140" height="65" rx="6" fill="#0284c7" stroke="#0369a1" stroke-width="2" />
          <circle cx="115" cy="482" r="18" fill="#94a3b8" stroke="#475569" stroke-width="2" />
          <circle cx="115" cy="482" r="14" fill="#cbd5e1" />
          <circle cx="195" cy="482" r="18" fill="#94a3b8" stroke="#475569" stroke-width="2" />
          <circle cx="195" cy="482" r="14" fill="#cbd5e1" />
          <line x1="110" y1="515" x2="110" y2="535" stroke="#cbd5e1" stroke-width="2.5" />
          <circle cx="110" cy="535" r="4" fill="#ef4444" />
          <text x="100" y="552" fill="#fca5a5" font-size="8" font-weight="800">VCC</text>
          <line x1="135" y1="515" x2="135" y2="535" stroke="#cbd5e1" stroke-width="2.5" />
          <circle cx="135" cy="535" r="4" fill="#3b82f6" />
          <text x="125" y="552" fill="#93c5fd" font-size="8" font-weight="800">TRIG</text>
          <line x1="160" y1="515" x2="160" y2="535" stroke="#cbd5e1" stroke-width="2.5" />
          <circle cx="160" cy="535" r="4" fill="#10b981" />
          <text x="150" y="552" fill="#6ee7b7" font-size="8" font-weight="800">ECHO</text>
          <line x1="185" y1="515" x2="185" y2="535" stroke="#cbd5e1" stroke-width="2.5" />
          <circle cx="185" cy="535" r="4" fill="#475569" />
          <text x="178" y="552" fill="#94a3b8" font-size="8" font-weight="800">GND</text>
        </g>

        <!-- ============================================== -->
        <!-- KABLOLAR (BEZIER ARCS)                         -->
        <!-- ============================================== -->
        <!-- Önceki Kablolar -->
        <g id="bg-wires">
          <path
            v-for="(wire, idx) in backgroundWires"
            :key="'bg-wire-' + idx"
            :d="wire.pathD"
            fill="none"
            :stroke="wire.step.kablo_rengi"
            stroke-width="3"
            stroke-linecap="round"
            opacity="0.25"
          />
        </g>

        <!-- Aktif Kablo -->
        <g id="active-wire" v-if="activeWire">
          <path
            :d="activeWire.pathD"
            fill="none"
            :stroke="activeWire.step.kablo_rengi"
            stroke-width="5"
            stroke-linecap="round"
            class="wire-flowing"
          />

          <!-- Kaynak Pin Radar -->
          <circle :cx="activeWire.p1.x" :cy="activeWire.p1.y" r="12" fill="none" :stroke="activeWire.step.kablo_rengi" stroke-width="2" class="animate-ping" opacity="0.8" />
          <circle :cx="activeWire.p1.x" :cy="activeWire.p1.y" r="5" :fill="activeWire.step.kablo_rengi" stroke="#ffffff" stroke-width="2" />

          <!-- Hedef Pin Radar -->
          <circle :cx="activeWire.p2.x" :cy="activeWire.p2.y" r="12" fill="none" :stroke="activeWire.step.kablo_rengi" stroke-width="2" class="animate-ping" opacity="0.8" />
          <circle :cx="activeWire.p2.x" :cy="activeWire.p2.y" r="5" :fill="activeWire.step.kablo_rengi" stroke="#ffffff" stroke-width="2" />

          <!-- Etiketler -->
          <g>
            <rect :x="activeWire.p1.x - 26" :y="activeWire.p1.y - 24" width="52" height="16" rx="4" fill="#0f172a" stroke="#cbd5e1" stroke-width="1" />
            <text :x="activeWire.p1.x" :y="activeWire.p1.y - 13" fill="#ffffff" font-size="8" font-weight="900" text-anchor="middle">BURADAN</text>
          </g>
          <g>
            <rect :x="activeWire.p2.x - 26" :y="activeWire.p2.y - 24" width="52" height="16" rx="4" fill="#0f172a" stroke="#cbd5e1" stroke-width="1" />
            <text :x="activeWire.p2.x" :y="activeWire.p2.y - 13" fill="#ffffff" font-size="8" font-weight="900" text-anchor="middle">BURAYA 🎯</text>
          </g>
        </g>
      </svg>
    </div>
  </div>
</template>

<script setup lang="ts">
import { ref, computed } from 'vue';
import type { BaglantiAdimi } from '../types/project';
import { PIN_COORDINATES, getPinCoordinates } from '../constants/pinCoordinates';

const props = defineProps<{
  baglantiAdimlari: BaglantiAdimi[];
  gerekliParcalar: string[];
}>();

defineEmits<{
  (e: 'completed'): void;
}>();

const currentStepIndex = ref(0);
const showAllWires = ref(false);

const totalSteps = computed(() => props.baglantiAdimlari.length);
const currentStepNumber = computed(() => (totalSteps.value > 0 ? currentStepIndex.value + 1 : 0));
const currentStep = computed(() => props.baglantiAdimlari[currentStepIndex.value] || null);

const upperArduinoPins = computed(() => {
  const all = PIN_COORDINATES.ARDUINO_UNO.pins;
  const upperKeys = ['D0', 'D1', 'D2', 'D3', 'D4', 'D5', 'D6', 'D7', 'D8', 'D9', 'D10', 'D11', 'D12', 'D13', 'GND_TOP', 'AREF'];
  const res: Record<string, { x: number; y: number; label: string }> = {};
  upperKeys.forEach(k => {
    if (all[k]) res[k] = all[k];
  });
  return res;
});

const lowerArduinoPins = computed(() => {
  const all = PIN_COORDINATES.ARDUINO_UNO.pins;
  const lowerKeys = ['RESET', '3.3V', '5V', 'GND', 'VIN', 'A0', 'A1', 'A2', 'A3', 'A4', 'A5'];
  const res: Record<string, { x: number; y: number; label: string }> = {};
  lowerKeys.forEach(k => {
    if (all[k]) res[k] = all[k];
  });
  return res;
});

function isComponentNeeded(compId: string): boolean {
  if (!props.gerekliParcalar || props.gerekliParcalar.length === 0) return true;
  return props.gerekliParcalar.includes(compId) || props.baglantiAdimlari.some(
    step => step.kaynak.parca === compId || step.hedef.parca === compId
  );
}

function createBezierPath(p1: { x: number; y: number }, p2: { x: number; y: number }): string {
  const dx = p2.x - p1.x;
  const dy = p2.y - p1.y;
  const dist = Math.sqrt(dx * dx + dy * dy);
  const sag = Math.min(Math.max(dist * 0.25, 40), 110);
  const cx1 = p1.x + dx * 0.3;
  const cy1 = p1.y - sag;
  const cx2 = p1.x + dx * 0.7;
  const cy2 = p2.y - sag;
  return `M ${p1.x} ${p1.y} C ${cx1} ${cy1}, ${cx2} ${cy2}, ${p2.x} ${p2.y}`;
}

const activeWire = computed(() => {
  if (!currentStep.value) return null;
  const p1 = getPinCoordinates(currentStep.value.kaynak.parca, currentStep.value.kaynak.pin);
  const p2 = getPinCoordinates(currentStep.value.hedef.parca, currentStep.value.hedef.pin);
  if (!p1 || !p2) return null;
  return {
    step: currentStep.value,
    p1,
    p2,
    pathD: createBezierPath(p1, p2)
  };
});

const backgroundWires = computed(() => {
  const wires = [];
  const limit = showAllWires.value ? props.baglantiAdimlari.length : currentStepIndex.value;
  for (let i = 0; i < limit; i++) {
    const step = props.baglantiAdimlari[i];
    if (!step) continue;
    if (showAllWires.value && i === currentStepIndex.value) continue;
    const p1 = getPinCoordinates(step.kaynak.parca, step.kaynak.pin);
    const p2 = getPinCoordinates(step.hedef.parca, step.hedef.pin);
    if (p1 && p2) {
      wires.push({ step, p1, p2, pathD: createBezierPath(p1, p2) });
    }
  }
  return wires;
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

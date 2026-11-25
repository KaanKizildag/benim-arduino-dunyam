<template>
  <div class="w-full max-w-6xl mx-auto flex-1 flex flex-col gap-3.5 py-2.5 sm:py-4 px-2 sm:px-4 select-none">

    <!-- 1. ÜST BAR: DONANIM PORT SEÇİMİ + DEVREYİ ÇALIŞTIR (KARTA YÜKLE) BUTONU -->
    <div class="bg-white rounded-3xl p-3.5 sm:p-4 border-[3px] border-slate-900 shadow-[0_5px_0_#0f172a] flex flex-col lg:flex-row items-stretch lg:items-center justify-between gap-3">
      <!-- Sol: Port ve Kart Durumu -->
      <div class="flex flex-wrap items-center gap-3">
        <div
          :class="[
            'w-12 h-12 rounded-2xl border-2 border-slate-900 flex items-center justify-center text-2xl shrink-0 shadow-[0_3px_0_#0f172a]',
            hasRealHardwarePort ? 'bg-emerald-200' : 'bg-amber-200'
          ]"
        >
          {{ hasRealHardwarePort ? '🔌' : '🖥️' }}
        </div>
        <div class="min-w-0">
          <div class="flex items-center gap-1.5 flex-wrap">
            <h2 class="text-sm sm:text-base font-black text-slate-900">
              {{ hasRealHardwarePort ? 'Arduino Uno Bağlı ve Hazır' : 'Sanal Serial Simülatör & Port İzleyici' }}
            </h2>
            <span
              :class="[
                'px-2 py-0.5 rounded-lg border border-slate-900 text-[10px] font-black',
                hasRealHardwarePort ? 'bg-emerald-100 text-emerald-950' : 'bg-sky-100 text-sky-950'
              ]"
            >
              {{ activePortLabel }}
            </span>
          </div>
          <p class="text-[11px] font-bold text-slate-600 mt-0.5">
            Kodu Arduino'ya yükle ve aşağıda <strong>Serial Monitor</strong> veri akışını canlı izle!
          </p>
        </div>
      </div>

      <!-- Sağ: Port Seçici + Baud Rate + Karta Yükle Butonu -->
      <div class="flex flex-wrap items-center gap-2">
        <div class="flex items-center gap-1.5 bg-slate-100 p-1.5 rounded-2xl border-2 border-slate-900">
          <select
            v-model="selectedPort"
            class="px-2.5 py-1.5 rounded-xl border border-slate-900 font-black text-xs bg-white text-slate-900 outline-none cursor-pointer"
          >
            <option value="auto">Otomatik Port</option>
            <option v-for="p in availablePorts" :key="p.address" :value="p.address">
              {{ p.label }}
            </option>
          </select>

          <select
            v-model.number="baudRate"
            class="px-2 py-1.5 rounded-xl border border-slate-900 font-black text-xs bg-white text-slate-900 outline-none cursor-pointer"
            title="Serial Baud Rate"
          >
            <option :value="9600">9600 baud</option>
            <option :value="115200">115200 baud</option>
          </select>

          <button
            type="button"
            @click="$emit('refresh-ports')"
            class="px-2.5 py-1.5 rounded-xl border border-slate-900 font-black text-xs bg-white hover:bg-slate-50 text-slate-800 cursor-pointer transition"
            title="Portları Yenile"
          >
            🔄
          </button>
        </div>

        <button
          type="button"
          @click="triggerUpload"
          :disabled="isUploading"
          class="px-6 py-3 rounded-2xl bg-[#4ade80] hover:bg-[#22c55e] border-2 border-slate-900 shadow-[0_4px_0_#15803d] active:translate-y-1 active:shadow-none text-slate-950 font-black text-xs sm:text-sm transition cursor-pointer flex items-center justify-center gap-2 disabled:opacity-50"
        >
          <span v-if="isUploading" class="animate-spin text-base">⚙️</span>
          <span v-else class="text-base">🚀</span>
          <span>{{ isUploading ? 'Karta Yükleniyor...' : 'Devreyi Kurdum, Çalıştır!' }}</span>
        </button>
      </div>
    </div>

    <!-- 2. ANA İKİ SÜTUNLU ÇALIŞTIRMA EKRANI: SOLDA SERIAL MONITOR AKIŞI, SAĞDA AKILLI GÖRSELLEŞTİRİCİ -->
    <div :class="['grid gap-3.5 flex-1 min-h-[380px]', hasVisualizableData ? 'grid-cols-1 lg:grid-cols-12' : 'grid-cols-1']">
      
      <!-- SOL SÜTUN: CANLI SERIAL MONITOR TERMİNALİ (Her Zaman Görünür) -->
      <div
        :class="[
          'bg-slate-950 rounded-3xl border-[3px] border-slate-900 shadow-[0_6px_0_#0f172a] flex flex-col overflow-hidden',
          hasVisualizableData ? 'lg:col-span-7' : 'w-full'
        ]"
      >
        <!-- Terminal Üst Başlık Çubuğu -->
        <div class="px-4 py-2.5 bg-slate-900 border-b-2 border-slate-800 flex flex-wrap items-center justify-between gap-2">
          <div class="flex items-center gap-2">
            <span
              class="w-3 h-3 rounded-full border border-slate-950 transition-colors"
              :class="!isSocketConnected ? 'bg-slate-600' : isPaused ? 'bg-amber-400' : 'bg-emerald-400 animate-pulse shadow-[0_0_8px_#34d399]'"
              :title="isSocketConnected ? 'Seri port bağlantısı aktif' : 'Seri port bağlı değil'"
            ></span>
            <span class="text-xs font-black text-white tracking-wide">
              🖥️ SERIAL MONITOR ({{ baudRate }} baud)
            </span>
            <span
              class="px-2 py-0.5 rounded-md text-[10px] font-black tracking-wide"
              :class="isSocketConnected ? 'bg-emerald-950 border border-emerald-500 text-emerald-300' : 'bg-slate-800 border border-slate-700 text-slate-400'"
            >
              {{ isSocketConnected ? 'CANLI BAĞLI' : 'BAĞLI DEĞİL' }}
            </span>
            <span class="px-2 py-0.5 rounded-md bg-slate-800 border border-slate-700 text-[10px] font-bold text-cyan-300">
              {{ serialLines.length }} satır
            </span>
          </div>

          <!-- Terminal Kontrolleri -->
          <div class="flex items-center gap-1.5">
            <!-- Port Aç / Kapat Butonu -->
            <button
              type="button"
              @click="toggleSocketConnection"
              :class="[
                'px-2.5 py-1 rounded-lg border text-[10px] font-black cursor-pointer transition flex items-center gap-1 shadow-sm',
                isSocketConnected
                  ? 'bg-rose-500/20 hover:bg-rose-500/30 border-rose-400 text-rose-300'
                  : 'bg-emerald-500/20 hover:bg-emerald-500/30 border-emerald-400 text-emerald-300'
              ]"
              :title="isSocketConnected ? 'Seri port bağlantısını kes' : 'Seri porta bağlan'"
            >
              <span>{{ isSocketConnected ? '🔴 Portu Kapat' : '🔌 Portu Aç' }}</span>
            </button>
            <button
              type="button"
              @click="showTimestamps = !showTimestamps"
              :class="[
                'px-2 py-1 rounded-lg border text-[10px] font-black cursor-pointer transition',
                showTimestamps
                  ? 'bg-sky-500/20 border-sky-400 text-sky-300'
                  : 'bg-slate-800 border-slate-700 text-slate-400'
              ]"
            >
              🕒 Saat
            </button>
            <button
              type="button"
              @click="autoScroll = !autoScroll"
              :class="[
                'px-2 py-1 rounded-lg border text-[10px] font-black cursor-pointer transition',
                autoScroll
                  ? 'bg-emerald-500/20 border-emerald-400 text-emerald-300'
                  : 'bg-slate-800 border-slate-700 text-slate-400'
              ]"
            >
              ⬇️ Otomatik Kaydır
            </button>
            <button
              type="button"
              @click="isPaused = !isPaused"
              :class="[
                'px-2.5 py-1 rounded-lg border text-[10px] font-black cursor-pointer transition',
                isPaused
                  ? 'bg-amber-400 border-slate-900 text-slate-950'
                  : 'bg-slate-800 hover:bg-slate-700 border-slate-700 text-amber-300'
              ]"
            >
              {{ isPaused ? '▶️ Devam Et' : '⏸️ Duraklat' }}
            </button>
            <button
              type="button"
              @click="clearSerialMonitor"
              class="px-2.5 py-1 rounded-lg bg-slate-800 hover:bg-rose-950 border border-slate-700 hover:border-rose-500 text-[10px] font-black text-rose-300 cursor-pointer transition"
            >
              🗑️ Temizle
            </button>
          </div>
        </div>

        <!-- Serial Veri Akışı Satırları -->
        <div
          ref="terminalScrollRef"
          class="flex-1 p-3.5 overflow-y-auto font-mono text-xs flex flex-col gap-1.5 max-h-[340px] min-h-[260px] select-text"
        >
          <div
            v-if="serialLines.length === 0"
            class="flex-1 flex flex-col items-center justify-center text-slate-500 py-10 gap-2"
          >
            <span class="text-2xl">📡</span>
            <span class="font-bold text-xs">Serial port veri akışı bekleniyor...</span>
          </div>

          <div
            v-for="line in serialLines"
            :key="line.id"
            class="px-2.5 py-1.5 rounded-xl bg-slate-900/90 border border-slate-800/90 flex items-start justify-between gap-2 hover:border-slate-700 transition"
          >
            <div class="flex items-start gap-2 min-w-0 flex-1">
              <span
                v-if="showTimestamps"
                class="text-[10px] text-slate-500 font-bold shrink-0 pt-0.5"
              >
                [{{ line.timestamp }}]
              </span>
              <span
                :class="[
                  'break-all leading-relaxed',
                  line.source === 'system'
                    ? 'text-amber-300 font-bold'
                    : line.source === 'user'
                    ? 'text-sky-300 font-bold'
                    : 'text-emerald-300'
                ]"
              >
                {{ line.text }}
              </span>
            </div>

            <!-- Satırdan Ayrıştırılan Sayısal Kanal Rozetleri -->
            <div v-if="Object.keys(line.channels).length > 0" class="flex flex-wrap items-center gap-1 shrink-0">
              <span
                v-for="(val, key) in line.channels"
                :key="key"
                class="px-1.5 py-0.5 rounded bg-slate-800 border border-emerald-500/40 text-[10px] font-black text-emerald-300"
              >
                {{ key }}={{ val }}
              </span>
            </div>
          </div>
        </div>

        <!-- Alt: Serial Porta Veri Gönderme / Test Değeri Girme Çubuğu -->
        <div class="p-2.5 bg-slate-900 border-t-2 border-slate-800 flex items-center gap-2">
          <input
            v-model="manualInput"
            type="text"
            placeholder="Serial porta veri gönder veya test satırı yaz (örn: IsikSol: 750, IsikSag: 320)..."
            class="flex-1 px-3 py-1.5 rounded-xl bg-slate-950 border border-slate-700 text-xs font-mono text-white placeholder:text-slate-500 outline-none focus:border-sky-400"
            @keydown.enter.prevent="sendManualSerialLine"
          />
          <button
            type="button"
            @click="sendManualSerialLine"
            class="px-3.5 py-1.5 rounded-xl bg-sky-400 hover:bg-sky-300 text-slate-950 font-black text-xs border border-slate-950 cursor-pointer shrink-0 transition"
          >
            Gönder ↵
          </button>
        </div>
      </div>

      <!-- SAĞ SÜTUN: AKILLI VERİ GÖRSELLEŞTİRİCİ (Yalnızca Görselleştirilebilir Kanal / Sensör Varsa Açılır) -->
      <div
        v-if="hasVisualizableData"
        class="lg:col-span-5 bg-white rounded-3xl p-4 border-[3px] border-slate-900 shadow-[0_6px_0_#0f172a] flex flex-col justify-between gap-3"
      >
        <!-- Başlık -->
        <div class="flex items-center justify-between border-b-2 border-slate-100 pb-2">
          <div class="flex items-center gap-2">
            <span class="text-lg">📊</span>
            <div>
              <h3 class="text-xs sm:text-sm font-black text-slate-900 leading-tight">
                Canlı Sensör & Çıkış Görselleştirici
              </h3>
              <span class="text-[10px] font-bold text-slate-500">
                Serial porttan okunan veriler otomatik grafiğe dönüştürülür
              </span>
            </div>
          </div>
          <span class="px-2 py-0.5 rounded-lg bg-emerald-100 border border-slate-900 text-[10px] font-black text-emerald-950">
            {{ channelCards.length }} Kanal
          </span>
        </div>

        <!-- Canlı Kanal Kartları (LDR1, LDR2, Mesafe, Servo Açısı vb.) -->
        <div class="flex flex-col gap-2.5 overflow-y-auto max-h-[210px] pr-0.5">
          <div
            v-for="ch in channelCards"
            :key="ch.name"
            class="p-3 rounded-2xl bg-slate-50 border-2 border-slate-900 flex flex-col gap-1.5"
          >
            <div class="flex items-center justify-between">
              <div class="flex items-center gap-1.5">
                <span class="text-base">{{ ch.icon }}</span>
                <span class="text-xs font-black text-slate-900">{{ ch.label }}</span>
                <span v-if="ch.pinBadge" class="px-1.5 py-0.2 rounded bg-sky-100 border border-slate-900 text-[9px] font-black text-sky-950">
                  {{ ch.pinBadge }}
                </span>
              </div>
              <div class="text-sm font-black text-slate-950 font-mono">
                {{ ch.currentValue }} <span class="text-[10px] font-bold text-slate-500">{{ ch.unit }}</span>
              </div>
            </div>

            <!-- Canlı Bar -->
            <div class="w-full h-3 rounded-full bg-slate-200 border border-slate-900 overflow-hidden p-0.5">
              <div
                class="h-full rounded-full transition-all duration-300"
                :style="{ width: `${ch.percent}%`, backgroundColor: ch.color }"
              ></div>
            </div>

            <!-- İnteraktif Simülasyon Kaydırıcısı (Fiziksel Kart Takılı Değilken Çocuğun Sensörü Test Etmesi İçin) -->
            <div v-if="!hasRealHardwarePort" class="flex items-center justify-between gap-2 pt-0.5">
              <span class="text-[9px] font-bold text-slate-500">Slayder ile Test Et:</span>
              <input
                type="range"
                :min="ch.min"
                :max="ch.max"
                :value="ch.currentValue"
                @input="onSliderAdjust(ch.name, Number(($event.target as HTMLInputElement).value))"
                class="w-36 accent-sky-600 cursor-pointer h-1.5"
              />
            </div>
          </div>
        </div>

        <!-- Canlı Zaman Grafiği (SVG Sparkline /Serial Plotter) -->
        <div class="bg-slate-900 rounded-2xl p-3 border-2 border-slate-900 flex flex-col gap-1.5">
          <div class="flex items-center justify-between text-[10px] font-black text-slate-300">
            <span>📈 SERIAL PLOTTER (SON ÖLÇÜMLER)</span>
            <div class="flex items-center gap-2">
              <span
                v-for="ch in channelCards"
                :key="ch.name"
                class="flex items-center gap-1"
              >
                <span class="w-2 h-2 rounded-full inline-block" :style="{ backgroundColor: ch.color }"></span>
                <span>{{ ch.label }}</span>
              </span>
            </div>
          </div>

          <svg class="w-full h-20 overflow-visible" viewBox="0 0 300 70" preserveAspectRatio="none">
            <line x1="0" y1="15" x2="300" y2="15" stroke="#334155" stroke-width="0.6" stroke-dasharray="3,3" />
            <line x1="0" y1="35" x2="300" y2="35" stroke="#334155" stroke-width="0.6" stroke-dasharray="3,3" />
            <line x1="0" y1="55" x2="300" y2="55" stroke="#334155" stroke-width="0.6" stroke-dasharray="3,3" />

            <polyline
              v-for="ch in channelCards"
              :key="ch.name"
              fill="none"
              :stroke="ch.color"
              stroke-width="2.5"
              stroke-linecap="round"
              stroke-linejoin="round"
              :points="ch.sparklinePoints"
            />
          </svg>
        </div>
      </div>

    </div>

    <!-- 3. ALT GERİ DÖNÜŞ VE DURUM ÇUBUĞU -->
    <div class="flex items-center justify-between gap-3 pt-1">
      <button
        type="button"
        @click="$emit('prev-page')"
        class="px-4 py-2 rounded-2xl border-2 border-slate-900 bg-white hover:bg-slate-50 text-slate-800 font-black text-xs transition cursor-pointer shadow-[0_2px_0_#0f172a] active:translate-y-0.5"
      >
        ◀ 3. Nasıl Çalışacak'a Dön
      </button>

      <div v-if="statusMessage" class="px-3.5 py-1.5 rounded-xl bg-amber-100 border-2 border-slate-900 text-xs font-black text-slate-900">
        {{ statusMessage }}
      </div>
    </div>

  </div>
</template>

<script setup lang="ts">
import { ref, computed, watch, nextTick, onMounted, onUnmounted } from 'vue';
import type { PortInfo, CircuitNetlist, UploadResult } from '../types/project';

const props = defineProps<{
  isUploading: boolean;
  uploadResult?: UploadResult | null;
  availablePorts: PortInfo[];
  arduinoCode: string;
  projectName?: string;
  netlist?: CircuitNetlist;
}>();

const emit = defineEmits<{
  (e: 'prev-page'): void;
  (e: 'refresh-ports'): void;
  (e: 'upload', port: string): void;
}>();

interface SerialLineItem {
  id: number;
  timestamp: string;
  text: string;
  source: 'hardware' | 'simulated' | 'system' | 'user';
  channels: Record<string, number>;
}

interface ChannelMeta {
  name: string;
  label: string;
  icon: string;
  pinBadge?: string;
  min: number;
  max: number;
  unit: string;
  color: string;
}

const COLORS = ['#38bdf8', '#4ade80', '#f59e0b', '#f43f5e', '#a855f7'];

const selectedPort = ref('auto');
const baudRate = ref(9600);
const statusMessage = ref('');
const isPaused = ref(false);
const autoScroll = ref(true);
const showTimestamps = ref(true);
const isSocketConnected = ref(false);
const manualInput = ref('');
const terminalScrollRef = ref<HTMLElement | null>(null);

const serialLines = ref<SerialLineItem[]>([]);
const channelHistory = ref<Record<string, number[]>>({});
const channelValues = ref<Record<string, number>>({});
const manualOverrides = ref<Record<string, number>>({});

let lineCounter = 1;
let eventSource: EventSource | null = null;
let simInterval: ReturnType<typeof setInterval> | null = null;

const hasRealHardwarePort = computed(() => {
  return (props.availablePorts || []).some(
    p => p.address !== 'SIMULATED_PORT' && p.address !== 'auto' && p.source !== 'simulated'
  );
});

const activePortLabel = computed(() => {
  if (!hasRealHardwarePort.value) return 'Simülasyon Akışı Aktif';
  const match = props.availablePorts.find(p => p.address === selectedPort.value);
  return match ? `${match.board_name} (${match.address})` : 'Donanım Portu Hazır';
});

/**
 * Devredeki (netlist) ve Arduino kodundaki gerçek bileşenlere göre
 * beklenen Serial Monitor kanallarını çıkarır.
 */
const expectedChannels = computed<ChannelMeta[]>(() => {
  const comps = props.netlist?.components || [];
  const conns = props.netlist?.connections || [];
  const metas: ChannelMeta[] = [];

  const findUnoPin = (compId: string): string | undefined => {
    for (const c of conns) {
      if (c.from.startsWith(`${compId}.`) && c.to.startsWith('uno.')) return c.to.replace('uno.', '');
      if (c.to.startsWith(`${compId}.`) && c.from.startsWith('uno.')) return c.from.replace('uno.', '');
    }
    return undefined;
  };

  let colorIdx = 0;
  for (const comp of comps) {
    if (comp.type === 'wokwi-resistor') continue;
    const pinBadge = findUnoPin(comp.id);
    const color = COLORS[colorIdx % COLORS.length]!;
    colorIdx++;

    if (comp.type === 'wokwi-photoresistor' || comp.type === 'wokwi-photoresistor-sensor') {
      metas.push({
        name: comp.id.toUpperCase(),
        label: comp.label || comp.id,
        icon: '☀️',
        pinBadge,
        min: 0,
        max: 1023,
        unit: '/ 1023',
        color
      });
    } else if (comp.type === 'wokwi-hc-sr04') {
      metas.push({
        name: 'MESAFE',
        label: comp.label || 'Mesafe (HC-SR04)',
        icon: '📏',
        pinBadge,
        min: 2,
        max: 200,
        unit: 'cm',
        color
      });
    } else if (comp.type === 'wokwi-potentiometer') {
      metas.push({
        name: comp.id.toUpperCase(),
        label: comp.label || 'Potansiyometre',
        icon: '🎚️',
        pinBadge,
        min: 0,
        max: 1023,
        unit: '/ 1023',
        color
      });
    } else if (comp.type === 'wokwi-pushbutton') {
      metas.push({
        name: comp.id.toUpperCase(),
        label: comp.label || 'Buton Durumu',
        icon: '🔘',
        pinBadge,
        min: 0,
        max: 1,
        unit: '(0/1)',
        color
      });
    } else if (comp.type === 'wokwi-servo') {
      metas.push({
        name: 'SERVO_ACI',
        label: comp.label || 'Servo Motor Açısı',
        icon: '🦾',
        pinBadge,
        min: 0,
        max: 180,
        unit: '°',
        color
      });
    }
  }

  return metas;
});

/**
 * Bir Serial Monitor satırındaki `Key: Value`, `Key = Value` veya tekil sayıları ayrıştırır.
 */
function parseChannelsFromText(lineText: string): Record<string, number> {
  const result: Record<string, number> = {};
  const pairRegex = /([A-Za-z0-9_ğüşıöçĞÜŞİÖÇ]+)\s*[:=]\s*(-?\d+(?:\.\d+)?)/g;
  let match: RegExpExecArray | null;
  while ((match = pairRegex.exec(lineText)) !== null) {
    if (match[1] && match[2] !== undefined) {
      result[match[1]] = Number(match[2]);
    }
  }

  if (Object.keys(result).length === 0) {
    const trimmed = lineText.trim();
    if (/^-?\d+(?:\.\d+)?$/.test(trimmed)) {
      result['Deger'] = Number(trimmed);
    }
  }
  return result;
}

function appendSerialLine(
  text: string,
  source: SerialLineItem['source'] = 'simulated',
  explicitChannels?: Record<string, number>,
  customTimestamp?: string
) {
  if (isPaused.value && source !== 'user' && source !== 'system') return;

  const parsed = explicitChannels && Object.keys(explicitChannels).length > 0
    ? explicitChannels
    : parseChannelsFromText(text);

  for (const [k, v] of Object.entries(parsed)) {
    channelValues.value[k] = v;
    if (!channelHistory.value[k]) {
      channelHistory.value[k] = [];
    }
    channelHistory.value[k]!.push(v);
    if (channelHistory.value[k]!.length > 28) {
      channelHistory.value[k]!.shift();
    }
  }

  const nowStr = customTimestamp || new Date().toLocaleTimeString('tr-TR', { hour12: false });
  serialLines.value.push({
    id: lineCounter++,
    timestamp: nowStr,
    text,
    source,
    channels: parsed
  });

  if (serialLines.value.length > 150) {
    serialLines.value.shift();
  }

  if (autoScroll.value) {
    void nextTick(() => {
      if (terminalScrollRef.value) {
        terminalScrollRef.value.scrollTop = terminalScrollRef.value.scrollHeight;
      }
    });
  }
}

const channelCards = computed(() => {
  const activeKeys = Object.keys(channelValues.value);
  if (activeKeys.length === 0) return [];

  return activeKeys.slice(0, 5).map((key, idx) => {
    const meta = expectedChannels.value.find(
      m => m.name.toLowerCase() === key.toLowerCase() || m.label.toLowerCase().includes(key.toLowerCase())
    ) || expectedChannels.value[idx];

    const min = meta?.min ?? 0;
    const max = meta?.max ?? (key.toLowerCase().includes('aci') || key.toLowerCase().includes('servo') ? 180 : 1023);
    const val = channelValues.value[key] ?? 0;
    const pct = Math.min(100, Math.max(2, Math.round(((val - min) / Math.max(1, max - min)) * 100)));
    const color = meta?.color || COLORS[idx % COLORS.length]!;
    const hist = channelHistory.value[key] || [val];

    // SVG Sparkline noktaları (300x70)
    const pts = hist
      .map((v, i) => {
        const x = hist.length <= 1 ? 150 : Math.round((i / (hist.length - 1)) * 292) + 4;
        const norm = Math.min(1, Math.max(0, (v - min) / Math.max(1, max - min)));
        const y = Math.round(62 - norm * 52);
        return `${x},${y}`;
      })
      .join(' ');

    return {
      name: key,
      label: meta?.label || key,
      icon: meta?.icon || '📡',
      pinBadge: meta?.pinBadge,
      currentValue: val,
      min,
      max,
      unit: meta?.unit || '',
      percent: pct,
      color,
      sparklinePoints: pts
    };
  });
});

const hasVisualizableData = computed(() => {
  return channelCards.value.length > 0;
});

function onSliderAdjust(channelName: string, newVal: number) {
  manualOverrides.value[channelName] = newVal;
  channelValues.value[channelName] = newVal;

  // Eğer çift LDR + Servo günebakan projesi ise servo açısını da anında güncelle
  const keys = Object.keys(channelValues.value);
  const ldrKeys = keys.filter(k => k.toLowerCase().includes('ldr'));
  if (ldrKeys.length >= 2 && 'SERVO_ACI' in channelValues.value) {
    const v1 = channelValues.value[ldrKeys[0]!] ?? 500;
    const v2 = channelValues.value[ldrKeys[1]!] ?? 500;
    const servoAngle = v1 > v2 + 30 ? 135 : v2 > v1 + 30 ? 45 : 90;
    manualOverrides.value['SERVO_ACI'] = servoAngle;
    channelValues.value['SERVO_ACI'] = servoAngle;
  }

  const summary = Object.entries(channelValues.value)
    .map(([k, v]) => `${k}: ${v}`)
    .join(' | ');
  appendSerialLine(summary, 'simulated', { ...channelValues.value });
}

let activeSocket: WebSocket | null = null;

function sendManualSerialLine() {
  const txt = manualInput.value.trim();
  if (!txt) return;

  if (activeSocket && activeSocket.readyState === WebSocket.OPEN) {
    activeSocket.send(txt);
  }
  appendSerialLine(`> ${txt}`, 'user');
  manualInput.value = '';
}

function clearSerialMonitor() {
  serialLines.value = [];
}

function toggleSocketConnection() {
  if (isSocketConnected.value && activeSocket) {
    activeSocket.close();
    activeSocket = null;
    isSocketConnected.value = false;
    appendSerialLine('[BİLGİ] Seri port bağlantısı kullanıcı tarafından kapatıldı.', 'system');
  } else {
    connectSerialStream();
  }
}

function triggerUpload() {
  if (activeSocket) {
    activeSocket.close();
    activeSocket = null;
  }
  isSocketConnected.value = false;
  if (eventSource) {
    eventSource.close();
    eventSource = null;
  }
  statusMessage.value = 'Arduino Uno kartına kod derlenip gönderiliyor...';
  appendSerialLine(`[DERLEME & YÜKLEME] "${props.projectName || 'Arduino Projem'}" derleniyor ve ${selectedPort.value} portuna yükleniyor...`, 'system');
  emit('upload', selectedPort.value);
}

function connectSerialStream() {
  if (activeSocket) {
    activeSocket.close();
    activeSocket = null;
  }
  isSocketConnected.value = false;
  if (eventSource) {
    eventSource.close();
    eventSource = null;
  }
  if (simInterval) {
    clearInterval(simInterval);
    simInterval = null;
  }

  // Gerçek donanım portu (COM* veya /dev/tty*) seçildiyse doğrudan WebSocket köprüsüne bağlan
  if (hasRealHardwarePort.value) {
    try {
      const loc = window.location;
      const wsProto = loc.protocol === 'https:' ? 'wss:' : 'ws:';
      // Vite proxy (/ws) üzerinden bağlan veya doğrudan 127.0.0.1:8001'i hedefle (IPv6 localhost çakışmasını önler)
      const wsUrl = loc.port === '5173'
        ? `${wsProto}//${loc.host}/ws/serial?port=${encodeURIComponent(selectedPort.value)}&baudrate=${baudRate.value}`
        : `${wsProto}//127.0.0.1:8001/ws/serial?port=${encodeURIComponent(selectedPort.value)}&baudrate=${baudRate.value}`;

      let triedDirect = false;

      const tryConnect = (targetUrl: string) => {
        appendSerialLine(`[WEBSOCKET] ${selectedPort.value} (${baudRate.value} baud) bağlantısı açılıyor...`, 'system');
        activeSocket = new WebSocket(targetUrl);

        activeSocket.onopen = () => {
          isSocketConnected.value = true;
          appendSerialLine(`[BAĞLANDI] ${selectedPort.value} canlı WebSocket köprüsü aktif. Arduino'dan gelen gerçek veriler bekleniyor...`, 'system');
        };

        activeSocket.onmessage = (event) => {
          try {
            const data = JSON.parse(event.data);
            if (data.type === 'connected') {
              isSocketConnected.value = true;
              appendSerialLine(data.text || `[PORT AÇILDI] ${data.port}`, 'system');
            } else if (data.type === 'data') {
              appendSerialLine(data.text, 'hardware', undefined, data.timestamp);
            } else if (data.type === 'error') {
              isSocketConnected.value = false;
              appendSerialLine(`[PORT UYARISI] ${data.message || data.text}`, 'system');
            }
          } catch {
            if (event.data) {
              appendSerialLine(String(event.data), 'hardware');
            }
          }
        };

        activeSocket.onerror = () => {
          if (!triedDirect && loc.port === '5173') {
            triedDirect = true;
            // Vite proxy üzerinden açılamadıysa doğrudan 127.0.0.1:8001 köprüsünü dene
            const directUrl = `${wsProto}//127.0.0.1:8001/ws/serial?port=${encodeURIComponent(selectedPort.value)}&baudrate=${baudRate.value}`;
            tryConnect(directUrl);
            return;
          }
          isSocketConnected.value = false;
          appendSerialLine(`[PORT BAĞLANTI HATASI] ${selectedPort.value} WebSocket köprüsüne bağlanılamadı. Backend'in 'python -m uvicorn main:app --host 0.0.0.0 --port 8001 --reload' ile çalıştığından emin olun.`, 'system');
        };

        activeSocket.onclose = (event) => {
          isSocketConnected.value = false;
          if (event.code !== 1000 && event.code !== 1005 && !triedDirect) {
            appendSerialLine(`[PORT KAPANDI] Bağlantı kapandı (Kod: ${event.code}). Tekrar bağlanmak için yukarıdaki "🔌 Portu Aç" butonuna basabilirsiniz.`, 'system');
          }
        };
      };

      tryConnect(wsUrl);
      return;
    } catch (e) {
      isSocketConnected.value = false;
      appendSerialLine(`[HATA] WebSocket başlatılamadı: ${e}`, 'system');
      return;
    }
  }

  // Donanım portu seçilmediğinde bilgi ver
  appendSerialLine(`[BİLGİ] Fiziksel Arduino portu seçilmedi (${selectedPort.value}). Gerçek kartınız için yukarıdaki menüden COM portunuzu seçin.`, 'system');
}

watch([selectedPort, baudRate], () => {
  connectSerialStream();
});

watch(
  () => props.isUploading,
  (newVal, oldVal) => {
    if (oldVal === true && newVal === false) {
      // Karta kod yüklendiğinde Arduino yeniden başlar (reboot); Windows USB-seri sürücüsünün portu bırakması için 2.2 sn sonra bağlan
      setTimeout(() => {
        connectSerialStream();
      }, 2200);
    }
  }
);

watch(
  () => props.uploadResult,
  (res) => {
    if (!res) return;
    if (res.success) {
      appendSerialLine(`[YÜKLEME BAŞARILI] ${res.message}`, 'system');
      if (res.compiler_output) {
        appendSerialLine(`[DERLEYİCİ] ${res.compiler_output.trim()}`, 'system');
      }
      if (res.uploader_output) {
        appendSerialLine(`[AVRDUDE] ${res.uploader_output.trim()}`, 'system');
      }
    } else {
      appendSerialLine(`[YÜKLEME BAŞARISIZ] ${res.message}`, 'system');
      if (res.error) {
        appendSerialLine(`[HATA AYRINTISI] ${res.error.trim()}`, 'system');
      }
      if (res.compiler_output) {
        appendSerialLine(`[DERLEYİCİ] ${res.compiler_output.trim()}`, 'system');
      }
    }
  }
);

onMounted(() => {
  connectSerialStream();
});

onUnmounted(() => {
  if (activeSocket) {
    activeSocket.close();
    activeSocket = null;
  }
  isSocketConnected.value = false;
  if (eventSource) eventSource.close();
  if (simInterval) clearInterval(simInterval);
});
</script>

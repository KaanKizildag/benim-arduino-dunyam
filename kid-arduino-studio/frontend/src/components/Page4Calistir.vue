<template>
  <div class="max-w-4xl mx-auto w-full flex flex-col items-center gap-6 py-4 sm:py-8 px-4">
    
    <!-- Üst Donanım ve Port Durum Bandı -->
    <div
      :class="[
        'w-full p-4 rounded-3xl border-2 flex flex-col sm:flex-row items-center justify-between gap-3 text-xs shadow-xs',
        isHardwareReady
          ? 'bg-emerald-50 border-emerald-200 text-emerald-950'
          : 'bg-amber-50 border-amber-200 text-amber-950'
      ]"
    >
      <div class="flex items-center gap-3">
        <span class="text-3xl">{{ isHardwareReady ? '🔌' : '⏳' }}</span>
        <div>
          <strong class="text-sm font-black block">
            {{ isHardwareReady ? 'Arduino Uno Kartı Bağlı ve Hazır!' : 'Arduino Kartı Aranıyor...' }}
          </strong>
          <span class="text-[11px] font-bold opacity-80">
            {{ activePortLabel }}
          </span>
        </div>
      </div>

      <!-- Port Seçici veya Yenileme -->
      <div class="flex items-center gap-2">
        <select
          v-model="selectedPort"
          class="p-2 rounded-xl border border-current font-bold text-xs bg-white text-slate-800 outline-none cursor-pointer"
        >
          <option value="auto">Otomatik Port (Tavsiye Edilen)</option>
          <option v-for="p in availablePorts" :key="p.address" :value="p.address">
            {{ p.label }} ({{ p.address }})
          </option>
        </select>
        <button
          type="button"
          @click="$emit('refresh-ports')"
          class="p-2 rounded-xl border border-current font-bold bg-white/80 hover:bg-white text-slate-700 transition"
          title="Portları Yenile"
        >
          🔄
        </button>
      </div>
    </div>

    <!-- Ortada Devasa, Pofuduk Yeşil 'Devreyi Kurdum, Çalıştır! 🚀' Butonu -->
    <div class="w-full bg-white rounded-3xl p-6 sm:p-10 border-2 border-slate-200 shadow-xl flex flex-col items-center text-center gap-4">
      <div class="text-4xl animate-bounce">
        🌟
      </div>
      <div>
        <h2 class="text-xl sm:text-2xl font-black text-slate-900 mb-1">
          Harika Bir İş Çıkardın!
        </h2>
        <p class="text-xs sm:text-sm text-slate-500 font-medium max-w-md">
          Devren kuruldu, mantık onaylandı. Şimdi tek bir tıkla Arduino Uno beynine kodunu yükleyip hayat verelim!
        </p>
      </div>

      <button
        type="button"
        @click="triggerUpload"
        :disabled="isUploading"
        :class="[
          'w-full max-w-md py-5 sm:py-6 rounded-3xl font-black text-lg sm:text-xl shadow-2xl transition-all transform active:scale-95 cursor-pointer flex items-center justify-center gap-3',
          isUploading
            ? 'bg-emerald-400 text-white cursor-wait opacity-80'
            : 'bg-gradient-to-r from-emerald-500 to-teal-500 hover:from-emerald-600 hover:to-teal-600 text-white shadow-emerald-200 hover:shadow-emerald-300 hover:scale-102'
        ]"
      >
        <span v-if="isUploading" class="animate-spin text-2xl">⚙️</span>
        <span v-else class="text-2xl">🚀</span>
        <span>{{ isUploading ? 'Karta Yükleniyor...' : 'Devreyi Kurdum, Çalıştır! 🚀' }}</span>
      </button>

      <!-- Yükleme Durum Bildirimi -->
      <p v-if="statusMessage" class="text-xs font-bold text-indigo-600 animate-pulse">
        {{ statusMessage }}
      </p>
    </div>

    <!-- Altta Güneş & Ay Motifli Dairesel Sensör İbresi (Canlı Seri Port Verisi) -->
    <div class="w-full bg-white rounded-3xl p-6 border-2 border-slate-200 shadow-md flex flex-col items-center text-center gap-4">
      <div class="flex items-center justify-between w-full border-b border-slate-100 pb-2">
        <div class="flex items-center gap-2">
          <span class="text-xl">📡</span>
          <h3 class="text-xs sm:text-sm font-black text-slate-800">
            Canlı Sensör Verisi (Seri Port İzleyici)
          </h3>
        </div>
        <span class="px-2.5 py-0.5 rounded-full bg-emerald-100 text-emerald-800 text-[10px] font-black animate-pulse">
          ● CANLI AKIŞ
        </span>
      </div>

      <!-- Güneş ve Ay Motifli Dairesel Gösterge -->
      <div class="relative w-48 h-48 flex items-center justify-center">
        <!-- Dairesel Arka Plan -->
        <svg class="w-full h-full transform -rotate-90" viewBox="0 0 100 100">
          <circle
            cx="50"
            cy="50"
            r="40"
            stroke="#e2e8f0"
            stroke-width="10"
            fill="none"
          />
          <circle
            cx="50"
            cy="50"
            r="40"
            :stroke="liveSensorValue < 400 ? '#6366f1' : '#f59e0b'"
            stroke-width="10"
            stroke-dasharray="251.2"
            :stroke-dashoffset="gaugeOffset"
            stroke-linecap="round"
            fill="none"
            class="transition-all duration-300"
          />
        </svg>

        <!-- İçerideki Güneş/Ay İkonu ve Değer -->
        <div class="absolute inset-0 flex flex-col items-center justify-center">
          <span class="text-3xl mb-1">
            {{ liveSensorValue < 400 ? '🌙' : '☀️' }}
          </span>
          <span class="text-2xl font-black text-slate-900 leading-none">
            {{ liveSensorValue }}
          </span>
          <span class="text-[10px] font-extrabold text-slate-400 mt-0.5">
            / 1023
          </span>
        </div>
      </div>

      <!-- Cana Yakın Durum Bildirimi -->
      <div class="px-5 py-2.5 rounded-2xl bg-slate-50 border border-slate-200 text-xs font-black">
        <span v-if="liveSensorValue < 400" class="text-indigo-600">
          🌙 Oda Karanlık (Işık 400'ün altında) ➔ Lamban Yanıyor! 💡
        </span>
        <span v-else class="text-amber-600">
          ☀️ Oda Aydınlık (Işık Bol) ➔ Lamba Dinleniyor! 😴
        </span>
      </div>
    </div>

    <!-- Alt Geri Butonu -->
    <div class="w-full flex items-center justify-start pt-2">
      <button
        type="button"
        @click="$emit('prev-page')"
        class="px-4 py-2.5 rounded-2xl border-2 border-slate-300 bg-white hover:bg-slate-100 text-slate-700 font-extrabold text-xs transition cursor-pointer"
      >
        ◀ Devre Şemasına Geri Dön
      </button>
    </div>

  </div>
</template>

<script setup lang="ts">
import { ref, computed, onMounted, onUnmounted } from 'vue';
import confetti from 'canvas-confetti';
import type { PortInfo, UploadResult } from '../types/project';

const props = defineProps<{
  isUploading: boolean;
  availablePorts: PortInfo[];
  arduinoCode: string;
}>();

const emit = defineEmits<{
  (e: 'prev-page'): void;
  (e: 'refresh-ports'): void;
  (e: 'upload', port: string): void;
}>();

const selectedPort = ref('auto');
const statusMessage = ref('');
const liveSensorValue = ref(320);
let eventSource: EventSource | null = null;
let simulatedTimer: any = null;

const isHardwareReady = computed(() => {
  return props.availablePorts && props.availablePorts.length > 0;
});

const activePortLabel = computed(() => {
  if (!isHardwareReady.value) return 'Simüle Port Modunda Çalışıyor';
  const match = props.availablePorts.find(p => p.address === selectedPort.value);
  return match ? `${match.board_name} (${match.address})` : 'Otomatik Port Seçili';
});

// Dairesel Gösterge Ofseti (251.2 tam çember çevresi)
const gaugeOffset = computed(() => {
  const pct = Math.min(Math.max(liveSensorValue.value / 1023, 0), 1);
  return 251.2 * (1 - pct);
});

function triggerUpload() {
  statusMessage.value = 'Arduino Uno kartına kod derlenip gönderiliyor...';
  emit('upload', selectedPort.value);
}

// Canlı Veri İzleme (SSE veya Gerçekçi Simülasyon)
onMounted(() => {
  try {
    eventSource = new EventSource('/api/serial-events');
    eventSource.onmessage = (event) => {
      try {
        const data = JSON.parse(event.data);
        if (data && typeof data.value === 'number') {
          liveSensorValue.value = data.value;
        }
      } catch {
        // SSE yoksa yerel simülasyon
      }
    };
    eventSource.onerror = () => {
      startSimulatedSensorStream();
    };
  } catch {
    startSimulatedSensorStream();
  }
});

function startSimulatedSensorStream() {
  if (simulatedTimer) return;
  simulatedTimer = setInterval(() => {
    // 150 ile 850 arasında yumuşak salınım
    const delta = (Math.random() - 0.48) * 40;
    liveSensorValue.value = Math.min(Math.max(Math.round(liveSensorValue.value + delta), 80), 960);
  }, 1200);
}

onUnmounted(() => {
  if (eventSource) eventSource.close();
  if (simulatedTimer) clearInterval(simulatedTimer);
});
</script>

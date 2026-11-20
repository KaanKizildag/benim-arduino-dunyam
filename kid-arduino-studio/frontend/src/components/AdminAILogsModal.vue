<template>
  <div
    v-if="isOpen"
    class="fixed inset-0 z-50 flex items-center justify-center p-2 sm:p-4 bg-slate-950/75 backdrop-blur-xs select-text"
    @click.self="$emit('close')"
  >
    <div class="bg-slate-900 border-[3px] border-slate-700 rounded-3xl w-full max-w-6xl h-[88vh] shadow-2xl flex flex-col overflow-hidden text-slate-100">
      
      <!-- 1. ÜST BAR: ADMIN AI İSTEK & CEVAP İZLEYİCİ -->
      <div class="bg-slate-950 px-5 py-3.5 border-b border-slate-800 flex flex-wrap items-center justify-between gap-3 shrink-0">
        <div class="flex items-center gap-3">
          <div class="w-10 h-10 rounded-2xl bg-indigo-600 border border-indigo-400 flex items-center justify-center text-xl shadow-md">
            🛠️
          </div>
          <div>
            <div class="flex items-center gap-2">
              <h2 class="text-base sm:text-lg font-black text-white">
                Admin Modu • Yapay Zeka İstek & Cevap İzleyici (AI Inspector)
              </h2>
              <span class="px-2 py-0.5 rounded-full bg-amber-500/20 border border-amber-400/50 text-amber-300 text-[10px] font-black">
                {{ logs.length }} Kayıt
              </span>
            </div>
            <p class="text-xs text-slate-400 font-medium">
              1. Aşama (Kablolama/Wiring) ve 2. Aşama (Akış & Arduino Kodu) AI çağrılarında gönderilen tam promptları ve dönen ham yanıtları inceleyin.
            </p>
          </div>
        </div>

        <div class="flex items-center gap-2">
          <button
            type="button"
            @click="$emit('refresh')"
            class="px-3 py-1.5 rounded-xl bg-slate-800 hover:bg-slate-700 border border-slate-600 text-xs font-black text-slate-200 transition cursor-pointer flex items-center gap-1.5"
          >
            <span>🔄</span>
            <span>Yenile</span>
          </button>

          <button
            type="button"
            @click="$emit('clear')"
            :disabled="logs.length === 0"
            class="px-3 py-1.5 rounded-xl bg-rose-950/80 hover:bg-rose-900 border border-rose-700/70 text-xs font-black text-rose-200 transition cursor-pointer disabled:opacity-40 flex items-center gap-1.5"
          >
            <span>🗑️</span>
            <span>Logları Temizle</span>
          </button>

          <button
            type="button"
            @click="$emit('close')"
            class="w-9 h-9 rounded-xl bg-slate-800 hover:bg-rose-600 border border-slate-600 text-white font-black text-sm flex items-center justify-center cursor-pointer transition"
            title="Kapat"
          >
            ✕
          </button>
        </div>
      </div>

      <!-- 2. ANA GÖVDE: SOLDA ÇAĞRI LİSTESİ, SAĞDA DETAYLI İSTEK & CEVAP -->
      <div class="flex-1 flex flex-col md:flex-row overflow-hidden">
        
        <!-- SOL SÜTUN: AI Çağrı Geçmişi Listesi -->
        <div class="w-full md:w-80 border-b md:border-b-0 md:border-r border-slate-800 bg-slate-950/50 overflow-y-auto p-3 flex flex-col gap-2 shrink-0 max-h-52 md:max-h-full">
          <div v-if="logs.length === 0" class="p-6 text-center text-slate-500 text-xs font-bold">
            Henüz bir yapay zeka isteği kaydedilmedi. "1. Hayal Et" ekranından yeni bir devre tasarladığınızda tüm istek ve cevaplar burada görünecektir.
          </div>

          <button
            v-for="item in logs"
            :key="item.id"
            type="button"
            @click="selectedLogId = item.id"
            :class="[
              'w-full text-left p-3 rounded-2xl border transition cursor-pointer flex flex-col gap-1.5',
              activeLog?.id === item.id
                ? 'bg-indigo-950/90 border-indigo-400 shadow-md'
                : 'bg-slate-900/90 hover:bg-slate-800/80 border-slate-800'
            ]"
          >
            <div class="flex items-center justify-between gap-1">
              <span
                :class="[
                  'px-2 py-0.5 rounded-md text-[10px] font-black',
                  item.stage.includes('1.')
                    ? 'bg-sky-500/20 text-sky-300 border border-sky-500/40'
                    : 'bg-purple-500/20 text-purple-300 border border-purple-500/40'
                ]"
              >
                {{ item.stage }}
              </span>
              <span
                :class="[
                  'px-1.5 py-0.2 rounded text-[9px] font-black',
                  item.status === 'SUCCESS'
                    ? 'bg-emerald-500/20 text-emerald-300'
                    : item.status === 'REPAIRED'
                    ? 'bg-amber-500/20 text-amber-300'
                    : 'bg-rose-500/20 text-rose-300'
                ]"
              >
                {{ item.status }}
              </span>
            </div>

            <div class="text-xs font-bold text-slate-200 line-clamp-1">
              "{{ item.user_goal }}"
            </div>

            <div class="flex items-center justify-between text-[10px] text-slate-400 font-mono">
              <span class="truncate">{{ item.model }}</span>
              <span>{{ item.duration_ms }} ms • {{ item.timestamp.split(' ')[1] || item.timestamp }}</span>
            </div>
          </button>
        </div>

        <!-- SAĞ SÜTUN: Seçili AI Çağrısının İstek (Request) ve Cevap (Response) Detayı -->
        <div v-if="activeLog" class="flex-1 overflow-y-auto p-4 sm:p-6 flex flex-col gap-4 bg-slate-900">
          
          <!-- Çağrı Özet Kartı -->
          <div class="bg-slate-950 rounded-2xl p-4 border border-slate-800 flex flex-wrap items-center justify-between gap-3">
            <div>
              <div class="flex items-center gap-2 mb-1">
                <span class="text-xs font-black text-indigo-400 uppercase tracking-wider">
                  {{ activeLog.stage }}
                </span>
                <span class="text-xs text-slate-500">•</span>
                <span class="text-xs font-mono text-slate-400">{{ activeLog.timestamp }}</span>
              </div>
              <h3 class="text-sm sm:text-base font-black text-white">
                Kullanıcı İstemi: "{{ activeLog.user_goal }}"
              </h3>
            </div>

            <div class="flex flex-wrap items-center gap-2 text-xs font-mono">
              <span class="px-2.5 py-1 rounded-xl bg-slate-900 border border-slate-700 text-sky-300">
                Model: {{ activeLog.model }}
              </span>
              <span class="px-2.5 py-1 rounded-xl bg-slate-900 border border-slate-700 text-amber-300">
                Süre: {{ activeLog.duration_ms }} ms
              </span>
              <span class="px-2.5 py-1 rounded-xl bg-slate-900 border border-slate-700 text-emerald-300">
                Durum: {{ activeLog.status }}
              </span>
            </div>
          </div>

          <!-- Normalizasyon / Filtreleme / Doğrulama Notları -->
          <div
            v-if="activeLog.notes && activeLog.notes.length > 0"
            class="bg-amber-950/40 border border-amber-500/40 rounded-2xl p-3.5 flex flex-col gap-1.5"
          >
            <span class="text-xs font-black text-amber-300 flex items-center gap-1.5">
              <span>🛡️</span>
              <span>Backend Doğrulama, Filtreleme ve Onarım Notları:</span>
            </span>
            <ul class="list-disc list-inside text-xs text-amber-100/90 font-medium space-y-0.5">
              <li v-for="(note, nIdx) in activeLog.notes" :key="nIdx">
                {{ note }}
              </li>
            </ul>
          </div>

          <!-- BÖLÜM 1: YAPAY ZEKAYA GÖNDERİLEN İSTEK (REQUEST) -->
          <div class="grid grid-cols-1 lg:grid-cols-2 gap-4">
            <!-- Sol: Gönderilen Kullanıcı Promptu (User Prompt) -->
            <div class="bg-slate-950 rounded-2xl border border-sky-500/40 overflow-hidden flex flex-col">
              <div class="bg-sky-950/60 px-4 py-2.5 border-b border-sky-500/30 flex items-center justify-between">
                <span class="text-xs font-black text-sky-300 flex items-center gap-1.5">
                  <span>📤</span>
                  <span>1. Yapay Zekaya Gönderilen İstek (User Prompt)</span>
                </span>
                <span class="text-[10px] font-mono text-sky-400">role: "user"</span>
              </div>
              <pre class="p-4 text-xs font-mono text-slate-200 whitespace-pre-wrap overflow-x-auto max-h-80 leading-relaxed">{{ activeLog.user_prompt }}</pre>
            </div>

            <!-- Sağ: Gönderilen Sistem Talimatı (System Prompt) -->
            <div class="bg-slate-950 rounded-2xl border border-slate-700 overflow-hidden flex flex-col">
              <div class="bg-slate-900 px-4 py-2.5 border-b border-slate-800 flex items-center justify-between">
                <span class="text-xs font-black text-slate-300 flex items-center gap-1.5">
                  <span>⚙️</span>
                  <span>Gönderilen Sistem Kuralları (System Prompt)</span>
                </span>
                <span class="text-[10px] font-mono text-slate-400">role: "system"</span>
              </div>
              <pre class="p-4 text-xs font-mono text-slate-400 whitespace-pre-wrap overflow-x-auto max-h-80 leading-relaxed">{{ activeLog.system_prompt }}</pre>
            </div>
          </div>

          <!-- BÖLÜM 2: YAPAY ZEKADAN DÖNEN HAM CEVAP (RAW RESPONSE) VE İŞLENMİŞ ÇIKTI -->
          <div class="grid grid-cols-1 lg:grid-cols-2 gap-4">
            <!-- Sol: Ham LLM Cevabı -->
            <div class="bg-slate-950 rounded-2xl border border-emerald-500/40 overflow-hidden flex flex-col">
              <div class="bg-emerald-950/60 px-4 py-2.5 border-b border-emerald-500/30 flex items-center justify-between">
                <span class="text-xs font-black text-emerald-300 flex items-center gap-1.5">
                  <span>📥</span>
                  <span>2. Yapay Zekadan Dönen Ham Cevap (Raw Response)</span>
                </span>
                <span class="text-[10px] font-mono text-emerald-400">LLM Raw Output</span>
              </div>
              <pre class="p-4 text-xs font-mono text-emerald-200 whitespace-pre-wrap overflow-x-auto max-h-96 leading-relaxed">{{ formatJsonIfPossible(activeLog.raw_response) }}</pre>
            </div>

            <!-- Sağ: Doğrulanmış & Normalize Edilmiş Son JSON Çıktısı -->
            <div class="bg-slate-950 rounded-2xl border border-purple-500/40 overflow-hidden flex flex-col">
              <div class="bg-purple-950/60 px-4 py-2.5 border-b border-purple-500/30 flex items-center justify-between">
                <span class="text-xs font-black text-purple-300 flex items-center gap-1.5">
                  <span>✅</span>
                  <span>3. Doğrulanmış & Render Edilen Çıktı (Processed JSON)</span>
                </span>
                <span class="text-[10px] font-mono text-purple-400">Validated Payload</span>
              </div>
              <pre class="p-4 text-xs font-mono text-purple-200 whitespace-pre-wrap overflow-x-auto max-h-96 leading-relaxed">{{ JSON.stringify(activeLog.processed_output, null, 2) }}</pre>
            </div>
          </div>

        </div>

        <!-- Seçili Log Yoksa -->
        <div v-else class="flex-1 flex items-center justify-center text-slate-500 text-sm font-bold p-8">
          İncelemek için sol taraftan bir yapay zeka çağrısı seçin.
        </div>

      </div>

    </div>
  </div>
</template>

<script setup lang="ts">
import { ref, computed, watch } from 'vue';
import type { AILogEntry } from '../types/project';

const props = defineProps<{
  isOpen: boolean;
  logs: AILogEntry[];
}>();

defineEmits<{
  (e: 'close'): void;
  (e: 'refresh'): void;
  (e: 'clear'): void;
}>();

const selectedLogId = ref<string>('');

watch(
  () => props.logs,
  (newLogs) => {
    if (newLogs.length > 0 && (!selectedLogId.value || !newLogs.some(l => l.id === selectedLogId.value))) {
      selectedLogId.value = newLogs[0].id;
    }
  },
  { immediate: true }
);

const activeLog = computed<AILogEntry | null>(() => {
  if (!props.logs || props.logs.length === 0) return null;
  return props.logs.find(l => l.id === selectedLogId.value) || props.logs[0];
});

function formatJsonIfPossible(raw: string): string {
  if (!raw) return '';
  try {
    const parsed = JSON.parse(raw);
    return JSON.stringify(parsed, null, 2);
  } catch {
    return raw;
  }
}
</script>

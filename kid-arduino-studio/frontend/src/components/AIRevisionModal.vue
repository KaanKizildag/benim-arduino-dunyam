<template>
  <div v-if="isOpen">
    <!-- Karartma Arka Planı -->
    <div
      class="fixed inset-0 z-50 bg-slate-900/65 backdrop-blur-xs flex items-center justify-center p-3 sm:p-5 select-none"
      @click.self="!isRevising && $emit('close')"
    >
      <!-- Modal Kutusu -->
      <div class="bg-white rounded-[32px] border-[3px] border-slate-900 shadow-[0_14px_0_rgba(15,23,42,0.35)] max-w-xl w-full overflow-hidden flex flex-col animate-in fade-in zoom-in-95 duration-150">
        
        <!-- ÜST BAŞLIK ÇUBUĞU (Mor / İndigo Gradient) -->
        <div class="px-5 py-4 bg-gradient-to-r from-[#a855f7] via-[#818cf8] to-[#38bdf8] border-b-[3px] border-slate-900 flex items-center justify-between">
          <div class="flex items-center gap-3">
            <div class="w-11 h-11 rounded-2xl bg-[#fef08a] border-2 border-slate-900 shadow-xs flex items-center justify-center text-2xl">
              ✨
            </div>
            <div>
              <h3 class="text-base sm:text-lg font-black text-slate-950 leading-tight">
                Projeyi AI ile Geliştir & Revize Et
              </h3>
              <span class="text-[11px] font-bold text-slate-900/85 truncate block max-w-xs sm:max-w-md">
                Mevcut Proje: <strong class="underline decoration-slate-900">{{ projectName }}</strong>
              </span>
            </div>
          </div>

          <!-- Kapat / Durdur Butonu -->
          <button
            type="button"
            @click="isRevising ? $emit('cancel') : $emit('close')"
            class="w-8 h-8 rounded-xl bg-rose-500 hover:bg-rose-600 active:translate-y-0.5 text-white font-black text-sm flex items-center justify-center border-2 border-slate-900 shadow-[0_2px_0_#9f1239] cursor-pointer transition"
            :title="isRevising ? 'Revizyonu Durdur' : 'Kapat'"
          >
            ✕
          </button>
        </div>

        <!-- İÇERİK: REVİZYON YAZMA VEYA CANLI STREAM MODU -->
        <div class="p-5 flex flex-col gap-4 bg-slate-50">
          
          <!-- DURUM A: REVİZYON İŞLENİYOR (Canlı İlerleme) -->
          <div v-if="isRevising" class="flex flex-col gap-3 py-3">
            <div class="flex items-center gap-3">
              <span class="text-3xl animate-spin">⚙️</span>
              <div>
                <h4 class="text-sm font-black text-slate-900">
                  {{ streamData?.stageTitle || 'Yapay Zeka Devreni Güncelliyor...' }}
                </h4>
                <p class="text-xs font-bold text-slate-600">
                  {{ streamData?.stageSubtitle || 'Mevcut pinler korunarak yeni parçalar ve kod senkronize ediliyor...' }}
                </p>
              </div>
            </div>

            <!-- Canlı İlerleme Çubuğu -->
            <div class="w-full h-4 rounded-full bg-slate-200 border-2 border-slate-900 overflow-hidden p-0.5 mt-2">
              <div
                class="h-full rounded-full bg-gradient-to-r from-[#a855f7] via-[#38bdf8] to-[#4ade80] transition-all duration-300"
                :style="{ width: `${streamData?.progressPercent || 35}%` }"
              ></div>
            </div>

            <!-- Canlı Parça Rozetleri -->
            <div v-if="streamData?.discoveredComponents?.length" class="flex flex-wrap gap-1.5 pt-2">
              <span
                v-for="comp in streamData.discoveredComponents"
                :key="comp.id"
                class="px-2.5 py-1 rounded-xl bg-emerald-100 border border-emerald-600 text-emerald-950 text-[11px] font-black flex items-center gap-1 shadow-2xs"
              >
                <span>{{ comp.icon }}</span>
                <span>{{ comp.label }}</span>
                <span>✓</span>
              </span>
            </div>

            <div class="pt-2 flex justify-end">
              <button
                type="button"
                @click="$emit('cancel')"
                class="px-3.5 py-1.5 rounded-xl bg-rose-100 hover:bg-rose-200 border-2 border-rose-600 text-rose-950 text-xs font-black cursor-pointer shadow-xs active:translate-y-0.5"
              >
                🛑 Revizyonu Durdur
              </button>
            </div>
          </div>

          <!-- DURUM B: REVİZYON YAZMA FORMU -->
          <div v-else class="flex flex-col gap-3.5">
            <div class="text-xs font-bold text-slate-700 leading-relaxed bg-white border-2 border-slate-900/15 rounded-2xl p-3">
              💡 Mevcut devrendeki çalışan parçaları bozmadan yeni bir parça ekleyebilir veya çalışma mantığını değiştirebilirsin.
            </div>

            <!-- Hızlı Öneri Çipleri -->
            <div class="flex flex-col gap-1.5">
              <span class="text-[11px] font-black text-slate-700">Hızlı Fikir Seç veya Kendin Yaz:</span>
              <div class="flex flex-wrap gap-1.5">
                <button
                  v-for="chip in quickChips"
                  :key="chip"
                  type="button"
                  @click="revisionText = chip"
                  class="px-2.5 py-1 rounded-xl bg-white hover:bg-[#fef08a] border-2 border-slate-900 text-[11px] font-black text-slate-800 cursor-pointer shadow-2xs active:translate-y-0.5 transition"
                >
                  {{ chip }}
                </button>
              </div>
            </div>

            <!-- Revizyon İstek Metin Kutusu -->
            <div class="relative">
              <textarea
                v-model="revisionText"
                rows="3"
                placeholder="Örn: Devreme sarı ikaz lambası ekle ve mesafe 10cm altına inince yansın..."
                class="w-full p-3.5 rounded-2xl border-2 border-slate-900 bg-white focus:ring-2 focus:ring-purple-400 text-slate-900 font-black text-xs sm:text-sm outline-none transition resize-none placeholder:text-slate-400 placeholder:font-bold"
                @keydown.enter.prevent="handleRevise"
              ></textarea>
            </div>

            <!-- Butonlar -->
            <div class="flex items-center justify-end gap-2 pt-1">
              <button
                type="button"
                @click="$emit('close')"
                class="px-4 py-2.5 rounded-xl bg-slate-100 hover:bg-slate-200 border-2 border-slate-900 text-slate-800 text-xs font-black cursor-pointer shadow-xs active:translate-y-0.5"
              >
                Vazgeç
              </button>

              <button
                type="button"
                @click="handleRevise"
                :disabled="!revisionText.trim()"
                class="px-6 py-2.5 rounded-xl bg-[#a855f7] hover:bg-[#9333ea] disabled:opacity-40 border-2 border-slate-900 text-white text-xs font-black cursor-pointer shadow-[0_3px_0_#6b21a8] active:translate-y-0.5 active:shadow-none transition flex items-center gap-1.5"
              >
                <span>🪄</span>
                <span>Projeyi Revize Et ➔</span>
              </button>
            </div>
          </div>

        </div>

      </div>
    </div>
  </div>
</template>

<script setup lang="ts">
import { ref } from 'vue';
import type { AIStreamProgress } from './Page1HayalEt.vue';

const props = defineProps<{
  isOpen: boolean;
  projectName: string;
  isRevising: boolean;
  streamData?: AIStreamProgress | null;
}>();

const emit = defineEmits<{
  (e: 'close'): void;
  (e: 'revise', prompt: string): void;
  (e: 'cancel'): void;
}>();

const revisionText = ref('');

const quickChips = [
  '🔴 Kırmızı ikaz LED\'i ekle',
  '📢 Buzzer ile sesli uyarı ekle',
  '🎚️ Potansiyometre ile hız/açı ayarı ekle',
  '🔘 Butona basılınca çalışsın',
  '🟡 Sarı uyarı lambası ekle',
  '⚡ Röle modülü ekle'
];

function handleRevise() {
  if (!revisionText.value.trim() || props.isRevising) return;
  emit('revise', revisionText.value.trim());
}
</script>

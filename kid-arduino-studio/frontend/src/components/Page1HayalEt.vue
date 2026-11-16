<template>
  <div class="w-full max-w-5xl mx-auto flex-1 flex flex-col items-center justify-between gap-4 py-3 sm:py-5 px-3 sm:px-6 select-none">
    
    <!-- 1. SEVİMLİ KARŞILAMA VE DİYALOG (Referans Görsel 1 Sol Üst Sohbet Stili) -->
    <div class="w-full flex flex-col sm:flex-row items-center gap-4 bg-white rounded-3xl p-4 sm:p-5 border-[3px] border-slate-900 shadow-[0_4px_0_#0f172a]">
      <!-- Sevimli Robot Başlığı -->
      <div class="relative shrink-0 group">
        <div class="w-20 h-20 sm:w-24 sm:h-24 rounded-3xl bg-[#38bdf8] border-[3px] border-slate-900 shadow-[0_4px_0_#0284c7] flex items-center justify-center text-4xl sm:text-5xl group-hover:rotate-6 transition-transform">
          🤖
        </div>
        <span class="absolute -top-1 -right-1 w-5 h-5 rounded-full bg-emerald-400 border-2 border-slate-900 animate-ping"></span>
        <span class="absolute -top-1 -right-1 w-5 h-5 rounded-full bg-emerald-500 border-2 border-slate-900"></span>
      </div>

      <!-- Konuşma Balonu -->
      <div class="flex-1 text-center sm:text-left">
        <div class="flex items-center justify-center sm:justify-start gap-2 mb-1">
          <h2 class="text-base sm:text-xl font-black text-slate-900">
            Merhaba Geleceğin Mucidi! 👋
          </h2>
          <span class="px-2 py-0.5 rounded-full bg-amber-200 border border-slate-900 text-[10px] font-black text-slate-900">
            AI Asistanın Hazır
          </span>
        </div>
        <p class="text-xs sm:text-sm text-slate-600 font-bold leading-relaxed">
          Ben senin yapay zeka devre asistanınım. Arduino ile yapmak istediğin şeyi bana kendi kelimelerinle anlat! Örneğin: <em>"Odam kararınca sarı gece lambam yansın, aydınlanınca sönsün."</em>
        </p>
      </div>
    </div>

    <!-- 2. BÜYÜK FİKİR GİRİŞ KUTUSU VE SESLİ GİRİŞ -->
    <div class="w-full bg-white rounded-3xl p-4 sm:p-6 border-[3px] border-slate-900 shadow-[0_5px_0_#0f172a] flex flex-col gap-3">
      <div class="relative">
        <textarea
          v-model="promptText"
          rows="3"
          placeholder="Hayalindeki projeyi buraya yaz... (Örn: Biri 15 cm yaklaştığında buzzer ötsün ve kırmızı LED yansın)"
          class="w-full p-4 sm:p-5 rounded-2xl border-2 border-slate-900 bg-slate-50 focus:bg-white focus:ring-2 focus:ring-sky-400 text-slate-900 font-black text-sm sm:text-base outline-none transition resize-none placeholder:text-slate-400 placeholder:font-bold"
          @keydown.enter.prevent="handleGenerate"
        ></textarea>

        <!-- Mikrofona Basma Simülasyonu -->
        <button
          type="button"
          @click="simulateVoiceInput"
          class="absolute bottom-3 right-3 px-3 py-1.5 rounded-xl border-2 border-slate-900 bg-white hover:bg-slate-100 text-slate-800 transition shadow-[0_2px_0_#0f172a] active:translate-y-0.5 active:shadow-none cursor-pointer flex items-center gap-1.5 text-xs font-black"
          title="Sesli Konuş (Simüle)"
        >
          <span>🎙️</span>
          <span class="hidden sm:inline">Sesle Söyle</span>
        </button>
      </div>

      <!-- İlham Verici Hızlı Fikir Kartları -->
      <div>
        <div class="flex items-center justify-between mb-2">
          <span class="text-xs font-black text-slate-500 uppercase tracking-wider">
            💡 İlham Verici Popüler Projeler (Tıkla ve Dene!):
          </span>
        </div>
        <div class="grid grid-cols-1 sm:grid-cols-3 gap-2.5">
          <button
            v-for="(idea, idx) in inspirationIdeas"
            :key="idx"
            type="button"
            @click="selectIdea(idea.text)"
            class="p-3 rounded-2xl border-2 border-slate-900 bg-slate-50 hover:bg-amber-50 hover:shadow-[0_3px_0_#ca8a04] active:translate-y-0.5 transition text-left flex items-start gap-2.5 cursor-pointer group shadow-[0_2px_0_#0f172a]"
          >
            <span class="text-2xl p-1 bg-white rounded-xl border border-slate-900 shadow-xs group-hover:scale-110 transition-transform">
              {{ idea.icon }}
            </span>
            <div class="min-w-0">
              <strong class="text-xs font-black text-slate-900 block truncate group-hover:text-amber-800">
                {{ idea.title }}
              </strong>
              <p class="text-[11px] text-slate-600 font-bold line-clamp-2 leading-snug mt-0.5">
                {{ idea.text }}
              </p>
            </div>
          </button>
        </div>
      </div>
    </div>

    <!-- 3. ALT ÇUBUK: ÇANTA BİLGİSİ VE BÜYÜK TASARLA BUTONU -->
    <div class="w-full bg-white rounded-2xl p-3 sm:p-4 border-[3px] border-slate-900 shadow-[0_4px_0_#0f172a] flex flex-col sm:flex-row items-center justify-between gap-3">
      <div class="flex items-center gap-2 text-xs font-black text-slate-700">
        <span class="text-lg">🎒</span>
        <span>Malzeme Çantam:</span>
        <span class="px-2 py-0.5 rounded-lg bg-emerald-100 text-emerald-900 border border-slate-900">
          {{ inventoryCount }} Elektronik Parça Hazır
        </span>
      </div>

      <button
        type="button"
        @click="handleGenerate"
        :disabled="isGenerating || !promptText.trim()"
        class="w-full sm:w-auto px-10 py-3.5 rounded-2xl bg-[#4ade80] hover:bg-[#22c55e] border-2 border-slate-900 shadow-[0_5px_0_#15803d] active:translate-y-1 active:shadow-[0_1px_0_#15803d] text-slate-950 font-black text-sm sm:text-base transition cursor-pointer flex items-center justify-center gap-2 group disabled:opacity-40 disabled:cursor-not-allowed"
      >
        <span v-if="isGenerating" class="animate-spin text-xl">⚙️</span>
        <span v-else class="text-xl group-hover:rotate-12 transition-transform">🚀</span>
        <span>{{ isGenerating ? 'Yapay Zeka Devreyi Tasarlıyor...' : 'Devreyi ve Kodu Tasarla! ➔' }}</span>
      </button>
    </div>

  </div>
</template>

<script setup lang="ts">
import { ref } from 'vue';

defineProps<{
  isGenerating: boolean;
  inventoryCount: number;
}>();

const emit = defineEmits<{
  (e: 'generate', prompt: string): void;
}>();

const promptText = ref('Odam kararınca sarı gece lambam yansın, aydınlanınca sönsün.');

const inspirationIdeas = [
  {
    icon: '🌙',
    title: 'Akıllı Gece Lambası',
    text: 'Odam karardığında sarı gece lambam yansın, sabah olunca otomatik sönsün.'
  },
  {
    icon: '🦇',
    title: 'Park ve Mesafe Radarı',
    text: 'Biri 15 cm yaklaştığında buzzer hızlıca biplemeye başlasın ve kırmızı LED yansın.'
  },
  {
    icon: '🚨',
    title: 'Hırsız Alarm Sistemi',
    text: 'Işık aniden kesilirse veya biri geçerse buzzer siren çalarak alarm versin.'
  }
];

function selectIdea(text: string) {
  promptText.value = text;
}

function simulateVoiceInput() {
  promptText.value = 'Odam karardığında sevimli gece lambam yansın, aydınlanınca sönsün.';
}

function handleGenerate() {
  if (!promptText.value.trim()) return;
  emit('generate', promptText.value.trim());
}
</script>
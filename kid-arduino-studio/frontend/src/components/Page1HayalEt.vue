<template>
  <div class="max-w-4xl mx-auto w-full flex flex-col items-center gap-6 py-4 sm:py-8 px-4">
    
    <!-- Sevimli Robot Karakteri & Karşılama Balonu -->
    <div class="flex flex-col sm:flex-row items-center gap-5 text-center sm:text-left">
      <!-- Hareketli Sevimli Robot -->
      <div class="relative shrink-0 group">
        <div class="w-24 h-24 sm:w-28 sm:h-28 rounded-3xl bg-gradient-to-tr from-indigo-500 via-sky-400 to-emerald-400 p-1 shadow-xl flex items-center justify-center transform group-hover:scale-105 transition-transform duration-300">
          <div class="w-full h-full bg-slate-900 rounded-[22px] flex items-center justify-center text-5xl">
            🤖
          </div>
        </div>
        <!-- Yanıp Sönen Sevimli Anten Işığı -->
        <span class="absolute -top-1.5 -right-1.5 flex h-5 w-5">
          <span class="animate-ping absolute inline-flex h-full w-full rounded-full bg-emerald-400 opacity-75"></span>
          <span class="relative inline-flex rounded-full h-5 w-5 bg-emerald-500 border-2 border-white"></span>
        </span>
      </div>

      <!-- Konuşma Balonu -->
      <div class="bg-white rounded-3xl p-5 border-2 border-slate-200 shadow-md relative max-w-lg">
        <div class="hidden sm:block absolute top-10 -left-3 w-4 h-4 bg-white border-l-2 border-b-2 border-slate-200 transform rotate-45"></div>
        <h2 class="text-base sm:text-lg font-black text-slate-900 mb-1">
          Merhaba Geleceğin Mucidi! 👋
        </h2>
        <p class="text-xs sm:text-sm text-slate-600 font-medium leading-relaxed">
          Ben senin akıllı robot arkadaşınım. Bugün Arduino ile ne yapmak istersin? Bana aklındaki hayali sadece kendi cümlelerinle anlat!
        </p>
      </div>
    </div>

    <!-- Büyük Doğal Dil Sohbet / Fikir Giriş Kutusu -->
    <div class="w-full bg-white rounded-3xl p-4 sm:p-6 border-2 border-slate-200 shadow-lg flex flex-col gap-4">
      <div class="relative">
        <textarea
          v-model="promptText"
          rows="3"
          placeholder="Örn: Odam karardığında kendiliğinden yanan sevimli bir gece lambası yapmak istiyorum..."
          class="w-full p-4 sm:p-5 rounded-2xl border-2 border-slate-200 bg-slate-50 focus:bg-white focus:border-indigo-600 text-slate-900 font-extrabold text-sm sm:text-base outline-none transition resize-none placeholder:text-slate-400 placeholder:font-bold"
          @keydown.enter.prevent="handleGenerate"
        ></textarea>

        <!-- Mikrofona Basma Simülasyonu Butonu -->
        <button
          type="button"
          @click="simulateVoiceInput"
          class="absolute bottom-3 right-3 p-2.5 rounded-xl border border-slate-300 bg-white hover:bg-slate-100 text-slate-600 transition shadow-xs cursor-pointer flex items-center gap-1.5 text-xs font-bold"
          title="Sesli Konuş (Simüle)"
        >
          <span>🎙️</span>
          <span class="hidden sm:inline">Konuş</span>
        </button>
      </div>

      <!-- İlham Verici Hızlı Fikir Kartları -->
      <div>
        <span class="text-xs font-extrabold text-slate-400 uppercase tracking-wider block mb-2">
          💡 İlham Verici Fikirler (Tıkla ve Dene!):
        </span>
        <div class="grid grid-cols-1 sm:grid-cols-3 gap-2.5">
          <button
            v-for="(idea, idx) in inspirationIdeas"
            :key="idx"
            type="button"
            @click="selectIdea(idea.text)"
            class="p-3 rounded-2xl border-2 border-slate-200 bg-slate-50/70 hover:bg-white hover:border-indigo-400 hover:shadow-xs transition text-left flex items-start gap-2.5 cursor-pointer group"
          >
            <span class="text-2xl p-1 bg-white rounded-xl shadow-xs border border-slate-100 group-hover:scale-110 transition-transform">
              {{ idea.icon }}
            </span>
            <div class="min-w-0">
              <strong class="text-xs font-black text-slate-900 block truncate group-hover:text-indigo-600">
                {{ idea.title }}
              </strong>
              <p class="text-[11px] text-slate-500 font-medium line-clamp-2 leading-snug">
                {{ idea.text }}
              </p>
            </div>
          </button>
        </div>
      </div>

      <!-- Alt Buton: Büyük Yanıp Sönen Devreyi Tasarla Butonu -->
      <div class="flex flex-col sm:flex-row items-center justify-between gap-3 pt-3 border-t border-slate-100">
        <div class="text-xs text-slate-500 font-bold flex items-center gap-2">
          <span>🎒 Çantandaki Parçalar:</span>
          <span class="text-indigo-600 font-extrabold">{{ inventoryCount }} Parça Seçili</span>
        </div>

        <button
          type="button"
          @click="handleGenerate"
          :disabled="isGenerating || !promptText.trim()"
          class="w-full sm:w-auto px-8 py-4 rounded-2xl bg-emerald-500 hover:bg-emerald-600 text-white font-black text-base shadow-lg shadow-emerald-200 hover:shadow-emerald-300 transition-all transform active:scale-98 disabled:opacity-50 disabled:cursor-not-allowed flex items-center justify-center gap-2.5 cursor-pointer group animate-pulse hover:animate-none"
        >
          <span v-if="isGenerating" class="animate-spin text-xl">⚙️</span>
          <span v-else class="text-xl group-hover:translate-x-1 transition-transform">✨</span>
          <span>{{ isGenerating ? 'Devre Tasarlanıyor...' : 'Devreyi Tasarla! ➔' }}</span>
        </button>
      </div>

    </div>

  </div>
</template>

<script setup lang="ts">
import { ref } from 'vue';

const props = defineProps<{
  isGenerating: boolean;
  inventoryCount: number;
}>();

const emit = defineEmits<{
  (e: 'generate', prompt: string): void;
}>();

const promptText = ref('Odam karardığında kendiliğinden yanan sevimli bir akıllı gece lambası yapmak istiyorum!');

const inspirationIdeas = [
  {
    title: 'Akıllı Gece Lambası',
    icon: '🌙',
    text: 'Odam karardığında sihir gibi kendiliğinden yanan bir gece lambası yapalım.'
  },
  {
    title: 'Yarasa Park Sensörü',
    icon: '🦇',
    text: 'Önüne bir engel yaklaştığında tıpkı bir araba gibi bip bip öten park alarmı.'
  },
  {
    title: 'Gizli Kasa Alarmı',
    icon: '🚨',
    text: 'Çekmecem açılıp ışık gördüğünde veya butona basıldığında korna çalan alarm.'
  }
];

function selectIdea(text: string) {
  promptText.value = text;
}

function simulateVoiceInput() {
  promptText.value = 'Harekete duyarlı ve biri yaklaşınca ışık saçan eğlenceli bir robot gözü yap!';
}

function handleGenerate() {
  if (!promptText.value.trim() || props.isGenerating) return;
  emit('generate', promptText.value.trim());
}
</script>

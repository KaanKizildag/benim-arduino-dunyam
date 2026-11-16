<template>
  <div class="bg-white rounded-2xl p-5 border border-slate-200 shadow-sm">
    <div class="mb-3">
      <h2 class="text-base sm:text-lg font-black text-slate-900 mb-1">Bugün ne yapmak istiyorsun?</h2>
      <p class="text-xs text-slate-500 font-medium">Hayalindeki cihazı Türkçe yaz, yapay zeka senin için devresini çizsin.</p>
    </div>

    <!-- Giriş Kutusu -->
    <div class="relative mb-3">
      <textarea
        v-model="promptText"
        rows="2"
        placeholder="Örnek: Odam kararınca gece lambam yansın..."
        class="w-full p-3.5 rounded-xl border border-slate-300 focus:border-indigo-600 focus:ring-2 focus:ring-indigo-100 text-slate-800 font-semibold text-sm outline-none transition resize-none placeholder:text-slate-400"
        @keydown.enter.prevent="handleGenerate"
      ></textarea>
    </div>

    <!-- Hızlı Örnek Fikirler -->
    <div class="flex flex-wrap items-center gap-2 mb-4">
      <span class="text-xs text-slate-400 font-bold">Örnekler:</span>
      <button
        v-for="idea in presetIdeas"
        :key="idea.title"
        type="button"
        @click="selectPreset(idea.prompt)"
        class="px-2.5 py-1 rounded-lg bg-slate-100 hover:bg-slate-200 text-slate-700 text-xs font-semibold transition flex items-center gap-1"
      >
        <span>{{ idea.emoji }}</span>
        <span>{{ idea.title }}</span>
      </button>
    </div>

    <!-- Aksiyon Butonu -->
    <div class="flex items-center justify-between gap-3 pt-3 border-t border-slate-100">
      <button
        type="button"
        @click="showSettings = !showSettings"
        class="text-xs text-slate-500 hover:text-slate-700 font-medium"
      >
        ⚙️ {{ showSettings ? 'Ayarları Kapat' : 'API Ayarları (İsteğe Bağlı)' }}
      </button>

      <button
        type="button"
        @click="handleGenerate"
        :disabled="isLoading || !promptText.trim()"
        class="px-5 py-2.5 rounded-xl bg-indigo-600 hover:bg-indigo-700 text-white font-bold text-sm shadow-sm transition flex items-center gap-2 disabled:opacity-40 disabled:cursor-not-allowed"
      >
        <span v-if="!isLoading">Devreyi Oluştur ✨</span>
        <span v-else class="flex items-center gap-2">
          <svg class="animate-spin h-4 w-4 text-white" fill="none" viewBox="0 0 24 24">
            <circle class="opacity-25" cx="12" cy="12" r="10" stroke="currentColor" stroke-width="4"></circle>
            <path class="opacity-75" fill="currentColor" d="M4 12a8 8 0 018-8V0C5.373 0 0 5.373 0 12h4zm2 5.291A7.962 7.962 0 014 12H0c0 3.042 1.135 5.824 3 7.938l3-2.647z"></path>
          </svg>
          Hazırlanıyor...
        </span>
      </button>
    </div>

    <!-- Opsiyonel Ayarlar -->
    <div v-if="showSettings" class="mt-3 p-3 rounded-xl bg-slate-50 border border-slate-200 text-xs flex flex-col gap-2">
      <div>
        <label class="block font-bold text-slate-600 mb-1">Gemini / OpenAI API Anahtarı:</label>
        <input
          v-model="apiKey"
          type="password"
          placeholder="Boş bırakırsanız dahili akıllı şablonlar çalışır"
          class="w-full px-3 py-1.5 rounded-lg border border-slate-300 font-mono text-xs focus:ring-1 focus:ring-indigo-400 outline-none"
        />
      </div>
    </div>
  </div>
</template>

<script setup lang="ts">
import { ref } from 'vue';

const props = defineProps<{
  isLoading: boolean;
}>();

const emit = defineEmits<{
  (e: 'generate', payload: { prompt: string; apiKey?: string }): void;
}>();

const promptText = ref('Odam kararınca gece lambam yansın, biri yaklaşınca buzzer ötsün');
const showSettings = ref(false);
const apiKey = ref('');

const presetIdeas = [
  {
    emoji: '🌙',
    title: 'Gece Lambası',
    prompt: 'Oda kararınca kendiliğinden yanan akıllı bir gece lambası yapalım.'
  },
  {
    emoji: '🦇',
    title: 'Park Sensörü',
    prompt: 'Önüne 15 cm\'den daha yakın bir engel geldiğinde korna çalan akıllı bir park sensörü yap.'
  },
  {
    emoji: '🚨',
    title: 'Oda Alarmı',
    prompt: 'Işık sensörünün üstü gölgelenince kırmızı LED yansın ve buzzer ötsün.'
  }
];

function selectPreset(prompt: string) {
  promptText.value = prompt;
}

function handleGenerate() {
  if (props.isLoading || !promptText.value.trim()) return;
  emit('generate', {
    prompt: promptText.value.trim(),
    apiKey: apiKey.value.trim() || undefined
  });
}
</script>

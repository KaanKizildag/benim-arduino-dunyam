<template>
  <div class="bg-white rounded-2xl p-5 border border-slate-200 shadow-sm flex flex-col gap-4">
    <!-- Üst Başlık ve Model Seçici Şeridi -->
    <div class="flex flex-wrap items-center justify-between gap-3 pb-3 border-b border-slate-100">
      <div>
        <h2 class="text-base sm:text-lg font-black text-slate-900 leading-tight">Bugün ne yapmak istiyorsun?</h2>
        <p class="text-xs text-slate-500 font-medium">Hayalindeki icadı Türkçe yaz, yapay zeka senin için devreyi ve kodu hazırlasın.</p>
      </div>

      <!-- Model Seçim Kutusu -->
      <div class="flex items-center gap-2">
        <div class="flex items-center gap-1.5 bg-slate-100 px-3 py-1.5 rounded-xl border border-slate-200 text-xs">
          <span class="text-slate-400 font-bold">🧠 Model:</span>
          <select
            v-model="selectedModel"
            class="bg-transparent font-extrabold text-slate-800 outline-none cursor-pointer max-w-[220px] truncate"
          >
            <!-- Yerel Modeller Grubu -->
            <optgroup label="💻 Yerel Modeller (Ollama - Ücretsiz)">
              <option
                v-for="m in localModels"
                :key="m.id"
                :value="m.id"
              >
                {{ m.name }}
              </option>
            </optgroup>

            <!-- Bulut Modelleri Grubu -->
            <optgroup label="☁️ Bulut Modelleri">
              <option
                v-for="m in cloudModels"
                :key="m.id"
                :value="m.id"
              >
                {{ m.name }}
              </option>
            </optgroup>
          </select>

          <!-- Durum Işığı -->
          <span
            v-if="isLocalModelSelected"
            class="w-2 h-2 rounded-full bg-emerald-500 animate-pulse"
            title="Yerel Ollama Modeli Aktif"
          ></span>
          <span
            v-else
            class="w-2 h-2 rounded-full bg-blue-500"
            title="Bulut Modeli Seçili"
          ></span>
        </div>
      </div>
    </div>

    <!-- Giriş Kutusu -->
    <div class="relative">
      <textarea
        v-model="promptText"
        rows="2"
        placeholder="Örnek: Odam kararınca gece lambam yansın, biri yaklaşınca buzzer ötsün..."
        class="w-full p-3.5 rounded-xl border border-slate-300 focus:border-indigo-600 focus:ring-2 focus:ring-indigo-100 text-slate-800 font-semibold text-sm outline-none transition resize-none placeholder:text-slate-400"
        @keydown.enter.prevent="handleGenerate"
      ></textarea>
    </div>

    <!-- Hızlı Örnek Fikirler -->
    <div class="flex flex-wrap items-center gap-2">
      <span class="text-xs text-slate-400 font-bold">Örnek Fikirler:</span>
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

    <!-- Bulut Modeli Seçildiyse API Key Girişi veya Yerel Model Bilgisi -->
    <div v-if="!isLocalModelSelected" class="p-3 bg-blue-50/70 border border-blue-200 rounded-xl flex flex-col sm:flex-row items-center justify-between gap-2 text-xs">
      <div class="flex items-center gap-2 text-blue-900 font-medium">
        <span>🔑</span>
        <span>{{ getProviderKeyLabel() }} API Anahtarı:</span>
      </div>
      <input
        v-model="apiKey"
        type="password"
        placeholder="Ortamda tanımlı değilse buraya yapıştırın"
        class="w-full sm:w-64 px-3 py-1.5 rounded-lg border border-blue-300 bg-white font-mono text-xs focus:ring-1 focus:ring-blue-500 outline-none"
      />
    </div>

    <div v-else class="flex items-center gap-2 text-xs text-emerald-800 bg-emerald-50 px-3 py-1.5 rounded-xl border border-emerald-200">
      <span>🟢</span>
      <span><strong>Yerel Çalışma Modu:</strong> Verileriniz bilgisayarınızdaki Ollama ile işlenir. API anahtarı veya internet bağlantısı gerekmez.</span>
    </div>

    <!-- Aksiyon Barı -->
    <div class="flex items-center justify-between pt-1">
      <div class="text-xs text-slate-400 font-medium">
        Enter ↵ tuşuna basarak da başlatabilirsin
      </div>

      <button
        type="button"
        @click="handleGenerate"
        :disabled="isLoading || !promptText.trim()"
        class="px-6 py-2.5 rounded-xl bg-indigo-600 hover:bg-indigo-700 text-white font-bold text-sm shadow-sm transition flex items-center gap-2 disabled:opacity-40 disabled:cursor-not-allowed"
      >
        <span v-if="!isLoading">Projeyi Tasarla ✨</span>
        <span v-else class="flex items-center gap-2">
          <svg class="animate-spin h-4 w-4 text-white" fill="none" viewBox="0 0 24 24">
            <circle class="opacity-25" cx="12" cy="12" r="10" stroke="currentColor" stroke-width="4"></circle>
            <path class="opacity-75" fill="currentColor" d="M4 12a8 8 0 018-8V0C5.373 0 0 5.373 0 12h4zm2 5.291A7.962 7.962 0 014 12H0c0 3.042 1.135 5.824 3 7.938l3-2.647z"></path>
          </svg>
          <span>{{ isLocalModelSelected ? 'Yerel Model Üretiyor...' : 'Bulut Modeli Üretiyor...' }}</span>
        </span>
      </button>
    </div>
  </div>
</template>

<script setup lang="ts">
import { ref, computed } from 'vue';
import type { ModelOption, ModelsResponse } from '../types/project';

const props = defineProps<{
  isLoading: boolean;
  modelsData: ModelsResponse | null;
}>();

const emit = defineEmits<{
  (e: 'generate', payload: { prompt: string; model: string; apiKey?: string }): void;
}>();

const promptText = ref('Odam kararınca gece lambam yansın, biri yaklaşınca buzzer ötsün');
const selectedModel = ref<string>('ollama/qwen2.5-coder:1.5b');
const apiKey = ref('');

const localModels = computed<ModelOption[]>(() => {
  if (props.modelsData?.local_models && props.modelsData.local_models.length > 0) {
    return props.modelsData.local_models;
  }
  return [
    { id: 'ollama/qwen2.5-coder:1.5b', name: 'qwen2.5-coder:1.5b (Önerilen)', provider: 'local', category: 'Yerel', badge: '💻 Yerel' },
    { id: 'ollama/qwen2.5-coder:3b', name: 'qwen2.5-coder:3b (Güçlü Kodlama)', provider: 'local', category: 'Yerel', badge: '💻 Yerel' },
    { id: 'ollama/deepseek-r1:1.5b', name: 'deepseek-r1:1.5b (Düşünme)', provider: 'local', category: 'Yerel', badge: '💻 Yerel' },
    { id: 'ollama/codellama:latest', name: 'codellama:latest', provider: 'local', category: 'Yerel', badge: '💻 Yerel' },
  ];
});

const cloudModels = computed<ModelOption[]>(() => {
  if (props.modelsData?.cloud_models && props.modelsData.cloud_models.length > 0) {
    return props.modelsData.cloud_models;
  }
  return [
    { id: 'gemini/gemini-2.0-flash', name: 'Gemini 2.0 Flash', provider: 'gemini', category: 'Google Gemini', badge: '☁️ Bulut' },
    { id: 'gemini/gemini-1.5-flash', name: 'Gemini 1.5 Flash', provider: 'gemini', category: 'Google Gemini', badge: '☁️ Bulut' },
    { id: 'gpt-4o-mini', name: 'GPT-4o Mini', provider: 'openai', category: 'OpenAI', badge: '☁️ Bulut' },
    { id: 'claude-3-5-haiku-20241022', name: 'Claude 3.5 Haiku', provider: 'anthropic', category: 'Claude', badge: '☁️ Bulut' },
    { id: 'claude-3-5-sonnet-20241022', name: 'Claude 3.5 Sonnet', provider: 'anthropic', category: 'Claude', badge: '☁️ Bulut' },
  ];
});

const isLocalModelSelected = computed(() => {
  return selectedModel.value.startsWith('ollama/') || selectedModel.value.includes('qwen') || selectedModel.value.includes('deepseek');
});

function getProviderKeyLabel(): string {
  if (selectedModel.value.includes('gemini')) return 'Google Gemini';
  if (selectedModel.value.includes('claude') || selectedModel.value.includes('anthropic')) return 'Anthropic Claude';
  if (selectedModel.value.includes('gpt')) return 'OpenAI';
  return 'API';
}

const presetIdeas = [
  { emoji: '🌙', title: 'Gece Lambası', prompt: 'Oda kararınca kendiliğinden yanan akıllı bir gece lambası yapalım.' },
  { emoji: '🦇', title: 'Park Sensörü', prompt: 'Önüne 15 cm\'den daha yakın bir engel geldiğinde korna çalan akıllı bir park sensörü yap.' },
  { emoji: '🚨', title: 'Oda Alarmı', prompt: 'Işık sensörünün üstü gölgelenince kırmızı LED yansın ve buzzer ötsün.' }
];

function selectPreset(prompt: string) {
  promptText.value = prompt;
}

function handleGenerate() {
  if (props.isLoading || !promptText.value.trim()) return;
  emit('generate', {
    prompt: promptText.value.trim(),
    model: selectedModel.value,
    apiKey: apiKey.value.trim() || undefined
  });
}
</script>

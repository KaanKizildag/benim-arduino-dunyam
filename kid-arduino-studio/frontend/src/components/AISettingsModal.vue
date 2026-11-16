<template>
  <div v-if="isOpen">
    <!-- Karartma Arka Planı -->
    <div
      class="fixed inset-0 z-50 bg-slate-900/50 backdrop-blur-xs flex items-center justify-center p-4"
      @click.self="$emit('close')"
    >
      <!-- Modal Kutusu -->
      <div class="bg-white rounded-3xl border-2 border-slate-200 shadow-2xl max-w-lg w-full overflow-hidden flex flex-col max-h-[90vh]">
        
        <!-- Üst Başlık -->
        <div class="p-5 border-b border-slate-200 bg-slate-50 flex items-center justify-between">
          <div class="flex items-center gap-3">
            <div class="w-10 h-10 rounded-2xl bg-indigo-600 text-white flex items-center justify-center text-xl shadow-xs">
              ⚙️
            </div>
            <div>
              <h3 class="text-base font-black text-slate-900">
                Yapay Zeka ve Model Ayarları
              </h3>
              <p class="text-xs font-bold text-slate-500">
                Yerel Ollama veya Bulut (Gemini, OpenAI, Claude) seçimi
              </p>
            </div>
          </div>

          <button
            type="button"
            @click="$emit('close')"
            class="w-8 h-8 rounded-xl border border-slate-300 bg-white hover:bg-slate-100 text-slate-600 font-bold flex items-center justify-center cursor-pointer transition text-xs"
          >
            ✕
          </button>
        </div>

        <!-- İçerik Alanı -->
        <div class="p-5 overflow-y-auto flex flex-col gap-4 text-xs">
          
          <!-- Ollama Durum Şeridi -->
          <div
            :class="[
              'p-3.5 rounded-2xl border flex items-center justify-between gap-3',
              ollamaActive
                ? 'bg-emerald-50 border-emerald-200 text-emerald-900'
                : 'bg-amber-50 border-amber-200 text-amber-900'
            ]"
          >
            <div class="flex items-center gap-2.5">
              <span class="text-xl">{{ ollamaActive ? '💻' : '🔌' }}</span>
              <div>
                <strong class="font-extrabold block text-xs">
                  {{ ollamaActive ? 'Yerel Ollama Aktif ve Hazır!' : 'Yerel Ollama Bulunamadı' }}
                </strong>
                <span class="text-[11px] font-medium opacity-80">
                  {{ ollamaActive ? 'İnternetsiz, tamamen yerel çalışabilirsin.' : 'localhost:11434 üzerinde servis algılanmadı (Bulut modeller kullanılabilir).' }}
                </span>
              </div>
            </div>
            <button
              type="button"
              @click="$emit('refresh-models')"
              class="px-2.5 py-1.5 rounded-lg border border-current text-[11px] font-extrabold bg-white/70 hover:bg-white transition shrink-0"
            >
              Yenile 🔄
            </button>
          </div>

          <!-- Model Seçimi -->
          <div>
            <label class="font-extrabold text-slate-800 block mb-1.5">
              Kullanılacak Yapay Zeka Modeli:
            </label>
            <select
              v-model="selectedModel"
              class="w-full p-3 rounded-xl border-2 border-slate-200 bg-slate-50 font-extrabold text-slate-900 focus:border-indigo-600 focus:bg-white outline-none transition cursor-pointer"
            >
              <optgroup v-if="localModels.length > 0" label="💻 Yerel Modeller (Ollama)">
                <option v-for="m in localModels" :key="m.id" :value="m.id">
                  {{ m.name }}
                </option>
              </optgroup>
              <optgroup label="☁️ Bulut Modelleri (Google, OpenAI, Anthropic)">
                <option v-for="m in cloudModels" :key="m.id" :value="m.id">
                  {{ m.name }}
                </option>
              </optgroup>
            </select>
          </div>

          <!-- Bulut API Anahtarı Alanı (Bulut modeli seçiliyse gösterilir) -->
          <div v-if="isCloudSelected" class="bg-indigo-50/50 p-4 rounded-2xl border border-indigo-100 flex flex-col gap-2">
            <div class="flex items-center justify-between">
              <label class="font-extrabold text-indigo-950">
                {{ selectedProviderName }} API Anahtarı:
              </label>
              <span class="text-[10px] text-slate-400 font-bold">
                (Tarayıcıda güvenle saklanır)
              </span>
            </div>
            <input
              type="password"
              v-model="apiKey"
              placeholder="API anahtarınızı buraya yapıştırın (örn: AIzaSy... veya sk-...)"
              class="w-full p-2.5 rounded-xl border border-indigo-200 bg-white font-mono text-xs text-slate-800 focus:border-indigo-600 outline-none"
            />
            <p class="text-[11px] text-slate-500 font-medium leading-relaxed">
              💡 <em>İpucu:</em> API anahtarı girmeden de uygulamanın tüm sayfalarını ve devre simülasyonunu üstteki hazır demolarla tam olarak deneyimleyebilirsin.
            </p>
          </div>

          <!-- Ollama URL Alanı -->
          <div>
            <label class="font-extrabold text-slate-700 block mb-1">
              Ollama Sunucu Adresi:
            </label>
            <input
              type="text"
              v-model="ollamaUrl"
              placeholder="http://127.0.0.1:11434"
              class="w-full p-2.5 rounded-xl border border-slate-200 bg-slate-50 font-mono text-xs text-slate-800"
            />
          </div>

        </div>

        <!-- Alt Butonlar -->
        <div class="p-4 border-t border-slate-200 bg-slate-50 flex items-center justify-end gap-2">
          <button
            type="button"
            @click="$emit('close')"
            class="px-4 py-2 rounded-xl border border-slate-300 font-bold text-slate-700 hover:bg-slate-100 transition cursor-pointer"
          >
            İptal
          </button>
          <button
            type="button"
            @click="saveSettings"
            class="px-5 py-2 rounded-xl bg-indigo-600 hover:bg-indigo-700 text-white font-extrabold shadow-sm transition cursor-pointer"
          >
            Ayarları Kaydet ✓
          </button>
        </div>

      </div>
    </div>
  </div>
</template>

<script setup lang="ts">
import { ref, computed, watch } from 'vue';
import type { ModelOption } from '../types/project';

const props = defineProps<{
  isOpen: boolean;
  ollamaActive: boolean;
  currentModel: string;
  localModels: ModelOption[];
  cloudModels: ModelOption[];
}>();

const emit = defineEmits<{
  (e: 'close'): void;
  (e: 'save', payload: { model: string; apiKey?: string; ollamaUrl: string }): void;
  (e: 'refresh-models'): void;
}>();

const selectedModel = ref(props.currentModel || 'ollama/qwen2.5-coder:1.5b');
const apiKey = ref(localStorage.getItem('kid_arduino_api_key') || '');
const ollamaUrl = ref(localStorage.getItem('kid_arduino_ollama_url') || 'http://127.0.0.1:11434');

watch(() => props.currentModel, (val) => {
  if (val) selectedModel.value = val;
});

const isCloudSelected = computed(() => {
  return !selectedModel.value.startsWith('ollama/') && selectedModel.value !== 'local';
});

const selectedProviderName = computed(() => {
  if (selectedModel.value.includes('gemini')) return 'Google Gemini';
  if (selectedModel.value.includes('gpt')) return 'OpenAI';
  if (selectedModel.value.includes('claude')) return 'Anthropic Claude';
  return 'Bulut Sağlayıcısı';
});

function saveSettings() {
  if (apiKey.value) {
    localStorage.setItem('kid_arduino_api_key', apiKey.value);
  }
  if (ollamaUrl.value) {
    localStorage.setItem('kid_arduino_ollama_url', ollamaUrl.value);
  }
  emit('save', {
    model: selectedModel.value,
    apiKey: apiKey.value,
    ollamaUrl: ollamaUrl.value
  });
  emit('close');
}
</script>

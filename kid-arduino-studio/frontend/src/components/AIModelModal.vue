<template>
  <div v-if="isOpen">
    <!-- Karartma Arka Planı -->
    <div
      class="fixed inset-0 z-50 bg-slate-900/60 backdrop-blur-xs flex items-center justify-center p-2 sm:p-4"
      @click.self="$emit('close')"
    >
      <!-- Modal Kutusu (Referans Görsel Tarzında) -->
      <div class="bg-white rounded-[32px] border-[3px] border-slate-900 shadow-[0_12px_0_rgba(15,23,42,0.3)] max-w-lg w-full overflow-hidden flex flex-col max-h-[90vh] animate-in fade-in zoom-in-95 duration-150">
        
        <!-- ÜST BAŞLIK ÇUBUĞU: Camgöbeği Banner + Robot İkonu + Kırmızı Kare Çarpı Butonu -->
        <div class="px-5 py-3.5 bg-[#bae6fd] border-b-[3px] border-slate-900 flex items-center justify-between shrink-0">
          <div class="flex items-center gap-3">
            <div class="w-9 h-9 rounded-xl bg-white/90 border-2 border-slate-900 flex items-center justify-center text-xl shadow-xs">
              🤖
            </div>
            <div>
              <h2 class="text-base sm:text-xl font-black text-slate-900 tracking-tight leading-tight">
                AI Asistan Seçimi
              </h2>
              <span class="text-[11px] font-bold text-slate-700">
                Projelerini tasarlayacak yapay zekayı seç
              </span>
            </div>
          </div>

          <!-- Kırmızı Kare Kapat Butonu -->
          <button
            type="button"
            @click="$emit('close')"
            class="w-8 h-8 rounded-xl bg-rose-500 hover:bg-rose-600 active:translate-y-0.5 text-white font-black text-sm flex items-center justify-center border-2 border-slate-900 shadow-[0_2px_0_#9f1239] cursor-pointer transition"
          >
            ✕
          </button>
        </div>

        <!-- OLLAMA YEREL DURUM BİLGİ BANDI -->
        <div class="px-4 py-2.5 bg-slate-50 border-b-2 border-slate-900 flex items-center justify-between text-xs">
          <div class="flex items-center gap-2">
            <span class="w-3 h-3 rounded-full border border-slate-900" :class="ollamaAvailable ? 'bg-emerald-500 shadow-[0_0_8px_#10b981]' : 'bg-amber-400'"></span>
            <span class="font-black text-slate-800">
              {{ ollamaAvailable ? 'Yerel Ollama Hazır (İnternetsiz)' : 'Yerel Ollama Bekleniyor' }}
            </span>
          </div>
          <button
            type="button"
            @click="checkOllama"
            class="px-2 py-0.5 rounded-lg bg-white hover:bg-slate-100 border border-slate-900 text-[10px] font-black text-slate-700 cursor-pointer shadow-xs"
          >
            Yenile 🔄
          </button>
        </div>

        <!-- MODEL LİSTESİ (Referans Görsel 1 Sağ Sütun) -->
        <div class="p-5 flex flex-col gap-3 overflow-y-auto">
          
          <!-- 1. Local Model (Ollama) -->
          <div
            @click="selectedModel = 'ollama/qwen2.5-coder:1.5b'"
            :class="[
              'p-3.5 rounded-2xl border-[2.5px] flex items-center gap-3 relative select-none cursor-pointer transition-all shadow-[0_3px_0_#0f172a]',
              selectedModel.includes('ollama') || selectedModel === 'local'
                ? 'border-[#0284c7] bg-[#f0f9ff] ring-2 ring-[#38bdf8]'
                : 'border-slate-900 bg-white hover:bg-slate-50'
            ]"
          >
            <!-- Sarı Zeminli Sevimli Robot İkonu -->
            <div class="w-12 h-12 rounded-2xl bg-[#fef08a] border-2 border-slate-900 flex items-center justify-center text-2xl shrink-0 shadow-xs">
              🤖
            </div>
            <div class="min-w-0 flex-1">
              <div class="text-sm font-black text-slate-900 flex items-center gap-1.5">
                <span>Local Model</span>
                <span class="text-[10px] bg-sky-100 text-sky-800 px-1.5 py-0.2 rounded-md font-bold">Yerel / Gizli</span>
              </div>
              <div class="text-[11px] font-bold text-slate-500 truncate mt-0.5">
                (Ollama - qwen2.5-coder:7b)
              </div>
            </div>
            <!-- Yeşil 'Aktif' Rozeti -->
            <span
              v-if="selectedModel.includes('ollama') || selectedModel === 'local'"
              class="px-3 py-1 rounded-full bg-[#4ade80] text-slate-950 text-xs font-black border-2 border-slate-900 shadow-xs"
            >
              Aktif
            </span>
          </div>

          <!-- 2. Google Gemini -->
          <div
            @click="selectedModel = 'gemini/gemini-2.0-flash'"
            :class="[
              'p-3.5 rounded-2xl border-[2.5px] flex items-center gap-3 relative select-none cursor-pointer transition-all shadow-[0_3px_0_#0f172a]',
              selectedModel.includes('gemini')
                ? 'border-[#0284c7] bg-[#f0f9ff] ring-2 ring-[#38bdf8]'
                : 'border-slate-900 bg-white hover:bg-slate-50'
            ]"
          >
            <!-- 4 Köşeli Renkli Yıldız İkonu -->
            <div class="w-12 h-12 rounded-2xl bg-white border-2 border-slate-900 flex items-center justify-center text-xl shrink-0 shadow-xs">
              <svg class="w-7 h-7" viewBox="0 0 24 24">
                <path d="M12 2L14.5 9.5L22 12L14.5 14.5L12 22L9.5 14.5L2 12L9.5 9.5L12 2Z" fill="url(#geminiGradModal)" />
                <defs>
                  <linearGradient id="geminiGradModal" x1="0%" y1="0%" x2="100%" y2="100%">
                    <stop offset="0%" stop-color="#38bdf8" />
                    <stop offset="50%" stop-color="#818cf8" />
                    <stop offset="100%" stop-color="#f43f5e" />
                  </linearGradient>
                </defs>
              </svg>
            </div>
            <div class="min-w-0 flex-1">
              <div class="text-sm font-black text-slate-900">Google Gemini</div>
              <div class="text-[11px] font-bold text-slate-500 truncate mt-0.5">Gemini 2.0 Flash (Hızlı & Zeki)</div>
            </div>
            <span
              v-if="selectedModel.includes('gemini')"
              class="px-3 py-1 rounded-full bg-[#4ade80] text-slate-950 text-xs font-black border-2 border-slate-900 shadow-xs"
            >
              Aktif
            </span>
          </div>

          <!-- 3. OpenAI -->
          <div
            @click="selectedModel = 'gpt-4o-mini'"
            :class="[
              'p-3.5 rounded-2xl border-[2.5px] flex items-center gap-3 relative select-none cursor-pointer transition-all shadow-[0_3px_0_#0f172a]',
              selectedModel.includes('gpt')
                ? 'border-[#0284c7] bg-[#f0f9ff] ring-2 ring-[#38bdf8]'
                : 'border-slate-900 bg-white hover:bg-slate-50'
            ]"
          >
            <div class="w-12 h-12 rounded-2xl bg-slate-900 border-2 border-slate-900 flex items-center justify-center text-white text-xl shrink-0 shadow-xs">
              <svg class="w-7 h-7 fill-current" viewBox="0 0 24 24">
                <path d="M22.2819 9.8211a5.9847 5.9847 0 0 0-.5157-4.9108 6.0462 6.0462 0 0 0-6.5098-2.9A6.0651 6.0651 0 0 0 4.9807 4.1818a5.9847 5.9847 0 0 0-3.9977 2.9 6.0462 6.0462 0 0 0 .7427 7.0966 5.98 5.98 0 0 0 .511 4.9107 6.051 6.051 0 0 0 6.5146 2.9001A5.9847 5.9847 0 0 0 13.2599 24a6.0557 6.0557 0 0 0 5.7718-4.2058 5.9894 5.9894 0 0 0 3.9977-2.9001 6.0557 6.0557 0 0 0-.7475-7.0729zm-9.022 12.6081a4.4755 4.4755 0 0 1-2.8764-1.0408l.1419-.0804 4.7783-2.7582a.7948.7948 0 0 0 .3927-.6813v-6.7369l2.02 1.1683a.071.071 0 0 1 .038.052v5.5826a4.5045 4.5045 0 0 1-4.4945 4.4947z"/>
              </svg>
            </div>
            <div class="min-w-0 flex-1">
              <div class="text-sm font-black text-slate-900">OpenAI</div>
              <div class="text-[11px] font-bold text-slate-500 truncate mt-0.5">GPT-4o Mini / GPT-4o</div>
            </div>
            <span
              v-if="selectedModel.includes('gpt')"
              class="px-3 py-1 rounded-full bg-[#4ade80] text-slate-950 text-xs font-black border-2 border-slate-900 shadow-xs"
            >
              Aktif
            </span>
          </div>

          <!-- 4. Claude -->
          <div
            @click="selectedModel = 'claude-3-5-haiku-20241022'"
            :class="[
              'p-3.5 rounded-2xl border-[2.5px] flex items-center gap-3 relative select-none cursor-pointer transition-all shadow-[0_3px_0_#0f172a]',
              selectedModel.includes('claude')
                ? 'border-[#0284c7] bg-[#f0f9ff] ring-2 ring-[#38bdf8]'
                : 'border-slate-900 bg-white hover:bg-slate-50'
            ]"
          >
            <div class="w-12 h-12 rounded-2xl bg-[#d97706] border-2 border-slate-900 flex items-center justify-center text-white text-lg font-black shrink-0 shadow-xs">
              A\
            </div>
            <div class="min-w-0 flex-1">
              <div class="text-sm font-black text-slate-900">Claude</div>
              <div class="text-[11px] font-bold text-slate-500 truncate mt-0.5">Anthropic Claude 3.5 Haiku</div>
            </div>
            <span
              v-if="selectedModel.includes('claude')"
              class="px-3 py-1 rounded-full bg-[#4ade80] text-slate-950 text-xs font-black border-2 border-slate-900 shadow-xs"
            >
              Aktif
            </span>
          </div>

          <!-- BULUT API ANAHTARI GİRİŞİ -->
          <div v-if="isCloud" class="mt-2 p-3 bg-sky-50 rounded-2xl border-2 border-slate-900 flex flex-col gap-1.5">
            <label class="text-xs font-black text-slate-900 flex items-center justify-between">
              <span>🔑 {{ selectedProviderName }} API Anahtarı:</span>
              <span class="text-[10px] text-slate-500 font-bold">(İsteğe bağlı)</span>
            </label>
            <input
              type="password"
              v-model="apiKey"
              placeholder="API anahtarını buraya yapıştır..."
              class="w-full px-3 py-2 rounded-xl border-2 border-slate-900 text-xs font-mono bg-white outline-none focus:ring-2 focus:ring-sky-400"
            />
          </div>

        </div>

        <!-- ALT BUTON: KAYDET VE BAŞLA! (Yıldızlı 3D Buton) -->
        <div class="p-4 sm:p-5 bg-slate-50 border-t-[3px] border-slate-900 flex items-center justify-center shrink-0">
          <div class="relative">
            <span class="absolute -left-6 -top-2 text-amber-400 text-2xl select-none animate-pulse">⭐</span>
            <span class="absolute -right-5 -bottom-1 text-emerald-500 text-lg select-none">✨</span>
            <span class="absolute right-0 -top-3 text-sky-400 text-xs select-none">✦</span>

            <button
              type="button"
              @click="handleSave"
              class="px-12 py-3 rounded-full bg-gradient-to-r from-[#38bdf8] to-[#0284c7] hover:from-[#7dd3fc] hover:to-[#0369a1] active:translate-y-1 active:shadow-none text-slate-950 font-black text-sm sm:text-base border-[2.5px] border-slate-900 shadow-[0_5px_0_#0f172a] transition-all cursor-pointer flex items-center gap-2"
            >
              <span>Kaydet ve Başla! 🚀</span>
            </button>
          </div>
        </div>

      </div>
    </div>
  </div>
</template>

<script setup lang="ts">
import { ref, computed, watch, onMounted } from 'vue';

const props = defineProps<{
  isOpen: boolean;
  currentModel: string;
}>();

const emit = defineEmits<{
  (e: 'close'): void;
  (e: 'save', payload: { model: string; apiKey?: string }): void;
}>();

const selectedModel = ref(props.currentModel || 'ollama/qwen2.5-coder:1.5b');
const apiKey = ref(localStorage.getItem('kid_arduino_api_key') || '');
const ollamaAvailable = ref(true);

watch(() => props.currentModel, (v) => {
  if (v) selectedModel.value = v;
});

const isCloud = computed(() => {
  return !selectedModel.value.startsWith('ollama') && selectedModel.value !== 'local';
});

const selectedProviderName = computed(() => {
  if (selectedModel.value.includes('gemini')) return 'Google Gemini';
  if (selectedModel.value.includes('gpt')) return 'OpenAI';
  if (selectedModel.value.includes('claude')) return 'Anthropic Claude';
  return 'Bulut';
});

async function checkOllama() {
  try {
    const res = await fetch('/api/models');
    if (res.ok) {
      const data = await res.json();
      ollamaAvailable.value = data.ollama_active;
    }
  } catch {
    ollamaAvailable.value = false;
  }
}

function handleSave() {
  if (apiKey.value) {
    localStorage.setItem('kid_arduino_api_key', apiKey.value);
  }
  emit('save', {
    model: selectedModel.value,
    apiKey: apiKey.value || undefined
  });
  emit('close');
}

onMounted(() => {
  checkOllama();
});
</script>
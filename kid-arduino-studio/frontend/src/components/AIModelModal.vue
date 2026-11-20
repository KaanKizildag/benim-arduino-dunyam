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
              {{ ollamaAvailable ? `Yerel Ollama Hazır (${localModels.length} Model Kurulu)` : 'Yerel Ollama Bekleniyor' }}
            </span>
          </div>
          <button
            type="button"
            @click="checkOllama"
            class="px-2 py-0.5 rounded-lg bg-white hover:bg-slate-100 border border-slate-900 text-[10px] font-black text-slate-700 cursor-pointer shadow-xs"
          >
            {{ isLoadingModels ? 'Aranıyor...' : 'Yenile 🔄' }}
          </button>
        </div>

        <!-- MODEL LİSTESİ (Referans Görsel 1 Sağ Sütun) -->
        <div class="p-5 flex flex-col gap-3 overflow-y-auto">
          
          <!-- 1. Local Model (Ollama - Kurulu Tüm Modeller) -->
          <div
            @click="selectOllamaCard"
            :class="[
              'p-3.5 rounded-2xl border-[2.5px] flex flex-col gap-2.5 relative select-none cursor-pointer transition-all shadow-[0_3px_0_#0f172a]',
              isOllamaSelected
                ? 'border-[#0284c7] bg-[#f0f9ff] ring-2 ring-[#38bdf8]'
                : 'border-slate-900 bg-white hover:bg-slate-50'
            ]"
          >
            <div class="flex items-center gap-3">
              <!-- Sarı Zeminli Sevimli Robot İkonu -->
              <div class="w-12 h-12 rounded-2xl bg-[#fef08a] border-2 border-slate-900 flex items-center justify-center text-2xl shrink-0 shadow-xs">
                🤖
              </div>
              <div class="min-w-0 flex-1">
                <div class="text-sm font-black text-slate-900 flex items-center gap-1.5 flex-wrap">
                  <span>Local Model (Ollama)</span>
                  <span class="text-[10px] bg-sky-100 text-sky-800 px-1.5 py-0.5 rounded-md font-bold border border-sky-300">
                    Yerel / Gizli ({{ localModels.length }})
                  </span>
                </div>
                <div class="text-[11px] font-bold text-slate-600 truncate mt-0.5">
                  {{ activeOllamaSubtitle }}
                </div>
              </div>
              <!-- Yeşil 'Aktif' Rozeti -->
              <span
                v-if="isOllamaSelected"
                class="px-3 py-1 rounded-full bg-[#4ade80] text-slate-950 text-xs font-black border-2 border-slate-900 shadow-xs shrink-0"
              >
                Aktif
              </span>
            </div>

            <!-- Ollama Üzerinde Kurulu Modellerin Seçim Listesi -->
            <div
              v-if="localModels.length > 0"
              class="pt-2 border-t-2 border-dashed border-slate-900/15 flex flex-col gap-1.5"
              @click.stop
            >
              <div class="text-[10px] font-black text-slate-500 uppercase tracking-wider px-0.5">
                Kurulu Ollama Modelleri ({{ localModels.length }} adet):
              </div>
              <div class="grid grid-cols-1 gap-1.5 max-h-40 overflow-y-auto pr-0.5">
                <button
                  v-for="m in localModels"
                  :key="m.id"
                  type="button"
                  @click="selectedModel = m.id"
                  :class="[
                    'w-full px-3 py-2 rounded-xl border-2 text-left flex items-center justify-between gap-2 transition cursor-pointer',
                    selectedModel === m.id
                      ? 'bg-[#fef08a] border-slate-900 text-slate-950 shadow-[0_2px_0_#0f172a]'
                      : 'bg-white/90 hover:bg-white border-slate-300 hover:border-slate-900 text-slate-700'
                  ]"
                >
                  <div class="flex items-center gap-2 min-w-0">
                    <span
                      class="w-2.5 h-2.5 rounded-full border border-slate-900 shrink-0"
                      :class="selectedModel === m.id ? 'bg-emerald-500' : 'bg-slate-200'"
                    ></span>
                    <span class="text-xs font-black truncate">{{ m.raw_name || m.id.replace('ollama/', '') }}</span>
                  </div>
                  <div class="flex items-center gap-1.5 shrink-0">
                    <span v-if="extractSizeBadge(m.name)" class="text-[10px] font-bold px-1.5 py-0.5 rounded-md bg-slate-100 border border-slate-300 text-slate-700">
                      {{ extractSizeBadge(m.name) }}
                    </span>
                    <span
                      v-if="selectedModel === m.id"
                      class="text-[10px] font-black px-1.5 py-0.5 rounded-md bg-emerald-500 text-white border border-slate-900"
                    >
                      Seçili
                    </span>
                  </div>
                </button>
              </div>
            </div>

            <!-- Kurulu Model Bulunamadıysa Uyarı -->
            <div
              v-else
              class="pt-2 border-t-2 border-dashed border-slate-900/15 text-[11px] font-bold text-amber-800 bg-amber-50/80 px-2.5 py-1.5 rounded-xl border border-amber-300"
            >
              Ollama üzerinde kurulu model algılanamadı. Terminalden <code class="font-mono bg-white px-1 py-0.5 rounded border">ollama list</code> kontrol edip <b>Yenile 🔄</b> butonuna basabilirsin.
            </div>
          </div>

          <!-- 2. Google Gemini (Alt Model Seçim Listesi ile) -->
          <div
            @click="selectGeminiCard"
            :class="[
              'p-3.5 rounded-2xl border-[2.5px] flex flex-col gap-2.5 relative select-none cursor-pointer transition-all shadow-[0_3px_0_#0f172a]',
              isGeminiSelected
                ? 'border-[#0284c7] bg-[#f0f9ff] ring-2 ring-[#38bdf8]'
                : 'border-slate-900 bg-white hover:bg-slate-50'
            ]"
          >
            <div class="flex items-center gap-3">
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
                <div class="text-sm font-black text-slate-900 flex items-center gap-1.5 flex-wrap">
                  <span>Google Gemini</span>
                  <span class="text-[10px] bg-indigo-100 text-indigo-800 px-1.5 py-0.5 rounded-md font-bold border border-indigo-300">
                    {{ geminiModels.length }} Model
                  </span>
                </div>
                <div class="text-[11px] font-bold text-slate-600 truncate mt-0.5">
                  {{ activeGeminiSubtitle }}
                </div>
              </div>
              <span
                v-if="isGeminiSelected"
                class="px-3 py-1 rounded-full bg-[#4ade80] text-slate-950 text-xs font-black border-2 border-slate-900 shadow-xs shrink-0"
              >
                Aktif
              </span>
            </div>

            <!-- Google Gemini Seçiliyse Alt Modelleri Göster -->
            <div
              v-if="isGeminiSelected"
              class="pt-2 border-t-2 border-dashed border-slate-900/15 flex flex-col gap-1.5"
              @click.stop
            >
              <div class="flex items-center justify-between px-0.5">
                <span class="text-[10px] font-black text-slate-500 uppercase tracking-wider">
                  Gemini Modeli Seç ({{ geminiModels.length }} adet):
                </span>
                <button
                  v-if="apiKey.trim()"
                  type="button"
                  @click="checkOllama"
                  class="text-[10px] font-black text-sky-700 hover:text-sky-900 underline cursor-pointer"
                >
                  {{ isLoadingModels ? 'Yükleniyor...' : 'Token ile Modelleri Sorgula 🔄' }}
                </button>
              </div>
              <div class="grid grid-cols-1 gap-1.5 max-h-40 overflow-y-auto pr-0.5">
                <button
                  v-for="gm in geminiModels"
                  :key="gm.id"
                  type="button"
                  @click="selectedModel = gm.id"
                  :class="[
                    'w-full px-3 py-2 rounded-xl border-2 text-left flex items-center justify-between gap-2 transition cursor-pointer',
                    selectedModel === gm.id
                      ? 'bg-[#fef08a] border-slate-900 text-slate-950 shadow-[0_2px_0_#0f172a]'
                      : 'bg-white/90 hover:bg-white border-slate-300 hover:border-slate-900 text-slate-700'
                  ]"
                >
                  <div class="flex items-center gap-2 min-w-0">
                    <span
                      class="w-2.5 h-2.5 rounded-full border border-slate-900 shrink-0"
                      :class="selectedModel === gm.id ? 'bg-emerald-500' : 'bg-slate-200'"
                    ></span>
                    <span class="text-xs font-black truncate">{{ gm.name }}</span>
                  </div>
                  <span
                    v-if="selectedModel === gm.id"
                    class="text-[10px] font-black px-1.5 py-0.5 rounded-md bg-emerald-500 text-white border border-slate-900 shrink-0"
                  >
                    Seçili
                  </span>
                </button>
              </div>
            </div>
          </div>

          <!-- 3. OpenAI (Alt Model Seçim Listesi ile) -->
          <div
            @click="selectOpenAICard"
            :class="[
              'p-3.5 rounded-2xl border-[2.5px] flex flex-col gap-2.5 relative select-none cursor-pointer transition-all shadow-[0_3px_0_#0f172a]',
              isOpenAISelected
                ? 'border-[#0284c7] bg-[#f0f9ff] ring-2 ring-[#38bdf8]'
                : 'border-slate-900 bg-white hover:bg-slate-50'
            ]"
          >
            <div class="flex items-center gap-3">
              <div class="w-12 h-12 rounded-2xl bg-slate-900 border-2 border-slate-900 flex items-center justify-center text-white text-xl shrink-0 shadow-xs">
                <svg class="w-7 h-7 fill-current" viewBox="0 0 24 24">
                  <path d="M22.2819 9.8211a5.9847 5.9847 0 0 0-.5157-4.9108 6.0462 6.0462 0 0 0-6.5098-2.9A6.0651 6.0651 0 0 0 4.9807 4.1818a5.9847 5.9847 0 0 0-3.9977 2.9 6.0462 6.0462 0 0 0 .7427 7.0966 5.98 5.98 0 0 0 .511 4.9107 6.051 6.051 0 0 0 6.5146 2.9001A5.9847 5.9847 0 0 0 13.2599 24a6.0557 6.0557 0 0 0 5.7718-4.2058 5.9894 5.9894 0 0 0 3.9977-2.9001 6.0557 6.0557 0 0 0-.7475-7.0729zm-9.022 12.6081a4.4755 4.4755 0 0 1-2.8764-1.0408l.1419-.0804 4.7783-2.7582a.7948.7948 0 0 0 .3927-.6813v-6.7369l2.02 1.1683a.071.071 0 0 1 .038.052v5.5826a4.5045 4.5045 0 0 1-4.4945 4.4947z"/>
                </svg>
              </div>
              <div class="min-w-0 flex-1">
                <div class="text-sm font-black text-slate-900">OpenAI</div>
                <div class="text-[11px] font-bold text-slate-600 truncate mt-0.5">
                  {{ isOpenAISelected ? `Seçili: ${selectedModel}` : 'GPT-4o Mini / GPT-4o / GPT-4.1 Mini' }}
                </div>
              </div>
              <span
                v-if="isOpenAISelected"
                class="px-3 py-1 rounded-full bg-[#4ade80] text-slate-950 text-xs font-black border-2 border-slate-900 shadow-xs shrink-0"
              >
                Aktif
              </span>
            </div>

            <div
              v-if="isOpenAISelected"
              class="pt-2 border-t-2 border-dashed border-slate-900/15 grid grid-cols-1 gap-1.5"
              @click.stop
            >
              <button
                v-for="om in openaiModels"
                :key="om.id"
                type="button"
                @click="selectedModel = om.id"
                :class="[
                  'w-full px-3 py-2 rounded-xl border-2 text-left flex items-center justify-between gap-2 transition cursor-pointer',
                  selectedModel === om.id
                    ? 'bg-[#fef08a] border-slate-900 text-slate-950 shadow-[0_2px_0_#0f172a]'
                    : 'bg-white/90 hover:bg-white border-slate-300 hover:border-slate-900 text-slate-700'
                ]"
              >
                <span class="text-xs font-black truncate">{{ om.name }}</span>
                <span
                  v-if="selectedModel === om.id"
                  class="text-[10px] font-black px-1.5 py-0.5 rounded-md bg-emerald-500 text-white border border-slate-900 shrink-0"
                >
                  Seçili
                </span>
              </button>
            </div>
          </div>

          <!-- 4. Claude (Alt Model Seçim Listesi ile) -->
          <div
            @click="selectClaudeCard"
            :class="[
              'p-3.5 rounded-2xl border-[2.5px] flex flex-col gap-2.5 relative select-none cursor-pointer transition-all shadow-[0_3px_0_#0f172a]',
              isClaudeSelected
                ? 'border-[#0284c7] bg-[#f0f9ff] ring-2 ring-[#38bdf8]'
                : 'border-slate-900 bg-white hover:bg-slate-50'
            ]"
          >
            <div class="flex items-center gap-3">
              <div class="w-12 h-12 rounded-2xl bg-[#d97706] border-2 border-slate-900 flex items-center justify-center text-white text-lg font-black shrink-0 shadow-xs">
                A\
              </div>
              <div class="min-w-0 flex-1">
                <div class="text-sm font-black text-slate-900">Claude</div>
                <div class="text-[11px] font-bold text-slate-600 truncate mt-0.5">
                  {{ isClaudeSelected ? `Seçili: ${selectedModel}` : 'Anthropic Claude 3.5 Haiku / Sonnet' }}
                </div>
              </div>
              <span
                v-if="isClaudeSelected"
                class="px-3 py-1 rounded-full bg-[#4ade80] text-slate-950 text-xs font-black border-2 border-slate-900 shadow-xs shrink-0"
              >
                Aktif
              </span>
            </div>

            <div
              v-if="isClaudeSelected"
              class="pt-2 border-t-2 border-dashed border-slate-900/15 grid grid-cols-1 gap-1.5"
              @click.stop
            >
              <button
                v-for="cm in claudeModels"
                :key="cm.id"
                type="button"
                @click="selectedModel = cm.id"
                :class="[
                  'w-full px-3 py-2 rounded-xl border-2 text-left flex items-center justify-between gap-2 transition cursor-pointer',
                  selectedModel === cm.id
                    ? 'bg-[#fef08a] border-slate-900 text-slate-950 shadow-[0_2px_0_#0f172a]'
                    : 'bg-white/90 hover:bg-white border-slate-300 hover:border-slate-900 text-slate-700'
                ]"
              >
                <span class="text-xs font-black truncate">{{ cm.name }}</span>
                <span
                  v-if="selectedModel === cm.id"
                  class="text-[10px] font-black px-1.5 py-0.5 rounded-md bg-emerald-500 text-white border border-slate-900 shrink-0"
                >
                  Seçili
                </span>
              </button>
            </div>
          </div>

          <!-- BULUT API ANAHTARI GİRİŞİ -->
          <div v-if="isCloud" class="mt-1 p-3 bg-sky-50 rounded-2xl border-2 border-slate-900 flex flex-col gap-1.5">
            <label class="text-xs font-black text-slate-900 flex items-center justify-between">
              <span>🔑 {{ selectedProviderName }} API Anahtarı (Token):</span>
              <span class="text-[10px] text-slate-500 font-bold">(Tarayıcıya kaydedilir)</span>
            </label>
            <div class="flex items-center gap-1.5">
              <input
                type="password"
                v-model="apiKey"
                placeholder="API anahtarını (AIza...) buraya yapıştır..."
                class="flex-1 px-3 py-2 rounded-xl border-2 border-slate-900 text-xs font-mono bg-white outline-none focus:ring-2 focus:ring-sky-400"
                @change="onApiKeyChange"
              />
              <button
                v-if="isGeminiSelected && apiKey.trim()"
                type="button"
                @click="checkOllama"
                class="px-3 py-2 rounded-xl bg-amber-200 hover:bg-amber-300 border-2 border-slate-900 text-[11px] font-black text-slate-900 cursor-pointer shrink-0 shadow-2xs"
                title="Bu token ile erişilebilen Gemini modellerini listele"
              >
                Modelleri Getir 🔄
              </button>
            </div>
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
import type { ModelInfo, ModelsResponse } from '../types/project';

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
const isLoadingModels = ref(false);
const localModels = ref<ModelInfo[]>([]);
const cloudModels = ref<ModelInfo[]>([
  { id: 'gemini/gemini-2.5-flash', name: 'Gemini 2.5 Flash (En Yeni & Hızlı)', provider: 'gemini', category: 'Google Gemini', badge: '☁️ Bulut' },
  { id: 'gemini/gemini-2.5-pro', name: 'Gemini 2.5 Pro (Gelişmiş Muhakeme)', provider: 'gemini', category: 'Google Gemini', badge: '☁️ Bulut' },
  { id: 'gemini/gemini-2.0-flash', name: 'Gemini 2.0 Flash (Hızlı & Dengeli)', provider: 'gemini', category: 'Google Gemini', badge: '☁️ Bulut' },
  { id: 'gemini/gemini-2.0-flash-lite', name: 'Gemini 2.0 Flash Lite (Hafif & Ekonomik)', provider: 'gemini', category: 'Google Gemini', badge: '☁️ Bulut' },
  { id: 'gemini/gemini-1.5-flash', name: 'Gemini 1.5 Flash (Kararlı)', provider: 'gemini', category: 'Google Gemini', badge: '☁️ Bulut' },
  { id: 'gemini/gemini-1.5-pro', name: 'Gemini 1.5 Pro (Derin Analiz)', provider: 'gemini', category: 'Google Gemini', badge: '☁️ Bulut' },
  { id: 'gpt-4o-mini', name: 'GPT-4o Mini (Hızlı & Ekonomik)', provider: 'openai', category: 'OpenAI', badge: '☁️ Bulut' },
  { id: 'gpt-4o', name: 'GPT-4o (Amiral Gemisi)', provider: 'openai', category: 'OpenAI', badge: '☁️ Bulut' },
  { id: 'gpt-4.1-mini', name: 'GPT-4.1 Mini (Yeni Nesil Kodlama)', provider: 'openai', category: 'OpenAI', badge: '☁️ Bulut' },
  { id: 'claude-3-5-haiku-20241022', name: 'Claude 3.5 Haiku (Hızlı & Canlı)', provider: 'anthropic', category: 'Anthropic Claude', badge: '☁️ Bulut' },
  { id: 'claude-3-5-sonnet-20241022', name: 'Claude 3.5 Sonnet (Kodlama Uzmanı)', provider: 'anthropic', category: 'Anthropic Claude', badge: '☁️ Bulut' }
]);

watch(() => props.currentModel, (v) => {
  if (v) selectedModel.value = v;
});

watch(() => props.isOpen, (open) => {
  if (open) {
    checkOllama();
  }
});

const isOllamaSelected = computed(() => {
  return selectedModel.value.startsWith('ollama') || selectedModel.value === 'local';
});

const isGeminiSelected = computed(() => {
  return selectedModel.value.includes('gemini');
});

const isOpenAISelected = computed(() => {
  return selectedModel.value.includes('gpt');
});

const isClaudeSelected = computed(() => {
  return selectedModel.value.includes('claude');
});

const geminiModels = computed(() => {
  return cloudModels.value.filter(m => m.provider === 'gemini' || m.id.includes('gemini'));
});

const openaiModels = computed(() => {
  return cloudModels.value.filter(m => m.provider === 'openai' || m.id.includes('gpt'));
});

const claudeModels = computed(() => {
  return cloudModels.value.filter(m => m.provider === 'anthropic' || m.id.includes('claude'));
});

const activeOllamaSubtitle = computed(() => {
  if (isOllamaSelected.value) {
    const found = localModels.value.find(m => m.id === selectedModel.value);
    if (found) return `Seçili: ${found.name}`;
    return `Seçili: ${selectedModel.value.replace('ollama/', '')}`;
  }
  if (localModels.value.length > 0 && localModels.value[0]) {
    return `${localModels.value.length} kurulu model (${localModels.value[0].raw_name || localModels.value[0].id.replace('ollama/', '')} ...)`;
  }
  return 'Yerel Ollama Modelleri';
});

const activeGeminiSubtitle = computed(() => {
  if (isGeminiSelected.value) {
    const found = geminiModels.value.find(m => m.id === selectedModel.value);
    if (found) return `Seçili: ${found.name}`;
    return `Seçili: ${selectedModel.value.replace('gemini/', '')}`;
  }
  return 'Gemini 2.5 Flash / 2.5 Pro / 2.0 Flash / 1.5 Pro';
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

function extractSizeBadge(displayName: string): string {
  const m = displayName.match(/\(([^)]+)\)/);
  return m && m[1] ? m[1] : '';
}

function selectOllamaCard() {
  if (isOllamaSelected.value) return;
  if (localModels.value.length > 0 && localModels.value[0]) {
    selectedModel.value = localModels.value[0].id;
  } else {
    selectedModel.value = 'ollama/qwen2.5-coder:1.5b';
  }
}

function selectGeminiCard() {
  if (isGeminiSelected.value) return;
  if (geminiModels.value.length > 0 && geminiModels.value[0]) {
    selectedModel.value = geminiModels.value[0].id;
  } else {
    selectedModel.value = 'gemini/gemini-2.0-flash';
  }
}

function selectOpenAICard() {
  if (isOpenAISelected.value) return;
  if (openaiModels.value.length > 0 && openaiModels.value[0]) {
    selectedModel.value = openaiModels.value[0].id;
  } else {
    selectedModel.value = 'gpt-4o-mini';
  }
}

function selectClaudeCard() {
  if (isClaudeSelected.value) return;
  if (claudeModels.value.length > 0 && claudeModels.value[0]) {
    selectedModel.value = claudeModels.value[0].id;
  } else {
    selectedModel.value = 'claude-3-5-haiku-20241022';
  }
}

function onApiKeyChange() {
  if (apiKey.value.trim()) {
    localStorage.setItem('kid_arduino_api_key', apiKey.value.trim());
    if (isGeminiSelected.value) {
      void checkOllama();
    }
  }
}

async function checkOllama() {
  isLoadingModels.value = true;
  try {
    const queryParam =
      apiKey.value.trim() && isGeminiSelected.value
        ? `?gemini_api_key=${encodeURIComponent(apiKey.value.trim())}`
        : '';
    const res = await fetch(`/api/models${queryParam}`);
    if (res.ok) {
      const data: ModelsResponse = await res.json();
      ollamaAvailable.value = data.ollama_active;
      localModels.value = data.local_models || [];
      if (Array.isArray(data.cloud_models) && data.cloud_models.length > 0) {
        cloudModels.value = data.cloud_models;
      }
      if (
        isOllamaSelected.value &&
        localModels.value.length > 0 &&
        !localModels.value.some(m => m.id === selectedModel.value) &&
        localModels.value[0]
      ) {
        selectedModel.value = localModels.value[0].id;
      }
      if (
        isGeminiSelected.value &&
        geminiModels.value.length > 0 &&
        !geminiModels.value.some(m => m.id === selectedModel.value) &&
        geminiModels.value[0]
      ) {
        selectedModel.value = geminiModels.value[0].id;
      }
    }
  } catch {
    ollamaAvailable.value = false;
  } finally {
    isLoadingModels.value = false;
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
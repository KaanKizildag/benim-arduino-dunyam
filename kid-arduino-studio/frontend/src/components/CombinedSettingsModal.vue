<template>
  <div v-if="isOpen">
    <!-- Karartma Arka Planı -->
    <div
      class="fixed inset-0 z-50 bg-slate-900/60 backdrop-blur-xs flex items-center justify-center p-3 sm:p-4"
      @click.self="$emit('close')"
    >
      <!-- Modal Kutusu (Referans Görsel 1 ile Birebir Aynı) -->
      <div class="bg-white rounded-[32px] border-[3px] border-slate-900 shadow-[0_12px_0_rgba(15,23,42,0.25)] max-w-2xl w-full overflow-hidden flex flex-col animate-in fade-in zoom-in-95 duration-150">
        
        <!-- Üst Başlık Çubuğu (Nane Yeşili Banner + Kırmızı Çarpı Butonu) -->
        <div class="px-5 py-3.5 bg-[#a7f3d0] border-b-[3px] border-slate-900 flex items-center justify-between">
          <div class="flex items-center gap-2.5">
            <span class="text-2xl drop-shadow-xs">🧰</span>
            <h2 class="text-lg sm:text-xl font-black text-slate-900 tracking-tight">
              Malzeme Çantası & AI Ayarları
            </h2>
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

        <!-- Ana İçerik: İki Sütunlu Düzen (Sol: Malzeme Çantam, Sağ: AI Asistan Seçimi) -->
        <div class="p-5 sm:p-6 grid grid-cols-1 md:grid-cols-2 gap-6 bg-white overflow-y-auto max-h-[75vh]">
          
          <!-- SOL SÜTUN: MALZEME ÇANTAM -->
          <div class="flex flex-col gap-3">
            <div class="text-center md:text-left">
              <h3 class="text-base font-black text-slate-900">
                Malzeme Çantam
              </h3>
            </div>

            <!-- Parça Kartları Izgarası (2 sütun x 3 satır = 6 parça) -->
            <div class="grid grid-cols-2 gap-2.5">
              
              <!-- 1. Arduino Uno -->
              <div
                @click="toggleItem('ARDUINO_UNO')"
                :class="[
                  'p-3 rounded-2xl border-2 border-slate-900 flex flex-col items-center justify-center text-center relative select-none cursor-pointer transition-all shadow-[0_3px_0_#1e293b]',
                  isSelected('ARDUINO_UNO') ? 'bg-[#bbf7d0]' : 'bg-slate-50'
                ]"
              >
                <span class="text-3xl mb-1">🤖</span>
                <span class="text-xs font-black text-slate-900">Arduino Uno</span>
                <span
                  v-if="isSelected('ARDUINO_UNO')"
                  class="absolute -top-1.5 -right-1.5 w-5 h-5 rounded-full bg-emerald-500 border border-slate-900 text-white font-black text-[10px] flex items-center justify-center shadow-xs"
                >
                  ✓
                </span>
              </div>

              <!-- 2. Breadboard -->
              <div
                @click="toggleItem('BREADBOARD')"
                :class="[
                  'p-3 rounded-2xl border-2 border-slate-900 flex flex-col items-center justify-center text-center relative select-none cursor-pointer transition-all shadow-[0_3px_0_#1e293b]',
                  isSelected('BREADBOARD') ? 'bg-amber-50' : 'bg-slate-50'
                ]"
              >
                <span class="text-3xl mb-1">🍞</span>
                <span class="text-xs font-black text-slate-900">Breadboard</span>
                <span
                  v-if="isSelected('BREADBOARD')"
                  class="absolute -top-1.5 -right-1.5 w-5 h-5 rounded-full bg-emerald-500 border border-slate-900 text-white font-black text-[10px] flex items-center justify-center shadow-xs"
                >
                  ✓
                </span>
              </div>

              <!-- 3. Kırmızı LED -->
              <div
                @click="toggleItem('LED_RED')"
                :class="[
                  'p-3 rounded-2xl border-2 border-slate-900 flex flex-col items-center justify-center text-center relative select-none cursor-pointer transition-all shadow-[0_3px_0_#1e293b]',
                  isSelected('LED_RED') ? 'bg-rose-100' : 'bg-slate-50'
                ]"
              >
                <span class="text-3xl mb-1">🔴</span>
                <span class="text-xs font-black text-slate-900">Kırmızı LED</span>
                <span
                  v-if="isSelected('LED_RED')"
                  class="absolute -top-1.5 -right-1.5 w-5 h-5 rounded-full bg-emerald-500 border border-slate-900 text-white font-black text-[10px] flex items-center justify-center shadow-xs"
                >
                  ✓
                </span>
              </div>

              <!-- 4. 220Ω Direnç -->
              <div
                @click="toggleItem('RESISTOR_220')"
                :class="[
                  'p-3 rounded-2xl border-2 border-slate-900 flex flex-col items-center justify-center text-center relative select-none cursor-pointer transition-all shadow-[0_3px_0_#1e293b]',
                  isSelected('RESISTOR_220') ? 'bg-amber-100' : 'bg-slate-50'
                ]"
              >
                <span class="text-3xl mb-1">⚡</span>
                <span class="text-xs font-black text-slate-900">220Ω Direnç</span>
                <span
                  v-if="isSelected('RESISTOR_220')"
                  class="absolute -top-1.5 -right-1.5 w-5 h-5 rounded-full bg-emerald-500 border border-slate-900 text-white font-black text-[10px] flex items-center justify-center shadow-xs"
                >
                  ✓
                </span>
              </div>

              <!-- 5. Işık Sensörü LDR -->
              <div
                @click="toggleItem('LDR_SENSOR')"
                :class="[
                  'p-3 rounded-2xl border-2 border-slate-900 flex flex-col items-center justify-center text-center relative select-none cursor-pointer transition-all shadow-[0_3px_0_#1e293b]',
                  isSelected('LDR_SENSOR') ? 'bg-orange-100' : 'bg-slate-50'
                ]"
              >
                <span class="text-3xl mb-1">☀️</span>
                <span class="text-xs font-black text-slate-900">Işık Sensörü LDR</span>
                <span
                  v-if="isSelected('LDR_SENSOR')"
                  class="absolute -top-1.5 -right-1.5 w-5 h-5 rounded-full bg-emerald-500 border border-slate-900 text-white font-black text-[10px] flex items-center justify-center shadow-xs"
                >
                  ✓
                </span>
              </div>

              <!-- 6. Buzzer -->
              <div
                @click="toggleItem('BUZZER')"
                :class="[
                  'p-3 rounded-2xl border-2 border-slate-900 flex flex-col items-center justify-center text-center relative select-none cursor-pointer transition-all shadow-[0_3px_0_#1e293b]',
                  isSelected('BUZZER') ? 'bg-slate-200' : 'bg-slate-50'
                ]"
              >
                <span class="text-3xl mb-1">🔊</span>
                <span class="text-xs font-black text-slate-900">Buzzer</span>
                <span
                  v-if="isSelected('BUZZER')"
                  class="absolute -top-1.5 -right-1.5 w-5 h-5 rounded-full bg-emerald-500 border border-slate-900 text-white font-black text-[10px] flex items-center justify-center shadow-xs"
                >
                  ✓
                </span>
              </div>

            </div>
          </div>

          <!-- SAĞ SÜTUN: AI ASİSTAN SEÇİMİ -->
          <div class="flex flex-col gap-3">
            <div class="text-center md:text-left">
              <h3 class="text-base font-black text-slate-900">
                AI Asistan Seçimi
              </h3>
            </div>

            <!-- Model Seçenekleri Listesi -->
            <div class="flex flex-col gap-2.5">
              
              <!-- 1. Local Model (Ollama) -->
              <div
                @click="selectedModel = 'ollama/qwen2.5-coder:1.5b'"
                :class="[
                  'p-3 rounded-2xl border-2 border-slate-900 flex items-center gap-3 relative select-none cursor-pointer transition-all shadow-[0_3px_0_#1e293b]',
                  selectedModel.includes('ollama') || selectedModel === 'local'
                    ? 'bg-sky-50 border-sky-600 ring-2 ring-sky-400'
                    : 'bg-white hover:bg-slate-50'
                ]"
              >
                <div class="w-9 h-9 rounded-xl bg-amber-100 border border-slate-900 flex items-center justify-center text-xl shrink-0">
                  🤖
                </div>
                <div class="min-w-0 flex-1">
                  <div class="text-xs font-black text-slate-900">Local Model</div>
                  <div class="text-[10px] font-bold text-slate-500 truncate">(Ollama - qwen2.5-coder)</div>
                </div>
                <!-- Aktif Rozeti -->
                <span
                  v-if="selectedModel.includes('ollama') || selectedModel === 'local'"
                  class="px-2 py-0.5 rounded-full bg-emerald-500 text-white text-[10px] font-black border border-slate-900 shadow-xs"
                >
                  Aktif
                </span>
              </div>

              <!-- 2. Google Gemini -->
              <div
                @click="selectedModel = 'gemini/gemini-2.0-flash'"
                :class="[
                  'p-3 rounded-2xl border-2 border-slate-900 flex items-center gap-3 relative select-none cursor-pointer transition-all shadow-[0_3px_0_#1e293b]',
                  selectedModel.includes('gemini')
                    ? 'bg-sky-50 border-sky-600 ring-2 ring-sky-400'
                    : 'bg-white hover:bg-slate-50'
                ]"
              >
                <div class="w-9 h-9 rounded-xl bg-gradient-to-tr from-sky-400 to-indigo-500 border border-slate-900 flex items-center justify-center text-white text-lg shrink-0">
                  ✨
                </div>
                <div class="min-w-0 flex-1">
                  <div class="text-xs font-black text-slate-900">Google Gemini</div>
                  <div class="text-[10px] font-bold text-slate-500 truncate">Hızlı & Zeki Bulut Modeli</div>
                </div>
                <span
                  v-if="selectedModel.includes('gemini')"
                  class="px-2 py-0.5 rounded-full bg-emerald-500 text-white text-[10px] font-black border border-slate-900 shadow-xs"
                >
                  Aktif
                </span>
              </div>

              <!-- 3. OpenAI -->
              <div
                @click="selectedModel = 'gpt-4o-mini'"
                :class="[
                  'p-3 rounded-2xl border-2 border-slate-900 flex items-center gap-3 relative select-none cursor-pointer transition-all shadow-[0_3px_0_#1e293b]',
                  selectedModel.includes('gpt')
                    ? 'bg-sky-50 border-sky-600 ring-2 ring-sky-400'
                    : 'bg-white hover:bg-slate-50'
                ]"
              >
                <div class="w-9 h-9 rounded-xl bg-slate-900 border border-slate-900 flex items-center justify-center text-white text-lg shrink-0">
                  🌀
                </div>
                <div class="min-w-0 flex-1">
                  <div class="text-xs font-black text-slate-900">OpenAI</div>
                  <div class="text-[10px] font-bold text-slate-500 truncate">GPT-4o Mini</div>
                </div>
                <span
                  v-if="selectedModel.includes('gpt')"
                  class="px-2 py-0.5 rounded-full bg-emerald-500 text-white text-[10px] font-black border border-slate-900 shadow-xs"
                >
                  Aktif
                </span>
              </div>

              <!-- 4. Claude -->
              <div
                @click="selectedModel = 'claude-3-5-haiku-20241022'"
                :class="[
                  'p-3 rounded-2xl border-2 border-slate-900 flex items-center gap-3 relative select-none cursor-pointer transition-all shadow-[0_3px_0_#1e293b]',
                  selectedModel.includes('claude')
                    ? 'bg-sky-50 border-sky-600 ring-2 ring-sky-400'
                    : 'bg-white hover:bg-slate-50'
                ]"
              >
                <div class="w-9 h-9 rounded-xl bg-amber-600 border border-slate-900 flex items-center justify-center text-white text-xs font-black shrink-0">
                  A\
                </div>
                <div class="min-w-0 flex-1">
                  <div class="text-xs font-black text-slate-900">Claude</div>
                  <div class="text-[10px] font-bold text-slate-500 truncate">Claude 3.5 Haiku</div>
                </div>
                <span
                  v-if="selectedModel.includes('claude')"
                  class="px-2 py-0.5 rounded-full bg-emerald-500 text-white text-[10px] font-black border border-slate-900 shadow-xs"
                >
                  Aktif
                </span>
              </div>

            </div>

            <!-- Bulut API Key Girişi (Gerektiğinde Açılır) -->
            <div v-if="isCloud" class="mt-1">
              <input
                type="password"
                v-model="apiKey"
                placeholder="API Anahtarı (isteğe bağlı)"
                class="w-full px-3 py-1.5 rounded-xl border-2 border-slate-900 text-xs font-mono bg-slate-50 outline-none"
              />
            </div>
          </div>

        </div>

        <!-- Alt Buton: 'Kaydet ve Başla!' (Referans Görseldeki Yıldızlı Camgöbeği 3D Buton) -->
        <div class="p-4 bg-slate-50 border-t-[3px] border-slate-900 flex items-center justify-center">
          <div class="relative">
            <!-- Yanlardaki Minik Çizgi Film Yıldızları -->
            <span class="absolute -left-5 -top-2 text-amber-400 text-lg select-none">⭐</span>
            <span class="absolute -right-4 -bottom-1 text-emerald-400 text-sm select-none">✨</span>

            <button
              type="button"
              @click="handleSave"
              class="px-10 py-3 rounded-full bg-gradient-to-r from-cyan-400 to-sky-500 hover:from-cyan-300 hover:to-sky-400 active:translate-y-1 active:shadow-none text-slate-950 font-black text-sm sm:text-base border-2 border-slate-900 shadow-[0_4px_0_#0369a1] transition-all cursor-pointer flex items-center gap-2"
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
import { ref, computed, watch } from 'vue';

const props = defineProps<{
  isOpen: boolean;
  currentModel: string;
  inventory: string[];
}>();

const emit = defineEmits<{
  (e: 'close'): void;
  (e: 'save', payload: { model: string; inventory: string[]; apiKey?: string }): void;
}>();

const selectedModel = ref(props.currentModel || 'ollama/qwen2.5-coder:1.5b');
const selectedInventory = ref<string[]>([...props.inventory]);
const apiKey = ref(localStorage.getItem('kid_arduino_api_key') || '');

watch(() => props.currentModel, (v) => { if (v) selectedModel.value = v; });
watch(() => props.inventory, (v) => { if (v) selectedInventory.value = [...v]; }, { deep: true });

const isCloud = computed(() => {
  return !selectedModel.value.startsWith('ollama') && selectedModel.value !== 'local';
});

function isSelected(id: string): boolean {
  return selectedInventory.value.includes(id);
}

function toggleItem(id: string) {
  if (selectedInventory.value.includes(id)) {
    selectedInventory.value = selectedInventory.value.filter(i => i !== id);
  } else {
    selectedInventory.value.push(id);
  }
}

function handleSave() {
  if (apiKey.value) {
    localStorage.setItem('kid_arduino_api_key', apiKey.value);
  }
  emit('save', {
    model: selectedModel.value,
    inventory: selectedInventory.value,
    apiKey: apiKey.value || undefined
  });
  emit('close');
}
</script>

<template>
  <div v-if="isOpen">
    <!-- Karartma Arka Planı -->
    <div
      class="fixed inset-0 z-50 bg-slate-900/60 backdrop-blur-xs flex items-center justify-center p-2 sm:p-4"
      @click.self="$emit('close')"
    >
      <!-- Modal Kutusu (Referans Görsel ile Birebir Aynı Tasarım) -->
      <div class="bg-white rounded-[32px] border-[3px] border-slate-900 shadow-[0_12px_0_rgba(15,23,42,0.3)] max-w-2xl w-full overflow-hidden flex flex-col animate-in fade-in zoom-in-95 duration-150">
        
        <!-- Üst Başlık Çubuğu: Nane Yeşili Banner + Çanta İkonu + Kırmızı Kare Çarpı Butonu -->
        <div class="px-5 py-3.5 bg-[#a7f3d0] border-b-[3px] border-slate-900 flex items-center justify-between">
          <div class="flex items-center gap-2.5">
            <!-- Çanta & Aletler İkonu -->
            <div class="w-8 h-8 rounded-lg bg-white/80 border-2 border-slate-900 flex items-center justify-center text-lg shadow-xs">
              🧰
            </div>
            <h2 class="text-base sm:text-xl font-black text-slate-900 tracking-tight">
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

        <!-- İki Sütunlu Ana Gövde (Sol: Malzeme Çantam, Sağ: AI Asistan Seçimi) -->
        <div class="p-5 sm:p-6 grid grid-cols-1 md:grid-cols-2 gap-5 sm:gap-6 bg-white overflow-y-auto max-h-[75vh]">
          
          <!-- ============================================== -->
          <!-- SOL SÜTUN: MALZEME ÇANTAM (6 PARÇA KARTI)      -->
          <!-- ============================================== -->
          <div class="flex flex-col gap-3">
            <h3 class="text-sm sm:text-base font-black text-slate-900 text-center md:text-left">
              Malzeme Çantam
            </h3>

            <div class="grid grid-cols-2 gap-2.5">
              
              <!-- 1. Arduino Uno -->
              <div
                @click="toggleItem('ARDUINO_UNO')"
                :class="[
                  'p-2.5 rounded-2xl border-2 border-slate-900 flex flex-col items-center justify-center text-center relative select-none cursor-pointer transition-all shadow-[0_3px_0_#1e293b]',
                  isSelected('ARDUINO_UNO') ? 'bg-[#bbf7d0]' : 'bg-slate-50'
                ]"
              >
                <!-- Arduino Uno İllüstrasyonu -->
                <div class="w-16 h-12 relative flex items-center justify-center mb-1">
                  <svg class="w-14 h-11" viewBox="0 0 100 80">
                    <rect x="5" y="10" width="85" height="60" rx="4" fill="#0284c7" stroke="#0f172a" stroke-width="2.5" />
                    <rect x="0" y="15" width="12" height="15" rx="2" fill="#94a3b8" stroke="#0f172a" stroke-width="2" />
                    <rect x="0" y="48" width="14" height="18" rx="2" fill="#1e293b" stroke="#0f172a" stroke-width="2" />
                    <rect x="35" y="30" width="35" height="12" rx="2" fill="#1e293b" />
                    <!-- Headerlar -->
                    <rect x="25" y="12" width="60" height="6" fill="#0f172a" />
                    <rect x="28" y="62" width="55" height="6" fill="#0f172a" />
                    <circle cx="20" cy="18" r="3" fill="#ef4444" />
                    <circle cx="50" cy="50" r="4" fill="none" stroke="#ffffff" stroke-width="1.5" />
                  </svg>
                </div>
                <span class="text-xs font-black text-slate-900">Arduino Uno</span>
                
                <!-- Yeşil Onay Rozeti -->
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
                  'p-2.5 rounded-2xl border-2 border-slate-900 flex flex-col items-center justify-center text-center relative select-none cursor-pointer transition-all shadow-[0_3px_0_#1e293b]',
                  isSelected('BREADBOARD') ? 'bg-amber-50' : 'bg-slate-50'
                ]"
              >
                <!-- Breadboard İllüstrasyonu -->
                <div class="w-16 h-12 relative flex items-center justify-center mb-1">
                  <svg class="w-14 h-11" viewBox="0 0 100 80">
                    <rect x="5" y="10" width="90" height="60" rx="4" fill="#f8fafc" stroke="#0f172a" stroke-width="2.5" />
                    <!-- Kırmızı ve Mavi Güç Hatları -->
                    <line x1="12" y1="16" x2="88" y2="16" stroke="#ef4444" stroke-width="2" />
                    <line x1="12" y1="21" x2="88" y2="21" stroke="#3b82f6" stroke-width="2" />
                    <line x1="12" y1="59" x2="88" y2="59" stroke="#3b82f6" stroke-width="2" />
                    <line x1="12" y1="64" x2="88" y2="64" stroke="#ef4444" stroke-width="2" />
                    <!-- Orta Oluk -->
                    <rect x="10" y="38" width="80" height="4" rx="1" fill="#cbd5e1" />
                    <!-- Delikler -->
                    <circle cx="25" cy="30" r="1.5" fill="#0f172a" />
                    <circle cx="40" cy="30" r="1.5" fill="#0f172a" />
                    <circle cx="55" cy="30" r="1.5" fill="#0f172a" />
                    <circle cx="70" cy="30" r="1.5" fill="#0f172a" />
                    <circle cx="25" cy="50" r="1.5" fill="#0f172a" />
                    <circle cx="40" cy="50" r="1.5" fill="#0f172a" />
                    <circle cx="55" cy="50" r="1.5" fill="#0f172a" />
                    <circle cx="70" cy="50" r="1.5" fill="#0f172a" />
                  </svg>
                </div>
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
                  'p-2.5 rounded-2xl border-2 border-slate-900 flex flex-col items-center justify-center text-center relative select-none cursor-pointer transition-all shadow-[0_3px_0_#1e293b]',
                  isSelected('LED_RED') ? 'bg-[#ffe4e6]' : 'bg-slate-50'
                ]"
              >
                <!-- Kırmızı LED İllüstrasyonu -->
                <div class="w-16 h-12 relative flex items-center justify-center mb-1">
                  <svg class="w-10 h-11" viewBox="0 0 80 90">
                    <path d="M 25 50 C 25 15, 55 15, 55 50 Z" fill="#ef4444" stroke="#0f172a" stroke-width="2.5" />
                    <ellipse cx="40" cy="50" rx="15" ry="4" fill="#b91c1c" stroke="#0f172a" stroke-width="2" />
                    <!-- Bacaklar -->
                    <line x1="33" y1="54" x2="33" y2="80" stroke="#64748b" stroke-width="3" stroke-linecap="round" />
                    <line x1="47" y1="54" x2="47" y2="74" stroke="#64748b" stroke-width="3" stroke-linecap="round" />
                  </svg>
                </div>
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
                  'p-2.5 rounded-2xl border-2 border-slate-900 flex flex-col items-center justify-center text-center relative select-none cursor-pointer transition-all shadow-[0_3px_0_#1e293b]',
                  isSelected('RESISTOR_220') ? 'bg-[#fef3c7]' : 'bg-slate-50'
                ]"
              >
                <!-- Direnç İllüstrasyonu -->
                <div class="w-16 h-12 relative flex items-center justify-center mb-1">
                  <svg class="w-14 h-11" viewBox="0 0 100 60">
                    <line x1="10" y1="30" x2="30" y2="30" stroke="#64748b" stroke-width="3" stroke-linecap="round" />
                    <line x1="70" y1="30" x2="90" y2="30" stroke="#64748b" stroke-width="3" stroke-linecap="round" />
                    <rect x="30" y="20" width="40" height="20" rx="6" fill="#d97706" stroke="#0f172a" stroke-width="2.5" />
                    <!-- Renk Bantları -->
                    <rect x="38" y="20" width="4" height="20" fill="#ef4444" />
                    <rect x="46" y="20" width="4" height="20" fill="#ef4444" />
                    <rect x="54" y="20" width="4" height="20" fill="#78350f" />
                    <rect x="62" y="20" width="3" height="20" fill="#facc15" />
                  </svg>
                </div>
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
                  'p-2.5 rounded-2xl border-2 border-slate-900 flex flex-col items-center justify-center text-center relative select-none cursor-pointer transition-all shadow-[0_3px_0_#1e293b]',
                  isSelected('LDR_SENSOR') ? 'bg-[#fed7aa]' : 'bg-slate-50'
                ]"
              >
                <!-- LDR İllüstrasyonu -->
                <div class="w-16 h-12 relative flex items-center justify-center mb-1">
                  <svg class="w-11 h-11" viewBox="0 0 80 80">
                    <circle cx="40" cy="35" r="22" fill="#fed7aa" stroke="#0f172a" stroke-width="2.5" />
                    <path d="M 28 30 Q 40 22, 52 30 Q 40 38, 28 38 Q 40 46, 52 46" fill="none" stroke="#9a3412" stroke-width="2.5" stroke-linecap="round" />
                    <!-- Bacaklar -->
                    <line x1="33" y1="57" x2="33" y2="75" stroke="#64748b" stroke-width="3" stroke-linecap="round" />
                    <line x1="47" y1="57" x2="47" y2="75" stroke="#64748b" stroke-width="3" stroke-linecap="round" />
                  </svg>
                </div>
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
                  'p-2.5 rounded-2xl border-2 border-slate-900 flex flex-col items-center justify-center text-center relative select-none cursor-pointer transition-all shadow-[0_3px_0_#1e293b]',
                  isSelected('BUZZER') ? 'bg-[#e2e8f0]' : 'bg-slate-50'
                ]"
              >
                <!-- Buzzer İllüstrasyonu -->
                <div class="w-16 h-12 relative flex items-center justify-center mb-1">
                  <svg class="w-11 h-11" viewBox="0 0 80 80">
                    <circle cx="40" cy="35" r="22" fill="#1e293b" stroke="#0f172a" stroke-width="2.5" />
                    <circle cx="40" cy="35" r="6" fill="#0f172a" />
                    <text x="26" y="32" fill="#cbd5e1" font-size="9" font-weight="900">+</text>
                    <!-- Bacaklar -->
                    <line x1="33" y1="57" x2="33" y2="75" stroke="#64748b" stroke-width="3" stroke-linecap="round" />
                    <line x1="47" y1="57" x2="47" y2="75" stroke="#64748b" stroke-width="3" stroke-linecap="round" />
                  </svg>
                </div>
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

          <!-- ============================================== -->
          <!-- SAĞ SÜTUN: AI ASİSTAN SEÇİMİ (4 MODEL KARTI)   -->
          <!-- ============================================== -->
          <div class="flex flex-col gap-3">
            <h3 class="text-sm sm:text-base font-black text-slate-900 text-center md:text-left">
              AI Asistan Seçimi
            </h3>

            <div class="flex flex-col gap-2.5">
              
              <!-- 1. Local Model (Ollama) - Referans Görseldeki Mavi Çerçeveli Seçim -->
              <div
                @click="selectedModel = 'ollama/qwen2.5-coder:1.5b'"
                :class="[
                  'p-3 rounded-2xl border-[2.5px] flex items-center gap-3 relative select-none cursor-pointer transition-all shadow-[0_3px_0_#0f172a]',
                  selectedModel.includes('ollama') || selectedModel === 'local'
                    ? 'border-[#0284c7] bg-[#f0f9ff] ring-2 ring-[#38bdf8]'
                    : 'border-slate-900 bg-white hover:bg-slate-50'
                ]"
              >
                <!-- Sarı Arka Planlı Sevimli Robot Başlığı -->
                <div class="w-10 h-10 rounded-xl bg-[#fef08a] border-2 border-slate-900 flex items-center justify-center text-2xl shrink-0 shadow-xs">
                  🤖
                </div>
                <div class="min-w-0 flex-1">
                  <div class="text-xs sm:text-sm font-black text-slate-900">Local Model</div>
                  <div class="text-[10px] font-bold text-slate-500 truncate">(Ollama - qwen2.5-coder:7b)</div>
                </div>
                <!-- Yeşil 'Aktif' Rozeti -->
                <span
                  v-if="selectedModel.includes('ollama') || selectedModel === 'local'"
                  class="px-2.5 py-0.5 rounded-full bg-[#4ade80] text-slate-950 text-[10px] font-black border-2 border-slate-900 shadow-xs"
                >
                  Aktif
                </span>
              </div>

              <!-- 2. Google Gemini -->
              <div
                @click="selectedModel = 'gemini/gemini-2.0-flash'"
                :class="[
                  'p-3 rounded-2xl border-[2.5px] flex items-center gap-3 relative select-none cursor-pointer transition-all shadow-[0_3px_0_#0f172a]',
                  selectedModel.includes('gemini')
                    ? 'border-[#0284c7] bg-[#f0f9ff] ring-2 ring-[#38bdf8]'
                    : 'border-slate-900 bg-white hover:bg-slate-50'
                ]"
              >
                <!-- Çok Renkli Gemini Yıldız İkonu -->
                <div class="w-10 h-10 rounded-xl bg-white border-2 border-slate-900 flex items-center justify-center text-xl shrink-0 shadow-xs">
                  <svg class="w-6 h-6" viewBox="0 0 24 24">
                    <path d="M12 2L14.5 9.5L22 12L14.5 14.5L12 22L9.5 14.5L2 12L9.5 9.5L12 2Z" fill="url(#geminiGrad)" />
                    <defs>
                      <linearGradient id="geminiGrad" x1="0%" y1="0%" x2="100%" y2="100%">
                        <stop offset="0%" stop-color="#38bdf8" />
                        <stop offset="50%" stop-color="#818cf8" />
                        <stop offset="100%" stop-color="#f43f5e" />
                      </linearGradient>
                    </defs>
                  </svg>
                </div>
                <div class="min-w-0 flex-1">
                  <div class="text-xs sm:text-sm font-black text-slate-900">Google Gemini</div>
                </div>
                <span
                  v-if="selectedModel.includes('gemini')"
                  class="px-2.5 py-0.5 rounded-full bg-[#4ade80] text-slate-950 text-[10px] font-black border-2 border-slate-900 shadow-xs"
                >
                  Aktif
                </span>
              </div>

              <!-- 3. OpenAI -->
              <div
                @click="selectedModel = 'gpt-4o-mini'"
                :class="[
                  'p-3 rounded-2xl border-[2.5px] flex items-center gap-3 relative select-none cursor-pointer transition-all shadow-[0_3px_0_#0f172a]',
                  selectedModel.includes('gpt')
                    ? 'border-[#0284c7] bg-[#f0f9ff] ring-2 ring-[#38bdf8]'
                    : 'border-slate-900 bg-white hover:bg-slate-50'
                ]"
              >
                <!-- OpenAI Girdap Logosu -->
                <div class="w-10 h-10 rounded-xl bg-slate-900 border-2 border-slate-900 flex items-center justify-center text-white text-xl shrink-0 shadow-xs">
                  <svg class="w-6 h-6 fill-current" viewBox="0 0 24 24">
                    <path d="M22.2819 9.8211a5.9847 5.9847 0 0 0-.5157-4.9108 6.0462 6.0462 0 0 0-6.5098-2.9A6.0651 6.0651 0 0 0 4.9807 4.1818a5.9847 5.9847 0 0 0-3.9977 2.9 6.0462 6.0462 0 0 0 .7427 7.0966 5.98 5.98 0 0 0 .511 4.9107 6.051 6.051 0 0 0 6.5146 2.9001A5.9847 5.9847 0 0 0 13.2599 24a6.0557 6.0557 0 0 0 5.7718-4.2058 5.9894 5.9894 0 0 0 3.9977-2.9001 6.0557 6.0557 0 0 0-.7475-7.0729zm-9.022 12.6081a4.4755 4.4755 0 0 1-2.8764-1.0408l.1419-.0804 4.7783-2.7582a.7948.7948 0 0 0 .3927-.6813v-6.7369l2.02 1.1683a.071.071 0 0 1 .038.052v5.5826a4.5045 4.5045 0 0 1-4.4945 4.4947z"/>
                  </svg>
                </div>
                <div class="min-w-0 flex-1">
                  <div class="text-xs sm:text-sm font-black text-slate-900">OpenAI</div>
                </div>
                <span
                  v-if="selectedModel.includes('gpt')"
                  class="px-2.5 py-0.5 rounded-full bg-[#4ade80] text-slate-950 text-[10px] font-black border-2 border-slate-900 shadow-xs"
                >
                  Aktif
                </span>
              </div>

              <!-- 4. Claude -->
              <div
                @click="selectedModel = 'claude-3-5-haiku-20241022'"
                :class="[
                  'p-3 rounded-2xl border-[2.5px] flex items-center gap-3 relative select-none cursor-pointer transition-all shadow-[0_3px_0_#0f172a]',
                  selectedModel.includes('claude')
                    ? 'border-[#0284c7] bg-[#f0f9ff] ring-2 ring-[#38bdf8]'
                    : 'border-slate-900 bg-white hover:bg-slate-50'
                ]"
              >
                <!-- Turuncu Claude A\ Logosu -->
                <div class="w-10 h-10 rounded-xl bg-[#d97706] border-2 border-slate-900 flex items-center justify-center text-white text-base font-black shrink-0 shadow-xs">
                  A\
                </div>
                <div class="min-w-0 flex-1">
                  <div class="text-xs sm:text-sm font-black text-slate-900">Claude</div>
                </div>
                <span
                  v-if="selectedModel.includes('claude')"
                  class="px-2.5 py-0.5 rounded-full bg-[#4ade80] text-slate-950 text-[10px] font-black border-2 border-slate-900 shadow-xs"
                >
                  Aktif
                </span>
              </div>

            </div>

            <!-- API Key Girişi (Bulut Seçiliyse) -->
            <div v-if="isCloud" class="mt-1">
              <input
                type="password"
                v-model="apiKey"
                placeholder="API Anahtarı (isteğe bağlı)"
                class="w-full px-3 py-2 rounded-xl border-2 border-slate-900 text-xs font-mono bg-slate-50 outline-none"
              />
            </div>

          </div>

        </div>

        <!-- ============================================== -->
        <!-- ALT BUTON: KAYDET VE BAŞLA! (YILDIZLI 3D BUTON)-->
        <!-- ============================================== -->
        <div class="p-4 sm:p-5 bg-slate-50 border-t-[3px] border-slate-900 flex items-center justify-center">
          <div class="relative">
            <!-- Çizgi Film Yıldızları -->
            <span class="absolute -left-6 -top-2 text-amber-400 text-2xl select-none animate-pulse">⭐</span>
            <span class="absolute -right-5 -bottom-1 text-emerald-500 text-lg select-none">✨</span>
            <span class="absolute right-0 -top-3 text-sky-400 text-xs select-none">✦</span>

            <!-- Parlak Camgöbeği 3D Buton -->
            <button
              type="button"
              @click="handleSave"
              class="px-12 py-3.5 rounded-full bg-gradient-to-r from-[#38bdf8] to-[#0284c7] hover:from-[#7dd3fc] hover:to-[#0369a1] active:translate-y-1 active:shadow-none text-slate-950 font-black text-sm sm:text-base border-[2.5px] border-slate-900 shadow-[0_5px_0_#0f172a] transition-all cursor-pointer flex items-center gap-2"
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

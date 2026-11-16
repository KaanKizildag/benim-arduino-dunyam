<template>
  <header class="bg-[#7dd3fc] px-3 sm:px-6 py-2.5 sm:py-3 border-b-[3px] border-slate-900 select-none shrink-0 shadow-xs">
    <div class="w-full flex flex-wrap items-center justify-between gap-3">
      
      <!-- Sol: 'Benim Arduino Dünyam' Çizgi Film Logosu & Profil Avatarı (Referans Görsel) -->
      <div class="flex items-center gap-2.5">
        <div
          class="flex items-center gap-2 cursor-pointer group"
          @click="$emit('go-step', 1)"
          title="İlk Adıma Git"
        >
          <!-- Teal Renkli Arduino Sonsuzluk İkonu -->
          <div class="w-10 h-10 rounded-2xl bg-[#0d9488] border-2 border-slate-900 shadow-[0_3px_0_#0f172a] flex items-center justify-center text-white text-base font-black group-hover:rotate-6 transition-transform">
            <svg class="w-6 h-6 fill-current" viewBox="0 0 24 24">
              <path d="M12 2C6.48 2 2 6.48 2 12s4.48 10 10 10 10-4.48 10-10S17.52 2 12 2zm-1 14H9v-2h2v2zm0-4H9V8h2v4zm4 4h-2v-2h2v2zm0-4h-2V8h2v4z"/>
            </svg>
          </div>

          <!-- 3D Renkli Çizgi Film Yazısı -->
          <div class="flex flex-col">
            <div class="flex items-center gap-0.5 font-black text-lg sm:text-xl tracking-tight leading-none drop-shadow-[0_2px_0_rgba(255,255,255,0.8)]">
              <span class="text-amber-500">B</span>
              <span class="text-sky-600">e</span>
              <span class="text-emerald-500">n</span>
              <span class="text-purple-600">i</span>
              <span class="text-rose-500">m</span>
              <span class="text-slate-800 ml-1.5">Arduino</span>
              <span class="text-teal-700 ml-1.5">Dünyam</span>
            </div>
            <span class="text-[9px] font-black text-teal-900/80 tracking-widest uppercase mt-0.5">
              Çocuk AI Stüdyosu 🚀
            </span>
          </div>
        </div>

        <!-- Referans Görseldeki Yuvarlak Çocuk Avatarı -->
        <div class="w-8 h-8 rounded-full bg-slate-200 border-2 border-slate-900 shadow-xs flex items-center justify-center text-sm font-black text-slate-700">
          👦
        </div>
      </div>

      <!-- Orta: 4 Ayrı Ekran Sekmeleri (Referans Görsel 2'deki Sarı 3D Buton Stili) -->
      <nav class="flex items-center gap-1.5 sm:gap-2 overflow-x-auto py-0.5">
        <button
          v-for="step in steps"
          :key="step.num"
          type="button"
          @click="$emit('go-step', step.num)"
          :class="[
            'px-3 sm:px-4 py-1.5 sm:py-2 rounded-2xl text-xs sm:text-sm font-black transition-all cursor-pointer whitespace-nowrap border-2 border-slate-900',
            currentStep === step.num
              ? 'bg-[#fbbf24] text-slate-900 shadow-[0_4px_0_#ca8a04] scale-103'
              : 'bg-white/70 text-slate-800 hover:bg-white shadow-[0_2px_0_#0f172a]'
          ]"
        >
          {{ step.num }}. {{ step.title }}
        </button>
      </nav>

      <!-- Sağ: Malzeme Çantam, AI Modeli, Ayarlar ve Çarpı Butonu (Referans Görsel 1 Sağ Üst) -->
      <div class="flex items-center gap-2">
        <!-- 1. Malzeme Çantam Butonu (Sol griddeki zengin elektronik menüsünü açar) -->
        <button
          type="button"
          @click="$emit('open-inventory')"
          class="px-3 py-1.5 sm:py-2 rounded-2xl bg-[#e2d5c3] hover:bg-[#d6c5b0] border-2 border-slate-900 shadow-[0_3px_0_#0f172a] active:translate-y-0.5 active:shadow-none text-slate-900 text-xs font-black transition flex items-center gap-1.5 cursor-pointer"
          title="Elektronik Malzeme Çantamı Aç"
        >
          <span class="text-sm">🧰</span>
          <span class="hidden sm:inline">Malzeme Çantam</span>
          <span class="px-1.5 py-0.2 rounded-full bg-emerald-500 text-white text-[10px] font-black border border-slate-900">
            {{ inventoryCount }}
          </span>
        </button>

        <!-- 2. AI Modeli Butonu (Sağ griddeki yapay zeka seçim ekranını açar) -->
        <button
          type="button"
          @click="$emit('open-ai-model')"
          class="px-3 py-1.5 sm:py-2 rounded-2xl bg-[#bae6fd] hover:bg-[#7dd3fc] border-2 border-slate-900 shadow-[0_3px_0_#0f172a] active:translate-y-0.5 active:shadow-none text-slate-900 text-xs font-black transition flex items-center gap-1.5 cursor-pointer"
          title="Yapay Zeka Asistanı Seçimi"
        >
          <span class="text-sm">🤖</span>
          <span class="hidden md:inline">AI Modeli</span>
        </button>

        <!-- 3. Ayarlar Butonu -->
        <button
          type="button"
          @click="$emit('open-settings')"
          class="px-2.5 py-1.5 sm:py-2 rounded-2xl bg-[#bae6fd] hover:bg-[#7dd3fc] border-2 border-slate-900 shadow-[0_3px_0_#0f172a] active:translate-y-0.5 active:shadow-none text-slate-900 text-xs font-black transition flex items-center gap-1 cursor-pointer"
          title="Genel Ayarlar"
        >
          <span class="text-sm">⚙️</span>
          <span class="hidden lg:inline">Ayarlar</span>
        </button>

        <!-- 4. Kırmızı Kare Çarpı Butonu -->
        <button
          type="button"
          @click="$emit('reset-or-close')"
          class="w-8 h-8 rounded-xl bg-[#f43f5e] hover:bg-[#e11d48] border-2 border-slate-900 shadow-[0_3px_0_#9f1239] active:translate-y-0.5 active:shadow-none text-white font-black text-xs sm:text-sm flex items-center justify-center cursor-pointer transition"
          title="Projeyi Sıfırla / Başa Dön"
        >
          ✕
        </button>
      </div>

    </div>
  </header>
</template>

<script setup lang="ts">
defineProps<{
  currentStep: number;
  inventoryCount: number;
  activeModelName?: string;
}>();

defineEmits<{
  (e: 'go-step', stepNum: number): void;
  (e: 'open-inventory'): void;
  (e: 'open-ai-model'): void;
  (e: 'open-settings'): void;
  (e: 'reset-or-close'): void;
}>();

const steps = [
  { num: 1, title: 'Hayal Et' },
  { num: 2, title: 'Devreyi Kur' },
  { num: 3, title: 'Nasıl Çalışacak?' },
  { num: 4, title: 'Çalıştır' },
];
</script>
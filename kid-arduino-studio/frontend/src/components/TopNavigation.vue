<template>
  <header class="bg-[#7dd3fc] px-3 sm:px-4 py-2 sm:py-2.5 border-b-[2.5px] border-slate-900 select-none shrink-0 shadow-xs">
    <div class="w-full flex flex-wrap items-center justify-between gap-2">
      
      <!-- Sol: 'Benim Arduino Dünyam' Çizgi Film Logosu & Profil Avatarı (Referans Görseldeki Gibi) -->
      <div class="flex items-center gap-2">
        <div
          class="flex items-center gap-2 cursor-pointer group"
          @click="$emit('go-step', 0)"
          title="Ana Stüdyo Görünümüne Dön"
        >
          <!-- Teal Renkli Arduino Sonsuzluk İkonu -->
          <div class="w-9 h-9 sm:w-10 sm:h-10 rounded-2xl bg-[#0d9488] border-2 border-slate-900 shadow-[0_3px_0_#0f172a] flex items-center justify-center text-white text-base font-black group-hover:rotate-6 transition-transform">
            <svg class="w-5 h-5 fill-current" viewBox="0 0 24 24">
              <path d="M12 2C6.48 2 2 6.48 2 12s4.48 10 10 10 10-4.48 10-10S17.52 2 12 2zm-1 14H9v-2h2v2zm0-4H9V8h2v4zm4 4h-2v-2h2v2zm0-4h-2V8h2v4z"/>
            </svg>
          </div>

          <!-- 3D Renkli Çizgi Film Yazısı -->
          <div class="flex flex-col">
            <div class="flex items-center gap-0.5 font-black text-base sm:text-lg tracking-tight leading-none drop-shadow-[0_2px_0_rgba(255,255,255,0.8)]">
              <span class="text-amber-500">B</span>
              <span class="text-sky-600">e</span>
              <span class="text-emerald-500">n</span>
              <span class="text-purple-600">i</span>
              <span class="text-rose-500">m</span>
              <span class="text-slate-800 ml-1.5">Arduino</span>
              <span class="text-teal-700 ml-1.5">Dünyam</span>
            </div>
            <span class="text-[8px] sm:text-[9px] font-black text-teal-900/80 tracking-widest uppercase mt-0.5">
              Çocuk AI Stüdyosu 🚀
            </span>
          </div>
        </div>

        <!-- Referans Görseldeki Yuvarlak Çocuk Avatarı -->
        <div class="w-8 h-8 rounded-full bg-slate-200 border-2 border-slate-900 shadow-xs flex items-center justify-center text-sm font-black text-slate-700">
          👦
        </div>
      </div>

      <!-- Orta: 4 Adım + 4'lü Stüdyo Sekmeleri -->
      <nav class="flex items-center gap-1 sm:gap-1.5 overflow-x-auto py-0.5">
        <!-- 4'lü Stüdyo Butonu (Referans Görsel 1'deki Tam Ekran Panel Modu) -->
        <button
          type="button"
          @click="$emit('go-step', 0)"
          :class="[
            'px-3 py-1.5 rounded-xl text-xs font-black transition-all cursor-pointer whitespace-nowrap border-2 border-slate-900',
            currentStep === 0
              ? 'bg-[#fbbf24] text-slate-900 shadow-[0_3px_0_#ca8a04] scale-103'
              : 'bg-white/80 text-slate-800 hover:bg-white shadow-[0_2px_0_#0f172a]'
          ]"
        >
          🌟 4'lü Stüdyo
        </button>

        <button
          v-for="step in steps"
          :key="step.num"
          type="button"
          @click="$emit('go-step', step.num)"
          :class="[
            'px-2.5 sm:px-3 py-1.5 rounded-xl text-xs font-black transition-all cursor-pointer whitespace-nowrap border-2 border-slate-900',
            currentStep === step.num
              ? 'bg-[#fbbf24] text-slate-900 shadow-[0_3px_0_#ca8a04] scale-103'
              : 'bg-white/60 text-slate-800 hover:bg-white/90 shadow-[0_2px_0_#0f172a]'
          ]"
        >
          {{ step.num }}. {{ step.title }}
        </button>
      </nav>

      <!-- Sağ: Malzeme Çantam, AI Modeli, Ayarlar ve Çarpı Kapat Butonu (Referans Görsel 1 Sağ Üst) -->
      <div class="flex items-center gap-1.5 sm:gap-2">
        <!-- 1. Malzeme Çantam (Açık Kahverengi/Bej Buton) -->
        <button
          type="button"
          @click="$emit('open-modal', 'inventory')"
          class="px-2.5 sm:px-3 py-1.5 rounded-xl bg-[#e2d5c3] hover:bg-[#d6c5b0] border-2 border-slate-900 shadow-[0_3px_0_#0f172a] active:translate-y-0.5 active:shadow-none text-slate-900 text-xs font-black transition flex items-center gap-1.5 cursor-pointer"
        >
          <span class="text-sm">🧰</span>
          <span class="hidden sm:inline">Malzeme Çantam</span>
          <span class="w-4 h-4 rounded-full bg-emerald-500 text-white text-[9px] font-black flex items-center justify-center border border-slate-900">
            {{ inventoryCount }}
          </span>
        </button>

        <!-- 2. AI Modeli (Mavi/Camgöbeği Buton) -->
        <button
          type="button"
          @click="$emit('open-modal', 'ai')"
          class="px-2.5 sm:px-3 py-1.5 rounded-xl bg-[#bae6fd] hover:bg-[#7dd3fc] border-2 border-slate-900 shadow-[0_3px_0_#0f172a] active:translate-y-0.5 active:shadow-none text-slate-900 text-xs font-black transition flex items-center gap-1.5 cursor-pointer"
          title="Yapay Zeka Asistanı Seçimi"
        >
          <span class="text-sm">🤖</span>
          <span class="hidden md:inline">AI Modeli</span>
        </button>

        <!-- 3. Ayarlar (Camgöbeği Buton) -->
        <button
          type="button"
          @click="$emit('open-modal', 'settings')"
          class="px-2 sm:px-2.5 py-1.5 rounded-xl bg-[#bae6fd] hover:bg-[#7dd3fc] border-2 border-slate-900 shadow-[0_3px_0_#0f172a] active:translate-y-0.5 active:shadow-none text-slate-900 text-xs font-black transition flex items-center gap-1 cursor-pointer"
          title="Genel Ayarlar"
        >
          <span class="text-sm">⚙️</span>
          <span class="hidden lg:inline">Ayarlar</span>
        </button>

        <!-- 4. Kırmızı Kare Çarpı Butonu (Referans Görsel 1 En Sağ) -->
        <button
          type="button"
          @click="$emit('reset-or-close')"
          class="w-7 h-7 sm:w-8 sm:h-8 rounded-xl bg-[#f43f5e] hover:bg-[#e11d48] border-2 border-slate-900 shadow-[0_3px_0_#9f1239] active:translate-y-0.5 active:shadow-none text-white font-black text-xs sm:text-sm flex items-center justify-center cursor-pointer transition"
          title="Projeyi Sıfırla / Çıkış"
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
  (e: 'open-modal', tab?: string): void;
  (e: 'reset-or-close'): void;
}>();

const steps = [
  { num: 1, title: 'Hayal Et' },
  { num: 2, title: 'Devreyi Kur' },
  { num: 3, title: 'Nasıl Çalışacak?' },
  { num: 4, title: 'Çalıştır' },
];
</script>
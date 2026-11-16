<template>
  <header class="bg-[#7dd3fc] px-4 py-3 border-b-2 border-slate-800/20 select-none">
    <div class="max-w-7xl mx-auto flex flex-wrap items-center justify-between gap-3">
      
      <!-- Sol: 'Benim Arduino Dünyam' Çizgi Film Logosu -->
      <div
        class="flex items-center gap-2 cursor-pointer group"
        @click="$emit('go-step', 1)"
      >
        <!-- Arduino İkonu -->
        <div class="w-10 h-10 rounded-2xl bg-teal-500 border-2 border-slate-900 shadow-[0_3px_0_#0f172a] flex items-center justify-center text-white text-lg font-black group-hover:rotate-6 transition-transform">
          <svg class="w-6 h-6 fill-current" viewBox="0 0 24 24">
            <path d="M12 2C6.48 2 2 6.48 2 12s4.48 10 10 10 10-4.48 10-10S17.52 2 12 2zm-1 14H9v-2h2v2zm0-4H9V8h2v4zm4 4h-2v-2h2v2zm0-4h-2V8h2v4z"/>
          </svg>
        </div>

        <!-- 3D Renkli Çizgi Film Yazısı -->
        <div class="flex flex-col">
          <div class="flex items-center gap-0.5 font-black text-lg sm:text-xl tracking-tight leading-none drop-shadow-[0_2px_0_rgba(255,255,255,0.8)]">
            <span class="text-amber-500 stroke-black text-stroke">B</span>
            <span class="text-sky-600">e</span>
            <span class="text-emerald-500">n</span>
            <span class="text-purple-600">i</span>
            <span class="text-rose-500">m</span>
            <span class="text-slate-800 ml-1.5">Arduino</span>
            <span class="text-emerald-600 ml-1.5">Dünyam</span>
          </div>
          <span class="text-[9px] font-black text-teal-900/70 tracking-widest uppercase mt-0.5">
            Akıllı Çocuk Stüdyosu 🚀
          </span>
        </div>
      </div>

      <!-- Orta: 4 Adım Sekmeleri (Referans Görseldeki Sarı 3D Buton Stili) -->
      <nav class="flex items-center gap-1 sm:gap-2 overflow-x-auto py-1">
        <button
          v-for="step in steps"
          :key="step.num"
          type="button"
          @click="$emit('go-step', step.num)"
          :class="[
            'px-3.5 sm:px-4 py-1.5 sm:py-2 rounded-2xl text-xs sm:text-sm font-black transition-all cursor-pointer whitespace-nowrap',
            currentStep === step.num
              ? 'bg-[#fbbf24] text-slate-900 border-2 border-slate-900 shadow-[0_4px_0_#ca8a04] scale-103'
              : 'text-slate-700 hover:text-slate-900 hover:bg-white/60 font-extrabold'
          ]"
        >
          {{ step.num }}. {{ step.title }}
        </button>
      </nav>

      <!-- Sağ: Çanta ve Ayarlar Butonları -->
      <div class="flex items-center gap-2">
        <!-- Malzeme Çantam -->
        <button
          type="button"
          @click="$emit('open-modal', 'inventory')"
          class="px-3.5 py-1.5 sm:py-2 rounded-2xl bg-white/90 hover:bg-white border-2 border-slate-900 shadow-[0_3px_0_#1e293b] active:translate-y-1 active:shadow-none text-slate-800 text-xs font-black transition-all flex items-center gap-1.5 cursor-pointer"
        >
          <span class="text-base">🎒</span>
          <span class="hidden sm:inline">Malzeme Çantam</span>
          <span class="w-5 h-5 rounded-full bg-emerald-500 text-white text-[11px] font-black flex items-center justify-center border border-slate-900">
            {{ inventoryCount }}
          </span>
        </button>

        <!-- Ayarlar -->
        <button
          type="button"
          @click="$emit('open-modal', 'settings')"
          class="px-3 py-1.5 sm:py-2 rounded-2xl bg-white/90 hover:bg-white border-2 border-slate-900 shadow-[0_3px_0_#1e293b] active:translate-y-1 active:shadow-none text-slate-800 text-xs font-black transition-all flex items-center gap-1.5 cursor-pointer"
          title="Yapay Zeka ve Model Ayarları"
        >
          <span class="text-base">⚙️</span>
          <span class="hidden md:inline">Ayarlar</span>
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
}>();

const steps = [
  { num: 1, title: 'Hayal Et' },
  { num: 2, title: 'Devreyi Kur' },
  { num: 3, title: 'Nasıl Çalışacak?' },
  { num: 4, title: 'Çalıştır' },
];
</script>

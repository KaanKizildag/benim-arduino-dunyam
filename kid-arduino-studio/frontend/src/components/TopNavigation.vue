<template>
  <header class="bg-white/95 backdrop-blur-md border-b-2 border-slate-200 sticky top-0 z-40 px-3 sm:px-6 py-2.5 shadow-xs">
    <div class="max-w-7xl mx-auto flex flex-wrap items-center justify-between gap-3">
      
      <!-- Sol: Sevimli Canlı Logo -->
      <div class="flex items-center gap-2.5 select-none cursor-pointer" @click="$emit('go-step', 1)">
        <div class="w-10 h-10 rounded-2xl bg-gradient-to-tr from-indigo-600 via-sky-500 to-emerald-400 flex items-center justify-center text-xl text-white shadow-md shadow-indigo-100 hover:rotate-6 transition-transform">
          🤖
        </div>
        <div>
          <h1 class="text-base sm:text-lg font-black tracking-tight text-slate-900 leading-none">
            Benim Arduino Dünyam
          </h1>
          <p class="text-[10px] font-extrabold text-indigo-600 tracking-wide uppercase mt-0.5">
            Çocuklar İçin Akıllı Stüdyo ✨
          </p>
        </div>
      </div>

      <!-- Orta: 4 Adımlı Sihirbaz Navigasyonu -->
      <nav class="flex items-center bg-slate-100/90 p-1 rounded-2xl border border-slate-200/90 text-xs font-black shadow-inner overflow-x-auto">
        <button
          v-for="step in steps"
          :key="step.num"
          type="button"
          @click="$emit('go-step', step.num)"
          :class="[
            'px-3 sm:px-4 py-2 rounded-xl transition-all flex items-center gap-1.5 shrink-0 select-none cursor-pointer',
            currentStep === step.num
              ? `${step.activeBg} text-white shadow-md scale-102`
              : currentStep > step.num
              ? 'text-emerald-700 bg-emerald-50/80 hover:bg-emerald-100/80'
              : 'text-slate-600 hover:text-slate-900 hover:bg-white/70'
          ]"
        >
          <span class="text-sm">{{ step.icon }}</span>
          <span>{{ step.num }}. {{ step.title }}</span>
          <span
            v-if="currentStep > step.num"
            class="w-4 h-4 rounded-full bg-emerald-600 text-white flex items-center justify-center text-[10px] font-extrabold ml-0.5"
          >
            ✓
          </span>
        </button>
      </nav>

      <!-- Sağ: Çanta ve Ayarlar Butonları -->
      <div class="flex items-center gap-2">
        <!-- Malzeme Çantam Butonu -->
        <button
          type="button"
          @click="$emit('open-inventory')"
          class="px-3.5 py-2 rounded-xl border-2 border-indigo-200 bg-indigo-50/80 hover:bg-indigo-100 text-indigo-900 text-xs font-black transition flex items-center gap-2 shadow-xs cursor-pointer select-none"
        >
          <span class="text-base">🎒</span>
          <span class="hidden sm:inline">Malzeme Çantam</span>
          <span class="px-1.5 py-0.2 rounded-full bg-indigo-600 text-white text-[11px] font-extrabold">
            {{ inventoryCount }}
          </span>
        </button>

        <!-- Ayarlar (Model Seçici) Butonu -->
        <button
          type="button"
          @click="$emit('open-settings')"
          class="p-2 sm:px-3 sm:py-2 rounded-xl border-2 border-slate-200 bg-white hover:bg-slate-50 text-slate-700 text-xs font-black transition flex items-center gap-1.5 shadow-xs cursor-pointer select-none"
          title="Yapay Zeka ve Model Ayarları"
        >
          <span class="text-base">⚙️</span>
          <span class="hidden md:inline">Ayarlar</span>
          <span v-if="activeModelName" class="text-[10px] text-slate-400 font-bold hidden lg:inline truncate max-w-[100px]">
            ({{ activeModelName }})
          </span>
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
  (e: 'open-settings'): void;
}>();

const steps = [
  { num: 1, title: 'Hayal Et', icon: '💭', activeBg: 'bg-indigo-600' },
  { num: 2, title: 'Devreyi Kur', icon: '🔌', activeBg: 'bg-sky-600' },
  { num: 3, title: 'Nasıl Çalışacak?', icon: '🧠', activeBg: 'bg-amber-600' },
  { num: 4, title: 'Çalıştır', icon: '🚀', activeBg: 'bg-emerald-600' },
];
</script>

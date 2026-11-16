<template>
  <div class="bg-white rounded-2xl p-5 border border-slate-200 shadow-sm">
    <div class="flex items-center justify-between mb-4 pb-2 border-b border-slate-100">
      <div>
        <h3 class="font-extrabold text-slate-900 text-base">Kodun Mantığı (Algoritma Blokları)</h3>
        <p class="text-xs text-slate-500 font-medium">Arduino bu devrede sırasıyla şu mantıkla çalışır:</p>
      </div>
      <span class="text-xs font-bold text-indigo-700 bg-indigo-50 px-2.5 py-1 rounded-lg">
        {{ dusunmeAdimlari.length }} Mantık Adımı
      </span>
    </div>

    <!-- Mantık Adım Listesi (Scratch benzeri birbirini takip eden temiz bloklar) -->
    <div class="flex flex-col gap-2.5">
      <div
        v-for="(card, index) in dusunmeAdimlari"
        :key="index"
        class="p-3.5 rounded-xl border border-slate-200 bg-slate-50/60 hover:bg-slate-50 transition flex items-start gap-3"
      >
        <!-- Sol İkon Rozeti -->
        <div
          :class="[
            'w-8 h-8 rounded-lg flex items-center justify-center text-sm shrink-0 font-bold text-white',
            getBadgeColor(card.tip)
          ]"
        >
          {{ index + 1 }}
        </div>

        <!-- Metin -->
        <div class="flex-1 min-w-0">
          <div class="flex items-center gap-2 mb-0.5">
            <span class="font-extrabold text-xs text-slate-900">{{ card.baslik }}</span>
            <span class="text-[10px] font-bold uppercase tracking-wider text-slate-400 bg-slate-100 px-1.5 py-0.2 rounded">
              {{ card.tip }}
            </span>
          </div>
          <p class="text-xs text-slate-600 font-medium leading-relaxed">
            {{ card.aciklama }}
          </p>
        </div>
      </div>
    </div>
  </div>
</template>

<script setup lang="ts">
import type { DusunmeAdimi, DusunmeTipi } from '../types/project';

defineProps<{
  dusunmeAdimlari: DusunmeAdimi[];
}>();

function getBadgeColor(tip: DusunmeTipi): string {
  switch (tip) {
    case 'BASLANGIC': return 'bg-indigo-600';
    case 'DONGU': return 'bg-sky-600';
    case 'EGER': return 'bg-amber-600';
    case 'YAP': return 'bg-emerald-600';
    default: return 'bg-slate-600';
  }
}
</script>

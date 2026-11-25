---
name: add-vue-component
description: "Kid Arduino Studio projesine yeni bir Vue 3 bileşeni veya modal ekleme rehberi. TypeScript setup script standartları, Neobrutalism UI stili, props/emits tanımları ve typecheck doğrulamasını kapsar."
---

# Yeni Vue 3 Bileşeni Ekleme Kılavuzu

Bu beceri, **Kid Arduino Studio** projesine yeni bir modal, sayfa veya görsel arayüz bileşeni eklerken izlenmesi gereken adımları tanımlar.

---

## 1. Dosya Konumu ve Adlandırma
- Tüm bileşenler `frontend/src/components/` dizininde yer alır.
- PascalCase adlandırma kullanılır (Örnek: `AdminDeviceModal.vue`, `SensorBadge.vue`).
- Paylaşılan tipler `frontend/src/types/` içine, yeniden kullanılabilir mantık `frontend/src/composables/` içine konur.

---

## 2. Standart Bileşen Şablonu

```vue
<script setup lang="ts">
import { computed } from 'vue';

// 1. Props tanımlaması (TypeScript generic ile)
interface Props {
  isOpen: boolean;
  title?: string;
}

const props = withDefaults(defineProps<Props>(), {
  title: 'Bilgi Paneli ✨'
});

// 2. Emits tanımlaması
const emit = defineEmits<{
  (e: 'close'): void;
  (e: 'save', payload: string): void;
}>();

// 3. Reaktif mantık
const isVisible = computed(() => props.isOpen);
</script>

<template>
  <div
    v-if="isVisible"
    class="fixed inset-0 z-50 bg-slate-900/75 backdrop-blur-xs flex items-center justify-center p-3 sm:p-5 select-none animate-in fade-in"
    @click.self="emit('close')"
  >
    <div
      class="bg-white rounded-[32px] border-[3px] border-slate-900 shadow-[0_14px_0_rgba(15,23,42,0.35)] max-w-xl w-full max-h-[88vh] overflow-hidden flex flex-col"
    >
      <!-- Başlık Çubuğu (Shrink-0) -->
      <div class="bg-[#bae6fd] border-b-2 border-slate-900 px-5 py-3.5 flex items-center justify-between shrink-0">
        <h3 class="font-black text-slate-900 text-lg sm:text-xl flex items-center gap-2">
          {{ title }}
        </h3>
        <button
          type="button"
          class="w-9 h-9 rounded-xl bg-rose-500 hover:bg-rose-600 text-white font-black text-lg border-2 border-slate-900 shadow-[0_3px_0_#0f172a] active:translate-y-0.5 active:shadow-none flex items-center justify-center transition-all cursor-pointer"
          @click="emit('close')"
        >
          ✕
        </button>
      </div>

      <!-- Kaydırılabilir İçerik Gövdesi -->
      <div class="p-5 overflow-y-auto space-y-4 flex-1">
        <slot />
      </div>
    </div>
  </div>
</template>
```

---

## 3. Doğrulama Adımları
Yeni bileşeni ekledikten veya değiştirdikten sonra terminalde mutlaka çalıştırın:
```bash
# Tip kontrolü (0 hata olmalı)
npm.cmd --prefix frontend run typecheck

# Üretim derlemesi
npm.cmd --prefix frontend run build
```

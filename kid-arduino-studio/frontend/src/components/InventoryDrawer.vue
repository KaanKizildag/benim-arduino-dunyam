<template>
  <div v-if="isOpen">
    <!-- Karartma Arka Planı -->
    <div
      class="fixed inset-0 z-50 bg-slate-900/50 backdrop-blur-xs transition-opacity"
      @click="$emit('close')"
    ></div>

    <!-- Sağdan Açılan Çekmece -->
    <div
      class="fixed inset-y-0 right-0 z-50 w-full max-w-md bg-white border-l-2 border-slate-200 shadow-2xl flex flex-col transform transition-transform duration-300 ease-out"
    >
      <!-- Başlık Çubuğu -->
      <div class="p-5 border-b border-slate-200 flex items-center justify-between bg-indigo-50/50">
        <div class="flex items-center gap-3">
          <div class="w-10 h-10 rounded-2xl bg-indigo-600 text-white flex items-center justify-center text-xl shadow-xs">
            🎒
          </div>
          <div>
            <h3 class="text-base font-black text-slate-900 leading-tight">
              Malzeme Çantam
            </h3>
            <p class="text-xs font-bold text-slate-500">
              Kullanmak istediğin parçaları seç ({{ selectedItems.length }} parça hazır)
            </p>
          </div>
        </div>

        <button
          type="button"
          @click="$emit('close')"
          class="w-9 h-9 rounded-xl border border-slate-300 bg-white hover:bg-slate-100 text-slate-600 font-black text-sm flex items-center justify-center cursor-pointer transition"
        >
          ✕
        </button>
      </div>

      <!-- Hızlı Seçim Butonları -->
      <div class="px-5 py-2.5 bg-slate-50 border-b border-slate-200 flex items-center justify-between text-xs">
        <span class="font-bold text-slate-500">Hızlı İşlem:</span>
        <div class="flex items-center gap-2">
          <button
            type="button"
            @click="selectAll"
            class="px-2.5 py-1 rounded-lg bg-white border border-slate-300 font-bold text-slate-700 hover:bg-slate-100 transition"
          >
            Hepsini Seç
          </button>
          <button
            type="button"
            @click="resetDefault"
            class="px-2.5 py-1 rounded-lg bg-white border border-slate-300 font-bold text-slate-700 hover:bg-slate-100 transition"
          >
            Varsayılan Set
          </button>
        </div>
      </div>

      <!-- Parçalar Izgarası -->
      <div class="flex-1 overflow-y-auto p-5 grid grid-cols-1 sm:grid-cols-2 gap-3">
        <button
          v-for="item in inventoryList"
          :key="item.id"
          type="button"
          @click="toggleItem(item.id)"
          :class="[
            'p-3.5 rounded-2xl border-2 text-left transition-all flex items-center gap-3 relative select-none cursor-pointer',
            isSelected(item.id)
              ? 'border-indigo-500 bg-indigo-50/70 text-indigo-950 shadow-xs scale-101'
              : 'border-slate-200 bg-white hover:bg-slate-50 text-slate-600'
          ]"
        >
          <span class="text-3xl shrink-0 p-1.5 rounded-xl bg-white shadow-xs border border-slate-100">
            {{ item.icon }}
          </span>

          <div class="flex-1 min-w-0">
            <div class="text-xs font-black truncate text-slate-900">{{ item.name }}</div>
            <div class="text-[11px] font-bold text-slate-400 truncate">{{ item.tag }}</div>
          </div>

          <!-- Seçili Rozeti -->
          <span
            v-if="isSelected(item.id)"
            class="w-6 h-6 rounded-full bg-indigo-600 text-white flex items-center justify-center text-xs font-black shrink-0 shadow-xs"
          >
            ✓
          </span>
          <span
            v-else
            class="w-6 h-6 rounded-full border-2 border-slate-300 shrink-0"
          ></span>
        </button>
      </div>

      <!-- Alt Kapat & Uygula Butonu -->
      <div class="p-5 border-t border-slate-200 bg-white">
        <button
          type="button"
          @click="$emit('close')"
          class="w-full py-3.5 rounded-2xl bg-indigo-600 hover:bg-indigo-700 text-white font-extrabold text-sm shadow-md transition flex items-center justify-center gap-2 cursor-pointer"
        >
          <span>Tamam, Çantam Hazır! 🎒</span>
        </button>
      </div>
    </div>
  </div>
</template>

<script setup lang="ts">
import { ref, watch } from 'vue';
import type { InventoryItem } from '../types/project';

const props = defineProps<{
  isOpen: boolean;
  modelValue: string[];
}>();

const emit = defineEmits<{
  (e: 'update:modelValue', value: string[]): void;
  (e: 'close'): void;
}>();

const inventoryList: InventoryItem[] = [
  { id: 'ARDUINO_UNO', name: 'Arduino Uno R3', icon: '🤖', tag: 'Ana Beyin', category: 'board' },
  { id: 'BREADBOARD', name: 'Deney Tahtası', icon: '🍞', tag: 'Breadboard', category: 'board' },
  { id: 'LED_RED', name: 'Kırmızı LED', icon: '🔴', tag: 'Işık / Lamba', category: 'output' },
  { id: 'RESISTOR_220', name: '220Ω Direnç', icon: '⚡', tag: 'LED Koruyucu', category: 'passive' },
  { id: 'LDR_SENSOR', name: 'Işık Sensörü (LDR)', icon: '☀️', tag: 'Karanlık Gözü', category: 'sensor' },
  { id: 'HCSR04', name: 'Mesafe Sensörü', icon: '🦇', tag: 'Yarasa Sonar', category: 'sensor' },
  { id: 'BUZZER', name: 'Buzzer (Korna)', icon: '🔊', tag: 'Ses Çıkarıcı', category: 'output' },
  { id: 'BUTTON', name: 'Dokunma Butonu', icon: '🔘', tag: 'Tuş / Düğme', category: 'sensor' },
  { id: 'SERVO', name: 'Servo Motor', icon: '🦾', tag: 'Dönen Robot Kol', category: 'output' },
];

const selectedItems = ref<string[]>(props.modelValue || ['ARDUINO_UNO', 'BREADBOARD', 'LED_RED', 'RESISTOR_220', 'LDR_SENSOR', 'HCSR04', 'BUZZER']);

watch(() => props.modelValue, (newVal) => {
  if (newVal) selectedItems.value = [...newVal];
});

function isSelected(id: string): boolean {
  return selectedItems.value.includes(id);
}

function toggleItem(id: string) {
  if (id === 'ARDUINO_UNO' || id === 'BREADBOARD') return; // Zorunlu temel parçalar
  if (selectedItems.value.includes(id)) {
    selectedItems.value = selectedItems.value.filter(i => i !== id);
  } else {
    selectedItems.value = [...selectedItems.value, id];
  }
  emit('update:modelValue', selectedItems.value);
}

function selectAll() {
  selectedItems.value = inventoryList.map(i => i.id);
  emit('update:modelValue', selectedItems.value);
}

function resetDefault() {
  selectedItems.value = ['ARDUINO_UNO', 'BREADBOARD', 'LED_RED', 'RESISTOR_220', 'LDR_SENSOR', 'HCSR04', 'BUZZER'];
  emit('update:modelValue', selectedItems.value);
}
</script>

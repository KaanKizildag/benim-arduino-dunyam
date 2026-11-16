<template>
  <div class="bg-white rounded-2xl p-5 border border-slate-200 shadow-sm">
    <div class="flex items-center justify-between mb-3">
      <div class="flex items-center gap-2">
        <span class="text-xl">🧰</span>
        <h3 class="font-extrabold text-slate-800 text-sm sm:text-base">Elindeki Parçalar</h3>
      </div>
      <span class="text-xs font-bold text-slate-500 bg-slate-100 px-2.5 py-1 rounded-lg">
        {{ selectedItems.length }} Parça Seçili
      </span>
    </div>

    <!-- Parçalar Izgarası -->
    <div class="grid grid-cols-2 sm:grid-cols-4 gap-2.5">
      <button
        v-for="item in inventoryList"
        :key="item.id"
        type="button"
        @click="toggleItem(item.id)"
        :class="[
          'p-3 rounded-xl border text-left transition flex items-center gap-3 relative select-none',
          isSelected(item.id)
            ? 'border-indigo-500 bg-indigo-50/50 text-indigo-950 font-bold shadow-xs'
            : 'border-slate-200 bg-white hover:bg-slate-50 text-slate-600 font-medium'
        ]"
      >
        <span class="text-2xl shrink-0">{{ item.icon }}</span>
        <div class="flex-1 min-w-0">
          <div class="text-xs font-extrabold truncate">{{ item.name }}</div>
          <div class="text-[10px] text-slate-400 truncate">{{ item.tag }}</div>
        </div>
        <span
          v-if="isSelected(item.id)"
          class="w-5 h-5 rounded-full bg-indigo-600 text-white flex items-center justify-center text-[11px] font-bold shrink-0"
        >
          ✓
        </span>
      </button>
    </div>
  </div>
</template>

<script setup lang="ts">
import { ref } from 'vue';

const props = defineProps<{
  modelValue: string[];
}>();

const emit = defineEmits<{
  (e: 'update:modelValue', value: string[]): void;
}>();

const inventoryList = [
  { id: 'ARDUINO_UNO', name: 'Arduino Uno', icon: '🤖', tag: 'Ana Beyin' },
  { id: 'LED_RED', name: 'Kırmızı LED', icon: '🔴', tag: 'Işık / Lamba' },
  { id: 'RESISTOR_220', name: '220Ω Direnç', icon: '⚡', tag: 'Koruyucu' },
  { id: 'LDR_SENSOR', name: 'Işık Sensörü', icon: '☀️', tag: 'Göz / LDR' },
  { id: 'HCSR04', name: 'Mesafe Sensörü', icon: '🦇', tag: 'Sonar Göz' },
  { id: 'BUZZER', name: 'Buzzer', icon: '🔊', tag: 'Ses / Korna' },
  { id: 'BUTTON', name: 'Buton Tuş', icon: '🔘', tag: 'Dokunma' },
  { id: 'SERVO', name: 'Servo Motor', icon: '🦾', tag: 'Dönen Kol' }
];

const selectedItems = ref<string[]>(props.modelValue || ['ARDUINO_UNO', 'LED_RED', 'RESISTOR_220', 'LDR_SENSOR', 'HCSR04', 'BUZZER']);

function isSelected(id: string): boolean {
  return selectedItems.value.includes(id);
}

function toggleItem(id: string) {
  if (id === 'ARDUINO_UNO') return;
  if (selectedItems.value.includes(id)) {
    selectedItems.value = selectedItems.value.filter(item => item !== id);
  } else {
    selectedItems.value = [...selectedItems.value, id];
  }
  emit('update:modelValue', selectedItems.value);
}
</script>

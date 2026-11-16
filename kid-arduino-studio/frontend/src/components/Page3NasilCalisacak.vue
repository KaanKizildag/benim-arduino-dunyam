<template>
  <div class="max-w-5xl mx-auto w-full flex flex-col gap-6 py-4 px-3 sm:px-6">
    
    <!-- Üst Başlık & Açıklama -->
    <div class="text-center">
      <div class="inline-flex items-center gap-2 px-3.5 py-1.5 rounded-full bg-amber-100 text-amber-900 text-xs font-black mb-2 shadow-xs">
        <span>🧠</span>
        <span>Sebep ➔ Sonuç İnteraktif Simülatörü</span>
      </div>
      <h2 class="text-xl sm:text-2xl font-black text-slate-900">
        Bu Devre Nasıl Düşünüyor ve Çalışıyor?
      </h2>
      <p class="text-xs sm:text-sm text-slate-600 font-medium max-w-xl mx-auto mt-1">
        Karmaşık kodlar yok! Sensörü elle değiştir, Arduino beyninin nasıl karar verdiğini ve lambanın nasıl tepki verdiğini canlı izle!
      </p>
    </div>

    <!-- 3 Sütunlu Canlı Sebep-Sonuç Simülatörü -->
    <div class="grid grid-cols-1 lg:grid-cols-3 gap-4 items-stretch">
      
      <!-- SÜTUN 1: GÖZLEMLE (Sensör Durumu / Çocuk Kontrol Eder) -->
      <div class="bg-white rounded-3xl p-5 border-2 border-slate-200 shadow-md flex flex-col justify-between">
        <div>
          <div class="flex items-center gap-2 mb-3">
            <span class="w-7 h-7 rounded-xl bg-sky-500 text-white font-black text-xs flex items-center justify-center">1</span>
            <h3 class="text-sm font-black text-slate-900 uppercase tracking-wide">
              Gözlemle (Sensör)
            </h3>
          </div>
          <p class="text-xs text-slate-600 font-medium mb-4 leading-relaxed">
            {{ akisAdimi?.gozlemle || 'Sensör çevredeki değişiklikleri anlık olarak dinler.' }}
          </p>
        </div>

        <!-- İnteraktif Kaydırıcı / Sensör Durum Kontrolü -->
        <div class="bg-slate-50 p-4 rounded-2xl border-2 border-slate-200 flex flex-col gap-3 my-2">
          <div class="flex items-center justify-between text-xs font-black text-slate-700">
            <span>{{ isNightMode ? '🌙 Gece / Karanlık' : '☀️ Gündüz / Aydınlık' }}</span>
            <span class="px-2 py-0.5 rounded-md text-[11px]" :class="isNightMode ? 'bg-indigo-600 text-white' : 'bg-amber-400 text-slate-900'">
              Değer: {{ sensorValue }}
            </span>
          </div>

          <!-- Kaydırıcı Slider -->
          <input
            type="range"
            min="0"
            max="1000"
            v-model.number="sensorValue"
            class="w-full accent-indigo-600 cursor-pointer h-2 bg-slate-200 rounded-lg"
          />

          <!-- Hızlı Toggle Butonları -->
          <div class="grid grid-cols-2 gap-2 mt-1">
            <button
              type="button"
              @click="sensorValue = 850"
              :class="[
                'py-2 px-3 rounded-xl font-extrabold text-xs transition cursor-pointer flex items-center justify-center gap-1.5',
                !isNightMode ? 'bg-amber-400 text-amber-950 shadow-xs scale-102' : 'bg-white border border-slate-200 text-slate-600 hover:bg-slate-100'
              ]"
            >
              <span>☀️ Gündüz</span>
            </button>
            <button
              type="button"
              @click="sensorValue = 250"
              :class="[
                'py-2 px-3 rounded-xl font-extrabold text-xs transition cursor-pointer flex items-center justify-center gap-1.5',
                isNightMode ? 'bg-indigo-600 text-white shadow-xs scale-102' : 'bg-white border border-slate-200 text-slate-600 hover:bg-slate-100'
              ]"
            >
              <span>🌙 Gece</span>
            </button>
          </div>
        </div>

        <span class="text-[11px] font-bold text-slate-400 text-center block mt-2">
          👆 Parmağınla veya butonla ışık seviyesini değiştir!
        </span>
      </div>

      <!-- SÜTUN 2: KARAR VER (Arduino Pelerinli Robot Beyin) -->
      <div class="bg-gradient-to-b from-indigo-50 to-white rounded-3xl p-5 border-2 border-indigo-200 shadow-md flex flex-col justify-between items-center text-center relative overflow-hidden">
        
        <div class="w-full text-left flex items-center gap-2 mb-2">
          <span class="w-7 h-7 rounded-xl bg-indigo-600 text-white font-black text-xs flex items-center justify-center">2</span>
          <h3 class="text-sm font-black text-indigo-950 uppercase tracking-wide">
            Karar Ver (Arduino Beyni)
          </h3>
        </div>

        <!-- Pelerinli Robot Beyin Karakteri -->
        <div class="relative my-3 group">
          <div class="w-24 h-24 rounded-3xl bg-indigo-600 text-white flex items-center justify-center text-5xl shadow-xl shadow-indigo-200 relative z-10 transition-transform">
            🧠
          </div>
          <!-- Pelerin İllüstrasyonu -->
          <div class="absolute -top-1 -right-3 w-8 h-12 bg-rose-500 rounded-tr-xl rounded-br-2xl transform rotate-12 z-0 opacity-90 shadow-xs"></div>
          <!-- Beyin Düşünme Parıltısı -->
          <div
            v-if="isNightMode"
            class="absolute -inset-2 bg-indigo-400 rounded-3xl opacity-40 blur-md animate-pulse z-0"
          ></div>
        </div>

        <!-- Karar Kuralları Kutusu -->
        <div class="w-full bg-white p-3.5 rounded-2xl border-2 border-indigo-100 shadow-xs flex flex-col gap-2 text-xs">
          <span class="font-black text-slate-700 block">
            {{ akisAdimi?.karar_ver || 'Koşul: Işık azaldı mı?' }}
          </span>

          <div
            :class="[
              'p-2.5 rounded-xl font-extrabold text-xs transition flex items-center justify-center gap-2',
              isNightMode
                ? 'bg-emerald-500 text-white shadow-xs animate-bounce'
                : 'bg-slate-100 text-slate-500'
            ]"
          >
            <span>{{ isNightMode ? '✓ EVET! (Karanlık Oldu)' : '✗ HAYIR (Aydınlık)' }}</span>
          </div>
        </div>

        <!-- İki Yöne Karar Okları -->
        <div class="text-xs font-black text-indigo-600 flex items-center gap-1.5 mt-2">
          <span>⚡ Karar:</span>
          <span class="underline">{{ isNightMode ? akisAdimi?.evet_sonucu : akisAdimi?.hayir_sonucu }}</span>
        </div>
      </div>

      <!-- SÜTUN 3: UYGULA (Görsel Canlı Donanım Önizlemesi) -->
      <div class="bg-white rounded-3xl p-5 border-2 border-slate-200 shadow-md flex flex-col justify-between items-center text-center">
        
        <div class="w-full text-left flex items-center gap-2 mb-2">
          <span class="w-7 h-7 rounded-xl bg-emerald-500 text-white font-black text-xs flex items-center justify-center">3</span>
          <h3 class="text-sm font-black text-slate-900 uppercase tracking-wide">
            Uygula (Donanım Tepkisi)
          </h3>
        </div>

        <!-- Canlı Tepki Veren LED / Donanım Animasyonu -->
        <div class="relative my-4 flex flex-col items-center">
          <!-- Parlayan Kırmızı LED -->
          <div class="relative">
            <div
              :class="[
                'w-20 h-20 rounded-full flex items-center justify-center text-4xl transition-all duration-300',
                isNightMode
                  ? 'bg-rose-500 text-white shadow-2xl shadow-rose-500 ring-8 ring-rose-200 scale-110'
                  : 'bg-slate-200 text-slate-400'
              ]"
            >
              💡
            </div>
            <!-- Işık Hüzmeleri Efekti -->
            <div
              v-if="isNightMode"
              class="absolute -inset-4 rounded-full border-4 border-dashed border-rose-300 animate-spin opacity-75"
              style="animation-duration: 6s;"
            ></div>
          </div>

          <!-- LED'in Konuşma Balonu -->
          <div
            :class="[
              'mt-4 px-3.5 py-2 rounded-2xl text-xs font-black shadow-xs transition-all max-w-[220px]',
              isNightMode
                ? 'bg-rose-50 text-rose-900 border border-rose-200 scale-102'
                : 'bg-slate-100 text-slate-500 border border-slate-200'
            ]"
          >
            <span v-if="isNightMode">
              "Karanlık oldu! Şimdi odanı aydınlatıyorum! ✨"
            </span>
            <span v-else>
              "Hava aydınlık, enerjiyi saklamak için dinleniyorum. 😴"
            </span>
          </div>
        </div>

        <!-- Durum Rozeti -->
        <div class="w-full">
          <span
            :class="[
              'w-full py-2.5 rounded-xl font-black text-xs block',
              isNightMode ? 'bg-rose-500 text-white shadow-xs' : 'bg-slate-100 text-slate-600'
            ]"
          >
            {{ isNightMode ? 'LAMBA: YANDI (AÇIK) 🔥' : 'LAMBA: SÖNDÜ (KAPALI) ❄️' }}
          </span>
        </div>

      </div>

    </div>

    <!-- Alt Çubuk: Kodu Gör Modalı ve Çalıştırmaya Geç -->
    <div class="flex flex-col sm:flex-row items-center justify-between gap-3 pt-4 border-t border-slate-200">
      
      <!-- Meraklı Çocuklar İçin Kodu Gör Butonu -->
      <button
        type="button"
        @click="$emit('open-code-modal')"
        class="px-4 py-2.5 rounded-2xl border-2 border-slate-300 bg-white hover:bg-slate-100 text-slate-700 font-extrabold text-xs transition flex items-center gap-2 cursor-pointer shadow-xs"
      >
        <span>&lt;/&gt;</span>
        <span>Perde Arkasındaki Arduino Kodunu Gör!</span>
      </button>

      <!-- İleri / Çalıştır Butonu -->
      <div class="flex items-center gap-2 w-full sm:w-auto">
        <button
          type="button"
          @click="$emit('prev-page')"
          class="px-4 py-3 rounded-2xl border-2 border-slate-200 text-slate-700 font-extrabold text-xs hover:bg-slate-100 transition cursor-pointer"
        >
          ◀ Devreye Geri Dön
        </button>

        <button
          type="button"
          @click="$emit('next-page')"
          class="flex-1 sm:flex-initial px-7 py-3 rounded-2xl bg-emerald-600 hover:bg-emerald-700 text-white font-black text-sm shadow-md transition flex items-center justify-center gap-2 cursor-pointer"
        >
          <span>Devreyi Çalıştırmaya Geç ➔</span>
        </button>
      </div>

    </div>

  </div>
</template>

<script setup lang="ts">
import { ref, computed } from 'vue';
import type { AkisAdimi } from '../types/project';

const props = defineProps<{
  akisAdimi?: AkisAdimi;
  arduinoKodu?: string;
}>();

defineEmits<{
  (e: 'next-page'): void;
  (e: 'prev-page'): void;
  (e: 'open-code-modal'): void;
}>();

// Simülatör Işık Değeri (0 - 1000): 400 altı karanlık / gece kabul edilir
const sensorValue = ref(250);

const isNightMode = computed(() => {
  return sensorValue.value < 400;
});
</script>

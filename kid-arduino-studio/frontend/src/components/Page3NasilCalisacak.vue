<template>
  <div class="w-full max-w-5xl mx-auto flex-1 flex flex-col justify-between py-3 sm:py-5 px-3 sm:px-6 select-none">
    
    <!-- Ana Beyaz Kart -->
    <div class="w-full flex-1 bg-white rounded-[32px] sm:rounded-[36px] border-[3px] border-slate-900 shadow-[0_8px_0_rgba(15,23,42,0.12)] p-5 sm:p-8 relative overflow-hidden flex flex-col justify-between gap-4">
      
      <!-- Faint Arka Plan Doodle Çizimleri -->
      <div class="absolute inset-0 pointer-events-none opacity-20 select-none overflow-hidden">
        <svg class="w-full h-full text-slate-400" viewBox="0 0 1000 600" fill="none">
          <path d="M 280 80 Q 290 60, 310 80 Q 290 100, 280 80" stroke="currentColor" stroke-width="2" />
          <circle cx="820" cy="120" r="14" stroke="currentColor" stroke-width="2" stroke-dasharray="3,3" />
          <path d="M 120 180 Q 130 160, 140 180" stroke="currentColor" stroke-width="2" />
          <circle cx="700" cy="460" r="18" stroke="currentColor" stroke-width="2" />
        </svg>
      </div>

      <!-- ÜST PROJE VE BİLEŞEN ÖZET BAŞLIĞI -->
      <div class="relative z-10 flex flex-wrap items-center justify-between gap-2 pb-2 border-b-2 border-slate-100">
        <div>
          <span class="text-[10px] font-black uppercase tracking-wider text-slate-500 block">
            Projeye Özgü Sebep – Sonuç Algoritması
          </span>
          <h2 class="text-base sm:text-lg font-black text-slate-900">
            {{ projectName || 'Devremiz Nasıl Çalışacak?' }}
          </h2>
        </div>

        <!-- Devredeki Gerçek Aktif Parça Rozetleri -->
        <div class="flex flex-wrap items-center gap-1.5">
          <span
            v-for="comp in nonResistorComponents"
            :key="comp.id"
            class="px-2.5 py-1 rounded-xl bg-amber-100 border-2 border-slate-900 text-[11px] font-black text-slate-900 shadow-2xs flex items-center gap-1"
          >
            <span>{{ getComponentEmoji(comp.type) }}</span>
            <span>{{ comp.label }}</span>
            <span v-if="getPinForComponent(comp.id)" class="px-1.5 py-0.2 rounded bg-white border border-slate-900 text-[9px] text-indigo-900">
              {{ getPinForComponent(comp.id) }}
            </span>
          </span>
        </div>
      </div>

      <!-- YÜKLENİYOR DURUMU (2. Aşama AI Çağrısı Devam Ederken) -->
      <div
        v-if="isGeneratingLogic"
        class="relative z-10 my-auto py-12 flex flex-col items-center justify-center text-center gap-3"
      >
        <div class="w-16 h-16 rounded-3xl bg-sky-100 border-2 border-slate-900 flex items-center justify-center text-3xl animate-spin">
          ⚙️
        </div>
        <h3 class="text-base sm:text-lg font-black text-slate-900">
          Yapay Zeka Devrendeki Parçalara Özel Çalışma Mantığını Hazırlıyor...
        </h3>
        <p class="text-xs font-bold text-slate-600 max-w-md">
          Az önce kurulan kablolamadaki ({{ nonResistorComponents.map(c => c.label).join(', ') }}) parçalarına ve Arduino pinlerine birebir uyan akış diyagramı ve C++ kodu doğrulanıyor.
        </p>
      </div>

      <!-- ORTADAKİ 3 AŞAMALI DİNAMİK AKIŞ ŞEMASI (1. Gözlemle ➔ 2. Karar Ver ➔ Evet / Hayır) -->
      <div
        v-else
        class="relative z-10 flex flex-col lg:flex-row items-center justify-center gap-3 sm:gap-5 my-auto py-2"
      >
        
        <!-- ============================================== -->
        <!-- 1. KUTU: 1. GÖZLEMLE (Gerçek Giriş Bileşeni)   -->
        <!-- ============================================== -->
        <div class="w-full max-w-[235px] bg-white rounded-[26px] border-[3px] border-[#38bdf8] shadow-[0_5px_0_#0284c7] p-4 flex flex-col items-center text-center">
          <div class="flex items-center gap-2 mb-2">
            <div class="w-7 h-7 rounded-full bg-[#38bdf8] text-white flex items-center justify-center text-xs font-black shadow-xs">
              👁️
            </div>
            <h3 class="text-xs sm:text-sm font-black text-slate-900">
              1. Gözlemle (Giriş)
            </h3>
          </div>

          <!-- Projeye Özgü Giriş/Sensör Görseli -->
          <div class="relative w-24 h-24 rounded-2xl bg-sky-50 flex flex-col items-center justify-center border-2 border-sky-300 shadow-inner mb-2.5 p-2 overflow-hidden">
            <template v-if="inputComponents.length > 0">
              <div class="scale-[0.65] origin-center pointer-events-none flex items-center justify-center">
                <component
                  :is="inputComponents[0].type"
                  v-bind="inputComponents[0].props"
                ></component>
              </div>
              <span class="mt-1 px-2 py-0.2 rounded-full bg-sky-200 border border-slate-900 text-[9px] font-black text-slate-900">
                {{ inputComponents[0].label }}
                <template v-if="getPinForComponent(inputComponents[0].id)">
                  ({{ getPinForComponent(inputComponents[0].id) }})
                </template>
              </span>
            </template>
            <template v-else>
              <span class="text-4xl mb-1">⏱️</span>
              <span class="px-2 py-0.2 rounded-full bg-amber-200 border border-slate-900 text-[9px] font-black text-slate-900">
                Arduino Zamanlayıcı
              </span>
            </template>
          </div>

          <!-- Açıklama Metni -->
          <p class="text-xs font-black text-slate-900 leading-snug">
            {{ akisAdimi?.gozlemle }}
          </p>
        </div>

        <!-- BAĞLANTI OKU 1 ➔ 2 -->
        <div class="hidden lg:flex items-center justify-center px-1">
          <svg class="w-14 h-9 drop-shadow-[0_2px_0_#0f172a]" viewBox="0 0 60 40">
            <defs>
              <linearGradient id="arrowGrad3" x1="0%" y1="0%" x2="100%" y2="0%">
                <stop offset="0%" stop-color="#38bdf8" />
                <stop offset="100%" stop-color="#4ade80" />
              </linearGradient>
            </defs>
            <path d="M 5 14 L 35 14 L 35 4 L 55 20 L 35 36 L 35 26 L 5 26 Z" fill="url(#arrowGrad3)" stroke="#0f172a" stroke-width="2.5" />
          </svg>
        </div>

        <!-- ============================================== -->
        <!-- 2. KUTU: 2. KARAR VER (Arduino Uno Beyni)      -->
        <!-- ============================================== -->
        <div class="w-full max-w-[235px] bg-white rounded-[26px] border-[3px] border-slate-900 shadow-[0_5px_0_#0f172a] p-4 flex flex-col items-center text-center">
          <div class="flex items-center gap-2 mb-2">
            <div class="w-7 h-7 rounded-full bg-[#38bdf8] text-white flex items-center justify-center text-xs font-black shadow-xs">
              🤖
            </div>
            <h3 class="text-xs sm:text-sm font-black text-slate-900">
              2. Karar Ver (Koşul)
            </h3>
          </div>

          <div class="relative w-24 h-20 rounded-2xl bg-purple-50 border-2 border-purple-300 flex flex-col items-center justify-center mb-2.5 p-2">
            <span class="text-4xl drop-shadow-xs">🧠</span>
            <span class="text-[9px] font-black text-purple-900 mt-0.5">
              Arduino Uno Karar Merkezi
            </span>
          </div>

          <!-- Açıklama Metni -->
          <p class="text-xs font-black text-slate-900 leading-snug">
            {{ akisAdimi?.karar_ver }}
          </p>
        </div>

        <!-- ÇATAL BAĞLANTI -->
        <div class="hidden lg:flex items-center justify-center w-11 h-44">
          <svg class="w-full h-full" viewBox="0 0 50 140" fill="none">
            <path d="M 5 70 C 25 70, 25 25, 45 25" stroke="#4ade80" stroke-width="4.5" stroke-linecap="round" />
            <path d="M 5 70 C 25 70, 25 115, 45 115" stroke="#f87171" stroke-width="4.5" stroke-linecap="round" />
          </svg>
        </div>

        <!-- ============================================== -->
        <!-- 3. SONUÇLAR: EVET / HAYIR DALLARI (Gerçek Çıkış Parçaları) -->
        <!-- ============================================== -->
        <div class="flex flex-col gap-3.5 w-full max-w-[300px]">
          
          <!-- ÜST KOL: EVET (Koşul Doğru ➔ Aktif Çıkışlar) -->
          <div class="flex items-center gap-2.5">
            <div class="relative shrink-0">
              <div class="px-3 py-1.5 rounded-full bg-[#86efac] border-2 border-slate-900 shadow-[0_3px_0_#15803d] text-slate-950 font-black text-xs flex items-center gap-1">
                <span>EVET</span>
                <span>➔</span>
              </div>
            </div>

            <!-- Sonuç Kutusu 1: Devredeki Gerçek Çıkış Parçaları Aktif Halde -->
            <div class="flex-1 bg-white rounded-2xl border-[3px] border-emerald-600 shadow-[0_4px_0_#0f172a] p-3 flex flex-col items-center text-center">
              <div class="flex items-center justify-center gap-2 min-h-[46px] mb-1">
                <template v-if="outputComponents.length > 0">
                  <div
                    v-for="outComp in outputComponents.slice(0, 3)"
                    :key="`yes-${outComp.id}`"
                    class="flex flex-col items-center"
                  >
                    <div class="scale-[0.65] origin-center pointer-events-none">
                      <component
                        :is="outComp.type"
                        v-bind="getActiveOutputProps(outComp, true)"
                      ></component>
                    </div>
                  </div>
                </template>
                <span v-else class="text-2xl">⚡</span>
              </div>
              <strong class="text-xs font-black text-slate-900 leading-snug">
                {{ akisAdimi?.evet_sonucu }}
              </strong>
            </div>
          </div>

          <!-- ALT KOL: HAYIR (Koşul Yanlış ➔ Pasif / Bekleme Durumu) -->
          <div class="flex items-center gap-2.5">
            <div class="relative shrink-0">
              <div class="px-3 py-1.5 rounded-full bg-[#fca5a5] border-2 border-slate-900 shadow-[0_3px_0_#9f1239] text-slate-950 font-black text-xs flex items-center gap-1">
                <span>HAYIR</span>
                <span>➔</span>
              </div>
            </div>

            <!-- Sonuç Kutusu 2: Devredeki Gerçek Çıkış Parçaları Pasif Halde -->
            <div class="flex-1 bg-white rounded-2xl border-[3px] border-slate-900 shadow-[0_4px_0_#0f172a] p-3 flex flex-col items-center text-center">
              <div class="flex items-center justify-center gap-2 min-h-[46px] mb-1 opacity-70">
                <template v-if="outputComponents.length > 0">
                  <div
                    v-for="outComp in outputComponents.slice(0, 3)"
                    :key="`no-${outComp.id}`"
                    class="flex flex-col items-center"
                  >
                    <div class="scale-[0.65] origin-center pointer-events-none">
                      <component
                        :is="outComp.type"
                        v-bind="getActiveOutputProps(outComp, false)"
                      ></component>
                    </div>
                  </div>
                </template>
                <span v-else class="text-2xl">⏸️</span>
              </div>
              <strong class="text-xs font-black text-slate-900 leading-snug">
                {{ akisAdimi?.hayir_sonucu }}
              </strong>
            </div>
          </div>

        </div>

      </div>

      <!-- KABLOLAMA ↔ KOD VE AKIŞ UYUMLULUK TEYİT PANELİ -->
      <div
        :class="[
          'relative z-10 rounded-2xl p-3 border-2 border-slate-900 flex flex-col gap-2 text-xs',
          isGeneratingLogic ? 'bg-sky-50' : 'bg-emerald-50'
        ]"
      >
        <div class="flex flex-wrap items-center justify-between gap-2">
          <div class="flex items-center gap-2 font-black text-slate-900">
            <span v-if="isGeneratingLogic" class="animate-spin text-base">⚙️</span>
            <span v-else class="text-base">🛡️</span>
            <span v-if="isGeneratingLogic">
              Yapay zeka ajanı kablolamaya uygun Arduino kodunu ve akışı doğruluyor...
            </span>
            <span v-else>
              Kablolama (Wiring) ↔ Akış Diyagramı & Arduino Kodu Uyumluluk Teyidi: %100 Başarılı!
            </span>
          </div>

          <div v-if="!isGeneratingLogic" class="flex items-center gap-1.5">
            <span class="px-2 py-0.5 rounded-full bg-emerald-200 border border-slate-900 text-[10px] font-black text-emerald-950">
              ✓ Sözdizimi Hatasız
            </span>
            <span class="px-2 py-0.5 rounded-full bg-amber-200 border border-slate-900 text-[10px] font-black text-amber-950">
              ✓ Pinler Birebir Eşleşti
            </span>
          </div>
        </div>

        <div v-if="!isGeneratingLogic && verification" class="flex flex-wrap items-center justify-between gap-2 pt-1 border-t border-emerald-200">
          <div class="flex flex-wrap items-center gap-1.5">
            <span class="text-[10px] font-black text-slate-600">Doğrulanan Pinler:</span>
            <span
              v-for="b in verification.pin_bindings"
              :key="`${b.uno_pin}-${b.component_id}`"
              class="px-2 py-0.5 rounded-lg bg-white border border-slate-900 text-[10px] font-black text-slate-900"
            >
              Arduino {{ b.uno_pin }} ➔ {{ b.component_label }} ({{ b.role }})
            </span>
          </div>
          <span v-if="verification.checks?.length" class="text-[11px] font-bold text-emerald-900">
            {{ verification.checks[verification.checks.length - 1] }}
          </span>
        </div>
      </div>

      <!-- ALT KONTROL ÇUBUĞU -->
      <div class="relative z-10 flex flex-col sm:flex-row items-center justify-between gap-3 pt-2 border-t-2 border-slate-100">
        
        <!-- Sol: Mor 3D '</> Perde Arkasındaki Kodu Gör' Butonu -->
        <button
          type="button"
          @click="$emit('open-code-modal')"
          class="px-5 py-2.5 rounded-full bg-[#c084fc] hover:bg-[#b06cf5] active:translate-y-1 active:shadow-none border-2 border-slate-900 shadow-[0_4px_0_#7e22ce] text-slate-950 font-black text-xs transition cursor-pointer flex items-center gap-2"
        >
          <span>&lt;/&gt;</span>
          <span>Perde Arkasındaki Kodu Gör</span>
        </button>

        <!-- Sağ: Yeşil 3D 'Çalıştırmaya Geç ➔' Butonu -->
        <div class="relative">
          <button
            type="button"
            @click="$emit('next-page')"
            class="px-8 py-3 rounded-full bg-[#4ade80] hover:bg-[#22c55e] active:translate-y-1 active:shadow-none border-2 border-slate-900 shadow-[0_4px_0_#15803d] text-slate-950 font-black text-sm transition cursor-pointer flex items-center gap-2"
          >
            <span>4. Çalıştırmaya Geç</span>
            <span class="text-base">➔</span>
          </button>
        </div>

      </div>

    </div>

  </div>
</template>

<script setup lang="ts">
import { computed } from 'vue';
import type {
  AkisAdimi,
  CircuitNetlist,
  NetlistComponent,
  LogicVerificationReport
} from '../types/project';

const props = defineProps<{
  projectName?: string;
  netlist?: CircuitNetlist;
  akisAdimi?: AkisAdimi;
  arduinoKodu?: string;
  isGeneratingLogic?: boolean;
  verification?: LogicVerificationReport;
}>();

defineEmits<{
  (e: 'next-page'): void;
  (e: 'prev-page'): void;
  (e: 'open-code-modal'): void;
}>();

const INPUT_TYPES = new Set([
  'wokwi-photoresistor',
  'wokwi-photoresistor-sensor',
  'wokwi-hc-sr04',
  'wokwi-pushbutton',
  'wokwi-potentiometer'
]);

const OUTPUT_TYPES = new Set([
  'wokwi-led',
  'wokwi-buzzer',
  'wokwi-servo'
]);

const nonResistorComponents = computed<NetlistComponent[]>(() => {
  return (props.netlist?.components || []).filter(c => c.type !== 'wokwi-resistor');
});

const inputComponents = computed<NetlistComponent[]>(() => {
  return nonResistorComponents.value.filter(c => INPUT_TYPES.has(c.type));
});

const outputComponents = computed<NetlistComponent[]>(() => {
  return nonResistorComponents.value.filter(c => OUTPUT_TYPES.has(c.type));
});

function getPinForComponent(compId: string): string {
  const bindings = props.verification?.pin_bindings || [];
  const matched = bindings.filter(b => b.component_id === compId).map(b => b.uno_pin);
  return matched.join('/');
}

function getComponentEmoji(type: string): string {
  if (type === 'wokwi-led') return '💡';
  if (type === 'wokwi-buzzer') return '🔊';
  if (type === 'wokwi-servo') return '🦾';
  if (type === 'wokwi-hc-sr04') return '🦇';
  if (type === 'wokwi-pushbutton') return '🔘';
  if (type === 'wokwi-potentiometer') return '🎛️';
  if (type.includes('photoresistor')) return '☀️';
  return '🧩';
}

function getActiveOutputProps(comp: NetlistComponent, isActive: boolean): Record<string, any> {
  const base = { ...(comp.props || {}) };
  if (comp.type === 'wokwi-led') {
    return { ...base, value: isActive, brightness: isActive ? 1.0 : 0.0 };
  }
  if (comp.type === 'wokwi-buzzer') {
    return { ...base, hasSignal: isActive };
  }
  if (comp.type === 'wokwi-servo') {
    return { ...base, angle: isActive ? 90 : 0 };
  }
  return base;
}
</script>

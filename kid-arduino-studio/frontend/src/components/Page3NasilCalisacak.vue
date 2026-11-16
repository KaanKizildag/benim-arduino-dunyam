<template>
  <div class="w-full max-w-5xl mx-auto flex-1 flex flex-col justify-between py-3 sm:py-5 px-3 sm:px-6 select-none">
    
    <!-- Ana Beyaz Kart (Referans Görsel 2 ile Birebir Aynı Tasarım) -->
    <div class="w-full flex-1 bg-white rounded-[32px] sm:rounded-[36px] border-[3px] border-slate-900 shadow-[0_8px_0_rgba(15,23,42,0.12)] p-5 sm:p-8 relative overflow-hidden flex flex-col justify-between">
      
      <!-- Faint Arka Plan Doodle Çizimleri -->
      <div class="absolute inset-0 pointer-events-none opacity-25 select-none overflow-hidden">
        <svg class="w-full h-full text-slate-400" viewBox="0 0 1000 600" fill="none">
          <path d="M 280 80 Q 290 60, 310 80 Q 290 100, 280 80" stroke="currentColor" stroke-width="2" />
          <circle cx="820" cy="120" r="14" stroke="currentColor" stroke-width="2" stroke-dasharray="3,3" />
          <path d="M 120 180 Q 130 160, 140 180" stroke="currentColor" stroke-width="2" />
          <circle cx="700" cy="460" r="18" stroke="currentColor" stroke-width="2" />
        </svg>
      </div>

      <!-- Ortadaki 3 Aşamalı Akış Şeması (Flowchart: 1. Gözlemle ➔ 2. Karar Ver ➔ Evet / Hayır) -->
      <div class="relative z-10 flex flex-col lg:flex-row items-center justify-center gap-3 sm:gap-6 my-auto py-4">
        
        <!-- ============================================== -->
        <!-- 1. KUTU: 1. GÖZLEMLE                           -->
        <!-- ============================================== -->
        <div class="w-full max-w-[210px] bg-white rounded-[26px] border-[3px] border-[#38bdf8] shadow-[0_5px_0_#0284c7] p-4 flex flex-col items-center text-center">
          <!-- Başlık (Mavi Göz İkonu + Yazı) -->
          <div class="flex items-center gap-2 mb-3">
            <div class="w-7 h-7 rounded-full bg-[#38bdf8] text-white flex items-center justify-center text-xs font-black shadow-xs">
              👁️
            </div>
            <h3 class="text-xs sm:text-sm font-black text-slate-900">
              1. Gözlemle
            </h3>
          </div>

          <!-- LDR Sensör İllüstrasyonu (Sarı Spot Işık Dairesi Üzerinde) -->
          <div class="relative w-22 h-22 rounded-full bg-[#fef08a] flex items-center justify-center border-2 border-[#facc15] shadow-inner mb-3">
            <!-- Çizgi Film LDR Sensörü -->
            <svg class="w-14 h-14" viewBox="0 0 100 100">
              <circle cx="50" cy="45" r="26" fill="#fde68a" stroke="#d97706" stroke-width="3" />
              <path d="M 36 38 Q 50 30, 64 38 Q 50 48, 36 48 Q 50 58, 64 58" fill="none" stroke="#b45309" stroke-width="3.5" stroke-linecap="round" />
              <line x1="42" y1="71" x2="42" y2="92" stroke="#64748b" stroke-width="4" stroke-linecap="round" />
              <line x1="58" y1="71" x2="58" y2="92" stroke="#64748b" stroke-width="4" stroke-linecap="round" />
            </svg>
          </div>

          <!-- Açıklama Metni -->
          <p class="text-xs font-black text-slate-900 leading-snug">
            {{ akisAdimi?.gozlemle || 'Odadaki ışığı her an takip et' }}
          </p>
        </div>

        <!-- BAĞLANTI OKU 1 ➔ 2 (Cyan/Yeşil Gradyanlı 3D Ok) -->
        <div class="hidden lg:flex items-center justify-center px-1">
          <svg class="w-16 h-10 drop-shadow-[0_2px_0_#0f172a]" viewBox="0 0 60 40">
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
        <!-- 2. KUTU: 2. KARAR VER                          -->
        <!-- ============================================== -->
        <div class="w-full max-w-[210px] bg-white rounded-[26px] border-[3px] border-slate-900 shadow-[0_5px_0_#0f172a] p-4 flex flex-col items-center text-center">
          <!-- Başlık (Mavi Robot İkonu + Yazı) -->
          <div class="flex items-center gap-2 mb-3">
            <div class="w-7 h-7 rounded-full bg-[#38bdf8] text-white flex items-center justify-center text-xs font-black shadow-xs">
              🤖
            </div>
            <h3 class="text-xs sm:text-sm font-black text-slate-900">
              2. Karar Ver
            </h3>
          </div>

          <!-- Pembe Çizgi Film Beyin İllüstrasyonu -->
          <div class="relative w-22 h-22 flex items-center justify-center mb-3">
            <span class="text-5xl drop-shadow-md">🧠</span>
          </div>

          <!-- Açıklama Metni -->
          <p class="text-xs font-black text-slate-900 leading-snug">
            {{ akisAdimi?.karar_ver || 'Hava karardı mı diye sor' }}
          </p>
        </div>

        <!-- ÇATAL BAĞLANTI (Referans Görseldeki İkiye Ayrılan Kıvrımlı Yol) -->
        <div class="hidden lg:flex items-center justify-center w-12 h-44">
          <svg class="w-full h-full" viewBox="0 0 50 140" fill="none">
            <!-- Yeşil Üst Dal -->
            <path d="M 5 70 C 25 70, 25 25, 45 25" stroke="#4ade80" stroke-width="4.5" stroke-linecap="round" />
            <!-- Kırmızı Alt Dal -->
            <path d="M 5 70 C 25 70, 25 115, 45 115" stroke="#f87171" stroke-width="4.5" stroke-linecap="round" />
          </svg>
        </div>

        <!-- ============================================== -->
        <!-- 3. SONUÇLAR: EVET / HAYIR DALLARI              -->
        <!-- ============================================== -->
        <div class="flex flex-col gap-4 w-full max-w-[270px]">
          
          <!-- ÜST KOL: EVET (Karanlık) ➔ Lambayı Yak! -->
          <div class="flex items-center gap-2.5">
            <!-- EVET Rozeti -->
            <div class="relative shrink-0">
              <div class="px-3 py-1.5 rounded-full bg-[#86efac] border-2 border-slate-900 shadow-[0_3px_0_#15803d] text-slate-950 font-black text-xs flex items-center gap-1">
                <span>EVET</span>
                <span class="text-[9px] font-bold opacity-80">(Karanlık)</span>
                <span>➔</span>
              </div>
            </div>

            <!-- Sonuç Kutusu 1 (Kırmızı Yanan LED) -->
            <div class="flex-1 bg-white rounded-2xl border-[3px] border-slate-900 shadow-[0_4px_0_#0f172a] p-3 flex flex-col items-center text-center">
              <div class="relative w-11 h-11 flex items-center justify-center mb-1">
                <div class="absolute inset-0 bg-rose-400 rounded-full blur-sm opacity-70 animate-pulse"></div>
                <svg class="w-9 h-9 relative z-10" viewBox="0 0 100 100">
                  <path d="M 35 60 C 35 25, 65 25, 65 60 Z" fill="#ef4444" stroke="#991b1b" stroke-width="3" />
                  <ellipse cx="50" cy="60" rx="15" ry="4" fill="#b91c1c" />
                  <line x1="42" y1="64" x2="42" y2="85" stroke="#94a3b8" stroke-width="4" />
                  <line x1="58" y1="64" x2="58" y2="85" stroke="#94a3b8" stroke-width="4" />
                </svg>
              </div>
              <strong class="text-xs font-black text-slate-900">
                {{ akisAdimi?.evet_sonucu || 'Lambayı Yak!' }}
              </strong>
            </div>
          </div>

          <!-- ALT KOL: HAYIR (Aydınlık) ➔ Lambayı Söndür! -->
          <div class="flex items-center gap-2.5">
            <!-- HAYIR Rozeti -->
            <div class="relative shrink-0">
              <div class="px-3 py-1.5 rounded-full bg-[#fca5a5] border-2 border-slate-900 shadow-[0_3px_0_#9f1239] text-slate-950 font-black text-xs flex items-center gap-1">
                <span>HAYIR</span>
                <span class="text-[9px] font-bold opacity-80">(Aydınlık)</span>
                <span>➔</span>
              </div>
            </div>

            <!-- Sonuç Kutusu 2 (Uyuyan Ay ve Sönük LED) -->
            <div class="flex-1 bg-white rounded-2xl border-[3px] border-slate-900 shadow-[0_4px_0_#0f172a] p-3 flex flex-col items-center text-center">
              <div class="flex items-center justify-center gap-1 w-11 h-11 mb-1">
                <span class="text-2xl">🌙</span>
                <svg class="w-7 h-7" viewBox="0 0 100 100">
                  <path d="M 35 60 C 35 25, 65 25, 65 60 Z" fill="#cbd5e1" stroke="#64748b" stroke-width="3" />
                  <ellipse cx="50" cy="60" rx="15" ry="4" fill="#94a3b8" />
                  <line x1="42" y1="64" x2="42" y2="85" stroke="#94a3b8" stroke-width="4" />
                  <line x1="58" y1="64" x2="58" y2="85" stroke="#94a3b8" stroke-width="4" />
                </svg>
              </div>
              <strong class="text-xs font-black text-slate-900">
                {{ akisAdimi?.hayir_sonucu || 'Lambayı Söndür!' }}
              </strong>
            </div>
          </div>

        </div>

      </div>

      <!-- ALT KONTROL ÇUBUĞU (Referans Görsel 2 ile Birebir Butonlar) -->
      <div class="relative z-10 flex flex-col sm:flex-row items-center justify-between gap-3 pt-3 border-t-2 border-slate-100">
        
        <!-- Sol: Mor 3D '</> Perde Arkasındaki Kodu Gör' Butonu -->
        <button
          type="button"
          @click="$emit('open-code-modal')"
          class="px-5 py-2.5 rounded-full bg-[#c084fc] hover:bg-[#b06cf5] active:translate-y-1 active:shadow-none border-2 border-slate-900 shadow-[0_4px_0_#7e22ce] text-slate-950 font-black text-xs transition cursor-pointer flex items-center gap-2"
        >
          <span>&lt;/&gt;</span>
          <span>Perde Arkasındaki Kodu Gör</span>
        </button>

        <!-- Sağ: Konfeti & Yıldız Süsleri İçinde Yeşil 3D 'Çalıştırmaya Geç ➔' Butonu -->
        <div class="relative">
          <span class="absolute -top-3.5 -left-3 text-rose-500 text-xs select-none">🎉</span>
          <span class="absolute -bottom-2 -left-2 text-amber-500 text-xs select-none">⭐</span>
          <span class="absolute -top-3.5 -right-2 text-sky-500 text-xs select-none">✨</span>
          <span class="absolute -bottom-2 -right-3 text-purple-500 text-xs select-none">🎊</span>

          <button
            type="button"
            @click="$emit('next-page')"
            class="px-8 py-3 rounded-full bg-[#4ade80] hover:bg-[#22c55e] active:translate-y-1 active:shadow-none border-2 border-slate-900 shadow-[0_4px_0_#15803d] text-slate-950 font-black text-sm transition cursor-pointer flex items-center gap-2"
          >
            <span>Çalıştırmaya Geç</span>
            <span class="text-base">➔</span>
          </button>
        </div>

      </div>

    </div>

  </div>
</template>

<script setup lang="ts">
import type { AkisAdimi } from '../types/project';

defineProps<{
  akisAdimi?: AkisAdimi;
  arduinoKodu?: string;
}>();

defineEmits<{
  (e: 'next-page'): void;
  (e: 'prev-page'): void;
  (e: 'open-code-modal'): void;
}>();
</script>
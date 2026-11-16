<template>
  <div class="max-w-6xl mx-auto w-full flex flex-col items-center py-4 px-2 sm:px-4">
    
    <!-- Ana Beyaz Kart (Referans Görsel 2 ile Birebir Aynı) -->
    <div class="w-full bg-white rounded-[36px] border-[3px] border-slate-900/10 shadow-[0_8px_0_rgba(15,23,42,0.06)] p-6 sm:p-10 relative overflow-hidden flex flex-col justify-between min-h-[580px]">
      
      <!-- Faint Doodle Arka Plan Süsleri -->
      <div class="absolute inset-0 pointer-events-none opacity-35 select-none overflow-hidden">
        <svg class="w-full h-full text-slate-300" viewBox="0 0 1000 600" fill="none">
          <!-- Minik doodle yıldızlar, ampuller, kalpler -->
          <path d="M 280 80 Q 290 60, 310 80 Q 290 100, 280 80" stroke="currentColor" stroke-width="2" />
          <circle cx="820" cy="120" r="14" stroke="currentColor" stroke-width="2" stroke-dasharray="3,3" />
          <path d="M 120 180 Q 130 160, 140 180" stroke="currentColor" stroke-width="2" />
          <circle cx="700" cy="460" r="18" stroke="currentColor" stroke-width="2" />
        </svg>
      </div>

      <!-- Ortadaki 3 Aşamalı Akış Şeması (Flowchart) -->
      <div class="relative z-10 flex flex-col lg:flex-row items-center justify-center gap-4 sm:gap-6 my-auto py-6">
        
        <!-- KUTU 1: 1. GÖZLEMLE -->
        <div class="w-full max-w-[220px] bg-white rounded-[28px] border-[3px] border-blue-500 shadow-[0_5px_0_#3b82f6] p-5 flex flex-col items-center text-center">
          <!-- Başlık (Göz İkonu + Yazı) -->
          <div class="flex items-center gap-2 mb-4">
            <div class="w-7 h-7 rounded-full bg-blue-500 text-white flex items-center justify-center text-sm shadow-xs">
              👁️
            </div>
            <h3 class="text-sm font-black text-slate-900">
              1. Gözlemle
            </h3>
          </div>

          <!-- LDR Sensör İllüstrasyonu (Sarı Spot Işık Dairesi Üzerinde) -->
          <div class="relative w-24 h-24 rounded-full bg-amber-100 flex items-center justify-center border-2 border-amber-300 shadow-inner mb-4">
            <!-- Gerçekçi Çizgi Film LDR Sensörü -->
            <svg class="w-16 h-16" viewBox="0 0 100 100">
              <!-- Sensör Başı (Krem disk + turuncu kıvrımlı direnç yolu) -->
              <circle cx="50" cy="45" r="26" fill="#fde68a" stroke="#d97706" stroke-width="3" />
              <path d="M 36 38 Q 50 30, 64 38 Q 50 48, 36 48 Q 50 58, 64 58" fill="none" stroke="#b45309" stroke-width="3.5" stroke-linecap="round" />
              <!-- Bacaklar -->
              <line x1="42" y1="71" x2="42" y2="92" stroke="#64748b" stroke-width="4" stroke-linecap="round" />
              <line x1="58" y1="71" x2="58" y2="92" stroke="#64748b" stroke-width="4" stroke-linecap="round" />
            </svg>
          </div>

          <!-- Açıklama Metni -->
          <p class="text-xs font-black text-slate-900 leading-snug">
            {{ akisAdimi?.gozlemle || 'Odadaki ışığı her an takip et' }}
          </p>
        </div>

        <!-- BAĞLANTI OKU 1 ➔ 2 (Cyan/Yeşil Gradyan Kalın Çizgi Film Oku) -->
        <div class="hidden lg:flex items-center justify-center px-1">
          <svg class="w-16 h-10 drop-shadow-[0_2px_0_#0f172a]" viewBox="0 0 60 40">
            <defs>
              <linearGradient id="arrowGrad" x1="0%" y1="0%" x2="100%" y2="0%">
                <stop offset="0%" stop-color="#38bdf8" />
                <stop offset="100%" stop-color="#4ade80" />
              </linearGradient>
            </defs>
            <path d="M 5 14 L 35 14 L 35 4 L 55 20 L 35 36 L 35 26 L 5 26 Z" fill="url(#arrowGrad)" stroke="#0f172a" stroke-width="2.5" />
          </svg>
        </div>

        <!-- KUTU 2: 2. KARAR VER -->
        <div class="w-full max-w-[220px] bg-white rounded-[28px] border-[3px] border-slate-900 shadow-[0_5px_0_#0f172a] p-5 flex flex-col items-center text-center">
          <!-- Başlık (Robot İkonu + Yazı) -->
          <div class="flex items-center gap-2 mb-4">
            <div class="w-7 h-7 rounded-full bg-blue-500 text-white flex items-center justify-center text-sm shadow-xs">
              🤖
            </div>
            <h3 class="text-sm font-black text-slate-900">
              2. Karar Ver
            </h3>
          </div>

          <!-- Pembe Çizgi Film Beyin İllüstrasyonu -->
          <div class="relative w-24 h-24 flex items-center justify-center mb-4">
            <span class="text-6xl drop-shadow-md">🧠</span>
          </div>

          <!-- Açıklama Metni -->
          <p class="text-xs font-black text-slate-900 leading-snug">
            {{ akisAdimi?.karar_ver || 'Hava karardı mı diye sor' }}
          </p>
        </div>

        <!-- İKİYE AYRILAN KARAR OKLARI & SONUÇ KUTULARI -->
        <div class="flex flex-col gap-4 w-full max-w-[280px]">
          
          <!-- ÜST KOL: EVET (Karanlık) ➔ Lambayı Yak! -->
          <div class="flex items-center gap-3">
            <!-- EVET Rozeti (Yeşil Ok Rozeti) -->
            <div class="relative shrink-0">
              <div class="px-3.5 py-1.5 rounded-full bg-[#86efac] border-2 border-slate-900 shadow-[0_3px_0_#15803d] text-slate-950 font-black text-xs flex items-center gap-1">
                <span>EVET</span>
                <span class="text-[10px] font-bold opacity-80">(Karanlık)</span>
                <span>➔</span>
              </div>
            </div>

            <!-- Sonuç Kutusu 1 (Kırmızı Yanan LED) -->
            <div class="flex-1 bg-white rounded-[24px] border-[3px] border-slate-900 shadow-[0_4px_0_#0f172a] p-3.5 flex flex-col items-center text-center">
              <!-- Parlayan Kırmızı LED İllüstrasyonu -->
              <div class="relative w-12 h-12 flex items-center justify-center mb-1">
                <!-- Kırmızı Hüzme Parıltısı -->
                <div class="absolute inset-0 bg-rose-400 rounded-full blur-md opacity-70 animate-pulse"></div>
                <svg class="w-10 h-10 relative z-10" viewBox="0 0 100 100">
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
          <div class="flex items-center gap-3">
            <!-- HAYIR Rozeti (Kırmızı/Mercan Ok Rozeti) -->
            <div class="relative shrink-0">
              <div class="px-3.5 py-1.5 rounded-full bg-[#fca5a5] border-2 border-slate-900 shadow-[0_3px_0_#9f1239] text-slate-950 font-black text-xs flex items-center gap-1">
                <span>HAYIR</span>
                <span class="text-[10px] font-bold opacity-80">(Aydınlık)</span>
                <span>➔</span>
              </div>
            </div>

            <!-- Sonuç Kutusu 2 (Uyuyan Ay ve Sönük LED) -->
            <div class="flex-1 bg-white rounded-[24px] border-[3px] border-slate-900 shadow-[0_4px_0_#0f172a] p-3.5 flex flex-col items-center text-center">
              <div class="flex items-center justify-center gap-1 w-12 h-12 mb-1">
                <span class="text-2xl">🌙</span>
                <!-- Sönük Gri LED -->
                <svg class="w-8 h-8" viewBox="0 0 100 100">
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

      <!-- ALT KONTROL ÇUBUĞU (Referans Görsel 2 ile Birebir Aynı Butonlar) -->
      <div class="relative z-10 flex flex-col sm:flex-row items-center justify-between gap-4 pt-4 border-t-2 border-slate-100">
        
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
          <!-- Uçuşan Çizgi Film Konfeti Süsleri -->
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

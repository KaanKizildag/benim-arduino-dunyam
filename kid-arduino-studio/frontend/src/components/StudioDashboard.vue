<template>
  <div class="w-full h-full grid grid-cols-1 lg:grid-cols-2 grid-rows-2 gap-2.5 sm:gap-3 p-2 sm:p-3 select-none overflow-hidden">
    
    <!-- ======================================================== -->
    <!-- PANEL 1 (SOL ÜST): YAPAY ZEKA İLE TASARLA!              -->
    <!-- ======================================================== -->
    <div class="bg-white rounded-2xl sm:rounded-3xl border-[3px] border-slate-900 shadow-[0_4px_0_#0f172a] flex flex-col overflow-hidden">
      <!-- Panel Başlığı -->
      <div class="px-3.5 py-2 sm:py-2.5 bg-[#fef08a] border-b-[2.5px] border-slate-900 flex items-center justify-between shrink-0">
        <div class="flex items-center gap-2">
          <span class="text-base sm:text-lg">🤖</span>
          <h2 class="text-xs sm:text-sm font-black text-slate-900">
            Yapay Zeka ile Tasarla!
          </h2>
        </div>

        <!-- Malzemelerimiz Rozeti -->
        <button
          type="button"
          @click="$emit('open-modal', 'inventory')"
          class="px-2.5 py-0.5 sm:py-1 rounded-xl bg-white hover:bg-slate-50 border-2 border-slate-900 shadow-[0_2px_0_#0f172a] active:translate-y-0.5 active:shadow-none text-slate-800 text-[10px] sm:text-xs font-black transition flex items-center gap-1 cursor-pointer"
        >
          <span>🎒</span>
          <span>Malzemelerimiz</span>
          <span class="w-4 h-4 rounded-full bg-emerald-500 text-white text-[9px] font-black flex items-center justify-center">
            {{ inventoryCount }}
          </span>
        </button>
      </div>

      <!-- Sohbet ve Mesajlaşma Alanı -->
      <div class="flex-1 p-3 overflow-y-auto flex flex-col gap-2.5 text-xs">
        <!-- 1. Çocuk Mesajı (Referans Görseldeki Boy Avatarı) -->
        <div class="flex items-start gap-2.5 max-w-[85%] self-start">
          <div class="w-8 h-8 rounded-full bg-amber-200 border-2 border-slate-900 flex items-center justify-center text-base shrink-0 shadow-xs overflow-hidden">
            👦
          </div>
          <div class="bg-[#f0f9ff] border-2 border-slate-900 rounded-2xl rounded-tl-none p-2.5 shadow-[0_2px_0_#0f172a] text-slate-900 font-bold leading-relaxed">
            Akıllı gece lambası yapmak istiyorum. Odam kararınca sarı yansın, aydınlanınca sönsün! 🌙
          </div>
        </div>

        <!-- 2. Robot Asistan Mesajı (Referans Görseldeki Robot) -->
        <div class="flex items-start gap-2.5 max-w-[88%] self-start">
          <div class="w-8 h-8 rounded-full bg-[#38bdf8] border-2 border-slate-900 flex items-center justify-center text-base shrink-0 shadow-xs">
            🤖
          </div>
          <div class="bg-[#fef9c3] border-2 border-slate-900 rounded-2xl rounded-tl-none p-2.5 shadow-[0_2px_0_#ca8a04] text-slate-900 font-bold leading-relaxed">
            Harika bir fikir! 🌟 Işık sensörü (LDR) ile odanın karanlığını takip edeceğiz. Hava kararınca LED lambayı otomatik yakacağız. Devre adımlarını sağ tarafta hazırladım! 👇
          </div>
        </div>

        <!-- Hızlı İlham Butonları -->
        <div class="flex flex-wrap items-center gap-1.5 pt-1">
          <span class="text-[10px] font-black text-slate-400 uppercase">Hızlı Fikirler:</span>
          <button
            type="button"
            v-for="chip in quickChips"
            :key="chip.name"
            @click="selectPrompt(chip.prompt)"
            class="px-2 py-0.5 rounded-lg bg-slate-100 hover:bg-amber-100 border border-slate-300 text-[10px] font-bold text-slate-700 cursor-pointer transition"
          >
            {{ chip.name }}
          </button>
        </div>
      </div>

      <!-- Giriş Kutusu -->
      <div class="p-2 sm:p-2.5 bg-slate-50 border-t-2 border-slate-900 flex items-center gap-2 shrink-0">
        <input
          v-model="userPrompt"
          type="text"
          placeholder="Hayalindeki projeyi yaz... (Örn: Hırsız yaklaşınca siren çalsın)"
          class="flex-1 px-3 py-1.5 sm:py-2 rounded-xl bg-white border-2 border-slate-900 text-xs font-bold text-slate-800 placeholder:text-slate-400 focus:outline-hidden focus:ring-2 focus:ring-sky-400"
          @keyup.enter="submitPrompt"
        />
        <button
          type="button"
          @click="submitPrompt"
          :disabled="isGenerating || !userPrompt.trim()"
          class="px-3.5 py-1.5 sm:py-2 rounded-xl bg-[#38bdf8] hover:bg-[#0284c7] disabled:opacity-50 border-2 border-slate-900 shadow-[0_2px_0_#0f172a] active:translate-y-0.5 active:shadow-none text-slate-950 font-black text-xs transition cursor-pointer flex items-center gap-1"
        >
          <span>{{ isGenerating ? '⏳' : '🚀' }}</span>
          <span class="hidden sm:inline">Tasarla!</span>
        </button>
      </div>
    </div>


    <!-- ======================================================== -->
    <!-- PANEL 2 (SAĞ ÜST): DEVRE KURULUMU (BREADBOARD + ARDUINO)-->
    <!-- ======================================================== -->
    <div class="bg-white rounded-2xl sm:rounded-3xl border-[3px] border-slate-900 shadow-[0_4px_0_#0f172a] flex flex-col overflow-hidden relative">
      <!-- Panel Başlığı ve Bölgeler (Sol, Orta, Sağ) -->
      <div class="px-3 py-2 bg-[#bae6fd] border-b-[2.5px] border-slate-900 flex items-center justify-between shrink-0">
        <div class="flex items-center gap-2">
          <span class="text-base sm:text-lg">⚡</span>
          <h2 class="text-xs sm:text-sm font-black text-slate-900">
            Devre Kurulumu
          </h2>
        </div>

        <!-- Referans Görseldeki Sol / Orta / Sağ Bölge Hapları -->
        <div class="flex items-center gap-1">
          <span
            :class="[
              'px-2 py-0.5 rounded-lg text-[10px] font-black border border-slate-900 cursor-pointer transition',
              activeZone === 'sol' ? 'bg-[#38bdf8] text-slate-950 shadow-xs' : 'bg-white/80 text-slate-700'
            ]"
            @click="activeZone = 'sol'"
          >
            Sol (LED)
          </span>
          <span
            :class="[
              'px-2 py-0.5 rounded-lg text-[10px] font-black border border-slate-900 cursor-pointer transition',
              activeZone === 'orta' ? 'bg-[#fde047] text-slate-950 shadow-xs' : 'bg-white/80 text-slate-700'
            ]"
            @click="activeZone = 'orta'"
          >
            Orta (Sensör)
          </span>
          <span
            :class="[
              'px-2 py-0.5 rounded-lg text-[10px] font-black border border-slate-900 cursor-pointer transition',
              activeZone === 'sag' ? 'bg-[#f87171] text-slate-950 shadow-xs' : 'bg-white/80 text-slate-700'
            ]"
            @click="activeZone = 'sag'"
          >
            Sağ (Buzzer)
          </span>
        </div>
      </div>

      <!-- Devre Alanı (SVG Breadboard + Arduino Uno + Buraya Tak Baloncuğu) -->
      <div class="flex-1 p-2 bg-gradient-to-b from-sky-50/50 to-slate-50 relative flex flex-col items-center justify-center overflow-hidden">
        
        <!-- Çizgi Film 'Buraya Tak' Çağrı Baloncuğu (Referans Görseldeki Gibi!) -->
        <div
          class="absolute z-20 pointer-events-none transition-all duration-300"
          :style="{ top: calloutPosition.top, left: calloutPosition.left }"
        >
          <div class="relative bg-[#fde047] text-slate-950 font-black text-[11px] px-2.5 py-1 rounded-xl border-2 border-slate-900 shadow-[0_3px_0_#0f172a] animate-bounce flex items-center gap-1">
            <span>👇</span>
            <span>Buraya Tak!</span>
          </div>
        </div>

        <!-- SVG Mini Devre Şeması -->
        <svg
          class="w-full h-full max-h-[170px] sm:max-h-[190px]"
          viewBox="0 0 500 240"
          preserveAspectRatio="xMidYMid meet"
        >
          <!-- 1. BREADBOARD GÖVDESİ -->
          <g id="breadboard-group">
            <rect x="20" y="15" width="460" height="110" rx="10" fill="#f8fafc" stroke="#0f172a" stroke-width="2.5" />
            
            <!-- Güç Rayları Çizgileri -->
            <line x1="30" y1="24" x2="470" y2="24" stroke="#ef4444" stroke-width="2" stroke-linecap="round" />
            <line x1="30" y1="31" x2="470" y2="31" stroke="#3b82f6" stroke-width="2" stroke-linecap="round" />
            
            <line x1="30" y1="108" x2="470" y2="108" stroke="#3b82f6" stroke-width="2" stroke-linecap="round" />
            <line x1="30" y1="115" x2="470" y2="115" stroke="#ef4444" stroke-width="2" stroke-linecap="round" />

            <!-- Bölge Arka Plan Vurguları (Sol: Mavi, Orta: Sarı, Sağ: Kırmızı) -->
            <rect x="35" y="38" width="125" height="62" rx="4" fill="#38bdf8" fill-opacity="0.18" stroke="#0284c7" stroke-width="1" stroke-dasharray="3,3" />
            <rect x="180" y="38" width="135" height="62" rx="4" fill="#fde047" fill-opacity="0.22" stroke="#eab308" stroke-width="1" stroke-dasharray="3,3" />
            <rect x="335" y="38" width="125" height="62" rx="4" fill="#f87171" fill-opacity="0.18" stroke="#ef4444" stroke-width="1" stroke-dasharray="3,3" />

            <!-- Orta Yalıtkan Oluk -->
            <rect x="30" y="66" width="440" height="6" rx="2" fill="#cbd5e1" stroke="#94a3b8" stroke-width="1" />

            <!-- Breadboard Delikleri Matrisi (Temsili 20 Sütun) -->
            <g id="holes" fill="#0f172a">
              <template v-for="col in 20" :key="col">
                <circle :cx="35 + (col - 1) * 22" cy="45" r="1.8" />
                <circle :cx="35 + (col - 1) * 22" cy="55" r="1.8" />
                <circle :cx="35 + (col - 1) * 22" cy="79" r="1.8" />
                <circle :cx="35 + (col - 1) * 22" cy="89" r="1.8" />
              </template>
            </g>

            <!-- Takılı Bileşenler (Örn: Sol bölgede Kırmızı LED, Orta bölgede LDR) -->
            <!-- LED -->
            <g transform="translate(68, 36)">
              <circle cx="0" cy="0" r="7" fill="#ef4444" stroke="#0f172a" stroke-width="1.5" />
              <circle cx="-2" cy="-2" r="2" fill="#ffffff" />
              <line x1="0" y1="7" x2="0" y2="19" stroke="#64748b" stroke-width="2" />
              <line x1="10" y1="7" x2="10" y2="19" stroke="#64748b" stroke-width="2" />
            </g>

            <!-- LDR Sensör (Orta Bölge) -->
            <g transform="translate(230, 42)">
              <circle cx="0" cy="0" r="7" fill="#fed7aa" stroke="#0f172a" stroke-width="1.5" />
              <path d="M -4 -2 Q 0 -5 4 -2 Q 0 1 -4 1 Q 0 4 4 4" fill="none" stroke="#9a3412" stroke-width="1" />
              <line x1="-3" y1="7" x2="-3" y2="15" stroke="#64748b" stroke-width="1.5" />
              <line x1="3" y1="7" x2="3" y2="15" stroke="#64748b" stroke-width="1.5" />
            </g>

            <!-- Aktif Parlayan Pin Deliği -->
            <circle
              cx="101"
              cy="89"
              r="6"
              fill="#fde047"
              stroke="#0f172a"
              stroke-width="2"
              class="animate-ping opacity-75"
            />
            <circle
              cx="101"
              cy="89"
              r="4"
              fill="#fbbf24"
              stroke="#0f172a"
              stroke-width="1.5"
            />
          </g>

          <!-- 2. ARDUINO UNO KARTI (AŞAĞIDA) -->
          <g id="arduino-group" transform="translate(130, 140)">
            <rect x="0" y="0" width="240" height="90" rx="8" fill="#0284c7" stroke="#0f172a" stroke-width="2.5" />
            <!-- USB Portu & Güç Jackı -->
            <rect x="-10" y="8" width="14" height="22" rx="2" fill="#94a3b8" stroke="#0f172a" stroke-width="1.5" />
            <rect x="-10" y="55" width="16" height="24" rx="2" fill="#1e293b" stroke="#0f172a" stroke-width="1.5" />
            <!-- Mikrodenetleyici Çip -->
            <rect x="75" y="32" width="75" height="24" rx="3" fill="#0f172a" stroke="#475569" stroke-width="1" />
            <text x="85" y="48" fill="#94a3b8" font-size="9" font-family="monospace" font-weight="900">ATmega328P</text>
            <!-- Pin Başlıkları -->
            <rect x="25" y="5" width="185" height="10" rx="2" fill="#0f172a" />
            <rect x="35" y="75" width="165" height="10" rx="2" fill="#0f172a" />
            <!-- Pin Yazıları -->
            <text x="145" y="13" fill="#38bdf8" font-size="7" font-weight="bold">D13</text>
            <text x="185" y="13" fill="#cbd5e1" font-size="7" font-weight="bold">GND</text>
            <text x="45" y="83" fill="#ef4444" font-size="7" font-weight="bold">5V</text>
            <text x="65" y="83" fill="#cbd5e1" font-size="7" font-weight="bold">GND</text>
            <!-- Logo -->
            <text x="30" y="48" fill="#ffffff" font-size="12" font-weight="900">ARDUINO</text>
          </g>

          <!-- 3. BAĞLANTI KABLOLARI (Kıvrımlı Bezier Eğrileri) -->
          <!-- D13 Kablosu (Kırmızı/Sarı Sinyal) -->
          <path
            d="M 275 145 C 275 120, 101 125, 101 89"
            fill="none"
            stroke="#ef4444"
            stroke-width="3"
            stroke-linecap="round"
            class="wire-flowing"
          />
          <!-- GND Kablosu (Mavi) -->
          <path
            d="M 315 145 C 330 115, 340 100, 370 108"
            fill="none"
            stroke="#3b82f6"
            stroke-width="3"
            stroke-linecap="round"
          />
        </svg>

        <!-- Alt Kılavuz Talimatı ve Adım Düğmeleri -->
        <div class="w-full flex items-center justify-between gap-2 pt-1 z-10">
          <div class="flex items-center gap-2">
            <span class="w-6 h-6 rounded-lg bg-indigo-600 text-white font-black text-xs flex items-center justify-center border border-slate-900 shadow-xs">
              {{ currentStepIndex + 1 }}
            </span>
            <span class="text-[11px] font-black text-slate-900 truncate max-w-[200px] sm:max-w-xs">
              {{ currentInstruction }}
            </span>
          </div>

          <div class="flex items-center gap-1 shrink-0">
            <button
              type="button"
              @click="prevStep"
              :disabled="currentStepIndex === 0"
              class="px-2 py-1 rounded-lg bg-white hover:bg-slate-50 disabled:opacity-40 border border-slate-900 text-slate-800 text-xs font-black cursor-pointer"
            >
              ◀
            </button>
            <button
              type="button"
              @click="nextStep"
              :disabled="currentStepIndex >= totalSteps - 1"
              class="px-2 py-1 rounded-lg bg-[#38bdf8] hover:bg-[#0284c7] disabled:opacity-40 border border-slate-900 text-slate-950 text-xs font-black cursor-pointer"
            >
              ▶
            </button>
          </div>
        </div>
      </div>
    </div>


    <!-- ======================================================== -->
    <!-- PANEL 3 (SOL ALT): GÖRSEL ALGORİTMA (SCRATCH / AKIŞ)    -->
    <!-- ======================================================== -->
    <div class="bg-white rounded-2xl sm:rounded-3xl border-[3px] border-slate-900 shadow-[0_4px_0_#0f172a] flex flex-col overflow-hidden">
      <!-- Panel Başlığı -->
      <div class="px-3.5 py-2 sm:py-2.5 bg-[#fed7aa] border-b-[2.5px] border-slate-900 flex items-center justify-between shrink-0">
        <div class="flex items-center gap-2">
          <span class="text-base sm:text-lg">🧩</span>
          <h2 class="text-xs sm:text-sm font-black text-slate-900">
            Görsel Algoritma
          </h2>
        </div>

        <!-- Görünüm Seçici: Bloklar vs Akış Şeması -->
        <div class="flex items-center bg-white/70 p-0.5 rounded-xl border border-slate-900 text-[10px] font-black">
          <button
            type="button"
            @click="algoViewMode = 'blocks'"
            :class="[
              'px-2 py-0.5 rounded-lg transition cursor-pointer',
              algoViewMode === 'blocks' ? 'bg-amber-400 text-slate-950 shadow-xs' : 'text-slate-700'
            ]"
          >
            🧩 Bloklar
          </button>
          <button
            type="button"
            @click="algoViewMode = 'flowchart'"
            :class="[
              'px-2 py-0.5 rounded-lg transition cursor-pointer',
              algoViewMode === 'flowchart' ? 'bg-amber-400 text-slate-950 shadow-xs' : 'text-slate-700'
            ]"
          >
            🔀 Akış Şeması
          </button>
        </div>
      </div>

      <!-- Algoritma İçeriği (Referans Görsel 1'deki Scratch Blokları veya Referans Görsel 2 Akış Şeması) -->
      <div class="flex-1 p-3 overflow-y-auto flex flex-col justify-center">
        
        <!-- MOD A: SCRATCH-BENZERİ GEÇMELİ BLOKLAR (Referans Görsel 1 Sol Alt) -->
        <div v-if="algoViewMode === 'blocks'" class="flex flex-col gap-1.5 max-w-sm mx-auto w-full">
          <!-- 1. BAŞLAT BLOĞU (Turuncu Başlık Bloğu) -->
          <div class="bg-[#f97316] text-white px-4 py-2 rounded-t-2xl rounded-br-2xl border-2 border-slate-900 shadow-[0_3px_0_#9a3412] font-black text-xs flex items-center gap-2 w-fit">
            <span>🚩</span>
            <span>BAŞLAT</span>
          </div>

          <!-- 2. EĞER BLOĞU (Sarı C-Bloğu) -->
          <div class="bg-[#f59e0b] border-2 border-slate-900 rounded-2xl rounded-tl-none p-2 sm:p-2.5 shadow-[0_3px_0_#b45309] flex flex-col gap-1.5">
            <div class="flex items-center gap-1.5 text-xs font-black text-slate-950">
              <span class="bg-amber-600 text-white px-2 py-0.5 rounded-md text-[10px]">EĞER</span>
              <span class="bg-[#0284c7] text-white px-2 py-0.5 rounded-full text-[10px] border border-slate-900">
                karanlık ise (Işık &lt; 400)
              </span>
            </div>

            <!-- EĞER İÇİ: LED'i Yak -->
            <div class="ml-4 pl-2 border-l-4 border-amber-600 flex flex-col gap-1 my-1">
              <div class="bg-[#0284c7] text-white px-3 py-1.5 rounded-xl border-2 border-slate-900 shadow-[0_2px_0_#0369a1] text-xs font-black flex items-center gap-1.5 w-fit">
                <span>💡</span>
                <span>LED'i yak</span>
              </div>
            </div>

            <!-- DEĞİLSE İÇİ: LED'i Söndür -->
            <div class="text-[10px] font-black text-slate-900 uppercase tracking-wider pl-1">
              DEĞİLSE (Aydınlık ise):
            </div>
            <div class="ml-4 pl-2 border-l-4 border-amber-600 flex flex-col gap-1">
              <div class="bg-[#64748b] text-white px-3 py-1.5 rounded-xl border-2 border-slate-900 shadow-[0_2px_0_#334155] text-xs font-black flex items-center gap-1.5 w-fit">
                <span>🌙</span>
                <span>LED'i söndür</span>
              </div>
            </div>
          </div>
        </div>

        <!-- MOD B: AKIŞ ŞEMASI (Referans Görsel 2: 1. Gözlemle -> 2. Karar Ver -> Evet/Hayır) -->
        <div v-else class="flex items-center justify-center gap-2 sm:gap-3 py-1">
          <!-- 1. Gözlemle -->
          <div class="bg-white rounded-xl border-2 border-sky-400 p-2 flex flex-col items-center text-center shadow-xs w-28">
            <span class="text-[10px] font-black text-sky-600">1. Gözlemle</span>
            <div class="w-8 h-8 rounded-full bg-amber-100 flex items-center justify-center text-sm my-1">
              👁️
            </div>
            <span class="text-[9px] font-bold text-slate-700 leading-tight">Odadaki ışığı izle</span>
          </div>

          <span class="text-base font-black text-slate-400">➔</span>

          <!-- 2. Karar Ver -->
          <div class="bg-white rounded-xl border-2 border-indigo-400 p-2 flex flex-col items-center text-center shadow-xs w-28">
            <span class="text-[10px] font-black text-indigo-600">2. Karar Ver</span>
            <div class="w-8 h-8 rounded-full bg-pink-100 flex items-center justify-center text-sm my-1">
              🧠
            </div>
            <span class="text-[9px] font-bold text-slate-700 leading-tight">Hava karardı mı?</span>
          </div>

          <span class="text-base font-black text-slate-400">➔</span>

          <!-- Çıktılar (Evet / Hayır) -->
          <div class="flex flex-col gap-1.5">
            <div class="bg-emerald-50 border border-emerald-500 rounded-lg p-1.5 flex items-center gap-1.5 text-[9px] font-black text-emerald-800">
              <span>✅</span>
              <span>Evet ➔ Lambayı Yak!</span>
            </div>
            <div class="bg-rose-50 border border-rose-500 rounded-lg p-1.5 flex items-center gap-1.5 text-[9px] font-black text-rose-800">
              <span>❌</span>
              <span>Hayır ➔ Lambayı Söndür!</span>
            </div>
          </div>
        </div>

      </div>

      <!-- Alt Bar: Perde Arkasındaki Kodu Gör Düğmesi -->
      <div class="px-3 py-1.5 bg-slate-50 border-t-2 border-slate-900 flex items-center justify-between shrink-0">
        <span class="text-[10px] font-bold text-slate-500">
          Otomatik C++ derleyicisi devrede
        </span>
        <button
          type="button"
          @click="$emit('open-code-modal')"
          class="px-2.5 py-1 rounded-xl bg-purple-600 hover:bg-purple-700 text-white font-black text-[10px] border-2 border-slate-900 shadow-[0_2px_0_#581c87] active:translate-y-0.5 active:shadow-none transition cursor-pointer flex items-center gap-1"
        >
          <span>&lt;/&gt;</span>
          <span>Perde Arkasındaki Kodu Gör</span>
        </button>
      </div>
    </div>


    <!-- ======================================================== -->
    <!-- PANEL 4 (SAĞ ALT): DEVREYİ KURDUM, ÇALIŞTIR!            -->
    <!-- ======================================================== -->
    <div class="bg-white rounded-2xl sm:rounded-3xl border-[3px] border-slate-900 shadow-[0_4px_0_#0f172a] flex flex-col overflow-hidden relative">
      <!-- Panel Başlığı ve Port -->
      <div class="px-3 py-2 bg-[#bbf7d0] border-b-[2.5px] border-slate-900 flex items-center justify-between shrink-0">
        <div class="flex items-center gap-2">
          <span class="text-base sm:text-lg">🎉</span>
          <h2 class="text-xs sm:text-sm font-black text-slate-900">
            Devreyi Kurdum, Çalıştır!
          </h2>
        </div>

        <!-- Port Rozeti -->
        <span class="px-2 py-0.5 rounded-full bg-white border border-slate-900 text-[10px] font-black text-slate-800 shadow-xs flex items-center gap-1">
          <span class="w-2 h-2 rounded-full bg-emerald-500 animate-pulse"></span>
          <span>COM3 (Arduino Uno)</span>
        </span>
      </div>

      <!-- Gövde: 3D Dev Yeşil Buton + İbre / İntetaktif Simülatör -->
      <div class="flex-1 p-3 flex flex-col items-center justify-between gap-2 overflow-y-auto bg-gradient-to-b from-emerald-50/40 to-white">
        
        <!-- Dev Yeşil 3D Çalıştır Butonu (Referans Görsel 1 Sağ Alt) -->
        <div class="w-full flex items-center justify-center pt-1">
          <button
            type="button"
            @click="triggerUpload"
            :disabled="isUploading"
            class="w-full max-w-xs py-3 px-4 rounded-full bg-[#4ade80] hover:bg-[#22c55e] border-[3px] border-slate-900 shadow-[0_5px_0_#15803d] active:translate-y-1 active:shadow-[0_1px_0_#15803d] text-slate-950 font-black text-sm sm:text-base transition cursor-pointer flex items-center justify-center gap-2 select-none group"
          >
            <span class="text-xl group-hover:scale-125 transition-transform">
              {{ isUploading ? '⏳' : '▶' }}
            </span>
            <span>{{ isUploading ? 'Karta Yükleniyor...' : 'Devreyi Kurdum, Çalıştır!' }}</span>
            <span class="text-lg">🎊</span>
          </button>
        </div>

        <!-- İnteraktif Sensör İbresi (Işık Seviyesi Gauge) -->
        <div class="flex flex-col items-center justify-center w-full">
          <!-- Yarım Daire İbre SVG -->
          <div class="relative w-44 sm:w-52 h-24 flex items-center justify-center">
            <svg class="w-full h-full" viewBox="0 0 200 110">
              <!-- İbre Yay Arka Planı (Kırmızı -> Sarı -> Yeşil) -->
              <defs>
                <linearGradient id="gaugeGradient" x1="0%" y1="0%" x2="100%" y2="0%">
                  <stop offset="0%" stop-color="#ef4444" />
                  <stop offset="35%" stop-color="#f59e0b" />
                  <stop offset="70%" stop-color="#84cc16" />
                  <stop offset="100%" stop-color="#10b981" />
                </linearGradient>
              </defs>

              <!-- Kalın Renkli Yay -->
              <path
                d="M 20 100 A 80 80 0 0 1 180 100"
                fill="none"
                stroke="url(#gaugeGradient)"
                stroke-width="16"
                stroke-linecap="round"
              />

              <!-- İbre İğnesi (Needle) -->
              <g :transform="`rotate(${needleAngle}, 100, 100)`" class="transition-transform duration-200">
                <line x1="100" y1="100" x2="100" y2="35" stroke="#0f172a" stroke-width="4.5" stroke-linecap="round" />
                <circle cx="100" cy="100" r="7" fill="#0f172a" />
                <circle cx="100" cy="100" r="3" fill="#ffffff" />
              </g>
            </svg>
          </div>

          <!-- İbre Etiketi -->
          <div class="flex items-center gap-2 -mt-2">
            <span class="text-xs font-black text-slate-800">Işık Seviyesi:</span>
            <span
              :class="[
                'px-2 py-0.5 rounded-md text-xs font-black border border-slate-900',
                sensorValue < 400 ? 'bg-amber-300 text-slate-950' : 'bg-emerald-300 text-slate-950'
              ]"
            >
              {{ sensorValue }} {{ sensorValue < 400 ? '(Karanlık 🌙)' : '(Aydınlık ☀️)' }}
            </span>
          </div>

          <!-- Simülasyon Test Kaydırıcısı (Çocuğun Odayı Karartıp Aydınlatması İçin!) -->
          <div class="w-full max-w-xs flex items-center gap-2 mt-1 px-2">
            <span class="text-xs">🌑</span>
            <input
              type="range"
              min="50"
              max="950"
              v-model.number="sensorValue"
              class="w-full h-2 bg-slate-200 rounded-lg appearance-none cursor-pointer accent-emerald-500"
            />
            <span class="text-xs">☀️</span>
          </div>
        </div>

        <!-- Canlı Tepki Rozeti: LED Yanıyor mu Söndü mü? -->
        <div class="w-full bg-slate-100 rounded-xl p-1.5 border border-slate-300 flex items-center justify-between text-[11px] font-black">
          <div class="flex items-center gap-1.5">
            <span :class="['w-3 h-3 rounded-full border border-slate-900', sensorValue < 400 ? 'bg-red-500 shadow-[0_0_8px_#ef4444]' : 'bg-slate-300']"></span>
            <span class="text-slate-800">
              LED Durumu: <strong>{{ sensorValue < 400 ? 'YANIYOR! 💡' : 'SÖNÜK 🌑' }}</strong>
            </span>
          </div>
          <span class="text-slate-500 text-[10px]">
            {{ sensorValue < 400 ? 'D13: HIGH' : 'D13: LOW' }}
          </span>
        </div>

      </div>
    </div>

  </div>
</template>

<script setup lang="ts">
import { ref, computed } from 'vue';
import confetti from 'canvas-confetti';
import type { ProjeTasarimi } from '../types/project';

const props = defineProps<{
  currentProject: ProjeTasarimi;
  inventoryCount: number;
  isGenerating: boolean;
  isUploading: boolean;
}>();

const emit = defineEmits<{
  (e: 'generate', prompt: string): void;
  (e: 'upload'): void;
  (e: 'open-code-modal'): void;
  (e: 'open-modal', tab: string): void;
}>();

// Panel 1: Prompt ve İlham
const userPrompt = ref('');
const quickChips = [
  { name: '🌙 Gece Lambası', prompt: 'Odam kararınca sarı gece lambam yansın, aydınlanınca sönsün.' },
  { name: '🦇 Park Sensörü', prompt: 'Biri 15 cm yaklaştığında buzzer hızlı ötsün ve kırmızı LED yansın.' },
  { name: '🚨 Hırsız Alarmı', prompt: 'Işık aniden kesilirse buzzer alarm çalsın!' },
];

function selectPrompt(p: string) {
  userPrompt.value = p;
  submitPrompt();
}

function submitPrompt() {
  if (!userPrompt.value.trim() || props.isGenerating) return;
  emit('generate', userPrompt.value);
}

// Panel 2: Devre Kurulumu & Bölgeler
const activeZone = ref<'sol' | 'orta' | 'sag'>('sol');
const currentStepIndex = ref(0);

const totalSteps = computed(() => props.currentProject.baglanti_adimlari?.length || 1);
const currentStep = computed(() => props.currentProject.baglanti_adimlari?.[currentStepIndex.value]);

const currentInstruction = computed(() => {
  return currentStep.value?.talimat || "Kırmızı LED'in uzun bacağını Arduino D13 pinine bağla.";
});

const calloutPosition = computed(() => {
  // Aktif adıma göre baloncuğun konumu
  if (currentStepIndex.value === 0) return { top: '35%', left: '16%' };
  if (currentStepIndex.value === 1) return { top: '48%', left: '22%' };
  if (currentStepIndex.value === 2) return { top: '38%', left: '46%' };
  return { top: '50%', left: '70%' };
});

function nextStep() {
  if (currentStepIndex.value < totalSteps.value - 1) {
    currentStepIndex.value++;
  }
}

function prevStep() {
  if (currentStepIndex.value > 0) {
    currentStepIndex.value--;
  }
}

// Panel 3: Algoritma
const algoViewMode = ref<'blocks' | 'flowchart'>('blocks');

// Panel 4: Çalıştır & İbre Simülasyonu
const sensorValue = ref(240); // Başlangıçta karanlık: 240

// İbre açısı: 0 (en sol / 50) ile 180 (en sağ / 950) derece arası
const needleAngle = computed(() => {
  // Açı: -90 ile +90 arası
  const ratio = Math.max(0, Math.min(1, (sensorValue.value - 50) / 900));
  return -90 + (ratio * 180);
});

function triggerUpload() {
  confetti({
    particleCount: 80,
    spread: 70,
    origin: { y: 0.7 }
  });
  emit('upload');
}
</script>
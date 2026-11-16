<template>
  <div class="flex flex-col gap-4">
    <!-- ==================================================== -->
    <!-- ÜST KONTROL BAR VE GÖRÜNÜM SEÇİCİ                    -->
    <!-- ==================================================== -->
    <div class="bg-white rounded-2xl p-4 sm:p-5 border border-slate-200 shadow-sm flex flex-col md:flex-row items-center justify-between gap-4">
      <!-- Sol: Görünüm Modu Seçici (Slide Selector) -->
      <div class="flex items-center gap-3">
        <div class="flex items-center bg-slate-100 p-1 rounded-xl text-xs font-extrabold border border-slate-200">
          <button
            type="button"
            @click="viewMode = 'breadboard'"
            :class="[
              'px-3.5 py-1.5 rounded-lg transition flex items-center gap-1.5',
              viewMode === 'breadboard'
                ? 'bg-white text-indigo-700 shadow-xs'
                : 'text-slate-600 hover:text-slate-900'
            ]"
          >
            <span>🍞</span>
            <span>Breadboard Modu</span>
          </button>

          <button
            type="button"
            @click="viewMode = 'direct'"
            :class="[
              'px-3.5 py-1.5 rounded-lg transition flex items-center gap-1.5',
              viewMode === 'direct'
                ? 'bg-white text-indigo-700 shadow-xs'
                : 'text-slate-600 hover:text-slate-900'
            ]"
          >
            <span>🎛️</span>
            <span>Doğrudan Bağlantı</span>
          </button>
        </div>

        <!-- Devredeki Parçalar Rozeti -->
        <span class="text-xs font-bold text-slate-500 hidden lg:inline">
          Devrede {{ activeComponentsList.length }} parça var
        </span>
      </div>

      <!-- Sağ: Tümü / Adım Adım Modu Toggle -->
      <div class="flex items-center gap-2">
        <button
          type="button"
          @click="showAllWires = !showAllWires"
          :class="[
            'px-3.5 py-1.5 rounded-xl text-xs font-bold border transition flex items-center gap-1.5',
            showAllWires
              ? 'bg-indigo-600 text-white border-indigo-600 shadow-xs'
              : 'bg-white text-slate-700 border-slate-300 hover:bg-slate-50'
          ]"
        >
          <span>{{ showAllWires ? '👁️ Tüm Kabloları Göster (Açık)' : '🔍 Adım Adım İncele' }}</span>
        </button>
      </div>
    </div>

    <!-- ==================================================== -->
    <!-- BREADBOARD FİZİK REHBERİ (KATILIK VE KISA DEVRE KURALI) -->
    <!-- ==================================================== -->
    <div
      v-if="viewMode === 'breadboard'"
      class="bg-indigo-50/70 border border-indigo-200/80 rounded-2xl p-3.5 sm:p-4 text-xs flex items-start gap-3 text-indigo-950"
    >
      <span class="text-xl shrink-0">⚡</span>
      <div class="flex-1 leading-relaxed">
        <strong class="font-extrabold text-indigo-900">Breadboard Dikey İletkenlik Kuralı:</strong>
        Aynı sütundaki <strong>A-B-C-D-E</strong> delikleri içeriden tek bir iletken hatla birbirine bağlıdır.
        Kısa devre yapmamak için parçaların bacakları farklı sütunlara takılır (Örn: LED Anot <strong>E5</strong>, Katot <strong>E6</strong>).
        Arduino'dan gelen sinyal kablosu ise parçanın bacağıyla <strong>aynı sütundaki boş deliğe (Örn: A5)</strong> takılır!
      </div>
    </div>

    <!-- ==================================================== -->
    <!-- ADIM TALİMAT KARTI VE ADIM SEÇİCİ                   -->
    <!-- ==================================================== -->
    <div class="bg-white rounded-2xl p-4 sm:p-5 border border-slate-200 shadow-sm flex flex-col gap-3">
      <!-- Tıklanabilir Adım Hapları Barı -->
      <div class="flex items-center justify-between gap-2 overflow-x-auto pb-1">
        <div class="flex items-center gap-1.5">
          <button
            v-for="(step, idx) in baglantiAdimlari"
            :key="idx"
            type="button"
            @click="goToStep(idx)"
            :class="[
              'px-3 py-1 rounded-lg text-xs font-extrabold transition flex items-center gap-1 shrink-0',
              currentStepIndex === idx
                ? 'bg-indigo-600 text-white shadow-xs'
                : idx < currentStepIndex
                ? 'bg-emerald-50 text-emerald-700 border border-emerald-200'
                : 'bg-slate-100 text-slate-600 hover:bg-slate-200'
            ]"
          >
            <span v-if="idx < currentStepIndex">✓</span>
            <span>Adım {{ idx + 1 }}</span>
          </button>
        </div>

        <!-- Önceki / Sonraki Butonları -->
        <div class="flex items-center gap-1.5 shrink-0">
          <button
            type="button"
            @click="prevStep"
            :disabled="currentStepIndex === 0"
            class="px-2.5 py-1 rounded-lg text-xs font-bold border border-slate-300 text-slate-700 hover:bg-slate-100 disabled:opacity-40"
          >
            ◀ Önceki
          </button>
          <button
            type="button"
            @click="nextStep"
            :disabled="currentStepIndex >= totalSteps - 1"
            class="px-2.5 py-1 rounded-lg text-xs font-bold bg-indigo-600 text-white hover:bg-indigo-700 disabled:opacity-40"
          >
            Sonraki ▶
          </button>
        </div>
      </div>

      <!-- Büyük Talimat Kartı -->
      <div v-if="currentStep" class="flex items-start gap-3 pt-2 border-t border-slate-100">
        <div
          class="w-8 h-8 rounded-lg flex items-center justify-center font-black text-sm text-white shrink-0 shadow-xs"
          :style="{ backgroundColor: currentStep.kablo_rengi }"
        >
          {{ currentStepNumber }}
        </div>
        <div class="flex-1">
          <div class="flex flex-wrap items-center gap-2 mb-1">
            <h4 class="font-extrabold text-slate-900 text-sm sm:text-base leading-snug">
              {{ currentStep.talimat }}
            </h4>
            <span
              class="px-2.5 py-0.5 rounded-full text-[11px] font-bold text-white shadow-xs"
              :style="{ backgroundColor: currentStep.kablo_rengi }"
            >
              {{ currentStep.kaynak.parca }} ({{ currentStep.kaynak.pin }}) ➔ {{ currentStep.hedef.parca }} ({{ currentStep.hedef.pin }})
            </span>
          </div>
          <p class="text-xs text-slate-500 font-medium">
            💡 <strong>İpucu:</strong> {{ currentStep.ipucu }}
          </p>
        </div>
      </div>
    </div>

    <!-- ==================================================== -->
    <!-- SVG DEVRE ÇALIŞMA ALANI                              -->
    <!-- ==================================================== -->
    <div class="relative w-full overflow-hidden bg-slate-900 rounded-2xl border border-slate-800 shadow-md flex items-center justify-center p-2">
      <svg
        viewBox="0 0 1000 680"
        class="w-full h-auto select-none max-h-[660px]"
        xmlns="http://www.w3.org/2000/svg"
      >
        <defs>
          <pattern id="workbenchGrid" width="25" height="25" patternUnits="userSpaceOnUse">
            <circle cx="2" cy="2" r="1" fill="#334155" opacity="0.3" />
          </pattern>
        </defs>

        <!-- Arka Plan Izgarası -->
        <rect width="1000" height="680" fill="#0f172a" />
        <rect width="1000" height="680" fill="url(#workbenchGrid)" />

        <!-- Çalışma Alanı Başlık Etiketi -->
        <text x="30" y="32" fill="#475569" font-size="11" font-weight="800" letter-spacing="1">
          KID ARDUINO STUDIO • {{ viewMode === 'breadboard' ? 'STANDART BREADBOARD GÖRÜNÜMÜ (30 SÜTUN)' : 'DOĞRUDAN BAĞLANTI GÖRÜNÜMÜ' }}
        </text>

        <!-- ============================================== -->
        <!-- 1. BREADBOARD (30 SÜTUN STANDART DENEY TAHTASI)-->
        <!-- ============================================== -->
        <g id="breadboard-container" v-if="viewMode === 'breadboard'">
          <!-- Breadboard Gövdesi (x=40, y=50, w=920, h=315) -->
          <rect x="40" y="50" width="920" height="315" rx="14" fill="#f8fafc" stroke="#cbd5e1" stroke-width="2.5" />
          
          <!-- Bölge (Zone) Arka Plan Şeritleri -->
          <!-- Bölge 1: Sütun 1-8 (Sol Bölge: LED & Direnç) -->
          <rect x="75" y="112" width="235" height="92" rx="6" fill="#e0f2fe" opacity="0.45" />
          <text x="192" y="106" fill="#0284c7" font-size="9" font-weight="900" text-anchor="middle">
            BÖLGE 1: LED & DİRENÇ (SÜTUN 1–8)
          </text>

          <!-- Bölge 2: Sütun 10-18 (Orta Bölge: Sensörler & Buton) -->
          <rect x="330" y="112" width="265" height="188" rx="6" fill="#f3e8ff" opacity="0.45" />
          <text x="462" y="106" fill="#9333ea" font-size="9" font-weight="900" text-anchor="middle">
            BÖLGE 2: SENSÖRLER & BUTON (SÜTUN 10–18)
          </text>

          <!-- Bölge 3: Sütun 20-28 (Sağ Bölge: Buzzer & Motor) -->
          <rect x="610" y="212" width="265" height="88" rx="6" fill="#fef3c7" opacity="0.45" />
          <text x="742" y="106" fill="#d97706" font-size="9" font-weight="900" text-anchor="middle">
            BÖLGE 3: BUZZER & MOTOR (SÜTUN 20–28)
          </text>

          <!-- Üst Güç Hatları (5V Kırmızı, GND Mavi) -->
          <line x1="80" y1="74" x2="910" y2="74" stroke="#ef4444" stroke-width="3" opacity="0.8" />
          <line x1="80" y1="92" x2="910" y2="92" stroke="#3b82f6" stroke-width="3" opacity="0.8" />
          <text x="58" y="77" fill="#ef4444" font-size="11" font-weight="900">+</text>
          <text x="58" y="95" fill="#3b82f6" font-size="12" font-weight="900">-</text>
          <text x="930" y="77" fill="#ef4444" font-size="11" font-weight="900">+</text>
          <text x="930" y="95" fill="#3b82f6" font-size="12" font-weight="900">-</text>

          <!-- Alt Güç Hatları (5V Kırmızı, GND Mavi) -->
          <line x1="80" y1="320" x2="910" y2="320" stroke="#ef4444" stroke-width="3" opacity="0.8" />
          <line x1="80" y1="338" x2="910" y2="338" stroke="#3b82f6" stroke-width="3" opacity="0.8" />
          <text x="58" y="323" fill="#ef4444" font-size="11" font-weight="900">+</text>
          <text x="58" y="341" fill="#3b82f6" font-size="12" font-weight="900">-</text>
          <text x="930" y="323" fill="#ef4444" font-size="11" font-weight="900">+</text>
          <text x="930" y="341" fill="#3b82f6" font-size="12" font-weight="900">-</text>

          <!-- Orta Yalıtkan Kanal (Trench) -->
          <rect x="55" y="206" width="890" height="8" rx="3" fill="#cbd5e1" />
          <text x="500" y="212" fill="#94a3b8" font-size="7" font-weight="900" text-anchor="middle" letter-spacing="8">
            B R E A D B O A R D   ( Y A L I T K A N   O R T A   O L U K )
          </text>

          <!-- Satır Harfleri (A B C D E | F G H I J) Sol ve Sağ Kenarlar -->
          <g font-size="9" font-weight="800" fill="#64748b" text-anchor="middle">
            <text x="68" y="123">A</text>
            <text x="68" y="141">B</text>
            <text x="68" y="159">C</text>
            <text x="68" y="177">D</text>
            <text x="68" y="195">E</text>

            <text x="68" y="223">F</text>
            <text x="68" y="241">G</text>
            <text x="68" y="259">H</text>
            <text x="68" y="277">I</text>
            <text x="68" y="295">J</text>

            <text x="932" y="123">A</text>
            <text x="932" y="141">B</text>
            <text x="932" y="159">C</text>
            <text x="932" y="177">D</text>
            <text x="932" y="195">E</text>

            <text x="932" y="223">F</text>
            <text x="932" y="241">G</text>
            <text x="932" y="259">H</text>
            <text x="932" y="277">I</text>
            <text x="932" y="295">J</text>
          </g>

          <!-- 30 Sütun Numaraları & Delikler -->
          <g>
            <template v-for="c in 30" :key="'bb-col-' + c">
              <!-- Sütun Numarası (Üst ve Alt) -->
              <text
                v-if="c === 1 || c % 5 === 0"
                :x="getColX(c)"
                y="114"
                font-size="8"
                font-weight="800"
                fill="#64748b"
                text-anchor="middle"
              >
                {{ c }}
              </text>
              <text
                v-if="c === 1 || c % 5 === 0"
                :x="getColX(c)"
                y="308"
                font-size="8"
                font-weight="800"
                fill="#64748b"
                text-anchor="middle"
              >
                {{ c }}
              </text>

              <!-- Üst Güç Delikleri (+, -) -->
              <circle :cx="getColX(c)" :cy="74" r="2.5" fill="#0f172a" stroke="#94a3b8" stroke-width="0.5" />
              <circle :cx="getColX(c)" :cy="92" r="2.5" fill="#0f172a" stroke="#94a3b8" stroke-width="0.5" />

              <!-- Üst Terminal Delikleri (A-E) -->
              <circle :cx="getColX(c)" :cy="120" r="2.5" fill="#0f172a" stroke="#94a3b8" stroke-width="0.5" />
              <circle :cx="getColX(c)" :cy="138" r="2.5" fill="#0f172a" stroke="#94a3b8" stroke-width="0.5" />
              <circle :cx="getColX(c)" :cy="156" r="2.5" fill="#0f172a" stroke="#94a3b8" stroke-width="0.5" />
              <circle :cx="getColX(c)" :cy="174" r="2.5" fill="#0f172a" stroke="#94a3b8" stroke-width="0.5" />
              <circle :cx="getColX(c)" :cy="192" r="2.5" fill="#0f172a" stroke="#94a3b8" stroke-width="0.5" />

              <!-- Alt Terminal Delikleri (F-J) -->
              <circle :cx="getColX(c)" :cy="220" r="2.5" fill="#0f172a" stroke="#94a3b8" stroke-width="0.5" />
              <circle :cx="getColX(c)" :cy="238" r="2.5" fill="#0f172a" stroke="#94a3b8" stroke-width="0.5" />
              <circle :cx="getColX(c)" :cy="256" r="2.5" fill="#0f172a" stroke="#94a3b8" stroke-width="0.5" />
              <circle :cx="getColX(c)" :cy="274" r="2.5" fill="#0f172a" stroke="#94a3b8" stroke-width="0.5" />
              <circle :cx="getColX(c)" :cy="292" r="2.5" fill="#0f172a" stroke="#94a3b8" stroke-width="0.5" />

              <!-- Alt Güç Delikleri (+, -) -->
              <circle :cx="getColX(c)" :cy="320" r="2.5" fill="#0f172a" stroke="#94a3b8" stroke-width="0.5" />
              <circle :cx="getColX(c)" :cy="338" r="2.5" fill="#0f172a" stroke="#94a3b8" stroke-width="0.5" />
            </template>
          </g>

          <!-- Aktif Dikey Sütun İletken Şerit Vurgusu (Net Parıltısı) -->
          <g id="active-net-highlight" v-if="activeNetHighlight">
            <rect
              :x="activeNetHighlight.x - 7"
              :y="activeNetHighlight.y1 - 4"
              width="14"
              :height="activeNetHighlight.y2 - activeNetHighlight.y1 + 8"
              rx="7"
              :fill="activeWire ? activeWire.step.kablo_rengi : '#6366f1'"
              opacity="0.35"
            />
            <line
              :x1="activeNetHighlight.x"
              :y1="activeNetHighlight.y1"
              :x2="activeNetHighlight.x"
              :y2="activeNetHighlight.y2"
              :stroke="activeWire ? activeWire.step.kablo_rengi : '#6366f1'"
              stroke-width="3"
              stroke-dasharray="3,2"
            />
          </g>

          <!-- ============================================== -->
          <!-- BREADBOARD ÜZERİNDEKİ GERÇEKÇİ BİLEŞENLER     -->
          <!-- ============================================== -->

          <!-- 1. Kırmızı LED (Anot: E5, Katot: E6) -->
          <g id="bb-comp-led" v-if="isComponentNeeded('LED_RED')">
            <!-- LED Başlığı (5. ve 6. sütunlar arasında durur) -->
            <path d="M 210 178 C 210 152, 228 152, 228 178 Z" fill="#ef4444" stroke="#b91c1c" stroke-width="2" />
            <ellipse cx="219" cy="178" rx="9" ry="3" fill="#991b1b" />
            <!-- Uzun Anot Bacağı -> E5 (205, 192) -->
            <path d="M 214 181 L 205 192" fill="none" stroke="#cbd5e1" stroke-width="2.5" />
            <circle cx="205" cy="192" r="4.5" fill="#ef4444" stroke="#ffffff" stroke-width="1.5" />
            <!-- Kısa Katot Bacağı -> E6 (233, 192) -->
            <path d="M 224 181 L 233 192" fill="none" stroke="#94a3b8" stroke-width="2.5" />
            <circle cx="233" cy="192" r="4.5" fill="#3b82f6" stroke="#ffffff" stroke-width="1.5" />
            <text x="219" y="150" fill="#f87171" font-size="8" font-weight="900" text-anchor="middle">LED</text>
          </g>

          <!-- 2. 220Ω Direnç (Bir ucu C6'da LED katot ile buluşur, diğer ucu Alt RAIL_GND hattına girer) -->
          <g id="bb-comp-resistor" v-if="isComponentNeeded('RESISTOR_220')">
            <!-- Üst bacak: C6 (233, 156) -->
            <line x1="233" y1="156" x2="233" y2="170" stroke="#cbd5e1" stroke-width="2.5" />
            <!-- Direnç Gövdesi -->
            <rect x="227" y="170" width="12" height="30" rx="4" fill="#d97706" stroke="#b45309" stroke-width="1" />
            <rect x="227" y="175" width="12" height="2.5" fill="#ef4444" />
            <rect x="227" y="180" width="12" height="2.5" fill="#ef4444" />
            <rect x="227" y="185" width="12" height="2.5" fill="#78350f" />
            <rect x="227" y="192" width="12" height="2" fill="#fbbf24" />
            <!-- Alt bacak -> Alt Ray GND (233, 338) -->
            <path d="M 233 200 L 233 338" fill="none" stroke="#cbd5e1" stroke-width="2.5" stroke-dasharray="4,2" />
            <!-- Pin Uçları -->
            <circle cx="233" cy="156" r="4.5" fill="#f59e0b" stroke="#ffffff" stroke-width="1.5" />
            <circle cx="233" cy="338" r="4.5" fill="#3b82f6" stroke="#ffffff" stroke-width="1.5" />
            <text x="248" y="188" fill="#d97706" font-size="8" font-weight="900">220Ω</text>
          </g>

          <!-- 3. LDR Işık Sensörü (E12 ve E14 deliklerine takılı) -->
          <g id="bb-comp-ldr" v-if="isComponentNeeded('LDR_SENSOR')">
            <circle cx="429" cy="165" r="14" fill="#f59e0b" stroke="#b45309" stroke-width="2" />
            <path d="M 421 160 Q 429 155, 437 160 Q 429 170, 421 170" fill="none" stroke="#78350f" stroke-width="1.5" />
            <!-- Bacak 1 -> E12 (401, 192) -->
            <line x1="423" y1="175" x2="401" y2="192" stroke="#cbd5e1" stroke-width="2.5" />
            <circle cx="401" cy="192" r="4.5" fill="#10b981" stroke="#ffffff" stroke-width="1.5" />
            <!-- Bacak 2 -> E14 (457, 192) -->
            <line x1="435" y1="175" x2="457" y2="192" stroke="#cbd5e1" stroke-width="2.5" />
            <circle cx="457" cy="192" r="4.5" fill="#ef4444" stroke="#ffffff" stroke-width="1.5" />
            <text x="429" y="145" fill="#059669" font-size="8" font-weight="900" text-anchor="middle">LDR Göz</text>
          </g>

          <!-- 4. HC-SR04 Mesafe Sensörü (Alt Yarı: F14, F15, F16, F17) -->
          <g id="bb-comp-hcsr04" v-if="isComponentNeeded('HCSR04')">
            <rect x="420" y="235" width="125" height="45" rx="5" fill="#0284c7" stroke="#0369a1" stroke-width="1.5" />
            <!-- İki Sonar Göz -->
            <circle cx="445" cy="257" r="14" fill="#94a3b8" stroke="#475569" stroke-width="1.5" />
            <circle cx="445" cy="257" r="9" fill="#cbd5e1" />
            <circle cx="515" cy="257" r="14" fill="#94a3b8" stroke="#475569" stroke-width="1.5" />
            <circle cx="515" cy="257" r="9" fill="#cbd5e1" />
            <!-- 4 Pin Bağlantı Uçları (F14: VCC, F15: TRIG, F16: ECHO, F17: GND) -->
            <circle :cx="getColX(14)" :cy="220" r="4" fill="#ef4444" stroke="#ffffff" stroke-width="1" />
            <circle :cx="getColX(15)" :cy="220" r="4" fill="#3b82f6" stroke="#ffffff" stroke-width="1" />
            <circle :cx="getColX(16)" :cy="220" r="4" fill="#10b981" stroke="#ffffff" stroke-width="1" />
            <circle :cx="getColX(17)" :cy="220" r="4" fill="#475569" stroke="#ffffff" stroke-width="1" />
            <text x="480" y="275" fill="#ffffff" font-size="8" font-weight="900" text-anchor="middle">HC-SR04</text>
          </g>

          <!-- 5. Buzzer Korna (Alt Yarı: F22 Artı, F24 Eksi) -->
          <g id="bb-comp-buzzer" v-if="isComponentNeeded('BUZZER')">
            <circle cx="709" cy="245" r="22" fill="#0f172a" stroke="#475569" stroke-width="2" />
            <circle cx="709" cy="245" r="7" fill="#1e293b" />
            <text x="695" y="238" fill="#f59e0b" font-size="10" font-weight="900">+</text>
            <!-- Bacak 1 -> F22 (681, 220) -->
            <line x1="697" y1="230" x2="681" y2="220" stroke="#cbd5e1" stroke-width="2.5" />
            <circle cx="681" cy="220" r="4.5" fill="#f59e0b" stroke="#ffffff" stroke-width="1.5" />
            <!-- Bacak 2 -> F24 (737, 220) -->
            <line x1="721" y1="230" x2="737" y2="220" stroke="#cbd5e1" stroke-width="2.5" />
            <circle cx="737" cy="220" r="4.5" fill="#3b82f6" stroke="#ffffff" stroke-width="1.5" />
            <text x="709" y="280" fill="#f59e0b" font-size="8" font-weight="900" text-anchor="middle">Buzzer</text>
          </g>
        </g>

        <!-- ============================================== -->
        <!-- 2. DOĞRUDAN BAĞLANTI MODU KARTLARI (MOD 2)    -->
        <!-- ============================================== -->
        <g id="direct-cards-container" v-if="viewMode === 'direct'">
          <!-- LED Kartı -->
          <g v-if="isComponentNeeded('LED_RED')">
            <rect x="75" y="70" width="115" height="135" rx="10" fill="#1e293b" stroke="#334155" />
            <text x="132" y="90" fill="#f87171" font-size="11" font-weight="800" text-anchor="middle">Kırmızı LED</text>
            <path d="M 115 145 C 115 110, 155 110, 155 145 Z" fill="#ef4444" stroke="#dc2626" stroke-width="2" />
            <circle cx="120" cy="180" r="5" fill="#ef4444" stroke="#ffffff" stroke-width="1.5" />
            <circle cx="155" cy="180" r="5" fill="#3b82f6" stroke="#ffffff" stroke-width="1.5" />
            <text x="105" y="195" fill="#ef4444" font-size="8" font-weight="800">UZUN (+)</text>
            <text x="170" y="195" fill="#93c5fd" font-size="8" font-weight="800">KISA (-)</text>
          </g>

          <!-- 220Ω Direnç Kartı -->
          <g v-if="isComponentNeeded('RESISTOR_220')">
            <rect x="220" y="70" width="140" height="135" rx="10" fill="#1e293b" stroke="#334155" />
            <text x="290" y="90" fill="#fde047" font-size="11" font-weight="800" text-anchor="middle">220Ω Direnç</text>
            <rect x="250" y="125" width="50" height="20" rx="6" fill="#d97706" />
            <circle cx="240" cy="135" r="5" fill="#f59e0b" stroke="#ffffff" stroke-width="1.5" />
            <circle cx="340" cy="135" r="5" fill="#f59e0b" stroke="#ffffff" stroke-width="1.5" />
            <text x="240" y="155" fill="#fde047" font-size="8" font-weight="700" text-anchor="middle">Uç 1</text>
            <text x="340" y="155" fill="#fde047" font-size="8" font-weight="700" text-anchor="middle">Uç 2</text>
          </g>

          <!-- LDR Kartı -->
          <g v-if="isComponentNeeded('LDR_SENSOR')">
            <rect x="390" y="70" width="120" height="135" rx="10" fill="#1e293b" stroke="#334155" />
            <text x="450" y="90" fill="#34d399" font-size="11" font-weight="800" text-anchor="middle">Işık Sensörü</text>
            <circle cx="450" cy="130" r="18" fill="#f59e0b" stroke="#b45309" stroke-width="2" />
            <circle cx="430" cy="180" r="5" fill="#10b981" stroke="#ffffff" stroke-width="1.5" />
            <circle cx="480" cy="180" r="5" fill="#10b981" stroke="#ffffff" stroke-width="1.5" />
            <text x="430" y="195" fill="#6ee7b7" font-size="8" font-weight="800" text-anchor="middle">5V</text>
            <text x="480" y="195" fill="#6ee7b7" font-size="8" font-weight="800" text-anchor="middle">A0</text>
          </g>

          <!-- HC-SR04 Kartı -->
          <g v-if="isComponentNeeded('HCSR04')">
            <rect x="540" y="70" width="180" height="135" rx="10" fill="#1e293b" stroke="#334155" />
            <text x="630" y="90" fill="#38bdf8" font-size="11" font-weight="800" text-anchor="middle">Mesafe Sensörü</text>
            <circle cx="590" cy="130" r="16" fill="#94a3b8" />
            <circle cx="670" cy="130" r="16" fill="#94a3b8" />
            <circle cx="580" cy="180" r="5" fill="#ef4444" stroke="#ffffff" stroke-width="1.5" />
            <circle cx="610" cy="180" r="5" fill="#3b82f6" stroke="#ffffff" stroke-width="1.5" />
            <circle cx="640" cy="180" r="5" fill="#10b981" stroke="#ffffff" stroke-width="1.5" />
            <circle cx="670" cy="180" r="5" fill="#475569" stroke="#ffffff" stroke-width="1.5" />
          </g>

          <!-- Buzzer Kartı -->
          <g v-if="isComponentNeeded('BUZZER')">
            <rect x="750" y="70" width="130" height="135" rx="10" fill="#1e293b" stroke="#334155" />
            <text x="815" y="90" fill="#c084fc" font-size="11" font-weight="800" text-anchor="middle">Buzzer (Korna)</text>
            <circle cx="815" cy="130" r="22" fill="#0f172a" stroke="#475569" stroke-width="2" />
            <circle cx="785" cy="180" r="5" fill="#a855f7" stroke="#ffffff" stroke-width="1.5" />
            <circle cx="835" cy="180" r="5" fill="#64748b" stroke="#ffffff" stroke-width="1.5" />
          </g>
        </g>

        <!-- ============================================== -->
        <!-- 3. ARDUINO UNO R3 (BREADBOARD ALTINDA SABİT)   -->
        <!-- ============================================== -->
        <g id="arduino-uno">
          <!-- PCB Gövde (x=280, y=390, w=440, h=270) -->
          <rect x="280" y="390" width="440" height="270" rx="14" fill="#0284c7" stroke="#0369a1" stroke-width="2.5" />

          <!-- USB Portu (Sol) -->
          <rect x="250" y="415" width="45" height="50" rx="3" fill="#94a3b8" stroke="#475569" stroke-width="1.5" />
          <text x="253" y="480" fill="#cbd5e1" font-size="8" font-weight="700">USB</text>

          <!-- Güç Jakı (Sol Alt) -->
          <rect x="255" y="570" width="45" height="55" rx="4" fill="#1e293b" stroke="#0f172a" stroke-width="2" />
          <circle cx="277" cy="597" r="7" fill="#475569" />

          <!-- Reset Butonu -->
          <circle cx="315" cy="415" r="5.5" fill="#ef4444" stroke="#b91c1c" stroke-width="1.5" />
          <text x="315" y="432" fill="#e0f2fe" font-size="7" font-weight="800" text-anchor="middle">RESET</text>

          <!-- ATmega328P Çip -->
          <rect x="420" y="500" width="160" height="40" rx="4" fill="#1e293b" stroke="#334155" stroke-width="2" />
          <circle cx="430" cy="520" r="3" fill="#475569" />
          <text x="460" y="525" fill="#94a3b8" font-size="11" font-weight="800" font-family="monospace">ATmega328P</text>

          <!-- Kart Yazıları -->
          <text x="325" y="530" fill="#ffffff" font-size="18" font-weight="900">Arduino</text>
          <text x="395" y="530" fill="#38bdf8" font-size="14" font-weight="800">UNO R3</text>

          <!-- Üst Header (Dijital Pinler - Breadboard'a Doğrudan Bakan Pinler) -->
          <rect x="385" y="395" width="295" height="20" rx="3" fill="#0f172a" stroke="#1e293b" stroke-width="1.5" />
          <g v-for="(pin, key) in upperArduinoPins" :key="'upper-pin-' + key">
            <rect :x="pin.x - 5" :y="pin.y - 5" width="10" height="10" rx="2" fill="#1e293b" stroke="#475569" />
            <circle :cx="pin.x" :cy="pin.y" r="2.5" fill="#f8fafc" />
            <text :x="pin.x" :y="pin.y + 16" fill="#bae6fd" font-size="7.5" font-weight="800" text-anchor="middle">
              {{ pin.label }}
            </text>
          </g>

          <!-- Alt Header (Güç ve Analog Pinler) -->
          <rect x="395" y="628" width="250" height="20" rx="3" fill="#0f172a" stroke="#1e293b" stroke-width="1.5" />
          <g v-for="(pin, key) in lowerArduinoPins" :key="'lower-pin-' + key">
            <rect :x="pin.x - 5" :y="pin.y - 5" width="10" height="10" rx="2" fill="#1e293b" stroke="#475569" />
            <circle :cx="pin.x" :cy="pin.y" r="2.5" fill="#f8fafc" />
            <text :x="pin.x" :y="pin.y - 8" fill="#bae6fd" font-size="7.5" font-weight="800" text-anchor="middle">
              {{ pin.label }}
            </text>
          </g>

          <text x="440" y="660" fill="#facc15" font-size="8" font-weight="800">GÜÇ (POWER)</text>
          <text x="590" y="660" fill="#38bdf8" font-size="8" font-weight="800">ANALOG GİRİŞ (A0..A5)</text>
        </g>

        <!-- ============================================== -->
        <!-- 4. KABLOLAR (PİNLERLE %100 BİREBİR KESİŞİR)     -->
        <!-- ============================================== -->

        <!-- A. Önceki Kablolar (Arka Planda Yarı Saydam veya Tümü Açıkken) -->
        <g id="bg-wires">
          <g v-for="(wire, idx) in backgroundWires" :key="'bg-wire-' + idx">
            <path
              :d="wire.pathD"
              fill="none"
              :stroke="wire.step.kablo_rengi"
              :stroke-width="showAllWires ? 4 : 3"
              stroke-linecap="round"
              :opacity="showAllWires ? 0.85 : 0.25"
            />
            <circle :cx="wire.p1.x" :cy="wire.p1.y" :r="showAllWires ? 4.5 : 3" :fill="wire.step.kablo_rengi" stroke="#ffffff" stroke-width="1" />
            <circle :cx="wire.p2.x" :cy="wire.p2.y" :r="showAllWires ? 4.5 : 3" :fill="wire.step.kablo_rengi" stroke="#ffffff" stroke-width="1" />
          </g>
        </g>

        <!-- B. Aktif Kablo (Akan Akım Animasyonu + Hedef Radar Efektleri) -->
        <g id="active-wire" v-if="activeWire">
          <!-- Parlayan Dış Çizgi -->
          <path
            :d="activeWire.pathD"
            fill="none"
            :stroke="activeWire.step.kablo_rengi"
            stroke-width="8"
            stroke-linecap="round"
            opacity="0.3"
          />

          <!-- Ana Akım Akan Kablo -->
          <path
            :d="activeWire.pathD"
            fill="none"
            :stroke="activeWire.step.kablo_rengi"
            stroke-width="4.5"
            stroke-linecap="round"
            class="wire-flowing"
          />

          <!-- Kaynak Pin Radar Efekti (Pinin tam merkezinde) -->
          <circle :cx="activeWire.p1.x" :cy="activeWire.p1.y" r="14" fill="none" :stroke="activeWire.step.kablo_rengi" stroke-width="2" class="animate-ping" opacity="0.8" />
          <circle :cx="activeWire.p1.x" :cy="activeWire.p1.y" r="5.5" :fill="activeWire.step.kablo_rengi" stroke="#ffffff" stroke-width="2" />

          <!-- Hedef Pin Radar Efekti (Pinin tam merkezinde) -->
          <circle :cx="activeWire.p2.x" :cy="activeWire.p2.y" r="14" fill="none" :stroke="activeWire.step.kablo_rengi" stroke-width="2" class="animate-ping" opacity="0.8" />
          <circle :cx="activeWire.p2.x" :cy="activeWire.p2.y" r="5.5" :fill="activeWire.step.kablo_rengi" stroke="#ffffff" stroke-width="2" />
        </g>
      </svg>
    </div>
  </div>
</template>

<script setup lang="ts">
import { ref, computed, watch } from 'vue';
import type { BaglantiAdimi } from '../types/project';
import {
  BREADBOARD_GRID,
  ARDUINO_UNO_PINS,
  getPinCoordinates
} from '../constants/pinCoordinates';

const props = defineProps<{
  baglantiAdimlari: BaglantiAdimi[];
  gerekliParcalar: string[];
}>();

const viewMode = ref<'breadboard' | 'direct'>('breadboard');
const currentStepIndex = ref(0);
const showAllWires = ref(false);

watch(() => props.baglantiAdimlari, () => {
  currentStepIndex.value = 0;
}, { deep: true });

const totalSteps = computed(() => props.baglantiAdimlari.length);
const currentStepNumber = computed(() => (totalSteps.value > 0 ? currentStepIndex.value + 1 : 0));
const currentStep = computed(() => props.baglantiAdimlari[currentStepIndex.value] || null);

function getColX(col: number): number {
  return BREADBOARD_GRID.getColX(col);
}

// Devrede kullanılan parçaların listesi
const activeComponentsList = computed(() => {
  const set = new Set<string>();
  if (props.gerekliParcalar) {
    props.gerekliParcalar.forEach(p => set.add(p.toUpperCase().trim()));
  }
  if (props.baglantiAdimlari) {
    props.baglantiAdimlari.forEach(step => {
      set.add(step.kaynak.parca.toUpperCase().trim());
      set.add(step.hedef.parca.toUpperCase().trim());
    });
  }
  return Array.from(set).filter(p => p !== 'ARDUINO_UNO' && p !== 'BREADBOARD');
});

function isComponentNeeded(compId: string): boolean {
  return activeComponentsList.value.includes(compId.toUpperCase().trim());
}

// Arduino Header Pinleri
const upperArduinoPins = computed(() => {
  const upperKeys = ['AREF', 'GND_TOP', 'D13', 'D12', 'D11', 'D10', 'D9', 'D8', 'D7', 'D6', 'D5', 'D4', 'D3', 'D2', 'D1', 'D0'];
  const res: Record<string, { x: number; y: number; label: string }> = {};
  upperKeys.forEach(k => {
    if (ARDUINO_UNO_PINS[k]) res[k] = ARDUINO_UNO_PINS[k];
  });
  return res;
});

const lowerArduinoPins = computed(() => {
  const lowerKeys = ['IOREF', 'RESET', '3.3V', '5V', 'GND', 'VIN', 'A0', 'A1', 'A2', 'A3', 'A4', 'A5'];
  const res: Record<string, { x: number; y: number; label: string }> = {};
  lowerKeys.forEach(k => {
    if (ARDUINO_UNO_PINS[k]) res[k] = ARDUINO_UNO_PINS[k];
  });
  return res;
});

// Breadboard Aktif Dikey Sütun Net Vurgusu (BB_TOP_col veya BB_BOTTOM_col)
const activeNetHighlight = computed(() => {
  if (viewMode.value !== 'breadboard' || !currentStep.value) return null;
  const p1 = getPinCoordinates(currentStep.value.kaynak.parca, currentStep.value.kaynak.pin, 'breadboard');
  const p2 = getPinCoordinates(currentStep.value.hedef.parca, currentStep.value.hedef.pin, 'breadboard');

  const target = (p2 && p2.col) ? p2 : (p1 && p1.col ? p1 : null);
  if (!target || !target.col) return null;

  const colX = getColX(target.col);
  const isTop = target.row && 'ABCDE'.includes(target.row);
  const isBottom = target.row && 'FGHIJ'.includes(target.row);

  if (isTop) {
    return { x: colX, y1: 120, y2: 192 };
  } else if (isBottom) {
    return { x: colX, y1: 220, y2: 292 };
  }
  return null;
});

/**
 * Pürüzsüz Bezier eğrisi hesaplar. Kablonun pin merkezine tam oturmasını sağlar.
 */
function createBezierPath(p1: { x: number; y: number }, p2: { x: number; y: number }): string {
  const dx = p2.x - p1.x;
  const dy = p2.y - p1.y;
  const dist = Math.sqrt(dx * dx + dy * dy);

  // Kısa jumperlar için yumuşak yay
  if (dist < 40) {
    const arch = 16;
    return `M ${p1.x} ${p1.y} C ${p1.x} ${p1.y - arch}, ${p2.x} ${p2.y - arch}, ${p2.x} ${p2.y}`;
  }

  // Doğal kavis eğrisi
  const sag = Math.min(Math.max(dist * 0.22, 35), 90);
  const cy1 = p1.y < p2.y ? p1.y - sag * 0.5 : p1.y - sag * 0.7;
  const cy2 = p2.y > 350 ? p2.y + sag * 0.5 : p2.y - sag * 0.7;
  const cx1 = p1.x + dx * 0.35;
  const cx2 = p1.x + dx * 0.65;

  return `M ${p1.x} ${p1.y} C ${cx1} ${cy1}, ${cx2} ${cy2}, ${p2.x} ${p2.y}`;
}

// Aktif Adımın Kablosu
const activeWire = computed(() => {
  if (!currentStep.value) return null;
  const p1 = getPinCoordinates(currentStep.value.kaynak.parca, currentStep.value.kaynak.pin, viewMode.value);
  const p2 = getPinCoordinates(currentStep.value.hedef.parca, currentStep.value.hedef.pin, viewMode.value);
  if (!p1 || !p2) return null;
  return {
    step: currentStep.value,
    p1,
    p2,
    pathD: createBezierPath(p1, p2)
  };
});

// Arka plandaki kablolar (Tümünü Göster açıkken veya önceki adımlar)
const backgroundWires = computed(() => {
  const wires = [];
  const limit = showAllWires.value ? props.baglantiAdimlari.length : currentStepIndex.value;
  for (let i = 0; i < limit; i++) {
    const step = props.baglantiAdimlari[i];
    if (!step) continue;
    if (!showAllWires.value && i === currentStepIndex.value) continue;
    
    const p1 = getPinCoordinates(step.kaynak.parca, step.kaynak.pin, viewMode.value);
    const p2 = getPinCoordinates(step.hedef.parca, step.hedef.pin, viewMode.value);
    if (p1 && p2) {
      wires.push({ step, p1, p2, pathD: createBezierPath(p1, p2) });
    }
  }
  return wires;
});

function goToStep(index: number) {
  if (index >= 0 && index < totalSteps.value) {
    currentStepIndex.value = index;
  }
}

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
</script>

<style scoped>
@keyframes flowDash {
  to {
    stroke-dashoffset: -32;
  }
}

.wire-flowing {
  stroke-dasharray: 8, 8;
  animation: flowDash 1.2s linear infinite;
}
</style>

<template>
  <div class="max-w-6xl mx-auto w-full flex flex-col gap-4 py-3 px-2 sm:px-4">
    
    <!-- Üst Büyük Talimat Bandı -->
    <div class="bg-white rounded-3xl p-4 sm:p-5 border-2 border-slate-200 shadow-sm flex flex-col sm:flex-row items-center justify-between gap-4">
      <div class="flex items-start sm:items-center gap-3.5 flex-1">
        <!-- Adım Sayacı -->
        <div
          class="w-12 h-12 rounded-2xl flex items-center justify-center font-black text-lg text-white shrink-0 shadow-md"
          :style="{ backgroundColor: currentStep ? currentStep.kablo_rengi : '#6366f1' }"
        >
          {{ currentStepNumber }}/{{ totalSteps }}
        </div>
        <div>
          <span class="text-[11px] font-black uppercase tracking-wider text-slate-400 block mb-0.5">
            Devre Kurulum Kılavuzu (Adım {{ currentStepNumber }})
          </span>
          <h3 class="text-sm sm:text-base font-black text-slate-900 leading-snug">
            {{ currentStep?.talimat || 'Bağlantı talimatı yükleniyor...' }}
          </h3>
          <p class="text-xs text-slate-500 font-bold mt-0.5">
            💡 <strong>İpucu:</strong> {{ currentStep?.ipucu }}
          </p>
        </div>
      </div>

      <!-- Sağ: Tümü / Adım Adım Modu -->
      <div class="flex items-center gap-2 shrink-0">
        <button
          type="button"
          @click="showAllWires = !showAllWires"
          :class="[
            'px-3.5 py-2 rounded-xl text-xs font-black border-2 transition flex items-center gap-1.5 cursor-pointer',
            showAllWires
              ? 'bg-indigo-600 text-white border-indigo-600 shadow-xs'
              : 'bg-white text-slate-700 border-slate-200 hover:bg-slate-50'
          ]"
        >
          <span>{{ showAllWires ? '👁️ Tüm Kablolar (Açık)' : '🔍 Adım Adım İncele' }}</span>
        </button>
      </div>
    </div>

    <!-- Adım Hapları Çubuğu -->
    <div class="bg-white rounded-2xl p-2.5 border-2 border-slate-200 shadow-xs flex items-center justify-between gap-2 overflow-x-auto">
      <div class="flex items-center gap-1.5 overflow-x-auto py-1">
        <button
          v-for="(step, idx) in baglantiAdimlari"
          :key="idx"
          type="button"
          @click="currentStepIndex = idx"
          :class="[
            'px-3.5 py-1.5 rounded-xl text-xs font-black transition flex items-center gap-1 shrink-0 cursor-pointer select-none',
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
      <div class="flex items-center gap-2 shrink-0">
        <button
          type="button"
          @click="prevStep"
          :disabled="currentStepIndex === 0"
          class="px-3 py-1.5 rounded-xl text-xs font-extrabold border-2 border-slate-200 text-slate-700 hover:bg-slate-100 disabled:opacity-40 cursor-pointer transition"
        >
          ◀ Önceki
        </button>
        <button
          type="button"
          @click="nextStep"
          :disabled="currentStepIndex >= totalSteps - 1"
          class="px-3.5 py-1.5 rounded-xl text-xs font-black bg-indigo-600 text-white hover:bg-indigo-700 disabled:opacity-40 shadow-xs cursor-pointer transition"
        >
          Sonraki ▶
        </button>
      </div>
    </div>

    <!-- SVG DEVRE ÇALIŞMA ALANI -->
    <div class="relative w-full overflow-hidden bg-slate-900 rounded-3xl border-2 border-slate-800 shadow-xl flex items-center justify-center p-2">
      <svg
        viewBox="0 0 1000 680"
        class="w-full h-auto select-none max-h-[660px]"
        xmlns="http://www.w3.org/2000/svg"
      >
        <defs>
          <pattern id="devreGrid" width="25" height="25" patternUnits="userSpaceOnUse">
            <circle cx="2" cy="2" r="1" fill="#334155" opacity="0.3" />
          </pattern>
        </defs>

        <rect width="1000" height="680" fill="#0f172a" />
        <rect width="1000" height="680" fill="url(#devreGrid)" />

        <text x="30" y="32" fill="#475569" font-size="11" font-weight="800" letter-spacing="1">
          KID ARDUINO STUDIO • ADIM {{ currentStepNumber }}: {{ currentStep?.kaynak_parca }} ({{ currentStep?.kaynak_pin }}) ➔ {{ currentStep?.hedef_parca }} ({{ currentStep?.hedef_pin }})
        </text>

        <!-- ============================================== -->
        <!-- 1. BREADBOARD (30 SÜTUN STANDART DENEY TAHTASI)-->
        <!-- ============================================== -->
        <g id="breadboard-container">
          <!-- Breadboard Gövdesi (x=40, y=50, w=920, h=315) -->
          <rect x="40" y="50" width="920" height="315" rx="14" fill="#f8fafc" stroke="#cbd5e1" stroke-width="2.5" />

          <!-- Bölge 1: Sütun 1-8 (Sol Bölge: LED & Direnç) -->
          <rect x="75" y="112" width="235" height="92" rx="6" fill="#e0f2fe" opacity="0.5" />
          <text x="192" y="106" fill="#0284c7" font-size="9" font-weight="900" text-anchor="middle">
            SOL BÖLGE: LED & DİRENÇ (SÜTUN 1–8)
          </text>

          <!-- Bölge 2: Sütun 10-18 (Orta Bölge: Sensörler & Buton) -->
          <rect x="330" y="112" width="265" height="188" rx="6" fill="#f3e8ff" opacity="0.5" />
          <text x="462" y="106" fill="#9333ea" font-size="9" font-weight="900" text-anchor="middle">
            ORTA BÖLGE: SENSÖRLER & BUTON (SÜTUN 10–18)
          </text>

          <!-- Bölge 3: Sütun 20-28 (Sağ Bölge: Buzzer & Motor) -->
          <rect x="610" y="212" width="265" height="88" rx="6" fill="#fef3c7" opacity="0.5" />
          <text x="742" y="106" fill="#d97706" font-size="9" font-weight="900" text-anchor="middle">
            SAĞ BÖLGE: BUZZER & MOTOR (SÜTUN 20–28)
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

          <!-- Satır Harfleri (A B C D E | F G H I J) -->
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

          <!-- 30 Sütun Delikleri -->
          <g>
            <template v-for="c in 30" :key="'bb-col-' + c">
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

              <circle :cx="getColX(c)" :cy="74" r="2.5" fill="#0f172a" stroke="#94a3b8" stroke-width="0.5" />
              <circle :cx="getColX(c)" :cy="92" r="2.5" fill="#0f172a" stroke="#94a3b8" stroke-width="0.5" />

              <circle :cx="getColX(c)" :cy="120" r="2.5" fill="#0f172a" stroke="#94a3b8" stroke-width="0.5" />
              <circle :cx="getColX(c)" :cy="138" r="2.5" fill="#0f172a" stroke="#94a3b8" stroke-width="0.5" />
              <circle :cx="getColX(c)" :cy="156" r="2.5" fill="#0f172a" stroke="#94a3b8" stroke-width="0.5" />
              <circle :cx="getColX(c)" :cy="174" r="2.5" fill="#0f172a" stroke="#94a3b8" stroke-width="0.5" />
              <circle :cx="getColX(c)" :cy="192" r="2.5" fill="#0f172a" stroke="#94a3b8" stroke-width="0.5" />

              <circle :cx="getColX(c)" :cy="220" r="2.5" fill="#0f172a" stroke="#94a3b8" stroke-width="0.5" />
              <circle :cx="getColX(c)" :cy="238" r="2.5" fill="#0f172a" stroke="#94a3b8" stroke-width="0.5" />
              <circle :cx="getColX(c)" :cy="256" r="2.5" fill="#0f172a" stroke="#94a3b8" stroke-width="0.5" />
              <circle :cx="getColX(c)" :cy="274" r="2.5" fill="#0f172a" stroke="#94a3b8" stroke-width="0.5" />
              <circle :cx="getColX(c)" :cy="292" r="2.5" fill="#0f172a" stroke="#94a3b8" stroke-width="0.5" />

              <circle :cx="getColX(c)" :cy="320" r="2.5" fill="#0f172a" stroke="#94a3b8" stroke-width="0.5" />
              <circle :cx="getColX(c)" :cy="338" r="2.5" fill="#0f172a" stroke="#94a3b8" stroke-width="0.5" />
            </template>
          </g>

          <!-- Aktif Dikey Sütun İletken Şerit Vurgusu -->
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

          <!-- Bileşenler (Breadboard Üzerinde) -->
          <!-- LED: E5, E6 -->
          <g id="bb-comp-led" v-if="hasComponent('LED')">
            <path d="M 210 178 C 210 152, 228 152, 228 178 Z" fill="#ef4444" stroke="#b91c1c" stroke-width="2" />
            <ellipse cx="219" cy="178" rx="9" ry="3" fill="#991b1b" />
            <path d="M 214 181 L 205 192" fill="none" stroke="#cbd5e1" stroke-width="2.5" />
            <circle cx="205" cy="192" r="4.5" fill="#ef4444" stroke="#ffffff" stroke-width="1.5" />
            <path d="M 224 181 L 233 192" fill="none" stroke="#94a3b8" stroke-width="2.5" />
            <circle cx="233" cy="192" r="4.5" fill="#3b82f6" stroke="#ffffff" stroke-width="1.5" />
            <text x="219" y="150" fill="#f87171" font-size="8" font-weight="900" text-anchor="middle">LED</text>
          </g>

          <!-- 220Ω Direnç: C6 -> RAIL_GND -->
          <g id="bb-comp-resistor" v-if="hasComponent('RESISTOR')">
            <line x1="233" y1="156" x2="233" y2="170" stroke="#cbd5e1" stroke-width="2.5" />
            <rect x="227" y="170" width="12" height="30" rx="4" fill="#d97706" stroke="#b45309" stroke-width="1" />
            <rect x="227" y="175" width="12" height="2.5" fill="#ef4444" />
            <rect x="227" y="180" width="12" height="2.5" fill="#ef4444" />
            <rect x="227" y="185" width="12" height="2.5" fill="#78350f" />
            <rect x="227" y="192" width="12" height="2" fill="#fbbf24" />
            <path d="M 233 200 L 233 338" fill="none" stroke="#cbd5e1" stroke-width="2.5" stroke-dasharray="4,2" />
            <circle cx="233" cy="156" r="4.5" fill="#f59e0b" stroke="#ffffff" stroke-width="1.5" />
            <circle cx="233" cy="338" r="4.5" fill="#3b82f6" stroke="#ffffff" stroke-width="1.5" />
            <text x="248" y="188" fill="#d97706" font-size="8" font-weight="900">220Ω</text>
          </g>

          <!-- LDR: E12, E14 -->
          <g id="bb-comp-ldr" v-if="hasComponent('LDR')">
            <circle cx="429" cy="165" r="14" fill="#f59e0b" stroke="#b45309" stroke-width="2" />
            <path d="M 421 160 Q 429 155, 437 160 Q 429 170, 421 170" fill="none" stroke="#78350f" stroke-width="1.5" />
            <line x1="423" y1="175" x2="401" y2="192" stroke="#cbd5e1" stroke-width="2.5" />
            <circle cx="401" cy="192" r="4.5" fill="#10b981" stroke="#ffffff" stroke-width="1.5" />
            <line x1="435" y1="175" x2="457" y2="192" stroke="#cbd5e1" stroke-width="2.5" />
            <circle cx="457" cy="192" r="4.5" fill="#ef4444" stroke="#ffffff" stroke-width="1.5" />
            <text x="429" y="145" fill="#059669" font-size="8" font-weight="900" text-anchor="middle">LDR Göz</text>
          </g>

          <!-- HC-SR04: F14..F17 -->
          <g id="bb-comp-hcsr04" v-if="hasComponent('HCSR04')">
            <rect x="420" y="235" width="125" height="45" rx="5" fill="#0284c7" stroke="#0369a1" stroke-width="1.5" />
            <circle cx="445" cy="257" r="14" fill="#94a3b8" stroke="#475569" stroke-width="1.5" />
            <circle cx="445" cy="257" r="9" fill="#cbd5e1" />
            <circle cx="515" cy="257" r="14" fill="#94a3b8" stroke="#475569" stroke-width="1.5" />
            <circle cx="515" cy="257" r="9" fill="#cbd5e1" />
            <circle :cx="getColX(14)" :cy="220" r="4" fill="#ef4444" stroke="#ffffff" stroke-width="1" />
            <circle :cx="getColX(15)" :cy="220" r="4" fill="#3b82f6" stroke="#ffffff" stroke-width="1" />
            <circle :cx="getColX(16)" :cy="220" r="4" fill="#10b981" stroke="#ffffff" stroke-width="1" />
            <circle :cx="getColX(17)" :cy="220" r="4" fill="#475569" stroke="#ffffff" stroke-width="1" />
            <text x="480" y="275" fill="#ffffff" font-size="8" font-weight="900" text-anchor="middle">HC-SR04</text>
          </g>

          <!-- Buzzer: F22, F24 -->
          <g id="bb-comp-buzzer" v-if="hasComponent('BUZZER')">
            <circle cx="709" cy="245" r="22" fill="#0f172a" stroke="#475569" stroke-width="2" />
            <circle cx="709" cy="245" r="7" fill="#1e293b" />
            <text x="695" y="238" fill="#f59e0b" font-size="10" font-weight="900">+</text>
            <line x1="697" y1="230" x2="681" y2="220" stroke="#cbd5e1" stroke-width="2.5" />
            <circle cx="681" cy="220" r="4.5" fill="#f59e0b" stroke="#ffffff" stroke-width="1.5" />
            <line x1="721" y1="230" x2="737" y2="220" stroke="#cbd5e1" stroke-width="2.5" />
            <circle cx="737" cy="220" r="4.5" fill="#3b82f6" stroke="#ffffff" stroke-width="1.5" />
            <text x="709" y="280" fill="#f59e0b" font-size="8" font-weight="900" text-anchor="middle">Buzzer</text>
          </g>
        </g>

        <!-- ============================================== -->
        <!-- 2. ARDUINO UNO R3 (BREADBOARD ALTINDA SABİT)   -->
        <!-- ============================================== -->
        <g id="arduino-uno">
          <rect x="280" y="390" width="440" height="270" rx="14" fill="#0284c7" stroke="#0369a1" stroke-width="2.5" />

          <!-- USB Portu (Sol) -->
          <rect x="250" y="415" width="45" height="50" rx="3" fill="#94a3b8" stroke="#475569" stroke-width="1.5" />
          <text x="253" y="480" fill="#cbd5e1" font-size="8" font-weight="700">USB</text>

          <!-- Güç Jakı -->
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

          <!-- Üst Header (Dijital Header) -->
          <rect x="385" y="395" width="295" height="20" rx="3" fill="#0f172a" stroke="#1e293b" stroke-width="1.5" />
          <g v-for="(pin, key) in upperArduinoPins" :key="'upper-pin-' + key">
            <rect :x="pin.x - 5" :y="pin.y - 5" width="10" height="10" rx="2" fill="#1e293b" stroke="#475569" />
            <circle :cx="pin.x" :cy="pin.y" r="2.5" fill="#f8fafc" />
            <text :x="pin.x" :y="pin.y + 16" fill="#bae6fd" font-size="7.5" font-weight="800" text-anchor="middle">
              {{ pin.label }}
            </text>
          </g>

          <!-- Alt Header (Güç ve Analog) -->
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
        <!-- 3. KABLOLAR (BEZIER ARCLARI + HEDEF BALONLARI)-->
        <!-- ============================================== -->

        <!-- Pasif / Önceki Kablolar (%20 Opaklık) -->
        <g id="bg-wires">
          <g v-for="(wire, idx) in backgroundWires" :key="'bg-wire-' + idx">
            <path
              :d="wire.pathD"
              fill="none"
              :stroke="wire.step.kablo_rengi"
              :stroke-width="showAllWires ? 4 : 3"
              stroke-linecap="round"
              :opacity="showAllWires ? 0.85 : 0.2"
            />
            <circle :cx="wire.p1.x" :cy="wire.p1.y" :r="showAllWires ? 4 : 3" :fill="wire.step.kablo_rengi" stroke="#ffffff" stroke-width="1" />
            <circle :cx="wire.p2.x" :cy="wire.p2.y" :r="showAllWires ? 4 : 3" :fill="wire.step.kablo_rengi" stroke="#ffffff" stroke-width="1" />
          </g>
        </g>

        <!-- Aktif Kablo (Pulsing Glow + Flowing Akım) -->
        <g id="active-wire" v-if="activeWire">
          <!-- Parlayan Dış Aura -->
          <path
            :d="activeWire.pathD"
            fill="none"
            :stroke="activeWire.step.kablo_rengi"
            stroke-width="9"
            stroke-linecap="round"
            opacity="0.35"
          />

          <!-- Ana Akım Kablosu -->
          <path
            :d="activeWire.pathD"
            fill="none"
            :stroke="activeWire.step.kablo_rengi"
            stroke-width="4.5"
            stroke-linecap="round"
            class="wire-flowing"
          />

          <!-- Kaynak Pin Radar Efekti -->
          <circle :cx="activeWire.p1.x" :cy="activeWire.p1.y" r="14" fill="none" :stroke="activeWire.step.kablo_rengi" stroke-width="2" class="animate-ping" opacity="0.8" />
          <circle :cx="activeWire.p1.x" :cy="activeWire.p1.y" r="5.5" :fill="activeWire.step.kablo_rengi" stroke="#ffffff" stroke-width="2" />

          <!-- Hedef Pin Radar Efekti -->
          <circle :cx="activeWire.p2.x" :cy="activeWire.p2.y" r="14" fill="none" :stroke="activeWire.step.kablo_rengi" stroke-width="2" class="animate-ping" opacity="0.8" />
          <circle :cx="activeWire.p2.x" :cy="activeWire.p2.y" r="5.5" :fill="activeWire.step.kablo_rengi" stroke="#ffffff" stroke-width="2" />

          <!-- Eğlenceli 'Buraya Tak' Konuşma Balonları -->
          <g :transform="`translate(${activeWire.p1.x}, ${activeWire.p1.y - 20})`">
            <rect x="-35" y="-14" width="70" height="18" rx="9" fill="#1e293b" stroke="#ffffff" stroke-width="1.5" />
            <text x="0" y="-2" fill="#38bdf8" font-size="8" font-weight="900" text-anchor="middle">📍 Buraya Tak</text>
          </g>

          <g :transform="`translate(${activeWire.p2.x}, ${activeWire.p2.y - 20})`">
            <rect x="-30" y="-14" width="60" height="18" rx="9" :fill="activeWire.step.kablo_rengi" stroke="#ffffff" stroke-width="1.5" />
            <text x="0" y="-2" fill="#ffffff" font-size="8" font-weight="900" text-anchor="middle">🎯 Tıkla!</text>
          </g>
        </g>
      </svg>
    </div>

    <!-- Alt Buton: Sonraki Sayfaya Geç -->
    <div class="flex items-center justify-between pt-2">
      <button
        type="button"
        @click="$emit('prev-page')"
        class="px-5 py-3 rounded-2xl border-2 border-slate-300 bg-white hover:bg-slate-50 text-slate-700 font-extrabold text-sm transition cursor-pointer"
      >
        ◀ Fikri Düzenle
      </button>

      <button
        type="button"
        @click="$emit('next-page')"
        class="px-7 py-3 rounded-2xl bg-amber-500 hover:bg-amber-600 text-white font-black text-sm shadow-md transition flex items-center gap-2 cursor-pointer"
      >
        <span>Devreyi Kurdum, Mantığa Geç! 🧠</span>
        <span>➔</span>
      </button>
    </div>

  </div>
</template>

<script setup lang="ts">
import { ref, computed } from 'vue';
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

defineEmits<{
  (e: 'next-page'): void;
  (e: 'prev-page'): void;
}>();

const currentStepIndex = ref(0);
const showAllWires = ref(false);

const totalSteps = computed(() => props.baglantiAdimlari.length);
const currentStepNumber = computed(() => (totalSteps.value > 0 ? currentStepIndex.value + 1 : 0));
const currentStep = computed(() => props.baglantiAdimlari[currentStepIndex.value] || null);

function getColX(col: number): number {
  return BREADBOARD_GRID.getColX(col);
}

function hasComponent(name: string): boolean {
  const comp = name.toUpperCase();
  return (
    (props.gerekliParcalar && props.gerekliParcalar.some(p => p.toUpperCase().includes(comp))) ||
    (props.baglantiAdimlari && props.baglantiAdimlari.some(s => s.kaynak_parca.toUpperCase().includes(comp) || s.hedef_parca.toUpperCase().includes(comp)))
  );
}

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

const activeNetHighlight = computed(() => {
  if (!currentStep.value) return null;
  const p1 = getPinCoordinates(currentStep.value.kaynak_parca, currentStep.value.kaynak_pin, 'breadboard');
  const p2 = getPinCoordinates(currentStep.value.hedef_parca, currentStep.value.hedef_pin, 'breadboard');
  const target = (p2 && p2.col) ? p2 : (p1 && p1.col ? p1 : null);
  if (!target || !target.col) return null;

  const colX = getColX(target.col);
  const isTop = target.row && 'ABCDE'.includes(target.row);
  const isBottom = target.row && 'FGHIJ'.includes(target.row);

  if (isTop) return { x: colX, y1: 120, y2: 192 };
  if (isBottom) return { x: colX, y1: 220, y2: 292 };
  return null;
});

function createBezierPath(p1: { x: number; y: number }, p2: { x: number; y: number }): string {
  const dx = p2.x - p1.x;
  const dy = p2.y - p1.y;
  const dist = Math.sqrt(dx * dx + dy * dy);

  if (dist < 40) {
    const arch = 16;
    return `M ${p1.x} ${p1.y} C ${p1.x} ${p1.y - arch}, ${p2.x} ${p2.y - arch}, ${p2.x} ${p2.y}`;
  }

  const sag = Math.min(Math.max(dist * 0.22, 35), 90);
  const cy1 = p1.y < p2.y ? p1.y - sag * 0.5 : p1.y - sag * 0.7;
  const cy2 = p2.y > 350 ? p2.y + sag * 0.5 : p2.y - sag * 0.7;
  const cx1 = p1.x + dx * 0.35;
  const cx2 = p1.x + dx * 0.65;

  return `M ${p1.x} ${p1.y} C ${cx1} ${cy1}, ${cx2} ${cy2}, ${p2.x} ${p2.y}`;
}

const activeWire = computed(() => {
  if (!currentStep.value) return null;
  const p1 = getPinCoordinates(currentStep.value.kaynak_parca, currentStep.value.kaynak_pin, 'breadboard');
  const p2 = getPinCoordinates(currentStep.value.hedef_parca, currentStep.value.hedef_pin, 'breadboard');
  if (!p1 || !p2) return null;
  return {
    step: currentStep.value,
    p1,
    p2,
    pathD: createBezierPath(p1, p2)
  };
});

const backgroundWires = computed(() => {
  const wires = [];
  const limit = showAllWires.value ? props.baglantiAdimlari.length : currentStepIndex.value;
  for (let i = 0; i < limit; i++) {
    const step = props.baglantiAdimlari[i];
    if (!step) continue;
    if (!showAllWires.value && i === currentStepIndex.value) continue;
    const p1 = getPinCoordinates(step.kaynak_parca, step.kaynak_pin, 'breadboard');
    const p2 = getPinCoordinates(step.hedef_parca, step.hedef_pin, 'breadboard');
    if (p1 && p2) {
      wires.push({ step, p1, p2, pathD: createBezierPath(p1, p2) });
    }
  }
  return wires;
});

function nextStep() {
  if (currentStepIndex.value < totalSteps.value - 1) currentStepIndex.value++;
}

function prevStep() {
  if (currentStepIndex.value > 0) currentStepIndex.value--;
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

<template>
  <div class="w-full max-w-6xl mx-auto flex-1 flex flex-col gap-3 py-2 sm:py-3 px-2 sm:px-4 select-none">
    
    <!-- 0. 2. AŞAMA AI (AKIŞ & ARDUINO KODU) CANLI DOĞRULAMA DURUM BANDI -->
    <div
      :class="[
        'rounded-2xl px-3.5 py-2 border-2 border-slate-900 shadow-[0_3px_0_#0f172a] flex flex-wrap items-center justify-between gap-2 text-xs transition-colors',
        isGeneratingLogic
          ? 'bg-sky-100 text-sky-950'
          : 'bg-emerald-100 text-emerald-950'
      ]"
    >
      <div class="flex items-center gap-2 font-black">
        <span v-if="isGeneratingLogic" class="animate-spin text-base">⚙️</span>
        <span v-else class="text-base">✅</span>
        <span v-if="isGeneratingLogic">
          2. Aşama AI Ajanı Çalışıyor: Bu kablolamaya (wiring) uygun Akış Diyagramı ve Arduino Kodu hazırlanıp doğrulanıyor...
        </span>
        <span v-else>
          Kablolama, Akış Diyagramı ve Arduino Kodu %100 Uyumlu! ({{ layoutResult.components.length }} Parça, {{ layoutResult.wires.length }} Kablo, 0 Hata)
        </span>
      </div>

      <div v-if="!isGeneratingLogic && verification?.pin_bindings?.length" class="flex flex-wrap items-center gap-1.5">
        <span
          v-for="b in verification.pin_bindings"
          :key="`${b.uno_pin}-${b.component_id}`"
          class="px-2 py-0.5 rounded-lg bg-white border border-slate-900 text-[10px] font-black text-slate-900 shadow-2xs"
        >
          Pin {{ b.uno_pin }} ➔ {{ b.component_label }}
        </span>
      </div>
    </div>

    <!-- 0-B. MALZEME ÇANTASINDA OLMAYAN PARÇALAR İÇİN MİNİK UYARI -->
    <div
      v-if="missingInventoryComponents.length > 0"
      class="rounded-xl px-3 py-1.5 bg-amber-50 border border-amber-400 text-amber-950 flex flex-wrap items-center justify-between gap-2 text-[11px] font-bold shadow-2xs"
    >
      <div class="flex items-center gap-1.5 flex-wrap">
        <span>🎒</span>
        <span>
          <strong>Çanta Notu:</strong> Bu devrede kullanılan
          <strong class="underline decoration-amber-500">{{ missingInventoryComponents.map(m => m.label).join(', ') }}</strong>
          şu an Malzeme Çantanda seçili görünmüyor.
        </span>
      </div>
      <button
        type="button"
        @click="$emit('open-inventory')"
        class="px-2 py-0.5 rounded-lg bg-amber-200 hover:bg-amber-300 border border-slate-900 text-[10px] font-black text-slate-900 cursor-pointer shrink-0 transition"
      >
        🧰 Çantamı Düzenle
      </button>
    </div>

    <!-- 1. ÜST ADIM VE ÇOCUK DOSTU TALİMAT BANDI (3D Çizgi Film Kartı) -->
    <div class="bg-white rounded-2xl sm:rounded-3xl p-3 sm:p-4 border-[3px] border-slate-900 shadow-[0_4px_0_#0f172a] flex flex-col lg:flex-row items-stretch lg:items-center justify-between gap-3">
      <div class="flex items-start sm:items-center gap-3 flex-1 min-w-0">
        <!-- Adım Sayacı Rozeti -->
        <div
          class="w-12 h-12 sm:w-14 sm:h-14 rounded-2xl flex flex-col items-center justify-center font-black text-white shrink-0 border-2 border-slate-900 shadow-[0_3px_0_#0f172a]"
          :style="{ backgroundColor: currentWire ? currentWire.color : '#3b82f6' }"
        >
          <span class="text-[9px] uppercase tracking-wider opacity-90">ADIM</span>
          <span class="text-base sm:text-lg leading-none">{{ currentStepNumber }}/{{ totalSteps }}</span>
        </div>

        <!--
          Tüm adımların metinleri aynı ızgara hücresinde üst üste durur, sadece geçerli adım görünür.
          Kart böylece en uzun adımın yüksekliğini alır ve adım değişince alttaki
          Önceki/Sonraki Kablo butonları aşağı yukarı kaymaz.
        -->
        <div class="min-w-0 flex-1 grid">
          <div
            v-for="(details, idx) in stepTextVariants"
            :key="details.id"
            :class="['col-start-1 row-start-1 min-w-0', idx === currentStepIndex ? '' : 'invisible']"
            :aria-hidden="idx !== currentStepIndex"
          >
            <!-- Nereden -> Nereye Görsel Rozetleri -->
            <div v-if="!details.isPlaceholder" class="flex flex-wrap items-center gap-1.5 mb-1">
              <span
                class="px-2 py-0.5 rounded-lg text-[10px] font-black border border-slate-900 text-white shadow-2xs"
                :style="{ backgroundColor: layoutResult.wires[idx]?.color || '#3b82f6' }"
              >
                {{ details.colorName }} Kablo
              </span>
              <span class="px-2.5 py-0.5 rounded-lg bg-sky-100 border border-slate-900 text-[11px] font-black text-slate-900">
                1️⃣ Nereden: {{ details.fromTitle }}
              </span>
              <span class="font-black text-slate-900 text-xs">➔</span>
              <span class="px-2.5 py-0.5 rounded-lg bg-[#fde047] border border-slate-900 text-[11px] font-black text-slate-950">
                2️⃣ Nereye Tak: {{ details.toTitle }}
              </span>
            </div>

            <h3 class="text-xs sm:text-sm md:text-base font-black text-slate-900 leading-snug">
              {{ details.kidInstruction }}
            </h3>
            <p class="text-[11px] sm:text-xs text-slate-600 font-bold mt-0.5">
              💡 <strong>Ne İşe Yarar?</strong> {{ details.kidWhy }}
            </p>
          </div>
        </div>
      </div>

      <!-- Aksiyon Butonları: AI ile Revize Et, Oto-Kayıt kapalıysa Kaydet, Tümü/Adım Adım -->
      <div class="flex items-center gap-1.5 sm:gap-2 shrink-0 flex-wrap self-end lg:self-center">
        <!-- AI ile Geliştir / Revize Et Butonu -->
        <button
          type="button"
          @click="$emit('open-revision')"
          class="px-3.5 py-2 rounded-xl text-xs font-black border-2 border-slate-900 bg-gradient-to-r from-purple-200 via-indigo-100 to-sky-200 hover:from-purple-300 hover:to-sky-300 text-slate-950 transition flex items-center gap-1.5 cursor-pointer shadow-[0_2px_0_#0f172a] active:translate-y-0.5"
          title="Mevcut devreye yeni bir sensör, LED veya kural eklemek için yapay zekayı kullan"
        >
          <span>✨</span>
          <span>Projeyi Geliştir</span>
        </button>

        <!-- Projeyi Kaydet (Otomatik kayıt kapalıysa görünür) -->
        <button
          v-if="!autoSave"
          type="button"
          @click="$emit('save-project')"
          class="px-3 py-2 rounded-xl text-xs font-black border-2 border-slate-900 bg-emerald-100 hover:bg-emerald-200 text-emerald-950 transition flex items-center gap-1.5 cursor-pointer shadow-[0_2px_0_#0f172a] active:translate-y-0.5"
          title="Bu projeyi arşivime kaydet"
        >
          <span>💾</span>
          <span>Projeyi Kaydet</span>
        </button>

        <!-- Tümü / Adım Adım Modu Butonları -->
        <button
          type="button"
          @click="showAllWires = !showAllWires"
          :class="[
            'px-3 py-2 rounded-xl text-xs font-black border-2 border-slate-900 transition flex items-center gap-1.5 cursor-pointer shadow-[0_2px_0_#0f172a] active:translate-y-0.5',
            showAllWires
              ? 'bg-[#38bdf8] text-slate-950'
              : 'bg-white text-slate-800 hover:bg-slate-50'
          ]"
        >
          <!-- İki yazı da aynı hücrede durur; buton en uzun yazının genişliğinde sabit kalır -->
          <span class="grid">
            <span :class="['col-start-1 row-start-1', showAllWires ? '' : 'invisible']">👁️ Tüm Kablolar</span>
            <span :class="['col-start-1 row-start-1', showAllWires ? 'invisible' : '']">🔍 Adım Adım</span>
          </span>
        </button>
      </div>
    </div>

    <!-- 2. ADIM SEÇİCİ VE İLERİ/GERİ KONTROLLERİ -->
    <div class="bg-white rounded-2xl p-2 sm:p-2.5 border-[2.5px] border-slate-900 shadow-[0_3px_0_#0f172a] flex items-center justify-between gap-2 overflow-x-auto">
      <div class="flex items-center gap-1.5 overflow-x-auto py-0.5">
        <button
          v-for="(wire, idx) in layoutResult.wires"
          :key="wire.id"
          type="button"
          @click="selectStep(idx)"
          :class="[
            'px-3 py-1 rounded-xl text-xs font-black transition flex items-center gap-1.5 shrink-0 cursor-pointer border-2 border-slate-900 select-none',
            currentStepIndex === idx
              ? 'bg-[#fde047] text-slate-950 shadow-[0_2px_0_#ca8a04] scale-102'
              : idx < currentStepIndex
              ? 'bg-emerald-100 text-emerald-950'
              : 'bg-slate-100 text-slate-600 hover:bg-slate-200'
          ]"
        >
          <span
            class="w-2.5 h-2.5 rounded-full border border-slate-900 shrink-0"
            :style="{ backgroundColor: wire.color || '#38bdf8' }"
          ></span>
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
          class="px-3 py-1.5 rounded-xl text-xs font-black border-2 border-slate-900 bg-white hover:bg-slate-50 disabled:opacity-40 text-slate-800 shadow-xs cursor-pointer active:translate-y-0.5"
        >
          ◀ Önceki Kablo
        </button>
        <button
          type="button"
          @click="nextStep"
          :disabled="currentStepIndex >= totalSteps - 1"
          class="px-3.5 py-1.5 rounded-xl text-xs font-black border-2 border-slate-900 bg-[#38bdf8] hover:bg-[#0284c7] disabled:opacity-40 text-slate-950 shadow-[0_2px_0_#0f172a] cursor-pointer active:translate-y-0.5"
        >
          Sonraki Kablo ▶
        </button>
      </div>
    </div>

    <!-- 3. OTOMATİK NETLIST-TO-BREADBOARD GÖRSEL ÇALIŞMA ALANI (Dinamik Fit-to-Screen & Tam Ekran) -->
    <div
      ref="workspaceRef"
      :class="[
        'relative w-full overflow-auto bg-slate-900 border-[3px] border-slate-900 shadow-[0_8px_0_rgba(15,23,42,0.2)] select-none pt-12 pb-3 px-3 transition-all',
        isFullscreen ? 'fixed inset-0 z-50 rounded-none h-screen' : 'rounded-3xl min-h-[540px]'
      ]"
      :style="isFullscreen ? {} : { minHeight: `${workspaceMinHeight}px` }"
    >
      <!-- Arka Plan Grid Ağı -->
      <div class="absolute inset-0 pointer-events-none opacity-25" style="background-image: radial-gradient(#64748b 1px, transparent 1px); background-size: 20px 20px;"></div>

      <!-- Üst Bilgi Rozeti -->
      <div class="absolute top-3 left-4 right-32 z-20 pointer-events-none flex flex-wrap items-center gap-2">
        <span class="px-2.5 py-1 rounded-lg bg-slate-800/90 border border-slate-700 text-[11px] font-black tracking-wide text-amber-300">
          ⚡ AKILLI DEVRE ŞEMASI • Çocuk Dostu Kablolama
        </span>
        <span
          v-if="layoutResult.errors.length === 0"
          class="px-2 py-0.5 rounded-lg bg-emerald-950/90 border border-emerald-500/60 text-[10px] font-bold text-emerald-300"
        >
          ✓ Elektriksel Kontrol: 0 Kısa Devre, 0 Hata
        </span>
        <span
          v-else
          class="px-2 py-0.5 rounded-lg bg-rose-950/90 border border-rose-500/70 text-[10px] font-bold text-rose-300"
        >
          ⚠️ {{ layoutResult.errors[0] }}
        </span>
      </div>

      <!-- Sağ Üst Zoom, Tam Ekran ve Entegre Rehber Kontrolleri -->
      <div class="absolute top-2.5 right-3 z-40 flex items-center gap-1 bg-slate-800/90 border border-slate-700 rounded-xl p-1 shadow-md">
        <!-- Entegre Devre Rehberi Dock Butonu -->
        <button
          type="button"
          @click="isDockOpen = !isDockOpen"
          :class="[
            'px-2.5 h-6 rounded-lg font-black text-[10px] flex items-center gap-1 cursor-pointer transition',
            isDockOpen ? 'bg-indigo-400 text-slate-950' : 'bg-slate-700 hover:bg-slate-600 text-slate-200'
          ]"
          :title="isDockOpen ? 'Rehber Panelini Gizle' : 'Rehber Panelini Göster'"
        >
          <span>📋</span>
          <span class="hidden sm:inline">{{ isDockOpen ? 'Paneli Kapat' : 'Parça & Kablo Rehberi' }}</span>
        </button>

        <button
          type="button"
          @click="zoomOut"
          title="Uzaklaştır"
          class="w-6 h-6 rounded-lg bg-slate-900 hover:bg-slate-700 text-slate-200 font-black text-xs flex items-center justify-center cursor-pointer"
        >
          −
        </button>
        <button
          type="button"
          @click="resetZoom"
          title="Ekrana Sığdır"
          class="px-2 h-6 rounded-lg bg-amber-400 hover:bg-amber-300 text-slate-950 font-black text-[10px] flex items-center justify-center cursor-pointer"
        >
          Sığdır {{ Math.round(effectiveScale * 100) }}%
        </button>
        <button
          type="button"
          @click="zoomIn"
          title="Yakınlaştır"
          class="w-6 h-6 rounded-lg bg-slate-900 hover:bg-slate-700 text-slate-200 font-black text-xs flex items-center justify-center cursor-pointer"
        >
          +
        </button>

        <!-- Tam Ekran Modu Butonu -->
        <button
          type="button"
          @click="toggleFullscreen"
          class="w-6 h-6 rounded-lg bg-slate-700 hover:bg-slate-600 text-white font-black text-xs flex items-center justify-center cursor-pointer"
          :title="isFullscreen ? 'Tam Ekrandan Çık' : 'Tam Ekran Moduna Geç'"
        >
          {{ isFullscreen ? '🗗' : '⛶' }}
        </button>
      </div>

      <!-- ÖLÇEKLENMİŞ SAHNE SARMALAYICISI (Kırpma olmadan ekrana tam sığar) -->
      <div
        class="relative mx-auto shrink-0"
        :style="{
          width: `${scaledStageWidth}px`,
          height: `${scaledStageHeight}px`
        }"
      >
        <!-- SAHNE İÇ KUTUSU (Dinamik bounds boyutunda, top-left origin ile scale) -->
        <div
          class="relative"
          :style="{
            width: `${sceneBounds.width}px`,
            height: `${sceneBounds.height}px`,
            transform: `scale(${effectiveScale})`,
            transformOrigin: 'top left'
          }"
        >
          <!-- HTML BİLEŞEN KATMANI (Sahne minX/minY ofseti kadar kaydırılır) -->
          <div
            class="absolute top-0 left-0"
            :style="{
              transform: `translate(${-sceneBounds.minX}px, ${-sceneBounds.minY}px)`
            }"
          >
        <!-- ======================================================== -->
        <!-- A) ARDUINO UNO KARTI (Tek kaynak SCENE_LAYOUT)           -->
        <!-- ======================================================== -->
        <div
          id="comp-arduino-card"
          class="absolute z-10 p-[8px] rounded-2xl bg-slate-800/45 border border-slate-700/70 shadow-lg pointer-events-auto"
          :style="{
            left: `${SCENE_LAYOUT.uno.x - SCENE_LAYOUT.uno.cardPad}px`,
            top: `${SCENE_LAYOUT.uno.y - SCENE_LAYOUT.uno.cardPad}px`
          }"
        >
          <div class="relative">
            <wokwi-arduino-uno></wokwi-arduino-uno>
          </div>
          <div class="text-[11px] font-black text-center text-sky-300 mt-1 pointer-events-none">
            🟦 Arduino Uno (Ana Beyin)
          </div>
        </div>

        <!-- ======================================================== -->
        <!-- B) BREADBOARD VE ÜZERİNE TAKILAN PARÇALAR (SCENE_LAYOUT) -->
        <!-- ======================================================== -->
        <div
          id="comp-breadboard-card"
          class="absolute z-10 p-[8px] rounded-2xl bg-slate-800/45 border border-slate-700/70 shadow-lg"
          :style="{
            left: `${SCENE_LAYOUT.bb.x - SCENE_LAYOUT.bb.cardPad}px`,
            top: `${SCENE_LAYOUT.bb.y - SCENE_LAYOUT.bb.cardPad}px`,
            width: `${(layoutResult.breadboardWidth || SCENE_LAYOUT.bb.width) + SCENE_LAYOUT.bb.cardPad * 2}px`
          }"
        >
          <!-- Sıfır Paddingli İç Kutu: Orijini Tam (448, 108) -->
          <div class="relative">
            <component
              :is="layoutResult.breadboardType === 'full' ? 'wokwi-breadboard' : 'wokwi-breadboard-half'"
              id="comp-breadboard"
              :highlighted-columns="highlightedColsStr"
              :highlighted-rails="layoutResult.highlightedRails"
            ></component>

            <!-- BREADBOARD ÜZERİNE TAKILAN PARÇALAR -->
            <div
              v-for="comp in mountedComponents"
              :key="comp.id"
              class="absolute z-20 group pointer-events-auto cursor-pointer"
              :style="{ left: `${comp.left}px`, top: `${comp.top}px` }"
            >
              <component :is="comp.type" v-bind="comp.props" class="pointer-events-none"></component>

              <!-- Kademelendirilmiş Çocuk Dostu Parça Etiketi (Delik Bilgisi Sadece Hover'da Görünür) -->
              <div
                class="absolute -translate-x-1/2 px-2 py-0.5 rounded-lg bg-slate-900/95 border border-amber-400/80 text-[9px] font-black text-amber-300 shadow-md whitespace-nowrap flex items-center gap-1 pointer-events-none"
                :style="{ left: `${comp.labelX - comp.left}px`, top: `${comp.labelY}px` }"
              >
                <span>{{ comp.label }}</span>
                <span class="hidden group-hover:inline text-emerald-300 text-[8px]">
                  ({{ formatComponentHolesShort(comp) }})
                </span>
              </div>
            </div>
          </div>

          <div class="text-[10px] font-black text-center text-amber-300 mt-1.5 pointer-events-none">
            {{ layoutResult.breadboardType === 'full' ? '🟨 Büyük Breadboard (60 Sütun - İç İletken Hatlar A-E ve F-J)' : '🟨 Breadboard (30 Sütun - İç İletken Hatlar A-E ve F-J)' }}
          </div>
        </div>

        <!-- ======================================================== -->
        <!-- C) HARİCİ SENSÖR & MOTOR İSTASYONU (Gerçek pinInfo)      -->
        <!-- ======================================================== -->
        <div
          v-for="comp in offBoardComponents"
          :key="comp.id"
          class="absolute z-10 rounded-2xl bg-slate-800/80 border-2 border-cyan-500/60 shadow-lg"
          :style="{
            left: `${comp.left}px`,
            top: `${comp.top}px`,
            width: `${comp.width || 140}px`,
            height: `${comp.height || 96}px`
          }"
        >
          <!-- Modül Başlığı -->
          <div class="absolute top-1 left-1.5 right-1.5 flex justify-center pointer-events-none">
            <span class="px-2 py-0.5 rounded-md bg-slate-950/90 border border-cyan-500/40 text-[9px] font-black text-cyan-300 truncate max-w-full">
              {{ comp.label }}
            </span>
          </div>

          <!-- Wokwi Elemanı Görseli (Deterministik top-left origin + scale) -->
          <div
            class="absolute pointer-events-none"
            :style="{
              left: `${comp.elementOffsetX ?? 14}px`,
              top: `${comp.elementOffsetY ?? 28}px`,
              width: `${comp.elementNaturalWidth ?? 80}px`,
              height: `${comp.elementNaturalHeight ?? 78}px`,
              transform: `scale(${comp.elementScale ?? 0.7})`,
              transformOrigin: 'top left'
            }"
          >
            <component :is="comp.type" v-bind="comp.props"></component>
          </div>
        </div>

        <!-- Off-Board Pin Etiketleri Overlay (Doğrudan gerçek soket koordinatlarına hizalı) -->
        <div class="absolute inset-0 pointer-events-none z-25">
          <div
            v-for="lbl in offBoardPinLabels"
            :key="lbl.key"
            class="absolute px-1 py-0.2 rounded bg-slate-950/95 border border-amber-400/90 text-[7.5px] font-black text-amber-200 leading-none shadow-xs whitespace-nowrap"
            :class="lbl.posClass"
            :style="{ left: `${lbl.x}px`, top: `${lbl.y}px` }"
          >
            {{ lbl.pinName }}
          </div>
        </div>
          </div>

          <!-- ======================================================== -->
          <!-- D) BİLEŞEN BACAKLARI, İÇ İLETKENLİK VE KABLOLAR (SVG)     -->
          <!-- ======================================================== -->
          <svg
            class="absolute inset-0 pointer-events-none z-30"
            :width="sceneBounds.width"
            :height="sceneBounds.height"
            :viewBox="sceneViewBox"
          >
          <defs>
            <filter id="wireGlow" x="-20%" y="-20%" width="140%" height="140%">
              <feDropShadow dx="0" dy="3" stdDeviation="2.5" flood-color="#000000" flood-opacity="0.6" />
            </filter>
          </defs>

          <!-- 1. Ortak Sütun İç İletkenlik Köprüleri (Örn: Direnç 8C <-> LED Anot 8E) -->
          <g v-for="bridge in sharedColumnBridges" :key="bridge.id">
            <line
              :x1="bridge.x"
              :y1="bridge.y1"
              :x2="bridge.x"
              :y2="bridge.y2"
              stroke="#22c55e"
              stroke-width="6"
              stroke-linecap="round"
              opacity="0.35"
            />
            <line
              :x1="bridge.x"
              :y1="bridge.y1"
              :x2="bridge.x"
              :y2="bridge.y2"
              stroke="#4ade80"
              stroke-width="2.5"
              stroke-dasharray="3,2"
              stroke-linecap="round"
            />
          </g>

          <!-- 2. Breadboard Üzerindeki Parçaların Delik Noktaları ve Delik Etiketleri (Sadece Mouse Üzerine Geldiğinde Görünür) -->
          <g
            v-for="pinMarker in mountedPinMarkers"
            :key="pinMarker.key"
            class="group pointer-events-auto cursor-pointer"
          >
            <!-- Rahat Hover Alanı (Şeffaf Yakalama Halkası) -->
            <circle
              :cx="pinMarker.cx"
              :cy="pinMarker.cy"
              r="9"
              fill="transparent"
            />
            <!-- Bacak Lehim/Temas Noktası -->
            <circle
              :cx="pinMarker.cx"
              :cy="pinMarker.cy"
              r="3.5"
              fill="#fbbf24"
              stroke="#0f172a"
              stroke-width="1.5"
              class="transition-transform group-hover:scale-125"
            />
            <!-- Delik Koordinat Rozeti (4E, 6E vb.) - Sadece Hover'da Görünür -->
            <g class="opacity-0 group-hover:opacity-100 transition-opacity duration-150 pointer-events-none">
              <rect
                :x="pinMarker.cx - 13"
                :y="pinMarker.cy + 5"
                width="26"
                height="14"
                rx="4"
                fill="#0f172a"
                stroke="#fbbf24"
                stroke-width="1.2"
              />
              <text
                :x="pinMarker.cx"
                :y="pinMarker.cy + 14.5"
                fill="#fde047"
                font-size="8.5"
                font-weight="900"
                text-anchor="middle"
              >
                {{ pinMarker.holeName }}
              </text>
            </g>
          </g>

          <!-- 3. Kablolar -->
          <g v-for="(wire, idx) in visibleWires" :key="wire.id">
            <!-- Kablo Gölgesi -->
            <path
              :d="wire.path"
              fill="none"
              stroke="#020617"
              :stroke-width="idx === currentStepIndex && !showAllWires ? 7 : 5.5"
              stroke-linecap="round"
              opacity="0.55"
            />
            <!-- Ana Kablo Yolu -->
            <path
              :d="wire.path"
              fill="none"
              :stroke="wire.color || '#38bdf8'"
              :stroke-width="idx === currentStepIndex && !showAllWires ? 4.5 : 3.5"
              stroke-linecap="round"
              :opacity="!showAllWires && idx !== currentStepIndex ? 0.55 : 1"
            />

            <!-- Başlangıç Pini Halkası -->
            <circle
              :cx="wire.from.x"
              :cy="wire.from.y"
              r="4.5"
              :fill="wire.color || '#38bdf8'"
              stroke="#ffffff"
              stroke-width="1.5"
            />

            <!-- Bitiş Pini Halkası -->
            <circle
              :cx="wire.to.x"
              :cy="wire.to.y"
              r="4.5"
              :fill="wire.color || '#38bdf8'"
              stroke="#ffffff"
              stroke-width="1.5"
            />
          </g>

          <!-- 4. Aktif Adım Başlangıç ("1️⃣ Buradan") ve Hedef ("2️⃣ Buraya Tak!") Göstergeleri -->
          <g v-if="currentWire && !showAllWires">
            <!-- Başlangıç Pini Parlama Halkası -->
            <circle
              :cx="currentWire.from.x"
              :cy="currentWire.from.y"
              r="8"
              fill="#38bdf8"
              opacity="0.3"
            />
            <circle
              :cx="currentWire.from.x"
              :cy="currentWire.from.y"
              r="5.5"
              fill="#0284c7"
              stroke="#ffffff"
              stroke-width="2"
            />

            <!-- "1️⃣ Başla" Etiketi -->
            <g :transform="`translate(${currentWire.from.x}, ${currentWire.from.y - 24})`">
              <rect
                x="-46"
                y="-12"
                width="92"
                height="20"
                rx="7"
                fill="#bae6fd"
                stroke="#0f172a"
                stroke-width="2"
                filter="url(#wireGlow)"
              />
              <text x="0" y="1.5" fill="#0f172a" font-size="9.5" font-weight="900" text-anchor="middle">
                1️⃣ {{ currentWireShortFrom }}
              </text>
            </g>

            <!-- Hedef Pini Parlama Halkası -->
            <circle
              :cx="currentWire.to.x"
              :cy="currentWire.to.y"
              r="10"
              fill="#facc15"
              opacity="0.3"
            />
            <circle
              :cx="currentWire.to.x"
              :cy="currentWire.to.y"
              r="6"
              fill="#eab308"
              stroke="#ffffff"
              stroke-width="2"
            />

            <!-- "2️⃣ Buraya Tak!" Çizgi Film Konuşma Baloncuğu -->
            <g :transform="`translate(${currentWire.to.x}, ${currentWire.to.y - 34})`">
              <rect
                x="-62"
                y="-15"
                width="124"
                height="26"
                rx="9"
                fill="#fde047"
                stroke="#0f172a"
                stroke-width="2.5"
                filter="url(#wireGlow)"
              />
              <polygon
                points="0,12 -6,17 6,17"
                fill="#fde047"
                stroke="#0f172a"
                stroke-width="2"
              />
              <text x="0" y="2.5" fill="#0f172a" font-size="10.5" font-weight="900" text-anchor="middle">
                👇 2️⃣ {{ currentWireShortTo }}
              </text>
            </g>
          </g>
          </svg>
        </div>
      </div>

      <!-- ENTEGRE ÇOCUK DOSTU PARÇA & KABLO REHBERİ (Açılıp Kapanabilen Akıllı Dock) -->
      <div
        v-if="isDockOpen"
        class="absolute bottom-3 right-3 left-3 sm:left-auto sm:w-[390px] max-h-[300px] bg-white/95 backdrop-blur-md rounded-2xl border-2 border-slate-900 shadow-[0_8px_0_rgba(15,23,42,0.4)] z-40 flex flex-col overflow-hidden animate-in fade-in slide-in-from-bottom-2 duration-150 pointer-events-auto"
      >
        <!-- Dock Başlık & Sekmeler -->
        <div class="px-3 py-2 bg-slate-100 border-b border-slate-300 flex items-center justify-between gap-2 shrink-0">
          <div class="flex items-center gap-1">
            <button
              type="button"
              @click="activeDockTab = 'parts'"
              :class="[
                'px-2.5 py-1 rounded-lg text-xs font-black transition cursor-pointer border',
                activeDockTab === 'parts'
                  ? 'bg-amber-300 text-slate-950 border-slate-900 shadow-2xs'
                  : 'bg-white text-slate-700 border-slate-300 hover:bg-slate-50'
              ]"
            >
              🧩 Parçalar ({{ layoutResult.components.length }})
            </button>
            <button
              type="button"
              @click="activeDockTab = 'wires'"
              :class="[
                'px-2.5 py-1 rounded-lg text-xs font-black transition cursor-pointer border',
                activeDockTab === 'wires'
                  ? 'bg-sky-300 text-slate-950 border-slate-900 shadow-2xs'
                  : 'bg-white text-slate-700 border-slate-300 hover:bg-slate-50'
              ]"
            >
              🔌 Kablo Adımları ({{ layoutResult.wires.length }})
            </button>
          </div>

          <button
            type="button"
            @click="isDockOpen = false"
            class="w-6 h-6 rounded-lg bg-slate-200 hover:bg-rose-100 hover:text-rose-700 text-slate-700 font-black text-xs flex items-center justify-center cursor-pointer transition"
            title="Paneli Kapat"
          >
            ✕
          </button>
        </div>

        <!-- Dock İçeriği -->
        <div class="p-2.5 overflow-y-auto flex-1 flex flex-col gap-1.5 text-xs">
          <!-- Sekme 1: Parça Yerleşimleri -->
          <template v-if="activeDockTab === 'parts'">
            <div
              v-for="comp in layoutResult.components"
              :key="comp.id"
              class="p-2 rounded-xl bg-slate-50 border border-slate-200 flex flex-col gap-1"
            >
              <div class="flex items-center justify-between gap-1">
                <strong class="font-black text-slate-900 truncate">{{ comp.label }}</strong>
                <span class="text-[9.5px] px-1.5 py-0.2 rounded bg-amber-100 border border-amber-300 text-amber-950 font-bold">
                  {{ comp.isBreadboardMounted ? 'Breadboard' : 'Harici Modül' }}
                </span>
              </div>
              <div class="flex flex-wrap gap-1">
                <span
                  v-for="pin in Object.values(comp.pins)"
                  :key="pin.pinName"
                  class="px-1.5 py-0.5 rounded bg-white border border-slate-300 text-[9px] font-bold text-slate-700"
                >
                  {{ pin.pinName }}: <strong class="text-slate-950">{{ comp.isBreadboardMounted ? `${pin.holeName} Pini` : `${pin.pinName} Pini` }}</strong>
                </span>
              </div>
            </div>
          </template>

          <!-- Sekme 2: Kablo Adımları Listesi -->
          <template v-else>
            <button
              v-for="(item, idx) in allWireDetails"
              :key="item.id"
              type="button"
              @click="selectStep(idx)"
              :class="[
                'w-full text-left px-2 py-1.5 rounded-xl border text-[11px] font-bold transition flex items-center justify-between gap-2 cursor-pointer',
                currentStepIndex === idx
                  ? 'bg-[#fde047] border-slate-900 text-slate-950 font-black shadow-2xs'
                  : 'bg-white hover:bg-slate-50 border-slate-200 text-slate-700'
              ]"
            >
              <div class="flex items-center gap-1.5 min-w-0">
                <span
                  class="w-4 h-4 rounded-md border border-slate-900 text-[8.5px] font-black text-white flex items-center justify-center shrink-0"
                  :style="{ backgroundColor: item.color }"
                >
                  {{ idx + 1 }}
                </span>
                <span class="truncate">
                  {{ item.fromTitle }} ➔ {{ item.toTitle }}
                </span>
              </div>
              <span class="text-[9px] font-black shrink-0 opacity-75">{{ item.colorName }}</span>
            </button>
          </template>
        </div>
      </div>
    </div>

    <!-- 5. ALT BİLGİ BANDI VE GEÇİŞ BUTONU -->
    <div class="bg-amber-50 rounded-2xl border-2 border-amber-300 p-2.5 flex flex-col sm:flex-row items-center justify-between gap-3 text-xs">
      <div class="flex items-center gap-2 text-amber-950 font-bold">
        <span class="text-base">💡</span>
        <span>
          <strong>Süper İpucu:</strong> Breadboard üzerinde yeşil kesikli çizgiyle birleşen pinler (örneğin aynı sütundaki <strong>C</strong> ve <strong>E</strong> pinleri) içeriden birbirine bağlıdır, aralarına ekstra kablo takmana gerek yoktur!
        </span>
      </div>

      <div class="flex items-center gap-2 shrink-0">
        <button
          type="button"
          @click="$emit('prev-page')"
          class="px-3 py-1.5 rounded-xl border-2 border-slate-900 bg-white hover:bg-slate-50 text-slate-800 font-black text-xs transition cursor-pointer shadow-xs active:translate-y-0.5"
        >
          ◀ 1. Hayal Et
        </button>

        <button
          type="button"
          @click="$emit('next-page')"
          class="px-5 py-2 rounded-2xl border-2 border-slate-900 bg-[#4ade80] hover:bg-[#22c55e] text-slate-950 font-black text-xs sm:text-sm shadow-[0_4px_0_#15803d] active:translate-y-1 active:shadow-none transition cursor-pointer flex items-center gap-1.5"
        >
          <span>3. Nasıl Çalışacak'a Geç</span>
          <span class="text-base">➔</span>
        </button>
      </div>
    </div>

  </div>
</template>

<script setup lang="ts">
import { ref, computed, watch, onMounted, onBeforeUnmount } from 'vue';
import type { CircuitNetlist, BaglantiAdimi, LogicVerificationReport } from '../types/project';
import {
  compileNetlistToBreadboard,
  SCENE_LAYOUT,
  DEFAULT_ROUTER_OFFSETS,
  type AutoLayoutResult,
  type PlacedComponent,
  type RoutedWire
} from '../circuit';

const props = defineProps<{
  netlist?: CircuitNetlist;
  baglantiAdimlari?: BaglantiAdimi[];
  gerekliParcalar?: string[];
  selectedInventory?: string[];
  isGeneratingLogic?: boolean;
  verification?: LogicVerificationReport;
  autoSave?: boolean;
}>();

const emit = defineEmits<{
  (e: 'next-page'): void;
  (e: 'prev-page'): void;
  (e: 'open-inventory'): void;
  (e: 'open-revision'): void;
  (e: 'save-project'): void;
}>();

function isComponentInInventory(comp: PlacedComponent): boolean {
  const inv = props.selectedInventory || [];
  if (inv.length === 0) return false;
  const invSet = new Set(inv.map(i => i.toUpperCase()));

  if (comp.type === 'wokwi-led') {
    const color = String(comp.props?.color || 'red').toLowerCase();
    if (color === 'green') return invSet.has('LED_GREEN') || invSet.has('LED_RGB');
    if (color === 'yellow') return invSet.has('LED_YELLOW') || invSet.has('LED_RGB');
    if (color === 'blue') return invSet.has('LED_BLUE') || invSet.has('LED_RGB');
    return invSet.has('LED_RED') || invSet.has('LED_RGB');
  }
  if (comp.type === 'wokwi-resistor') {
    const val = String(comp.props?.value || '').toLowerCase();
    if (val.includes('10000') || val.includes('10k')) {
      return invSet.has('RESISTOR_10K') || invSet.has('RESISTOR_1K') || invSet.has('RESISTOR_220');
    }
    if (val.includes('1000') || val.includes('1k')) {
      return invSet.has('RESISTOR_1K') || invSet.has('RESISTOR_220') || invSet.has('RESISTOR_10K');
    }
    return invSet.has('RESISTOR_220') || invSet.has('RESISTOR_1K') || invSet.has('RESISTOR_10K');
  }
  if (comp.type === 'wokwi-photoresistor') {
    return invSet.has('LDR_DISCRETE') || invSet.has('LDR_SENSOR') || invSet.has('LDR_MODULE');
  }
  if (comp.type === 'wokwi-photoresistor-sensor') {
    return invSet.has('LDR_MODULE') || invSet.has('LDR_SENSOR') || invSet.has('LDR_DISCRETE');
  }
  if (comp.type === 'wokwi-servo') {
    return invSet.has('SERVO_SG90');
  }
  if (comp.type === 'wokwi-buzzer') {
    return invSet.has('BUZZER') || invSet.has('ACTIVE_BUZZER');
  }
  if (comp.type === 'wokwi-pushbutton') {
    return invSet.has('PUSH_BUTTON') || invSet.has('SLIDE_SWITCH');
  }
  if (comp.type === 'wokwi-hc-sr04') {
    return invSet.has('HCSR04');
  }
  if (comp.type === 'wokwi-potentiometer') {
    return invSet.has('POTENTIOMETER');
  }
  return true;
}

const missingInventoryComponents = computed(() => {
  return layoutResult.value.components.filter(c => !isComponentInInventory(c));
});

const currentStepIndex = ref(0);
const showAllWires = ref(false);

const activeNetlist = computed<CircuitNetlist>(() => {
  if (props.netlist && props.netlist.components && props.netlist.components.length > 0) {
    return props.netlist;
  }
  return {
    board: 'arduino-uno',
    components: [],
    connections: []
  };
});

// Auto-Layout Motorunun Çalıştırılması (Tek kaynak DEFAULT_ROUTER_OFFSETS)
const layoutResult = computed<AutoLayoutResult>(() => {
  return compileNetlistToBreadboard(activeNetlist.value, DEFAULT_ROUTER_OFFSETS);
});

// Dinamik Fit-to-Screen + ResizeObserver + Zoom Kontrolleri
const workspaceRef = ref<HTMLElement | null>(null);
const containerWidth = ref(980);
const containerHeight = ref(540);
const userZoom = ref(1);
let workspaceObserver: ResizeObserver | null = null;

const isFullscreen = ref(false);
const isDockOpen = ref(false);
const activeDockTab = ref<'parts' | 'wires'>('parts');

function toggleFullscreen() {
  isFullscreen.value = !isFullscreen.value;
  setTimeout(() => {
    updateWorkspaceSize();
  }, 100);
}

function updateWorkspaceSize() {
  const el = workspaceRef.value;
  if (!el) return;
  containerWidth.value = Math.max(260, el.clientWidth - 24);
  const vh = typeof window !== 'undefined' ? window.innerHeight : 800;
  if (isFullscreen.value) {
    containerHeight.value = Math.max(500, vh - 60);
  } else {
    containerHeight.value = Math.max(480, Math.min(850, Math.round(vh * 0.74)));
  }
}

onMounted(() => {
  updateWorkspaceSize();
  if (typeof ResizeObserver !== 'undefined' && workspaceRef.value) {
    workspaceObserver = new ResizeObserver(() => {
      updateWorkspaceSize();
    });
    workspaceObserver.observe(workspaceRef.value);
  }
  if (typeof window !== 'undefined') {
    window.addEventListener('resize', updateWorkspaceSize);
  }
});

onBeforeUnmount(() => {
  if (workspaceObserver) {
    workspaceObserver.disconnect();
    workspaceObserver = null;
  }
  if (typeof window !== 'undefined') {
    window.removeEventListener('resize', updateWorkspaceSize);
  }
});

const sceneBounds = computed(() => layoutResult.value.bounds);
const sceneViewBox = computed(
  () => `${sceneBounds.value.minX} ${sceneBounds.value.minY} ${sceneBounds.value.width} ${sceneBounds.value.height}`
);

const fitScale = computed(() => {
  const w = Math.max(1, sceneBounds.value.width);
  const h = Math.max(1, sceneBounds.value.height);
  return Math.min(1, containerWidth.value / w, containerHeight.value / h);
});

const effectiveScale = computed(() => {
  return Math.max(0.25, Math.min(2, fitScale.value * userZoom.value));
});

const scaledStageWidth = computed(() => Math.ceil(sceneBounds.value.width * effectiveScale.value));
const scaledStageHeight = computed(() => Math.ceil(sceneBounds.value.height * effectiveScale.value));
const workspaceMinHeight = computed(() => Math.max(480, scaledStageHeight.value + 58));

function zoomIn() {
  userZoom.value = Math.min(2.2, Number((userZoom.value + 0.15).toFixed(2)));
}

function zoomOut() {
  userZoom.value = Math.max(0.5, Number((userZoom.value - 0.15).toFixed(2)));
}

function resetZoom() {
  userZoom.value = 1;
}

watch(activeNetlist, () => {
  currentStepIndex.value = 0;
  userZoom.value = 1;
});

const mountedComponents = computed(() => {
  return layoutResult.value.components.filter(c => c.isBreadboardMounted);
});

const offBoardComponents = computed(() => {
  return layoutResult.value.components.filter(c => !c.isBreadboardMounted);
});

const offBoardPinLabels = computed(() => {
  const labels: Array<{ key: string; pinName: string; x: number; y: number; posClass: string }> = [];
  for (const comp of offBoardComponents.value) {
    for (const pin of Object.values(comp.pins)) {
      const cx = SCENE_LAYOUT.bb.x + pin.x;
      const cy = SCENE_LAYOUT.bb.y + pin.y;
      const side = pin.side || 'bottom';
      if (side === 'left') {
        labels.push({
          key: `${comp.id}.${pin.pinName}`,
          pinName: pin.pinName,
          x: cx - 5,
          y: cy,
          posClass: '-translate-x-full -translate-y-1/2'
        });
      } else if (side === 'right') {
        labels.push({
          key: `${comp.id}.${pin.pinName}`,
          pinName: pin.pinName,
          x: cx + 5,
          y: cy,
          posClass: '-translate-y-1/2'
        });
      } else if (side === 'top') {
        labels.push({
          key: `${comp.id}.${pin.pinName}`,
          pinName: pin.pinName,
          x: cx,
          y: cy - 6,
          posClass: '-translate-x-1/2 -translate-y-full'
        });
      } else {
        labels.push({
          key: `${comp.id}.${pin.pinName}`,
          pinName: pin.pinName,
          x: cx,
          y: cy + 5,
          posClass: '-translate-x-1/2'
        });
      }
    }
  }
  return labels;
});

// Breadboard üzerine takılan parçaların delik işaretçileri
const mountedPinMarkers = computed(() => {
  const markers: Array<{ key: string; cx: number; cy: number; holeName: string }> = [];
  for (const comp of mountedComponents.value) {
    for (const pin of Object.values(comp.pins)) {
      markers.push({
        key: `${comp.id}.${pin.pinName}`,
        cx: SCENE_LAYOUT.bb.x + pin.x,
        cy: SCENE_LAYOUT.bb.y + pin.y,
        holeName: pin.holeName
      });
    }
  }
  return markers;
});

// Aynı breadboard sütununda buluşan bacakların ve kabloların yeşil iletkenlik köprüleri
const sharedColumnBridges = computed(() => {
  const byColHalf = new Map<string, Array<{ x: number; y: number }>>();
  for (const comp of mountedComponents.value) {
    for (const pin of Object.values(comp.pins)) {
      const half = ['A', 'B', 'C', 'D', 'E'].includes(pin.row.toUpperCase()) ? 'U' : 'L';
      const key = `${pin.col}:${half}`;
      if (!byColHalf.has(key)) byColHalf.set(key, []);
      byColHalf.get(key)!.push({ x: SCENE_LAYOUT.bb.x + pin.x, y: SCENE_LAYOUT.bb.y + pin.y });
    }
  }

  for (const wire of visibleWires.value) {
    for (const ep of [wire.from, wire.to]) {
      const m = (ep.holeName || '').match(/^(\d+)([A-J])$/i);
      if (m) {
        const col = parseInt(m[1], 10);
        const row = m[2].toUpperCase();
        const half = ['A', 'B', 'C', 'D', 'E'].includes(row) ? 'U' : 'L';
        const key = `${col}:${half}`;
        if (!byColHalf.has(key)) byColHalf.set(key, []);
        byColHalf.get(key)!.push({ x: ep.x, y: ep.y });
      }
    }
  }

  const bridges: Array<{ id: string; x: number; y1: number; y2: number }> = [];
  for (const [key, pts] of byColHalf.entries()) {
    if (pts.length >= 2) {
      const ys = pts.map(p => p.y);
      const minY = Math.min(...ys);
      const maxY = Math.max(...ys);
      if (maxY > minY) {
        bridges.push({
          id: `bridge-${key}`,
          x: pts[0].x,
          y1: minY,
          y2: maxY
        });
      }
    }
  }
  return bridges;
});

const totalSteps = computed(() => layoutResult.value.wires.length);
const currentStepNumber = computed(() => (totalSteps.value > 0 ? currentStepIndex.value + 1 : 0));
const currentWire = computed(() => layoutResult.value.wires[currentStepIndex.value]);

const visibleWires = computed(() => {
  if (showAllWires.value) {
    return layoutResult.value.wires;
  }
  return layoutResult.value.wires.slice(0, currentStepIndex.value + 1);
});

const highlightedColsStr = computed(() => {
  return layoutResult.value.highlightedColumns.join(',');
});

function getColorTurkishName(colorStr?: string): string {
  const c = (colorStr || '').toLowerCase();
  if (c.includes('ef4444') || c === 'red') return '🔴 Kırmızı';
  if (c.includes('1e293b') || c.includes('1f2937') || c === 'black') return '⚫ Siyah';
  if (c.includes('f97316') || c.includes('f59e0b') || c === 'orange') return '🟠 Turuncu';
  if (c.includes('eab308') || c === 'yellow') return '🟡 Sarı';
  if (c.includes('10b981') || c.includes('22c55e') || c === 'green') return '🟢 Yeşil';
  return '🔵 Mavi';
}

function formatEndpointForKid(ep: RoutedWire['from']): string {
  if (ep.part === 'uno') {
    return `Arduino Pin ${ep.pin}`;
  }
  if (ep.part === 'breadboard') {
    if (ep.holeName?.startsWith('bn.')) return `Breadboard Mavi Eksi (-) Hattı (${ep.holeName} Pini)`;
    if (ep.holeName?.startsWith('bp.')) return `Breadboard Kırmızı Artı (+) Hattı (${ep.holeName} Pini)`;
    return `Breadboard ${ep.holeName || ep.pin} Pini`;
  }
  const compId = ep.part.split('.')[0];
  const comp = layoutResult.value.components.find(c => c.id === compId);
  const compName = comp?.label || compId;
  if (comp && !comp.isBreadboardMounted) {
    return `${compName} (${ep.pin} Pini)`;
  }
  return `Breadboard ${ep.holeName || ep.pin} Pini (${compName})`;
}

function buildWireKidDetail(wire: RoutedWire) {
  const fromTitle = formatEndpointForKid(wire.from);
  const toTitle = formatEndpointForKid(wire.to);
  const colorName = getColorTurkishName(wire.color);

  let kidWhy = 'Elektrik sinyalini ve veriyi iki nokta arasında güvenle taşır.';
  if (wire.isPowerBus && wire.to.holeName?.startsWith('bn.')) {
    kidWhy = 'Arduino\'nun GND (Toprak) hattını breadboard\'un altındaki mavi (-) sırasına taşır; böylece tüm parçalar ortak toprağı kullanır.';
  } else if (wire.isPowerBus && wire.to.holeName?.startsWith('bp.')) {
    kidWhy = 'Arduino\'nun 5V enerji hattını breadboard\'un altındaki kırmızı (+) sırasına taşır.';
  } else if (wire.to.holeName?.startsWith('bn.')) {
    kidWhy = 'Parçanın eksi (GND) bacağını mavi toprak hattına bağlayarak elektrik devresini tamamlar.';
  } else if (wire.to.holeName?.startsWith('bp.')) {
    kidWhy = 'Parçanın çalışması için gereken 5V elektriği kırmızı güç hattından alır.';
  } else if (wire.from.part === 'uno') {
    kidWhy = `Arduino beyninin ${wire.from.pin} kapısından çıkan komutu veya okuma sinyalini parçamıza ulaştırır.`;
  }

  return {
    id: wire.id,
    color: wire.color || '#38bdf8',
    colorName,
    fromTitle,
    toTitle,
    kidInstruction: `${colorName} kabloyu ${fromTitle} noktasından ${toTitle} noktasına tak.`,
    kidWhy
  };
}

const allWireDetails = computed(() => {
  return layoutResult.value.wires.map(w => buildWireKidDetail(w));
});

// Talimat kartında üst üste dizilen adım metinleri (kablo yoksa tek bir bekleme metni)
const stepTextVariants = computed(() => {
  if (allWireDetails.value.length > 0) {
    return allWireDetails.value.map(d => ({ ...d, isPlaceholder: false }));
  }
  return [{
    id: '__bekleniyor__',
    color: '#3b82f6',
    colorName: '',
    fromTitle: '',
    toTitle: '',
    kidInstruction: 'Kablo bağlantısı hazırlanıyor...',
    kidWhy: '',
    isPlaceholder: true
  }];
});

const currentWireShortFrom = computed(() => {
  const w = currentWire.value;
  if (!w) return '';
  if (w.from.part === 'uno') return `Arduino ${w.from.pin}`;
  return w.from.holeName || w.from.pin;
});

const currentWireShortTo = computed(() => {
  const w = currentWire.value;
  if (!w) return 'Buraya Tak!';
  if (w.to.holeName?.startsWith('bn.')) return `Eksi (-) ${w.to.holeName}`;
  if (w.to.holeName?.startsWith('bp.')) return `Artı (+) ${w.to.holeName}`;
  return `${w.to.holeName || w.to.pin} Pini`;
});

function formatComponentHolesShort(comp: PlacedComponent): string {
  return Object.values(comp.pins)
    .map(p => p.holeName)
    .join(' - ');
}

function formatPinFriendlyName(type: string, pinName: string): string {
  if (type === 'wokwi-led') {
    return pinName === 'A' ? 'Uzun Bacak (+)' : 'Kısa Bacak (-)';
  }
  if (type === 'wokwi-resistor' || type === 'wokwi-photoresistor' || type === 'wokwi-pushbutton') {
    return `${pinName}. Bacak`;
  }
  if (type === 'wokwi-buzzer') {
    return pinName === '1' ? 'Artı (+)' : 'Eksi (-)';
  }
  return `${pinName}`;
}

function selectStep(idx: number) {
  currentStepIndex.value = idx;
  showAllWires.value = false;
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
</style>

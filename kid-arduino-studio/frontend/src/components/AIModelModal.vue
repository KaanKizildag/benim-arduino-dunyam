<template>
  <div v-if="isOpen">
    <!-- Karartma Arka Planı -->
    <div
      class="fixed inset-0 z-50 bg-slate-900/60 backdrop-blur-xs flex items-center justify-center p-2 sm:p-4 select-none animate-in fade-in duration-150"
      @click.self="$emit('close')"
    >
      <!-- Modal Kutusu -->
      <div class="bg-white rounded-[32px] border-[3px] border-slate-900 shadow-[0_14px_0_rgba(15,23,42,0.35)] max-w-xl w-full overflow-hidden flex flex-col max-h-[90vh]">
        
        <!-- ÜST BAŞLIK ÇUBUĞU -->
        <div class="px-5 py-3.5 bg-gradient-to-r from-[#bae6fd] via-[#c7d2fe] to-[#e9d5ff] border-b-[3px] border-slate-900 flex items-center justify-between shrink-0">
          <div class="flex items-center gap-3">
            <div class="w-10 h-10 rounded-2xl bg-white border-2 border-slate-900 flex items-center justify-center text-2xl shadow-[0_2px_0_#0f172a]">
              🤖
            </div>
            <div>
              <h2 class="text-base sm:text-lg font-black text-slate-900 tracking-tight leading-tight flex items-center gap-2">
                <span>AI Model & Admin Paneli</span>
                <span class="px-1.5 py-0.2 rounded-md bg-indigo-600 text-white text-[9px] font-black uppercase tracking-wider">Dev</span>
              </h2>
              <span class="text-[11px] font-bold text-slate-700">
                Projeleri üreten yapay zeka modelini ve API anahtarlarını yönet
              </span>
            </div>
          </div>

          <!-- Kırmızı Kare Kapat Butonu -->
          <button
            type="button"
            @click="$emit('close')"
            class="w-8 h-8 rounded-xl bg-rose-500 hover:bg-rose-600 active:translate-y-0.5 text-white font-black text-sm flex items-center justify-center border-2 border-slate-900 shadow-[0_2px_0_#9f1239] cursor-pointer transition"
            title="Kapat"
          >
            ✕
          </button>
        </div>

        <!-- ÜST SEKME SEÇİCİ (Modeller vs API Tokenları) -->
        <div class="px-5 py-2.5 bg-slate-100 border-b-2 border-slate-900 flex items-center justify-between gap-2 shrink-0">
          <div class="flex items-center gap-2">
            <button
              type="button"
              @click="activeTab = 'models'"
              :class="[
                'px-3.5 py-1.5 rounded-xl border-2 font-black text-xs transition cursor-pointer flex items-center gap-1.5',
                activeTab === 'models'
                  ? 'bg-[#fbbf24] border-slate-900 text-slate-950 shadow-[0_2px_0_#0f172a]'
                  : 'bg-white border-slate-300 text-slate-700 hover:border-slate-900'
              ]"
            >
              <span>🤖</span>
              <span>Model Seçimi</span>
              <span class="px-1.5 py-0.2 rounded-full bg-slate-900 text-white text-[9px] font-bold">
                {{ selectedModelShortLabel }}
              </span>
            </button>

            <button
              type="button"
              @click="activeTab = 'tokens'"
              :class="[
                'px-3.5 py-1.5 rounded-xl border-2 font-black text-xs transition cursor-pointer flex items-center gap-1.5',
                activeTab === 'tokens'
                  ? 'bg-[#fbbf24] border-slate-900 text-slate-950 shadow-[0_2px_0_#0f172a]'
                  : 'bg-white border-slate-300 text-slate-700 hover:border-slate-900'
              ]"
            >
              <span>🔑</span>
              <span>API Tokenları (Kalıcı)</span>
              <span
                v-if="hasAnyToken"
                class="w-2 h-2 rounded-full bg-emerald-500"
                title="En az 1 token kayıtlı"
              ></span>
            </button>
          </div>

          <!-- OLLAMA YEREL DURUM BİLGİSİ -->
          <div class="flex items-center gap-1.5 text-[11px] font-black text-slate-700">
            <span
              class="w-2.5 h-2.5 rounded-full border border-slate-900"
              :class="ollamaAvailable ? 'bg-emerald-500 shadow-[0_0_6px_#10b981]' : 'bg-amber-400'"
            ></span>
            <span class="hidden sm:inline">{{ ollamaAvailable ? 'Ollama Aktif' : 'Ollama Yok' }}</span>
          </div>
        </div>

        <!-- İÇERİK BÖLÜMÜ (Scroll edilebilir alan) -->
        <div class="p-4 sm:p-5 flex-1 overflow-y-auto flex flex-col gap-3 min-h-0 bg-slate-50">

          <!-- ================= TAB 1: MODEL SEÇİMİ ================= -->
          <template v-if="activeTab === 'models'">
            <!-- Aktif Model Özet Bandı -->
            <div class="p-3 rounded-2xl bg-white border-2 border-slate-900/20 flex items-center justify-between text-xs font-black text-slate-800">
              <div class="flex items-center gap-2">
                <span class="text-base">🎯</span>
                <span>Aktif Model: <strong class="text-sky-700">{{ selectedModel }}</strong></span>
              </div>
              <span class="px-2 py-0.5 rounded-full bg-emerald-100 border border-emerald-600 text-emerald-950 text-[10px]">
                Seçili
              </span>
            </div>

            <!-- 1. Local Model (Ollama - Kurulu Tüm Modeller) -->
            <div
              @click="selectOllamaCard"
              :class="[
                'p-3.5 rounded-2xl border-[2.5px] flex flex-col gap-2.5 relative select-none cursor-pointer transition-all shadow-[0_3px_0_#0f172a]',
                isOllamaSelected
                  ? 'border-[#0284c7] bg-[#f0f9ff] ring-2 ring-[#38bdf8]'
                  : 'border-slate-900 bg-white hover:bg-slate-50'
              ]"
            >
              <div class="flex items-center gap-3">
                <div class="w-12 h-12 rounded-2xl bg-[#fef08a] border-2 border-slate-900 flex items-center justify-center text-2xl shrink-0 shadow-xs">
                  🤖
                </div>
                <div class="min-w-0 flex-1">
                  <div class="text-sm font-black text-slate-900 flex items-center gap-1.5 flex-wrap">
                    <span>Local Model (Ollama)</span>
                    <span class="text-[10px] bg-sky-100 text-sky-800 px-1.5 py-0.5 rounded-md font-bold border border-sky-300">
                      Yerel / Çevrimdışı ({{ localModels.length }})
                    </span>
                  </div>
                  <div class="text-[11px] font-bold text-slate-600 truncate mt-0.5">
                    {{ activeOllamaSubtitle }}
                  </div>
                </div>
                <span
                  v-if="isOllamaSelected"
                  class="px-3 py-1 rounded-full bg-[#4ade80] text-slate-950 text-xs font-black border-2 border-slate-900 shadow-xs shrink-0"
                >
                  Aktif
                </span>
              </div>

              <!-- Ollama Üzerinde Kurulu Modellerin Seçim Listesi -->
              <div
                v-if="localModels.length > 0"
                class="pt-2 border-t-2 border-dashed border-slate-900/15 flex flex-col gap-1.5"
                @click.stop
              >
                <div class="flex items-center justify-between text-[10px] font-black text-slate-500 uppercase tracking-wider px-0.5">
                  <span>Kurulu Ollama Modelleri ({{ localModels.length }} adet):</span>
                  <button
                    type="button"
                    @click="checkOllama"
                    class="text-sky-700 hover:text-sky-900 underline cursor-pointer"
                  >
                    {{ isLoadingModels ? 'Yenileniyor...' : 'Yenile 🔄' }}
                  </button>
                </div>
                <div class="grid grid-cols-1 gap-1.5 max-h-36 overflow-y-auto pr-0.5">
                  <button
                    v-for="m in localModels"
                    :key="m.id"
                    type="button"
                    @click="selectedModel = m.id"
                    :class="[
                      'w-full px-3 py-2 rounded-xl border-2 text-left flex items-center justify-between gap-2 transition cursor-pointer',
                      selectedModel === m.id
                        ? 'bg-[#fef08a] border-slate-900 text-slate-950 shadow-[0_2px_0_#0f172a]'
                        : 'bg-white/90 hover:bg-white border-slate-300 hover:border-slate-900 text-slate-700'
                    ]"
                  >
                    <div class="flex items-center gap-2 min-w-0">
                      <span
                        class="w-2.5 h-2.5 rounded-full border border-slate-900 shrink-0"
                        :class="selectedModel === m.id ? 'bg-emerald-500' : 'bg-slate-200'"
                      ></span>
                      <span class="text-xs font-black truncate">{{ m.raw_name || m.id.replace('ollama/', '') }}</span>
                    </div>
                    <span
                      v-if="selectedModel === m.id"
                      class="text-[10px] font-black px-1.5 py-0.5 rounded-md bg-emerald-500 text-white border border-slate-900 shrink-0"
                    >
                      Seçili
                    </span>
                  </button>
                </div>
              </div>

              <!-- Kurulu Model Bulunamadıysa Uyarı -->
              <div
                v-else
                class="pt-2 border-t-2 border-dashed border-slate-900/15 text-[11px] font-bold text-amber-800 bg-amber-50/80 px-2.5 py-1.5 rounded-xl border border-amber-300"
              >
                Ollama üzerinde model algılanamadı. Terminalden <code class="font-mono bg-white px-1 py-0.5 rounded border">ollama list</code> kontrol edip <b>Yenile 🔄</b> yapabilirsin.
              </div>
            </div>

            <!-- 2. Google Gemini (Alt Model Seçim Listesi ile) -->
            <div
              @click="selectGeminiCard"
              :class="[
                'p-3.5 rounded-2xl border-[2.5px] flex flex-col gap-2.5 relative select-none cursor-pointer transition-all shadow-[0_3px_0_#0f172a]',
                isGeminiSelected
                  ? 'border-[#0284c7] bg-[#f0f9ff] ring-2 ring-[#38bdf8]'
                  : 'border-slate-900 bg-white hover:bg-slate-50'
              ]"
            >
              <div class="flex items-center gap-3">
                <div class="w-12 h-12 rounded-2xl bg-white border-2 border-slate-900 flex items-center justify-center text-xl shrink-0 shadow-xs">
                  <svg class="w-7 h-7" viewBox="0 0 24 24">
                    <path d="M12 2L14.5 9.5L22 12L14.5 14.5L12 22L9.5 14.5L2 12L9.5 9.5L12 2Z" fill="url(#geminiGradModal)" />
                    <defs>
                      <linearGradient id="geminiGradModal" x1="0%" y1="0%" x2="100%" y2="100%">
                        <stop offset="0%" stop-color="#38bdf8" />
                        <stop offset="50%" stop-color="#818cf8" />
                        <stop offset="100%" stop-color="#f43f5e" />
                      </linearGradient>
                    </defs>
                  </svg>
                </div>
                <div class="min-w-0 flex-1">
                  <div class="text-sm font-black text-slate-900 flex items-center gap-1.5 flex-wrap">
                    <span>Google Gemini</span>
                    <span class="text-[10px] bg-indigo-100 text-indigo-800 px-1.5 py-0.5 rounded-md font-bold border border-indigo-300">
                      {{ geminiModels.length }} Model
                    </span>
                    <span
                      v-if="geminiKey.trim()"
                      class="text-[10px] bg-emerald-100 text-emerald-800 px-1.5 py-0.5 rounded-md font-bold border border-emerald-300"
                    >
                      Token Kayıtlı ✓
                    </span>
                  </div>
                  <div class="text-[11px] font-bold text-slate-600 truncate mt-0.5">
                    {{ activeGeminiSubtitle }}
                  </div>
                </div>
                <span
                  v-if="isGeminiSelected"
                  class="px-3 py-1 rounded-full bg-[#4ade80] text-slate-950 text-xs font-black border-2 border-slate-900 shadow-xs shrink-0"
                >
                  Aktif
                </span>
              </div>

              <!-- Google Gemini Seçiliyse Alt Modelleri Göster -->
              <div
                v-if="isGeminiSelected"
                class="pt-2 border-t-2 border-dashed border-slate-900/15 flex flex-col gap-1.5"
                @click.stop
              >
                <div class="flex items-center justify-between px-0.5">
                  <span class="text-[10px] font-black text-slate-500 uppercase tracking-wider">
                    Gemini Modeli Seç:
                  </span>
                  <button
                    v-if="geminiKey.trim()"
                    type="button"
                    @click="checkOllama"
                    class="text-[10px] font-black text-sky-700 hover:text-sky-900 underline cursor-pointer"
                  >
                    {{ isLoadingModels ? 'Yükleniyor...' : 'Token ile Güncelle 🔄' }}
                  </button>
                </div>
                <div class="grid grid-cols-1 gap-1.5 max-h-36 overflow-y-auto pr-0.5">
                  <button
                    v-for="gm in geminiModels"
                    :key="gm.id"
                    type="button"
                    @click="selectedModel = gm.id"
                    :class="[
                      'w-full px-3 py-2 rounded-xl border-2 text-left flex items-center justify-between gap-2 transition cursor-pointer',
                      selectedModel === gm.id
                        ? 'bg-[#fef08a] border-slate-900 text-slate-950 shadow-[0_2px_0_#0f172a]'
                        : 'bg-white/90 hover:bg-white border-slate-300 hover:border-slate-900 text-slate-700'
                    ]"
                  >
                    <div class="flex items-center gap-2 min-w-0">
                      <span
                        class="w-2.5 h-2.5 rounded-full border border-slate-900 shrink-0"
                        :class="selectedModel === gm.id ? 'bg-emerald-500' : 'bg-slate-200'"
                      ></span>
                      <span class="text-xs font-black truncate">{{ gm.name }}</span>
                    </div>
                    <span
                      v-if="selectedModel === gm.id"
                      class="text-[10px] font-black px-1.5 py-0.5 rounded-md bg-emerald-500 text-white border border-slate-900 shrink-0"
                    >
                      Seçili
                    </span>
                  </button>
                </div>
              </div>
            </div>

            <!-- 3. OpenAI (Alt Model Seçim Listesi ile) -->
            <div
              @click="selectOpenAICard"
              :class="[
                'p-3.5 rounded-2xl border-[2.5px] flex flex-col gap-2.5 relative select-none cursor-pointer transition-all shadow-[0_3px_0_#0f172a]',
                isOpenAISelected
                  ? 'border-[#0284c7] bg-[#f0f9ff] ring-2 ring-[#38bdf8]'
                  : 'border-slate-900 bg-white hover:bg-slate-50'
              ]"
            >
              <div class="flex items-center gap-3">
                <div class="w-12 h-12 rounded-2xl bg-slate-900 border-2 border-slate-900 flex items-center justify-center text-white text-xl shrink-0 shadow-xs">
                  <svg class="w-7 h-7 fill-current" viewBox="0 0 24 24">
                    <path d="M22.2819 9.8211a5.9847 5.9847 0 0 0-.5157-4.9108 6.0462 6.0462 0 0 0-6.5098-2.9A6.0651 6.0651 0 0 0 4.9807 4.1818a5.9847 5.9847 0 0 0-3.9977 2.9 6.0462 6.0462 0 0 0 .7427 7.0966 5.98 5.98 0 0 0 .511 4.9107 6.051 6.051 0 0 0 6.5146 2.9001A5.9847 5.9847 0 0 0 13.2599 24a6.0557 6.0557 0 0 0 5.7718-4.2058 5.9894 5.9894 0 0 0 3.9977-2.9001 6.0557 6.0557 0 0 0-.7475-7.0729zm-9.022 12.6081a4.4755 4.4755 0 0 1-2.8764-1.0408l.1419-.0804 4.7783-2.7582a.7948.7948 0 0 0 .3927-.6813v-6.7369l2.02 1.1683a.071.071 0 0 1 .038.052v5.5826a4.5045 4.5045 0 0 1-4.4945 4.4947z"/>
                  </svg>
                </div>
                <div class="min-w-0 flex-1">
                  <div class="text-sm font-black text-slate-900 flex items-center gap-1.5 flex-wrap">
                    <span>OpenAI</span>
                    <span
                      v-if="openaiKey.trim()"
                      class="text-[10px] bg-emerald-100 text-emerald-800 px-1.5 py-0.5 rounded-md font-bold border border-emerald-300"
                    >
                      Token Kayıtlı ✓
                    </span>
                  </div>
                  <div class="text-[11px] font-bold text-slate-600 truncate mt-0.5">
                    {{ isOpenAISelected ? `Seçili: ${selectedModel}` : 'GPT-4o Mini / GPT-4o / GPT-4.1 Mini' }}
                  </div>
                </div>
                <span
                  v-if="isOpenAISelected"
                  class="px-3 py-1 rounded-full bg-[#4ade80] text-slate-950 text-xs font-black border-2 border-slate-900 shadow-xs shrink-0"
                >
                  Aktif
                </span>
              </div>

              <div
                v-if="isOpenAISelected"
                class="pt-2 border-t-2 border-dashed border-slate-900/15 grid grid-cols-1 gap-1.5 max-h-36 overflow-y-auto pr-0.5"
                @click.stop
              >
                <button
                  v-for="om in openaiModels"
                  :key="om.id"
                  type="button"
                  @click="selectedModel = om.id"
                  :class="[
                    'w-full px-3 py-2 rounded-xl border-2 text-left flex items-center justify-between gap-2 transition cursor-pointer',
                    selectedModel === om.id
                      ? 'bg-[#fef08a] border-slate-900 text-slate-950 shadow-[0_2px_0_#0f172a]'
                      : 'bg-white/90 hover:bg-white border-slate-300 hover:border-slate-900 text-slate-700'
                  ]"
                >
                  <span class="text-xs font-black truncate">{{ om.name }}</span>
                  <span
                    v-if="selectedModel === om.id"
                    class="text-[10px] font-black px-1.5 py-0.5 rounded-md bg-emerald-500 text-white border border-slate-900 shrink-0"
                  >
                    Seçili
                  </span>
                </button>
              </div>
            </div>

            <!-- 4. Claude (Alt Model Seçim Listesi ile) -->
            <div
              @click="selectClaudeCard"
              :class="[
                'p-3.5 rounded-2xl border-[2.5px] flex flex-col gap-2.5 relative select-none cursor-pointer transition-all shadow-[0_3px_0_#0f172a]',
                isClaudeSelected
                  ? 'border-[#0284c7] bg-[#f0f9ff] ring-2 ring-[#38bdf8]'
                  : 'border-slate-900 bg-white hover:bg-slate-50'
              ]"
            >
              <div class="flex items-center gap-3">
                <div class="w-12 h-12 rounded-2xl bg-[#d97706] border-2 border-slate-900 flex items-center justify-center text-white text-lg font-black shrink-0 shadow-xs">
                  A\
                </div>
                <div class="min-w-0 flex-1">
                  <div class="text-sm font-black text-slate-900 flex items-center gap-1.5 flex-wrap">
                    <span>Claude</span>
                    <span
                      v-if="anthropicKey.trim()"
                      class="text-[10px] bg-emerald-100 text-emerald-800 px-1.5 py-0.5 rounded-md font-bold border border-emerald-300"
                    >
                      Token Kayıtlı ✓
                    </span>
                  </div>
                  <div class="text-[11px] font-bold text-slate-600 truncate mt-0.5">
                    {{ isClaudeSelected ? `Seçili: ${selectedModel}` : 'Anthropic Claude 3.5 Haiku / Sonnet' }}
                  </div>
                </div>
                <span
                  v-if="isClaudeSelected"
                  class="px-3 py-1 rounded-full bg-[#4ade80] text-slate-950 text-xs font-black border-2 border-slate-900 shadow-xs shrink-0"
                >
                  Aktif
                </span>
              </div>

              <div
                v-if="isClaudeSelected"
                class="pt-2 border-t-2 border-dashed border-slate-900/15 grid grid-cols-1 gap-1.5 max-h-36 overflow-y-auto pr-0.5"
                @click.stop
              >
                <button
                  v-for="cm in claudeModels"
                  :key="cm.id"
                  type="button"
                  @click="selectedModel = cm.id"
                  :class="[
                    'w-full px-3 py-2 rounded-xl border-2 text-left flex items-center justify-between gap-2 transition cursor-pointer',
                    selectedModel === cm.id
                      ? 'bg-[#fef08a] border-slate-900 text-slate-950 shadow-[0_2px_0_#0f172a]'
                      : 'bg-white/90 hover:bg-white border-slate-300 hover:border-slate-900 text-slate-700'
                  ]"
                >
                  <span class="text-xs font-black truncate">{{ cm.name }}</span>
                  <span
                    v-if="selectedModel === cm.id"
                    class="text-[10px] font-black px-1.5 py-0.5 rounded-md bg-emerald-500 text-white border border-slate-900 shrink-0"
                  >
                    Seçili
                  </span>
                </button>
              </div>
            </div>
          </template>

          <!-- ================= TAB 2: API TOKENLARI (KALICI LOCALSTORAGE) ================= -->
          <template v-else-if="activeTab === 'tokens'">
            <div class="p-3 bg-amber-50 rounded-2xl border-2 border-amber-300 text-xs font-bold text-amber-950 flex items-start gap-2">
              <span class="text-base shrink-0">💡</span>
              <div>
                Girdiğin API anahtarları tarayıcının yerel hafızasında (<code class="bg-white px-1 py-0.5 rounded font-mono">localStorage</code>) kalıcı olarak saklanır. Sayfa yenilendiğinde tekrar girmek zorunda kalmazsın!
              </div>
            </div>

            <!-- 1. Google Gemini Token Kartı -->
            <div class="p-3.5 bg-white rounded-2xl border-2 border-slate-900 flex flex-col gap-2 shadow-[0_2px_0_#0f172a]">
              <div class="flex items-center justify-between">
                <label class="text-xs font-black text-slate-900 flex items-center gap-1.5">
                  <span>🌟</span>
                  <span>Google Gemini API Key:</span>
                </label>
                <div class="flex items-center gap-1.5">
                  <span
                    class="text-[10px] font-black px-2 py-0.5 rounded-md border"
                    :class="geminiKey.trim() ? 'bg-emerald-100 text-emerald-800 border-emerald-400' : 'bg-slate-100 text-slate-500 border-slate-300'"
                  >
                    {{ geminiKey.trim() ? 'Kayıtlı ✓' : 'Tanımlanmadı' }}
                  </span>
                  <a
                    href="https://aistudio.google.com/app/apikey"
                    target="_blank"
                    rel="noopener"
                    class="text-[10px] text-sky-700 hover:underline font-bold"
                  >
                    Key Al ↗
                  </a>
                </div>
              </div>
              <div class="flex items-center gap-1.5">
                <div class="relative flex-1">
                  <input
                    :type="showGeminiKey ? 'text' : 'password'"
                    v-model="geminiKey"
                    placeholder="AIzaSy... (Gemini API Anahtarı)"
                    class="w-full px-3 py-2 pr-8 rounded-xl border-2 border-slate-900 text-xs font-mono bg-slate-50 outline-none focus:ring-2 focus:ring-sky-400"
                    @change="saveTokensToStorage"
                  />
                  <button
                    type="button"
                    @click="showGeminiKey = !showGeminiKey"
                    class="absolute right-2 top-2.5 text-xs text-slate-500 hover:text-slate-800 cursor-pointer"
                    title="Göster / Gizle"
                  >
                    {{ showGeminiKey ? '🙈' : '👁️' }}
                  </button>
                </div>
                <button
                  type="button"
                  @click="geminiKey = ''; saveTokensToStorage()"
                  class="px-2.5 py-2 rounded-xl bg-slate-100 hover:bg-rose-100 border-2 border-slate-900 text-xs text-slate-700 cursor-pointer"
                  title="Temizle"
                >
                  🗑️
                </button>
              </div>
            </div>

            <!-- 2. OpenAI Token Kartı -->
            <div class="p-3.5 bg-white rounded-2xl border-2 border-slate-900 flex flex-col gap-2 shadow-[0_2px_0_#0f172a]">
              <div class="flex items-center justify-between">
                <label class="text-xs font-black text-slate-900 flex items-center gap-1.5">
                  <span>⚡</span>
                  <span>OpenAI API Key:</span>
                </label>
                <div class="flex items-center gap-1.5">
                  <span
                    class="text-[10px] font-black px-2 py-0.5 rounded-md border"
                    :class="openaiKey.trim() ? 'bg-emerald-100 text-emerald-800 border-emerald-400' : 'bg-slate-100 text-slate-500 border-slate-300'"
                  >
                    {{ openaiKey.trim() ? 'Kayıtlı ✓' : 'Tanımlanmadı' }}
                  </span>
                  <a
                    href="https://platform.openai.com/api-keys"
                    target="_blank"
                    rel="noopener"
                    class="text-[10px] text-sky-700 hover:underline font-bold"
                  >
                    Key Al ↗
                  </a>
                </div>
              </div>
              <div class="flex items-center gap-1.5">
                <div class="relative flex-1">
                  <input
                    :type="showOpenaiKey ? 'text' : 'password'"
                    v-model="openaiKey"
                    placeholder="sk-... (OpenAI API Anahtarı)"
                    class="w-full px-3 py-2 pr-8 rounded-xl border-2 border-slate-900 text-xs font-mono bg-slate-50 outline-none focus:ring-2 focus:ring-sky-400"
                    @change="saveTokensToStorage"
                  />
                  <button
                    type="button"
                    @click="showOpenaiKey = !showOpenaiKey"
                    class="absolute right-2 top-2.5 text-xs text-slate-500 hover:text-slate-800 cursor-pointer"
                    title="Göster / Gizle"
                  >
                    {{ showOpenaiKey ? '🙈' : '👁️' }}
                  </button>
                </div>
                <button
                  type="button"
                  @click="openaiKey = ''; saveTokensToStorage()"
                  class="px-2.5 py-2 rounded-xl bg-slate-100 hover:bg-rose-100 border-2 border-slate-900 text-xs text-slate-700 cursor-pointer"
                  title="Temizle"
                >
                  🗑️
                </button>
              </div>
            </div>

            <!-- 3. Anthropic Claude Token Kartı -->
            <div class="p-3.5 bg-white rounded-2xl border-2 border-slate-900 flex flex-col gap-2 shadow-[0_2px_0_#0f172a]">
              <div class="flex items-center justify-between">
                <label class="text-xs font-black text-slate-900 flex items-center gap-1.5">
                  <span>🎭</span>
                  <span>Anthropic Claude API Key:</span>
                </label>
                <div class="flex items-center gap-1.5">
                  <span
                    class="text-[10px] font-black px-2 py-0.5 rounded-md border"
                    :class="anthropicKey.trim() ? 'bg-emerald-100 text-emerald-800 border-emerald-400' : 'bg-slate-100 text-slate-500 border-slate-300'"
                  >
                    {{ anthropicKey.trim() ? 'Kayıtlı ✓' : 'Tanımlanmadı' }}
                  </span>
                  <a
                    href="https://console.anthropic.com/settings/keys"
                    target="_blank"
                    rel="noopener"
                    class="text-[10px] text-sky-700 hover:underline font-bold"
                  >
                    Key Al ↗
                  </a>
                </div>
              </div>
              <div class="flex items-center gap-1.5">
                <div class="relative flex-1">
                  <input
                    :type="showAnthropicKey ? 'text' : 'password'"
                    v-model="anthropicKey"
                    placeholder="sk-ant-... (Claude API Anahtarı)"
                    class="w-full px-3 py-2 pr-8 rounded-xl border-2 border-slate-900 text-xs font-mono bg-slate-50 outline-none focus:ring-2 focus:ring-sky-400"
                    @change="saveTokensToStorage"
                  />
                  <button
                    type="button"
                    @click="showAnthropicKey = !showAnthropicKey"
                    class="absolute right-2 top-2.5 text-xs text-slate-500 hover:text-slate-800 cursor-pointer"
                    title="Göster / Gizle"
                  >
                    {{ showAnthropicKey ? '🙈' : '👁️' }}
                  </button>
                </div>
                <button
                  type="button"
                  @click="anthropicKey = ''; saveTokensToStorage()"
                  class="px-2.5 py-2 rounded-xl bg-slate-100 hover:bg-rose-100 border-2 border-slate-900 text-xs text-slate-700 cursor-pointer"
                  title="Temizle"
                >
                  🗑️
                </button>
              </div>
            </div>
          </template>

        </div>

        <!-- ALT BUTON: KAYDET VE UYGULA! -->
        <div class="p-3.5 sm:p-4 bg-white border-t-[3px] border-slate-900 flex items-center justify-between gap-3 shrink-0">
          <div class="text-xs font-bold text-slate-600 flex items-center gap-1.5">
            <span v-if="saveSuccess" class="text-emerald-700 font-black animate-in fade-in flex items-center gap-1">
              <span>✅</span> Ayarlar Kaydedildi!
            </span>
            <span v-else>
              💾 Yapılan seçimler tarayıcıya otomatik işlenir.
            </span>
          </div>

          <button
            type="button"
            @click="handleSave"
            class="px-6 py-2.5 rounded-full bg-gradient-to-r from-[#38bdf8] to-[#0284c7] hover:from-[#7dd3fc] hover:to-[#0369a1] active:translate-y-0.5 text-slate-950 font-black text-xs sm:text-sm border-2 border-slate-900 shadow-[0_3px_0_#0f172a] transition-all cursor-pointer flex items-center gap-1.5"
          >
            <span>Kaydet ve Uygula 🚀</span>
          </button>
        </div>

      </div>
    </div>
  </div>
</template>

<script setup lang="ts">
import { ref, computed, watch, onMounted } from 'vue';
import type { ModelInfo, ModelsResponse } from '../types/project';

const props = defineProps<{
  isOpen: boolean;
  currentModel: string;
}>();

const emit = defineEmits<{
  (e: 'close'): void;
  (e: 'save', payload: { model: string; apiKey?: string }): void;
}>();

const activeTab = ref<'models' | 'tokens'>('models');
const saveSuccess = ref(false);

// Kalıcı model seçimi
const selectedModel = ref(
  props.currentModel ||
  localStorage.getItem('kid_arduino_selected_model') ||
  'gemini/gemini-2.5-flash'
);

// Bağımsız kalıcı tokenlar
const geminiKey = ref(
  localStorage.getItem('kid_arduino_gemini_key') ||
  localStorage.getItem('kid_arduino_api_key') ||
  ''
);
const openaiKey = ref(
  localStorage.getItem('kid_arduino_openai_key') || ''
);
const anthropicKey = ref(
  localStorage.getItem('kid_arduino_anthropic_key') || ''
);

// Şifre göster / gizle durumları
const showGeminiKey = ref(false);
const showOpenaiKey = ref(false);
const showAnthropicKey = ref(false);

const ollamaAvailable = ref(true);
const isLoadingModels = ref(false);
const localModels = ref<ModelInfo[]>([]);
const cloudModels = ref<ModelInfo[]>([
  { id: 'gemini/gemini-2.5-flash', name: 'Gemini 2.5 Flash (Önerilen & Hızlı)', provider: 'gemini', category: 'Google Gemini', badge: '☁️ Bulut' },
  { id: 'gemini/gemini-2.5-pro', name: 'Gemini 2.5 Pro (Gelişmiş Mantık)', provider: 'gemini', category: 'Google Gemini', badge: '☁️ Bulut' },
  { id: 'gemini/gemini-2.0-flash', name: 'Gemini 2.0 Flash (Hızlı)', provider: 'gemini', category: 'Google Gemini', badge: '☁️ Bulut' },
  { id: 'gemini/gemini-1.5-flash', name: 'Gemini 1.5 Flash', provider: 'gemini', category: 'Google Gemini', badge: '☁️ Bulut' },
  { id: 'gpt-4o-mini', name: 'GPT-4o Mini (Hızlı & Ekonomik)', provider: 'openai', category: 'OpenAI', badge: '☁️ Bulut' },
  { id: 'gpt-4o', name: 'GPT-4o (Amiral Gemisi)', provider: 'openai', category: 'OpenAI', badge: '☁️ Bulut' },
  { id: 'gpt-4.1-mini', name: 'GPT-4.1 Mini (Yeni Nesil Kodlama)', provider: 'openai', category: 'OpenAI', badge: '☁️ Bulut' },
  { id: 'claude-3-5-haiku-20241022', name: 'Claude 3.5 Haiku (Hızlı)', provider: 'anthropic', category: 'Anthropic Claude', badge: '☁️ Bulut' },
  { id: 'claude-3-5-sonnet-20241022', name: 'Claude 3.5 Sonnet (Kodlama Uzmanı)', provider: 'anthropic', category: 'Anthropic Claude', badge: '☁️ Bulut' }
]);

const hasAnyToken = computed(() => {
  return Boolean(geminiKey.value.trim() || openaiKey.value.trim() || anthropicKey.value.trim());
});

watch(() => props.currentModel, (v) => {
  if (v) selectedModel.value = v;
});

watch(() => props.isOpen, (open) => {
  if (open) {
    checkOllama();
  }
});

const isOllamaSelected = computed(() => {
  return selectedModel.value.startsWith('ollama') || selectedModel.value === 'local';
});

const isGeminiSelected = computed(() => {
  return selectedModel.value.includes('gemini');
});

const isOpenAISelected = computed(() => {
  return selectedModel.value.includes('gpt');
});

const isClaudeSelected = computed(() => {
  return selectedModel.value.includes('claude');
});

const geminiModels = computed(() => {
  return cloudModels.value.filter(m => m.provider === 'gemini' || m.id.includes('gemini'));
});

const openaiModels = computed(() => {
  return cloudModels.value.filter(m => m.provider === 'openai' || m.id.includes('gpt'));
});

const claudeModels = computed(() => {
  return cloudModels.value.filter(m => m.provider === 'anthropic' || m.id.includes('claude'));
});

const selectedModelShortLabel = computed(() => {
  if (isOllamaSelected.value) return 'Ollama';
  if (isGeminiSelected.value) return 'Gemini';
  if (isOpenAISelected.value) return 'OpenAI';
  if (isClaudeSelected.value) return 'Claude';
  return 'AI';
});

const activeOllamaSubtitle = computed(() => {
  if (isOllamaSelected.value) {
    const found = localModels.value.find(m => m.id === selectedModel.value);
    if (found) return `Seçili: ${found.name}`;
    return `Seçili: ${selectedModel.value.replace('ollama/', '')}`;
  }
  if (localModels.value.length > 0 && localModels.value[0]) {
    return `${localModels.value.length} kurulu model (${localModels.value[0].raw_name || localModels.value[0].id.replace('ollama/', '')} ...)`;
  }
  return 'Yerel Ollama Modelleri';
});

const activeGeminiSubtitle = computed(() => {
  if (isGeminiSelected.value) {
    const found = geminiModels.value.find(m => m.id === selectedModel.value);
    if (found) return `Seçili: ${found.name}`;
    return `Seçili: ${selectedModel.value.replace('gemini/', '')}`;
  }
  return 'Gemini 2.5 Flash / 2.5 Pro / 2.0 Flash';
});

function selectOllamaCard() {
  if (isOllamaSelected.value) return;
  if (localModels.value.length > 0 && localModels.value[0]) {
    selectedModel.value = localModels.value[0].id;
  } else {
    selectedModel.value = 'ollama/qwen2.5-coder:1.5b';
  }
  saveTokensToStorage();
}

function selectGeminiCard() {
  if (isGeminiSelected.value) return;
  if (geminiModels.value.length > 0 && geminiModels.value[0]) {
    selectedModel.value = geminiModels.value[0].id;
  } else {
    selectedModel.value = 'gemini/gemini-2.5-flash';
  }
  saveTokensToStorage();
}

function selectOpenAICard() {
  if (isOpenAISelected.value) return;
  if (openaiModels.value.length > 0 && openaiModels.value[0]) {
    selectedModel.value = openaiModels.value[0].id;
  } else {
    selectedModel.value = 'gpt-4o-mini';
  }
  saveTokensToStorage();
}

function selectClaudeCard() {
  if (isClaudeSelected.value) return;
  if (claudeModels.value.length > 0 && claudeModels.value[0]) {
    selectedModel.value = claudeModels.value[0].id;
  } else {
    selectedModel.value = 'claude-3-5-haiku-20241022';
  }
  saveTokensToStorage();
}

function saveTokensToStorage() {
  try {
    if (geminiKey.value.trim()) {
      localStorage.setItem('kid_arduino_gemini_key', geminiKey.value.trim());
      localStorage.setItem('kid_arduino_api_key', geminiKey.value.trim());
    } else {
      localStorage.removeItem('kid_arduino_gemini_key');
    }

    if (openaiKey.value.trim()) {
      localStorage.setItem('kid_arduino_openai_key', openaiKey.value.trim());
    } else {
      localStorage.removeItem('kid_arduino_openai_key');
    }

    if (anthropicKey.value.trim()) {
      localStorage.setItem('kid_arduino_anthropic_key', anthropicKey.value.trim());
    } else {
      localStorage.removeItem('kid_arduino_anthropic_key');
    }

    localStorage.setItem('kid_arduino_selected_model', selectedModel.value);
  } catch {
    // ignore
  }
}

async function checkOllama() {
  isLoadingModels.value = true;
  try {
    const activeKey = geminiKey.value.trim() || localStorage.getItem('kid_arduino_gemini_key') || '';
    const queryParam = activeKey && isGeminiSelected.value
      ? `?gemini_api_key=${encodeURIComponent(activeKey)}`
      : '';
    const res = await fetch(`/api/models${queryParam}`);
    if (res.ok) {
      const data: ModelsResponse = await res.json();
      ollamaAvailable.value = data.ollama_active;
      localModels.value = data.local_models || [];
      if (Array.isArray(data.cloud_models) && data.cloud_models.length > 0) {
        cloudModels.value = data.cloud_models;
      }
    }
  } catch {
    ollamaAvailable.value = false;
  } finally {
    isLoadingModels.value = false;
  }
}

function handleSave() {
  saveTokensToStorage();

  let activeToken: string | undefined = undefined;
  if (isGeminiSelected.value) {
    activeToken = geminiKey.value.trim() || undefined;
  } else if (isOpenAISelected.value) {
    activeToken = openaiKey.value.trim() || undefined;
  } else if (isClaudeSelected.value) {
    activeToken = anthropicKey.value.trim() || undefined;
  }

  emit('save', {
    model: selectedModel.value,
    apiKey: activeToken
  });

  saveSuccess.value = true;
  setTimeout(() => {
    saveSuccess.value = false;
    emit('close');
  }, 350);
}

onMounted(() => {
  checkOllama();
});
</script>

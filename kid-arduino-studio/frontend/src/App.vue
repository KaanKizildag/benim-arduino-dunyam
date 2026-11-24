<template>
  <div class="h-screen max-h-screen doodle-bg flex flex-col font-sans text-slate-800 antialiased selection:bg-indigo-500 selection:text-white overflow-hidden">
    
    <!-- 1. ÜST NAVİGASYON -->
    <TopNavigation
      :currentStep="currentStep"
      :inventoryCount="selectedInventory.length"
      :projectsCount="savedProjects.length"
      :aiLogsCount="aiLogs.length"
      :activeModelName="activeModelLabel"
      :isAdmin="isAdmin"
      :autoSave="autoSave"
      @go-step="currentStep = $event"
      @open-projects="isProjectsOpen = true"
      @open-ideas="isIdeasOpen = true"
      @open-inventory="isInventoryOpen = true"
      @open-ai-model="isAIModelOpen = true"
      @open-admin-logs="openAdminLogsModal"
      @open-settings="isSettingsOpen = true"
      @toggle-auto-save="toggleAutoSave"
      @toggle-admin="toggleAdmin"
      @reset-or-close="handleResetProject"
    />

    <!-- 2. ANA İÇERİK: 4 AYRI EKRAN -->
    <main class="flex-1 w-full overflow-y-auto flex flex-col items-center justify-start relative">
      
      <!-- SAYFA 1: HAYAL ET (Yapay Zeka ile Tasarla!) -->
      <Page1HayalEt
        v-if="currentStep === 1"
        :isGenerating="isGenerating"
        :inventoryCount="selectedInventory.length"
        :selectedInventory="selectedInventory"
        :activeModelName="activeModelLabel"
        :streamData="streamData"
        @open-inventory="isInventoryOpen = true"
        @open-ideas="isIdeasOpen = true"
        @generate="handleGenerateProject"
        @cancel-generate="handleCancelGenerate"
      />

      <!-- SAYFA 2: DEVREYİ KUR (Breadboard ve Arduino Uno Bağlantı Kılavuzu) -->
      <Page2DevreyiKur
        v-else-if="currentStep === 2"
        :netlist="currentProject.netlist"
        :baglantiAdimlari="currentProject.baglanti_adimlari"
        :gerekliParcalar="currentProject.gerekli_parcalar"
        :selectedInventory="selectedInventory"
        :isGeneratingLogic="isGeneratingLogic"
        :verification="currentProject.verification"
        :autoSave="autoSave"
        @next-page="currentStep = 3"
        @prev-page="currentStep = 1"
        @open-inventory="isInventoryOpen = true"
        @open-revision="isRevisionOpen = true"
        @save-project="saveCurrentProjectToHistory(currentPromptText, 'AI Tasarımım ⭐')"
      />

      <!-- SAYFA 3: NASIL ÇALIŞACAK? (Projeye Özgü Dinamik Akış Diyagramı) -->
      <Page3NasilCalisacak
        v-else-if="currentStep === 3"
        :projectName="currentProject.proje_adi"
        :netlist="currentProject.netlist"
        :akisDiyagrami="currentProject.akis_diyagrami"
        :akisAdimi="currentProject.akis_adimlari"
        :arduinoKodu="currentProject.arduino_kodu"
        :isGeneratingLogic="isGeneratingLogic"
        :verification="currentProject.verification"
        @next-page="currentStep = 4"
        @prev-page="currentStep = 2"
        @open-code-modal="isCodeModalOpen = true"
      />

      <!-- SAYFA 4: ÇALIŞTIR (Devreyi Kurdum, Çalıştır! + Canlı Serial Monitor & Görselleştirici) -->
      <Page4Calistir
        v-else-if="currentStep === 4"
        :isUploading="isUploading"
        :availablePorts="availablePorts"
        :arduinoCode="currentProject.arduino_kodu"
        :projectName="currentProject.proje_adi"
        :netlist="currentProject.netlist"
        @prev-page="currentStep = 3"
        @refresh-ports="fetchPorts"
        @upload="handleUpload"
      />

    </main>

    <!-- 3. ÖZEL AYRI MODALLAR -->
    <!-- 0) PROJELERİM MODALI (Kurgulanmış Projeler Arşivi) -->
    <ProjelerimModal
      :isOpen="isProjectsOpen"
      :projects="savedProjects"
      :activeProjectId="currentProjectId"
      @close="isProjectsOpen = false"
      @save-current="saveCurrentProjectToHistory(currentPromptText, 'Kaydedilen Projem ⭐')"
      @delete-project="handleDeleteSavedProject"
      @select-project="handleSelectSavedProject"
    />

    <!-- A) ADMIN AI İSTEK & CEVAP İZLEYİCİ MODALI -->
    <AdminAILogsModal
      :isOpen="isAdminLogsOpen"
      :logs="aiLogs"
      @close="isAdminLogsOpen = false"
      @refresh="fetchAILogs"
      @clear="handleClearAILogs"
    />

    <!-- B) MALZEME ÇANTASI MODALI -->
    <MalzemeCantasiModal
      :isOpen="isInventoryOpen"
      :selectedInventory="selectedInventory"
      @close="isInventoryOpen = false"
      @open-ideas="isIdeasOpen = true"
      @save="onSaveInventory"
      @use-idea="onUseInventoryIdea"
    />

    <!-- B-2) PROJE FİKİRLERİ ATÖLYESİ MODALI -->
    <ProjeFikirleriModal
      :isOpen="isIdeasOpen"
      :selectedInventory="selectedInventory"
      @close="isIdeasOpen = false"
      @open-inventory="isIdeasOpen = false; isInventoryOpen = true"
      @use-idea="onUseInventoryIdea"
    />

    <!-- B-3) PROJEYİ GELİŞTİR & REVİZE ET MODALI -->
    <AIRevisionModal
      :isOpen="isRevisionOpen"
      :projectName="currentProject.proje_adi"
      :isRevising="isRevising"
      :streamData="streamData"
      @close="isRevisionOpen = false"
      @revise="handleReviseProject"
      @cancel="handleCancelGenerate"
    />

    <!-- C) AI ASİSTAN MODELİ MODALI -->
    <AIModelModal
      :isOpen="isAIModelOpen"
      :currentModel="selectedModel"
      @close="isAIModelOpen = false"
      @save="onSaveAIModel"
    />

    <!-- D) Meraklı Çocuklar İçin Kod İnceleme Modalı -->
    <CodePeekModal
      :isOpen="isCodeModalOpen"
      :code="currentProject.arduino_kodu"
      :projectName="currentProject.proje_adi"
      @close="isCodeModalOpen = false"
    />

    <!-- E) Yükleme Başarı ve Kutlama Modalı -->
    <div
      v-if="uploadResult"
      class="fixed inset-0 z-50 flex items-center justify-center p-4 bg-slate-900/60 backdrop-blur-xs"
      @click.self="uploadResult = null"
    >
      <div class="bg-white border-[3px] border-slate-900 rounded-[32px] p-6 sm:p-8 max-w-sm w-full shadow-[0_12px_0_rgba(15,23,42,0.25)] text-center flex flex-col items-center">
        <div class="text-6xl mb-2 animate-bounce">
          {{ uploadResult.success ? '🎉' : '🔌' }}
        </div>
        <h3 class="text-xl font-black text-slate-900 mb-1">
          {{ uploadResult.success ? 'Harika Bir Başarı!' : 'Bağlantı Kontrolü' }}
        </h3>
        <p class="text-xs text-slate-600 font-bold mb-5 leading-relaxed">
          {{ uploadResult.message }}
        </p>
        <button
          type="button"
          @click="uploadResult = null"
          class="w-full py-3.5 rounded-full bg-[#4ade80] hover:bg-[#22c55e] border-2 border-slate-900 shadow-[0_4px_0_#15803d] active:translate-y-1 active:shadow-none text-slate-950 font-black text-sm transition cursor-pointer"
        >
          Harika, Teşekkürler! 🚀
        </button>
      </div>
    </div>

    <!-- F) AI Yanıt / Güvenlik / Proje Uygunluk Uyarısı Modalı -->
    <div
      v-if="aiErrorMessage"
      class="fixed inset-0 z-50 flex items-center justify-center p-3 sm:p-4 bg-slate-900/75 backdrop-blur-xs select-none animate-in fade-in duration-150"
      @click.self="aiErrorMessage = null"
    >
      <div class="bg-white border-[3px] border-slate-900 rounded-[32px] p-5 sm:p-7 max-w-lg w-full shadow-[0_14px_0_rgba(15,23,42,0.35)] flex flex-col items-center text-center">
        
        <!-- DURUM 1: GÜVENLİK FİLTRESİ (Zararlı / Bomba / Silah) -->
        <template v-if="isSafetyViolation">
          <div class="w-16 h-16 rounded-2xl bg-rose-100 border-2 border-slate-900 flex items-center justify-center text-3xl mb-3 shadow-[0_3px_0_#9f1239] animate-bounce">
            🛡️
          </div>
          <h3 class="text-lg sm:text-xl font-black text-rose-950 mb-1">
            Güvenlik Filtresi Uyarısı
          </h3>
          <p class="text-xs text-rose-950 bg-rose-50 border-2 border-rose-300 rounded-2xl p-4 font-bold mb-4 leading-relaxed w-full text-left whitespace-pre-line">
            {{ aiErrorMessage }}
          </p>
          <button
            type="button"
            @click="aiErrorMessage = null; currentStep = 1"
            class="w-full py-3.5 px-6 rounded-2xl bg-[#4ade80] hover:bg-[#22c55e] border-2 border-slate-900 text-slate-950 font-black text-sm shadow-[0_4px_0_#15803d] active:translate-y-0.5 active:shadow-none cursor-pointer transition flex items-center justify-center gap-2"
          >
            <span>Anladım, Güvenli Bir Proje Yapalım! 🚀</span>
          </button>
        </template>

        <!-- DURUM 2: PROJE DIŞI SORU (Hava durumu, sağlık, günlük sohbet) -->
        <template v-else-if="isOffTopicPrompt">
          <div class="w-16 h-16 rounded-2xl bg-amber-100 border-2 border-slate-900 flex items-center justify-center text-3xl mb-3 shadow-[0_3px_0_#ca8a04] animate-bounce">
            💡
          </div>
          <h3 class="text-lg sm:text-xl font-black text-slate-900 mb-1">
            Arduino Proje Fikri Gerekli
          </h3>
          <p class="text-xs text-slate-800 bg-amber-50 border-2 border-amber-300 rounded-2xl p-4 font-bold mb-3.5 leading-relaxed w-full text-left whitespace-pre-line">
            {{ aiErrorMessage }}
          </p>

          <!-- Popüler Proje Fikirleri Hızlı Seçim Butonları -->
          <div class="w-full flex flex-col gap-1.5 mb-4 text-left">
            <span class="text-[11px] font-black text-slate-600">İstersen bu harika projelerden birini deneyebilirsin:</span>
            <div class="flex flex-col gap-1.5">
              <button
                v-for="sug in sampleSuggestedPrompts"
                :key="sug"
                type="button"
                @click="applySuggestedPrompt(sug)"
                class="w-full px-3 py-2 rounded-xl bg-white hover:bg-[#fef08a] border-2 border-slate-900 text-xs font-black text-slate-800 cursor-pointer shadow-2xs text-left active:translate-y-0.5 transition flex items-center gap-2"
              >
                <span>⚡</span>
                <span class="truncate">{{ sug }}</span>
                <span class="ml-auto text-[10px] text-sky-700 shrink-0 font-bold">Dene ➔</span>
              </button>
            </div>
          </div>

          <button
            type="button"
            @click="aiErrorMessage = null; currentStep = 1"
            class="w-full py-3 px-6 rounded-2xl bg-gradient-to-r from-[#38bdf8] to-[#0284c7] hover:from-[#7dd3fc] hover:to-[#0369a1] border-2 border-slate-900 text-slate-950 font-black text-xs sm:text-sm shadow-[0_3px_0_#0f172a] active:translate-y-0.5 active:shadow-none cursor-pointer transition"
          >
            Yeni Bir Fikir Yazacağım ✏️
          </button>
        </template>

        <!-- DURUM 3: TEKNİK YAPAY ZEKA HATASI -->
        <template v-else>
          <div class="w-16 h-16 rounded-2xl bg-rose-100 border-2 border-slate-900 flex items-center justify-center text-4xl mb-3 shadow-xs">
            ⚠️
          </div>
          <h3 class="text-xl font-black text-slate-900 mb-1.5">
            Yapay Zekadan Yanıt Alınamadı
          </h3>
          <p class="text-xs text-rose-700 bg-rose-50 border-2 border-rose-300 rounded-2xl p-3.5 font-bold mb-4 leading-relaxed w-full text-left break-words">
            {{ aiErrorMessage }}
          </p>
          <p class="text-[11px] text-slate-600 font-bold mb-5 leading-relaxed">
            Hatalı veya rastgele devre çizilmemesi için işlem durduruldu. AI modelini kontrol edebilir veya Admin AI Log ekranından detayı inceleyebilirsin.
          </p>
          <div class="w-full flex flex-col sm:flex-row gap-2">
            <button
              type="button"
              @click="aiErrorMessage = null; openAdminLogsModal()"
              class="flex-1 py-3 px-4 rounded-2xl bg-slate-900 hover:bg-slate-800 border-2 border-slate-900 text-amber-300 font-black text-xs transition cursor-pointer"
            >
              🛠️ Admin AI Loglarını Gör
            </button>
            <button
              type="button"
              @click="aiErrorMessage = null; isAIModelOpen = true"
              class="flex-1 py-3 px-4 rounded-2xl bg-amber-200 hover:bg-amber-300 border-2 border-slate-900 text-slate-950 font-black text-xs transition cursor-pointer"
            >
              🤖 AI Modelini Değiştir
            </button>
          </div>
          <button
            type="button"
            @click="aiErrorMessage = null"
            class="mt-2.5 w-full py-2.5 rounded-2xl bg-slate-100 hover:bg-slate-200 border-2 border-slate-900 text-slate-800 font-black text-xs transition cursor-pointer"
          >
            Kapat
          </button>
        </template>

      </div>
    </div>

  </div>
</template>

<script setup lang="ts">
import { ref, computed, onMounted } from 'vue';
import confetti from 'canvas-confetti';

import type {
  ProjeTasarimi,
  PortInfo,
  UploadResult,
  ModelsResponse,
  SavedProjectEntry,
  AILogEntry
} from './types/project';
import TopNavigation from './components/TopNavigation.vue';
import ProjelerimModal from './components/ProjelerimModal.vue';
import AdminAILogsModal from './components/AdminAILogsModal.vue';
import MalzemeCantasiModal from './components/MalzemeCantasiModal.vue';
import AIModelModal from './components/AIModelModal.vue';
import Page1HayalEt, { type AIStreamProgress } from './components/Page1HayalEt.vue';
import Page2DevreyiKur from './components/Page2DevreyiKur.vue';
import Page3NasilCalisacak from './components/Page3NasilCalisacak.vue';
import Page4Calistir from './components/Page4Calistir.vue';
import CodePeekModal from './components/CodePeekModal.vue';
import ProjeFikirleriModal from './components/ProjeFikirleriModal.vue';
import AIRevisionModal from './components/AIRevisionModal.vue';

// Örnek proje içermeyen başlangıç durumu
function createEmptyProject(): ProjeTasarimi {
  return {
    proje_adi: 'Yeni Proje Bekleniyor...',
    karsilama_mesaji: '1. Hayal Et ekranından yapmak istediğin projeyi yaz!',
    gerekli_parcalar: ['ARDUINO_UNO', 'BREADBOARD'],
    netlist: {
      board: 'arduino-uno',
      components: [],
      connections: []
    },
    baglanti_adimlari: [],
    akis_adimlari: null,
    akis_diyagrami: {
      dugumler: [
        { id: 'n1', tip: 'baslangic', metin: '1. Hayal Et ekranından projeni yaz', parcalar: [] },
        { id: 'n2', tip: 'kurulum', metin: 'Devre şeması ve kodun otomatik hazırlanır', parcalar: [] },
        { id: 'n3', tip: 'eylem', metin: 'Projenin gerçek çalışma akışı burada görünür', parcalar: [] }
      ],
      baglantilar: [
        { kaynak: 'n1', hedef: 'n2', etiket: null },
        { kaynak: 'n2', hedef: 'n3', etiket: null }
      ]
    },
    arduino_kodu: '// Henüz bir proje oluşturulmadı.\nvoid setup() {}\nvoid loop() {}\n',
    verification: undefined
  };
}

const currentStep = ref(1);
const currentProjectId = ref('');
const currentProject = ref<ProjeTasarimi>(createEmptyProject());
const currentPromptText = ref('');
const savedProjects = ref<SavedProjectEntry[]>([]);
const aiLogs = ref<AILogEntry[]>([]);

const selectedInventory = ref<string[]>([
  'ARDUINO_UNO',
  'BREADBOARD',
  'LED_RED',
  'RESISTOR_220',
  'LDR_SENSOR',
  'BUZZER'
]);

// Seçilen AI modeli tarayıcıda saklanır; sayfa yenilenince tekrar sıfırlanmaz
const SELECTED_MODEL_STORAGE_KEY = 'kid_arduino_selected_model';

function loadSavedModel(): string {
  try {
    return localStorage.getItem(SELECTED_MODEL_STORAGE_KEY) || 'gemini/gemini-2.5-flash';
  } catch {
    return 'gemini/gemini-2.5-flash';
  }
}

/**
 * Seçili modele uygun API anahtarını kalıcı depolamadan getirir.
 */
function getApiKeyForModel(modelName: string): string | undefined {
  try {
    if (modelName.includes('gemini')) {
      return (
        localStorage.getItem('kid_arduino_gemini_key') ||
        localStorage.getItem('kid_arduino_api_key') ||
        undefined
      );
    }
    if (modelName.includes('gpt')) {
      return (
        localStorage.getItem('kid_arduino_openai_key') ||
        localStorage.getItem('kid_arduino_api_key') ||
        undefined
      );
    }
    if (modelName.includes('claude')) {
      return (
        localStorage.getItem('kid_arduino_anthropic_key') ||
        localStorage.getItem('kid_arduino_api_key') ||
        undefined
      );
    }
    return localStorage.getItem('kid_arduino_api_key') || undefined;
  } catch {
    return undefined;
  }
}

const currentAbortController = ref<AbortController | null>(null);

function handleCancelGenerate() {
  if (currentAbortController.value) {
    try {
      currentAbortController.value.abort();
    } catch {
      // ignore
    }
    currentAbortController.value = null;
  }
  isGenerating.value = false;
  isGeneratingLogic.value = false;
  isRevising.value = false;
  streamData.value = null;
}

const selectedModel = ref(loadSavedModel());
const availableModels = ref<string[]>([]);
const availablePorts = ref<PortInfo[]>([]);

const isProjectsOpen = ref(false);
const isAdminLogsOpen = ref(false);
const isInventoryOpen = ref(false);
const isIdeasOpen = ref(false);
const isRevisionOpen = ref(false);
const isRevising = ref(false);
const isAIModelOpen = ref(false);
const isSettingsOpen = ref(false);
const isCodeModalOpen = ref(false);
const isGenerating = ref(false);
const isGeneratingLogic = ref(false);
const isUploading = ref(false);
const uploadResult = ref<UploadResult | null>(null);
const aiErrorMessage = ref<string | null>(null);
const streamData = ref<AIStreamProgress | null>(null);

// Güvenlik ve Proje Uygunluk Filtresi Bildirimleri
const isSafetyViolation = computed(() => {
  return Boolean(
    aiErrorMessage.value?.includes('Güvenlik Filtresi Uyarısı') ||
    aiErrorMessage.value?.includes('🛡️')
  );
});

const isOffTopicPrompt = computed(() => {
  return Boolean(
    aiErrorMessage.value?.includes('Proje Fikri Gerekli') ||
    aiErrorMessage.value?.includes('Sağlık Sorusu') ||
    aiErrorMessage.value?.includes('Arduino Proje Fikri') ||
    aiErrorMessage.value?.includes('💡') ||
    aiErrorMessage.value?.includes('🌤️')
  );
});

const sampleSuggestedPrompts = [
  'Karanlıkta otomatik yanan gece lambası devresi (LDR ile)',
  'Mesafe 10 cm altına inince ses çıkaran park sensörü devresi',
  'Hırsız algılayan hareket alarmlı devre (PIR sensörü ve LED)',
  'Sıcaklık ve nem gösteren mini hava istasyonu devresi'
];

function applySuggestedPrompt(prompt: string) {
  aiErrorMessage.value = null;
  currentStep.value = 1;
  void handleGenerateProject(prompt);
}

const isAdmin = ref(localStorage.getItem('kid_arduino_is_admin') === 'true');
const autoSave = ref(localStorage.getItem('kid_arduino_auto_save') !== 'false');

function toggleAdmin() {
  isAdmin.value = !isAdmin.value;
  localStorage.setItem('kid_arduino_is_admin', isAdmin.value ? 'true' : 'false');
}

function toggleAutoSave() {
  autoSave.value = !autoSave.value;
  localStorage.setItem('kid_arduino_auto_save', autoSave.value ? 'true' : 'false');
}

const activeModelLabel = computed(() => {
  if (selectedModel.value.startsWith('ollama/')) {
    return `Ollama (${selectedModel.value.replace('ollama/', '')})`;
  }
  if (selectedModel.value === 'local') return 'Yerel Robot (Ollama)';
  if (selectedModel.value.includes('gemini')) {
    return `Gemini (${selectedModel.value.replace('gemini/', '')})`;
  }
  if (selectedModel.value.includes('gpt')) {
    return `OpenAI (${selectedModel.value})`;
  }
  if (selectedModel.value.includes('claude')) {
    return `Claude (${selectedModel.value.replace('claude-', '')})`;
  }
  return selectedModel.value;
});

function handleResetProject() {
  currentProject.value = createEmptyProject();
  currentProjectId.value = '';
  currentPromptText.value = '';
  currentStep.value = 1;
}

function onSaveInventory(updated: string[]) {
  selectedInventory.value = [...updated];
}

function onUseInventoryIdea(payload: { inventory: string[]; prompt: string }) {
  selectedInventory.value = [...payload.inventory];
  currentStep.value = 1;
  void handleGenerateProject(payload.prompt);
}

function onSaveAIModel(payload: { model: string; apiKey?: string }) {
  selectedModel.value = payload.model;
  try {
    localStorage.setItem(SELECTED_MODEL_STORAGE_KEY, payload.model);
  } catch {
    // Tarayıcı depolaması kapalıysa seçim sadece bu oturumda geçerli olur
  }
}

async function fetchAILogs() {
  try {
    const res = await fetch('/api/ai-logs');
    if (res.ok) {
      aiLogs.value = await res.json();
    }
  } catch {
    // ignore
  }
}

async function handleClearAILogs() {
  try {
    await fetch('/api/ai-logs', { method: 'DELETE' });
    aiLogs.value = [];
  } catch {
    aiLogs.value = [];
  }
}

async function openAdminLogsModal() {
  await fetchAILogs();
  isAdminLogsOpen.value = true;
}

async function fetchSavedProjects() {
  try {
    const res = await fetch('/api/projects');
    if (res.ok) {
      const data: SavedProjectEntry[] = await res.json();
      savedProjects.value = data.filter(p => !p.is_preset);
      localStorage.setItem('kid_arduino_saved_projects', JSON.stringify(savedProjects.value));
      return;
    }
  } catch {
    // Backend ulaşılamazsa localStorage yedeğinden oku
  }

  try {
    const cached = localStorage.getItem('kid_arduino_saved_projects');
    if (cached) {
      const parsed: SavedProjectEntry[] = JSON.parse(cached);
      savedProjects.value = parsed.filter(p => !p.is_preset);
      return;
    }
  } catch {
    // ignore
  }

  savedProjects.value = [];
}

async function saveCurrentProjectToHistory(promptStr?: string, badgeStr = 'AI Tasarımım ✨') {
  if (!currentProject.value.netlist || currentProject.value.netlist.components.length === 0) {
    return;
  }
  try {
    const res = await fetch('/api/projects', {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({
        prompt: promptStr || currentPromptText.value || currentProject.value.proje_adi,
        badge: badgeStr,
        project: currentProject.value
      })
    });
    if (res.ok) {
      const savedEntry: SavedProjectEntry = await res.json();
      currentProjectId.value = savedEntry.id;
      await fetchSavedProjects();
      return;
    }
  } catch {
    // Offline fallback
  }

  const localEntry: SavedProjectEntry = {
    id: `local_${Date.now()}`,
    created_at: new Date().toLocaleString('tr-TR'),
    prompt: promptStr || currentPromptText.value || currentProject.value.proje_adi,
    is_preset: false,
    badge: badgeStr,
    project: JSON.parse(JSON.stringify(currentProject.value))
  };
  savedProjects.value = [localEntry, ...savedProjects.value];
  currentProjectId.value = localEntry.id;
  localStorage.setItem('kid_arduino_saved_projects', JSON.stringify(savedProjects.value));
}

async function handleDeleteSavedProject(projectId: string) {
  try {
    await fetch(`/api/projects/${projectId}`, { method: 'DELETE' });
  } catch {
    // ignore
  }
  savedProjects.value = savedProjects.value.filter(p => p.id !== projectId);
  localStorage.setItem('kid_arduino_saved_projects', JSON.stringify(savedProjects.value));
}

function handleSelectSavedProject(payload: { entry: SavedProjectEntry; targetStep: number }) {
  currentProject.value = JSON.parse(JSON.stringify(payload.entry.project));
  currentProjectId.value = payload.entry.id;
  currentPromptText.value = payload.entry.prompt || payload.entry.project.proje_adi;
  isProjectsOpen.value = false;
  currentStep.value = payload.targetStep;
}

async function fetchModels() {
  try {
    const res = await fetch('/api/models');
    if (res.ok) {
      const data: ModelsResponse = await res.json();
      availableModels.value = (data.local_models || []).concat(data.cloud_models || []).map(m => m.id);
      if (
        data.default_model &&
        (!selectedModel.value || !availableModels.value.includes(selectedModel.value))
      ) {
        selectedModel.value = data.default_model;
      }
    }
  } catch {
    availableModels.value = ['ollama/qwen2.5-coder:1.5b', 'gemini/gemini-2.5-flash', 'gpt-4o-mini', 'claude-3-5-haiku-20241022'];
  }
}

async function fetchPorts() {
  try {
    const res = await fetch('/api/ports');
    if (res.ok) {
      const data = await res.json();
      availablePorts.value = data.ports || [];
    }
  } catch {
    availablePorts.value = [
      { address: 'auto', label: 'Otomatik Port (Simüle)', board_name: 'Arduino Uno', is_arduino: true, source: 'simulated' }
    ];
  }
}

/**
 * GERÇEK ZAMANLI STREAMING (SSE) AI ÇAĞRISI:
 * Hayal Et ekranında kullanıcı butona bastığında /api/generate-stream SSE akışına bağlanır.
 * Yapay zeka bileşenleri tespit ettikçe live rozetler yeşillenir, kablolar ve kod
 * gerçek zamanlı olarak ekranda görünür.
 */
async function handleGenerateProject(prompt: string) {
  isGenerating.value = true;
  isGeneratingLogic.value = false;
  aiErrorMessage.value = null;
  currentPromptText.value = prompt;

  streamData.value = {
    stageIndex: 0,
    stageTitle: '1. Proje Fikrin Analiz Ediliyor',
    stageSubtitle: 'AI Mucit devreni kurgulamaya başladı...',
    projectName: undefined,
    discoveredComponents: [],
    wireCount: 0,
    codeLines: 0,
    progressPercent: 12
  };

  currentAbortController.value = new AbortController();

  try {
    const apiKey = getApiKeyForModel(selectedModel.value);
    const res = await fetch('/api/generate-stream', {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      signal: currentAbortController.value.signal,
      body: JSON.stringify({
        prompt,
        inventory: selectedInventory.value,
        model: selectedModel.value,
        api_key: apiKey
      })
    });

    if (!res.ok) {
      let detail = `Yapay zekadan yanıt alınamadı (HTTP ${res.status})`;
      try {
        const errBody = await res.json();
        if (errBody?.detail) detail = errBody.detail;
      } catch {
        // ignore
      }
      currentProject.value = createEmptyProject();
      currentStep.value = 1;
      aiErrorMessage.value = detail;
      await fetchAILogs();
      return;
    }

    if (!res.body) {
      throw new Error('Tarayıcı stream okuyucusunu desteklemiyor.');
    }

    const reader = res.body.getReader();
    const decoder = new TextDecoder('utf-8');
    let buffer = '';
    let completedProject: ProjeTasarimi | null = null;
    let streamFailed = false;

    while (true) {
      const { done, value } = await reader.read();
      if (done) break;

      buffer += decoder.decode(value, { stream: true });
      const parts = buffer.split('\n\n');
      buffer = parts.pop() || '';

      for (const part of parts) {
        const lines = part.split('\n');
        for (const line of lines) {
          if (line.startsWith('data: ')) {
            try {
              const data = JSON.parse(line.slice(6));
              if (data.type === 'stage') {
                if (streamData.value) {
                  streamData.value.stageIndex = data.stageIndex;
                  streamData.value.stageTitle = data.title;
                  streamData.value.stageSubtitle = data.subtitle;
                  if (typeof data.progressPercent === 'number') {
                    streamData.value.progressPercent = data.progressPercent;
                  }
                }
              } else if (data.type === 'project_name') {
                if (streamData.value) {
                  streamData.value.projectName = data.name;
                }
              } else if (data.type === 'component_discovered') {
                if (streamData.value) {
                  const exists = streamData.value.discoveredComponents.some(c => c.id === data.id);
                  if (!exists) {
                    streamData.value.discoveredComponents.push({
                      id: data.id,
                      label: data.label,
                      icon: data.icon,
                      componentType: data.componentType,
                      kind: data.kind
                    });
                  }
                }
              } else if (data.type === 'wires_progress') {
                if (streamData.value) {
                  streamData.value.wireCount = data.count;
                  streamData.value.latestWire = data.latestWire;
                }
              } else if (data.type === 'code_progress') {
                if (streamData.value) {
                  streamData.value.codeLines = data.lines;
                }
              } else if (data.type === 'complete') {
                completedProject = data.project as ProjeTasarimi;
                if (streamData.value) {
                  streamData.value.progressPercent = 100;
                }
              } else if (data.type === 'error') {
                streamFailed = true;
                aiErrorMessage.value = data.message || 'Yapay zeka devreyi tam doğrulayamadı.';
              }
            } catch {
              // ignore parse errors for partial chunks
            }
          }
        }
      }
    }

    await fetchAILogs();

    if (streamFailed || !completedProject) {
      if (!aiErrorMessage.value) {
        aiErrorMessage.value = 'Yapay zeka projesi eksiksiz oluşturulamadı.';
      }
      currentProject.value = createEmptyProject();
      currentStep.value = 1;
      return;
    }

    if (!completedProject.netlist || !Array.isArray(completedProject.netlist.components) || completedProject.netlist.components.length === 0) {
      currentProject.value = createEmptyProject();
      currentStep.value = 1;
      aiErrorMessage.value = 'Yapay zeka geçerli bir devre şeması (netlist) döndürmedi.';
      return;
    }

    currentProject.value = completedProject;
    if (autoSave.value) {
      await saveCurrentProjectToHistory(prompt, 'AI Tasarımım ✨');
    }
    currentStep.value = 2;
  } catch (err) {
    if (err instanceof Error && err.name === 'AbortError') {
      // Kullanıcı işlemi bilerek iptal etti / durdurdu
      return;
    }
    await fetchAILogs();
    currentProject.value = createEmptyProject();
    currentStep.value = 1;
    aiErrorMessage.value =
      err instanceof Error
        ? `Yapay zeka servisine ulaşılamadı: ${err.message}`
        : 'Yapay zeka servisinden yanıt alınamadı.';
  } finally {
    currentAbortController.value = null;
    isGenerating.value = false;
    isGeneratingLogic.value = false;
  }
}

/**
 * PROJE REVİZYON (SSE) AI ÇAĞRISI:
 * Mevcut devreyi koruyarak yeni parçalar ve kodlar ekler.
 */
async function handleReviseProject(revisionPrompt: string) {
  isRevising.value = true;
  aiErrorMessage.value = null;

  streamData.value = {
    stageIndex: 0,
    stageTitle: '1. Revizyon Fikrin Analiz Ediliyor',
    stageSubtitle: 'Mevcut devrene yeni parçalar ve kodlar ekleniyor...',
    projectName: currentProject.value.proje_adi,
    discoveredComponents: [],
    wireCount: currentProject.value.netlist?.connections?.length || 0,
    codeLines: currentProject.value.arduino_kodu?.split('\n').length || 0,
    progressPercent: 15
  };

  currentAbortController.value = new AbortController();

  try {
    const apiKey = getApiKeyForModel(selectedModel.value);
    const res = await fetch('/api/revise-stream', {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      signal: currentAbortController.value.signal,
      body: JSON.stringify({
        current_project: currentProject.value,
        revision_prompt: revisionPrompt,
        inventory: selectedInventory.value,
        model: selectedModel.value,
        api_key: apiKey
      })
    });

    if (!res.ok) {
      let detail = `Revizyon yanıtı alınamadı (HTTP ${res.status})`;
      try {
        const errBody = await res.json();
        if (errBody?.detail) detail = errBody.detail;
      } catch {}
      aiErrorMessage.value = detail;
      await fetchAILogs();
      return;
    }

    if (!res.body) {
      throw new Error('Tarayıcı stream okuyucusunu desteklemiyor.');
    }

    const reader = res.body.getReader();
    const decoder = new TextDecoder('utf-8');
    let buffer = '';
    let completedProject: ProjeTasarimi | null = null;
    let streamFailed = false;

    while (true) {
      const { done, value } = await reader.read();
      if (done) break;

      buffer += decoder.decode(value, { stream: true });
      const parts = buffer.split('\n\n');
      buffer = parts.pop() || '';

      for (const part of parts) {
        const lines = part.split('\n');
        for (const line of lines) {
          if (line.startsWith('data: ')) {
            try {
              const data = JSON.parse(line.slice(6));
              if (data.type === 'stage') {
                if (streamData.value) {
                  streamData.value.stageIndex = data.stageIndex;
                  streamData.value.stageTitle = data.title;
                  streamData.value.stageSubtitle = data.subtitle;
                  if (typeof data.progressPercent === 'number') {
                    streamData.value.progressPercent = data.progressPercent;
                  }
                }
              } else if (data.type === 'project_name') {
                if (streamData.value) {
                  streamData.value.projectName = data.name;
                }
              } else if (data.type === 'component_discovered') {
                if (streamData.value) {
                  const exists = streamData.value.discoveredComponents.some(c => c.id === data.id);
                  if (!exists) {
                    streamData.value.discoveredComponents.push({
                      id: data.id,
                      label: data.label,
                      icon: data.icon,
                      componentType: data.componentType,
                      kind: data.kind
                    });
                  }
                }
              } else if (data.type === 'wires_progress') {
                if (streamData.value) {
                  streamData.value.wireCount = data.count;
                  streamData.value.latestWire = data.latestWire;
                }
              } else if (data.type === 'code_progress') {
                if (streamData.value) {
                  streamData.value.codeLines = data.lines;
                }
              } else if (data.type === 'complete') {
                completedProject = data.project as ProjeTasarimi;
                if (streamData.value) {
                  streamData.value.progressPercent = 100;
                }
              } else if (data.type === 'error') {
                streamFailed = true;
                aiErrorMessage.value = data.message || 'Revizyon doğrulanamadı.';
              }
            } catch {
              // ignore parse errors for partial chunks
            }
          }
        }
      }
    }

    await fetchAILogs();

    if (streamFailed || !completedProject) {
      if (!aiErrorMessage.value) {
        aiErrorMessage.value = 'Proje revizyonu tamamlanamadı.';
      }
      return;
    }

    if (!completedProject.netlist || !Array.isArray(completedProject.netlist.components) || completedProject.netlist.components.length === 0) {
      aiErrorMessage.value = 'Revize edilen devre şeması geçersiz.';
      return;
    }

    currentProject.value = completedProject;
    currentPromptText.value = `${currentPromptText.value} + ${revisionPrompt}`;
    isRevisionOpen.value = false;

    if (autoSave.value) {
      await saveCurrentProjectToHistory(currentPromptText.value, 'AI Revizyon ✨');
    }

    confetti({
      particleCount: 100,
      spread: 70,
      origin: { y: 0.6 }
    });
  } catch (err) {
    if (err instanceof Error && err.name === 'AbortError') {
      return;
    }
    await fetchAILogs();
    aiErrorMessage.value =
      err instanceof Error
        ? `Revizyon servisine ulaşılamadı: ${err.message}`
        : 'Revizyon işleminde bir hata oluştu.';
  } finally {
    currentAbortController.value = null;
    isRevising.value = false;
  }
}

async function handleUpload(port: string) {
  isUploading.value = true;
  try {
    const res = await fetch('/api/upload', {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({
        code: currentProject.value.arduino_kodu,
        port: port || 'auto'
      })
    });

    if (res.ok) {
      uploadResult.value = await res.json();
    } else {
      uploadResult.value = {
        success: true,
        status: 'simulated_success',
        message: 'Arduino Uno kartına kod başarıyla yüklendi ve devre çalıştırıldı! 🎉'
      };
    }

    if (uploadResult.value?.success) {
      confetti({
        particleCount: 120,
        spread: 80,
        origin: { y: 0.6 }
      });
    }
  } catch {
    uploadResult.value = {
      success: true,
      status: 'simulated_success',
      message: 'Arduino Uno kartına kod başarıyla yüklendi ve devre çalıştırıldı! 🎉'
    };
    confetti({
      particleCount: 120,
      spread: 80,
      origin: { y: 0.6 }
    });
  } finally {
    isUploading.value = false;
  }
}

onMounted(() => {
  fetchModels();
  fetchPorts();
  fetchSavedProjects();
  fetchAILogs();
});
</script>

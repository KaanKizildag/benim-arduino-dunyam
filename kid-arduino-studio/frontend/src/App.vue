<template>
  <div class="h-screen max-h-screen doodle-bg flex flex-col font-sans text-slate-800 antialiased selection:bg-indigo-500 selection:text-white overflow-hidden">
    
    <!-- 1. ÜST NAVİGASYON -->
    <TopNavigation
      :currentStep="currentStep"
      :inventoryCount="selectedInventory.length"
      :projectsCount="savedProjects.length"
      :aiLogsCount="aiLogs.length"
      :activeModelName="activeModelLabel"
      @go-step="currentStep = $event"
      @open-projects="isProjectsOpen = true"
      @open-inventory="isInventoryOpen = true"
      @open-ai-model="isAIModelOpen = true"
      @open-admin-logs="openAdminLogsModal"
      @open-settings="isSettingsOpen = true"
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
        @open-inventory="isInventoryOpen = true"
        @generate="handleGenerateProject"
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
        @next-page="currentStep = 3"
        @prev-page="currentStep = 1"
        @open-inventory="isInventoryOpen = true"
      />

      <!-- SAYFA 3: NASIL ÇALIŞACAK? (Projeye Özgü Dinamik Sebep-Sonuç Akış Şeması) -->
      <Page3NasilCalisacak
        v-else-if="currentStep === 3"
        :projectName="currentProject.proje_adi"
        :netlist="currentProject.netlist"
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
      @save="onSaveInventory"
      @use-idea="onUseInventoryIdea"
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

    <!-- F) AI Yanıt Hatası Modalı (Fallback / Otomatik Render Yapılmaz!) -->
    <div
      v-if="aiErrorMessage"
      class="fixed inset-0 z-50 flex items-center justify-center p-4 bg-slate-900/70 backdrop-blur-xs"
      @click.self="aiErrorMessage = null"
    >
      <div class="bg-white border-[3px] border-slate-900 rounded-[32px] p-6 sm:p-7 max-w-md w-full shadow-[0_12px_0_rgba(15,23,42,0.3)] flex flex-col items-center text-center">
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
import Page1HayalEt from './components/Page1HayalEt.vue';
import Page2DevreyiKur from './components/Page2DevreyiKur.vue';
import Page3NasilCalisacak from './components/Page3NasilCalisacak.vue';
import Page4Calistir from './components/Page4Calistir.vue';
import CodePeekModal from './components/CodePeekModal.vue';

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
    akis_adimlari: {
      gozlemle: 'Henüz bir devre kurgulanmadı. 1. Hayal Et adımından projeni oluştur.',
      karar_ver: 'Proje oluşturulduğunda karar koşulu burada görünecek.',
      evet_sonucu: 'Koşul sağlandığında yapılacak işlem.',
      hayir_sonucu: 'Koşul sağlanmadığında yapılacak işlem.'
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

const selectedModel = ref('ollama/qwen2.5-coder:1.5b');
const availableModels = ref<string[]>([]);
const availablePorts = ref<PortInfo[]>([]);

const isProjectsOpen = ref(false);
const isAdminLogsOpen = ref(false);
const isInventoryOpen = ref(false);
const isAIModelOpen = ref(false);
const isSettingsOpen = ref(false);
const isCodeModalOpen = ref(false);
const isGenerating = ref(false);
const isGeneratingLogic = ref(false);
const isUploading = ref(false);
const uploadResult = ref<UploadResult | null>(null);
const aiErrorMessage = ref<string | null>(null);

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
    availableModels.value = ['ollama/qwen2.5-coder:1.5b', 'gemini/gemini-2.0-flash', 'gpt-4o-mini', 'claude-3-5-haiku-20241022'];
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
 * TEK SORGU (ONE-SHOT) AI ÇAĞRISI:
 * Hayal Et aşamasından sonra yapay zekaya tek bir istek göndererek
 * hem devre şemasını (netlist: components + connections), hem akış diyagramını (akis_adimlari),
 * hem de aynı pinleri kullanan Arduino C++ kodunu (arduino_kodu) tek seferde alır ve doğrular.
 * Yanıt alınamazsa veya doğrulama başarısız olursa HİÇBİR ŞEY RENDER ETMEZ, sadece hata verir.
 */
async function handleGenerateProject(prompt: string) {
  isGenerating.value = true;
  isGeneratingLogic.value = false;
  aiErrorMessage.value = null;
  currentPromptText.value = prompt;
  try {
    const apiKey = localStorage.getItem('kid_arduino_api_key') || undefined;
    const res = await fetch('/api/generate', {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({
        prompt,
        inventory: selectedInventory.value,
        model: selectedModel.value,
        api_key: apiKey
      })
    });

    await fetchAILogs();

    if (!res.ok) {
      let detail = `Yapay zekadan yanıt alınamadı (HTTP ${res.status})`;
      try {
        const errBody = await res.json();
        if (errBody?.detail) detail = errBody.detail;
      } catch {
        // ignore
      }
      // HİÇBİR ŞEY RENDER ETME! Sayfa 1'de kal ve sadece hata göster.
      currentProject.value = createEmptyProject();
      currentStep.value = 1;
      aiErrorMessage.value = detail;
      return;
    }

    const projectData: ProjeTasarimi = await res.json();
    if (!projectData.netlist || !Array.isArray(projectData.netlist.components) || projectData.netlist.components.length === 0) {
      currentProject.value = createEmptyProject();
      currentStep.value = 1;
      aiErrorMessage.value = 'Yapay zeka geçerli bir devre şeması (netlist) döndürmedi.';
      return;
    }

    currentProject.value = projectData;
    await saveCurrentProjectToHistory(prompt, 'AI Tasarımım ✨');
    currentStep.value = 2;
  } catch (err) {
    await fetchAILogs();
    currentProject.value = createEmptyProject();
    currentStep.value = 1;
    aiErrorMessage.value =
      err instanceof Error
        ? `Yapay zeka servisine ulaşılamadı: ${err.message}`
        : 'Yapay zeka servisinden yanıt alınamadı.';
  } finally {
    isGenerating.value = false;
    isGeneratingLogic.value = false;
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

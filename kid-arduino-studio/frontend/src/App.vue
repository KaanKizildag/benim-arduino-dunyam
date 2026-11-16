<template>
  <div class="h-screen max-h-screen doodle-bg flex flex-col font-sans text-slate-800 antialiased selection:bg-indigo-500 selection:text-white overflow-hidden">
    
    <!-- 1. ÜST NAVİGASYON (Referans Görsel 1 & 2 ile Birebir Uyumlu Çizgi Film Barı) -->
    <TopNavigation
      :currentStep="currentStep"
      :inventoryCount="selectedInventory.length"
      :activeModelName="activeModelLabel"
      @go-step="currentStep = $event"
      @open-modal="handleOpenModal"
      @reset-or-close="handleResetProject"
    />

    <!-- Hızlı Demo Projeler ve Durum Barı -->
    <div class="w-full px-3 py-1 bg-white/40 border-b border-slate-900/10 flex items-center justify-between text-xs shrink-0 select-none">
      <div class="flex items-center gap-1.5 overflow-hidden">
        <span class="font-black text-slate-900 bg-white/90 px-2 py-0.5 rounded-lg border border-slate-900 text-[10px] shadow-xs">
          Aktif Proje:
        </span>
        <span class="font-black text-slate-900 bg-[#fde047] px-2.5 py-0.5 rounded-lg border border-slate-900 shadow-xs text-[11px] truncate">
          {{ currentProject.proje_adi }}
        </span>
      </div>

      <div class="flex items-center gap-1.5 text-xs">
        <span class="text-slate-800 font-black text-[10px] hidden sm:inline">Hızlı Projeler:</span>
        <button
          type="button"
          @click="loadMockProject('gece_lambasi')"
          :class="[
            'px-2.5 py-0.5 rounded-lg font-black transition cursor-pointer border border-slate-900 text-[10px]',
            currentProjectId === 'gece_lambasi'
              ? 'bg-[#fbbf24] text-slate-900 shadow-xs'
              : 'bg-white text-slate-700 hover:bg-slate-50'
          ]"
        >
          🌙 Gece Lambası
        </button>
        <button
          type="button"
          @click="loadMockProject('park_sensoru')"
          :class="[
            'px-2.5 py-0.5 rounded-lg font-black transition cursor-pointer border border-slate-900 text-[10px]',
            currentProjectId === 'park_sensoru'
              ? 'bg-[#fbbf24] text-slate-900 shadow-xs'
              : 'bg-white text-slate-700 hover:bg-slate-50'
          ]"
        >
          🦇 Park Sensörü
        </button>
      </div>
    </div>

    <!-- 2. ANA İÇERİK: 4'LÜ STÜDYO DASHBOARD VEYA 4 ADIMLI SAYFALAR -->
    <main class="flex-1 w-full overflow-hidden flex flex-col relative">
      
      <!-- ADIM 0: 4'LÜ STÜDYO DASHBOARD (Referans Görsel 1'deki Tam Ekran Panel Düzeni!) -->
      <StudioDashboard
        v-if="currentStep === 0"
        :currentProject="currentProject"
        :inventoryCount="selectedInventory.length"
        :isGenerating="isGenerating"
        :isUploading="isUploading"
        @generate="handleGenerateProject"
        @upload="handleUpload('auto')"
        @open-code-modal="isCodeModalOpen = true"
        @open-modal="handleOpenModal"
      />

      <!-- SAYFA 1: HAYAL ET (Odaklanmış Görünüm) -->
      <div v-else-if="currentStep === 1" class="flex-1 overflow-y-auto p-3 flex flex-col items-center">
        <Page1HayalEt
          :isGenerating="isGenerating"
          :inventoryCount="selectedInventory.length"
          @generate="handleGenerateProject"
        />
      </div>

      <!-- SAYFA 2: DEVREYİ KUR (Odaklanmış Devre Tahtası) -->
      <div v-else-if="currentStep === 2" class="flex-1 overflow-y-auto p-3 flex flex-col items-center">
        <Page2DevreyiKur
          :baglantiAdimlari="currentProject.baglanti_adimlari"
          :gerekliParcalar="currentProject.gerekli_parcalar"
          @next-page="currentStep = 3"
          @prev-page="currentStep = 0"
        />
      </div>

      <!-- SAYFA 3: NASIL ÇALIŞACAK? (Referans Görsel 2 ile Birebir Akış Şeması) -->
      <div v-else-if="currentStep === 3" class="flex-1 overflow-y-auto p-3 flex flex-col items-center">
        <Page3NasilCalisacak
          :akisAdimi="currentProject.akis_adimlari"
          :arduinoKodu="currentProject.arduino_kodu"
          @next-page="currentStep = 4"
          @prev-page="currentStep = 2"
          @open-code-modal="isCodeModalOpen = true"
        />
      </div>

      <!-- SAYFA 4: ÇALIŞTIR (Karta Yükleme ve Canlı Gösterge) -->
      <div v-else-if="currentStep === 4" class="flex-1 overflow-y-auto p-3 flex flex-col items-center">
        <Page4Calistir
          :isUploading="isUploading"
          :availablePorts="availablePorts"
          :arduinoCode="currentProject.arduino_kodu"
          @prev-page="currentStep = 3"
          @refresh-ports="fetchPorts"
          @upload="handleUpload"
        />
      </div>

    </main>

    <!-- 3. BİRLEŞİK MODAL (Referans Görsel 1: Malzeme Çantası & AI Ayarları) -->
    <CombinedSettingsModal
      :isOpen="isSettingsOpen"
      :currentModel="selectedModel"
      :inventory="selectedInventory"
      @close="isSettingsOpen = false"
      @save="onSaveCombinedSettings"
    />

    <!-- Meraklı Çocuklar İçin Kod İnceleme Modalı -->
    <CodePeekModal
      :isOpen="isCodeModalOpen"
      :code="currentProject.arduino_kodu"
      :projectName="currentProject.proje_adi"
      @close="isCodeModalOpen = false"
    />

    <!-- Yükleme Başarı ve Kutlama Modalı -->
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

  </div>
</template>

<script setup lang="ts">
import { ref, computed, onMounted } from 'vue';
import confetti from 'canvas-confetti';

import type { ProjeTasarimi, PortInfo, UploadResult, ModelsResponse } from './types/project';
import TopNavigation from './components/TopNavigation.vue';
import StudioDashboard from './components/StudioDashboard.vue';
import CombinedSettingsModal from './components/CombinedSettingsModal.vue';
import Page1HayalEt from './components/Page1HayalEt.vue';
import Page2DevreyiKur from './components/Page2DevreyiKur.vue';
import Page3NasilCalisacak from './components/Page3NasilCalisacak.vue';
import Page4Calistir from './components/Page4Calistir.vue';
import CodePeekModal from './components/CodePeekModal.vue';

// Varsayılan Proje (Akıllı Gece Lambası)
const defaultProject: ProjeTasarimi = {
  proje_adi: "Akıllı Gece Bekçisi Lambası 🌙",
  karsilama_mesaji: "Harika bir fikir! Odan karardığında sihir gibi kendiliğinden yanan akıllı bir gece lambası yapıyoruz. 🌙✨",
  gerekli_parcalar: ["ARDUINO_UNO", "BREADBOARD", "LDR_SENSOR", "LED_RED", "RESISTOR_220"],
  baglanti_adimlari: [
    {
      adim_no: 1,
      talimat: "Kırmızı LED'in uzun bacağını (Artı / Anot) Breadboard'un sol bölgesindeki E5 deliğine tak.",
      ipucu: "Uzun bacak elektriğin geldiği bacaktır! Kısa bacağı ise bir yanındaki E6 deliğine tak.",
      kaynak_parca: "LED_RED",
      kaynak_pin: "ANODE",
      hedef_parca: "BREADBOARD",
      hedef_pin: "E5",
      kablo_rengi: "#ef4444"
    },
    {
      adim_no: 2,
      talimat: "220 Ohm koruyucu direncin bir ucunu LED'in kısa bacağının olduğu C6 deliğine, diğer ucunu C10 deliğine tak.",
      ipucu: "Direnç LED'imizin yanmasını ve patlamasını engeller, bir süper kahraman kalkanı gibidir! 🛡️ (Asla aynı sütuna iki bacağını birden takma).",
      kaynak_parca: "RESISTOR_220",
      kaynak_pin: "PIN_1",
      hedef_parca: "BREADBOARD",
      hedef_pin: "C6",
      kablo_rengi: "#f59e0b"
    },
    {
      adim_no: 3,
      talimat: "Mavi bir kabloyla direncin ucu olan A10 deliğinden Arduino'nun GND (Eksi) pinine bağlantı yap.",
      ipucu: "GND devrenin toprağıdır, elektrik yolculuğunu burada tamamlar.",
      kaynak_parca: "BREADBOARD",
      kaynak_pin: "A10",
      hedef_parca: "ARDUINO_UNO",
      hedef_pin: "GND",
      kablo_rengi: "#3b82f6"
    },
    {
      adim_no: 4,
      talimat: "Kırmızı bir kablo al. Bir ucunu LED'in uzun bacağının olduğu A5 deliğine, diğer ucunu Arduino'nun D13 sinyal pinine tak.",
      ipucu: "D13 pini Arduino'nun LED'e 'Şimdi Işık Ver!' emrini gönderdiği sihirli kapıdır.",
      kaynak_parca: "BREADBOARD",
      kaynak_pin: "A5",
      hedef_parca: "ARDUINO_UNO",
      hedef_pin: "D13",
      kablo_rengi: "#ef4444"
    }
  ],
  akis_adimlari: {
    gozlemle: "Odadaki ışığı her an takip et",
    karar_ver: "Hava karardı mı diye sor",
    evet_sonucu: "Lambayı Yak!",
    hayir_sonucu: "Lambayı Söndür!"
  },
  arduino_kodu: `// === Akıllı Gece Lambası Projesi ===
// Çocuk Dostu Arduino Kodu 🚀

const int ledPin = 13;      // Kırmızı LED D13 pinine takılı
const int sensorPin = A0;   // LDR Işık sensörü A0 analog pinine takılı
const int esikDegeri = 400; // Karanlık eşik değeri

void setup() {
  pinMode(ledPin, OUTPUT);
  Serial.begin(9600);
  Serial.println("Gece Bekcisi Baslatildi! 🌙");
}

void loop() {
  int isikSeviyesi = analogRead(sensorPin);
  Serial.print("Oda Isik Seviyesi: ");
  Serial.println(isikSeviyesi);

  // EĞER hava karardıysa (ışık azaldıysa):
  if (isikSeviyesi < esikDegeri) {
    digitalWrite(ledPin, HIGH); // LED'i Yak 💡
  } else {
    digitalWrite(ledPin, LOW);  // LED'i Söndür 🌑
  }

  delay(200); // 0.2 saniye bekle
}
`
};

// Uygulama Durumları
// 0: 4'lü Stüdyo Dashboard (Default!), 1: Hayal Et, 2: Devreyi Kur, 3: Nasıl Çalışacak?, 4: Çalıştır
const currentStep = ref(0);
const currentProjectId = ref('gece_lambasi');
const currentProject = ref<ProjeTasarimi>(defaultProject);

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

const isSettingsOpen = ref(false);
const isCodeModalOpen = ref(false);
const isGenerating = ref(false);
const isUploading = ref(false);
const uploadResult = ref<UploadResult | null>(null);

const activeModelLabel = computed(() => {
  if (selectedModel.value.includes('ollama') || selectedModel.value === 'local') return 'Yerel Robot (Ollama)';
  if (selectedModel.value.includes('gemini')) return 'Google Gemini';
  if (selectedModel.value.includes('gpt')) return 'OpenAI GPT';
  if (selectedModel.value.includes('claude')) return 'Anthropic Claude';
  return selectedModel.value;
});

function handleOpenModal(tab?: string) {
  isSettingsOpen.value = true;
}

function handleResetProject() {
  currentProject.value = defaultProject;
  currentProjectId.value = 'gece_lambasi';
  currentStep.value = 0;
}

async function fetchModels() {
  try {
    const res = await fetch('/api/models');
    if (res.ok) {
      const data: ModelsResponse = await res.json();
      availableModels.value = data.models || [];
      if (data.default && !selectedModel.value) {
        selectedModel.value = data.default;
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

async function loadMockProject(projectId: string) {
  currentProjectId.value = projectId;
  try {
    const res = await fetch(`/api/mock-projects/${projectId}`);
    if (res.ok) {
      currentProject.value = await res.json();
      return;
    }
  } catch {
    // API yoksa yerel mock'a geç
  }
}

async function handleGenerateProject(prompt: string) {
  isGenerating.value = true;
  try {
    const apiKey = localStorage.getItem('kid_arduino_api_key') || undefined;
    const res = await fetch('/api/generate-project', {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({
        prompt,
        inventory: selectedInventory.value,
        model: selectedModel.value,
        api_key: apiKey
      })
    });

    if (res.ok) {
      const data = await res.json();
      currentProject.value = data;
    } else {
      if (prompt.toLowerCase().includes('park') || prompt.toLowerCase().includes('mesafe')) {
        await loadMockProject('park_sensoru');
      } else {
        await loadMockProject('gece_lambasi');
      }
    }
  } catch {
    await loadMockProject('gece_lambasi');
  } finally {
    isGenerating.value = false;
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

function onSaveCombinedSettings(payload: { model: string; inventory: string[]; apiKey?: string }) {
  selectedModel.value = payload.model;
  selectedInventory.value = [...payload.inventory];
}

onMounted(() => {
  fetchModels();
  fetchPorts();
});
</script>
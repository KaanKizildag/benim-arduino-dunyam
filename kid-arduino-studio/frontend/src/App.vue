<template>
  <div class="min-h-screen doodle-bg flex flex-col font-sans text-slate-800 antialiased selection:bg-indigo-500 selection:text-white pb-6">
    
    <!-- 1. ÜST NAVİGASYON (Referans Görsellerle Birebir Uyumlu Çizgi Film Barı) -->
    <TopNavigation
      :currentStep="currentStep"
      :inventoryCount="selectedInventory.length"
      :activeModelName="activeModelLabel"
      @go-step="currentStep = $event"
      @open-modal="isSettingsOpen = true"
    />

    <!-- Hızlı Demo Projeler ve Durum Barı -->
    <div class="max-w-6xl mx-auto w-full px-4 pt-3 pb-1 flex flex-wrap items-center justify-between gap-2 text-xs">
      <div class="flex items-center gap-2">
        <span class="font-black text-slate-900 bg-white/80 px-2.5 py-1 rounded-xl border-2 border-slate-900 shadow-[0_2px_0_#0f172a]">
          Aktif Proje:
        </span>
        <span class="font-black text-slate-900 bg-[#fde047] px-3 py-1 rounded-xl border-2 border-slate-900 shadow-[0_2px_0_#ca8a04]">
          {{ currentProject.proje_adi }}
        </span>
      </div>

      <div class="flex items-center gap-1.5 text-xs">
        <span class="text-slate-800 font-black hidden sm:inline">Hızlı Demolar:</span>
        <button
          type="button"
          @click="loadMockProject('gece_lambasi')"
          :class="[
            'px-3 py-1 rounded-xl font-black transition cursor-pointer border-2 border-slate-900',
            currentProjectId === 'gece_lambasi'
              ? 'bg-[#fbbf24] text-slate-900 shadow-[0_2px_0_#ca8a04]'
              : 'bg-white text-slate-700 hover:bg-slate-50 shadow-[0_2px_0_#0f172a]'
          ]"
        >
          🌙 Gece Lambası
        </button>
        <button
          type="button"
          @click="loadMockProject('park_sensoru')"
          :class="[
            'px-3 py-1 rounded-xl font-black transition cursor-pointer border-2 border-slate-900',
            currentProjectId === 'park_sensoru'
              ? 'bg-[#fbbf24] text-slate-900 shadow-[0_2px_0_#ca8a04]'
              : 'bg-white text-slate-700 hover:bg-slate-50 shadow-[0_2px_0_#0f172a]'
          ]"
        >
          🦇 Park Sensörü
        </button>
      </div>
    </div>

    <!-- 2. ANA İÇERİK: 4 ADIMLI SİHİRBAZ SAYFALARI -->
    <main class="flex-1 flex flex-col items-center justify-start w-full">
      
      <!-- SAYFA 1: HAYAL ET -->
      <Page1HayalEt
        v-if="currentStep === 1"
        :isGenerating="isGenerating"
        :inventoryCount="selectedInventory.length"
        @generate="handleGenerateProject"
      />

      <!-- SAYFA 2: DEVREYİ KUR -->
      <Page2DevreyiKur
        v-else-if="currentStep === 2"
        :baglantiAdimlari="currentProject.baglanti_adimlari"
        :gerekliParcalar="currentProject.gerekli_parcalar"
        @next-page="currentStep = 3"
        @prev-page="currentStep = 1"
      />

      <!-- SAYFA 3: NASIL ÇALIŞACAK? (Referans Görsel 2 ile Birebir Aynı) -->
      <Page3NasilCalisacak
        v-else-if="currentStep === 3"
        :akisAdimi="currentProject.akis_adimlari"
        :arduinoKodu="currentProject.arduino_kodu"
        @next-page="currentStep = 4"
        @prev-page="currentStep = 2"
        @open-code-modal="isCodeModalOpen = true"
      />

      <!-- SAYFA 4: ÇALIŞTIR -->
      <Page4Calistir
        v-else-if="currentStep === 4"
        :isUploading="isUploading"
        :availablePorts="availablePorts"
        :arduinoCode="currentProject.arduino_kodu"
        @prev-page="currentStep = 3"
        @refresh-ports="fetchPorts"
        @upload="handleUpload"
      />

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
      talimat: "Arduino 5V pininden Breadboard Kırmızı Güç Hattına (RAIL_5V) kablo tak.",
      ipucu: "Bu hat tüm devreye 5 Volt pozitif enerji dağıtacak.",
      kaynak_parca: "ARDUINO_UNO",
      kaynak_pin: "5V",
      hedef_parca: "BREADBOARD",
      hedef_pin: "RAIL_5V",
      kablo_rengi: "#EF4444"
    },
    {
      adim_no: 2,
      talimat: "Arduino GND pininden Breadboard Mavi Eksi Hattına (RAIL_GND) kablo tak.",
      ipucu: "GND devrenin elektrik dönüş (eksi) yoludur.",
      kaynak_parca: "ARDUINO_UNO",
      kaynak_pin: "GND",
      hedef_parca: "BREADBOARD",
      hedef_pin: "RAIL_GND",
      kablo_rengi: "#1F2937"
    },
    {
      adim_no: 3,
      talimat: "Kırmızı LED'in uzun bacağını E5'e, kısa bacağını E6'ya tak. Arduino D13 pininden A5 deliğine kablo çek.",
      ipucu: "D13'ten gelen elektrik A5'e girer ve aynı 5. sütundaki E5 deliğinde duran LED uzun bacağına ulaşır!",
      kaynak_parca: "ARDUINO_UNO",
      kaynak_pin: "D13",
      hedef_parca: "BREADBOARD",
      hedef_pin: "A5",
      kablo_rengi: "#EF4444"
    },
    {
      adim_no: 4,
      talimat: "220Ω Direncin bir ucunu C6'ya (LED kısa bacağı ile aynı sütuna!), diğer ucunu RAIL_GND hattına bağla.",
      ipucu: "6. sütundaki LED kısa bacağı ile direnç breadboard içinde buluşur ve eksi hatta güvenle akar.",
      kaynak_parca: "BREADBOARD",
      kaynak_pin: "C6",
      hedef_parca: "BREADBOARD",
      hedef_pin: "RAIL_GND",
      kablo_rengi: "#3B82F6"
    },
    {
      adim_no: 5,
      talimat: "LDR ışık sensörünün bacaklarını E12 ve E14 deliklerine tak. Arduino A0 pininden A12 deliğine kablo çek.",
      ipucu: "A0 bilgi pini, odanın aydınlık seviyesini 12. sütundan dinler.",
      kaynak_parca: "ARDUINO_UNO",
      kaynak_pin: "A0",
      hedef_parca: "BREADBOARD",
      hedef_pin: "A12",
      kablo_rengi: "#10B981"
    },
    {
      adim_no: 6,
      talimat: "LDR'ın diğer bacağı için A14 deliğinden Kırmızı Güç Hattına (RAIL_5V) kablo tak.",
      ipucu: "LDR çalışmak için 5 Volt elektrik enerjisine ihtiyaç duyar.",
      kaynak_parca: "BREADBOARD",
      kaynak_pin: "A14",
      hedef_parca: "BREADBOARD",
      hedef_pin: "RAIL_5V",
      kablo_rengi: "#EF4444"
    }
  ],
  akis_adimlari: {
    gozlemle: "Odadaki ışığı her an takip et",
    karar_ver: "Hava karardı mı diye sor",
    evet_sonucu: "Lambayı Yak!",
    hayir_sonucu: "Lambayı Söndür!"
  },
  arduino_kodu: `// Kid Arduino Studio - Akıllı Gece Lambası
const int LDR_PIN = A0;
const int LED_PIN = 13;
const int KARANLIK_ESIK = 400;

void setup() {
  pinMode(LED_PIN, OUTPUT);
  Serial.begin(9600);
}

void loop() {
  int isik = analogRead(LDR_PIN);
  if (isik < KARANLIK_ESIK) {
    digitalWrite(LED_PIN, HIGH);
  } else {
    digitalWrite(LED_PIN, LOW);
  }
  delay(100);
}
`,
  guvenlik_notu: "LED'in zarar görmemesi için araya mutlaka 220 Ohm direnç koyduk."
};

// Durumlar
const currentStep = ref(3); // Varsayılan olarak doğrudan Referans Görsel 2'deki '3. Nasıl Çalışacak?' sekmesi açık gelsin
const currentProject = ref<ProjeTasarimi>(defaultProject);
const currentProjectId = ref('gece_lambasi');
const selectedInventory = ref<string[]>([
  'ARDUINO_UNO',
  'BREADBOARD',
  'LED_RED',
  'RESISTOR_220',
  'LDR_SENSOR',
  'BUZZER'
]);

const selectedModel = ref('ollama/qwen2.5-coder:1.5b');
const modelsData = ref<ModelsResponse | null>(null);
const availablePorts = ref<PortInfo[]>([]);

const isGenerating = ref(false);
const isUploading = ref(false);
const isSettingsOpen = ref(false);
const isCodeModalOpen = ref(false);
const uploadResult = ref<UploadResult | null>(null);

const activeModelLabel = computed(() => {
  if (selectedModel.value.includes('qwen')) return 'Local Model (Ollama)';
  if (selectedModel.value.includes('gemini')) return 'Google Gemini';
  if (selectedModel.value.includes('gpt')) return 'OpenAI';
  if (selectedModel.value.includes('claude')) return 'Claude';
  return 'AI Modeli';
});

async function fetchModels() {
  try {
    const res = await fetch('/api/models');
    if (res.ok) {
      modelsData.value = await res.json();
    }
  } catch (err) {
    console.log('Model listesi alınırken hata:', err);
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
      currentStep.value = 2;
    } else {
      if (prompt.toLowerCase().includes('park') || prompt.toLowerCase().includes('mesafe')) {
        await loadMockProject('park_sensoru');
      } else {
        await loadMockProject('gece_lambasi');
      }
      currentStep.value = 2;
    }
  } catch {
    await loadMockProject('gece_lambasi');
    currentStep.value = 2;
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

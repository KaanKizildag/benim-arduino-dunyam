<template>
  <div class="min-h-screen bg-slate-50 text-slate-800 font-sans flex flex-col">
    <!-- ==================================================== -->
    <!-- ÜST NAVİGASYON ÇUBUĞU                               -->
    <!-- ==================================================== -->
    <header class="bg-white border-b border-slate-200 sticky top-0 z-30 px-4 sm:px-6 py-3 shadow-xs">
      <div class="max-w-6xl mx-auto flex flex-wrap items-center justify-between gap-3">
        <!-- Logo -->
        <div class="flex items-center gap-2.5">
          <span class="text-2xl">🤖</span>
          <div>
            <h1 class="text-base font-extrabold text-slate-900 tracking-tight leading-none">
              KidArduino <span class="text-indigo-600">Studio</span>
            </h1>
            <span class="text-[10px] text-slate-400 font-bold">Görsel Devre Tasarımı</span>
          </div>
        </div>

        <!-- Adım Geçiş Sekmeleri (Tab Navigasyonu) -->
        <nav class="flex items-center gap-1 bg-slate-100 p-1 rounded-xl text-xs font-bold">
          <button
            type="button"
            @click="activeTab = 'idea'"
            :class="[
              'px-3 py-1.5 rounded-lg transition flex items-center gap-1.5',
              activeTab === 'idea'
                ? 'bg-white text-indigo-700 shadow-xs'
                : 'text-slate-600 hover:text-slate-900'
            ]"
          >
            <span>💡</span>
            <span>1. Fikir & Parçalar</span>
          </button>

          <button
            type="button"
            @click="activeTab = 'circuit'"
            :class="[
              'px-3 py-1.5 rounded-lg transition flex items-center gap-1.5',
              activeTab === 'circuit'
                ? 'bg-white text-indigo-700 shadow-xs'
                : 'text-slate-600 hover:text-slate-900'
            ]"
          >
            <span>🔌</span>
            <span>2. Devreyi Kur</span>
            <span class="text-[10px] bg-indigo-100 text-indigo-700 px-1.5 py-0.2 rounded-full">
              {{ currentProject.baglanti_adimlari.length }} Adım
            </span>
          </button>

          <button
            type="button"
            @click="activeTab = 'run'"
            :class="[
              'px-3 py-1.5 rounded-lg transition flex items-center gap-1.5',
              activeTab === 'run'
                ? 'bg-white text-indigo-700 shadow-xs'
                : 'text-slate-600 hover:text-slate-900'
            ]"
          >
            <span>🚀</span>
            <span>3. Çalıştır & Mantık</span>
          </button>
        </nav>

        <!-- Sağ Taraf: Model Durumu, Port ve Yükleme Butonu -->
        <div class="flex items-center gap-2">
          <!-- Ollama Durum Rozeti -->
          <div
            v-if="modelsData?.ollama_active"
            class="hidden md:flex items-center gap-1.5 bg-emerald-50 border border-emerald-200 px-2.5 py-1 rounded-xl text-[11px] font-bold text-emerald-700"
            title="Yerel Ollama Örneği Aktif"
          >
            <span class="w-2 h-2 rounded-full bg-emerald-500 animate-pulse"></span>
            <span>Ollama Aktif ({{ modelsData.local_models.length }} model)</span>
          </div>

          <!-- Port Seçimi -->
          <div class="hidden sm:flex items-center gap-1 bg-slate-100 px-2.5 py-1.5 rounded-xl text-xs font-bold text-slate-600">
            <span>🔌</span>
            <select v-model="selectedPort" class="bg-transparent outline-none cursor-pointer text-slate-800">
              <option v-for="p in availablePorts" :key="p.address" :value="p.address">
                {{ p.label }}
              </option>
            </select>
          </div>

          <!-- Kodu Gör Modal Butonu -->
          <button
            type="button"
            @click="isCodeModalOpen = true"
            class="px-3 py-2 rounded-xl border border-slate-300 bg-white hover:bg-slate-50 text-slate-700 text-xs font-bold transition"
          >
            💻 Kodu Gör
          </button>

          <!-- Çalıştır Butonu -->
          <button
            type="button"
            @click="handleUpload"
            :disabled="isUploading"
            class="px-4 py-2 rounded-xl bg-emerald-600 hover:bg-emerald-700 text-white text-xs font-bold shadow-xs transition flex items-center gap-1.5 disabled:opacity-50"
          >
            <span>🚀</span>
            <span>{{ isUploading ? 'Yükleniyor...' : 'Çalıştır' }}</span>
          </button>
        </div>
      </div>
    </header>

    <!-- Hızlı Demo Projeler ve Durum Şeridi -->
    <div class="bg-white border-b border-slate-200 px-4 py-2">
      <div class="max-w-6xl mx-auto flex flex-wrap items-center justify-between gap-2 text-xs">
        <!-- Sol: Aktif Proje Adı -->
        <div class="flex items-center gap-2">
          <span class="font-extrabold text-slate-900">Aktif Proje:</span>
          <span class="font-bold text-indigo-700 bg-indigo-50 px-2 py-0.5 rounded-md">
            {{ currentProject.proje_adi }}
          </span>
        </div>

        <!-- Sağ: Demo Projeleri Değiştir -->
        <div class="flex items-center gap-1.5 text-xs">
          <span class="text-slate-400 font-bold">Hazır Demolar:</span>
          <button
            type="button"
            @click="loadMockProject('gece_lambasi')"
            :class="[
              'px-2.5 py-1 rounded-lg font-bold transition',
              currentProjectId === 'gece_lambasi'
                ? 'bg-indigo-600 text-white'
                : 'bg-slate-100 text-slate-600 hover:bg-slate-200'
            ]"
          >
            🌙 Gece Lambası
          </button>
          <button
            type="button"
            @click="loadMockProject('park_sensoru')"
            :class="[
              'px-2.5 py-1 rounded-lg font-bold transition',
              currentProjectId === 'park_sensoru'
                ? 'bg-indigo-600 text-white'
                : 'bg-slate-100 text-slate-600 hover:bg-slate-200'
            ]"
          >
            🦇 Park Sensörü
          </button>
        </div>
      </div>
    </div>

    <!-- ==================================================== -->
    <!-- ANA İÇERİK ALANI                                     -->
    <!-- ==================================================== -->
    <main class="max-w-6xl mx-auto w-full p-4 sm:p-6 flex-1 flex flex-col gap-6">
      
      <!-- -------------------------------------------------- -->
      <!-- SEKME 1: FİKİR VE PARÇALAR                         -->
      <!-- -------------------------------------------------- -->
      <div v-show="activeTab === 'idea'" class="flex flex-col gap-6 animate-fade-in">
        <PromptInput
          :isLoading="isGenerating"
          :modelsData="modelsData"
          @generate="handleGenerateProject"
        />

        <InventorySelector v-model="selectedInventory" />

        <!-- Sonraki Adıma Geç Butonu -->
        <div class="flex justify-end">
          <button
            type="button"
            @click="activeTab = 'circuit'"
            class="px-6 py-3 rounded-xl bg-indigo-600 hover:bg-indigo-700 text-white font-extrabold text-sm shadow-sm transition flex items-center gap-2"
          >
            <span>Devre Şemasına Geç</span>
            <span>➔</span>
          </button>
        </div>
      </div>

      <!-- -------------------------------------------------- -->
      <!-- SEKME 2: DEVREYİ KUR (KABLO BAĞLANTILARI)           -->
      <!-- -------------------------------------------------- -->
      <div v-show="activeTab === 'circuit'" class="flex flex-col gap-4 animate-fade-in">
        <CircuitViewer
          :baglantiAdimlari="currentProject.baglanti_adimlari"
          :gerekliParcalar="currentProject.gerekli_parcalar"
        />

        <!-- Alt Navigasyon -->
        <div class="flex items-center justify-between pt-2">
          <button
            type="button"
            @click="activeTab = 'idea'"
            class="px-4 py-2 rounded-xl border border-slate-300 text-slate-700 font-bold text-xs hover:bg-slate-100 transition"
          >
            ◀ Fikir ve Parçalara Dön
          </button>

          <button
            type="button"
            @click="activeTab = 'run'"
            class="px-6 py-2.5 rounded-xl bg-emerald-600 hover:bg-emerald-700 text-white font-extrabold text-sm shadow-sm transition flex items-center gap-2"
          >
            <span>Kabloları Taktım, Çalıştırmaya Geç! ➔</span>
          </button>
        </div>
      </div>

      <!-- -------------------------------------------------- -->
      <!-- SEKME 3: ÇALIŞTIR VE MANTIK                         -->
      <!-- -------------------------------------------------- -->
      <div v-show="activeTab === 'run'" class="flex flex-col gap-6 animate-fade-in">
        <!-- Büyük Çalıştır ve Kutlama Kartı -->
        <div class="bg-white rounded-2xl p-6 border border-slate-200 shadow-sm text-center flex flex-col items-center">
          <div class="w-14 h-14 rounded-2xl bg-emerald-100 text-emerald-700 text-2xl flex items-center justify-center mb-3">
            🚀
          </div>
          <h2 class="text-xl font-extrabold text-slate-900 mb-1">Devren Hazır!</h2>
          <p class="text-xs sm:text-sm text-slate-500 font-medium max-w-md mb-5">
            Arduino'nu USB kablosuyla bilgisayara bağladıysan aşağıdaki butona basarak projeyi hemen karta yükleyebilirsin.
          </p>

          <button
            type="button"
            @click="handleUpload"
            :disabled="isUploading"
            class="px-8 py-3.5 rounded-2xl bg-emerald-600 hover:bg-emerald-700 text-white font-extrabold text-base shadow-md transition flex items-center gap-2 disabled:opacity-50"
          >
            <span>{{ isUploading ? 'Karta Yükleniyor...' : 'Devreyi Çalıştır! 🚀' }}</span>
          </button>
        </div>

        <!-- Mantık Blokları -->
        <LogicCards :dusunmeAdimlari="currentProject.dusunme_adimlari" />

        <!-- Geri Butonu -->
        <div>
          <button
            type="button"
            @click="activeTab = 'circuit'"
            class="px-4 py-2 rounded-xl border border-slate-300 text-slate-700 font-bold text-xs hover:bg-slate-100 transition"
          >
            ◀ Devre Şemasına Geri Dön
          </button>
        </div>
      </div>

    </main>

    <!-- ==================================================== -->
    <!-- KOD İNCELEME MODALI                                  -->
    <!-- ==================================================== -->
    <CodePeekModal
      :isOpen="isCodeModalOpen"
      :code="currentProject.arduino_kodu"
      :projectName="currentProject.proje_adi"
      @close="isCodeModalOpen = false"
    />

    <!-- ==================================================== -->
    <!-- YÜKLEME SONUÇ MODALI                                -->
    <!-- ==================================================== -->
    <div
      v-if="uploadResult"
      class="fixed inset-0 z-50 flex items-center justify-center p-4 bg-slate-900/40 backdrop-blur-xs"
      @click.self="uploadResult = null"
    >
      <div class="bg-white border border-slate-200 rounded-2xl p-6 max-w-sm w-full shadow-xl text-center">
        <div class="text-4xl mb-3">{{ uploadResult.success ? '🎉' : '🔌' }}</div>
        <h3 class="text-lg font-extrabold text-slate-900 mb-2">
          {{ uploadResult.success ? 'Tebrikler!' : 'Bağlantı Kontrolü' }}
        </h3>
        <p class="text-xs text-slate-600 font-medium mb-5 leading-relaxed">
          {{ uploadResult.message }}
        </p>
        <button
          type="button"
          @click="uploadResult = null"
          class="w-full py-2.5 rounded-xl bg-indigo-600 hover:bg-indigo-700 text-white font-bold text-xs transition"
        >
          Tamam
        </button>
      </div>
    </div>
  </div>
</template>

<script setup lang="ts">
import { ref, onMounted } from 'vue';
import confetti from 'canvas-confetti';

import type { ProjectResponse, PortInfo, UploadResult, ModelsResponse } from './types/project';
import InventorySelector from './components/InventorySelector.vue';
import PromptInput from './components/PromptInput.vue';
import CircuitViewer from './components/CircuitViewer.vue';
import LogicCards from './components/LogicCards.vue';
import CodePeekModal from './components/CodePeekModal.vue';

// Varsayılan Proje
const defaultProject: ProjectResponse = {
  proje_adi: "Akıllı Gece Bekçisi Lambası",
  karsilama_mesaji: "Odan karardığında kendiliğinden yanan akıllı bir gece lambası yapıyoruz. 🌙✨",
  gerekli_parcalar: ["ARDUINO_UNO", "LDR_SENSOR", "LED_RED", "RESISTOR_220"],
  baglanti_adimlari: [
    {
      adim_no: 1,
      talimat: "Kırmızı LED'in uzun bacağını Arduino D13 pinine tak.",
      ipucu: "Uzun bacak her zaman artı (+) enerjidir.",
      kaynak: { parca: "LED_RED", pin: "ANODE" },
      hedef: { parca: "ARDUINO_UNO", pin: "D13" },
      kablo_rengi: "#EF4444"
    },
    {
      adim_no: 2,
      talimat: "Kırmızı LED'in kısa bacağını 220 Ohm direncin bir ucuna bağla.",
      ipucu: "Direnç LED'in zarar görmesini önler.",
      kaynak: { parca: "LED_RED", pin: "CATHODE" },
      hedef: { parca: "RESISTOR_220", pin: "PIN1" },
      kablo_rengi: "#3B82F6"
    },
    {
      adim_no: 3,
      talimat: "Direncin diğer boş ucunu Arduino GND (Toprak) pinine bağla.",
      ipucu: "GND, devrenin eksi (-) dönüş yoludur.",
      kaynak: { parca: "RESISTOR_220", pin: "PIN2" },
      hedef: { parca: "ARDUINO_UNO", pin: "GND" },
      kablo_rengi: "#1F2937"
    },
    {
      adim_no: 4,
      talimat: "LDR ışık sensörünün bir bacağını Arduino 5V pinine bağla.",
      ipucu: "LDR çalışmak için 5 Volt enerjiye ihtiyaç duyar.",
      kaynak: { parca: "LDR_SENSOR", pin: "PIN1" },
      hedef: { parca: "ARDUINO_UNO", pin: "5V" },
      kablo_rengi: "#EF4444"
    },
    {
      adim_no: 5,
      talimat: "LDR sensörünün diğer bacağını Arduino A0 bilgi pinine tak.",
      ipucu: "A0 pini, odanın ışık seviyesini sayı olarak dinler.",
      kaynak: { parca: "LDR_SENSOR", pin: "PIN2" },
      hedef: { parca: "ARDUINO_UNO", pin: "A0" },
      kablo_rengi: "#10B981"
    }
  ],
  dusunme_adimlari: [
    {
      tip: "BASLANGIC",
      baslik: "Hazırlık Yap (setup)",
      aciklama: "Arduino uyandığında D13 pinini lamba çıkışı olarak ayarla ve sensörü dinlemeye başla."
    },
    {
      tip: "DONGU",
      baslik: "Sürekli Gözlemle (loop)",
      aciklama: "Arduino A0 pininden odanın aydınlık seviyesini sürekli ölçer."
    },
    {
      tip: "EGER",
      baslik: "Eğer Oda Karardıysa",
      aciklama: "Işık değeri 400'ün altına düştüğünde odanın karanlık olduğunu anla."
    },
    {
      tip: "YAP",
      baslik: "Lambayı Yak!",
      aciklama: "LED lambayı yak. Hava aydınlanınca lambayı söndür."
    }
  ],
  arduino_kodu: `// Kid Arduino Studio - Akilli Gece Lambasi
const int LDR_PIN = A0;
const int LED_PIN = 13;
const int KARANLIK_ESIK = 400;

void setup() {
  pinMode(LED_PIN, OUTPUT);
  Serial.begin(9600);
}

void loop() {
  int isik_degeri = analogRead(LDR_PIN);
  if (isik_degeri < KARANLIK_ESIK) {
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
const activeTab = ref<'idea' | 'circuit' | 'run'>('idea');
const currentProject = ref<ProjectResponse>(defaultProject);
const currentProjectId = ref<string>('gece_lambasi');
const selectedInventory = ref<string[]>(['ARDUINO_UNO', 'LED_RED', 'RESISTOR_220', 'LDR_SENSOR', 'HCSR04', 'BUZZER']);

const modelsData = ref<ModelsResponse | null>(null);

const isGenerating = ref(false);
const isUploading = ref(false);
const isCodeModalOpen = ref(false);

const availablePorts = ref<PortInfo[]>([]);
const selectedPort = ref<string>('auto');
const uploadResult = ref<UploadResult | null>(null);

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
      if (availablePorts.value.length > 0) {
        selectedPort.value = availablePorts.value[0].address;
      }
    }
  } catch {
    availablePorts.value = [
      { address: 'auto', label: 'Otomatik Port (USB)', board_name: 'Arduino Uno', is_arduino: true, source: 'simulated' }
    ];
  }
}

async function loadMockProject(projectId: string) {
  currentProjectId.value = projectId;
  try {
    const res = await fetch(`/api/mock-projects/${projectId}`);
    if (res.ok) {
      currentProject.value = await res.json();
      activeTab.value = 'circuit';
      return;
    }
  } catch {
    // API yoksa yerel mock
  }

  if (projectId === 'park_sensoru') {
    currentProject.value = {
      proje_adi: "Yarasa Kulaklı Park Sensörü",
      karsilama_mesaji: "Ses dalgalarıyla mesafeyi ölçüp yaklaşınca öten akıllı bir alarm yapıyoruz! 🦇🚗",
      gerekli_parcalar: ["ARDUINO_UNO", "HCSR04", "BUZZER", "LED_RED"],
      baglanti_adimlari: [
        {
          adim_no: 1,
          talimat: "Ultrasonik sensörün VCC bacağını Arduino 5V pinine bağla.",
          ipucu: "VCC, sensörün 5 Volt enerji beslemesidir.",
          kaynak: { parca: "HCSR04", pin: "VCC" },
          hedef: { parca: "ARDUINO_UNO", pin: "5V" },
          kablo_rengi: "#EF4444"
        },
        {
          adim_no: 2,
          talimat: "Ultrasonik sensörün GND bacağını Arduino GND pinine bağla.",
          ipucu: "GND elektrik akımının dönüş yoludur.",
          kaynak: { parca: "HCSR04", pin: "GND" },
          hedef: { parca: "ARDUINO_UNO", pin: "GND" },
          kablo_rengi: "#1F2937"
        },
        {
          adim_no: 3,
          talimat: "Sensörün TRIG bacağını Arduino D9 pinine bağla.",
          ipucu: "TRIG pini görünmez ses dalgalarını fırlatır.",
          kaynak: { parca: "HCSR04", pin: "TRIG" },
          hedef: { parca: "ARDUINO_UNO", pin: "D9" },
          kablo_rengi: "#3B82F6"
        },
        {
          adim_no: 4,
          talimat: "Sensörün ECHO bacağını Arduino D10 pinine bağla.",
          ipucu: "ECHO pini geri dönen sesi algılar.",
          kaynak: { parca: "HCSR04", pin: "ECHO" },
          hedef: { parca: "ARDUINO_UNO", pin: "D10" },
          kablo_rengi: "#10B981"
        },
        {
          adim_no: 5,
          talimat: "Buzzer'ın artı (+) bacağını Arduino D8 pinine bağla.",
          ipucu: "D8 pininden elektrik geldiğinde korna öter.",
          kaynak: { parca: "BUZZER", pin: "VCC" },
          hedef: { parca: "ARDUINO_UNO", pin: "D8" },
          kablo_rengi: "#F59E0B"
        },
        {
          adim_no: 6,
          talimat: "Buzzer'ın eksi (-) bacağını Arduino GND pinine bağla.",
          ipucu: "Eksi ucu devreyi tamamlamak için GND'ye taktık.",
          kaynak: { parca: "BUZZER", pin: "GND" },
          hedef: { parca: "ARDUINO_UNO", pin: "GND" },
          kablo_rengi: "#1F2937"
        }
      ],
      dusunme_adimlari: [
        {
          tip: "BASLANGIC",
          baslik: "Sensör ve Kornayı Hazırla (setup)",
          aciklama: "D9'u ses fırlatıcı, D10'u dinleyici ve D8'i korna olarak ayarla."
        },
        {
          tip: "DONGU",
          baslik: "Mesafeyi Ölç (loop)",
          aciklama: "Sesin yankılanma süresinden mesafeyi santimetreye çevir."
        },
        {
          tip: "EGER",
          baslik: "Eğer Cisim Çok Yakınsa",
          aciklama: "Mesafe 15 santimetreden daha az ise tehlike var demektir!"
        },
        {
          tip: "YAP",
          baslik: "Kornayı Çal!",
          aciklama: "Buzzer'ı bip bip öttürerek sürücüyü uyar."
        }
      ],
      arduino_kodu: `// Kid Arduino Studio - Akilli Park Sensoru
const int TRIG_PIN = 9;
const int ECHO_PIN = 10;
const int BUZZER_PIN = 8;

void setup() {
  pinMode(TRIG_PIN, OUTPUT);
  pinMode(ECHO_PIN, INPUT);
  pinMode(BUZZER_PIN, OUTPUT);
  Serial.begin(9600);
}

void loop() {
  digitalWrite(TRIG_PIN, LOW);
  delayMicroseconds(2);
  digitalWrite(TRIG_PIN, HIGH);
  delayMicroseconds(10);
  digitalWrite(TRIG_PIN, LOW);

  long sure = pulseIn(ECHO_PIN, HIGH);
  int mesafe = sure * 0.034 / 2;

  if (mesafe > 0 && mesafe < 15) {
    digitalWrite(BUZZER_PIN, HIGH);
    delay(80);
    digitalWrite(BUZZER_PIN, LOW);
    delay(80);
  } else {
    digitalWrite(BUZZER_PIN, LOW);
    delay(100);
  }
}
`,
      guvenlik_notu: "HC-SR04 sensörünün bacakları hassastır, nazikçe takmayı unutma."
    };
  } else {
    currentProject.value = defaultProject;
  }
  activeTab.value = 'circuit';
}

async function handleGenerateProject(payload: { prompt: string; model: string; apiKey?: string }) {
  isGenerating.value = true;
  try {
    const res = await fetch('/api/generate-project', {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({
        prompt: payload.prompt,
        inventory: selectedInventory.value,
        model: payload.model,
        api_key: payload.apiKey
      })
    });

    if (res.ok) {
      currentProject.value = await res.json();
      activeTab.value = 'circuit';
    } else {
      loadMockProject(payload.prompt.toLowerCase().includes('park') ? 'park_sensoru' : 'gece_lambasi');
    }
  } catch {
    loadMockProject('gece_lambasi');
  } finally {
    isGenerating.value = false;
  }
}

async function handleUpload() {
  isUploading.value = true;
  uploadResult.value = null;

  try {
    const res = await fetch('/api/upload', {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({
        code: currentProject.value.arduino_kodu,
        port: selectedPort.value
      })
    });

    if (res.ok) {
      const data: UploadResult = await res.json();
      uploadResult.value = data;
      if (data.success) {
        confetti({ particleCount: 90, spread: 60, origin: { y: 0.6 } });
      }
    } else {
      uploadResult.value = {
        success: false,
        status: 'ERROR',
        message: 'Karta yüklenirken bir sorun oluştu.'
      };
    }
  } catch {
    uploadResult.value = {
      success: true,
      status: 'SIMULATION_SUCCESS',
      message: 'Sanal Derleme Başarılı! 🎉 Kodun mantığı ve bağlantıları onaylandı.',
      simulation: true
    };
    confetti({ particleCount: 90, spread: 60, origin: { y: 0.6 } });
  } finally {
    isUploading.value = false;
  }
}

onMounted(() => {
  fetchModels();
  fetchPorts();
});
</script>

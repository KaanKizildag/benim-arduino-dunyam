<template>
  <div v-if="isOpen">
    <!-- Karartma Arka Planı -->
    <div
      class="fixed inset-0 z-50 bg-slate-900/60 backdrop-blur-xs flex items-center justify-center p-2 sm:p-4"
      @click.self="$emit('close')"
    >
      <!-- Modal Kutusu (Referans Görsel Tarzında 3D Çizgi Film Kutusu) -->
      <div class="bg-white rounded-[32px] border-[3px] border-slate-900 shadow-[0_12px_0_rgba(15,23,42,0.3)] max-w-5xl w-full overflow-hidden flex flex-col max-h-[92vh] animate-in fade-in zoom-in-95 duration-150">
        
        <!-- ÜST BAŞLIK ÇUBUĞU (Nane Yeşili Banner) -->
        <div class="px-5 py-3.5 bg-[#a7f3d0] border-b-[3px] border-slate-900 flex items-center justify-between shrink-0">
          <div class="flex items-center gap-3">
            <div class="w-10 h-10 rounded-2xl bg-white/90 border-2 border-slate-900 flex items-center justify-center text-2xl shadow-xs">
              🧰
            </div>
            <div>
              <h2 class="text-base sm:text-xl font-black text-slate-900 tracking-tight leading-tight">
                Malzeme Çantam
              </h2>
              <span class="text-[11px] font-bold text-slate-700">
                Projende kullanabileceğin elektronikler ({{ selectedCount }} parça çantada)
              </span>
            </div>
          </div>

          <!-- Kırmızı Kare Kapat Butonu -->
          <button
            type="button"
            @click="$emit('close')"
            class="w-8 h-8 rounded-xl bg-rose-500 hover:bg-rose-600 active:translate-y-0.5 text-white font-black text-sm flex items-center justify-center border-2 border-slate-900 shadow-[0_2px_0_#9f1239] cursor-pointer transition"
          >
            ✕
          </button>
        </div>

        <!-- FİLTRE VE ARAMA ŞERİDİ -->
        <div class="p-3 bg-slate-50 border-b-2 border-slate-900 flex flex-wrap items-center justify-between gap-2 shrink-0">
          <!-- Arama Kutusu -->
          <div class="relative flex-1 min-w-[200px]">
            <span class="absolute left-3 top-2 text-slate-400 text-xs">🔍</span>
            <input
              v-model="searchQuery"
              type="text"
              placeholder="Elektronik ara... (örn: servo, ldr, lcd, buzzer, uno, nano)"
              class="w-full pl-8 pr-3 py-1.5 rounded-xl border-2 border-slate-900 text-xs font-bold bg-white focus:outline-hidden focus:ring-2 focus:ring-teal-400"
            />
          </div>

          <!-- Hızlı Seçim Butonları & Yeni Ekle Butonu -->
          <div class="flex items-center gap-1.5 text-xs">
            <button
              type="button"
              @click="selectAllFiltered"
              class="px-2.5 py-1 rounded-xl bg-white hover:bg-slate-100 border-2 border-slate-900 text-slate-800 font-black cursor-pointer shadow-xs active:translate-y-0.5"
            >
              Hepsini Seç
            </button>
            <button
              type="button"
              @click="resetToDefault"
              class="px-2.5 py-1 rounded-xl bg-amber-100 hover:bg-amber-200 border-2 border-slate-900 text-slate-900 font-black cursor-pointer shadow-xs active:translate-y-0.5"
            >
              Temel Set
            </button>
            <button
              type="button"
              @click="clearAll"
              class="px-2.5 py-1 rounded-xl bg-rose-50 hover:bg-rose-100 border-2 border-slate-900 text-rose-700 font-black cursor-pointer shadow-xs active:translate-y-0.5"
            >
              Temizle
            </button>
            <button
              type="button"
              @click="showAddCustom = !showAddCustom"
              class="px-3 py-1 rounded-xl bg-[#38bdf8] hover:bg-[#0284c7] border-2 border-slate-900 text-slate-950 font-black cursor-pointer shadow-[0_2px_0_#0f172a] active:translate-y-0.5 transition flex items-center gap-1"
            >
              <span>➕</span>
              <span>Yeni Parça Ekle</span>
            </button>
          </div>
        </div>

        <!-- KATEGORİ SEKMELERİ -->
        <div class="px-3 py-2 bg-white border-b border-slate-200 flex items-center gap-1.5 overflow-x-auto shrink-0 select-none">
          <button
            v-for="cat in categories"
            :key="cat.id"
            type="button"
            @click="activeCategory = cat.id"
            :class="[
              'px-3 py-1 rounded-xl text-xs font-black transition-all cursor-pointer whitespace-nowrap border-2',
              activeCategory === cat.id
                ? 'bg-amber-400 text-slate-950 border-slate-900 shadow-[0_2px_0_#b45309]'
                : 'bg-slate-100 text-slate-700 border-transparent hover:bg-slate-200'
            ]"
          >
            <span>{{ cat.icon }}</span>
            <span class="ml-1">{{ cat.label }}</span>
            <span class="ml-1 text-[10px] opacity-70">({{ getCategoryCount(cat.id) }})</span>
          </button>
        </div>

        <!-- YENİ PARÇA EKLEME FORMU (Açılır Panel) -->
        <div v-if="showAddCustom" class="p-4 bg-sky-50 border-b-2 border-slate-900 flex flex-col gap-2 shrink-0 animate-in slide-in-from-top-3">
          <div class="flex items-center justify-between">
            <h4 class="text-xs font-black text-slate-900 flex items-center gap-1">
              <span>🛠️</span>
              <span>Kendi Elektronik Parçanı Oluştur</span>
            </h4>
            <button
              type="button"
              @click="showAddCustom = false"
              class="text-xs font-bold text-slate-500 hover:text-slate-800"
            >
              İptal ✕
            </button>
          </div>

          <div class="grid grid-cols-1 sm:grid-cols-4 gap-2">
            <input
              v-model="newPartName"
              type="text"
              placeholder="Parça Adı (örn: Su Seviye Sensörü)"
              class="sm:col-span-2 px-3 py-1.5 rounded-xl border-2 border-slate-900 text-xs font-bold bg-white"
            />
            <select
              v-model="newPartCategory"
              class="px-2.5 py-1.5 rounded-xl border-2 border-slate-900 text-xs font-bold bg-white"
            >
              <option value="sensor">Sensörler</option>
              <option value="light_display">Işık ve Ekran</option>
              <option value="actuator_sound">Motor & Ses</option>
              <option value="passive">Temel Parça</option>
              <option value="board">Geliştirme Kartı</option>
            </select>
            <div class="flex items-center gap-1">
              <input
                v-model="newPartIcon"
                type="text"
                placeholder="İkon (💧, 🎛️)"
                class="w-16 px-2 py-1.5 rounded-xl border-2 border-slate-900 text-xs font-bold bg-white text-center"
              />
              <button
                type="button"
                @click="saveCustomPart"
                :disabled="!newPartName.trim()"
                class="flex-1 py-1.5 rounded-xl bg-emerald-500 hover:bg-emerald-600 disabled:opacity-40 text-white font-black text-xs border-2 border-slate-900 shadow-[0_2px_0_#0f172a] active:translate-y-0.5 cursor-pointer"
              >
                Ekle!
              </button>
            </div>
          </div>
          <input
            v-model="newPartDesc"
            type="text"
            placeholder="Kısa Açıklama (örn: Suyun yüksekliğini analog pin üzerinden okur)"
            class="px-3 py-1 rounded-xl border-2 border-slate-900 text-[11px] font-bold bg-white"
          />
        </div>

        <!-- ELEKTRONİK PARÇALAR IZGARASI (Gerçek Wokwi Görsel Donanım Kataloğu) -->
        <div class="flex-1 overflow-y-auto p-4 grid grid-cols-2 sm:grid-cols-3 md:grid-cols-4 lg:grid-cols-5 gap-3 bg-slate-50">
          <div
            v-for="item in filteredElectronics"
            :key="item.id"
            @click="toggleItem(item.id)"
            :class="[
              'p-3 rounded-2xl border-2 border-slate-900 flex flex-col items-center justify-between text-center relative select-none cursor-pointer transition-all shadow-[0_3px_0_#1e293b]',
              isSelected(item.id) ? (item.color || 'bg-[#bbf7d0]') : 'bg-white hover:bg-slate-50'
            ]"
          >
            <!-- Özel Parçayı Silme Butonu -->
            <button
              v-if="item.isCustom"
              type="button"
              @click.stop="removeCustomPart(item.id)"
              class="absolute top-1 left-1 w-5 h-5 rounded-full bg-rose-500 text-white text-[10px] font-black flex items-center justify-center hover:scale-110 cursor-pointer shadow-xs"
              title="Bu parçayı sil"
            >
              ✕
            </button>

            <!-- Gerçek Wokwi Web Bileşen Görseli -->
            <WokwiComponentPreview :item-id="item.id" :icon="item.icon" class="mb-2" />

            <!-- İsim ve Etiket -->
            <div class="w-full">
              <span class="text-xs font-black text-slate-900 block truncate leading-tight">
                {{ item.name }}
              </span>
              <span class="text-[10px] font-bold text-slate-500 block truncate mt-0.5">
                {{ item.tag }}
              </span>
            </div>

            <!-- Seçili Onay Rozeti (Referans Görseldeki Yeşil Çember Tik) -->
            <span
              v-if="isSelected(item.id)"
              class="absolute -top-1.5 -right-1.5 w-6 h-6 rounded-full bg-emerald-500 border-2 border-slate-900 text-white font-black text-xs flex items-center justify-center shadow-xs"
            >
              ✓
            </span>
          </div>

          <!-- Arama Sonucu Yoksa -->
          <div v-if="filteredElectronics.length === 0" class="col-span-full py-12 text-center flex flex-col items-center justify-center text-slate-400">
            <span class="text-4xl mb-2">🔍</span>
            <span class="text-sm font-black text-slate-600">Aradığınız kriterde malzeme bulunamadı.</span>
            <button
              type="button"
              @click="searchQuery = ''; activeCategory = 'all'"
              class="mt-3 px-3 py-1 rounded-xl bg-white border border-slate-300 text-xs font-bold text-slate-700"
            >
              Filtreleri Temizle
            </button>
          </div>
        </div>

        <!-- ALT BUTON ÇUBUĞU (Kaydet ve Çantaya Koy!) -->
        <div class="p-4 bg-white border-t-[3px] border-slate-900 flex items-center justify-between shrink-0">
          <div class="text-xs font-bold text-slate-600">
            Toplam <strong>{{ selectedCount }}</strong> malzeme çantaya yerleştirildi.
          </div>

          <button
            type="button"
            @click="handleSave"
            class="px-8 py-2.5 rounded-full bg-gradient-to-r from-[#4ade80] to-[#22c55e] hover:from-[#86efac] hover:to-[#16a34a] active:translate-y-1 active:shadow-none text-slate-950 font-black text-xs sm:text-sm border-2 border-slate-900 shadow-[0_4px_0_#0f172a] transition-all cursor-pointer flex items-center gap-1.5"
          >
            <span>Kaydet ve Çantaya Koy! 🎒</span>
          </button>
        </div>

      </div>
    </div>
  </div>
</template>

<script setup lang="ts">
import { ref, computed, onMounted } from 'vue';
import type { InventoryItem } from '../types/project';
import WokwiComponentPreview from './WokwiComponentPreview.vue';

const props = defineProps<{
  isOpen: boolean;
  selectedInventory: string[];
}>();

const emit = defineEmits<{
  (e: 'close'): void;
  (e: 'save', inventory: string[]): void;
}>();

const selectedItems = ref<string[]>([...props.selectedInventory]);
const searchQuery = ref('');
const activeCategory = ref('all');

// Yeni parça ekleme durumu
const showAddCustom = ref(false);
const newPartName = ref('');
const newPartCategory = ref('sensor');
const newPartIcon = ref('🧪');
const newPartDesc = ref('');

// Gerçek Wokwi Web Bileşenleri ile Donatılmış Zengin Parça Listesi
const defaultElectronics: InventoryItem[] = [
  // 1. Geliştirme Kartları
  { id: 'ARDUINO_UNO', name: 'Arduino Uno R3', icon: '🟦', tag: 'Standart Geliştirme Kartı', category: 'board', color: 'bg-[#bbf7d0]' },
  { id: 'ARDUINO_NANO', name: 'Arduino Nano', icon: '🎛️', tag: 'Kompakt Mini Kart', category: 'board', color: 'bg-[#bbf7d0]' },
  { id: 'ARDUINO_MEGA', name: 'Arduino Mega 2560', icon: '🏢', tag: '54 Pinli Güçlü Kart', category: 'board', color: 'bg-[#bbf7d0]' },
  { id: 'ESP32', name: 'ESP32 DevKit V1', icon: '📡', tag: 'WiFi & Bluetooth Modülü', category: 'board', color: 'bg-[#bbf7d0]' },

  // 2. Breadboard & Bağlantı
  { id: 'BREADBOARD', name: 'Breadboard (Devre Tahtası)', icon: '🍞', tag: '30 Sütun Lehimleme Gerektirmeyen Tahta', category: 'passive', color: 'bg-amber-50' },

  // 3. Işıklar ve Göstergeler
  { id: 'LED_RED', name: 'Kırmızı LED', icon: '🔴', tag: 'Parlak Kırmızı Işık', category: 'light_display', color: 'bg-[#ffe4e6]' },
  { id: 'LED_GREEN', name: 'Yeşil LED', icon: '🟢', tag: 'Parlak Yeşil Işık', category: 'light_display', color: 'bg-[#dcfce7]' },
  { id: 'LED_BLUE', name: 'Mavi LED', icon: '🔵', tag: 'Parlak Mavi Işık', category: 'light_display', color: 'bg-[#dbeafe]' },
  { id: 'LED_YELLOW', name: 'Sarı LED', icon: '🟡', tag: 'Parlak Sarı Işık', category: 'light_display', color: 'bg-[#fef9c3]' },
  { id: 'LED_RGB', name: 'RGB LED', icon: '🌈', tag: 'Her Rengi Yakan LED', category: 'light_display', color: 'bg-[#f3e8ff]' },
  { id: 'LCD_16X2_I2C', name: '16x2 LCD Ekran', icon: '📟', tag: 'Mavi I2C Karakter Ekran', category: 'light_display', color: 'bg-[#e0f2fe]' },
  { id: 'SEVEN_SEGMENT', name: '7-Segment Ekran', icon: '8️⃣', tag: 'Sayısal Gösterge', category: 'light_display', color: 'bg-[#fef3c7]' },
  { id: 'OLED_096_I2C', name: '0.96" OLED Ekran', icon: '📺', tag: 'SSD1306 Grafik Ekran', category: 'light_display', color: 'bg-[#e0f2fe]' },

  // 4. Dirençler ve Pasifler
  { id: 'RESISTOR_220', name: '220Ω Direnç', icon: '🟤', tag: 'LED Akım Koruyucu', category: 'passive', color: 'bg-[#fef3c7]' },
  { id: 'RESISTOR_1K', name: '1kΩ Direnç', icon: '🟤', tag: 'Sinyal Direnci', category: 'passive', color: 'bg-[#fef3c7]' },
  { id: 'RESISTOR_10K', name: '10kΩ Direnç', icon: '🟤', tag: 'Pull-up Sensör Direnci', category: 'passive', color: 'bg-[#fef3c7]' },
  { id: 'POTENTIOMETER', name: '10kΩ Potansiyometre', icon: '🎚️', tag: 'Ayarlanabilir Döner Direnç', category: 'passive', color: 'bg-[#e2e8f0]' },
  { id: 'PUSH_BUTTON', name: 'Push Buton', icon: '🔘', tag: 'Basmalı Düğme', category: 'passive', color: 'bg-[#f1f5f9]' },
  { id: 'SLIDE_SWITCH', name: 'Sürgülü Anahtar', icon: '🔛', tag: 'Aç/Kapa Switch', category: 'passive', color: 'bg-[#f1f5f9]' },

  // 5. Sensörler
  { id: 'LDR_DISCRETE', name: 'Foto-direnç (2 Bacaklı LDR)', icon: '☀️', tag: 'Klasik Işığa Duyarlı Direnç', category: 'sensor', color: 'bg-[#fed7aa]' },
  { id: 'LDR_MODULE', name: 'LDR Sensör Modülü (4 Pinli)', icon: '🎛️', tag: 'KY-018 Karşılaştırıcı Kart Modülü', category: 'sensor', color: 'bg-[#fed7aa]' },
  { id: 'LDR_SENSOR', name: 'Işık Sensörü (LDR)', icon: '☀️', tag: 'Oda Işığı Seviyesi Ölçer', category: 'sensor', color: 'bg-[#fed7aa]' },
  { id: 'HCSR04', name: 'HC-SR04 Mesafe Sensörü', icon: '🦇', tag: 'Ultrasonik Mesafe Ölçer', category: 'sensor', color: 'bg-[#bae6fd]' },
  { id: 'PIR_SENSOR', name: 'PIR Hareket Sensörü', icon: '🚶', tag: 'İnsan ve Vücut Isısı Algılayıcı', category: 'sensor', color: 'bg-[#fed7aa]' },
  { id: 'DHT11', name: 'DHT22 Sıcaklık & Nem', icon: '🌡️', tag: 'Hava Sıcaklığı ve Nem Ölçer', category: 'sensor', color: 'bg-[#bae6fd]' },
  { id: 'JOYSTICK_MODULE', name: 'Analog Joystick Modülü', icon: '🕹️', tag: 'X/Y Eksenli Oyun Çubuğu', category: 'sensor', color: 'bg-[#e2e8f0]' },
  { id: 'SOIL_MOISTURE', name: 'Toprak Nem Sensörü', icon: '🌱', tag: 'Bitki Toprak Nemi Ölçer', category: 'sensor', color: 'bg-[#dcfce7]' },
  { id: 'RAIN_SENSOR', name: 'Yağmur Sensörü', icon: '🌧️', tag: 'Su Damlası Dedektörü', category: 'sensor', color: 'bg-[#e0f2fe]' },
  { id: 'SOUND_SENSOR', name: 'Ses Mikrofon Modülü', icon: '🎤', tag: 'Alkış & Gürültü Algılar', category: 'sensor', color: 'bg-[#fed7aa]' },
  { id: 'MQ2_GAS', name: 'MQ-2 Gaz & Duman', icon: '💨', tag: 'Duman ve Gaz Algılayıcı', category: 'sensor', color: 'bg-[#fef3c7]' },

  // 6. Motorlar, Ses ve Aktüatörler
  { id: 'BUZZER', name: 'Piezo Buzzer (Hoparlör)', icon: '🔊', tag: 'Melodi, Alarm ve Bip Sesi', category: 'actuator_sound', color: 'bg-[#e2e8f0]' },
  { id: 'ACTIVE_BUZZER', name: 'Aktif Buzzer', icon: '📢', tag: 'Sürekli Bip Sesi Verici', category: 'actuator_sound', color: 'bg-[#e2e8f0]' },
  { id: 'SERVO_SG90', name: 'SG90 Servo Motor', icon: '🦾', tag: '0-180 Derece Dönen Kol', category: 'actuator_sound', color: 'bg-[#bae6fd]' },
  { id: 'DC_MOTOR_5V', name: '5V DC Motor', icon: '🌀', tag: 'Pervane ve Tekerlek Döndürücü', category: 'actuator_sound', color: 'bg-[#fed7aa]' },
  { id: 'RELAY_5V', name: '5V Röle Modülü', icon: '⚡', tag: 'Oda Lambası Anahtarı', category: 'actuator_sound', color: 'bg-[#fee2e2]' }
];

const customElectronics = ref<InventoryItem[]>([]);

const categories = [
  { id: 'all', label: 'Tümü', icon: '🌟' },
  { id: 'board', label: 'Kartlar', icon: '🧠' },
  { id: 'sensor', label: 'Sensörler', icon: '👁️' },
  { id: 'light_display', label: 'Işık & Ekran', icon: '💡' },
  { id: 'actuator_sound', label: 'Motor & Ses', icon: '⚙️' },
  { id: 'passive', label: 'Temel Parça', icon: '🎛️' },
  { id: 'custom', label: 'Özel Eklenenler', icon: '➕' },
];

const allElectronics = computed(() => {
  return [...defaultElectronics, ...customElectronics.value];
});

const filteredElectronics = computed(() => {
  let list = allElectronics.value;

  if (activeCategory.value !== 'all') {
    if (activeCategory.value === 'custom') {
      list = list.filter(item => item.isCustom);
    } else {
      list = list.filter(item => item.category === activeCategory.value);
    }
  }

  if (searchQuery.value.trim()) {
    const q = searchQuery.value.toLowerCase().trim();
    list = list.filter(item =>
      item.name.toLowerCase().includes(q) ||
      item.tag.toLowerCase().includes(q) ||
      item.id.toLowerCase().includes(q)
    );
  }

  return list;
});

const selectedCount = computed(() => selectedItems.value.length);

function getCategoryCount(catId: string): number {
  if (catId === 'all') return allElectronics.value.length;
  if (catId === 'custom') return customElectronics.value.length;
  return allElectronics.value.filter(i => i.category === catId).length;
}

function isSelected(id: string): boolean {
  return selectedItems.value.includes(id);
}

function toggleItem(id: string) {
  if (selectedItems.value.includes(id)) {
    selectedItems.value = selectedItems.value.filter(i => i !== id);
  } else {
    selectedItems.value.push(id);
  }
}

function selectAllFiltered() {
  filteredElectronics.value.forEach(item => {
    if (!selectedItems.value.includes(item.id)) {
      selectedItems.value.push(item.id);
    }
  });
}

function clearAll() {
  selectedItems.value = [];
}

function resetToDefault() {
  selectedItems.value = [
    'ARDUINO_UNO',
    'BREADBOARD',
    'LED_RED',
    'RESISTOR_220',
    'LDR_SENSOR',
    'BUZZER'
  ];
}

function saveCustomPart() {
  if (!newPartName.value.trim()) return;
  const newId = 'CUSTOM_' + newPartName.value.toUpperCase().replace(/[^A-Z0-9]/g, '_') + '_' + Date.now().toString().slice(-4);
  const item: InventoryItem = {
    id: newId,
    name: newPartName.value.trim(),
    icon: newPartIcon.value.trim() || '🧪',
    tag: newPartDesc.value.trim() || 'Özel Parça',
    category: newPartCategory.value,
    color: 'bg-purple-100',
    isCustom: true
  };
  customElectronics.value.push(item);
  selectedItems.value.push(newId);

  try {
    localStorage.setItem('kid_custom_electronics', JSON.stringify(customElectronics.value));
  } catch {}

  newPartName.value = '';
  newPartDesc.value = '';
  newPartIcon.value = '🧪';
  showAddCustom.value = false;
}

function removeCustomPart(id: string) {
  customElectronics.value = customElectronics.value.filter(i => i.id !== id);
  selectedItems.value = selectedItems.value.filter(i => i !== id);
  try {
    localStorage.setItem('kid_custom_electronics', JSON.stringify(customElectronics.value));
  } catch {}
}

function handleSave() {
  emit('save', selectedItems.value);
  emit('close');
}

onMounted(() => {
  try {
    const saved = localStorage.getItem('kid_custom_electronics');
    if (saved) {
      customElectronics.value = JSON.parse(saved);
    }
  } catch {}
});
</script>

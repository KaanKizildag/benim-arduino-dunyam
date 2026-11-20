<template>
  <div class="w-full max-w-5xl mx-auto flex-1 flex flex-col items-center justify-between gap-4 py-3 sm:py-5 px-3 sm:px-6 select-none">
    
    <!-- 1. SEVİMLİ KARŞILAMA VE DİYALOG (Referans Görsel 1 Sol Üst Sohbet Stili) -->
    <div class="w-full flex flex-col sm:flex-row items-center gap-4 bg-white rounded-3xl p-4 sm:p-5 border-[3px] border-slate-900 shadow-[0_4px_0_#0f172a]">
      <!-- Sevimli Robot Başlığı -->
      <div class="relative shrink-0 group">
        <div class="w-20 h-20 sm:w-24 sm:h-24 rounded-3xl bg-[#38bdf8] border-[3px] border-slate-900 shadow-[0_4px_0_#0284c7] flex items-center justify-center text-4xl sm:text-5xl group-hover:rotate-6 transition-transform">
          🤖
        </div>
        <span class="absolute -top-1 -right-1 w-5 h-5 rounded-full bg-emerald-400 border-2 border-slate-900 animate-ping"></span>
        <span class="absolute -top-1 -right-1 w-5 h-5 rounded-full bg-emerald-500 border-2 border-slate-900"></span>
      </div>

      <!-- Konuşma Balonu -->
      <div class="flex-1 text-center sm:text-left">
        <div class="flex items-center justify-center sm:justify-start gap-2 mb-1">
          <h2 class="text-base sm:text-xl font-black text-slate-900">
            Merhaba Geleceğin Mucidi! 👋
          </h2>
          <span class="px-2 py-0.5 rounded-full bg-amber-200 border border-slate-900 text-[10px] font-black text-slate-900">
            AI Asistanın Hazır
          </span>
        </div>
        <p class="text-xs sm:text-sm text-slate-600 font-bold leading-relaxed">
          Ben senin yapay zeka devre asistanınım. Arduino ile yapmak istediğin şeyi bana kendi kelimelerinle anlat! Örneğin: <em>"Odam kararınca sarı gece lambam yansın, aydınlanınca sönsün."</em>
        </p>
      </div>
    </div>

      <!-- SAYFA 1: HAYAL ET (Yapay Zeka ile Tasarla!) -->
    <!-- 2. BÜYÜK FİKİR GİRİŞ KUTUSU VE SESLİ GİRİŞ -->
    <div class="w-full bg-white rounded-3xl p-4 sm:p-6 border-[3px] border-slate-900 shadow-[0_5px_0_#0f172a] flex flex-col gap-3">
      <div class="relative">
        <textarea
          v-model="promptText"
          rows="3"
          placeholder="Hayalindeki projeyi buraya yaz... (Örn: 2 bacaklı ldr sensörü ile günebakan projesi yapmak istiyorum. 2 tane ldr sensörüm var. hangisinden ışık fazla geliyorsa servo motor o yöne doğru hareket etmeli)"
          class="w-full p-4 sm:p-5 rounded-2xl border-2 border-slate-900 bg-slate-50 focus:bg-white focus:ring-2 focus:ring-sky-400 text-slate-900 font-black text-sm sm:text-base outline-none transition resize-none placeholder:text-slate-400 placeholder:font-bold"
          @keydown.enter.prevent="handleGenerate"
        ></textarea>

        <!-- Temizle Butonu -->
        <button
          v-if="promptText"
          type="button"
          @click="promptText = ''"
          class="absolute bottom-3 right-3 px-3 py-1.5 rounded-xl border-2 border-slate-900 bg-white hover:bg-slate-100 text-slate-800 transition shadow-[0_2px_0_#0f172a] active:translate-y-0.5 active:shadow-none cursor-pointer flex items-center gap-1.5 text-xs font-black"
          title="Metni Temizle"
        >
          <span>🧹</span>
          <span class="hidden sm:inline">Temizle</span>
        </button>
      </div>

      <!-- Elimdeki Malzemelerle Ne Yapabilirim? (Malzeme Çantası Tabanlı Dinamik Öneriler) -->
      <div class="bg-amber-50/90 rounded-2xl border-2 border-slate-900 p-3 flex flex-col gap-2">
        <div class="flex flex-wrap items-center justify-between gap-2">
          <div class="flex items-center gap-1.5 text-xs font-black text-slate-900">
            <span>🎒</span>
            <span>Elimdeki Malzemelerle Ne Yapabilirim?</span>
            <span class="px-2 py-0.5 rounded-lg bg-emerald-100 border border-slate-900 text-[10px] text-emerald-950">
              Çantandaki {{ inventoryCount }} Parçaya Göre Öneriler
            </span>
          </div>
          <button
            type="button"
            @click="$emit('open-inventory')"
            class="px-2.5 py-1 rounded-xl bg-white hover:bg-slate-100 border border-slate-900 text-[10px] font-black text-slate-800 cursor-pointer shadow-2xs"
          >
            🧰 Çantamı Düzenle / Önerileri Gör
          </button>
        </div>

        <div v-if="bagSuggestions.length > 0" class="grid grid-cols-1 sm:grid-cols-3 gap-2">
          <button
            v-for="item in bagSuggestions"
            :key="item.id"
            type="button"
            @click="promptText = item.prompt"
            class="p-2.5 rounded-xl bg-white hover:bg-[#fef08a] border-2 border-slate-900 text-left transition cursor-pointer shadow-[0_2px_0_#0f172a] active:translate-y-0.5 flex flex-col gap-0.5"
          >
            <div class="text-xs font-black text-slate-900 truncate">
              {{ item.icon }} {{ item.title }}
            </div>
            <div class="text-[10px] font-bold text-slate-600 line-clamp-2 leading-snug">
              {{ item.description }}
            </div>
          </button>
        </div>
        <div v-else class="text-[11px] font-bold text-slate-600">
          Malzeme Çantana parçalarını ekleyerek elindeki malzemelerle yapabileceğin proje fikirlerini burada görebilirsin!
        </div>
      </div>
    </div>

    <!-- 3. ALT ÇUBUK: ÇANTA BİLGİSİ VE BÜYÜK TASARLA BUTONU -->
    <div class="w-full bg-white rounded-2xl p-3 sm:p-4 border-[3px] border-slate-900 shadow-[0_4px_0_#0f172a] flex flex-col sm:flex-row items-center justify-between gap-3">
      <div class="flex items-center gap-2 text-xs font-black text-slate-700">
        <span class="text-lg">🎒</span>
        <span>Malzeme Çantam:</span>
        <span class="px-2 py-0.5 rounded-lg bg-emerald-100 text-emerald-900 border border-slate-900">
          {{ inventoryCount }} Elektronik Parça Hazır
        </span>
      </div>

      <button
        type="button"
        @click="handleGenerate"
        :disabled="isGenerating || !promptText.trim()"
        class="w-full sm:w-auto px-10 py-3.5 rounded-2xl bg-[#4ade80] hover:bg-[#22c55e] border-2 border-slate-900 shadow-[0_5px_0_#15803d] active:translate-y-1 active:shadow-[0_1px_0_#15803d] text-slate-950 font-black text-sm sm:text-base transition cursor-pointer flex items-center justify-center gap-2 group disabled:opacity-40 disabled:cursor-not-allowed"
      >
        <span v-if="isGenerating" class="animate-spin text-xl">⚙️</span>
        <span v-else class="text-xl group-hover:rotate-12 transition-transform">🚀</span>
        <span>{{ isGenerating ? 'Yapay Zeka Devreyi Tasarlıyor...' : 'Devreyi ve Kodu Tasarla! ➔' }}</span>
      </button>
    </div>

    <!-- 4. YAPAY ZEKA TASARIM SÜRECİ CANLI ANİMASYON MODALI (isGenerating === true) -->
    <div
      v-if="isGenerating"
      class="fixed inset-0 z-50 bg-slate-900/75 backdrop-blur-xs flex items-center justify-center p-3 sm:p-5 select-none animate-in fade-in duration-150"
    >
      <div class="bg-white rounded-[32px] border-[3px] border-slate-900 shadow-[0_14px_0_rgba(15,23,42,0.35)] max-w-xl w-full overflow-hidden flex flex-col">
        <!-- Üst Başlık ve Canlı Süre Sayacı -->
        <div class="px-5 py-4 bg-gradient-to-r from-[#38bdf8] via-[#818cf8] to-[#c084fc] border-b-[3px] border-slate-900 flex items-center justify-between gap-3">
          <div class="flex items-center gap-3">
            <div class="w-12 h-12 rounded-2xl bg-[#fef08a] border-2 border-slate-900 shadow-[0_3px_0_#0f172a] flex items-center justify-center text-3xl animate-bounce">
              🤖
            </div>
            <div>
              <h3 class="text-base sm:text-lg font-black text-slate-950 leading-tight">
                AI Mucit Devreni Tasarlıyor...
              </h3>
              <div class="flex items-center gap-1.5 mt-0.5">
                <span class="px-2 py-0.5 rounded-md bg-slate-900 text-amber-300 text-[10px] font-black">
                  🧠 {{ activeModelName || 'Yapay Zeka' }}
                </span>
                <span class="text-[11px] font-black text-slate-900">
                  çalışıyor
                </span>
              </div>
            </div>
          </div>

          <!-- Geçen Süre Rozeti -->
          <div class="px-3 py-1.5 rounded-2xl bg-white border-2 border-slate-900 shadow-[0_2px_0_#0f172a] flex flex-col items-center shrink-0">
            <span class="text-[9px] font-black text-slate-500 uppercase tracking-wider">SÜRE</span>
            <span class="text-sm font-black text-slate-900 font-mono">{{ elapsedSeconds }}sn</span>
          </div>
        </div>

        <!-- Orta Kısım: Canlı İlerleme Çubuğu ve Aşamalar -->
        <div class="p-5 flex flex-col gap-4 bg-slate-50">
          <!-- Kullanıcının İstemi Özeti -->
          <div class="px-3.5 py-2.5 rounded-2xl bg-white border-2 border-slate-900/20 text-xs font-bold text-slate-700 flex items-start gap-2">
            <span class="text-base shrink-0">💭</span>
            <span class="line-clamp-2 italic">"{{ promptText || 'Proje fikrin analiz ediliyor...' }}"</span>
          </div>

          <!-- Animasyonlu İlerleme Çubuğu -->
          <div class="w-full flex flex-col gap-1.5">
            <div class="flex items-center justify-between text-xs font-black text-slate-800">
              <span>{{ currentProgressStage.title }}</span>
              <span class="text-sky-700">%{{ progressPercent }}</span>
            </div>
            <div class="w-full h-4 rounded-full bg-slate-200 border-2 border-slate-900 overflow-hidden p-0.5">
              <div
                class="h-full rounded-full bg-gradient-to-r from-[#38bdf8] via-[#4ade80] to-[#facc15] transition-all duration-500"
                :style="{ width: `${progressPercent}%` }"
              ></div>
            </div>
          </div>

          <!-- 5 Adımlı Canlı Yapay Zeka İşlem Listesi -->
          <div class="flex flex-col gap-2">
            <div
              v-for="(stage, idx) in progressStages"
              :key="stage.id"
              :class="[
                'px-3.5 py-2.5 rounded-2xl border-2 flex items-center justify-between gap-3 transition-all duration-300',
                idx < activeStageIndex
                  ? 'bg-emerald-50 border-emerald-500 text-emerald-950'
                  : idx === activeStageIndex
                  ? 'bg-[#fef08a] border-slate-900 text-slate-950 shadow-[0_3px_0_#0f172a] scale-[1.01]'
                  : 'bg-white/60 border-slate-200 text-slate-400'
              ]"
            >
              <div class="flex items-center gap-2.5 min-w-0">
                <span class="text-lg shrink-0">
                  <template v-if="idx < activeStageIndex">✅</template>
                  <template v-else-if="idx === activeStageIndex">
                    <span class="inline-block animate-spin">⚙️</span>
                  </template>
                  <template v-else>{{ stage.icon }}</template>
                </span>
                <div class="min-w-0">
                  <div class="text-xs font-black truncate">{{ stage.title }}</div>
                  <div class="text-[10px] font-bold truncate opacity-85">{{ stage.subtitle }}</div>
                </div>
              </div>

              <span
                v-if="idx < activeStageIndex"
                class="px-2 py-0.5 rounded-lg bg-emerald-500 text-white text-[9px] font-black shrink-0"
              >
                Tamam
              </span>
              <span
                v-else-if="idx === activeStageIndex"
                class="px-2 py-0.5 rounded-lg bg-slate-900 text-amber-300 text-[9px] font-black shrink-0 animate-pulse"
              >
                İşleniyor...
              </span>
            </div>
          </div>

          <!-- Eğlenceli Elektronik İpucu Kartı (Dönen İpuçları) -->
          <div class="p-3 rounded-2xl bg-sky-100/90 border-2 border-slate-900 flex items-center gap-3">
            <span class="text-2xl shrink-0">💡</span>
            <div class="text-[11px] font-bold text-slate-800 leading-snug">
              <strong class="text-slate-950 font-black">Biliyor muydun?</strong>
              {{ currentFunFact }}
            </div>
          </div>
        </div>
      </div>
    </div>

  </div>
</template>

<script setup lang="ts">
import { ref, computed, watch, onUnmounted } from 'vue';

const props = defineProps<{
  isGenerating: boolean;
  inventoryCount: number;
  selectedInventory?: string[];
  activeModelName?: string;
}>();

const emit = defineEmits<{
  (e: 'generate', prompt: string): void;
  (e: 'open-inventory'): void;
}>();

const promptText = ref('');
const elapsedSeconds = ref(0);
let timerHandle: ReturnType<typeof setInterval> | null = null;

interface ProgressStage {
  id: string;
  icon: string;
  title: string;
  subtitle: string;
}

const progressStages: ProgressStage[] = [
  {
    id: 'stage-1',
    icon: '🔍',
    title: '1. Proje Fikrin Analiz Ediliyor',
    subtitle: 'İstediğin sensörler, motorlar ve çalışma mantığı belirleniyor...'
  },
  {
    id: 'stage-2',
    icon: '🧩',
    title: '2. Elektronik Parçalar Seçiliyor',
    subtitle: 'Gerekli dirençler ve bileşen tipleri (Wokwi standartlarında) hazırlanıyor...'
  },
  {
    id: 'stage-3',
    icon: '🔌',
    title: '3. Breadboard ve Arduino Pinleri Bağlanıyor',
    subtitle: '5V, GND ve sinyal kabloları kısa devre olmayacak şekilde yönlendiriliyor...'
  },
  {
    id: 'stage-4',
    icon: '🗺️',
    title: '4. Sebep-Sonuç Akış Diyagramı Çiziliyor',
    subtitle: 'Gözlemle ➔ Karar Ver ➔ Evet/Hayır adımları devrene özel kurgulanıyor...'
  },
  {
    id: 'stage-5',
    icon: '💻',
    title: '5. Arduino C++ Kodu Yazılıyor ve Doğrulanıyor',
    subtitle: 'Koddaki pin numaraları ile devre kablolaması %100 eşleştiriliyor...'
  }
];

const FUN_FACTS = [
  'Breadboard üzerindeki aynı sütundaki 5 pin (A-B-C-D-E) içeriden metal bir klipsle birbirine bağlıdır!',
  '2 bacaklı LDR ışık sensörü karanlıkta yüksek direnç, aydınlıkta düşük direnç gösterir; 10kΩ dirençle birlikte Arduino A0 pininden okunur.',
  'LED ışıkların uzun bacağı (+) Anot, kısa bacağı (-) Katot uçtur ve yüksek akımdan korunmak için 220Ω dirençle bağlanır.',
  'SG90 Servo motorların içinde minik bir dişli kutusu ve açı sensörü vardır; PWM sinyaliyle 0° ile 180° arasında istediğin açıya döner!',
  'HC-SR04 mesafe sensörü tıpkı yarasalar gibi kulağımızın duyamadığı ultrasonik ses dalgaları gönderip yankı süresini ölçer.'
];

const activeStageIndex = computed(() => {
  const s = elapsedSeconds.value;
  if (s < 3) return 0;
  if (s < 7) return 1;
  if (s < 13) return 2;
  if (s < 20) return 3;
  return 4;
});

const currentProgressStage = computed(() => {
  return progressStages[activeStageIndex.value] || progressStages[0]!;
});

const progressPercent = computed(() => {
  const s = elapsedSeconds.value;
  if (s <= 20) {
    return Math.min(92, Math.max(8, Math.round((s / 20) * 88) + 8));
  }
  return Math.min(97, 92 + Math.floor((s - 20) / 8));
});

const currentFunFact = computed(() => {
  const idx = Math.floor(elapsedSeconds.value / 6) % FUN_FACTS.length;
  return FUN_FACTS[idx];
});

function startProgressTimer() {
  stopProgressTimer();
  elapsedSeconds.value = 0;
  timerHandle = setInterval(() => {
    elapsedSeconds.value += 1;
  }, 1000);
}

function stopProgressTimer() {
  if (timerHandle) {
    clearInterval(timerHandle);
    timerHandle = null;
  }
}

watch(
  () => props.isGenerating,
  (generating) => {
    if (generating) {
      startProgressTimer();
    } else {
      stopProgressTimer();
    }
  },
  { immediate: true }
);

onUnmounted(() => {
  stopProgressTimer();
});

interface BagSuggestion {
  id: string;
  title: string;
  icon: string;
  description: string;
  prompt: string;
  check: (inv: Set<string>) => boolean;
}

const BAG_SUGGESTION_RULES: BagSuggestion[] = [
  {
    id: 'bag-sunflower-2ldr',
    title: 'Günebakan Servo (2 LDR ile)',
    icon: '🌻',
    description: '2 adet 2 bacaklı LDR ile ışığın fazla geldiği yöne dönen günebakan servo.',
    prompt: '2 bacaklı ldr sensörü ile günebakan projesi yapmak istiyorum. 2 tane ldr sensörüm var. hangisinden ışık fazla geliyorsa servo motor o yöne doğru hareket etmeli.',
    check: (inv) => (inv.has('LDR_DISCRETE') || inv.has('LDR_SENSOR') || inv.has('LDR_MODULE')) && inv.has('SERVO_SG90')
  },
  {
    id: 'bag-night-lamp',
    title: 'Otomatik Gece Lambası',
    icon: '🌙',
    description: 'Oda karanlık olduğunda LDR algılasın ve LED otomatik olarak yansın.',
    prompt: 'LDR ışık sensörü ile ortam karanlık olduğunda LED yansın, aydınlık olduğunda LED sönsün.',
    check: (inv) =>
      (inv.has('LDR_DISCRETE') || inv.has('LDR_SENSOR') || inv.has('LDR_MODULE')) &&
      (inv.has('LED_RED') || inv.has('LED_GREEN') || inv.has('LED_YELLOW') || inv.has('LED_BLUE'))
  },
  {
    id: 'bag-morning-alarm',
    title: 'Güneş Doğdu Alarmı (LDR + Buzzer)',
    icon: '⏰',
    description: 'Sabah güneş doğup oda aydınlandığında LDR algılasın ve buzzer alarm çalsın.',
    prompt: 'LDR ışık sensörü üzerine güçlü ışık düştüğünde buzzer ile sabah uyandırma alarmı çalsın.',
    check: (inv) =>
      (inv.has('LDR_DISCRETE') || inv.has('LDR_SENSOR') || inv.has('LDR_MODULE')) &&
      (inv.has('BUZZER') || inv.has('ACTIVE_BUZZER'))
  },
  {
    id: 'bag-parking-radar',
    title: 'Ultrasonik Park Sensörü',
    icon: '🚗',
    description: 'HC-SR04 mesafe sensörü 15 cm yakında engel gördüğünde buzzer sesli uyarı versin.',
    prompt: 'HC-SR04 ultrasonik mesafe sensörü ile 15 cm yaklaşınca buzzer sesli uyarı versin.',
    check: (inv) => inv.has('HCSR04') && (inv.has('BUZZER') || inv.has('ACTIVE_BUZZER'))
  },
  {
    id: 'bag-smart-barrier',
    title: 'Akıllı Otopark Bariyeri',
    icon: '🚧',
    description: 'Mesafe sensörü yaklaşan aracı görünce servo motor bariyeri 90 derece kaldırsın.',
    prompt: 'HC-SR04 mesafe sensörü önüne araç yaklaştığında SG90 servo motor bariyeri 90 derece açsın.',
    check: (inv) => inv.has('HCSR04') && inv.has('SERVO_SG90')
  },
  {
    id: 'bag-button-servo',
    title: 'Butonlu Kapı Kilidi (Servo)',
    icon: '🚪',
    description: 'Push butona basıldığında servo motor kapıyı açsın, bırakıldığında kapatsın.',
    prompt: 'Push butona basıldığında SG90 servo motor 90 derece dönerek kapıyı açsın.',
    check: (inv) => inv.has('PUSH_BUTTON') && inv.has('SERVO_SG90')
  },
  {
    id: 'bag-pot-servo',
    title: 'Potansiyometre ile Robot Kol',
    icon: '🦾',
    description: 'Potansiyometreyi çevirdikçe servo motorun açısını 0-180 derece arasında kontrol et.',
    prompt: '10k potansiyometreyi çevirdikçe SG90 servo motorun açısı 0 ile 180 derece arasında dönsün.',
    check: (inv) => inv.has('POTENTIOMETER') && inv.has('SERVO_SG90')
  }
];

const bagSuggestions = computed(() => {
  const invSet = new Set((props.selectedInventory || []).map(i => i.toUpperCase()));
  return BAG_SUGGESTION_RULES.filter(r => r.check(invSet)).slice(0, 3);
});

function handleGenerate() {
  if (!promptText.value.trim()) return;
  emit('generate', promptText.value.trim());
}
</script>
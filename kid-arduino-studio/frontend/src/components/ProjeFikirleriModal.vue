<template>
  <div v-if="isOpen">
    <!-- Karartma Arka Planı -->
    <div
      class="fixed inset-0 z-50 bg-slate-900/60 backdrop-blur-xs flex items-center justify-center p-2 sm:p-4 select-none"
      @click.self="$emit('close')"
    >
      <!-- Modal Kutusu -->
      <div class="bg-white rounded-[32px] border-[3px] border-slate-900 shadow-[0_12px_0_rgba(15,23,42,0.3)] max-w-5xl w-full overflow-hidden flex flex-col max-h-[92vh] animate-in fade-in zoom-in-95 duration-150">
        
        <!-- ÜST BAŞLIK ÇUBUĞU -->
        <div class="px-5 py-3.5 bg-gradient-to-r from-[#fde047] via-[#facc15] to-[#fb923c] border-b-[3px] border-slate-900 flex items-center justify-between shrink-0">
          <div class="flex items-center gap-3">
            <div class="w-10 h-10 rounded-2xl bg-white border-2 border-slate-900 shadow-xs flex items-center justify-center text-2xl">
              💡
            </div>
            <div>
              <h2 class="text-base sm:text-xl font-black text-slate-950 tracking-tight leading-tight">
                Proje Fikirleri Atölyesi
              </h2>
              <span class="text-[11px] font-bold text-slate-900/80">
                Elindeki malzemelerle yapabileceğin harika robotik projeler (Çantanda {{ selectedInventory.length }} parça var)
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
          <!-- Kategori Butonları -->
          <div class="flex items-center gap-1.5 overflow-x-auto py-0.5">
            <button
              v-for="filter in filterOptions"
              :key="filter.id"
              type="button"
              @click="activeFilter = filter.id"
              :class="[
                'px-3 py-1 rounded-xl text-xs font-black transition cursor-pointer whitespace-nowrap border-2 border-slate-900',
                activeFilter === filter.id
                  ? 'bg-amber-400 text-slate-950 shadow-[0_2px_0_#b45309]'
                  : 'bg-white text-slate-700 hover:bg-slate-100 shadow-2xs'
              ]"
            >
              <span>{{ filter.icon }}</span>
              <span class="ml-1">{{ filter.label }}</span>
              <span class="ml-1 text-[10px] opacity-75">({{ getFilterCount(filter.id) }})</span>
            </button>
          </div>

          <!-- Malzeme Çantamı Düzenle Butonu -->
          <button
            type="button"
            @click="$emit('open-inventory')"
            class="px-3 py-1 rounded-xl bg-[#e2d5c3] hover:bg-[#d6c5b0] border-2 border-slate-900 text-slate-900 text-xs font-black shadow-xs cursor-pointer active:translate-y-0.5 transition flex items-center gap-1"
          >
            <span>🧰</span>
            <span>Malzeme Çantamı Aç</span>
          </button>
        </div>

        <!-- PROJE KARTLARI LİSTESİ -->
        <div class="p-4 sm:p-5 overflow-y-auto flex-1 bg-slate-100/60">
          <div v-if="filteredProjects.length === 0" class="text-center py-12 flex flex-col items-center gap-2">
            <span class="text-4xl">🔍</span>
            <span class="text-sm font-black text-slate-700">Bu kategoride gösterilecek proje bulunamadı.</span>
            <span class="text-xs font-bold text-slate-500">Malzeme çantana birkaç sensör ve LED ekleyerek yeni fikirler keşfedebilirsin!</span>
          </div>

          <div class="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-3.5">
            <div
              v-for="project in filteredProjects"
              :key="project.id"
              class="bg-white rounded-2xl border-2 border-slate-900 p-4 shadow-[0_4px_0_#0f172a] flex flex-col justify-between gap-3 hover:-translate-y-0.5 transition-all"
            >
              <!-- Kart Üstü: Başlık & Durum Rozeti -->
              <div class="flex flex-col gap-1.5">
                <div class="flex items-start justify-between gap-2">
                  <div class="flex items-center gap-2">
                    <span class="text-2xl p-1.5 rounded-xl bg-amber-50 border border-slate-900 shadow-2xs">{{ project.icon }}</span>
                    <div>
                      <h3 class="text-xs sm:text-sm font-black text-slate-900 leading-tight">
                        {{ project.title }}
                      </h3>
                      <div class="flex items-center gap-1.5 mt-0.5">
                        <span class="text-[10px] font-black text-amber-700">{{ project.difficulty }}</span>
                        <span class="text-slate-300">•</span>
                        <span class="text-[10px] font-bold text-slate-500">{{ project.category }}</span>
                      </div>
                    </div>
                  </div>

                  <!-- Çantada Durum Rozeti -->
                  <span
                    v-if="project.isReady"
                    class="px-2 py-0.5 rounded-full bg-emerald-100 border border-emerald-600 text-[10px] font-black text-emerald-950 shrink-0 flex items-center gap-1"
                  >
                    <span>✓</span>
                    <span>Hemen Yap!</span>
                  </span>
                  <span
                    v-else
                    class="px-2 py-0.5 rounded-full bg-amber-100 border border-amber-600 text-[10px] font-black text-amber-950 shrink-0"
                  >
                    {{ project.missingCount }} Parça Eksik
                  </span>
                </div>

                <!-- Açıklama -->
                <p class="text-xs text-slate-600 font-bold leading-relaxed mt-1">
                  {{ project.description }}
                </p>
              </div>

              <!-- Kart İçi: Parça Durumu -->
              <div class="p-2.5 rounded-xl bg-slate-50 border border-slate-200 flex flex-col gap-1.5">
                <span class="text-[10px] font-black text-slate-700 uppercase tracking-wider">Gereken Parçalar:</span>
                <div class="flex flex-wrap gap-1">
                  <span
                    v-for="part in project.parts"
                    :key="part.name"
                    :class="[
                      'px-2 py-0.5 rounded-md text-[10px] font-black flex items-center gap-1 border',
                      part.inBag
                        ? 'bg-emerald-50 text-emerald-950 border-emerald-300'
                        : 'bg-rose-50 text-rose-950 border-rose-300'
                    ]"
                  >
                    <span>{{ part.inBag ? '✓' : '✗' }}</span>
                    <span>{{ part.name }}</span>
                  </span>
                </div>
              </div>

              <!-- Kart Altı: Projeyi Başlat Butonu -->
              <button
                type="button"
                @click="startProject(project)"
                class="w-full py-2.5 px-3 rounded-xl bg-[#4ade80] hover:bg-[#22c55e] border-2 border-slate-900 text-slate-950 text-xs font-black transition cursor-pointer shadow-[0_3px_0_#15803d] active:translate-y-0.5 active:shadow-none flex items-center justify-center gap-1.5"
              >
                <span>🚀</span>
                <span>Bu Projeyi Başlat</span>
              </button>
            </div>
          </div>
        </div>

        <!-- ALT ÇUBUK -->
        <div class="p-3 bg-white border-t-2 border-slate-900 flex items-center justify-between text-xs font-bold text-slate-600 shrink-0">
          <span>💡 Seçtiğin projeye tıkladığında gerekli parçalar çantana eklenir ve doğrudan 1. Hayal Et ekranına aktarılır.</span>
          <button
            type="button"
            @click="$emit('close')"
            class="px-4 py-1.5 rounded-xl bg-slate-100 hover:bg-slate-200 border-2 border-slate-900 text-slate-800 font-black cursor-pointer shadow-xs active:translate-y-0.5"
          >
            Kapat
          </button>
        </div>

      </div>
    </div>
  </div>
</template>

<script setup lang="ts">
import { ref, computed } from 'vue';

const props = defineProps<{
  isOpen: boolean;
  selectedInventory: string[];
}>();

const emit = defineEmits<{
  (e: 'close'): void;
  (e: 'open-inventory'): void;
  (e: 'use-idea', payload: { inventory: string[]; prompt: string }): void;
}>();

const activeFilter = ref('all');

const filterOptions = [
  { id: 'all', icon: '🌟', label: 'Tüm Fikirler' },
  { id: 'ready', icon: '🟢', label: 'Hemen Yapabileceklerin' },
  { id: 'almost', icon: '🟡', label: '1 Parça Eksikle' },
  { id: 'sensors', icon: '📡', label: 'Sensörlü' },
  { id: 'robotics', icon: '🦾', label: 'Robotik & Motor' }
];

interface RawProjectIdea {
  id: string;
  icon: string;
  title: string;
  category: string;
  difficulty: string;
  description: string;
  requiredKeys: string[];
  partsNames: string[];
  prompt: string;
}

const PROJECT_IDEAS: RawProjectIdea[] = [
  {
    id: 'sunflower-2ldr',
    icon: '🌻',
    title: 'Günebakan Çiçek (2 LDR + Servo)',
    category: 'Robotik',
    difficulty: '⭐⭐ Orta',
    description: 'Tıpkı gerçek bir ayçiçeği gibi, iki LDR sensöründen hangisine daha çok ışık geliyorsa servo motor o yöne döner!',
    requiredKeys: ['LDR_DISCRETE', 'SERVO_SG90'],
    partsNames: ['2x 2 Bacaklı LDR', '2x 10kΩ Direnç', 'SG90 Servo'],
    prompt: '2 bacaklı ldr sensörü ile günebakan projesi yapmak istiyorum. 2 tane ldr sensörüm var. hangisinden ışık fazla geliyorsa servo motor o yöne doğru hareket etmeli.'
  },
  {
    id: 'parking-sensor',
    icon: '🦇',
    title: 'Yarasa Kulaklı Akıllı Park Radarı',
    category: 'Sensörlü',
    difficulty: '⭐ Kolay',
    description: 'HC-SR04 mesafe sensörü tıpkı bir yarasa gibi ses yankısıyla engeli fark eder; 15 cm yaklaşıldığında buzzer ve kırmızı LED uyarır!',
    requiredKeys: ['HCSR04', 'BUZZER', 'LED_RED'],
    partsNames: ['HC-SR04 Mesafe', 'Buzzer', 'Kırmızı LED', '220Ω Direnç'],
    prompt: 'HC-SR04 ultrasonik mesafe sensörü ile 15 cm yaklaşınca buzzer sesli uyarı versin ve kırmızı LED yansın.'
  },
  {
    id: 'night-lamp',
    icon: '🌙',
    title: 'Otomatik Gece Lambası',
    category: 'Sensörlü',
    difficulty: '⭐ Başlangıç',
    description: 'Hava karardığında LDR sensörü bunu hisseder ve sarı gece lambasını otomatik yakar; aydınlık olunca söndürür.',
    requiredKeys: ['LDR_DISCRETE', 'LED_YELLOW'],
    partsNames: ['LDR Işık Sensörü', '10kΩ Direnç', 'Sarı LED', '220Ω Direnç'],
    prompt: 'LDR ışık sensörü ile ortam karanlık olduğunda sarı LED yansın, aydınlık olduğunda LED sönsün.'
  },
  {
    id: 'smart-barrier',
    icon: '🚧',
    title: 'Akıllı Otopark Bariyeri',
    category: 'Robotik',
    difficulty: '⭐⭐ Orta',
    description: 'Mesafe sensörü yaklaşan aracı görünce SG90 servo motor bariyeri 90 derece yukarı kaldırarak yolu açar.',
    requiredKeys: ['HCSR04', 'SERVO_SG90'],
    partsNames: ['HC-SR04 Mesafe Sensörü', 'SG90 Servo Motor'],
    prompt: 'HC-SR04 mesafe sensörü önüne araç yaklaştığında SG90 servo motor bariyeri 90 derece açsın.'
  },
  {
    id: 'morning-alarm',
    icon: '⏰',
    title: 'Güneş Doğdu Sabah Alarmı',
    category: 'Sensörlü',
    difficulty: '⭐ Başlangıç',
    description: 'Sabah güneş doğup oda aydınlandığında LDR sensörü uyanır ve neşeli bir bip uyarısı ile seni uyandırır!',
    requiredKeys: ['LDR_DISCRETE', 'BUZZER'],
    partsNames: ['LDR Işık Sensörü', '10kΩ Direnç', 'Buzzer'],
    prompt: 'LDR ışık sensörü üzerine güçlü ışık düştüğünde buzzer ile sabah uyandırma alarmı çalsın.'
  },
  {
    id: 'button-door',
    icon: '🚪',
    title: 'Butonlu Akıllı Kapı Kilidi',
    category: 'Robotik',
    difficulty: '⭐ Kolay',
    description: 'Push butona basıldığında servo motor kapı mandalını 90 derece açar, parmağını çekince kapatır.',
    requiredKeys: ['PUSH_BUTTON', 'SERVO_SG90'],
    partsNames: ['Push Buton', '10kΩ Direnç', 'SG90 Servo Motor'],
    prompt: 'Push butona basıldığında SG90 servo motor 90 derece dönerek kapıyı açsın, bırakıldığında kapatsın.'
  },
  {
    id: 'pot-servo',
    icon: '🦾',
    title: 'Potansiyometre ile Robot Kol',
    category: 'Robotik',
    difficulty: '⭐ Kolay',
    description: 'Potansiyometre başlığını çevirdikçe servo motor 0 ile 180 derece arasında parmağının hareketini takip eder.',
    requiredKeys: ['POTENTIOMETER', 'SERVO_SG90'],
    partsNames: ['Potansiyometre', 'SG90 Servo Motor'],
    prompt: '10k potansiyometreyi çevirdikçe SG90 servo motorun açısı 0 ile 180 derece arasında dönsün.'
  },
  {
    id: 'traffic-lights',
    icon: '🚦',
    title: '3 Renkli Akıllı Trafik Lambası',
    category: 'Temel',
    difficulty: '⭐ Başlangıç',
    description: 'Kırmızı, sarı ve yeşil LED ışıklar gerçek trafik kurallarına göre sırayla yanıp söner.',
    requiredKeys: ['LED_RED', 'LED_YELLOW', 'LED_GREEN'],
    partsNames: ['Kırmızı LED', 'Sarı LED', 'Yeşil LED', '3x 220Ω Direnç'],
    prompt: 'Kırmızı, sarı ve yeşil LED ışıklar ile gerçek trafik lambası yap. Sırayla kırmızı yansın, sarı yansın, yeşil yansın.'
  },
  {
    id: 'pir-alarm',
    icon: '🚶',
    title: 'PIR Hareket Sensörlü Dedektör',
    category: 'Sensörlü',
    difficulty: '⭐ Kolay',
    description: 'Odaya birisi girdiğinde canlıların vücut ısısını hissederek buzzer ile siren çalar ve kırmızı ikaz LED\'i yakar.',
    requiredKeys: ['PIR_MOTION_SENSOR', 'BUZZER', 'LED_RED'],
    partsNames: ['PIR Hareket Sensörü', 'Buzzer', 'Kırmızı LED'],
    prompt: 'PIR hareket sensörü bir hareket gördüğünde buzzer alarm çalsın ve kırmızı LED yansın.'
  },
  {
    id: 'bluetooth-car',
    icon: '🚗',
    title: 'Bluetooth ile Kontrol Edilen Araba',
    category: 'Robotik',
    difficulty: '⭐⭐⭐ İleri Seviye',
    description: 'HC-05 bluetooth modülü ve L293D motor sürücü ile telefonundan kablosuz kontrol edebileceğin 2 motorlu araba!',
    requiredKeys: ['BLUETOOTH_HC05', 'MOTOR_DRIVER_L293D', 'DC_MOTOR_5V'],
    partsNames: ['HC-05 Bluetooth', 'L293D Motor Sürücü', '2x DC Motor'],
    prompt: 'HC-05 bluetooth modülü ve L293D motor sürücü ile iki DC motoru ileri, geri ve sağa sola kontrol eden araba devresi yap.'
  },
  {
    id: 'plant-watering',
    icon: '🌱',
    title: 'Konuşan Çiçek (Toprak Nem Alarmı)',
    category: 'Sensörlü',
    difficulty: '⭐ Kolay',
    description: 'Saksıdaki toprak kuruduğunda toprak nem sensörü fark eder ve "Bana su ver!" diye buzzer öttürür.',
    requiredKeys: ['SOIL_MOISTURE_SENSOR', 'BUZZER'],
    partsNames: ['Toprak Nem Sensörü', 'Buzzer', 'Kırmızı LED'],
    prompt: 'Toprak nem sensörü ile toprak kuruduğunda buzzer uyarı versin ve kırmızı LED yansın.'
  },
  {
    id: 'rain-shutter',
    icon: '🌧️',
    title: 'Akıllı Pencere Yağmur Kapatıcı',
    category: 'Sensörlü',
    difficulty: '⭐⭐ Orta',
    description: 'Pencereye ilk yağmur damlası düştüğünde servo motor pencereyi kapatır ve buzzer alarm çalar.',
    requiredKeys: ['RAIN_SENSOR', 'SERVO_SG90'],
    partsNames: ['Yağmur Sensörü', 'SG90 Servo Motor', 'Buzzer'],
    prompt: 'Yağmur sensörüne su damladığında buzzer ötsün ve servo motor 90 derece dönerek pencereyi kapatsın.'
  }
];

const processedProjects = computed(() => {
  const invSet = new Set((props.selectedInventory || []).map(i => i.toUpperCase()));
  // LDR_SENSOR veya LDR_MODULE varsa LDR_DISCRETE de eşleşsin
  if (invSet.has('LDR_SENSOR') || invSet.has('LDR_MODULE')) {
    invSet.add('LDR_DISCRETE');
  }

  return PROJECT_IDEAS.map(idea => {
    let missingCount = 0;
    const partsWithStatus = idea.requiredKeys.map((k, idx) => {
      const inBag = invSet.has(k);
      if (!inBag) missingCount++;
      return {
        key: k,
        name: idea.partsNames[idx] || k,
        inBag
      };
    });

    return {
      ...idea,
      parts: partsWithStatus,
      isReady: missingCount === 0,
      missingCount
    };
  });
});

const filteredProjects = computed(() => {
  return processedProjects.value.filter(p => {
    if (activeFilter.value === 'ready') return p.isReady;
    if (activeFilter.value === 'almost') return p.missingCount === 1;
    if (activeFilter.value === 'sensors') return p.category === 'Sensörlü';
    if (activeFilter.value === 'robotics') return p.category === 'Robotik';
    return true;
  });
});

function getFilterCount(filterId: string): number {
  if (filterId === 'all') return processedProjects.value.length;
  if (filterId === 'ready') return processedProjects.value.filter(p => p.isReady).length;
  if (filterId === 'almost') return processedProjects.value.filter(p => p.missingCount === 1).length;
  if (filterId === 'sensors') return processedProjects.value.filter(p => p.category === 'Sensörlü').length;
  if (filterId === 'robotics') return processedProjects.value.filter(p => p.category === 'Robotik').length;
  return 0;
}

function startProject(project: typeof processedProjects.value[0]) {
  // Eğer eksik parçalar varsa kullanıcı için otomatik çantaya da ekle
  const fullInvSet = new Set([...props.selectedInventory]);
  for (const p of project.parts) {
    fullInvSet.add(p.key);
  }
  emit('use-idea', {
    inventory: Array.from(fullInvSet),
    prompt: project.prompt
  });
  emit('close');
}
</script>

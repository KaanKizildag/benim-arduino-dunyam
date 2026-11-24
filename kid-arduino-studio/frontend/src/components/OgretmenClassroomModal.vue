<template>
  <div
    v-if="isOpen"
    class="fixed inset-0 z-50 flex items-center justify-center p-3 sm:p-5 bg-slate-900/60 backdrop-blur-xs select-none"
    @click.self="$emit('close')"
  >
    <div
      class="bg-[#f8fafc] border-[3px] border-slate-900 rounded-[32px] w-full max-w-5xl shadow-[0_12px_0_#0f172a] flex flex-col overflow-hidden max-h-[92vh] animate-in fade-in zoom-in-95 duration-200"
    >
      <!-- Üst Başlık & Sınıf Seçimi -->
      <div class="bg-[#4ade80] p-4 sm:p-5 border-b-[3px] border-slate-900 flex items-center justify-between">
        <div class="flex items-center gap-3">
          <div class="w-12 h-12 rounded-2xl bg-white border-2 border-slate-900 shadow-[0_3px_0_#15803d] flex items-center justify-center text-2xl">
            👩‍🏫
          </div>
          <div>
            <div class="flex items-center gap-2">
              <h2 class="text-xl font-black text-slate-900">
                Öğretmen Sınıf & Onay Paneli
              </h2>
              <span
                v-if="selectedClass"
                class="px-2.5 py-0.5 rounded-lg bg-white border border-slate-900 text-xs font-black text-slate-800"
              >
                {{ selectedClass.name }} Sınıfı
              </span>
            </div>
            <p class="text-xs font-bold text-emerald-950/80">
              Sınıf Arduino Envanteri Yönetimi, Devre Fiziksel Kontrolü & Medya Yükleme
            </p>
          </div>
        </div>

        <button
          type="button"
          @click="$emit('close')"
          class="w-9 h-9 rounded-xl bg-white hover:bg-rose-100 border-2 border-slate-900 shadow-[0_3px_0_#0f172a] active:translate-y-0.5 text-slate-800 font-black text-sm flex items-center justify-center cursor-pointer transition"
        >
          ✕
        </button>
      </div>

      <!-- Sınıf Değiştirme ve Sekmeler -->
      <div class="flex items-center justify-between px-4 sm:px-6 pt-3 bg-white border-b-2 border-slate-200 flex-wrap gap-2">
        <div class="flex items-center gap-2">
          <!-- Sekme Butonları -->
          <button
            type="button"
            @click="activeTab = 'projects'"
            :class="[
              'px-4 py-2 rounded-t-xl font-black text-xs sm:text-sm border-t-2 border-x-2 cursor-pointer transition flex items-center gap-1.5',
              activeTab === 'projects'
                ? 'bg-[#f8fafc] text-slate-900 border-slate-900 -mb-[2px] shadow-[0_-2px_0_#0f172a]'
                : 'bg-slate-100 text-slate-600 border-transparent hover:bg-slate-200'
            ]"
          >
            <span>🔌</span>
            <span>Öğrenci Projeleri & Onay Masası</span>
            <span class="px-1.5 py-0.2 rounded-full bg-emerald-500 text-white text-[10px] font-black">
              {{ studentProjects.length }}
            </span>
          </button>

          <button
            type="button"
            @click="activeTab = 'inventory'"
            :class="[
              'px-4 py-2 rounded-t-xl font-black text-xs sm:text-sm border-t-2 border-x-2 cursor-pointer transition flex items-center gap-1.5',
              activeTab === 'inventory'
                ? 'bg-[#f8fafc] text-slate-900 border-slate-900 -mb-[2px] shadow-[0_-2px_0_#0f172a]'
                : 'bg-slate-100 text-slate-600 border-transparent hover:bg-slate-200'
            ]"
          >
            <span>🧰</span>
            <span>Sınıf Kiti Envanteri</span>
          </button>
        </div>

        <!-- Sınıf Seçimi -->
        <div v-if="classes.length > 0" class="flex items-center gap-1.5 pb-2">
          <span class="text-xs font-black text-slate-600">Sınıf:</span>
          <select
            v-model="selectedClassId"
            @change="handleClassChange"
            class="px-2.5 py-1 rounded-xl border-2 border-slate-900 text-xs font-black bg-emerald-50 text-slate-800 outline-none"
          >
            <option v-for="c in classes" :key="c.id" :value="c.id">
              {{ c.name }} ({{ c.grade_level }}. Sınıf)
            </option>
          </select>
        </div>
      </div>

      <!-- Ana İçerik -->
      <div class="p-4 sm:p-6 overflow-y-auto flex-1 bg-[#f8fafc]">
        
        <!-- Bildirim Mesajı -->
        <div
          v-if="statusMessage"
          :class="[
            'p-3 mb-4 rounded-2xl border-2 text-xs font-black flex items-center gap-2',
            statusMessage.type === 'success'
              ? 'bg-emerald-100 border-emerald-500 text-emerald-900'
              : 'bg-rose-100 border-rose-500 text-rose-900'
          ]"
        >
          <span>{{ statusMessage.type === 'success' ? '✅' : '⚠️' }}</span>
          <span>{{ statusMessage.text }}</span>
        </div>

        <!-- 1. TAB: ÖĞRENCİ PROJELERİ & ONAY MASASI -->
        <div v-if="activeTab === 'projects'" class="space-y-4">
          <div v-if="studentProjects.length === 0" class="p-8 text-center bg-white rounded-3xl border-2 border-dashed border-slate-300">
            <div class="text-4xl mb-2">👦✨</div>
            <div class="text-sm font-black text-slate-700">Henüz Bu Sınıfta Kaydedilmiş Öğrenci Projesi Yok</div>
            <p class="text-xs text-slate-500 mt-1">Öğrenciler Arduino projelerini tamamlayıp kaydettikçe burada listelenecektir.</p>
          </div>

          <div
            v-for="p in studentProjects"
            :key="p.id"
            class="bg-white rounded-2xl border-2 border-slate-900 shadow-[0_3px_0_#94a3b8] p-4 flex flex-col md:flex-row gap-4"
          >
            <!-- Sol: Proje Detayları -->
            <div class="flex-1 space-y-2">
              <div class="flex items-center gap-2 flex-wrap">
                <span class="text-lg">💡</span>
                <h4 class="font-black text-sm text-slate-900">{{ p.title || 'İsimsiz Proje' }}</h4>
                <span class="px-2 py-0.5 rounded-lg bg-sky-100 border border-slate-900 text-[10px] font-black text-sky-900">
                  {{ p.student_name }} (No: {{ p.student_no }})
                </span>
                <span class="text-[10px] text-slate-400 font-bold">
                  {{ new Date(p.created_at).toLocaleDateString('tr-TR') }}
                </span>
              </div>

              <!-- Parçalar / Netlist Özeti -->
              <div class="text-xs text-slate-600 font-bold bg-slate-50 p-2.5 rounded-xl border border-slate-200">
                <span class="text-[10px] uppercase font-black text-slate-400 block mb-1">Kullanılan Parçalar:</span>
                <span v-if="p.components && p.components.length > 0">
                  {{ p.components.join(', ') }}
                </span>
                <span v-else class="text-slate-400 italic">Arduino Uno, Breadboard ve temel bileşenler</span>
              </div>

              <!-- Onay Durumu Rozeti -->
              <div class="flex items-center gap-2 pt-1">
                <span
                  :class="[
                    'px-2.5 py-1 rounded-xl border text-xs font-black flex items-center gap-1',
                    p.is_circuit_approved
                      ? 'bg-emerald-100 border-emerald-500 text-emerald-900'
                      : 'bg-amber-100 border-amber-500 text-amber-900'
                  ]"
                >
                  <span>{{ p.is_circuit_approved ? '✅' : '⏳' }}</span>
                  <span>{{ p.is_circuit_approved ? 'Fiziksel Devre Onaylandı' : 'Fiziksel Kontrol Bekliyor' }}</span>
                </span>

                <button
                  v-if="!p.is_circuit_approved"
                  type="button"
                  @click="handleApproveCircuit(p.id, true)"
                  class="px-3 py-1 bg-[#4ade80] hover:bg-[#22c55e] border-2 border-slate-900 shadow-[0_2px_0_#15803d] active:translate-y-0.5 rounded-xl text-xs font-black text-slate-900 cursor-pointer transition"
                >
                  Devreyi Masasında Kontrol Ettim & Onayla! ⚡
                </button>
              </div>

              <div v-if="p.circuit_approved_notes" class="text-[11px] text-emerald-700 font-bold italic">
                Öğretmen Notu: "{{ p.circuit_approved_notes }}"
              </div>
            </div>

            <!-- Sağ: Rozet Takma & Medya (Fotoğraf/Video) Yükleme -->
            <div class="md:w-72 bg-slate-50 p-3 rounded-xl border border-slate-200 flex flex-col justify-between gap-3">
              <!-- Rozet & Geri Bildirim -->
              <div>
                <span class="text-[10px] uppercase font-black text-slate-500 block mb-1">
                  Öğrenciye Rozet & Tebrik:
                </span>
                <div class="flex items-center gap-1 mb-2">
                  <select
                    v-model="feedbackForms[p.id].badge"
                    class="flex-1 px-2 py-1 rounded-lg border border-slate-900 text-xs font-black bg-white"
                  >
                    <option value="🚀 Usta Mucit">🚀 Usta Mucit</option>
                    <option value="⚡ Harika Devre">⚡ Harika Devre</option>
                    <option value="💡 Temiz Kod">💡 Temiz Kod</option>
                    <option value="🎯 Sorun Çözücü">🎯 Sorun Çözücü</option>
                    <option value="🌟 Süper Başarı">🌟 Süper Başarı</option>
                  </select>
                  <button
                    type="button"
                    @click="handleSaveFeedback(p.id)"
                    class="px-2.5 py-1 bg-amber-300 hover:bg-amber-400 border border-slate-900 rounded-lg text-xs font-black text-slate-900 cursor-pointer"
                  >
                    Kaydet
                  </button>
                </div>
                <input
                  v-model="feedbackForms[p.id].notes"
                  placeholder="Kısa tebrik notu (Aferin Can!)"
                  class="w-full px-2 py-1 rounded-lg border border-slate-300 text-xs font-bold bg-white"
                />
              </div>

              <!-- Çalışan Devre Videosu / Fotoğraf Yükleme -->
              <div class="pt-2 border-t border-slate-200">
                <span class="text-[10px] uppercase font-black text-slate-500 block mb-1">
                  📹 Çalışan Devre Videosu / Fotoğrafı:
                </span>
                <div class="flex items-center gap-1.5">
                  <input
                    type="file"
                    :id="`file-upload-${p.id}`"
                    accept="video/*,image/*"
                    class="hidden"
                    @change="handleFileUpload($event, p.id)"
                  />
                  <label
                    :for="`file-upload-${p.id}`"
                    class="flex-1 py-1.5 px-2 bg-sky-100 hover:bg-sky-200 border border-slate-900 rounded-lg text-center text-xs font-black text-slate-800 cursor-pointer transition flex items-center justify-center gap-1"
                  >
                    <span>📷</span>
                    <span>Video/Fotoğraf Seç</span>
                  </label>
                </div>
                <span class="text-[9px] text-slate-400 block mt-0.5">
                  Yalnızca veli ve öğrenciye özel kapalı devre saklanır.
                </span>
              </div>
            </div>
          </div>
        </div>

        <!-- 2. TAB: SINIF ARDUINO KİTİ ENVANTERİ -->
        <div v-else class="space-y-4">
          <div class="bg-white p-4 rounded-2xl border-2 border-slate-900 shadow-[0_3px_0_#94a3b8]">
            <div class="flex items-center justify-between mb-3">
              <div>
                <h3 class="text-sm font-black text-slate-900 flex items-center gap-1.5">
                  <span>🧰</span>
                  <span>Sınıfta Bulunan Donanım Parçalarını Seç</span>
                </h3>
                <p class="text-xs text-slate-500 font-bold">
                  İşaretlediğiniz parçalar, öğrencilerinizin proje üretiminde varsayılan olarak kullanılacaktır.
                </p>
              </div>
              <button
                type="button"
                @click="handleSaveInventory"
                class="px-4 py-2 bg-[#4ade80] hover:bg-[#22c55e] border-2 border-slate-900 shadow-[0_3px_0_#15803d] active:translate-y-0.5 rounded-xl text-xs font-black text-slate-900 cursor-pointer transition"
              >
                Sınıf Envanterini Kaydet 💾
              </button>
            </div>

            <!-- Parça Seçim Grid'i -->
            <div class="grid grid-cols-2 sm:grid-cols-3 md:grid-cols-4 gap-2 pt-2">
              <label
                v-for="item in allAvailableComponents"
                :key="item.name"
                :class="[
                  'p-2.5 rounded-xl border-2 cursor-pointer transition select-none flex items-center gap-2 text-xs font-bold',
                  selectedClassInventory.includes(item.name)
                    ? 'bg-emerald-50 border-emerald-500 text-emerald-950 shadow-xs'
                    : 'bg-white border-slate-200 text-slate-600 hover:border-slate-400'
                ]"
              >
                <input
                  type="checkbox"
                  :value="item.name"
                  v-model="selectedClassInventory"
                  class="rounded text-emerald-600 focus:ring-emerald-500"
                />
                <span>{{ item.icon }}</span>
                <span>{{ item.name }}</span>
              </label>
            </div>
          </div>
        </div>

      </div>
    </div>
  </div>
</template>

<script setup lang="ts">
import { ref, reactive, computed, onMounted, watch } from 'vue';
import { useAuth } from '../composables/useAuth';

const props = defineProps<{
  isOpen: boolean;
}>();

const emit = defineEmits<{
  (e: 'close'): void;
}>();

const { getAuthHeaders } = useAuth();

const activeTab = ref<'projects' | 'inventory'>('projects');
const classes = ref<any[]>([]);
const selectedClassId = ref<string>('');
const studentProjects = ref<any[]>([]);
const statusMessage = ref<{ type: 'success' | 'error'; text: string } | null>(null);

const feedbackForms = reactive<Record<string, { badge: string; notes: string }>>({});

const allAvailableComponents = [
  { name: 'Arduino Uno', icon: '🧠' },
  { name: 'Breadboard', icon: '🍞' },
  { name: 'Kırmızı LED', icon: '🔴' },
  { name: 'Yeşil LED', icon: '🟢' },
  { name: 'Sarı LED', icon: '🟡' },
  { name: 'Mavi LED', icon: '🔵' },
  { name: 'RGB LED', icon: '🌈' },
  { name: '220Ω Direnç', icon: '⚡' },
  { name: '10kΩ Direnç', icon: '⚡' },
  { name: 'Push Buton', icon: '🔘' },
  { name: 'Buzzer (Hoparlör)', icon: '📢' },
  { name: 'Ultrasonik Sensör (HC-SR04)', icon: '🦇' },
  { name: 'Servo Motor (SG90)', icon: '🦾' },
  { name: 'Potansiyometre', icon: '🎛️' },
  { name: 'Işık Sensörü (LDR)', icon: '☀️' },
  { name: 'Sıcaklık Sensörü (DHT11)', icon: '🌡️' },
  { name: 'Hareket Sensörü (PIR)', icon: '🚶' },
  { name: 'LCD Ekran 16x2 I2C', icon: '📟' },
  { name: 'Toprak Nem Sensörü', icon: '🌱' },
  { name: 'Jumper Kablolar', icon: '〰️' },
];

const selectedClassInventory = ref<string[]>([
  'Arduino Uno',
  'Breadboard',
  'Kırmızı LED',
  'Yeşil LED',
  '220Ω Direnç',
  'Push Buton',
  'Buzzer (Hoparlör)',
  'Ultrasonik Sensör (HC-SR04)',
  'Servo Motor (SG90)',
  'Jumper Kablolar'
]);

const selectedClass = computed(() => {
  return classes.value.find((c) => c.id === selectedClassId.value);
});

async function fetchClasses() {
  try {
    const res = await fetch('/api/teacher/classes', {
      headers: getAuthHeaders()
    });
    if (res.ok) {
      const data = await res.json();
      classes.value = data;
      if (data.length > 0 && !selectedClassId.value) {
        selectedClassId.value = data[0].id;
        if (data[0].inventory_json) {
          try {
            selectedClassInventory.value = JSON.parse(data[0].inventory_json);
          } catch {}
        }
      }
    }
  } catch (e) {
    console.error('Sınıflar yüklenemedi:', e);
  }
}

async function fetchProjects() {
  try {
    const res = await fetch('/api/teacher/projects', {
      headers: getAuthHeaders()
    });
    if (res.ok) {
      const data = await res.json();
      studentProjects.value = data;
      data.forEach((p: any) => {
        if (!feedbackForms[p.id]) {
          feedbackForms[p.id] = {
            badge: '🚀 Usta Mucit',
            notes: ''
          };
        }
      });
    }
  } catch (e) {
    console.error('Projeler yüklenemedi:', e);
  }
}

function handleClassChange() {
  const current = selectedClass.value;
  if (current && current.inventory_json) {
    try {
      selectedClassInventory.value = JSON.parse(current.inventory_json);
    } catch {}
  }
}

async function handleApproveCircuit(projectId: string, isApproved: boolean) {
  try {
    const res = await fetch('/api/teacher/approve-circuit', {
      method: 'POST',
      headers: { ...getAuthHeaders(), 'Content-Type': 'application/json' },
      body: JSON.stringify({
        project_id: projectId,
        is_approved: isApproved,
        teacher_notes: 'Fiziksel devre bağlantıları ve kutup kontrolleri öğretmen tarafından incelendi ve onaylandı.'
      })
    });
    const data = await res.json();
    if (!res.ok) throw new Error(data.detail || 'Onay işlemi başarısız');

    statusMessage.value = { type: 'success', text: 'Devre fiziksel kontrolü başarıyla onaylandı! ⚡' };
    await fetchProjects();
  } catch (e: any) {
    statusMessage.value = { type: 'error', text: e.message };
  }
}

async function handleSaveFeedback(projectId: string) {
  const form = feedbackForms[projectId];
  if (!form) return;
  try {
    const res = await fetch('/api/teacher/feedback', {
      method: 'POST',
      headers: { ...getAuthHeaders(), 'Content-Type': 'application/json' },
      body: JSON.stringify({
        project_id: projectId,
        badge: form.badge,
        feedback_text: form.notes || 'Harika bir çalışma, tebrikler!'
      })
    });
    const data = await res.json();
    if (!res.ok) throw new Error(data.detail || 'Rozet kaydedilemedi');

    statusMessage.value = { type: 'success', text: 'Öğrenciye rozet ve tebrik notu başarıyla iletildi! 🌟' };
  } catch (e: any) {
    statusMessage.value = { type: 'error', text: e.message };
  }
}

async function handleFileUpload(event: Event, projectId: string) {
  const target = event.target as HTMLInputElement;
  if (!target.files || target.files.length === 0) return;
  const file = target.files[0];
  const isVideo = file.type.startsWith('video');

  const formData = new FormData();
  formData.append('file', file);
  formData.append('project_id', projectId);
  formData.append('media_type', isVideo ? 'video' : 'photo');

  try {
    const res = await fetch('/api/media/upload', {
      method: 'POST',
      headers: getAuthHeaders(),
      body: formData
    });
    const data = await res.json();
    if (!res.ok) throw new Error(data.detail || 'Medya yüklenemedi');

    statusMessage.value = {
      type: 'success',
      text: 'Çalışan devrenin videosu/fotoğrafı başarıyla yüklendi! Veli portfolyosuna eklendi.'
    };
    await fetchProjects();
  } catch (e: any) {
    statusMessage.value = { type: 'error', text: e.message };
  }
}

async function handleSaveInventory() {
  if (!selectedClassId.value) return;
  try {
    const res = await fetch('/api/teacher/inventory', {
      method: 'POST',
      headers: { ...getAuthHeaders(), 'Content-Type': 'application/json' },
      body: JSON.stringify({
        class_id: selectedClassId.value,
        inventory: selectedClassInventory.value
      })
    });
    const data = await res.json();
    if (!res.ok) throw new Error(data.detail || 'Envanter kaydedilemedi');

    statusMessage.value = { type: 'success', text: 'Sınıf kiti envanteri güncellendi ve kaydedildi!' };
  } catch (e: any) {
    statusMessage.value = { type: 'error', text: e.message };
  }
}

watch(() => props.isOpen, (open) => {
  if (open) {
    statusMessage.value = null;
    fetchClasses();
    fetchProjects();
  }
});

onMounted(() => {
  if (props.isOpen) {
    fetchClasses();
    fetchProjects();
  }
});
</script>

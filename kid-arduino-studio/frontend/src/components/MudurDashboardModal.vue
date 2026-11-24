<template>
  <div
    v-if="isOpen"
    class="fixed inset-0 z-50 flex items-center justify-center p-3 sm:p-5 bg-slate-900/60 backdrop-blur-xs select-none"
    @click.self="$emit('close')"
  >
    <div
      class="bg-[#f8fafc] border-[3px] border-slate-900 rounded-[32px] w-full max-w-4xl shadow-[0_12px_0_#0f172a] flex flex-col overflow-hidden max-h-[90vh] animate-in fade-in zoom-in-95 duration-200"
    >
      <!-- Üst Başlık & Kurum Kodu -->
      <div class="bg-[#38bdf8] p-4 sm:p-5 border-b-[3px] border-slate-900 flex items-center justify-between">
        <div class="flex items-center gap-3">
          <div class="w-12 h-12 rounded-2xl bg-white border-2 border-slate-900 shadow-[0_3px_0_#0284c7] flex items-center justify-center text-2xl">
            🏫
          </div>
          <div>
            <div class="flex items-center gap-2">
              <h2 class="text-xl font-black text-slate-900">
                {{ overviewData?.institution?.name || 'Okul Müdürü Yönetim Paneli' }}
              </h2>
              <span
                v-if="overviewData?.institution?.code"
                class="px-2 py-0.5 rounded-lg bg-yellow-300 border border-slate-900 text-xs font-black text-slate-900"
              >
                KOD: {{ overviewData?.institution?.code }}
              </span>
            </div>
            <p class="text-xs font-bold text-sky-950/80">
              Kurum İçi Öğretmen, Sınıf, Öğrenci ve Veli Eşleştirme Merkezi
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

      <!-- İstatistik Sayaçları -->
      <div class="grid grid-cols-2 sm:grid-cols-4 gap-2.5 p-4 bg-sky-100/60 border-b-2 border-slate-900">
        <div class="bg-white p-2.5 rounded-2xl border-2 border-slate-900 shadow-[0_2px_0_#94a3b8] text-center">
          <div class="text-xs font-black text-slate-500">👩‍🏫 Öğretmenler</div>
          <div class="text-xl font-black text-slate-900">{{ overviewData?.teachers?.length || 0 }}</div>
        </div>
        <div class="bg-white p-2.5 rounded-2xl border-2 border-slate-900 shadow-[0_2px_0_#94a3b8] text-center">
          <div class="text-xs font-black text-slate-500">📚 Sınıflar</div>
          <div class="text-xl font-black text-slate-900">{{ overviewData?.classes?.length || 0 }}</div>
        </div>
        <div class="bg-white p-2.5 rounded-2xl border-2 border-slate-900 shadow-[0_2px_0_#94a3b8] text-center">
          <div class="text-xs font-black text-slate-500">👦 Öğrenciler</div>
          <div class="text-xl font-black text-slate-900">{{ overviewData?.students?.length || 0 }}</div>
        </div>
        <div class="bg-white p-2.5 rounded-2xl border-2 border-slate-900 shadow-[0_2px_0_#94a3b8] text-center">
          <div class="text-xs font-black text-slate-500">👨‍👩‍👧 Veli Eşleşmesi</div>
          <div class="text-xl font-black text-slate-900">{{ overviewData?.pairs?.length || 0 }}</div>
        </div>
      </div>

      <!-- Alt Sekmeler -->
      <div class="flex items-center gap-1.5 px-4 pt-3 border-b-2 border-slate-200 bg-white overflow-x-auto">
        <button
          v-for="tab in tabs"
          :key="tab.id"
          type="button"
          @click="currentTab = tab.id"
          :class="[
            'px-3.5 py-2 rounded-t-xl font-black text-xs sm:text-sm border-t-2 border-x-2 cursor-pointer transition whitespace-nowrap flex items-center gap-1.5',
            currentTab === tab.id
              ? 'bg-[#f8fafc] text-slate-900 border-slate-900 -mb-[2px] shadow-[0_-2px_0_#0f172a]'
              : 'bg-slate-100 text-slate-600 border-transparent hover:bg-slate-200'
          ]"
        >
          <span>{{ tab.icon }}</span>
          <span>{{ tab.label }}</span>
        </button>
      </div>

      <!-- Sekme İçerikleri -->
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

        <!-- 1. TAB: ÖĞRETMENLER -->
        <div v-if="currentTab === 'teachers'" class="space-y-4">
          <!-- Öğretmen Ekle Kartı -->
          <div class="bg-white p-4 rounded-2xl border-2 border-slate-900 shadow-[0_3px_0_#94a3b8]">
            <h3 class="text-sm font-black text-slate-900 mb-3 flex items-center gap-1.5">
              <span>➕</span>
              <span>Yeni Öğretmen Ekle</span>
            </h3>
            <form @submit.prevent="handleAddTeacher" class="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-4 gap-2.5">
              <input
                v-model="newTeacher.full_name"
                placeholder="Ad Soyad (Örn: Zeynep Kaya)"
                required
                class="px-3 py-2 rounded-xl border-2 border-slate-900 text-xs font-bold outline-none"
              />
              <input
                v-model="newTeacher.username"
                placeholder="Kullanıcı Adı"
                required
                class="px-3 py-2 rounded-xl border-2 border-slate-900 text-xs font-bold outline-none"
              />
              <input
                v-model="newTeacher.password"
                type="password"
                placeholder="Şifre"
                required
                class="px-3 py-2 rounded-xl border-2 border-slate-900 text-xs font-bold outline-none"
              />
              <input
                v-model="newTeacher.branch"
                placeholder="Branş (Bilişim / Fen)"
                class="px-3 py-2 rounded-xl border-2 border-slate-900 text-xs font-bold outline-none"
              />
              <button
                type="submit"
                class="col-span-1 sm:col-span-2 lg:col-span-4 py-2 bg-[#4ade80] hover:bg-[#22c55e] border-2 border-slate-900 shadow-[0_3px_0_#15803d] active:translate-y-0.5 rounded-xl text-xs font-black text-slate-900 cursor-pointer transition"
              >
                Öğretmeni Kaydet
              </button>
            </form>
          </div>

          <!-- Öğretmen Listesi -->
          <div class="bg-white rounded-2xl border-2 border-slate-900 shadow-[0_3px_0_#94a3b8] overflow-hidden">
            <div class="p-3 bg-slate-100 border-b-2 border-slate-900 font-black text-xs text-slate-800">
              Mevcut Öğretmenler
            </div>
            <div class="divide-y divide-slate-200">
              <div
                v-for="t in overviewData?.teachers"
                :key="t.id"
                class="p-3 flex items-center justify-between text-xs"
              >
                <div class="flex items-center gap-2.5">
                  <span class="text-lg">👩‍🏫</span>
                  <div>
                    <div class="font-black text-slate-900">{{ t.full_name }}</div>
                    <div class="text-[10px] text-slate-500">
                      @{{ t.username }} &bull; {{ t.branch || 'Genel' }}
                    </div>
                  </div>
                </div>
                <span class="px-2 py-0.5 rounded-lg bg-emerald-100 text-emerald-800 font-bold text-[10px]">
                  Aktif
                </span>
              </div>
            </div>
          </div>
        </div>

        <!-- 2. TAB: SINIFLAR & ATAMALAR -->
        <div v-else-if="currentTab === 'classes'" class="space-y-4">
          <!-- Sınıf Ekle Kartı -->
          <div class="bg-white p-4 rounded-2xl border-2 border-slate-900 shadow-[0_3px_0_#94a3b8]">
            <h3 class="text-sm font-black text-slate-900 mb-3 flex items-center gap-1.5">
              <span>➕</span>
              <span>Yeni Sınıf Oluştur & Öğretmen Ata</span>
            </h3>
            <form @submit.prevent="handleAddClass" class="grid grid-cols-1 sm:grid-cols-3 gap-2.5">
              <input
                v-model="newClass.name"
                placeholder="Sınıf Adı (Örn: 4-A)"
                required
                class="px-3 py-2 rounded-xl border-2 border-slate-900 text-xs font-bold outline-none"
              />
              <input
                v-model.number="newClass.grade_level"
                type="number"
                min="1"
                max="12"
                placeholder="Sınıf Düzeyi (Örn: 4)"
                required
                class="px-3 py-2 rounded-xl border-2 border-slate-900 text-xs font-bold outline-none"
              />
              <select
                v-model="newClass.teacher_id"
                class="px-3 py-2 rounded-xl border-2 border-slate-900 text-xs font-bold outline-none bg-white"
              >
                <option value="">-- Öğretmen Ata (Opsiyonel) --</option>
                <option v-for="t in overviewData?.teachers" :key="t.id" :value="t.id">
                  {{ t.full_name }} (@{{ t.username }})
                </option>
              </select>
              <button
                type="submit"
                class="sm:col-span-3 py-2 bg-[#fde047] hover:bg-[#facc15] border-2 border-slate-900 shadow-[0_3px_0_#ca8a04] active:translate-y-0.5 rounded-xl text-xs font-black text-slate-900 cursor-pointer transition"
              >
                Sınıfı Oluştur
              </button>
            </form>
          </div>

          <!-- Sınıf Listesi -->
          <div class="bg-white rounded-2xl border-2 border-slate-900 shadow-[0_3px_0_#94a3b8] overflow-hidden">
            <div class="p-3 bg-slate-100 border-b-2 border-slate-900 font-black text-xs text-slate-800">
              Mevcut Sınıflar ve Atanmış Öğretmenler
            </div>
            <div class="divide-y divide-slate-200">
              <div
                v-for="c in overviewData?.classes"
                :key="c.id"
                class="p-3 flex items-center justify-between text-xs"
              >
                <div class="flex items-center gap-2.5">
                  <span class="text-lg">📚</span>
                  <div>
                    <div class="font-black text-slate-900">{{ c.name }} ({{ c.grade_level }}. Sınıf)</div>
                    <div class="text-[10px] text-slate-500">
                      Öğretmen: {{ c.teacher_name ? c.teacher_name : 'Atanmadı' }}
                    </div>
                  </div>
                </div>
                <span class="px-2 py-0.5 rounded-lg bg-sky-100 text-sky-800 font-bold text-[10px]">
                  {{ c.name }}
                </span>
              </div>
            </div>
          </div>
        </div>

        <!-- 3. TAB: ÖĞRENCİLER & PIN SIFIRLA -->
        <div v-else-if="currentTab === 'students'" class="space-y-4">
          <!-- Öğrenci Ekle Kartı -->
          <div class="bg-white p-4 rounded-2xl border-2 border-slate-900 shadow-[0_3px_0_#94a3b8]">
            <h3 class="text-sm font-black text-slate-900 mb-3 flex items-center gap-1.5">
              <span>➕</span>
              <span>Yeni Öğrenci Ekle</span>
            </h3>
            <form @submit.prevent="handleAddStudent" class="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-4 gap-2.5">
              <input
                v-model="newStudent.full_name"
                placeholder="Öğrenci Adı Soyadı"
                required
                class="px-3 py-2 rounded-xl border-2 border-slate-900 text-xs font-bold outline-none"
              />
              <input
                v-model="newStudent.student_no"
                placeholder="Öğrenci No (Örn: 104)"
                required
                class="px-3 py-2 rounded-xl border-2 border-slate-900 text-xs font-bold outline-none"
              />
              <select
                v-model="newStudent.class_id"
                required
                class="px-3 py-2 rounded-xl border-2 border-slate-900 text-xs font-bold outline-none bg-white"
              >
                <option value="">-- Sınıf Seç --</option>
                <option v-for="c in overviewData?.classes" :key="c.id" :value="c.id">
                  {{ c.name }}
                </option>
              </select>
              <input
                v-model="newStudent.pin"
                placeholder="Emoji Şifre (Vars: 🚀⭐🤖⚡)"
                class="px-3 py-2 rounded-xl border-2 border-slate-900 text-xs font-bold outline-none text-center"
              />
              <button
                type="submit"
                class="col-span-1 sm:col-span-2 lg:col-span-4 py-2 bg-[#38bdf8] hover:bg-[#0284c7] border-2 border-slate-900 shadow-[0_3px_0_#0369a1] active:translate-y-0.5 rounded-xl text-xs font-black text-slate-900 hover:text-white cursor-pointer transition"
              >
                Öğrenciyi Kaydet
              </button>
            </form>
          </div>

          <!-- Öğrenci Listesi & PIN Sıfırlama Butonları -->
          <div class="bg-white rounded-2xl border-2 border-slate-900 shadow-[0_3px_0_#94a3b8] overflow-hidden">
            <div class="p-3 bg-slate-100 border-b-2 border-slate-900 font-black text-xs text-slate-800 flex items-center justify-between">
              <span>Kayıtlı Öğrenciler</span>
              <span class="text-[10px] text-slate-500 font-bold">Tek tıkla unutan öğrenci PIN'i sıfırlanabilir</span>
            </div>
            <div class="divide-y divide-slate-200 max-h-72 overflow-y-auto">
              <div
                v-for="s in overviewData?.students"
                :key="s.id"
                class="p-3 flex items-center justify-between text-xs"
              >
                <div class="flex items-center gap-2.5">
                  <span class="text-lg">👦</span>
                  <div>
                    <div class="font-black text-slate-900">{{ s.full_name }}</div>
                    <div class="text-[10px] text-slate-500">
                      No: {{ s.student_no }} &bull; Sınıf: {{ s.class_name || 'Yok' }}
                    </div>
                  </div>
                </div>
                <div class="flex items-center gap-2">
                  <button
                    type="button"
                    @click="handleResetPin(s.id, s.full_name)"
                    class="px-2.5 py-1 rounded-lg bg-amber-100 hover:bg-amber-200 border border-slate-900 text-[10px] font-black text-amber-950 transition active:scale-95 cursor-pointer"
                  >
                    🔑 Emoji Şifreyi Sıfırla (🚀⭐🤖⚡)
                  </button>
                </div>
              </div>
            </div>
          </div>
        </div>

        <!-- 4. TAB: VELİ - ÖĞRENCİ EŞLEŞTİRME -->
        <div v-else-if="currentTab === 'pairs'" class="space-y-4">
          <!-- Eşleştirme Kartı -->
          <div class="bg-white p-4 rounded-2xl border-2 border-slate-900 shadow-[0_3px_0_#94a3b8]">
            <h3 class="text-sm font-black text-slate-900 mb-3 flex items-center gap-1.5">
              <span>👨‍👩‍👧</span>
              <span>Veli Hesabı Tanımla & Öğrenciyle Eşleştir</span>
            </h3>
            <form @submit.prevent="handlePairParent" class="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-5 gap-2.5">
              <input
                v-model="newPair.parent_name"
                placeholder="Veli Adı Soyadı"
                required
                class="px-3 py-2 rounded-xl border-2 border-slate-900 text-xs font-bold outline-none"
              />
              <input
                v-model="newPair.parent_username"
                placeholder="Veli Kullanıcı Adı"
                required
                class="px-3 py-2 rounded-xl border-2 border-slate-900 text-xs font-bold outline-none"
              />
              <input
                v-model="newPair.parent_password"
                type="password"
                placeholder="Veli Şifresi"
                required
                class="px-3 py-2 rounded-xl border-2 border-slate-900 text-xs font-bold outline-none"
              />
              <select
                v-model="newPair.student_id"
                required
                class="px-3 py-2 rounded-xl border-2 border-slate-900 text-xs font-bold outline-none bg-white"
              >
                <option value="">-- Çocuğu (Öğrenci) Seç --</option>
                <option v-for="s in overviewData?.students" :key="s.id" :value="s.id">
                  {{ s.full_name }} (No: {{ s.student_no }})
                </option>
              </select>
              <select
                v-model="newPair.relation_type"
                class="px-3 py-2 rounded-xl border-2 border-slate-900 text-xs font-bold outline-none bg-white"
              >
                <option value="Anne">Anne</option>
                <option value="Baba">Baba</option>
                <option value="Vasi">Vasi</option>
              </select>

              <button
                type="submit"
                class="col-span-1 sm:col-span-2 lg:col-span-5 py-2 bg-[#f472b6] hover:bg-[#ec4899] border-2 border-slate-900 shadow-[0_3px_0_#be185d] active:translate-y-0.5 rounded-xl text-xs font-black text-slate-900 hover:text-white cursor-pointer transition"
              >
                Veli Hesabını Bağla
              </button>
            </form>
          </div>

          <!-- Mevcut Eşleşmeler Listesi -->
          <div class="bg-white rounded-2xl border-2 border-slate-900 shadow-[0_3px_0_#94a3b8] overflow-hidden">
            <div class="p-3 bg-slate-100 border-b-2 border-slate-900 font-black text-xs text-slate-800">
              Aktif Veli - Öğrenci Eşleşmeleri
            </div>
            <div class="divide-y divide-slate-200">
              <div
                v-for="p in overviewData?.pairs"
                :key="p.id"
                class="p-3 flex items-center justify-between text-xs"
              >
                <div class="flex items-center gap-2.5">
                  <span class="text-lg">👨‍👩‍👧</span>
                  <div>
                    <div class="font-black text-slate-900">
                      {{ p.parent_name }} ({{ p.relation_type }}) ➔ {{ p.student_name }}
                    </div>
                    <div class="text-[10px] text-slate-500">
                      Veli Kullanıcı: @{{ p.parent_username }} &bull; Öğrenci No: {{ p.student_no }}
                    </div>
                  </div>
                </div>
                <span class="px-2 py-0.5 rounded-lg bg-pink-100 text-pink-800 font-bold text-[10px]">
                  Bağlı
                </span>
              </div>
            </div>
          </div>
        </div>

      </div>
    </div>
  </div>
</template>

<script setup lang="ts">
import { ref, reactive, onMounted, watch } from 'vue';
import { useAuth } from '../composables/useAuth';

const props = defineProps<{
  isOpen: boolean;
}>();

const emit = defineEmits<{
  (e: 'close'): void;
}>();

const { getAuthHeaders } = useAuth();

const tabs = [
  { id: 'teachers', label: 'Öğretmenler', icon: '👩‍🏫' },
  { id: 'classes', label: 'Sınıflar & Atama', icon: '📚' },
  { id: 'students', label: 'Öğrenciler & PIN', icon: '👦' },
  { id: 'pairs', label: 'Veli Eşleştirme', icon: '👨‍👩‍👧' },
];

const currentTab = ref('teachers');
const overviewData = ref<any>(null);
const statusMessage = ref<{ type: 'success' | 'error'; text: string } | null>(null);

const newTeacher = reactive({
  full_name: '',
  username: '',
  password: '',
  branch: 'Bilişim Teknolojileri'
});

const newClass = reactive({
  name: '',
  grade_level: 4,
  teacher_id: ''
});

const newStudent = reactive({
  full_name: '',
  student_no: '',
  class_id: '',
  pin: '🚀⭐🤖⚡'
});

const newPair = reactive({
  parent_name: '',
  parent_username: '',
  parent_password: '123',
  student_id: '',
  relation_type: 'Anne'
});

async function fetchOverview() {
  try {
    const res = await fetch('/api/mudur/overview', {
      headers: getAuthHeaders()
    });
    if (res.ok) {
      overviewData.value = await res.json();
    }
  } catch (err) {
    console.error('Müdür verisi yüklenemedi:', err);
  }
}

async function handleAddTeacher() {
  try {
    const res = await fetch('/api/mudur/teachers', {
      method: 'POST',
      headers: { ...getAuthHeaders(), 'Content-Type': 'application/json' },
      body: JSON.stringify(newTeacher)
    });
    const data = await res.json();
    if (!res.ok) throw new Error(data.detail || 'Öğretmen eklenemedi');
    
    statusMessage.value = { type: 'success', text: 'Öğretmen başarıyla eklendi!' };
    newTeacher.full_name = '';
    newTeacher.username = '';
    newTeacher.password = '';
    await fetchOverview();
  } catch (e: any) {
    statusMessage.value = { type: 'error', text: e.message };
  }
}

async function handleAddClass() {
  try {
    const res = await fetch('/api/mudur/classes', {
      method: 'POST',
      headers: { ...getAuthHeaders(), 'Content-Type': 'application/json' },
      body: JSON.stringify(newClass)
    });
    const data = await res.json();
    if (!res.ok) throw new Error(data.detail || 'Sınıf eklenemedi');

    statusMessage.value = { type: 'success', text: 'Sınıf başarıyla oluşturuldu!' };
    newClass.name = '';
    newClass.teacher_id = '';
    await fetchOverview();
  } catch (e: any) {
    statusMessage.value = { type: 'error', text: e.message };
  }
}

async function handleAddStudent() {
  try {
    const res = await fetch('/api/mudur/students', {
      method: 'POST',
      headers: { ...getAuthHeaders(), 'Content-Type': 'application/json' },
      body: JSON.stringify(newStudent)
    });
    const data = await res.json();
    if (!res.ok) throw new Error(data.detail || 'Öğrenci eklenemedi');

    statusMessage.value = { type: 'success', text: 'Öğrenci kaydedildi!' };
    newStudent.full_name = '';
    newStudent.student_no = '';
    newStudent.pin = '1234';
    await fetchOverview();
  } catch (e: any) {
    statusMessage.value = { type: 'error', text: e.message };
  }
}

async function handleResetPin(studentId: string, studentName: string) {
  try {
    const res = await fetch(`/api/mudur/students/${studentId}/reset-pin`, {
      method: 'POST',
      headers: { ...getAuthHeaders(), 'Content-Type': 'application/json' },
      body: JSON.stringify({ new_pin: '🚀⭐🤖⚡' })
    });
    const data = await res.json();
    if (!res.ok) throw new Error(data.detail || 'PIN sıfırlanamadı');

    statusMessage.value = {
      type: 'success',
      text: `${studentName} isimli öğrencinin emoji şifresi '🚀⭐🤖⚡' olarak sıfırlandı!`
    };
  } catch (e: any) {
    statusMessage.value = { type: 'error', text: e.message };
  }
}

async function handlePairParent() {
  try {
    const res = await fetch('/api/mudur/pair-parent', {
      method: 'POST',
      headers: { ...getAuthHeaders(), 'Content-Type': 'application/json' },
      body: JSON.stringify(newPair)
    });
    const data = await res.json();
    if (!res.ok) throw new Error(data.detail || 'Veli eşleştirilemedi');

    statusMessage.value = { type: 'success', text: 'Veli hesabı oluşturuldu ve öğrenciyle eşleştirildi!' };
    newPair.parent_name = '';
    newPair.parent_username = '';
    newPair.student_id = '';
    await fetchOverview();
  } catch (e: any) {
    statusMessage.value = { type: 'error', text: e.message };
  }
}

watch(() => props.isOpen, (open) => {
  if (open) {
    statusMessage.value = null;
    fetchOverview();
  }
});

onMounted(() => {
  if (props.isOpen) {
    fetchOverview();
  }
});
</script>

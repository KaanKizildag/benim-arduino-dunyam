<template>
  <div
    v-if="isOpen"
    class="fixed inset-0 z-50 flex items-center justify-center p-3 sm:p-4 bg-slate-900/60 backdrop-blur-xs select-none"
    @click.self="$emit('close')"
  >
    <div
      class="bg-[#f0f9ff] border-[3px] border-slate-900 rounded-[32px] w-full max-w-lg shadow-[0_12px_0_#0f172a] flex flex-col overflow-hidden max-h-[94vh] animate-in fade-in zoom-in-95 duration-200"
    >
      <!-- Üst Başlık & Sekmeler -->
      <div class="bg-[#bae6fd] p-4 sm:p-5 border-b-[3px] border-slate-900 flex flex-col gap-3">
        <div class="flex items-center justify-between">
          <div class="flex items-center gap-2">
            <span class="text-2xl animate-bounce">🔐</span>
            <div>
              <h2 class="text-lg sm:text-xl font-black text-slate-900 leading-tight">
                Giriş Yap & Başla
              </h2>
              <p class="text-[11px] font-bold text-sky-900/80">
                Benim Arduino Dünyam Güvenli Portalı
              </p>
            </div>
          </div>
          <button
            type="button"
            @click="$emit('close')"
            class="w-8 h-8 rounded-xl bg-white hover:bg-rose-50 border-2 border-slate-900 shadow-[0_2px_0_#0f172a] active:translate-y-0.5 text-slate-800 font-black text-xs flex items-center justify-center cursor-pointer transition"
          >
            ✕
          </button>
        </div>

        <!-- Sekme Butonları (Öğrenci Emoji Girişi / Kurumsal Giriş) -->
        <div class="grid grid-cols-2 gap-2 bg-sky-200/70 p-1.5 rounded-2xl border-2 border-slate-900">
          <button
            type="button"
            @click="activeTab = 'student'"
            :class="[
              'py-2 px-3 rounded-xl font-black text-xs sm:text-sm transition-all border-2 cursor-pointer flex items-center justify-center gap-1.5',
              activeTab === 'student'
                ? 'bg-[#fde047] text-slate-900 border-slate-900 shadow-[0_3px_0_#ca8a04]'
                : 'bg-transparent text-slate-700 border-transparent hover:bg-white/50'
            ]"
          >
            <span>👦</span>
            <span>Öğrenci (Emoji Şifre)</span>
          </button>

          <button
            type="button"
            @click="activeTab = 'corporate'"
            :class="[
              'py-2 px-3 rounded-xl font-black text-xs sm:text-sm transition-all border-2 cursor-pointer flex items-center justify-center gap-1.5',
              activeTab === 'corporate'
                ? 'bg-[#38bdf8] text-slate-900 border-slate-900 shadow-[0_3px_0_#0284c7]'
                : 'bg-transparent text-slate-700 border-transparent hover:bg-white/50'
            ]"
          >
            <span>💼</span>
            <span>Öğretmen / Veli / Müdür</span>
          </button>
        </div>
      </div>

      <!-- İçerik Alanı -->
      <div class="p-4 sm:p-5 overflow-y-auto space-y-4">
        <!-- Hata Bildirimi -->
        <div
          v-if="errorMessage"
          class="p-3 bg-rose-100 border-2 border-rose-500 rounded-2xl text-xs font-black text-rose-800 flex items-center gap-2"
        >
          <span>⚠️</span>
          <span>{{ errorMessage }}</span>
        </div>

        <!-- 1. ÇOCUK DOSTU ÖĞRENCİ GİRİŞ FORMU (EMOJİ ŞİFRE TUŞ TAKIMI) -->
        <form
          v-if="activeTab === 'student'"
          @submit.prevent="handleStudentLogin"
          class="space-y-3"
        >
          <div class="grid grid-cols-2 gap-2.5">
            <div>
              <label class="block text-xs font-black text-slate-800 mb-1">
                🏫 Okul Kodu
              </label>
              <input
                v-model="studentForm.institutionCode"
                type="text"
                placeholder="Örn: KOD-01"
                required
                class="w-full px-3 py-2 rounded-xl bg-white border-2 border-slate-900 shadow-[0_2px_0_#94a3b8] focus:border-sky-500 font-bold text-xs text-slate-900 outline-none uppercase"
              />
            </div>

            <div>
              <label class="block text-xs font-black text-slate-800 mb-1">
                🔢 Öğrenci No
              </label>
              <input
                v-model="studentForm.studentNo"
                type="text"
                placeholder="Örn: 104"
                required
                class="w-full px-3 py-2 rounded-xl bg-white border-2 border-slate-900 shadow-[0_2px_0_#94a3b8] focus:border-sky-500 font-bold text-xs text-slate-900 outline-none"
              />
            </div>
          </div>

          <!-- GİZLİ EMOJİ ŞİFRESİ ALANI -->
          <div class="bg-white p-3.5 rounded-2xl border-2 border-slate-900 shadow-[0_3px_0_#94a3b8]">
            <div class="flex items-center justify-between mb-2">
              <label class="text-xs font-black text-slate-900 flex items-center gap-1.5">
                <span>🎨</span>
                <span>Gizli Emoji Şifren:</span>
              </label>
              <span class="text-[10px] font-bold text-amber-600 bg-amber-50 px-2 py-0.5 rounded-full border border-amber-200">
                4 Emoji Seç
              </span>
            </div>

            <!-- Seçilen 4 Emoji Yuvası (Slots) -->
            <div class="flex items-center justify-center gap-2.5 py-2">
              <div
                v-for="idx in 4"
                :key="idx"
                :class="[
                  'w-12 h-12 rounded-2xl border-2 flex items-center justify-center text-2xl transition-all shadow-xs select-none',
                  selectedEmojis[idx - 1]
                    ? 'bg-[#fef08a] border-slate-900 scale-105 shadow-[0_3px_0_#ca8a04]'
                    : 'bg-slate-100 border-dashed border-slate-400 text-slate-300'
                ]"
              >
                {{ selectedEmojis[idx - 1] || '✨' }}
              </div>
            </div>

            <!-- İnteraktif Emoji Tuş Takımı (8 Renkli Çizgi Film İkonu) -->
            <div class="pt-2">
              <div class="text-[10px] font-black text-slate-500 uppercase tracking-wider text-center mb-1.5">
                👇 Aşağıdaki Emojilere Sırayla Dokun 👇
              </div>
              <div class="grid grid-cols-4 gap-2">
                <button
                  v-for="item in emojiKeypad"
                  :key="item.emoji"
                  type="button"
                  @click="addEmoji(item.emoji)"
                  class="py-2 rounded-xl bg-slate-50 hover:bg-amber-100 border-2 border-slate-900 shadow-[0_3px_0_#94a3b8] active:translate-y-0.5 active:shadow-none transition flex flex-col items-center justify-center cursor-pointer select-none group"
                  :title="item.label"
                >
                  <span class="text-2xl group-hover:scale-115 transition-transform">{{ item.emoji }}</span>
                  <span class="text-[9px] font-black text-slate-700 mt-0.5">{{ item.label }}</span>
                </button>
              </div>

              <!-- Geri Al & Temizle Kontrolleri -->
              <div class="flex items-center justify-between gap-2 mt-2 pt-2 border-t border-slate-100">
                <button
                  type="button"
                  @click="removeLastEmoji"
                  :disabled="selectedEmojis.length === 0"
                  class="flex-1 py-1 px-2 rounded-lg bg-slate-100 hover:bg-rose-100 border border-slate-900 text-[11px] font-black text-slate-800 disabled:opacity-40 cursor-pointer flex items-center justify-center gap-1"
                >
                  <span>⌫</span>
                  <span>Sonuncuyu Sil</span>
                </button>

                <button
                  type="button"
                  @click="selectedEmojis = []"
                  :disabled="selectedEmojis.length === 0"
                  class="py-1 px-3 rounded-lg bg-slate-100 hover:bg-slate-200 border border-slate-900 text-[11px] font-black text-slate-700 disabled:opacity-40 cursor-pointer"
                >
                  Temizle
                </button>
              </div>
            </div>
          </div>

          <button
            type="submit"
            :disabled="isLoading || selectedEmojis.length < 3"
            class="w-full py-3 rounded-2xl bg-[#4ade80] hover:bg-[#22c55e] border-2 border-slate-900 shadow-[0_4px_0_#15803d] active:translate-y-1 active:shadow-none font-black text-sm text-slate-900 transition flex items-center justify-center gap-2 cursor-pointer disabled:opacity-50"
          >
            <span>🚀</span>
            <span>{{ isLoading ? 'Giriş Yapılıyor...' : 'Atölyeme Başla!' }}</span>
          </button>
        </form>

        <!-- 2. KURUMSAL GİRİŞ FORMU (Müdür / Öğretmen / Veli / Admin) -->
        <form
          v-else
          @submit.prevent="handleCorporateLogin"
          class="space-y-3.5"
        >
          <div>
            <label class="block text-xs font-black text-slate-800 mb-1">
              👤 Kullanıcı Adı
            </label>
            <input
              v-model="corpForm.username"
              type="text"
              placeholder="Kullanıcı adınız"
              required
              class="w-full px-3.5 py-2.5 rounded-2xl bg-white border-2 border-slate-900 shadow-[0_3px_0_#94a3b8] focus:border-sky-500 font-bold text-sm text-slate-900 outline-none"
            />
          </div>

          <div>
            <label class="block text-xs font-black text-slate-800 mb-1">
              🔒 Şifre
            </label>
            <input
              v-model="corpForm.password"
              type="password"
              placeholder="••••••••"
              required
              class="w-full px-3.5 py-2.5 rounded-2xl bg-white border-2 border-slate-900 shadow-[0_3px_0_#94a3b8] focus:border-sky-500 font-bold text-sm text-slate-900 outline-none"
            />
          </div>

          <button
            type="submit"
            :disabled="isLoading"
            class="w-full py-3 rounded-2xl bg-[#38bdf8] hover:bg-[#0284c7] border-2 border-slate-900 shadow-[0_4px_0_#0369a1] active:translate-y-1 active:shadow-none font-black text-sm text-slate-900 hover:text-white transition flex items-center justify-center gap-2 cursor-pointer disabled:opacity-50"
          >
            <span>💼</span>
            <span>{{ isLoading ? 'Giriş Yapılıyor...' : 'Giriş Yap' }}</span>
          </button>
        </form>

        <!-- HIZLI DEMO TEST BUTONLARI -->
        <div class="pt-3 border-t-2 border-slate-200">
          <div class="flex items-center justify-between mb-2">
            <span class="text-[10px] font-black uppercase tracking-wider text-slate-500">
              ⚡ Hızlı Demo Girişleri
            </span>
            <span class="text-[10px] font-bold text-emerald-600 bg-emerald-50 px-2 py-0.5 rounded-full border border-emerald-300">
              1-Tıkla Aktif
            </span>
          </div>
          <div class="grid grid-cols-2 sm:grid-cols-3 gap-1.5">
            <button
              type="button"
              @click="quickDemoLogin('student')"
              class="px-2 py-1.5 rounded-xl bg-amber-100 hover:bg-amber-200 border border-slate-900 text-left font-bold text-[11px] text-slate-800 transition active:scale-95 cursor-pointer flex items-center gap-1.5"
            >
              <span class="text-lg">👦</span>
              <div>
                <div class="font-black leading-none">Can (Öğrenci)</div>
                <div class="text-[9px] text-amber-900 font-extrabold mt-0.5">🚀⭐🤖⚡</div>
              </div>
            </button>

            <button
              type="button"
              @click="quickDemoLogin('teacher')"
              class="px-2 py-1.5 rounded-xl bg-emerald-100 hover:bg-emerald-200 border border-slate-900 text-left font-bold text-[11px] text-slate-800 transition active:scale-95 cursor-pointer flex items-center gap-1.5"
            >
              <span>👩‍🏫</span>
              <div>
                <div class="font-black leading-none">Zeynep Öğrt.</div>
                <div class="text-[9px] text-slate-500">Sınıf Paneli</div>
              </div>
            </button>

            <button
              type="button"
              @click="quickDemoLogin('mudur')"
              class="px-2 py-1.5 rounded-xl bg-sky-100 hover:bg-sky-200 border border-slate-900 text-left font-bold text-[11px] text-slate-800 transition active:scale-95 cursor-pointer flex items-center gap-1.5"
            >
              <span>🏫</span>
              <div>
                <div class="font-black leading-none">Müdür Kemal</div>
                <div class="text-[9px] text-slate-500">Atatürk Okulu</div>
              </div>
            </button>

            <button
              type="button"
              @click="quickDemoLogin('veli')"
              class="px-2 py-1.5 rounded-xl bg-pink-100 hover:bg-pink-200 border border-slate-900 text-left font-bold text-[11px] text-slate-800 transition active:scale-95 cursor-pointer flex items-center gap-1.5"
            >
              <span>👨‍👩‍👧</span>
              <div>
                <div class="font-black leading-none">Mehmet (Veli)</div>
                <div class="text-[9px] text-slate-500">Can'ın Velisi</div>
              </div>
            </button>

            <button
              type="button"
              @click="quickDemoLogin('admin')"
              class="px-2 py-1.5 rounded-xl bg-indigo-100 hover:bg-indigo-200 border border-slate-900 text-left font-bold text-[11px] text-slate-800 transition active:scale-95 cursor-pointer flex items-center gap-1.5 col-span-2 sm:col-span-1"
            >
              <span>👑</span>
              <div>
                <div class="font-black leading-none">Sistem Admin</div>
                <div class="text-[9px] text-slate-500">Tam Yetkili</div>
              </div>
            </button>
          </div>
        </div>

        <!-- Serbest Misafir Girişi -->
        <div class="pt-2 text-center">
          <button
            type="button"
            @click="continueAsGuest"
            class="text-xs font-black text-slate-600 hover:text-slate-900 hover:underline cursor-pointer"
          >
            🌟 Giriş yapmadan serbest Maker olarak devam et
          </button>
        </div>
      </div>
    </div>
  </div>
</template>

<script setup lang="ts">
import { ref, reactive } from 'vue';
import { useAuth } from '../composables/useAuth';

defineProps<{
  isOpen: boolean;
}>();

const emit = defineEmits<{
  (e: 'close'): void;
  (e: 'login-success'): void;
}>();

const { loginCorporate, loginStudent, logout } = useAuth();

const activeTab = ref<'student' | 'corporate'>('student');
const isLoading = ref(false);
const errorMessage = ref('');

// Çocuk Emoji Tuş Takımı
const emojiKeypad = [
  { emoji: '🚀', label: 'Roket' },
  { emoji: '⭐', label: 'Yıldız' },
  { emoji: '🤖', label: 'Robot' },
  { emoji: '⚡', label: 'Şimşek' },
  { emoji: '🐱', label: 'Kedi' },
  { emoji: '🎈', label: 'Balon' },
  { emoji: '🍕', label: 'Pizza' },
  { emoji: '🦁', label: 'Aslan' },
];

const selectedEmojis = ref<string[]>(['🚀', '⭐', '🤖', '⚡']);

const studentForm = reactive({
  institutionCode: 'KOD-01',
  studentNo: '104'
});

const corpForm = reactive({
  username: '',
  password: ''
});

function addEmoji(emoji: string) {
  if (selectedEmojis.value.length < 4) {
    selectedEmojis.value.push(emoji);
  }
}

function removeLastEmoji() {
  selectedEmojis.value.pop();
}

async function handleStudentLogin() {
  errorMessage.value = '';
  if (selectedEmojis.value.length < 3) {
    errorMessage.value = 'Lütfen en az 3 veya 4 emoji seç!';
    return;
  }
  isLoading.value = true;
  const emojiPin = selectedEmojis.value.join('');
  try {
    await loginStudent(
      studentForm.institutionCode.trim(),
      studentForm.studentNo.trim(),
      emojiPin
    );
    emit('login-success');
    emit('close');
  } catch (e: any) {
    errorMessage.value = e.message || 'Öğrenci numarası veya emoji şifre hatalı!';
  } finally {
    isLoading.value = false;
  }
}

async function handleCorporateLogin() {
  errorMessage.value = '';
  isLoading.value = true;
  try {
    await loginCorporate(corpForm.username.trim(), corpForm.password.trim());
    emit('login-success');
    emit('close');
  } catch (e: any) {
    errorMessage.value = e.message || 'Giriş başarısız oldu.';
  } finally {
    isLoading.value = false;
  }
}

async function quickDemoLogin(type: 'student' | 'teacher' | 'mudur' | 'veli' | 'admin') {
  errorMessage.value = '';
  isLoading.value = true;
  try {
    if (type === 'student') {
      await loginStudent('KOD-01', '104', '🚀⭐🤖⚡');
    } else if (type === 'teacher') {
      await loginCorporate('ogretmen1', 'ogretmen123');
    } else if (type === 'mudur') {
      await loginCorporate('mudur1', 'mudur123');
    } else if (type === 'veli') {
      await loginCorporate('veli1', 'veli123');
    } else if (type === 'admin') {
      await loginCorporate('admin', 'admin123');
    }
    emit('login-success');
    emit('close');
  } catch (e: any) {
    errorMessage.value = e.message || 'Hızlı giriş hatası.';
  } finally {
    isLoading.value = false;
  }
}

function continueAsGuest() {
  logout();
  emit('close');
}
</script>

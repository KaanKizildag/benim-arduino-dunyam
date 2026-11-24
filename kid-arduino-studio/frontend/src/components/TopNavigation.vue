<template>
  <header class="bg-[#7dd3fc] px-3 sm:px-6 py-2.5 sm:py-3 border-b-[3px] border-slate-900 select-none shrink-0 shadow-xs">
    <div class="w-full flex flex-wrap items-center justify-between gap-3">
      
      <!-- Sol: 'Benim Arduino Dünyam' Çizgi Film Logosu & Kullanıcı Durumu -->
      <div class="flex items-center gap-2.5">
        <div
          class="flex items-center gap-2 cursor-pointer group"
          @click="$emit('go-step', 1)"
          title="İlk Adıma Git"
        >
          <!-- Teal Renkli Arduino Sonsuzluk İkonu -->
          <div class="w-10 h-10 rounded-2xl bg-[#0d9488] border-2 border-slate-900 shadow-[0_3px_0_#0f172a] flex items-center justify-center text-white text-base font-black group-hover:rotate-6 transition-transform">
            <svg class="w-6 h-6 fill-current" viewBox="0 0 24 24">
              <path d="M12 2C6.48 2 2 6.48 2 12s4.48 10 10 10 10-4.48 10-10S17.52 2 12 2zm-1 14H9v-2h2v2zm0-4H9V8h2v4zm4 4h-2v-2h2v2zm0-4h-2V8h2v4z"/>
            </svg>
          </div>

          <!-- 3D Renkli Çizgi Film Yazısı -->
          <div class="flex flex-col">
            <div class="flex items-center gap-0.5 font-black text-lg sm:text-xl tracking-tight leading-none drop-shadow-[0_2px_0_rgba(255,255,255,0.8)]">
              <span class="text-amber-500">B</span>
              <span class="text-sky-600">e</span>
              <span class="text-emerald-500">n</span>
              <span class="text-purple-600">i</span>
              <span class="text-rose-500">m</span>
              <span class="text-slate-800 ml-1.5">Arduino</span>
              <span class="text-teal-700 ml-1.5">Dünyam</span>
            </div>
            <span class="text-[9px] font-black text-teal-900/80 tracking-widest uppercase mt-0.5">
              Çocuk AI Stüdyosu 🚀
            </span>
          </div>
        </div>

        <!-- Kullanıcı Rolü & Profil Rozeti -->
        <div class="flex items-center gap-1.5">
          <button
            v-if="isAuthenticated"
            type="button"
            @click="$emit('open-login')"
            class="px-2.5 py-1 rounded-2xl bg-white hover:bg-slate-50 border-2 border-slate-900 shadow-[0_2px_0_#0f172a] flex items-center gap-1.5 cursor-pointer transition active:scale-95"
            :title="`${roleLabel}: ${currentUser?.full_name || currentUser?.username} (Değiştirmek için tıkla)`"
          >
            <span class="text-base">{{ roleBadgeIcon }}</span>
            <div class="text-left hidden sm:block leading-tight">
              <div class="text-[11px] font-black text-slate-900 truncate max-w-[110px]">
                {{ currentUser?.full_name || currentUser?.username }}
              </div>
              <div class="text-[9px] font-bold text-slate-500">
                {{ roleLabel }}
              </div>
            </div>
          </button>

          <!-- Çıkış Butonu (Giriş yapılmışsa) -->
          <button
            v-if="isAuthenticated"
            type="button"
            @click="handleLogout"
            class="w-7 h-7 rounded-xl bg-slate-200 hover:bg-rose-200 border-2 border-slate-900 flex items-center justify-center text-xs font-black text-slate-700 cursor-pointer transition active:scale-95"
            title="Güvenli Çıkış Yap"
          >
            🚪
          </button>

          <!-- Giriş Yap Butonu (Misafir ise) -->
          <button
            v-else
            type="button"
            @click="$emit('open-login')"
            class="px-2.5 py-1.5 rounded-2xl bg-[#fde047] hover:bg-[#facc15] border-2 border-slate-900 shadow-[0_2px_0_#ca8a04] flex items-center gap-1 text-xs font-black text-slate-900 cursor-pointer transition active:scale-95"
            title="Okul / Öğrenci / Öğretmen Girişi"
          >
            <span>🔑</span>
            <span>Giriş Yap</span>
          </button>
        </div>
      </div>

      <!-- Orta: 4 Ayrı Ekran Sekmeleri -->
      <nav class="flex items-center gap-1 sm:gap-2 overflow-x-auto py-0.5 max-w-full">
        <button
          v-for="step in steps"
          :key="step.num"
          type="button"
          @click="$emit('go-step', step.num)"
          :class="[
            'px-2.5 sm:px-4 py-1.5 sm:py-2 rounded-2xl text-xs sm:text-sm font-black transition-all cursor-pointer whitespace-nowrap border-2 border-slate-900',
            currentStep === step.num
              ? 'bg-[#fbbf24] text-slate-900 shadow-[0_4px_0_#ca8a04] scale-103'
              : 'bg-white/70 text-slate-800 hover:bg-white shadow-[0_2px_0_#0f172a]'
          ]"
        >
          {{ step.num }}. {{ step.title }}
        </button>
      </nav>

      <!-- Sağ: Role Göre Modallar, Projelerim, Fikirler, Malzeme Çantam vb. -->
      <div class="flex items-center gap-1.5 sm:gap-2 flex-wrap justify-end">
        
        <!-- ROL BUTONU: Okul Müdürü Paneli -->
        <button
          v-if="isMudur || authIsAdmin"
          type="button"
          @click="$emit('open-mudur')"
          class="px-2.5 sm:px-3 py-1.5 sm:py-2 rounded-2xl bg-[#38bdf8] hover:bg-[#0284c7] hover:text-white border-2 border-slate-900 shadow-[0_3px_0_#0369a1] active:translate-y-0.5 active:shadow-none text-slate-900 text-xs font-black transition flex items-center gap-1.5 cursor-pointer"
          title="Okul Müdürü Yönetim Paneli"
        >
          <span class="text-sm">🏫</span>
          <span class="hidden sm:inline">Müdür Paneli</span>
        </button>

        <!-- ROL BUTONU: Öğretmen Sınıf & Onay Masası -->
        <button
          v-if="isTeacher || authIsAdmin"
          type="button"
          @click="$emit('open-teacher')"
          class="px-2.5 sm:px-3 py-1.5 sm:py-2 rounded-2xl bg-[#4ade80] hover:bg-[#22c55e] border-2 border-slate-900 shadow-[0_3px_0_#15803d] active:translate-y-0.5 active:shadow-none text-slate-900 text-xs font-black transition flex items-center gap-1.5 cursor-pointer"
          title="Öğretmen Sınıfım & Devre Onay Paneli"
        >
          <span class="text-sm">👩‍🏫</span>
          <span class="hidden sm:inline">Sınıfım & Onay</span>
        </button>

        <!-- ROL BUTONU: Veli Portfolyosu -->
        <button
          v-if="isParent || authIsAdmin"
          type="button"
          @click="$emit('open-parent')"
          class="px-2.5 sm:px-3 py-1.5 sm:py-2 rounded-2xl bg-[#f472b6] hover:bg-[#ec4899] hover:text-white border-2 border-slate-900 shadow-[0_3px_0_#be185d] active:translate-y-0.5 active:shadow-none text-slate-900 text-xs font-black transition flex items-center gap-1.5 cursor-pointer"
          title="Veli Portfolyosu & Mahremiyet"
        >
          <span class="text-sm">👨‍👩‍👧</span>
          <span class="hidden sm:inline">Portfolyo</span>
        </button>

        <!-- 0. Projelerim Butonu -->
        <button
          type="button"
          @click="$emit('open-projects')"
          class="px-2.5 sm:px-3 py-1.5 sm:py-2 rounded-2xl bg-[#fde047] hover:bg-[#facc15] border-2 border-slate-900 shadow-[0_3px_0_#0f172a] active:translate-y-0.5 active:shadow-none text-slate-900 text-xs font-black transition flex items-center gap-1.5 cursor-pointer"
          title="Projelerim Menüsünü Aç"
        >
          <span class="text-sm">📂</span>
          <span class="hidden sm:inline">Projelerim</span>
          <span
            v-if="projectsCount !== undefined"
            class="px-1.5 py-0.2 rounded-full bg-amber-600 text-white text-[10px] font-black border border-slate-900"
          >
            {{ projectsCount }}
          </span>
        </button>

        <!-- 0-B. Proje Fikirleri Butonu -->
        <button
          type="button"
          @click="$emit('open-ideas')"
          class="px-2.5 sm:px-3 py-1.5 sm:py-2 rounded-2xl bg-[#fef08a] hover:bg-[#fde047] border-2 border-slate-900 shadow-[0_3px_0_#0f172a] active:translate-y-0.5 active:shadow-none text-slate-900 text-xs font-black transition flex items-center gap-1.5 cursor-pointer"
          title="Elindeki malzemelerle yapabileceğin proje fikirlerini keşfet"
        >
          <span class="text-sm">💡</span>
          <span class="hidden md:inline">Fikirler</span>
        </button>

        <!-- 1. Malzeme Çantam Butonu -->
        <button
          type="button"
          @click="$emit('open-inventory')"
          class="px-2.5 sm:px-3 py-1.5 sm:py-2 rounded-2xl bg-[#e2d5c3] hover:bg-[#d6c5b0] border-2 border-slate-900 shadow-[0_3px_0_#0f172a] active:translate-y-0.5 active:shadow-none text-slate-900 text-xs font-black transition flex items-center gap-1.5 cursor-pointer"
          title="Elektronik Malzeme Çantamı Aç"
        >
          <span class="text-sm">🧰</span>
          <span class="hidden sm:inline">Çantam</span>
          <span class="px-1.5 py-0.2 rounded-full bg-emerald-500 text-white text-[10px] font-black border border-slate-900">
            {{ inventoryCount }}
          </span>
        </button>

        <!-- 1-B. Otomatik Kayıt Switch/Butonu -->
        <button
          type="button"
          @click="$emit('toggle-auto-save')"
          :class="[
            'px-2 sm:px-2.5 py-1.5 sm:py-2 rounded-2xl border-2 border-slate-900 shadow-[0_3px_0_#0f172a] active:translate-y-0.5 active:shadow-none text-xs font-black transition flex items-center gap-1 cursor-pointer',
            autoSave ? 'bg-emerald-100 text-emerald-950 hover:bg-emerald-200' : 'bg-slate-100 text-slate-600 hover:bg-slate-200'
          ]"
          :title="autoSave ? 'Otomatik Kayıt: AÇIK (Projeler otomatik arşive eklenir)' : 'Otomatik Kayıt: KAPALI (Projeleri manuel kaydedersin)'"
        >
          <span class="text-xs">💾</span>
          <span class="hidden lg:inline text-[11px]">{{ autoSave ? 'Oto-Kayıt: Açık' : 'Oto-Kayıt: Kapalı' }}</span>
        </button>

        <!-- 2. AI Modeli & Admin Paneli Butonu (Yalnızca Admin veya Dev) -->
        <button
          v-if="authIsAdmin || isDevAdmin"
          type="button"
          @click="$emit('open-ai-model')"
          class="px-2.5 py-1.5 sm:py-2 rounded-2xl bg-[#bae6fd] hover:bg-[#7dd3fc] border-2 border-slate-900 shadow-[0_3px_0_#0f172a] active:translate-y-0.5 active:shadow-none text-slate-900 text-xs font-black transition flex items-center gap-1.5 cursor-pointer"
          title="Yapay Zeka Modeli & Token Yönetimi (Admin Paneli)"
        >
          <span class="text-sm">🤖</span>
          <span class="hidden md:inline">AI Paneli</span>
        </button>

        <!-- 3. Admin (AI İstek & Cevap Logları) Butonu -->
        <button
          v-if="authIsAdmin || isDevAdmin"
          type="button"
          @click="$emit('open-admin-logs')"
          class="px-2.5 py-1.5 sm:py-2 rounded-2xl bg-slate-900 hover:bg-slate-800 border-2 border-slate-900 shadow-[0_3px_0_#334155] active:translate-y-0.5 active:shadow-none text-amber-300 text-xs font-black transition flex items-center gap-1.5 cursor-pointer"
          title="Admin: Yapay Zeka İstek ve Cevap Loglarını Gör"
        >
          <span class="text-sm">🛠️</span>
          <span class="hidden lg:inline">Admin Log</span>
          <span
            v-if="aiLogsCount !== undefined"
            class="px-1.5 py-0.2 rounded-full bg-indigo-600 text-white text-[10px] font-black border border-indigo-400"
          >
            {{ aiLogsCount }}
          </span>
        </button>

        <!-- 4. Kırmızı Kare Çarpı Butonu -->
        <button
          type="button"
          @click="$emit('reset-or-close')"
          class="w-8 h-8 rounded-xl bg-[#f43f5e] hover:bg-[#e11d48] border-2 border-slate-900 shadow-[0_3px_0_#9f1239] active:translate-y-0.5 active:shadow-none text-white font-black text-xs sm:text-sm flex items-center justify-center cursor-pointer transition shrink-0"
          title="Projeyi Sıfırla / Başa Dön"
        >
          ✕
        </button>
      </div>

    </div>
  </header>
</template>

<script setup lang="ts">
import { useAuth } from '../composables/useAuth';

const props = defineProps<{
  currentStep: number;
  inventoryCount: number;
  projectsCount?: number;
  aiLogsCount?: number;
  activeModelName?: string;
  isAdmin?: boolean;
  autoSave?: boolean;
}>();

const emit = defineEmits<{
  (e: 'go-step', stepNum: number): void;
  (e: 'open-projects'): void;
  (e: 'open-ideas'): void;
  (e: 'open-inventory'): void;
  (e: 'open-ai-model'): void;
  (e: 'open-admin-logs'): void;
  (e: 'open-settings'): void;
  (e: 'open-login'): void;
  (e: 'open-mudur'): void;
  (e: 'open-teacher'): void;
  (e: 'open-parent'): void;
  (e: 'toggle-auto-save'): void;
  (e: 'toggle-admin'): void;
  (e: 'reset-or-close'): void;
}>();

const {
  currentUser,
  isAuthenticated,
  isAdmin: authIsAdmin,
  isMudur,
  isTeacher,
  isParent,
  roleLabel,
  roleBadgeIcon,
  logout
} = useAuth();

const isDevAdmin = props.isAdmin;

function handleLogout() {
  logout();
}

const steps = [
  { num: 1, title: 'Hayal Et' },
  { num: 2, title: 'Devreyi Kur' },
  { num: 3, title: 'Nasıl Çalışacak?' },
  { num: 4, title: 'Çalıştır' },
];
</script>

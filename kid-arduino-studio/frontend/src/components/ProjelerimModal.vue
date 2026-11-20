<template>
  <div
    v-if="isOpen"
    class="fixed inset-0 z-50 flex items-center justify-center p-3 sm:p-5 bg-slate-900/65 backdrop-blur-xs select-none"
    @click.self="$emit('close')"
  >
    <div class="bg-[#fefce8] border-[3px] border-slate-900 rounded-[32px] w-full max-w-4xl max-h-[88vh] shadow-[0_12px_0_#0f172a] flex flex-col overflow-hidden">
      
      <!-- 1. ÜST BAŞLIK BANDI -->
      <div class="bg-[#fde047] px-5 sm:px-7 py-4 border-b-[3px] border-slate-900 flex flex-wrap items-center justify-between gap-3">
        <div class="flex items-center gap-3">
          <div class="w-12 h-12 rounded-2xl bg-white border-2 border-slate-900 shadow-[0_3px_0_#0f172a] flex items-center justify-center text-2xl">
            📂
          </div>
          <div>
            <h2 class="text-lg sm:text-xl font-black text-slate-900 leading-tight">
              Projelerim (Kurguladığım Devreler)
            </h2>
            <p class="text-xs font-bold text-slate-700">
              Yapay zeka ile kurguladığın ve kaydettiğin tüm devre projelerin burada saklanır!
            </p>
          </div>
        </div>

        <div class="flex items-center gap-2">
          <!-- Aktif Projeyi Kaydet Butonu -->
          <button
            type="button"
            @click="$emit('save-current')"
            class="px-3.5 py-2 rounded-2xl bg-[#4ade80] hover:bg-[#22c55e] border-2 border-slate-900 shadow-[0_3px_0_#15803d] active:translate-y-0.5 active:shadow-none text-slate-950 font-black text-xs transition cursor-pointer flex items-center gap-1.5"
          >
            <span>💾</span>
            <span>Aktif Projeyi Kaydet</span>
          </button>

          <!-- Kapat Butonu -->
          <button
            type="button"
            @click="$emit('close')"
            class="w-9 h-9 rounded-2xl bg-[#f43f5e] hover:bg-[#e11d48] border-2 border-slate-900 shadow-[0_3px_0_#9f1239] active:translate-y-0.5 active:shadow-none text-white font-black text-sm flex items-center justify-center cursor-pointer transition"
            title="Kapat"
          >
            ✕
          </button>
        </div>
      </div>

      <!-- 2. FİLTRE SEKMELERİ VE ARAMA ÇUBUĞU -->
      <div class="bg-white px-5 py-3 border-b-2 border-slate-900/15 flex flex-col sm:flex-row items-stretch sm:items-center justify-between gap-3">
        <div class="flex items-center gap-2 overflow-x-auto">
          <button
            v-for="tab in filterTabs"
            :key="tab.id"
            type="button"
            @click="activeFilter = tab.id"
            :class="[
              'px-3.5 py-1.5 rounded-xl text-xs font-black border-2 border-slate-900 transition cursor-pointer whitespace-nowrap flex items-center gap-1.5',
              activeFilter === tab.id
                ? 'bg-[#38bdf8] text-slate-950 shadow-[0_2px_0_#0284c7]'
                : 'bg-slate-100 text-slate-700 hover:bg-slate-200'
            ]"
          >
            <span>{{ tab.icon }}</span>
            <span>{{ tab.label }}</span>
            <span class="px-1.5 py-0.2 rounded-full bg-white/80 text-slate-900 text-[10px] border border-slate-900">
              {{ tab.count }}
            </span>
          </button>
        </div>

        <div class="relative flex-1 max-w-xs">
          <input
            v-model="searchQuery"
            type="text"
            placeholder="Proje veya parça ara (LED, Servo, LDR...)"
            class="w-full pl-8 pr-3 py-1.5 rounded-xl border-2 border-slate-900 bg-slate-50 focus:bg-white text-xs font-bold text-slate-900 outline-none"
          />
          <span class="absolute left-2.5 top-1/2 -translate-y-1/2 text-xs">🔍</span>
        </div>
      </div>

      <!-- 3. PROJE KARTLARI LİSTESİ -->
      <div class="flex-1 overflow-y-auto p-4 sm:p-6 grid grid-cols-1 md:grid-cols-2 gap-4">
        <div
          v-for="entry in filteredProjects"
          :key="entry.id"
          :class="[
            'bg-white rounded-3xl p-4 sm:p-5 border-[3px] border-slate-900 transition flex flex-col justify-between gap-3 relative',
            activeProjectId === entry.id
              ? 'ring-4 ring-amber-400 shadow-[0_6px_0_#ca8a04]'
              : 'shadow-[0_5px_0_#0f172a] hover:-translate-y-0.5'
          ]"
        >
          <!-- Üst Rozetler -->
          <div>
            <div class="flex items-start justify-between gap-2 mb-2">
              <div class="flex flex-wrap items-center gap-1.5">
                <span
                  :class="[
                    'px-2.5 py-0.5 rounded-full text-[10px] font-black border border-slate-900',
                    entry.is_preset
                      ? 'bg-amber-200 text-amber-950'
                      : 'bg-purple-200 text-purple-950'
                  ]"
                >
                  {{ entry.badge || (entry.is_preset ? '🎁 Hazır Kurgu' : '✨ Kendi Tasarımım') }}
                </span>

                <span
                  v-if="entry.project.verification?.is_valid !== false"
                  class="px-2 py-0.5 rounded-full bg-emerald-100 text-emerald-900 border border-emerald-700 text-[10px] font-black"
                >
                  ✓ Kablolama & Kod Uyumlu
                </span>

                <span
                  v-if="activeProjectId === entry.id"
                  class="px-2 py-0.5 rounded-full bg-[#fde047] text-slate-950 border border-slate-900 text-[10px] font-black"
                >
                  ● Şu An Açık
                </span>
              </div>

              <!-- Silme Butonu (Kullanıcı projeleri için) -->
              <button
                v-if="!entry.is_preset"
                type="button"
                @click.stop="$emit('delete-project', entry.id)"
                class="w-7 h-7 rounded-xl bg-rose-100 hover:bg-rose-500 hover:text-white text-rose-700 border border-slate-900 text-xs font-black flex items-center justify-center transition cursor-pointer shrink-0"
                title="Bu Projeyi Sil"
              >
                🗑️
              </button>
            </div>

            <!-- Proje Adı ve Açıklama -->
            <h3 class="text-base font-black text-slate-900 leading-snug mb-1">
              {{ entry.project.proje_adi }}
            </h3>
            <p class="text-xs text-slate-600 font-bold line-clamp-2 leading-relaxed">
              "{{ entry.prompt || entry.project.karsilama_mesaji }}"
            </p>
          </div>

          <!-- Orta: Bileşen ve Bağlantı Özeti -->
          <div class="bg-slate-50 rounded-2xl p-2.5 border-2 border-slate-200 flex flex-col gap-2">
            <div class="flex items-center justify-between text-[11px] font-black text-slate-700">
              <span>🧩 {{ (entry.project.netlist?.components || []).length }} Devre Elemanı</span>
              <span>🔌 {{ (entry.project.netlist?.connections || []).length }} Kablo Bağlantısı</span>
              <span class="text-[10px] text-slate-500">{{ entry.created_at }}</span>
            </div>

            <!-- Bileşen Etiketleri -->
            <div class="flex flex-wrap gap-1">
              <span
                v-for="comp in (entry.project.netlist?.components || [])"
                :key="comp.id"
                class="px-2 py-0.5 rounded-lg bg-white border border-slate-300 text-[10px] font-black text-slate-800"
              >
                {{ comp.label }}
              </span>
            </div>
          </div>

          <!-- Alt: Aksiyon Butonları -->
          <div class="flex items-center gap-2 pt-1">
            <button
              type="button"
              @click="$emit('select-project', { entry, targetStep: 2 })"
              class="flex-1 py-2.5 px-3 rounded-2xl bg-[#38bdf8] hover:bg-[#0284c7] hover:text-white border-2 border-slate-900 shadow-[0_3px_0_#0f172a] active:translate-y-0.5 active:shadow-none text-slate-950 font-black text-xs transition cursor-pointer flex items-center justify-center gap-1.5"
            >
              <span>🔌</span>
              <span>Devreyi Aç (2. Adım)</span>
            </button>

            <button
              type="button"
              @click="$emit('select-project', { entry, targetStep: 3 })"
              class="py-2.5 px-3 rounded-2xl bg-[#c084fc] hover:bg-[#a855f7] hover:text-white border-2 border-slate-900 shadow-[0_3px_0_#0f172a] active:translate-y-0.5 active:shadow-none text-slate-950 font-black text-xs transition cursor-pointer flex items-center justify-center gap-1"
              title="Akış Şeması ve Arduino Kodunu Gör"
            >
              <span>🧠</span>
              <span>Akış & Kod</span>
            </button>
          </div>
        </div>

        <!-- Boş Durum -->
        <div
          v-if="filteredProjects.length === 0"
          class="col-span-full bg-white rounded-3xl p-8 border-2 border-dashed border-slate-400 text-center flex flex-col items-center gap-2"
        >
          <span class="text-4xl">🚀</span>
          <h4 class="text-sm font-black text-slate-800">Henüz kurguladığın bir proje yok</h4>
          <p class="text-xs font-bold text-slate-500">
            "1. Hayal Et" ekranından hayalindeki projeyi yazıp "Devreyi ve Kodu Tasarla!" butonuna bastığında projelerin otomatik olarak buraya kaydedilir.
          </p>
        </div>
      </div>

    </div>
  </div>
</template>

<script setup lang="ts">
import { ref, computed } from 'vue';
import type { SavedProjectEntry } from '../types/project';

const props = defineProps<{
  isOpen: boolean;
  projects: SavedProjectEntry[];
  activeProjectId?: string;
}>();

defineEmits<{
  (e: 'close'): void;
  (e: 'save-current'): void;
  (e: 'delete-project', id: string): void;
  (e: 'select-project', payload: { entry: SavedProjectEntry; targetStep: number }): void;
}>();

const activeFilter = ref<'all'>('all');
const searchQuery = ref('');

const filterTabs = computed(() => {
  const allCount = props.projects.length;
  return [
    { id: 'all' as const, icon: '⭐', label: 'Kurguladığım Projeler', count: allCount },
  ];
});

const filteredProjects = computed(() => {
  return props.projects.filter(p => {
    const q = searchQuery.value.trim().toLowerCase();
    if (!q) return true;

    const titleMatch = (p.project.proje_adi || '').toLowerCase().includes(q);
    const promptMatch = (p.prompt || '').toLowerCase().includes(q);
    const compMatch = (p.project.netlist?.components || []).some(c =>
      (c.label || '').toLowerCase().includes(q) || (c.type || '').toLowerCase().includes(q)
    );
    return titleMatch || promptMatch || compMatch;
  });
});
</script>

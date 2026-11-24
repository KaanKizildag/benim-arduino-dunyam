<template>
  <div
    v-if="isOpen"
    class="fixed inset-0 z-50 flex items-center justify-center p-3 sm:p-5 bg-slate-900/60 backdrop-blur-xs select-none"
    @click.self="$emit('close')"
  >
    <div
      class="bg-[#fdf2f8] border-[3px] border-slate-900 rounded-[32px] w-full max-w-4xl shadow-[0_12px_0_#0f172a] flex flex-col overflow-hidden max-h-[92vh] animate-in fade-in zoom-in-95 duration-200"
    >
      <!-- Üst Başlık & Veli Karşılama -->
      <div class="bg-[#f472b6] p-4 sm:p-5 border-b-[3px] border-slate-900 flex items-center justify-between">
        <div class="flex items-center gap-3">
          <div class="w-12 h-12 rounded-2xl bg-white border-2 border-slate-900 shadow-[0_3px_0_#db2777] flex items-center justify-center text-2xl">
            👨‍👩‍👧
          </div>
          <div>
            <div class="flex items-center gap-2">
              <h2 class="text-xl font-black text-slate-900">
                Veli Portfolyosu & Başarı Takibi
              </h2>
              <span class="px-2.5 py-0.5 rounded-lg bg-pink-100 border border-slate-900 text-xs font-black text-pink-950">
                {{ portfolioData?.parent?.full_name || 'Veli Paneli' }}
              </span>
            </div>
            <p class="text-xs font-bold text-pink-950/80">
              Çocuğunuzun Gelişim Portfolyosu, Çalışan Devreleri & KVKK Mahremiyet Ayarları
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

      <!-- Çocuklar Arasında Geçiş (Birden çok çocuk varsa) -->
      <div
        v-if="portfolioData?.children && portfolioData.children.length > 1"
        class="flex items-center gap-2 px-6 pt-3 bg-white border-b-2 border-slate-200"
      >
        <span class="text-xs font-black text-slate-600">Öğrenci:</span>
        <button
          v-for="(child, idx) in portfolioData.children"
          :key="child.student.id"
          type="button"
          @click="selectedChildIndex = idx"
          :class="[
            'px-3 py-1.5 rounded-t-xl font-black text-xs border-t-2 border-x-2 cursor-pointer transition',
            selectedChildIndex === idx
              ? 'bg-[#fdf2f8] text-slate-900 border-slate-900 -mb-[2px]'
              : 'bg-slate-100 text-slate-600 border-transparent hover:bg-slate-200'
          ]"
        >
          👦 {{ child.student.full_name }}
        </button>
      </div>

      <!-- Ana İçerik -->
      <div class="p-4 sm:p-6 overflow-y-auto flex-1 bg-[#fdf2f8] space-y-5">
        
        <!-- 1. KVKK & ÇOCUK MAHREMİYETİ AÇIK RIZA KARTI -->
        <div class="bg-white p-4 sm:p-5 rounded-2xl border-2 border-slate-900 shadow-[0_3px_0_#94a3b8] flex flex-col md:flex-row items-start md:items-center justify-between gap-4">
          <div class="space-y-1 max-w-xl">
            <div class="flex items-center gap-2">
              <span class="text-lg">🛡️</span>
              <h3 class="text-sm font-black text-slate-900">
                KVKK & Kapalı Devre Medya İzni
              </h3>
              <span
                :class="[
                  'px-2 py-0.5 rounded-lg border text-[10px] font-black',
                  currentChild?.kvkk_consent
                    ? 'bg-emerald-100 border-emerald-500 text-emerald-800'
                    : 'bg-rose-100 border-rose-500 text-rose-800'
                ]"
              >
                {{ currentChild?.kvkk_consent ? '✅ İZİN VERİLDİ' : '❌ İZİN VERİLMEDİ' }}
              </span>
            </div>
            <p class="text-xs text-slate-600 font-bold leading-relaxed">
              Çocuğunuzun okul ortamında yaptığı çalışan devre videoları ve fotoğraflarının öğretmen tarafından çekilip, kapalı devre olarak yalnızca sizinle paylaşılmasına açık rıza veriyor musunuz?
            </p>
          </div>

          <button
            type="button"
            @click="toggleKvkkConsent"
            :class="[
              'px-4 py-2.5 rounded-xl border-2 border-slate-900 font-black text-xs transition active:translate-y-0.5 cursor-pointer whitespace-nowrap shrink-0 shadow-[0_3px_0_#0f172a]',
              currentChild?.kvkk_consent
                ? 'bg-rose-100 hover:bg-rose-200 text-rose-900'
                : 'bg-[#4ade80] hover:bg-[#22c55e] text-slate-900'
            ]"
          >
            {{ currentChild?.kvkk_consent ? 'İzni Kaldır (Paylaşımı Durdur)' : 'Açık Rıza Ver & İzin Ver ✅' }}
          </button>
        </div>

        <!-- 2. ÇOCUĞUN KİMLİK & BAŞARI ÖZETİ -->
        <div class="bg-white p-4 rounded-2xl border-2 border-slate-900 shadow-[0_3px_0_#94a3b8] flex flex-wrap items-center justify-between gap-4">
          <div class="flex items-center gap-3">
            <div class="w-14 h-14 rounded-2xl bg-amber-200 border-2 border-slate-900 shadow-[0_3px_0_#d97706] flex items-center justify-center text-3xl">
              👦
            </div>
            <div>
              <h3 class="text-base font-black text-slate-900">
                {{ currentChild?.student.full_name }}
              </h3>
              <div class="text-xs text-slate-600 font-bold">
                {{ currentChild?.student.institution_name }} &bull; Öğrenci No: {{ currentChild?.student.student_no }}
              </div>
            </div>
          </div>

          <!-- Rozet Sayaçları -->
          <div class="flex items-center gap-2">
            <button
              type="button"
              @click="showCertificateModal = true"
              class="px-3.5 py-2 rounded-xl bg-amber-300 hover:bg-amber-400 border-2 border-slate-900 shadow-[0_3px_0_#b45309] active:translate-y-0.5 text-slate-900 text-xs font-black flex items-center gap-1.5 cursor-pointer"
            >
              <span>🎓</span>
              <span>Başarı Sertifikasını Gör</span>
            </button>
          </div>
        </div>

        <!-- 3. PROJELER VE ÇALIŞAN DEVRE MEDYALARI -->
        <div>
          <div class="flex items-center justify-between mb-3">
            <h3 class="text-sm font-black text-slate-900 flex items-center gap-1.5">
              <span>🚀</span>
              <span>Çocuğumun Yaptığı Projeler & Videolar</span>
            </h3>
            <span class="text-xs font-black text-slate-500">
              Toplam {{ currentChild?.projects?.length || 0 }} Proje
            </span>
          </div>

          <div v-if="!currentChild?.projects || currentChild.projects.length === 0" class="p-8 text-center bg-white rounded-3xl border-2 border-dashed border-slate-300">
            <div class="text-4xl mb-2">🎈</div>
            <div class="text-sm font-black text-slate-700">Henüz Tamamlanmış Proje Bulunmuyor</div>
            <p class="text-xs text-slate-500 mt-1">Öğrenci derste projelerini tamamladıkça burada görüntülenecektir.</p>
          </div>

          <div class="grid grid-cols-1 md:grid-cols-2 gap-4">
            <div
              v-for="p in currentChild?.projects"
              :key="p.id"
              class="bg-white rounded-2xl border-2 border-slate-900 shadow-[0_3px_0_#94a3b8] p-4 flex flex-col justify-between gap-3"
            >
              <div>
                <div class="flex items-center justify-between mb-1.5">
                  <h4 class="font-black text-sm text-slate-900">{{ p.title }}</h4>
                  <span
                    :class="[
                      'px-2 py-0.5 rounded-lg border text-[10px] font-black',
                      p.is_circuit_approved
                        ? 'bg-emerald-100 border-emerald-500 text-emerald-800'
                        : 'bg-amber-100 border-amber-500 text-amber-800'
                    ]"
                  >
                    {{ p.is_circuit_approved ? '✅ Devre Onaylandı' : '⏳ Kontrol Bekliyor' }}
                  </span>
                </div>

                <p class="text-xs text-slate-600 font-bold mb-3">
                  {{ p.description || 'Arduino projesi başarıyla inşa edildi.' }}
                </p>

                <!-- Öğretmen Rozetleri ve Tebrik Notu -->
                <div v-if="p.feedback && p.feedback.length > 0" class="bg-amber-50 p-2.5 rounded-xl border border-amber-200 mb-3">
                  <div class="flex items-center gap-1.5 font-black text-xs text-amber-900 mb-1">
                    <span>🎖️</span>
                    <span>Öğretmen Rozeti: {{ p.feedback[0].badge }}</span>
                  </div>
                  <div class="text-[11px] text-amber-800 font-bold italic">
                    "{{ p.feedback[0].feedback_text }}"
                  </div>
                </div>

                <!-- Çalışan Devre Videosu / Fotoğrafı (Kapalı Devre Medya) -->
                <div v-if="p.media && p.media.length > 0" class="space-y-2">
                  <div class="text-[10px] font-black uppercase text-slate-500 tracking-wider">
                    📹 Sınıftan Çalışan Devre Kaydı:
                  </div>
                  <div class="rounded-xl overflow-hidden border-2 border-slate-900 bg-black flex items-center justify-center max-h-48">
                    <!-- Token ile Stream Edilen Video -->
                    <video
                      v-if="p.media[0].media_type === 'video'"
                      controls
                      class="w-full max-h-48 object-contain"
                      :src="getMediaUrl(p.media[0].id)"
                    ></video>
                    <img
                      v-else
                      :src="getMediaUrl(p.media[0].id)"
                      alt="Çalışan Devre Fotoğrafı"
                      class="w-full max-h-48 object-contain"
                    />
                  </div>
                </div>
                <div v-else class="text-[11px] text-slate-400 italic bg-slate-50 p-2 rounded-lg border border-slate-200 text-center">
                  📹 Öğretmen henüz çalışan devre videosu yüklemedi.
                </div>
              </div>

              <div class="pt-2 border-t border-slate-100 flex items-center justify-between text-[10px] text-slate-400 font-bold">
                <span>Eklenme: {{ new Date(p.created_at).toLocaleDateString('tr-TR') }}</span>
                <span class="text-emerald-600 font-black">🌟 Gurur Duyuyoruz!</span>
              </div>
            </div>
          </div>
        </div>

      </div>

      <!-- 4. BAŞARI SERTİFİKASI MODAL ÖNİZLEMESİ -->
      <div
        v-if="showCertificateModal"
        class="fixed inset-0 z-60 flex items-center justify-center p-4 bg-slate-900/70 backdrop-blur-xs"
        @click.self="showCertificateModal = false"
      >
        <div class="bg-amber-50 border-[4px] border-amber-500 rounded-[32px] p-6 sm:p-8 max-w-lg w-full shadow-[0_12px_0_#92400e] text-center relative">
          <div class="text-5xl mb-2">🎓</div>
          <div class="text-xs font-black tracking-widest text-amber-700 uppercase mb-1">
            Geleceğin Mühendisi Başarı Belgesi
          </div>
          <h2 class="text-2xl font-black text-slate-900 mb-2">
            {{ currentChild?.student.full_name }}
          </h2>
          <p class="text-xs text-slate-700 font-bold leading-relaxed mb-6">
            {{ currentChild?.student.institution_name }} bünyesinde Arduino devre tasarımı, algoritma ve yapay zeka destekli elektronik eğitimini üstün başarıyla sürdürdüğü için bu belge ile tebrik edilir!
          </p>
          <div class="flex items-center justify-center gap-3">
            <button
              type="button"
              @click="printCertificate"
              class="px-5 py-2.5 bg-amber-400 hover:bg-amber-500 border-2 border-slate-900 shadow-[0_3px_0_#b45309] rounded-xl text-xs font-black text-slate-900 cursor-pointer"
            >
              🖨️ Sertifikayı Yazdır / İndir
            </button>
            <button
              type="button"
              @click="showCertificateModal = false"
              class="px-5 py-2.5 bg-white hover:bg-slate-100 border-2 border-slate-900 shadow-[0_3px_0_#64748b] rounded-xl text-xs font-black text-slate-800 cursor-pointer"
            >
              Kapat
            </button>
          </div>
        </div>
      </div>

    </div>
  </div>
</template>

<script setup lang="ts">
import { ref, computed, onMounted, watch } from 'vue';
import { useAuth } from '../composables/useAuth';

const props = defineProps<{
  isOpen: boolean;
}>();

const emit = defineEmits<{
  (e: 'close'): void;
}>();

const { getAuthHeaders, token } = useAuth();

const portfolioData = ref<any>(null);
const selectedChildIndex = ref(0);
const showCertificateModal = ref(false);

const currentChild = computed(() => {
  if (
    portfolioData.value &&
    portfolioData.value.children &&
    portfolioData.value.children.length > selectedChildIndex.value
  ) {
    return portfolioData.value.children[selectedChildIndex.value];
  }
  return null;
});

async function fetchPortfolio() {
  try {
    const res = await fetch('/api/parent/portfolio', {
      headers: getAuthHeaders()
    });
    if (res.ok) {
      portfolioData.value = await res.json();
    }
  } catch (err) {
    console.error('Veli portfolyosu yüklenemedi:', err);
  }
}

async function toggleKvkkConsent() {
  if (!currentChild.value) return;
  const currentConsent = Boolean(currentChild.value.kvkk_consent);
  const newConsent = !currentConsent;

  try {
    const res = await fetch('/api/parent/consent', {
      method: 'POST',
      headers: { ...getAuthHeaders(), 'Content-Type': 'application/json' },
      body: JSON.stringify({
        student_id: currentChild.value.student.id,
        consent_given: newConsent
      })
    });
    if (res.ok) {
      currentChild.value.kvkk_consent = newConsent;
    }
  } catch (err) {
    console.error('KVKK onayı güncellenemedi:', err);
  }
}

function getMediaUrl(mediaId: string): string {
  // Kapalı devre erişim: token parametresi ile stream edilir
  return `/api/media/stream/${mediaId}?token=${encodeURIComponent(token.value || '')}`;
}

function printCertificate() {
  window.print();
}

watch(() => props.isOpen, (open) => {
  if (open) {
    fetchPortfolio();
  }
});

onMounted(() => {
  if (props.isOpen) {
    fetchPortfolio();
  }
});
</script>

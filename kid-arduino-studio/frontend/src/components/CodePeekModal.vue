<template>
  <div
    v-if="isOpen"
    class="fixed inset-0 z-50 flex items-center justify-center p-4 bg-slate-950/60 backdrop-blur-sm animate-fade-in"
    @click.self="emit('close')"
  >
    <div class="bg-slate-900 border-2 border-slate-700 w-full max-w-3xl rounded-3xl shadow-2xl overflow-hidden flex flex-col max-h-[85vh]">
      <!-- Modal Başlık Çubuğu -->
      <div class="px-6 py-4 bg-slate-800/80 border-b border-slate-700 flex items-center justify-between">
        <div class="flex items-center gap-3">
          <div class="w-9 h-9 rounded-xl bg-purple-500/20 border border-purple-500/40 text-purple-400 flex items-center justify-center font-black text-lg">
            💻
          </div>
          <div>
            <h3 class="text-base font-extrabold text-white flex items-center gap-2">
              <span>Perde Arkasındaki Gerçek Arduino Kodu</span>
              <span class="text-[10px] bg-indigo-500/20 text-indigo-300 border border-indigo-500/40 px-2 py-0.5 rounded-full font-mono">
                C++ (.ino)
              </span>
            </h3>
            <p class="text-xs text-slate-400">Meraklı mucitler için Arduino'nun okuduğu gerçek programlama kodu!</p>
          </div>
        </div>

        <button
          @click="emit('close')"
          class="w-8 h-8 rounded-xl bg-slate-700/60 hover:bg-slate-700 text-slate-400 hover:text-white flex items-center justify-center font-bold transition"
        >
          ✕
        </button>
      </div>

      <!-- Kod Önizleme Alanı -->
      <div class="relative flex-1 overflow-auto p-4 bg-slate-950 font-mono text-xs sm:text-sm text-slate-200">
        <!-- Kod Satırları -->
        <pre class="leading-relaxed select-text whitespace-pre overflow-x-auto p-2"><code>{{ code }}</code></pre>
      </div>

      <!-- Alt Bilgi ve Aksiyonlar -->
      <div class="px-6 py-4 bg-slate-800/80 border-t border-slate-700 flex flex-wrap items-center justify-between gap-3">
        <div class="flex items-center gap-2 text-xs text-slate-400">
          <span class="w-2 h-2 rounded-full bg-emerald-400 animate-pulse"></span>
          <span>arduino:avr:uno kartına hazır derlenebilir kod</span>
        </div>

        <div class="flex items-center gap-2">
          <!-- Kodu Kopyala -->
          <button
            @click="copyCode"
            class="px-4 py-2 rounded-xl bg-slate-700 hover:bg-slate-600 text-white text-xs font-bold transition flex items-center gap-1.5"
          >
            <span>{{ isCopied ? '✓ Kopyalandı!' : '📋 Kodu Kopyala' }}</span>
          </button>

          <!-- .ino Dosyası Olarak İndir -->
          <button
            @click="downloadIno"
            class="px-4 py-2 rounded-xl bg-indigo-600 hover:bg-indigo-500 text-white text-xs font-bold transition flex items-center gap-1.5 shadow"
          >
            <span>💾 .ino Dosyasını İndir</span>
          </button>
        </div>
      </div>
    </div>
  </div>
</template>

<script setup lang="ts">
import { ref } from 'vue';

const props = defineProps<{
  isOpen: boolean;
  code: string;
  projectName?: string;
}>();

const emit = defineEmits<{
  (e: 'close'): void;
}>();

const isCopied = ref(false);

async function copyCode() {
  try {
    await navigator.clipboard.writeText(props.code);
    isCopied.value = true;
    setTimeout(() => {
      isCopied.value = false;
    }, 2000);
  } catch (err) {
    console.error('Kopyalama hatası:', err);
  }
}

function downloadIno() {
  const blob = new Blob([props.code], { type: 'text/plain;charset=utf-8' });
  const url = URL.createObjectURL(blob);
  const a = document.createElement('a');
  const safeName = (props.projectName || 'KidArduinoProject').replace(/[^a-zA-Z0-9_-]/g, '_');
  a.href = url;
  a.download = `${safeName}.ino`;
  document.body.appendChild(a);
  a.click();
  document.body.removeChild(a);
  URL.revokeObjectURL(url);
}
</script>

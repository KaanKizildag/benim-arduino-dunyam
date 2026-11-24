---
name: kid-arduino-design-system
description: "Kid Arduino Studio projesinin çocuk dostu 3D çizgi film (Cartoon Neobrutalism) tasarım kuralları, UI bileşen standartları, renk paleti ve taşma önleme rehberi. Yeni ekran, modal veya bileşen tasarlarken daima bu kurallara uyulmalıdır."
---

# Kid Arduino Studio — Tasarım Sistemi ve Arayüz Kuralları

Bu kılavuz, **Kid Arduino Studio** projesinde tasarlanacak tüm yeni ekranlar, modallar, kartlar ve butonlar için temel tasarım standartlarını belirler. Projenin görsel bütünlüğünü korumak için yeni arayüz geliştirmelerinde bu kurallara titizlikle uyulmalıdır.

---

## 1. Tasarım Felsefesi: "Cartoon Neobrutalism"
Arayüz, 8-15 yaş arası çocukların ilgisini çekecek neşeli, renkli, yüksek kontrastlı ve dokunulası bir **3D Çizgi Film Oyun Dünyası** hissi vermelidir.
- **Kalın Siyah Çizgiler:** Tüm kartlar, butonlar ve modallar kalın koyu çerçevelere sahiptir (`border-2` veya `border-[3px] border-slate-900`).
- **Sert 3D Gölgeler:** Bulanık ve soluk gölgeler yerine fiziksel 3D basılabilir hissi veren sert gölgeler kullanılır (`shadow-[0_4px_0_#0f172a]`, `shadow-[0_3px_0_#ca8a04]`).
- **Mekanik Basma Hissi:** Tıklanabilir her öğe fare tıklandığında fiziksel olarak aşağı çöker: `active:translate-y-0.5 active:shadow-none`.
- **Cömert Yuvarlak Köşeler:** Sivri köşeler yasaktır. Butonlar `rounded-xl` / `rounded-2xl`, bilgi kartları `rounded-2xl` / `rounded-3xl`, modallar `rounded-[32px]`.

---

## 2. Renk Paleti (Color Tokens)

| Bölge / Rol | Tailwind Sınıfı | HEX Değeri | Kullanım Alanı |
|---|---|---|---|
| **Ana Üst Bar (Sky)** | `bg-[#7dd3fc]` | `#7dd3fc` | Üst navigasyon barı, canlı su mavisi arka plan |
| **Modal Başlığı** | `bg-[#bae6fd]` veya gradyan | `#bae6fd` | AI ve ayar modallarının üst başlık şeridi |
| **Eylem & Vurgu (Sarı)** | `bg-[#fde047]` / `bg-[#fbbf24]` | `#fbbf24` | Birincil aksiyon butonları, aktif sekmeler, parlayan rozetler |
| **Sevimli Robot & Kartlar** | `bg-[#fef08a]` | `#fef08a` | İkon arka planları, robot rozetleri, dikkat kutuları |
| **Başarı & Onay (Yeşil)** | `bg-[#4ade80]` / `bg-emerald-500` | `#10b981` | Tamamlanan adımlar, çalışan devreler, doğru bağlantılar |
| **Uyarı & İpucu (Amber)** | `bg-amber-100` / `border-amber-400` | `#f59e0b` | Bilgi ipuçları, çanta hatırlatıcıları, breadboard rozeti |
| **İptal & Hata (Kırmızı)** | `bg-rose-500` / `bg-rose-600` | `#f43f5e` | Kapatma çarpıları (✕), tasarımı durdur/iptal butonları |
| **Çerçeve & Kontrast** | `border-slate-900` | `#0f172a` | Standart çizgi film sınır çizgisi |
| **Karanlık Çalışma Alanı** | `bg-slate-900` / `bg-[#0f172a]` | `#0f172a` | SVG devre simülasyon tezgahı ve breadboard zemini |

---

## 3. Ekran ve Modal Boyutlandırma Kuralları (Fit-to-Screen)

> [!IMPORTANT]
> **ASLA TAM EKRAN DİKEY TAŞMAYA (VERTICAL OVERFLOW) İZİN VERME!**
> Kullanıcı bileşen ekledikçe veya içerik uzadıkça modal pencere büyüyüp ekranın altına doğru kaybolamaz.

### Modal Tasarım Şablonu
```html
<!-- Karartma Arka Planı -->
<div class="fixed inset-0 z-50 bg-slate-900/75 backdrop-blur-xs flex items-center justify-center p-3 sm:p-5 select-none animate-in fade-in">
  <!-- Modal Konteyneri: max-h-[88vh] ZORUNLUDUR! -->
  <div class="bg-white rounded-[32px] border-[3px] border-slate-900 shadow-[0_14px_0_rgba(15,23,42,0.35)] max-w-2xl w-full max-h-[88vh] overflow-hidden flex flex-col">
    
    <!-- 1. Sabit Üst Başlık (Shrink-0) -->
    <div class="px-5 py-3.5 bg-[#bae6fd] border-b-[3px] border-slate-900 flex items-center justify-between shrink-0">
      <div class="flex items-center gap-3">
        <div class="w-10 h-10 rounded-2xl bg-white border-2 border-slate-900 flex items-center justify-center text-2xl shadow-xs">
          🤖
        </div>
        <div>
          <h3 class="text-base sm:text-lg font-black text-slate-900 leading-tight">Başlık</h3>
          <p class="text-[11px] font-bold text-slate-700">Alt açıklama</p>
        </div>
      </div>
      <!-- Mutlaka Kapatma Çarpısı -->
      <button type="button" @click="$emit('close')" class="w-8 h-8 rounded-xl bg-rose-500 hover:bg-rose-600 text-white font-black text-sm flex items-center justify-center border-2 border-slate-900 shadow-[0_2px_0_#9f1239] cursor-pointer transition">
        ✕
      </button>
    </div>

    <!-- 2. Kaydırılabilir İç Gövde (overflow-y-auto + flex-1) -->
    <div class="p-4 sm:p-5 flex-1 overflow-y-auto flex flex-col gap-3 bg-slate-50">
      <!-- İçerik burada yer alır -->
      <!-- Dinamik büyüyen listeler (örn. parçalar) max-h-40 overflow-y-auto ile sınırlandırılır -->
    </div>

    <!-- 3. Sabit Alt Eylem Çubuğu (Gerekiyorsa, shrink-0) -->
    <div class="px-5 py-3 bg-white border-t-2 border-slate-900 flex items-center justify-between shrink-0">
      <span class="text-xs font-bold text-slate-500">Durum bilgisi</span>
      <div class="flex items-center gap-2">
        <button type="button" class="btn-primary">Tamam</button>
      </div>
    </div>

  </div>
</div>
```

---

## 4. Tipografi ve Metin Standartları
- **Yazı Ailesi:** Sistem sans-serif fontları (`ui-sans-serif, system-ui, Inter, sans-serif`).
- **Ağırlıklar:**
  - Başlıklar ve Rozetler: `font-black` (weight: 900)
  - Ara Başlıklar ve Butonlar: `font-extrabold` (weight: 800)
  - Açıklamalar ve Gövde: `font-bold` (weight: 700)
- **Dil ve Ton:**
  - Türkçe, samimi, teşvik edici, eğitici ve pozitif.
  - "Hata oluştu" yerine: "Minik bir sorun çıktı, merak etme hemen düzeltiyoruz!"
  - "Devreyi kur" yerine: "Devreni kuralım ve ışıkları yakalım! 🚀"
  - Her kavram için sevimli bir emoji (🍞 Breadboard, ⚡ Kablo, 🎒 Çanta, 💡 Fikir, 🤖 AI Mucit).

---

## 5. Çocuk Dostu Okuma Hızı ve Zamanlamalar
- **"Biliyor muydun?" İpuçları:** Çocukların okuma ve kavrama hızına saygı duyulmalıdır. Metin geçiş süreleri **en az 10-12 saniye** olmalı, otomatik geçiş duraklatılabilmeli (⏸️) ve çocuk istediğinde ileri/geri gidebilmelidir.
- **İlerleme Çubuğu:** Çok hızlı sıçramak yerine yumuşak geçişli (`transition-all duration-300`) olmalıdır.
- **İptal Edebilme:** Kullanıcı yanlış prompt yazdığında veya beklemek istemediğinde tek tıkla işlemi durdurabilmelidir (`AbortController` ile SSE bağlantısı kesilmeli, modal hemen kapanmalıdır).

---

## 6. Token ve Ayar Saklama Kuralları
- **Kalıcı `localStorage` Anahtarları:**
  - `kid_arduino_gemini_key`: Google Gemini API anahtarı
  - `kid_arduino_openai_key`: OpenAI API anahtarı
  - `kid_arduino_anthropic_key`: Anthropic API anahtarı
  - `kid_arduino_selected_model`: Tercih edilen yapay zeka modeli
  - `kid_arduino_auto_save`: Otomatik kayıt tercihi
- Kullanıcı bir API anahtarı girdiğinde sayfa yenilendiğinde tekrar girmek zorunda kalmamalıdır.
- Admin panelinde API anahtarları varsayılan olarak maskeli (`type="password"`) görünmeli, 👁️ ikonuna basılarak görünür kılınabilmelidir.

# 🤖 KidArduino Studio
### Çocuklar İçin AI Destekli Görsel Arduino Stüdyosu (Yerel/Local & Bulut)

8-14 yaş arası çocuklar için tasarlanmış; geleneksel C++ kodlama ve karmaşık devre şemaları yerine **doğal dil ile proje üretmeye, adım adım görsel devre kurmaya ve koddan türetilen akış diyagramlarıyla sebep-sonuç düşünmeye** odaklanan web tabanlı bir Arduino IDE'dir.

Çocuk ne yapmak istediğini Türkçe anlatır (*"Odam kararınca gece lambam yansın"*). Yapay zeka; çocuğun elindeki parçalara göre devreyi ve Arduino kodunu tasarlar, 30 sütunluk breadboard üzerinde kabloları adım adım nereye takacağını gösterir, kodun mantığını akış diyagramıyla anlatır ve kodu Arduino Uno'ya yükler.

---

## 🚀 Hızlı Başlatma

İki yol var. İkisini **aynı anda çalıştırmayın**: ikisi de 5173 ve 8001 portlarını kullanır ve tarayıcının hangisine bağlandığı karışır.

### Seçenek A: Docker ile
Backend ve frontend tek komutla ayağa kalkar. Yerel model kullanacaksanız Ollama Docker'da değil, bilgisayarınızda çalışır. Ayrıntılar ve ilk çalıştırma hazırlığı için **[README.Docker.md](README.Docker.md)** dosyasına bakın.

```bash
cd kid-arduino-studio
docker compose up -d --build
```

### Seçenek B: Yerelde Geliştirme Modu (Önerilen)

**1. Backend (Python 3.11+):**
```bash
cd backend

# A. Sanal ortamı (venv) oluşturun ve aktif edin
python -m venv .venv

# Windows PowerShell:
.\.venv\Scripts\Activate.ps1
# Windows CMD:
.\.venv\Scripts\activate.bat
# Linux / macOS:
source .venv/bin/activate

# B. Gerekli kütüphaneleri yükleyin
pip install -r requirements.txt

# C. Ortam değişkenleri şablonunu kopyalayın
copy .env.example .env    # Windows
# cp .env.example .env    # Linux / macOS

# D. Backend sunucusunu başlatın (Port 8001)
python -m uvicorn main:app --port 8001 --reload
```
- Backend `http://localhost:8001` adresinde çalışır (API dokümanı: `http://localhost:8001/docs`).
- Port **8001** olmalıdır; frontend geliştirme sunucusu `/api` isteklerini `127.0.0.1:8001`'e yönlendirir (`frontend/vite.config.ts`).
- `--reload` sayesinde Python kodu değişince sunucu kendini otomatik yeniden başlatır.
- `python -m uvicorn` kullanımı PATH problemlerini önler.

**2. Frontend (Node.js 18+):**
Ayrı bir terminal penceresinde:
```bash
cd frontend
npm install
npm run dev
```

**3. Tarayıcıda açın:** **`http://localhost:5173`**

> 💡 **Not:** Proje üretmek için bir yapay zeka modeli gerekir (Ollama veya bir bulut modeli için API anahtarı; aşağıya bakın). Hazır demo proje yoktur. Kaydettiğiniz projeler **📂 Projelerim** penceresinde durur.

### Arduino kartına yükleme (arduino-cli)
Kodu derleyip karta yüklemek için backend'in çalıştığı makinede [arduino-cli](https://arduino.github.io/arduino-cli/) ve AVR çekirdeği kurulu olmalıdır:
```bash
arduino-cli core update-index
arduino-cli core install arduino:avr
```
`arduino-cli` PATH'te değilse yolunu `backend/.env` içinde `ARDUINO_CLI_PATH` ile verebilirsiniz. Docker imajında arduino-cli hazır gelir, ancak konteyner bilgisayarın USB/COM portlarını görmez; **gerçek karta yüklemek için backend'i yerelde (Seçenek B) çalıştırın.**

---

## 🧠 Yapay Zeka Seçenekleri (Yerel ve Bulut)

KidArduino Studio, **LiteLLM** sayesinde hem yerel (Ollama) hem de bulut modelleriyle çalışır. Model, üst menüdeki **🤖 AI Modeli** butonundan seçilir ve seçiminiz tarayıcıda hatırlanır. Bu buton yalnızca **admin modunda** görünür: sol üstteki çocuk avatarına (👦) tıklayarak admin moduna (👑) geçebilirsiniz.

### A. Yerel Model (Ollama)
1. [Ollama](https://ollama.com)'yı bilgisayarınıza kurup bir model indirin (Docker ile çalıştırsanız da Ollama bilgisayarınızda çalışır):
   ```bash
   ollama pull qwen2.5-coder:1.5b
   ```
2. **🤖 AI Modeli** penceresi kurulu modelleri otomatik listeler. Yerel modda backend `http://127.0.0.1:11434` adresine, Docker'da `http://host.docker.internal:11434` adresine bağlanır.

> ⚠️ 1.5B gibi küçük modeller çoğu zaman doğrulamadan geçen bir devre üretemiyor ve bilgisayarı yoruyor. Daha güvenilir sonuç için bulut modeli önerilir.

### B. Bulut Modelleri (Gemini, OpenAI, Claude)
- Seçilebilen modeller: **Google Gemini** (3.8 Flash, 3.5 Flash Lite, 2.5 Flash, 2.5 Pro), **OpenAI** (GPT-4o Mini, GPT-4o, GPT-4.1 Mini) ve **Anthropic Claude** (3.5 Haiku, 3.5 Sonnet). Gemini anahtarı tanımlıysa liste Google'dan canlı olarak çekilir.
- Ollama çalışmıyorsa varsayılan model `gemini/gemini-2.5-flash`'tır.
- **Önerilen yol:** Anahtarı `backend/.env` dosyasına yazın (şablon: `backend/.env.example`):
  ```env
  GEMINI_API_KEY=
  OPENAI_API_KEY=
  ANTHROPIC_API_KEY=
  ```
  `.env` dosyası `.gitignore`'dadır, GitHub'a gitmez. **Anahtarları asla `.env.example`'a, koda ya da commit mesajlarına yazmayın.**
- Alternatif olarak anahtarı **🤖 AI Modeli** penceresine girebilirsiniz; bu durumda anahtar yalnızca o tarayıcının yerel deposunda (localStorage) saklanır.
- Bir bulut modeli "high demand / 503" hatası verirse bu, sağlayıcının geçici yoğunluğudur; biraz sonra tekrar deneyin veya başka bir model seçin.

---

## ⚡ 4 Adımlı Mucit Serüveni

1. **💭 1. Hayal Et (Page1HayalEt):** Hayalindeki projeyi yaz ya da **💡 Fikirler** atölyesinden elindeki malzemelere uygun bir proje seç. **🧰 Çantam** ile elindeki parçaları işaretle; yapay zeka devreyi bu parçalara göre tasarlar. Üretim sırasında yapay zekanın yanıtı canlı akar (SSE): tespit edilen parçalar anında yeşillenir ve beklerken çocuk dostu benzetme kartları gösterilir.
2. **🔌 2. Devreyi Kur (Page2DevreyiKur):** Wokwi parçalarıyla çizilmiş Arduino Uno ve 30 sütunluk breadboard. Kablolar tek tek gösterilir; **Sonraki Kablo** ile adım adım ilerlenir veya tüm kablolar birden görüntülenir. Sahne ekrana sığacak şekilde ölçeklenir. **Projeyi AI ile Geliştir & Revize Et** ile mevcut projeye yeni istek eklenebilir (ör. "sarı ikaz lambası ekle").
3. **🧠 3. Nasıl Çalışacak? (Page3NasilCalisacak):** Arduino kodundan türetilen **dinamik akış diyagramı**: kurulum, sensör okuma, karar (Evet/Hayır dalları), eylem, bekleme ve döngü adımları; her adımda ilgili parçalar ve pinler gösterilir.
4. **🚀 4. Çalıştır (Page4Calistir):** Kodu derleyip tek tıkla Arduino Uno'ya yükle ve karttan gelen canlı seri port verilerini izle. Meraklılar **</> Perde Arkasındaki Kodu Gör** ile C++ kodunu inceleyebilir.

Ek özellikler:
- **📂 Projelerim:** Kayıtlı projeler. **💾 Otomatik Kayıt** açıksa üretilen projeler kendiliğinden arşive eklenir; kapalıysa elle kaydedilir.
- **👦 Çocuk modu / 👑 Admin modu:** Sol üstteki avatara tıklanarak geçilir. **🤖 AI Modeli** ve **🛠️ Admin Log** (yapay zekaya giden istekler ve yanıtlar, hata ayıklama için) yalnızca admin modunda görünür.

---

## 🛠️ Doğrulama Katmanları

Yapay zekanın hayal ürünü ya da hatalı devreler üretmesini engellemek için birkaç deterministik kontrol vardır:

**Backend (Python):**
- **Netlist doğrulama:** Yalnızca desteklenen Wokwi parça tipleri kabul edilir; parçaların bacakları eksiksiz bağlı olmalı, sensör ve çıkış parçaları bir Arduino sinyal pinine (D2–D13, A0–A5) ya da motor sürücüye bağlanmalıdır.
- **Kod ↔ Netlist uyumu:** Kodda kullanılan pinler ile devrede bağlı pinler birebir aynı olmalıdır.
- **Otomatik tamamlama:** Kodda kullanılıp devrede unutulan parçalar ve 2 bacaklı LDR için gereken 10kΩ dirençler otomatik eklenir.
- **Akış diyagramı:** Koddan ayrı bir adımda üretilir ve doğrulanır (`flow_service.py`).
- **Türkçe karakter temizliği:** Değişken adlarındaki Türkçe harfler (ör. `ESİK_DEGER`) derleyici hata vermesin diye ASCII'ye çevrilir; yorumlar ve metinler korunur (`arduino_code_utils.py`).

**Frontend (breadboard yerleşimi, `circuit/BreadboardAllocator.ts`):**
- Bir parçanın iki bacağı asla aynı sütuna takılmaz (kısa devre yasağı).
- Farklı elektrik hatları (net) aynı sütun şeridini paylaşamaz; üst yarı (A–E) ve alt yarı (F–J) kendi içinde bağlıdır.
- Seri bağlı elemanlar (LED + direnç, LDR + direnç, buton + pull-down) ortak sütunda buluşturulur.
- Üst yarı dolunca alt yarıya geçilir. Modüller (4 pinli LDR, servo, HC-SR04 vb.) sağdaki modül alanına dizilir.

---

## 🧪 Testler

```bash
cd kid-arduino-studio/backend
python test_arduino_code_utils.py
python test_backend_repair.py
```

---

## 🩹 Sık Karşılaşılan Sorunlar

- **Ollama modelleri listede görünmüyor:** Bilgisayarınızda Ollama'nın çalıştığını ve en az bir model indirildiğini kontrol edin (`ollama list`).
- **Arayüz değişikliği görünmüyor:** Tarayıcı eski sayfayı önbellekten açıyor olabilir; **Ctrl+F5** ile yenileyin.
- **Backend değişikliği etki etmiyor:** Yerel modda `uvicorn`'u `--reload` ile başlatın ya da yeniden başlatın. Docker'da imajı yeniden derleyin (bkz. [README.Docker.md](README.Docker.md)).

---

## 📁 Proje Dizin Yapısı

```text
kid-arduino-studio/
├── backend/
│   ├── main.py                  # FastAPI uç noktaları (/api/generate-stream, /api/revise-stream, /api/generate-project, /api/models, /api/projects, /api/upload, /api/fix-code, /api/ports, /api/serial-events, /api/ai-logs)
│   ├── ai_service.py            # LiteLLM ile çoklu sağlayıcı (Ollama, Gemini, OpenAI, Claude) proje üretimi ve doğrulama
│   ├── flow_service.py          # Koddan dinamik akış diyagramı (AkisDiyagrami) üretimi ve doğrulaması
│   ├── arduino_service.py       # arduino-cli ile port algılama, derleme ve yükleme
│   ├── arduino_code_utils.py    # Değişken adlarındaki Türkçe harfleri ASCII'ye çeviren temizleyici
│   ├── schemas.py               # Ortak Pydantic v2 veri modelleri
│   ├── test_*.py                # Backend testleri
│   ├── requirements.txt
│   ├── Dockerfile
│   └── .env.example             # GEMINI_API_KEY, OPENAI_API_KEY, ANTHROPIC_API_KEY, OLLAMA_API_BASE, ARDUINO_CLI_PATH
│   # Çalışırken oluşan (git'e girmeyen) veri dosyaları: saved_projects.json, ai_logs.json
├── frontend/
│   ├── src/
│   │   ├── App.vue
│   │   ├── components/
│   │   │   ├── TopNavigation.vue        # Logo, 1-2-3-4 adım sekmeleri ve üst menü butonları
│   │   │   ├── Page1HayalEt.vue         # Fikir yazma, fikir kartları ve 'Devreyi ve Kodu Tasarla'
│   │   │   ├── Page2DevreyiKur.vue      # Arduino + breadboard sahnesi, adım adım kablo rehberi
│   │   │   ├── Page3NasilCalisacak.vue  # Koddan türetilen dinamik akış diyagramı
│   │   │   ├── Page4Calistir.vue        # Karta yükleme ve canlı seri port verisi
│   │   │   ├── AIModelModal.vue         # '🤖 AI Modeli' seçici (Ollama, Gemini, OpenAI, Claude)
│   │   │   ├── MalzemeCantasiModal.vue  # '🧰 Çantam' (elindeki malzemeler)
│   │   │   ├── ProjeFikirleriModal.vue  # '💡 Fikirler' (Proje Fikirleri Atölyesi)
│   │   │   ├── AIRevisionModal.vue      # 'Projeyi AI ile Geliştir & Revize Et'
│   │   │   ├── ProjelerimModal.vue      # '📂 Projelerim'
│   │   │   ├── AdminAILogsModal.vue     # '🛠️ Admin (AI Log)'
│   │   │   ├── CodePeekModal.vue        # '</> Perde Arkasındaki Kodu Gör'
│   │   │   └── wokwi-*.ts               # Özel Wokwi parça bileşenleri (breadboard, LDR, modüller)
│   │   ├── circuit/                     # Breadboard yerleşimi (BreadboardAllocator), kablo yönlendirme (WireRouter), modül geometrisi, doğrulama
│   │   ├── constants/pinCoordinates.ts  # Breadboard ve Arduino Uno pin koordinatları
│   │   ├── utils/pinResolver.ts
│   │   └── types/project.ts             # Backend JSON şemasıyla uyumlu TypeScript tipleri
│   ├── vite.config.ts                   # Geliştirme sunucusu ve /api → 127.0.0.1:8001 yönlendirmesi
│   ├── nginx.conf                       # Docker'da derlenmiş arayüzü sunar ve /api'yi backend'e iletir
│   └── package.json
├── docker-compose.yml                   # backend + frontend (Ollama bilgisayarda çalışır)
├── README.Docker.md
└── README.md
```

# 🤖 KidArduino Studio
### Çocuklar İçin AI Destekli Görsel Arduino Stüdyosu (Yerel/Local & Bulut)

8-14 yaş arası çocuklar için tasarlanmış; geleneksel C++ kodlama ve karmaşık devre şemaları yerine **doğal dil ile proje üretmeye, adım adım görsel devre kurmaya ve interaktif sebep-sonuç algoritmalarına** odaklanan web tabanlı bir Arduino IDE'dir.

Çocuk ne yapmak istediğini Türkçe anlatır (*"Odam kararınca gece lambam yansın, biri yaklaşınca buzzer ötsün"*). Yapay zeka; çocuğun elindeki parçalara göre devreyi tasarlar, 30 sütunluk standart breadboard üzerinde adım adım kabloları nereye takacağını parıldayan pinlerle gösterir, bloksuz sebep-sonuç simülatörüyle mantığını çalıştırır ve tek tıkla Arduino Uno'ya yükler!

---

## 🚀 3 Adımda Hızlı Başlatma

### 1. Backend Servisini Başlatın (Python 3.11+):
```bash
cd kid-arduino-studio/backend
pip install -r requirements.txt
python main.py
```
*(Backend `http://localhost:8000` adresinde çalışacaktır.)*

### 2. Frontend Arayüzünü Başlatın (Node.js 18+):
```bash
cd kid-arduino-studio/frontend
npm install
npm run dev
```
*(Arayüz `http://localhost:5173` adresinde açılacaktır.)*

### 3. Tarayıcınızda Açın:
Tarayıcınızdan **`http://localhost:5173`** adresine gidin.

> 💡 **Not:** API anahtarı veya Ollama bağlantısı olmasa bile sistem içerisinde 2 adet tam teşekküllü **Demo Proje** ("Akıllı Gece Lambası" ve "Park Sensörü") ve canlı simülatör mevcuttur!

---

## 🧠 Yapay Zeka Seçenekleri (Yerel ve Bulut)

KidArduino Studio, **LiteLLM** entegrasyonu sayesinde hem tamamen çevrimdışı (offline) hem de bulut modelleriyle çalışır:

### A. Yerel Model ile İnternetsiz Çalışma (Ollama):
1. Bilgisayarınızda [Ollama](https://ollama.ai)'yı kurun ve çalıştırın:
   ```bash
   ollama run qwen2.5-coder:1.5b
   # veya
   ollama run qwen2.5-coder:7b
   ```
2. Arayüzde sağ üstteki **Ayarlar (⚙️)** butonuna tıklayın. Sistem `http://127.0.0.1:11434` üzerindeki kurulu yerel modellerinizi otomatik algılayacaktır.

### B. Bulut Modelleri ile Çalışma (Gemini, OpenAI, Claude):
- Ayarlar penceresinden **Google Gemini (2.0 Flash / 1.5 Flash)**, **OpenAI (GPT-4o / GPT-4o Mini)** veya **Anthropic Claude (3.5 Haiku / Sonnet)** seçip API anahtarınızı girebilirsiniz. Anahtarınız tarayıcınızda yerel olarak saklanır.
- Alternatif olarak `backend/.env` dosyasına anahtarınızı kaydedebilirsiniz:
  ```env
  GEMINI_API_KEY=AIzaSy...
  OPENAI_API_KEY=sk-...
  ANTHROPIC_API_KEY=sk-ant-...
  ```

---

## ⚡ 4 Adımlı Mucit Serüveni

1. **💭 1. Hayal Et (Page1HayalEt):** Akıllı robot arkadaşına hayalindeki projeyi yaz veya mikrofona söyle. İlham verici fikir kartlarıyla tek tıkla fikir edin.
2. **🔌 2. Devreyi Kur (Page2DevreyiKur):** 30 sütunluk standart Breadboard ve kristal netliğinde Arduino Uno. Adım adım sadece aktif kablo ve hedef delikler parıldar, "Buraya Tak" ve "Tıkla" balonları yolu gösterir.
3. **🧠 3. Nasıl Çalışacak? (Page3NasilCalisacak):** Karmaşık bloklar yok! Sol tarafta sensörü gündüz/gece kaydır, ortada pelerinli robot beynin karar verişini gör, sağda ise lambanın anlık olarak yanışını canlı izle!
4. **🚀 4. Çalıştır (Page4Calistir):** Tek tıkla Arduino Uno'ya yükle! Yükleme bitince patlayan konfetilerle kutla, alttaki dairesel güneş/ay göstergesiyle Arduino'dan gelen canlı sensör verilerini takip et!

---

## 🛠️ Breadboard Fizik Kuralları & Doğrulayıcı

Sistem, yapay zekanın hayal ürünü kısa devreler yapmasını engellemek için arka planda çalışan **deterministik bir Python doğrulayıcısına** (`validate_breadboard_steps`) sahiptir:
- **Dikey İletkenlik:** A-B-C-D-E delikleri dikey olarak birbirine bağlıdır. Bir bileşenin iki bacağı asla aynı sütuna takılamaz.
- **Hazır Bölge Slotları:**
  - **Sol Bölge (Sütun 1–8):** LED'ler ve Dirençler
  - **Orta Bölge (Sütun 10–18):** Buton ve Sensörler (LDR, HC-SR04)
  - **Sağ Bölge (Sütun 20–28):** Buzzer ve Motorlar

---

## 📁 Proje Dizin Yapısı

```text
kid-arduino-studio/
├── backend/
│   ├── main.py              # FastAPI endpoints (/api/generate-project, /api/models, /api/upload, /api/ports, /api/serial-events)
│   ├── ai_service.py        # LiteLLM tabanlı multi-provider (Ollama, Gemini, OpenAI, Claude) JSON üretici
│   ├── schemas.py           # Ortak Pydantic v2 veri modelleri (ProjeTasarimi, BaglantiAdimi, AkisAdimi)
│   ├── arduino_service.py   # arduino-cli port algılama, derleme, yükleme ve self-healing döngüsü
│   ├── requirements.txt
│   └── .env.example         # GEMINI_API_KEY, OPENAI_API_KEY, ANTHROPIC_API_KEY, OLLAMA_API_BASE
├── frontend/
│   ├── src/
│   │   ├── components/
│   │   │   ├── TopNavigation.vue       # Logo, 1-2-3-4 Adım sekmeleri, Malzeme Çantam ve Ayarlar butonları
│   │   │   ├── InventoryDrawer.vue     # Açılır 'Malzeme Çantam' çekmecesi
│   │   │   ├── AISettingsModal.vue     # 'Ayarlar' / AI Model Seçici (Ollama, Gemini, OpenAI, Claude)
│   │   │   ├── Page1HayalEt.vue        # Fikir alma, robot asistan sohbeti ve 'Devreyi Tasarla' tetiği
│   │   │   ├── Page2DevreyiKur.vue     # SVG Arduino + 30 Sütunlu Breadboard, adım adım parlayan pinler
│   │   │   ├── Page3NasilCalisacak.vue # Sebep -> Sonuç akışı ve canlı interaktif simülatör
│   │   │   ├── Page4Calistir.vue       # Karta yükleme, başarı/konfeti animasyonları, canlı dairesel sensör ibresi
│   │   │   └── CodePeekModal.vue       # Meraklı çocuklar için '</> Perde Arkasındaki Kodu Gör' penceresi
│   │   ├── constants/
│   │   │   └── pinCoordinates.ts       # 30 sütun Breadboard ve Arduino Uno pin koordinat haritası
│   │   ├── types/
│   │   │   └── project.ts              # Backend JSON şeması ile birebir uyumlu TypeScript arayüzleri
│   │   └── App.vue
│   └── package.json
└── README.md
```

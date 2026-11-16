# 🤖 KidArduino Studio (MVP)
### Çocuklar İçin AI Destekli Görsel Arduino Stüdyosu

8-14 yaş arası çocuklar için tasarlanmış; geleneksel C++ kodlama ve karmaşık devre şemaları yerine **doğal dil ile proje üretmeye, adım adım görsel devre kurmaya ve algoritmik düşünmeye** odaklanan web tabanlı bir Arduino IDE prototipidir.

Çocuk ne yapmak istediğini Türkçe yazar (*"Odam kararınca gece lambam yansın, biri yaklaşınca buzzer ötsün"*). Yapay zeka; çocuğun elindeki parçalara göre devreyi tasarlar, adım adım kabloları nereye takacağını interaktif ve animasyonlu bir SVG şema üzerinde gösterir, kodun mantığını Türkçe düşünme kartlarıyla açıklar ve tek tıkla USB üzerinden Arduino Uno'ya yükler.

---

## 🚀 3 Komutta Hızlı Başlatma

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

### 3. Tarayıcınızda Açın ve Eğlenin:
Tarayıcınızdan **`http://localhost:5173`** adresine gidin.
> 💡 **Not:** Herhangi bir API anahtarı girmeseniz dahi sistem içerisinde 2 adet zengin **Demo Proje** ("Akıllı Gece Lambası" ve "Park Sensörü") ve tam çalışan simülasyon modu mevcuttur!

---

## 🛠️ Arduino CLI Yapılandırması (Karta Tek Tıkla Yükleme İçin)

Gerçek bir Arduino Uno kartına USB üzerinden kod yüklemek için `arduino-cli` aracının kurulu olması önerilir. *(Kurulu değilse sistem otomatik olarak sanal simülasyon modunda doğrular).*

### Windows Kurulumu:
1. `arduino-cli` en son sürümünü [resmi GitHub sayfasından](https://github.com/arduino/arduino-cli/releases) indirin veya komut satırından kurun:
   ```powershell
   winget install Arduino.ArduinoCLI
   # veya scoop ile:
   scoop install arduino-cli
   ```
2. Arduino AVR çekirdeğini yükleyin:
   ```powershell
   arduino-cli core update-index
   arduino-cli core install arduino:avr
   ```
3. Bağlı kartları test edin:
   ```powershell
   arduino-cli board list
   ```

---

## 📁 Proje Dizin Yapısı

```text
kid-arduino-studio/
├── backend/
│   ├── main.py              # FastAPI endpoints (/api/generate-project, /api/upload, /api/ports, /api/serial-stream)
│   ├── ai_service.py        # LLM sistem promptu, Pydantic JSON şema ve Self-Healing mekanizması
│   ├── arduino_service.py   # arduino-cli port algılama, geçici dizinde derleme ve karta yükleme
│   ├── requirements.txt
│   └── .env.example         # GEMINI_API_KEY, OPENAI_API_KEY, LLM_MODEL
├── frontend/
│   ├── src/
│   │   ├── components/
│   │   │   ├── InventorySelector.vue  # Çocuğun elindeki parçaları seçtiği renkli çekmece
│   │   │   ├── PromptInput.vue        # Hayalindeki projeyi yazdığı sohbet kutusu ve hazır fikir hapları
│   │   │   ├── CircuitViewer.vue      # Adım adım ilerleyen, pinleri parlatan Bezier kablo SVG motoru
│   │   │   ├── LogicCards.vue         # C++ kodu yerine "EĞER / SÜREKLİ / YAP" Türkçe mantık kartları
│   │   │   └── CodePeekModal.vue      # Meraklı çocuklar için "Perde Arkasındaki Gerçek Kod" penceresi
│   │   ├── constants/
│   │   │   └── pinCoordinates.ts      # Arduino Uno ve tüm sensörlerin (x, y) pin koordinat haritası
│   │   ├── types/
│   │   │   └── project.ts             # Backend JSON şeması ile birebir uyumlu TypeScript arayüzleri
│   │   ├── App.vue                    # Ana uygulama ve üst kontrol barı
│   │   └── main.ts
│   ├── package.json
│   ├── tailwind.config.js
│   └── vite.config.ts
└── README.md
```

---

## 🌟 Öne Çıkan Özellikler

- **🔌 İnteraktif SVG Devre Motoru:** Çocuğun kafasını karıştırmamak için kablolar adım adım gösterilir. Aktif kablo parlak renk ve akan akım animasyonu (`stroke-dasharray`) ile canlandırılır, kaynak ve hedef pinlerde radar puls halkaları yanıp söner.
- **🧠 Algoritmik Düşünme Kartları:** C++ sentaksı yerine `BASLANGIC (Hazırlık Yap)`, `DONGU (Sürekli Kontrol Et)`, `EGER (Karar Verme Anı)` ve `YAP (Harekete Geç)` blokları ile programlamanın mantığı öğretilir.
- **🧙‍♂️ Self-Healing (Otomatik Kod İyileştirme):** `arduino-cli` derleme hatası verirse, backend hatayı yakalayıp yapay zekaya göndererek kodu arka planda otomatik onarır.
- **🎉 Tek Tıkla Yükleme & Konfeti:** Yeşil "Devreyi Kurdum, Çalıştır! 🚀" butonu ile USB portu otomatik bulunur, derlenir ve yükleme bitince ekranda konfeti patlatılır.
- **📡 Canlı Arduino Gözlemcisi:** SSE (Server-Sent Events) üzerinden Arduino'dan gelen seri mesajları web ekranında canlı bir bilgi şeridi olarak gösterir.

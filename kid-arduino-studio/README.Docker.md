# Kid Arduino Studio - Docker Kılavuzu 🐳

Bu proje; **Ollama (Yerel LLM)**, **FastAPI Backend** ve **Vite + Vue 3 Frontend** (Nginx ile) servislerini tek bir komutla ayağa kaldıracak şekilde Dockerize edilmiştir.

> ⚠️ Docker ile çalışırken yerelde ayrıca `npm run dev` / `uvicorn` çalıştırmayın. Hepsi 5173 ve 8001 portlarını kullanır; tarayıcı hangisine bağlanırsa onun kodunu görürsünüz ve hangi sürümü test ettiğiniz karışır.

---

## 🚀 Hızlı Başlangıç

### 0. İlk çalıştırmadan önce (tek seferlik)
Backend, kayıtlı projeleri ve AI loglarını bilgisayarınızdaki iki dosyaya yazar (bind mount). Bu dosyalar git'te yoktur; **yoksa Docker onların yerine klasör oluşturur ve projeler kaydedilemez.** `kid-arduino-studio` klasöründe bir kez oluşturun:

```bash
# Linux / macOS / Git Bash
echo '[]' > backend/saved_projects.json
echo '[]' > backend/ai_logs.json
```
```powershell
# Windows PowerShell
Set-Content -Path backend/saved_projects.json -Value '[]' -Encoding ascii
Set-Content -Path backend/ai_logs.json -Value '[]' -Encoding ascii
```

Bulut modeli kullanacaksanız API anahtarınızı `backend/.env` dosyasına yazın (şablon: `backend/.env.example`, aşağıya bakın).

### 1. Servisleri Başlatma
Proje dizininde (`kid-arduino-studio`) aşağıdaki komutu çalıştırarak tüm servisleri (Ollama dahil) arka planda derleyip başlatabilirsiniz:

```bash
docker compose up -d --build
```

Konteyner ilk kez ayağa kalkarken `kid-arduino-ollama` servisi varsayılan yerel modeli (`qwen2.5:1.5b`) otomatik olarak kontrol eder ve indirir.

### 2. Uygulamaya Erişme
Konteynerler ayağa kalktığında tarayıcınızdan aşağıdaki adreslerden birine gidebilirsiniz:

- **Frontend (Kullanıcı Arayüzü):** [http://localhost:5173](http://localhost:5173)
- **Backend API Docs (Swagger):** [http://localhost:8001/docs](http://localhost:8001/docs)
- **API Health Check:** [http://localhost:8001/api/health](http://localhost:8001/api/health)
- **Ollama API:** [http://localhost:11434/api/tags](http://localhost:11434/api/tags)

### 3. Kod değiştikten sonra
Kod imajın içine kopyalandığı için değişiklikler kendiliğinden yansımaz. İmajları yeniden derleyip konteynerleri yeniden oluşturun, ardından tarayıcıda **Ctrl+F5** yapın (Nginx eski `index.html`'i önbellekten verebilir):

```bash
docker compose up -d --build --force-recreate backend frontend
```

---

## 🛠️ Mimari & Konteyner Yapısı

| Konteyner Adı | Servis | İç Port | Dış Port | Açıklama |
|---|---|---|---|---|
| `kid-arduino-ollama` | Ollama (Official) | 11434 | 11434 | Konteyner içi yerel LLM servisi (varsayılan model otomatik yüklenir) |
| `kid-arduino-backend` | FastAPI (Python 3.11) + arduino-cli | 8001 | 8001 | Devre ve Arduino kodu üretimi, doğrulama, derleme ve API |
| `kid-arduino-frontend` | Nginx (Alpine) + Vue 3 | 80 | 5173 | Derlenmiş SPA arayüzü ve API ters vekili (reverse proxy) |

> 🔌 **Karta yükleme:** Backend konteynerinde arduino-cli kurulu olduğu için kod derlenir, ancak bu yapılandırmada konteyner bilgisayarın USB/COM portlarını görmez (yükleme `NO_PORT` döner). Gerçek bir Arduino'ya yüklemek için backend'i yerelde çalıştırın (bkz. [README.md](README.md), Seçenek B).

---

## ⚙️ Çevre Değişkenleri & Konfigürasyon

- **Bulut LLM Anahtarları (Gemini, OpenAI, Anthropic):**
  `backend/.env` içine `GEMINI_API_KEY=...` (veya `OPENAI_API_KEY`, `ANTHROPIC_API_KEY`) ekleyin; backend konteyneri bu dosyayı otomatik okur. Dosya `.gitignore`'dadır, GitHub'a gitmez. Anahtarı arayüzdeki **🤖 AI Modeli** penceresine de girebilirsiniz (yalnızca o tarayıcıda saklanır).
- **Ollama Modeli:**
  Konteynerin indireceği model `docker-compose.yml` içindeki `ollama` servisinde `OLLAMA_MODEL=qwen2.5:1.5b` olarak tanımlıdır. Değiştirmek için bu satırı düzenleyin (`backend/.env` içindeki bir `OLLAMA_MODEL` değeri Ollama konteynerine **ulaşmaz**).
- **Ollama Adresi:**
  Backend'e compose tarafından `OLLAMA_API_BASE=http://ollama:11434` verilir; `backend/.env` içindeki değer Docker'da bunu ezmez.
- **Host Port Çakışması Notu:**
  Eğer host makinenizde Snap üzerinden çalışan bir Ollama servisi varsa, Docker'ın 11434 portunu dinlemesi için Snap servisini durdurabilirsiniz:
  ```bash
  sudo snap stop --disable ollama
  ```
  Veya Docker tarafındaki portu değiştirmek için `kid-arduino-studio/.env` dosyasına (compose dosyasının yanındaki `.env`, `backend/.env` değil) `OLLAMA_PORT=11435` yazabilirsiniz.

---

## 💾 Kalıcı Veri (Volumes)

Aşağıdaki veriler kalıcıdır; konteynerleri yeniden başlatsanız dahi silinmez:
- `ollama_models`: İndirilen Ollama modelleri kalıcı Docker volume'unda saklanır, her başlatmada tekrar indirilmez.
- `backend/saved_projects.json`: Kaydedilen projeler arşivi (bilgisayarınızdaki dosya).
- `backend/ai_logs.json`: Admin AI sorgu ve yanıt logları (bilgisayarınızdaki dosya).

---

## 🛑 Konteynerleri Yönetme

```bash
# Canlı logları izleme:
docker compose logs -f

# Yalnızca Ollama loglarını izleme:
docker compose logs -f ollama

# Yalnızca Backend loglarını izleme:
docker compose logs -f backend

# Servisleri durdurma (konteynerler silinmez, 'docker compose start' ile geri açılır):
docker compose stop

# Servisleri durdurup konteynerleri kaldırma (modeller volume'da kalır):
docker compose down

# Servisleri ve volume'ları (modeller dahil) tamamen temizleyerek durdurma:
docker compose down -v
```

---

## 🩹 Sorun Giderme

- **Ollama konteyneri sürekli yeniden başlıyor ve logda `syntax error near unexpected token $'{\r'` görünüyor (Windows):** `ollama/entrypoint.sh` Windows satır sonuyla (CRLF) çıkarılmış. Depodaki `.gitattributes` bunu yeni klonlarda engeller; eski bir klonda dosyayı silip yeniden çıkarın ve imajı yeniden derleyin:
  ```bash
  rm ollama/entrypoint.sh
  git checkout -- ollama/entrypoint.sh
  docker compose up -d --build ollama
  ```
- **Proje üretimi "API anahtarı girilmemiş" diyor:** `backend/.env` dosyasında ilgili anahtar var mı kontrol edin ve backend konteynerini yeniden oluşturun.
- **Bulut modeli "503 / high demand" hatası veriyor:** Sağlayıcı tarafındaki geçici yoğunluktur; biraz sonra deneyin ya da başka bir model seçin.

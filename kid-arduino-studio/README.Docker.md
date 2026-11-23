# Kid Arduino Studio - Docker Kılavuzu 🐳

Bu proje, hem **FastAPI Backend** hem de **Vite + Vue 3 Frontend** (Nginx ile) servislerini tek bir komutla ayağa kaldıracak şekilde Dockerize edilmiştir. Yerel yapay zeka (Ollama) Docker'ın içinde değil, **bilgisayarınızda** çalışır; bulut modelleri (Gemini, OpenAI, Claude) için Ollama gerekmez.

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
Proje ana dizininde (`kid-arduino-studio`) aşağıdaki komutu çalıştırarak servisleri arka planda derleyip başlatabilirsiniz:

```bash
docker compose up -d --build
```

### 2. Uygulamaya Erişme
Konteynerler ayağa kalktığında tarayıcınızdan aşağıdaki adreslerden birine gidebilirsiniz:

- **Frontend (Kullanıcı Arayüzü):** [http://localhost:5173](http://localhost:5173)
- **Backend API Docs (Swagger):** [http://localhost:8001/docs](http://localhost:8001/docs)
- **API Health Check:** [http://localhost:8001/api/health](http://localhost:8001/api/health)

### 3. Kod değiştikten sonra
Kod imajın içine kopyalandığı için değişiklikler kendiliğinden yansımaz. İmajları yeniden derleyip konteynerleri yeniden oluşturun, ardından tarayıcıda **Ctrl+F5** yapın (Nginx eski `index.html`'i önbellekten verebilir):

```bash
docker compose up -d --build --force-recreate backend frontend
```

---

## 🛠️ Mimari & Konteyner Yapısı

| Konteyner Adı | Servis | İç Port | Dış Port | Açıklama |
|---|---|---|---|---|
| `kid-arduino-backend` | FastAPI (Python 3.11) + arduino-cli | 8001 | 8001 | Arduino kod oluşturma, LLM entegrasyonu, doğrulama, derleme ve veri yönetimi |
| `kid-arduino-frontend` | Nginx (Alpine) + Vue 3 | 80 | 5173 | Derlenmiş SPA arayüzü ve `/api/` isteklerini backend'e ileten ters vekil (reverse proxy) |

> 🔌 **Karta yükleme:** Backend konteynerinde arduino-cli kurulu olduğu için kod derlenir, ancak bu yapılandırmada konteyner bilgisayarın USB/COM portlarını görmez (yükleme `NO_PORT` döner). Gerçek bir Arduino'ya yüklemek için backend'i yerelde çalıştırın (bkz. [README.md](README.md), Seçenek B).

---

## ⚙️ Çevre Değişkenleri & Konfigürasyon

Backend için `.env` dosyası kullanmak isterseniz `backend/.env` dosyasını düzenleyebilirsiniz (şablon: `backend/.env.example`). Backend konteyneri bu dosyayı otomatik okur.

- **Yerel Ollama Bağlantısı:**
  Backend konteyneri, bilgisayarınızda (host) çalışan Ollama servisine otomatik olarak `http://host.docker.internal:11434` adresi üzerinden erişir. Bilgisayarınızda Ollama çalışıyorsa herhangi bir ek ayar yapmanız gerekmez. Bu adres `docker-compose.yml` içinde verildiği için `backend/.env` içindeki `OLLAMA_API_BASE` değeri Docker'da etkisizdir.
- **Bulut LLM Anahtarları (Gemini, OpenAI, Anthropic):**
  `backend/.env` içine `GEMINI_API_KEY=...` (veya `OPENAI_API_KEY`, `ANTHROPIC_API_KEY`) ekleyin. Dosya `.gitignore`'dadır, GitHub'a gitmez; **gerçek anahtarları `.env.example`'a veya koda yazmayın.** Anahtarı arayüzdeki **🤖 AI Modeli** penceresine de girebilirsiniz (yalnızca o tarayıcıda saklanır).

---

## 💾 Kalıcı Veri (Volumes)

Aşağıdaki dosyalar host makine ile paylaşılır; konteynerleri yeniden başlatsanız dahi verileriniz kaybolmaz:
- `backend/saved_projects.json` (Kaydedilen projeler arşivi)
- `backend/ai_logs.json` (Admin AI sorgu ve yanıt logları)

---

## 🛑 Konteynerleri Yönetme

```bash
# Canlı logları izleme:
docker compose logs -f

# Yalnızca backend loglarını izleme:
docker compose logs -f backend

# Servisleri durdurma (konteynerler silinmez, 'docker compose start' ile geri açılır):
docker compose stop

# Servisleri durdurup konteynerleri kaldırma:
docker compose down

# Servisleri ve volume'ları tamamen temizleyerek durdurma:
docker compose down -v
```

---

## 🩹 Sorun Giderme

- **Ollama modelleri listede görünmüyor:** Bilgisayarınızda Ollama'nın çalıştığını ve en az bir model indirildiğini kontrol edin (`ollama list`). Linux'ta Ollama varsayılan olarak yalnızca `127.0.0.1`'i dinler; konteynerin erişebilmesi için Ollama'yı `OLLAMA_HOST=0.0.0.0` ile başlatmanız gerekebilir.
- **Proje üretimi "API anahtarı girilmemiş" diyor:** `backend/.env` dosyasında ilgili anahtar var mı kontrol edin ve backend konteynerini yeniden oluşturun.
- **Bulut modeli "503 / high demand" hatası veriyor:** Sağlayıcı tarafındaki geçici yoğunluktur; biraz sonra deneyin ya da başka bir model seçin.

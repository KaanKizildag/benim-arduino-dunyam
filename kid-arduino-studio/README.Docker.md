# Kid Arduino Studio - Docker Kılavuzu 🐳

Bu proje; **Ollama (Yerel LLM)**, **FastAPI Backend** ve **Vite + Vue 3 Frontend** (Nginx ile) servislerini tek bir komutla ayağa kaldıracak şekilde Dockerize edilmiştir.

---

## 🚀 Hızlı Başlangıç

### 1. Servisleri Başlatma
Proje ana dizininde (`kid-arduino-studio`) aşağıdaki komutu çalıştırarak tüm servisleri (Ollama dahil) arka planda derleyip başlatabilirsiniz:

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

---

## 🛠️ Mimari & Konteyner Yapısı

| Konteyner Adı | Servis | İç Port | Dış Port | Açıklama |
|---|---|---|---|---|
| `kid-arduino-ollama` | Ollama (Official) | 11434 | 11434 | Konteyner içi yerel LLM servisi (varsayılan model otomatik yüklenir) |
| `kid-arduino-backend` | FastAPI (Python 3.11) | 8001 | 8001 | Devre yerleşimi, Arduino kod oluşturma, LLM entegrasyonu ve API |
| `kid-arduino-frontend` | Nginx (Alpine) + Vue 3 | 80 | 5173 | Derlenmiş SPA arayüzü ve API ters vekili (reverse proxy) |

---

## ⚙️ Çevre Değişkenleri & Konfigürasyon

Backend ve Ollama için ayarları özelleştirmek isterseniz `backend/.env` dosyası oluşturabilirsiniz:

- **Ollama Modeli:**
  Konteyner ayağa kalktığında otomatik indirilecek modeli `OLLAMA_MODEL` ile değiştirebilirsiniz (Varsayılan: `qwen2.5:1.5b`).
  Örnek: `OLLAMA_MODEL=qwen2.5-coder:1.5b`
- **Host Port Çakışması Notu:**
  Eğer host makinenizde Snap üzerinden çalışan bir Ollama servisi varsa, Docker'ın 11434 portunu dinlemesi için Snap servisini durdurabilirsiniz:
  ```bash
  sudo snap stop --disable ollama
  ```
  Veya Docker portunu değiştirmek için `.env` içinde `OLLAMA_PORT=11435` belirtebilirsiniz.
- **Bulut LLM Anahtarları (Gemini, OpenAI, Anthropic):**
  İsterseniz `backend/.env` içine `GEMINI_API_KEY=...` ekleyebilir ya da doğrudan arayüzdeki model seçim modalından girebilirsiniz.

---

## 💾 Kalıcı Veri (Volumes)

Aşağıdaki veriler kalıcıdır; konteynerleri yeniden başlatsanız dahi silinmez:
- `ollama_models`: İndirilen Ollama modelleri kalıcı Docker volume'unda saklanır, her başlatmada tekrar indirilmez.
- `backend/saved_projects.json`: Kaydedilen projeler arşivi.
- `backend/ai_logs.json`: Admin AI sorgu ve yanıt logları.

---

## 🛑 Konteynerleri Yönetme

```bash
# Canlı logları izleme:
docker compose logs -f

# Yalnızca Ollama loglarını izleme:
docker compose logs -f ollama

# Yalnızca Backend loglarını izleme:
docker compose logs -f backend

# Servisleri durdurma:
docker compose down

# Servisleri ve volume'ları (modeller dahil) tamamen temizleyerek durdurma:
docker compose down -v
```

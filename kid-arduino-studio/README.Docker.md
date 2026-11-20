# Kid Arduino Studio - Docker Kılavuzu 🐳

Bu proje, hem **FastAPI Backend** hem de **Vite + Vue 3 Frontend** (Nginx ile) servislerini tek bir komutla ayağa kaldıracak şekilde Dockerize edilmiştir.

---

## 🚀 Hızlı Başlangıç

### 1. Servisleri Başlatma
Proje ana dizininde aşağıdaki komutu çalıştırarak servisleri arka planda derleyip başlatabilirsiniz:

```bash
docker compose up -d --build
```

### 2. Uygulamaya Erişme
Konteynerler ayağa kalktığında tarayıcınızdan aşağıdaki adreslerden birine gidebilirsiniz:

- **Frontend (Kullanıcı Arayüzü):** [http://localhost:5173](http://localhost:5173)
- **Backend API Docs (Swagger):** [http://localhost:8001/docs](http://localhost:8001/docs)
- **API Health Check:** [http://localhost:8001/api/health](http://localhost:8001/api/health)

---

## 🛠️ Mimari & Konteyner Yapısı

| Konteyner Adı | Servis | İç Port | Dış Port | Açıklama |
|---|---|---|---|---|
| `kid-arduino-backend` | FastAPI (Python 3.11) | 8001 | 8001 | Arduino kod oluşturma, LLM entegrasyonu, Arduino CLI ve veri yönetimi |
| `kid-arduino-frontend` | Nginx (Alpine) + Vue 3 | 80 | 5173 | Derlenmiş SPA arayüzü ve `/api/` isteklerini backend'e ileten ters vekil (reverse proxy) |

---

## ⚙️ Çevre Değişkenleri & Konfigürasyon

Backend için `.env` dosyası kullanmak isterseniz `backend/.env` dosyasını düzenleyebilirsiniz.

- **Yerel Ollama Bağlantısı:**
  Backend konteyneri, host makinenizde çalışan Ollama servisine otomatik olarak `http://host.docker.internal:11434` adresi üzerinden erişir.
- **Bulut LLM Anahtarları (Gemini, OpenAI, Anthropic):**
  İsterseniz `backend/.env` içine `GEMINI_API_KEY=...` ekleyebilir ya da doğrudan arayüzdeki model seçim modalından girebilirsiniz.

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

# Servisleri durdurma:
docker compose down

# Servisleri ve volume'ları tamamen temizleyerek durdurma:
docker compose down -v
```

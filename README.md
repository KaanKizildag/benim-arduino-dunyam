# 🤖 KidArduino Studio (MVP)
### Çocuklar İçin AI Destekli Görsel Arduino Stüdyosu

Proje kaynak kodları `kid-arduino-studio/` klasöründedir.

Detaylı mimari, kurulum ve kullanım yönergeleri için [kid-arduino-studio/README.md](kid-arduino-studio/README.md), Docker ile ayağa kaldırmak için [kid-arduino-studio/README.Docker.md](kid-arduino-studio/README.Docker.md) dosyalarını inceleyebilirsiniz.

---

## 🚀 Hızlı Başlatma

### Seçenek A: Yerelde Geliştirme (Önerilen)

```bash
# 1. Backend (Terminal 1)
cd kid-arduino-studio/backend
python -m venv .venv
.\.venv\Scripts\Activate.ps1    # Linux/macOS: source .venv/bin/activate
pip install -r requirements.txt
copy .env.example .env          # Linux/macOS: cp .env.example .env
python -m uvicorn main:app --port 8001 --reload

# 2. Frontend (Terminal 2)
cd kid-arduino-studio/frontend
npm install
npm run dev
```

Tarayıcınızda açın: **`http://localhost:5173`**

### Seçenek B: Docker ile Çalıştırma

```bash
cd kid-arduino-studio
docker compose up -d --build
```

> ⚠️ Docker ve yerel geliştirme modunu aynı anda çalıştırmayın; ikisi de 5173 ve 8001 portlarını kullanır.

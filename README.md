# 🤖 KidArduino Studio (MVP)
### Çocuklar İçin AI Destekli Görsel Arduino Stüdyosu

Proje dosyaları `kid-arduino-studio/` klasöründedir.

Detaylı dokümantasyon, kurulum ve kullanım yönergeleri için [kid-arduino-studio/README.md](kid-arduino-studio/README.md), Docker ile çalıştırmak için [kid-arduino-studio/README.Docker.md](kid-arduino-studio/README.Docker.md) dosyalarını inceleyin.

## 🚀 Hızlı Başlatma

### Seçenek A: Docker ile (önerilen)
```bash
cd kid-arduino-studio
docker compose up -d --build
```
İlk çalıştırmadan önce yapılması gereken küçük hazırlık için [README.Docker.md](kid-arduino-studio/README.Docker.md) dosyasına bakın.

### Seçenek B: Yerelde geliştirme modu
```bash
# 1. Backend (port 8001):
cd kid-arduino-studio/backend
pip install -r requirements.txt
uvicorn main:app --host 0.0.0.0 --port 8001 --reload

# 2. Frontend (ayrı bir terminalde):
cd kid-arduino-studio/frontend
npm install
npm run dev
```

Tarayıcınızda: `http://localhost:5173`

> ⚠️ Docker ve yerel geliştirme modunu aynı anda çalıştırmayın; ikisi de 5173 ve 8001 portlarını kullanır ve tarayıcının hangisine bağlandığı karışır.

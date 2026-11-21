#!/bin/bash
set -e

# Ollama arka planda başlatılıyor
echo "🚀 Ollama sunucusu başlatılıyor..."
ollama serve &
SERVER_PID=$!

# Sinyalleri yakala (zarif kapanış)
cleanup() {
    echo "🛑 Ollama sunucusu durduruluyor..."
    kill -TERM "$SERVER_PID" 2>/dev/null || true
    wait "$SERVER_PID"
    exit 0
}
trap cleanup SIGTERM SIGINT

# API servisinin yanıt vermesini bekle
echo "⏳ Ollama servisinin ayağa kalkması bekleniyor..."
for i in {1..30}; do
    if ollama list >/dev/null 2>&1; then
        echo "✅ Ollama servisi hazır!"
        break
    fi
    sleep 1
done

# Hedef modelin varlığını kontrol et ve gerekiyorsa indir
TARGET_MODEL="${OLLAMA_MODEL:-qwen2.5:1.5b}"
echo "🔍 Model kontrol ediliyor: $TARGET_MODEL"

if ollama list | grep -q "$TARGET_MODEL"; then
    echo "⚡ Model '$TARGET_MODEL' zaten mevcut ve hazır."
else
    echo "📥 Model '$TARGET_MODEL' bulunamadı, otomatik indiriliyor..."
    ollama pull "$TARGET_MODEL" || echo "⚠️ Model indirme sırasında hata veya uyarı oluştu."
    echo "✅ Model '$TARGET_MODEL' başarıyla hazırlandı!"
fi

# Ollama sunucusunun çalışmaya devam etmesini sağla
wait "$SERVER_PID"

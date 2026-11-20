FROM python:3.11-slim

# Sistem bağımlılıklarını ve arduino-cli gereksinimlerini yükle
RUN apt-get update && apt-get install -y --no-install-recommends \
    curl \
    ca-certificates \
    && rm -rf /var/lib/apt/lists/*

# Arduino CLI kur (Arduino C++ kodlarını derlemek için)
RUN curl -fsSL https://raw.githubusercontent.com/arduino/arduino-cli/master/install.sh | BINDIR=/usr/local/bin sh \
    && (arduino-cli config init || true) \
    && (arduino-cli core update-index || true) \
    && (arduino-cli core install arduino:avr || true)

WORKDIR /app

# Python bağımlılıklarını kopyala ve yükle
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Uygulama kodlarını kopyala
COPY . .

# Backend portu
EXPOSE 8001

CMD ["uvicorn", "main:app", "--host", "0.0.0.0", "--port", "8001"]

FROM ollama/ollama:latest

# Başlatma ve model sağlama betiği
COPY entrypoint.sh /entrypoint.sh
RUN chmod +x /entrypoint.sh

EXPOSE 11434

ENTRYPOINT ["/bin/bash", "/entrypoint.sh"]

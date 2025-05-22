# Используем официальный образ Ollama
FROM ollama/ollama:latest

# Открываем порт по умолчанию
EXPOSE 11434

# Команда для запуска сервера Ollama
CMD ["ollama", "serve"]

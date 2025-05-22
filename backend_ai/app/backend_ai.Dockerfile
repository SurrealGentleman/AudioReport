# Используем официальный образ Python
FROM python:3.11

# Устанавливаем рабочую директорию внутри контейнера
WORKDIR /app

# Копируем requirements в рабочую директорию
COPY requirements.txt .

# Устанавливаем зависимости
RUN pip install --no-cache-dir --upgrade pip \
    && pip install --no-cache-dir -r requirements.txt

# Копируем файлы проекта (исключая файлы, указанные в .dockerignore)
COPY . .

# Открываем порт для Django
EXPOSE 8800

# Запускаем сервер через Unicorn
CMD ["uvicorn", "main:app", "--host", "0.0.0.0", "--port", "8800"]

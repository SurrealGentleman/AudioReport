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

RUN python manage.py collectstatic --noinput

# Открываем порт для Django
EXPOSE 8000

# Запускаем сервер через Gunicorn
CMD ["gunicorn", "--bind", "0.0.0.0:8000", "audio_report.wsgi:application"]

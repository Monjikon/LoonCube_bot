FROM python:3.11-slim

WORKDIR /app

# Копируем файлы
COPY bot/requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

COPY bot/ .

# Создаем директорию для базы данных
RUN mkdir -p /data

# Запускаем бота
CMD ["python", "main.py"]

#!/bin/bash

# Стартовый скрипт для хостингов типа BotHost
# Автоматически устанавливает зависимости и запускает бота

echo "🚀 Запуск MCLink бота..."

# Проверка Python
if ! command -v python3 &> /dev/null; then
    echo "❌ Python 3 не найден"
    exit 1
fi

# Установка зависимостей
echo "📦 Установка зависимостей..."
pip3 install -r requirements.txt --break-system-packages 2>/dev/null || pip3 install -r requirements.txt

# Проверка .env
if [ ! -f .env ]; then
    echo "⚠️  Файл .env не найден. Используются переменные окружения из хостинга."
fi

# Запуск бота
echo "✅ Запуск бота..."
python3 main.py

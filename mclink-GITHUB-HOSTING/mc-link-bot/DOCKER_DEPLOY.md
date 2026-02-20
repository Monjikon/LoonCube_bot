# 🐳 Запуск бота через Docker

Если у тебя есть свой VPS или ты хочешь запустить бота локально в контейнере.

---

## Установка Docker

**Windows:**
- Скачай [Docker Desktop](https://www.docker.com/products/docker-desktop)
- Установи и запусти

**Linux:**
```bash
curl -fsSL https://get.docker.com -o get-docker.sh
sudo sh get-docker.sh
sudo systemctl enable docker
sudo systemctl start docker
```

---

## Запуск бота

```bash
# Перейди в папку с ботом
cd mc-link-bot

# Убедись что .env заполнен
cat bot/.env

# Запусти бота
docker-compose up -d
```

**Готово!** Бот работает в фоне.

---

## Управление

```bash
# Посмотреть логи
docker-compose logs -f

# Остановить
docker-compose down

# Перезапустить
docker-compose restart

# Обновить после изменений
docker-compose up -d --build
```

---

## Автозапуск при перезагрузке

Контейнер автоматически запустится после перезагрузки сервера благодаря `restart: unless-stopped` в docker-compose.yml

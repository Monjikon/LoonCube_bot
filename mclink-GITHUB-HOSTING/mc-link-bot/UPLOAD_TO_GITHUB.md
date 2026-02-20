# ⚡ Быстрая загрузка на GitHub

## Шаг 1 — Подготовка

1. **Скачай и установи Git:**
   - Windows: https://git-scm.com/download/win
   - Linux: `sudo apt install git`

2. **Настрой Git** (если первый раз):
```bash
git config --global user.name "Твое Имя"
git config --global user.email "твой@email.com"
```

---

## Шаг 2 — Создай репозиторий на GitHub

1. Зайди на https://github.com
2. Нажми **"+"** справа вверху → **"New repository"**
3. Заполни:
   - Repository name: `mclink-bot`
   - Description: `Привязка Minecraft к Telegram/VK`
   - ✅ Private (чтобы токены не утекли)
   - ❌ НЕ добавляй README, .gitignore, License — они уже есть
4. Нажми **"Create repository"**
5. **Скопируй URL** который появился (например: `https://github.com/username/mclink-bot.git`)

---

## Шаг 3 — Загрузи код

Открой **PowerShell** или **Git Bash** в папке `mc-link-bot`:

```bash
# Замени URL на свой!
git init
git add .
git commit -m "🎮 Initial commit: MCLink bot"
git branch -M main
git remote add origin https://github.com/ВАШ_USERNAME/mclink-bot.git
git push -u origin main
```

**Готово!** Код на GitHub ✅

---

## Шаг 4 — Деплой на хостинг

### Вариант A — Railway.app (рекомендуется)

1. Зайди на https://railway.app
2. Войди через GitHub
3. Нажми **"New Project"** → **"Deploy from GitHub repo"**
4. Выбери `mclink-bot`
5. Добавь переменные окружения:
   - `TELEGRAM_TOKEN`
   - `VK_TOKEN`
   - `VK_GROUP_ID`
   - `API_SECRET`
   - `API_PORT=8080`
6. Railway автоматически запустит бота!
7. Скопируй URL из раздела **"Settings" → "Domains"**

**Стоимость:** $5 бесплатно каждый месяц (хватит на бота)

---

### Вариант B — Google Cloud Run

```bash
# Установи Google Cloud SDK, затем:
gcloud run deploy mclink-bot \
  --source . \
  --region europe-west1 \
  --allow-unauthenticated \
  --set-env-vars TELEGRAM_TOKEN=твой_токен,VK_TOKEN=твой_токен
```

Подробнее: [GOOGLE_CLOUD_DEPLOY.md](GOOGLE_CLOUD_DEPLOY.md)

---

### Вариант C — BotHost.ru

1. Зайди на https://bothost.ru
2. Создай бота → Python
3. Подключи GitHub репозиторий
4. Укажи:
   - Корневая папка: `bot`
   - Файл запуска: `main.py`
5. Добавь переменные окружения
6. Запусти!

Подробнее: [GITHUB_BOTHOST.md](GITHUB_BOTHOST.md)

---

## Шаг 5 — Настрой Minecraft плагин

Когда бот запущен на хостинге, получи его URL и укажи в `plugins/MCLink/config.yml`:

```yaml
api:
  url: "https://твой-бот.railway.app"  # или другой URL
  secret: "mclink_secret_key_2024"
```

---

## 🔄 Обновление кода

После изменений:

```bash
git add .
git commit -m "Описание изменений"
git push
```

Хостинги с GitHub интеграцией обновятся автоматически!

---

## ✅ Проверка

1. **Telegram:** найди бота → `/start`
2. **VK:** напиши в группу → `help`
3. **Minecraft:** `/link` → получи код → отправь боту

Если всё работает — готово! 🎉

---

## 🆘 Проблемы?

- Логи на Railway: https://railway.app → твой проект → View Logs
- Логи на Google Cloud: `gcloud run logs read mclink-bot`
- GitHub Issues: создай issue в своем репозитории

---

**Удачи! 🚀**

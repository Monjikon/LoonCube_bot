# 🚀 Развертывание бота на Google Cloud Run

Google Cloud Run — это бесплатный сервис для запуска контейнеров 24/7.

---

## 📋 Что нужно

1. **Google аккаунт** (Gmail)
2. **Банковская карта** (для верификации, но не снимут деньги)
3. **10 минут времени**

---

## 🎯 Пошаговая инструкция

### Шаг 1 — Создай проект в Google Cloud

1. Перейди на [console.cloud.google.com](https://console.cloud.google.com)
2. Нажми **"Создать проект"**
3. Название: `mclink-bot` (любое)
4. Нажми **"Создать"**

---

### Шаг 2 — Активируй Cloud Run API

1. В меню слева → **APIs & Services** → **Enable APIs and Services**
2. Найди **"Cloud Run API"**
3. Нажми **"Enable"**
4. Так же включи **"Cloud Build API"**

---

### Шаг 3 — Установи Google Cloud SDK на компьютер

**Windows:**
- Скачай установщик: [cloud.google.com/sdk/docs/install](https://cloud.google.com/sdk/docs/install)
- Запусти `GoogleCloudSDKInstaller.exe`
- После установки откроется окно — следуй инструкциям для входа

**Или используй Cloud Shell прямо в браузере** (кнопка >_ справа вверху в консоли Google Cloud)

---

### Шаг 4 — Загрузи код бота

В **Cloud Shell** или в **PowerShell с gcloud** (если установил SDK):

```bash
# Войди в аккаунт (если еще не вошел)
gcloud auth login

# Выбери свой проект
gcloud config set project mclink-bot

# Перейди в папку с ботом
cd путь/к/mc-link-bot

# Убедись что .env файл существует и заполнен
cat bot/.env
```

---

### Шаг 5 — Разверни на Cloud Run

```bash
# Разверни бота (займет 2-3 минуты)
gcloud run deploy mclink-bot \
  --source . \
  --region europe-west1 \
  --allow-unauthenticated \
  --port 8080 \
  --cpu 1 \
  --memory 512Mi
```

**Важно:** При запросе региона выбери ближайший (europe-west1 для Европы)

---

### Шаг 6 — Получи публичный URL

После развертывания увидишь URL типа:
```
https://mclink-bot-xxxxx-ew.a.run.app
```

**Это адрес для плагина!** Скопируй его.

---

### Шаг 7 — Настрой плагин на сервере

В `config.yml` плагина укажи:
```yaml
api:
  url: "https://mclink-bot-xxxxx-ew.a.run.app"
  secret: "mclink_secret_key_2024"
```

---

## 💰 Бесплатные лимиты Google Cloud Run

- ✅ **2 миллиона запросов/месяц** — бесплатно
- ✅ **360,000 ГБ-секунд** памяти — бесплатно
- ✅ **180,000 vCPU-секунд** — бесплатно

**Для бота это значит:** ~700 часов работы в месяц БЕСПЛАТНО

---

## 📊 Мониторинг бота

Логи смотри в консоли:
```bash
gcloud run logs read mclink-bot --region europe-west1 --limit 50
```

Или в веб-интерфейсе: Cloud Run → твой сервис → **Logs**

---

## 🔄 Обновление бота

Если изменил код:
```bash
cd путь/к/mc-link-bot
gcloud run deploy mclink-bot --source . --region europe-west1
```

---

## ⚠️ Важные моменты

1. **База данных будет сбрасываться** при каждом обновлении. Для продакшена лучше использовать Cloud SQL или внешнюю БД.

2. **Переменные окружения** можно задать через Cloud Console:
   - Cloud Run → Сервис → Edit & Deploy New Revision
   - Variables & Secrets → добавь `TELEGRAM_TOKEN`, `VK_TOKEN` и т.д.

3. **Первый запрос** после простоя может быть медленным (cold start ~5 сек)

---

## 🆘 Если что-то не работает

Проверь логи:
```bash
gcloud run logs read mclink-bot --region europe-west1
```

Или напиши мне — помогу разобраться!

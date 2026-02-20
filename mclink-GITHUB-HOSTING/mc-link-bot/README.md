# 🎮 MCLink — Привязка Minecraft к VK и Telegram

Система для привязки аккаунтов игроков Minecraft к VK сообществу и Telegram боту.

---

## 📁 Структура проекта

```
mc-link-bot/
├── bot/                        # Python бот
│   ├── main.py                 # Точка входа
│   ├── config.py               # Конфигурация
│   ├── database.py             # SQLite база данных
│   ├── api.py                  # REST API для плагина
│   ├── telegram_bot.py         # Telegram бот
│   ├── vk_bot.py               # VK бот
│   ├── requirements.txt
│   └── .env.example
└── minecraft-plugin/           # Bukkit/Paper плагин
    ├── pom.xml
    └── src/main/
        ├── java/ru/mclink/plugin/
        │   ├── MCLinkPlugin.java
        │   ├── ApiClient.java
        │   └── commands/
        │       ├── LinkCommand.java
        │       ├── LinkStatusCommand.java
        │       └── LinkUnlinkCommand.java
        └── resources/
            ├── plugin.yml
            └── config.yml
```

---

## 🚀 Установка

> 📖 **Доступны 3 способа запуска:** Локально на ПК, Google Cloud (бесплатно 24/7), Docker

### Способ 1 — Локально на компьютере

**Требования:** Python 3.10+

```bash
cd bot
pip install -r requirements.txt
cp .env.example .env
```

Заполни `.env`:

| Параметр | Описание |
|---|---|
| `TELEGRAM_TOKEN` | Токен от [@BotFather](https://t.me/BotFather) |
| `VK_TOKEN` | Токен сообщества VK (Управление → API → Ключи доступа) |
| `VK_GROUP_ID` | ID вашего VK сообщества (число) |
| `API_SECRET` | Любой случайный секретный ключ |
| `API_PORT` | Порт API (по умолчанию 8080) |

Запуск:
```bash
python main.py
```

Или через systemd:
```ini
# /etc/systemd/system/mclink.service
[Unit]
Description=MCLink Bot
After=network.target

[Service]
WorkingDirectory=/opt/mclink/bot
ExecStart=/usr/bin/python3 main.py
Restart=always
User=mclink

[Install]
WantedBy=multi-user.target
```

```bash
systemctl enable mclink
systemctl start mclink
```

---

### Способ 2 — Google Cloud Run (рекомендуется)

✅ **Бесплатно** в пределах лимитов  
✅ **Работает 24/7** без твоего компьютера  
✅ **Автоматический публичный URL** для плагина

**Подробная инструкция:** [GOOGLE_CLOUD_DEPLOY.md](GOOGLE_CLOUD_DEPLOY.md)

**Быстрый старт:**
```bash
gcloud run deploy mclink-bot \
  --source . \
  --region europe-west1 \
  --allow-unauthenticated
```

---

### Способ 3 — Docker

Подходит для VPS или локального запуска в контейнере.

**Подробная инструкция:** [DOCKER_DEPLOY.md](DOCKER_DEPLOY.md)

**Быстрый старт:**
```bash
docker-compose up -d
```

---

### 2. Minecraft плагин

**Требования:** Paper/Spigot 1.20+, Java 17+

**Сборка через Maven:**
```bash
cd minecraft-plugin
mvn clean package
```

JAR будет в `target/mc-link-plugin-1.0.0.jar`

**Установка:**
1. Скопируй JAR в папку `plugins/` сервера
2. Запусти сервер (создастся `plugins/MCLink/config.yml`)
3. Укажи в `config.yml`:
   - `api.url` — адрес Python бота (напр. `http://192.168.1.10:8080`)
   - `api.secret` — тот же ключ, что в `.env`
4. `/reload` или перезапусти сервер

---

## 🔄 Процесс привязки

```
Игрок → /link в Minecraft
   ↓
Плагин запрашивает код у API
   ↓
Игрок получает: "Твой код: A3X9QK (10 минут)"
   ↓
Игрок пишет в Telegram: /link A3X9QK
  или в VK боте:          link A3X9QK
   ↓
Бот подтверждает привязку ✅
```

---

## 💬 Команды

### В Minecraft
| Команда | Описание |
|---|---|
| `/link` | Получить код привязки |
| `/linkstatus` | Проверить статус привязки |
| `/linkunlink` | Инструкция по отвязке |

### В Telegram
| Команда | Описание |
|---|---|
| `/link КОД` | Привязать аккаунт |
| `/unlink` | Отвязать аккаунт |
| `/status` | Показать привязку |

### В VK боте
| Команда | Описание |
|---|---|
| `link КОД` | Привязать аккаунт |
| `unlink` | Отвязать аккаунт |
| `status` | Показать привязку |

---

## 🔌 REST API

API работает на порту 8080 (настраивается). Используется плагином.

### `POST /api/generate_code`
Генерирует код привязки.
```json
// Запрос
{ "uuid": "550e8400-...", "nick": "Steve" }
// Ответ
{ "code": "A3X9QK", "expires_minutes": 10 }
```

### `GET /api/check_link?uuid=...`
Проверяет привязку по UUID.
```json
{ "linked": true, "platform": "telegram", "user_id": "123456", "linked_at": "2024-01-01T12:00:00" }
```

### `GET /api/get_link_by_nick?nick=...`
Проверяет привязку по нику.

> Все запросы требуют заголовок `X-API-Secret`.

---

## 🛡️ Безопасность

- API доступен только внутри сети сервера (не выставляй наружу без firewall)
- Все запросы защищены секретным ключом (`X-API-Secret`)
- Коды живут только 10 минут и удаляются после использования

---

## 📊 База данных (SQLite)

Таблица `linked_accounts`:
| Поле | Тип | Описание |
|---|---|---|
| minecraft_uuid | TEXT | UUID игрока (уникальный) |
| minecraft_nick | TEXT | Ник на момент привязки |
| platform | TEXT | `telegram` или `vk` |
| user_id | TEXT | ID пользователя в платформе |
| linked_at | TEXT | Дата и время привязки (UTC) |

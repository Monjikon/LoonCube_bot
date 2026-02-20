import os
from dotenv import load_dotenv

load_dotenv()

# Telegram
TELEGRAM_TOKEN = os.getenv("TELEGRAM_TOKEN", "")

# VK
VK_TOKEN = os.getenv("VK_TOKEN", "")          # токен сообщества
VK_GROUP_ID = int(os.getenv("VK_GROUP_ID", "0"))

# API сервер (для Minecraft плагина)
API_HOST = os.getenv("API_HOST", "0.0.0.0")
API_PORT = int(os.getenv("API_PORT", "8080"))
API_SECRET = os.getenv("API_SECRET", "change_me_secret_key")

# База данных
DATABASE_PATH = os.getenv("DATABASE_PATH", "mclink.db")

# Настройки кодов привязки
CODE_LENGTH = 6          # длина кода
CODE_EXPIRE_MINUTES = 10 # время жизни кода

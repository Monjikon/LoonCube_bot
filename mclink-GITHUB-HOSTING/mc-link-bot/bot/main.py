"""
Точка входа. Запускает все три компонента в отдельных потоках:
  • Telegram бот
  • VK бот
  • Flask API (для Minecraft плагина)
"""

import logging
import threading
import sys
import database as db

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(name)s: %(message)s",
    handlers=[
        logging.StreamHandler(sys.stdout),
        logging.FileHandler("mclink.log", encoding="utf-8"),
    ],
)
logger = logging.getLogger(__name__)


def main():
    # Инициализация базы данных
    db.init_db()
    logger.info("Database initialized")

    threads = []

    # ── API ──────────────────────────────────────────────────────────────────
    from api import run_api
    t_api = threading.Thread(target=run_api, name="API", daemon=True)
    t_api.start()
    threads.append(t_api)
    logger.info("API server started")

    # ── VK бот ──────────────────────────────────────────────────────────────
    from config import VK_TOKEN
    if VK_TOKEN:
        from vk_bot import run_vk
        t_vk = threading.Thread(target=run_vk, name="VK", daemon=True)
        t_vk.start()
        threads.append(t_vk)
        logger.info("VK bot started")
    else:
        logger.warning("VK_TOKEN not set — VK bot disabled")

    # ── Telegram бот (блокирующий, основной поток) ───────────────────────────
    from config import TELEGRAM_TOKEN
    if TELEGRAM_TOKEN:
        from telegram_bot import run_telegram
        run_telegram()  # блокирует поток
    else:
        logger.warning("TELEGRAM_TOKEN not set — Telegram bot disabled")
        # Ждём остальных
        for t in threads:
            t.join()


if __name__ == "__main__":
    main()

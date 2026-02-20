"""
VK бот (через Longpoll) для привязки Minecraft аккаунта.
Требует токен сообщества с доступом к сообщениям.
"""

import logging
import vk_api
from vk_api.longpoll import VkLongPoll, VkEventType
import database as db
from config import VK_TOKEN, VK_GROUP_ID, CODE_EXPIRE_MINUTES

logger = logging.getLogger(__name__)

HELP_TEXT = (
    "🎮 Привязка Minecraft аккаунта\n\n"
    "1️⃣ Зайди на сервер и введи команду /link\n"
    "2️⃣ Получишь код из 6 символов\n"
    "3️⃣ Отправь его сюда командой: link КОД\n\n"
    "Доступные команды:\n"
    "• link КОД — привязать аккаунт\n"
    "• unlink — отвязать аккаунт\n"
    "• status — показать привязку\n"
    "• help — это сообщение"
)


class VKBot:
    def __init__(self):
        if not VK_TOKEN:
            raise ValueError("VK_TOKEN не задан в .env")

        self.vk_session = vk_api.VkApi(token=VK_TOKEN)
        self.vk = self.vk_session.get_api()
        self.longpoll = VkLongPoll(self.vk_session, group_id=VK_GROUP_ID if VK_GROUP_ID else None)

    def send(self, user_id: int, text: str):
        import random
        self.vk.messages.send(
            user_id=user_id,
            message=text,
            random_id=random.randint(0, 2**31),
        )

    def handle_message(self, user_id: int, text: str):
        text = text.strip()
        lower = text.lower()

        try:
            if lower in ("start", "начать", "привет", "help", "помощь"):
                self.send(user_id, "👋 Привет!\n\n" + HELP_TEXT)

            elif lower.startswith("link ") or lower.startswith("линк "):
                parts = text.split(maxsplit=1)
                code = parts[1].strip().upper() if len(parts) > 1 else ""
                self._handle_link(user_id, code)

            elif lower == "unlink" or lower == "отвязать":
                self._handle_unlink(user_id)

            elif lower == "status" or lower == "статус":
                self._handle_status(user_id)

            else:
                self.send(
                    user_id,
                    "❓ Неизвестная команда\n\n"
                    "Доступные команды:\n"
                    "• help — помощь\n"
                    "• link КОД — привязать аккаунт\n"
                    "• unlink — отвязать\n"
                    "• status — проверить привязку",
                )
        except Exception as e:
            logger.error("Error handling VK message from %s: %s", user_id, e)
            self.send(user_id, "⚠️ Произошла ошибка. Попробуй позже.")

    def _handle_link(self, user_id: int, code: str):
        if not code:
            self.send(
                user_id,
                f"❓ Укажи код из игры:\n  link ABCDEF\n\n"
                f"Код действует {CODE_EXPIRE_MINUTES} минут.",
            )
            return

        existing = db.get_link_by_user("vk", str(user_id))
        if existing:
            self.send(
                user_id,
                f"⚠️ Ты уже привязан к нику {existing['minecraft_nick']}.\n"
                "Напиши unlink чтобы отвязать, затем привяжи заново.",
            )
            return

        result = db.consume_code(code)
        if result is None:
            self.send(
                user_id,
                "❌ Код неверный или истёк.\n"
                "Введи /link на сервере, чтобы получить новый.",
            )
            return

        mc_uuid, mc_nick = result
        db.link_account(mc_uuid, mc_nick, "vk", str(user_id))
        self.send(
            user_id,
            f"✅ Аккаунт успешно привязан!\n\n"
            f"👤 Minecraft ник: {mc_nick}\n"
            f"🔗 Платформа: VK",
        )
        logger.info("Linked: %s ↔ VK %s", mc_nick, user_id)

    def _handle_unlink(self, user_id: int):
        existing = db.get_link_by_user("vk", str(user_id))
        if not existing:
            self.send(user_id, "ℹ️ У тебя нет привязанного аккаунта.")
            return

        db.unlink_account_by_user("vk", str(user_id))
        self.send(user_id, f"🔓 Аккаунт {existing['minecraft_nick']} отвязан.")

    def _handle_status(self, user_id: int):
        row = db.get_link_by_user("vk", str(user_id))
        if row:
            self.send(
                user_id,
                f"✅ Аккаунт привязан\n\n"
                f"👤 Ник: {row['minecraft_nick']}\n"
                f"🆔 UUID: {row['minecraft_uuid']}\n"
                f"📅 Привязан: {row['linked_at'][:19].replace('T', ' ')} UTC",
            )
        else:
            self.send(user_id, "❌ Аккаунт не привязан.\n\n" + HELP_TEXT)

    def run(self):
        logger.info("Starting VK bot (longpoll)...")
        for event in self.longpoll.listen():
            if event.type == VkEventType.MESSAGE_NEW and event.to_me:
                try:
                    self.handle_message(event.user_id, event.text)
                except Exception as e:
                    logger.error("Error handling VK message: %s", e)


def run_vk():
    VKBot().run()

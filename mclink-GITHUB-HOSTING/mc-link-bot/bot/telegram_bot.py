"""
Telegram бот для привязки Minecraft аккаунта.
Команды:
  /start  — приветствие
  /link <CODE>  — привязать аккаунт по коду из игры
  /unlink       — отвязать аккаунт
  /status       — показать текущую привязку
"""

import logging
from telegram import Update, ReplyKeyboardMarkup, KeyboardButton
from telegram.ext import (
    Application, CommandHandler, MessageHandler,
    ContextTypes, filters,
)
import database as db
from config import TELEGRAM_TOKEN, CODE_EXPIRE_MINUTES

logger = logging.getLogger(__name__)

HELP_TEXT = (
    "🎮 *Привязка Minecraft аккаунта*\n\n"
    "1️⃣ Зайди на сервер и введи команду `/link`\n"
    "2️⃣ Получишь код из 6 символов\n"
    "3️⃣ Отправь его сюда командой `/link КОД`\n\n"
    "Доступные команды:\n"
    "`/link КОД` — привязать аккаунт\n"
    "`/unlink` — отвязать аккаунт\n"
    "`/status` — показать привязку\n"
)


async def cmd_start(update: Update, ctx: ContextTypes.DEFAULT_TYPE):
    kb = ReplyKeyboardMarkup(
        [[KeyboardButton("/status"), KeyboardButton("/unlink")]],
        resize_keyboard=True,
    )
    await update.message.reply_text(
        f"👋 Привет, {update.effective_user.first_name}!\n\n" + HELP_TEXT,
        parse_mode="Markdown",
        reply_markup=kb,
    )


async def cmd_link(update: Update, ctx: ContextTypes.DEFAULT_TYPE):
    user_id = str(update.effective_user.id)
    args = ctx.args

    if not args:
        await update.message.reply_text(
            "❓ Укажи код из игры:\n`/link ABCDEF`\n\n"
            f"Код действует {CODE_EXPIRE_MINUTES} минут.",
            parse_mode="Markdown",
        )
        return

    code = args[0].strip().upper()

    # Проверяем, не привязан ли уже этот Telegram аккаунт
    existing = db.get_link_by_user("telegram", user_id)
    if existing:
        await update.message.reply_text(
            f"⚠️ Ты уже привязан к нику *{existing['minecraft_nick']}*.\n"
            "Введи /unlink чтобы отвязать, затем привяжи заново.",
            parse_mode="Markdown",
        )
        return

    result = db.consume_code(code)
    if result is None:
        await update.message.reply_text(
            "❌ Код неверный или истёк.\n"
            "Введи `/link` на сервере, чтобы получить новый.",
            parse_mode="Markdown",
        )
        return

    mc_uuid, mc_nick = result
    db.link_account(mc_uuid, mc_nick, "telegram", user_id)

    await update.message.reply_text(
        f"✅ Аккаунт успешно привязан!\n\n"
        f"👤 Minecraft ник: *{mc_nick}*\n"
        f"🔗 Платформа: Telegram",
        parse_mode="Markdown",
    )
    logger.info("Linked: %s ↔ Telegram %s", mc_nick, user_id)


async def cmd_unlink(update: Update, ctx: ContextTypes.DEFAULT_TYPE):
    user_id = str(update.effective_user.id)
    existing = db.get_link_by_user("telegram", user_id)

    if not existing:
        await update.message.reply_text("ℹ️ У тебя нет привязанного аккаунта.")
        return

    db.unlink_account_by_user("telegram", user_id)
    await update.message.reply_text(
        f"🔓 Аккаунт *{existing['minecraft_nick']}* отвязан.",
        parse_mode="Markdown",
    )


async def cmd_status(update: Update, ctx: ContextTypes.DEFAULT_TYPE):
    user_id = str(update.effective_user.id)
    row = db.get_link_by_user("telegram", user_id)

    if row:
        await update.message.reply_text(
            f"✅ *Аккаунт привязан*\n\n"
            f"👤 Ник: `{row['minecraft_nick']}`\n"
            f"🆔 UUID: `{row['minecraft_uuid']}`\n"
            f"📅 Привязан: {row['linked_at'][:19].replace('T', ' ')} UTC",
            parse_mode="Markdown",
        )
    else:
        await update.message.reply_text(
            "❌ Аккаунт не привязан.\n\n" + HELP_TEXT,
            parse_mode="Markdown",
        )


async def unknown_cmd(update: Update, ctx: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text(
        "❓ *Неизвестная команда*\n\n"
        "Доступные команды:\n"
        "/start — помощь\n"
        "/link КОД — привязать аккаунт\n"
        "/unlink — отвязать аккаунт\n"
        "/status — проверить привязку",
        parse_mode="Markdown",
    )


async def error_handler(update: Update, ctx: ContextTypes.DEFAULT_TYPE):
    """Обработчик ошибок."""
    logger.error("Exception while handling an update:", exc_info=ctx.error)
    
    if update and update.effective_message:
        await update.effective_message.reply_text(
            "⚠️ Произошла ошибка при обработке команды. Попробуй позже."
        )


def build_app() -> Application:
    if not TELEGRAM_TOKEN:
        raise ValueError("TELEGRAM_TOKEN не задан в .env")

    app = Application.builder().token(TELEGRAM_TOKEN).build()
    app.add_handler(CommandHandler("start", cmd_start))
    app.add_handler(CommandHandler("link", cmd_link))
    app.add_handler(CommandHandler("unlink", cmd_unlink))
    app.add_handler(CommandHandler("status", cmd_status))
    app.add_handler(MessageHandler(filters.COMMAND, unknown_cmd))
    app.add_error_handler(error_handler)
    return app


def run_telegram():
    logger.info("Starting Telegram bot...")
    build_app().run_polling(drop_pending_updates=True)

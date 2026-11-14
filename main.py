
import os
import logging
import threading
from flask import Flask
from telegram import Update
from telegram.ext import (
    Application,
    CommandHandler,
    MessageHandler,
    ContextTypes,
    filters,
)

logging.basicConfig(level=logging.INFO)

TOKEN = os.getenv("BOT_TOKEN")
web = Flask(__name__)

@web.get("/")
def home():
    return "YUCAI POWER bot is running", 200

WELCOME = {
    "uz": "Assalomu alaykum! YUCAI POWER kompaniyasiga xush kelibsiz. Generator tanlash uchun savolingizni yozing.",
    "ru": "Здравствуйте! Добро пожаловать в YUCAI POWER. Напишите, какой генератор вас интересует.",
    "en": "Hello! Welcome to YUCAI POWER. Tell us what generator you are looking for."
}

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text(
        "⚡ YUCAI POWER | UZBEKISTAN\n\n"
        "Tilni tanlang / Выберите язык / Choose language:\n\n"
        "/uz — O‘zbekcha\n"
        "/ru — Русский\n"
        "/en — English"
    )

async def language(update: Update, context: ContextTypes.DEFAULT_TYPE):
    lang = update.message.text[1:]
    context.user_data["lang"] = lang
    await update.message.reply_text(WELCOME[lang])

async def chat(update: Update, context: ContextTypes.DEFAULT_TYPE):
    lang = context.user_data.get("lang", "uz")
    messages = {
        "uz": "Savolingiz qabul qilindi. Menejerimiz tez orada siz bilan bog‘lanadi.",
        "ru": "Ваш вопрос принят. Наш менеджер скоро свяжется с вами.",
        "en": "Your message has been received. Our manager will contact you soon."
    }
    await update.message.reply_text(messages[lang])

def run_bot():
    if not TOKEN:
        raise RuntimeError("BOT_TOKEN environment variable is missing")

    app = Application.builder().token(TOKEN).build()
    app.add_handler(CommandHandler("start", start))
    app.add_handler(CommandHandler("uz", language))
    app.add_handler(CommandHandler("ru", language))
    app.add_handler(CommandHandler("en", language))
    app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, chat))
    app.run_polling()

if __name__ == "__main__":
    threading.Thread(target=run_bot, daemon=True).start()
    port = int(os.environ.get("PORT", 10000))
    web.run(host="0.0.0.0", port=port)

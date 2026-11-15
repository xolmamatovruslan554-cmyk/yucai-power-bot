
import os
import sys
import logging
from groq import AsyncGroq
import threading
from flask import Flask
web = Flask(__name__)

@web.route("/")
def home():
    return "YUCAI POWER BOT IS RUNNING", 200
from telegram import Update, KeyboardButton, ReplyKeyboardMarkup, ReplyKeyboardRemove
from telegram.ext import (
    Application, CommandHandler, MessageHandler,
    ContextTypes, filters
) 

logging.basicConfig(
    level=logging.INFO,
    stream=sys.stdout,
    format="%(asctime)s %(levelname)s %(message)s"
)

TOKEN = os.getenv("BOT_TOKEN") 
groq_client = AsyncGroq(api_key=os.getenv("GROQ_API_KEY"))
ADMIN_IDS = [8493734628, 8738794018]

web = Flask(__name__)

@web.get("/")
def home():
    return "YUCAI POWER bot is running", 200

TEXTS = {
    "uz": {
        "power": "Generator quvvati qancha kW bo‘lishi kerak?",
        "place": "Generator qayerda va nima maqsadda ishlatiladi?",
        "fuel": "Qaysi yoqilg‘i turi kerak? Dizel yoki gaz (gaz generatori buyurtma asosida olib kelinadi).",
        "phone": "Telefon raqamingizni yuborish tugmasini bosing.",
        "button": "📱 Telefon raqamni yuborish",
        "done": "✅ Rahmat! Buyurtmangiz menejerlarga yuborildi.\n\n📞 Tez orada menejerimiz siz bilan bog‘lanadi."
    },
    "ru": {
        "power": "Какая мощность генератора нужна (кВт)?",
        "place": "Где и для чего будет использоваться генератор?",
        "fuel": "Какое топливо нужно? Дизель или газ (газовый генератор доступен под заказ).",
        "phone": "Нажмите кнопку, чтобы отправить номер телефона.",
        "button": "📱 Отправить номер телефона",
        "done": "Спасибо! Ваша заявка отправлена менеджерам."
    },
    "en": {
        "power": "What generator capacity do you need (kW)?",
        "place": "Where and for what purpose will it be used?",
        "fuel": "Which fuel do you need? Diesel or gas (gas generators are available by special order).",
        "phone": "Press the button to share your phone number.",
        "button": "📱 Share phone number",
        "done": "Thank you! Your request has been sent to our managers."
    }
}

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    context.user_data.clear()
    await update.message.reply_text(
        "⚡ Assalomu alaykum!\n"
        "YUCAI POWER | UZBEKISTAN ga xush kelibsiz!\n"
        "Sizga generator tanlashda yordam beramiz.\n\n"
        "Tilni tanlang / Выберите язык / Choose language:\n\n"
        "/uz — O‘zbekcha\n"
        "/ru — Русский\n"
        "/en — English\n"
   "/ai — AI konsultant"
    ) 

async def language(update: Update, context: ContextTypes.DEFAULT_TYPE):
    lang = update.message.text[1:]
    context.user_data["lang"] = lang
    context.user_data["step"] = "power"
    await update.message.reply_text(TEXTS[lang]["power"])
async def ai_start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    context.user_data["step"] = "ai"
    context.user_data["ai_history"] = []
    await update.message.reply_text(
        "🤖 YUCAI POWER AI konsultantiga xush kelibsiz!\n"
        "Generator haqida savolingizni yozing."
    )
async def chat(update: Update, context: ContextTypes.DEFAULT_TYPE):
    lang = context.user_data.get("lang", "uz")
    step = context.user_data.get("step")
    msg = update.message     
    if step == "ai":
        history = context.user_data.setdefault("ai_history", [])
        history.append({"role": "user", "content": msg.text})
        try:
            response = await groq_client.chat.completions.create(
                model="qwen/qwen3.8-27b",
                messages=[
                    {
                        "role": "system",
                        
"content": """
Sen YUCAI POWER kompaniyasining professional AI generator konsultantisan.

ASOSIY VAZIFANG:
Mijozlarga generator tanlash, texnik maslahat berish va buyurtma berishda yordam berish.

TIL:
- Mijoz qaysi tilda yozsa, shu tilda javob ber.
- O‘zbek, rus va ingliz tillarini mukammal tushun.
- Tabiiy, tushunarli va professional yoz.

MULOQOT:
- Mijoz bilan xushmuomala gaplash.
- Javoblarni qisqa, aniq va foydali ber.
- Bir vaqtning o‘zida juda ko‘p savol bermagin.
- Kerakli ma'lumotlarni bittadan so‘ra.
- Mijozni ortiqcha savollar bilan charchatma.

GENERATOR TANLASH:
Quyidagilarni aniqlashga yordam ber:
- Kerakli quvvat (kW yoki kVA).
- Dizel yoki gaz generatori.
- Bir fazali yoki uch fazali elektr ta'minoti.
- Ishlatish maqsadi.
- Doimiy yoki zaxira elektr ta'minoti.
- Ishlash sharoiti.

TEXNIK QOIDALAR:
- kW va kVA birliklarini adashtirma.
- Generator quvvatini tanlashda ishga tushish toki va yuklamani hisobga ol.
- Aniq bo‘lmagan texnik ma'lumotlarni to‘qima.
- Tasdiqlanmagan narxlarni aytma.
- Kompaniya katalogida yo‘q mahsulotni mavjud deb ko‘rsatma.
- Bilmagan savolingga halol javob ber. - Bir xabarda faqat BITTA savol ber.
- Bir nechta ma'lumot kerak bo‘lsa, ularni ketma-ket bittadan so‘ra.
- Mijoz javob bermaguncha keyingi savolga o‘tma.QAT'IY ISHONCHLILIK QOIDALARI:
- Hech qachon narx, model yoki texnik ko‘rsatkichlarni o‘zingdan to‘qima.
- Katalog yoki zavod hujjatida bo‘lmagan ma’lumotni tasdiqlangan fakt sifatida aytma.
- Yoqilg‘i sarfi, aylanish tezligi, kuchlanish, chastota, faza, og‘irlik va o‘lchamlarni taxmin qilib yozma.
- Narx so‘ralsa, menejer narxni tasdiqlashini ayt.
- kW ni kVA ga faqat quvvat koeffitsiyenti (PF) ma'lum bo‘lsa hisobla.
- Ma'lumot yetarli bo‘lmasa, mijozdan bittadan aniqlashtiruvchi savol so‘ra.
- Tasdiqlanmagan texnik ma'lumotlarni jadvalga joylab, haqiqiydek ko‘rsatma.

SOTUV:
- Mijozga mos generatorni aniqlashga yordam ber.
- Mijoz sotib olishga tayyor bo‘lsa, menejer bilan bog‘lanishni taklif qil.
- Buyurtmani o‘zing tasdiqlama.
- Menejer nomidan va'da berma.

O‘ZINGNI YUCAI POWER AI KONSULTANTI SIFATIDA TANIT.
Har doim professional, ishonchli va samimiy bo‘l.
"""
                    },
                    *history[-10:]
                ],
                max_tokens=500
            )
            answer = response.choices[0].message.content
            history.append({"role": "assistant", "content": answer})
            context.user_data["ai_history"] = history[-10:]
            await msg.reply_text(answer)

        except Exception:
            logging.exception("GROQ AI XATOSI")
            await msg.reply_text("Kechirasiz, hozir javob bera olmadim.")

        return

    if not step:
        await msg.reply_text("Boshlash uchun /start bosing.")
        return

    if step == "power":
        context.user_data["power"] = msg.text
        context.user_data["step"] = "place"
        await msg.reply_text(TEXTS[lang]["place"])

    elif step == "place":
        context.user_data["place"] = msg.text
        context.user_data["step"] = "fuel"
        await msg.reply_text(TEXTS[lang]["fuel"])

    elif step == "fuel":
        context.user_data["fuel"] = msg.text
        context.user_data["step"] = "phone"
        keyboard = [[KeyboardButton(
            TEXTS[lang]["button"], request_contact=True
        )]]
        await msg.reply_text(
            TEXTS[lang]["phone"],
            reply_markup=ReplyKeyboardMarkup(
                keyboard, resize_keyboard=True, one_time_keyboard=True
            )
        )

async def get_contact(update: Update, context: ContextTypes.DEFAULT_TYPE):
    lang = context.user_data.get("lang", "uz")

    if context.user_data.get("step") != "phone":
        return

    contact = update.message.contact
    if contact.user_id != update.effective_user.id:
        await update.message.reply_text(
            "Iltimos, o‘zingizning raqamingizni yuboring."
        )
        return

    user = update.effective_user
    username = f"@{user.username}" if user.username else "Yo‘q"

    order = (
        "⚡ YANGI YUCAI POWER BUYURTMASI\n\n"
        f"👤 Ism: {user.full_name}\n"
        f"🔗 Username: {username}\n"
        f"🆔 Telegram ID: {user.id}\n"
        f"⚡ Quvvat: {context.user_data.get('power')}\n"
        f"📍 Joylashuv/maqsad: {context.user_data.get('place')}\n"
        f"⛽ Yoqilg‘i: {context.user_data.get('fuel')}\n"
        f"📞 Telefon: {contact.phone_number}"
    )

    sent = 0

    for admin_id in ADMIN_IDS:
        try:
            await context.bot.send_message(
                chat_id=admin_id,
                text=order
            )
            sent += 1
            logging.info("BUYURTMA ADMIN %s GA YUBORILDI", admin_id)

        except Exception:
            logging.exception("ADMIN %s GA XABAR YUBORILMADI", admin_id)

    context.user_data.clear()

    if sent == len(ADMIN_IDS):
        await update.message.reply_text(
            TEXTS[lang]["done"],
            reply_markup=ReplyKeyboardRemove()
        )
    else:
        await update.message.reply_text(
            f"Buyurtma qabul qilindi. Menejerlarga xabar yuborishda muammo: "
            f"{sent}/{len(ADMIN_IDS)} ta xabar yetkazildi.",
            reply_markup=ReplyKeyboardRemove()
        )
def run_bot():
    print("TELEGRAM BOT ISHGA TUSHDI", flush=True)
    if not TOKEN:
        raise RuntimeError("BOT_TOKEN topilmadi!")

    app = Application.builder().token(TOKEN).build()

    app.add_handler(CommandHandler("start", start))
    app.add_handler(CommandHandler("uz", language))
    app.add_handler(CommandHandler("ru", language))
    app.add_handler(CommandHandler("en", language))
    app.add_handler(CommandHandler("ai", ai_start))
    app.add_handler(MessageHandler(filters.CONTACT, get_contact))
    app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, chat))

    app.run_polling(stop_signals=None)

if __name__ == "__main__":
    threading.Thread(target=run_bot, daemon=True).start()
    port = int(os.environ.get("PORT", 10000))
    web.run(host="0.0.0.0", port=port)



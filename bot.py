import os
import logging
from telegram import Update, KeyboardButton, ReplyKeyboardMarkup, ReplyKeyboardRemove, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import Application, CommandHandler, MessageHandler, filters, ContextTypes, ConversationHandler

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

TOKEN = os.environ.get("BOT_TOKEN")
WEBAPP_URL = os.environ.get("WEBAPP_URL", "https://saidislom6134-cmyk.github.io/SabbFlow-/")

ASK_NAME, ASK_PHONE = range(2)

users_db = {}

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_id = update.effective_user.id
    
    if user_id in users_db:
        user = users_db[user_id]
        keyboard = [[InlineKeyboardButton("🔧 SabbFlow ni ochish", web_app={"url": WEBAPP_URL})]]
        reply_markup = InlineKeyboardMarkup(keyboard)
        await update.message.reply_text(
            f"Xush kelibsiz, {user['name']}! 👋\n\n"
            f"Kalkulyatorni ochish uchun quyidagi tugmani bosing:",
            reply_markup=reply_markup
        )
        return ConversationHandler.END
    
    await update.message.reply_text(
        "👋 Salom! SabbFlow ga xush kelibsiz!\n\n"
        "🔧 Atopleniya va santexnika hisob-kitobi uchun O'zbekistoning zamonaviy platformasi.\n\n"
        "Ro'yxatdan o'tish uchun ismingizni kiriting:"
    )
    return ASK_NAME

async def ask_name(update: Update, context: ContextTypes.DEFAULT_TYPE):
    name = update.message.text.strip()
    
    if len(name) < 2:
        await update.message.reply_text("❌ Iltimos, to'g'ri ism kiriting:")
        return ASK_NAME
    
    context.user_data["name"] = name
    
    phone_button = KeyboardButton("📱 Telefon raqamni yuborish", request_contact=True)
    keyboard = ReplyKeyboardMarkup([[phone_button]], resize_keyboard=True, one_time_keyboard=True)
    
    await update.message.reply_text(
        f"Rahmat, {name}! 😊\n\n"
        "Endi telefon raqamingizni yuboring.\n"
        "Quyidagi tugmani bosing 👇",
        reply_markup=keyboard
    )
    return ASK_PHONE

async def ask_phone(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if update.message.contact:
        phone = update.message.contact.phone_number
        if not phone.startswith("+"):
            phone = "+" + phone
    else:
        phone = update.message.text.strip()
        if not phone.startswith("+"):
            phone = "+" + phone
    
    user_id = update.effective_user.id
    name = context.user_data.get("name", "Foydalanuvchi")
    
    users_db[user_id] = {
        "name": name,
        "phone": phone,
        "telegram_id": user_id
    }
    
    logger.info(f"New user: {name} | {phone} | ID: {user_id}")
    
    keyboard = [[InlineKeyboardButton("🔧 SabbFlow ni ochish", web_app={"url": WEBAPP_URL})]]
    reply_markup = InlineKeyboardMarkup(keyboard)
    
    await update.message.reply_text(
        f"✅ Ro'yxatdan muvaffaqiyatli o'tdingiz!\n\n"
        f"👤 Ism: {name}\n"
        f"📱 Telefon: {phone}\n\n"
        f"Endi kalkulyatorni ishlatishingiz mumkin 👇",
        reply_markup=ReplyKeyboardRemove()
    )
    
    await update.message.reply_text(
        "🔧 Kalkulyatorni ochish uchun quyidagi tugmani bosing:",
        reply_markup=reply_markup
    )
    
    return ConversationHandler.END

async def cancel(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text(
        "❌ Bekor qilindi. Qayta boshlash uchun /start yozing.",
        reply_markup=ReplyKeyboardRemove()
    )
    return ConversationHandler.END

async def help_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_id = update.effective_user.id
    keyboard = [[InlineKeyboardButton("🔧 SabbFlow ni ochish", web_app={"url": WEBAPP_URL})]]
    reply_markup = InlineKeyboardMarkup(keyboard)
    await update.message.reply_text(
        "🔧 *SabbFlow — Atopleniya Kalkulyatori*\n\n"
        "📌 Buyruqlar:\n"
        "/start — Botni boshlash\n"
        "/help — Yordam\n\n"
        "💡 Kalkulyatorni ochish uchun:",
        parse_mode="Markdown",
        reply_markup=reply_markup
    )

def main():
    app = Application.builder().token(TOKEN).build()
    
    conv_handler = ConversationHandler(
        entry_points=[CommandHandler("start", start)],
        states={
            ASK_NAME: [MessageHandler(filters.TEXT & ~filters.COMMAND, ask_name)],
            ASK_PHONE: [
                MessageHandler(filters.CONTACT, ask_phone),
                MessageHandler(filters.TEXT & ~filters.COMMAND, ask_phone)
            ],
        },
        fallbacks=[CommandHandler("cancel", cancel)],
    )
    
    app.add_handler(conv_handler)
    app.add_handler(CommandHandler("help", help_command))
    
    logger.info("SabbFlow bot ishga tushdi!")
    app.run_polling(drop_pending_updates=True)

if __name__ == "__main__":
    main()

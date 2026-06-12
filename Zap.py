import asyncio
import requests
from telegram import Update, ReplyKeyboardMarkup
from telegram.ext import ApplicationBuilder, CommandHandler, MessageHandler, ContextTypes, filters
from telegram.request import HTTPXRequest

BOT_TOKEN = "8688941654:AAHlK7QbaOm7ET8G1r3fhMa3W6YMoc9cDfQ"
API = "http://anishexploits.com/api/number.php?exploits="

keyboard = ReplyKeyboardMarkup(
    [["📱 Phone Lookup"]],
    resize_keyboard=True
)

# API se text fetch
def fetch_api(num):
    try:
        r = requests.get(API + num, timeout=60)
        return r.text.strip()
    except Exception as e:
        print("API Error:", e)
        return None

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text(
        "Welcome to Number Info Bot 👋",
        reply_markup=keyboard
    )

async def handle(update: Update, context: ContextTypes.DEFAULT_TYPE):
    text = update.message.text.strip()

    if text == "📱 Phone Lookup":
        await update.message.reply_text("📞 Send 10 digit mobile number:")
        return

    if text.isdigit() and len(text) == 10:
        await update.message.reply_text(f"🔍 Fetching info for {text} ...")
        await asyncio.sleep(1)

        data = await asyncio.to_thread(fetch_api, text)

        if not data:
            await update.message.reply_text("❌ No information found")
            return

        # Unwanted footer remove
        bad_lines = [
            "💳 BUY API : @Cyb3rS0ldier",
            "🆘 SUPPORT : @Cyb3rS0ldier"
        ]

        for line in bad_lines:
            data = data.replace(line, "")

        # Apna footer add karna ho
        data = data.strip() + "\n\n━━━━━━━━━━━━━━━━━━\n👑 Developer: ZAP PAPA"

        await update.message.reply_text(data)
        return

    await update.message.reply_text(
        "⚠️ Invalid input\nUse button below ⬇️",
        reply_markup=keyboard
    )

def main():
    print("Zap Papa Bot Started Successfully")

    request = HTTPXRequest(
        connect_timeout=120,
        read_timeout=120,
        write_timeout=120,
        pool_timeout=120
    )

    app = (
        ApplicationBuilder()
        .token(BOT_TOKEN)
        .request(request)
        .build()
    )

    app.add_handler(CommandHandler("start", start))
    app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, handle))

    app.run_polling(drop_pending_updates=True)

if __name__ == "__main__":
    main()
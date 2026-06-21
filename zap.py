#!/usr/bin/env python3
"""
ZAP PAPA 🔥 - Telegram Number Lookup Bot
Single file: bot.py | python-telegram-bot v22.x
Termux + Android compatible
"""

import json
import os
import logging
import asyncio
from datetime import datetime

import requests
from telegram import Update
from telegram.ext import Application, CommandHandler, MessageHandler, filters, ContextTypes

# ====================== CONFIGURATION ======================

BOT_TOKEN = "7075893121:AAFKZl7l_LsCp0993hF2ou2Mn3fElmkiRJo"          # @BotFather se lo
OWNER_ID = 6325764594                        # Aapki Telegram user ID
API_URL = "https://anishexploits.com/api/api.php?key=KEY_AE2E95D4_ZAP3X&type=number&num="  # Tumhari API URL

USERS_FILE = "users.json"
CREDIT_FOOTER = "\n━━━━━━━━━━━━━━\nPowered By: ZAP PAPA\n━━━━━━━━━━━━━━"

# ====================== LOGGING ======================

logging.basicConfig(
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
    level=logging.INFO
)
logger = logging.getLogger(__name__)

# ====================== USERS DATABASE ======================

def load_users() -> list:
    if not os.path.exists(USERS_FILE):
        return [OWNER_ID]
    try:
        with open(USERS_FILE, "r") as f:
            data = json.load(f)
            if isinstance(data, list):
                return data
            return [OWNER_ID]
    except (json.JSONDecodeError, IOError):
        return [OWNER_ID]

def save_users(users: list):
    with open(USERS_FILE, "w") as f:
        json.dump(users, f, indent=2)

def is_authorized(user_id: int, users: list) -> bool:
    return user_id in users

def is_owner(user_id: int) -> bool:
    return user_id == OWNER_ID

# ====================== COMMANDS ======================

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_id = update.effective_user.id
    users = load_users()
    
    if not is_authorized(user_id, users):
        await update.message.reply_text("Access Denied")
        return
    
    await update.message.reply_text(
        f"👋 Welcome!\n\n"
        f"Send me a mobile number to lookup.\n\n"
        f"Example: 9876543210{CREDIT_FOOTER}"
    )

async def handle_number(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_id = update.effective_user.id
    users = load_users()
    
    # Access check
    if not is_authorized(user_id, users):
        await update.message.reply_text("Access Denied")
        return
    
    text = update.message.text.strip()
    
    # Clean number - remove spaces, +, etc
    number = "".join(c for c in text if c.isdigit())
    
    if len(number) < 7 or len(number) > 15:
        await update.message.reply_text(
            f"❌ Invalid number. Please send a valid mobile number.\n\n"
            f"Example: 9876543210{CREDIT_FOOTER}"
        )
        return
    
    # Send typing indicator
    await context.bot.send_chat_action(chat_id=update.effective_chat.id, action="typing")
    
    try:
        # Call API
        resp = requests.get(
            f"{API_URL}?number={number}",
            timeout=30,
            headers={"User-Agent": "Mozilla/5.0 (Linux; Android 10; K)"}
        )
        resp.raise_for_status()
        
        # Parse JSON
        try:
            data = resp.json()
        except json.JSONDecodeError:
            await update.message.reply_text(
                f"❌ Invalid JSON response from server.{CREDIT_FOOTER}"
            )
            return
        
        # Check status
        if data.get("status") != "success":
            await update.message.reply_text(
                f"❌ API returned: {data.get('status', 'unknown error')}{CREDIT_FOOTER}"
            )
            return
        
        # Get result array
        results = data.get("result", [])
        if not results:
            await update.message.reply_text(
                f"❌ No data found for this number.{CREDIT_FOOTER}"
            )
            return
        
        # Show ALL results
        output = ""
        for idx, entry in enumerate(results, 1):
            output += f"━━━━━━━ #{idx} ━━━━━━━\n"
            # Only show useful fields from "result" - NO metadata
            fields = {
                "name": "👤 Name",
                "fname": "👨 Father",
                "aadhar": "🆔 Aadhaar",
                "address": "📍 Address",
                "alt": "📞 Alt Number",
                "circle": "🌐 Circle",
                "email": "📧 Email",
                "num": "🔢 Number"
            }
            
            for key, label in fields.items():
                val = entry.get(key)
                if val and str(val).strip():
                    output += f"{label}: {val}\n"
            
            output += "\n"
        
        output += CREDIT_FOOTER
        await update.message.reply_text(output)
    
    except requests.exceptions.Timeout:
        await update.message.reply_text(
            f"❌ API timeout. Server took too long to respond.{CREDIT_FOOTER}"
        )
    except requests.exceptions.ConnectionError:
        await update.message.reply_text(
            f"❌ Connection error. API server is unreachable.{CREDIT_FOOTER}"
        )
    except requests.exceptions.HTTPError as e:
        await update.message.reply_text(
            f"❌ HTTP Error: {e.response.status_code}{CREDIT_FOOTER}"
        )
    except requests.exceptions.RequestException as e:
        await update.message.reply_text(
            f"❌ API Error: {str(e)[:200]}{CREDIT_FOOTER}"
        )
    except Exception as e:
        logger.error(f"Unexpected error: {e}", exc_info=True)
        await update.message.reply_text(
            f"❌ Unexpected error occurred.{CREDIT_FOOTER}"
        )

# ====================== OWNER COMMANDS ======================

async def adduser(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_id = update.effective_user.id
    
    if not is_owner(user_id):
        await update.message.reply_text("Access Denied")
        return
    
    if not context.args:
        await update.message.reply_text("Usage: /adduser <telegram_id>")
        return
    
    try:
        target_id = int(context.args[0])
    except ValueError:
        await update.message.reply_text("❌ Invalid ID. Must be a number.")
        return
    
    users = load_users()
    
    if target_id in users:
        await update.message.reply_text(f"ℹ️ User `{target_id}` is already authorized.")
        return
    
    users.append(target_id)
    save_users(users)
    await update.message.reply_text(f"✅ User `{target_id}` has been authorized successfully!")

async def removeuser(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_id = update.effective_user.id
    
    if not is_owner(user_id):
        await update.message.reply_text("Access Denied")
        return
    
    if not context.args:
        await update.message.reply_text("Usage: /removeuser <telegram_id>")
        return
    
    try:
        target_id = int(context.args[0])
    except ValueError:
        await update.message.reply_text("❌ Invalid ID. Must be a number.")
        return
    
    if target_id == OWNER_ID:
        await update.message.reply_text("❌ Cannot remove the owner.")
        return
    
    users = load_users()
    
    if target_id not in users:
        await update.message.reply_text(f"ℹ️ User `{target_id}` is not in the authorized list.")
        return
    
    users.remove(target_id)
    save_users(users)
    await update.message.reply_text(f"✅ User `{target_id}` has been removed successfully!")

async def listusers(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_id = update.effective_user.id
    
    if not is_owner(user_id):
        await update.message.reply_text("Access Denied")
        return
    
    users = load_users()
    
    if not users:
        await update.message.reply_text("📭 No authorized users.")
        return
    
    msg = "👥 **Authorized Users:**\n\n"
    for i, uid in enumerate(users, 1):
        tag = " 👑 OWNER" if uid == OWNER_ID else ""
        msg += f"{i}. `{uid}`{tag}\n"
    
    msg += f"\nTotal: {len(users)}"
    await update.message.reply_text(msg)

# ====================== MAIN ======================

def main():
    token = BOT_TOKEN
    
    # Ensure users.json exists
    load_users()
    
    # Build application
    app = Application.builder().token(token).build()
    
    # Handlers
    app.add_handler(CommandHandler("start", start))
    app.add_handler(CommandHandler("adduser", adduser))
    app.add_handler(CommandHandler("removeuser", removeuser))
    app.add_handler(CommandHandler("users", listusers))
    
    # Catch all text messages as number input
    app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, handle_number))
    
    logger.info("🤖 ZAP PAPA Bot started successfully!")
    logger.info(f"👑 Owner ID: {OWNER_ID}")
    logger.info(f"📁 Users file: {USERS_FILE}")
    
    # Long polling - no webhook
    app.run_polling(allowed_updates=Update.ALL_TYPES)

if __name__ == "__main__":
    main()
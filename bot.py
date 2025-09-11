# bot.py (edited to provide an imghdr fallback using filetype)
import sys
import types
import logging

# --- imghdr fallback shim (for Python >=3.13 where imghdr may be removed) ---
try:
    import imghdr  # try native module first
except ModuleNotFoundError:
    try:
        import filetype
    except Exception:
        # If filetype is not installed (should be installed via requirements.txt),
        # provide a trivial fallback so import won't crash — returns None always.
        imghdr_module = types.ModuleType("imghdr")
        def what(filename, h=None):
            return None
        imghdr_module.what = what
        sys.modules['imghdr'] = imghdr_module
    else:
        # create a small imghdr-like module that uses filetype.guess on bytes
        imghdr_module = types.ModuleType("imghdr")
        def what(filename, h=None):
            try:
                if h is None:
                    with open(filename, "rb") as f:
                        data = f.read(4096)
                else:
                    # h is bytes
                    data = h
                kind = filetype.guess(data)
                if kind:
                    ext = kind.extension
                    # imghdr returns 'jpeg' not 'jpg'
                    if ext == "jpg":
                        return "jpeg"
                    return ext
            except Exception:
                return None
        imghdr_module.what = what
        sys.modules['imghdr'] = imghdr_module

# --- rest of imports ---
import os
from telegram.ext import Updater, MessageHandler, Filters, CommandHandler

# Logging setup
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(levelname)s - %(message)s"
)
logger = logging.getLogger(__name__)

# گرفتن توکن و چت آیدی از Environment Variables
TOKEN = os.getenv("TOKEN")
ADMIN_ID_STR = os.getenv("ADMIN_ID")

if not TOKEN:
    logger.error("Environment variable TOKEN is not set. Exiting.")
    raise SystemExit("TOKEN not set")
if not ADMIN_ID_STR:
    logger.error("Environment variable ADMIN_ID is not set. Exiting.")
    raise SystemExit("ADMIN_ID not set")

try:
    ADMIN_ID = int(ADMIN_ID_STR)
except ValueError:
    logger.error("ADMIN_ID must be an integer (no @). Value provided: %r", ADMIN_ID_STR)
    raise

# پیام خوش‌آمدگویی
WELCOME_MSG = """
سلام 👋
به ربات «ارتباط با ما» خوش آمدید ✨

📌 از طریق این ربات می‌توانید:
- متن پیام ارسال کنید 📝
- فایل، عکس، ویدیو یا ویس بفرستید 📂
- سوالات و درخواست‌های خودتون رو مطرح کنید 🎓

پیام‌های شما مستقیم برای پشتیبان ارسال میشه ✅
"""

def start(update, context):
    try:
        update.message.reply_text(WELCOME_MSG)
    except Exception as e:
        logger.exception("Failed to send welcome message: %s", e)

def forward_with_info(update, context):
    try:
        # Some updates might not have message (e.g. edited_message), guard it:
        msg = update.message
        if msg is None:
            return

        user = msg.from_user or {}
        name = getattr(user, "first_name", "") or ""
        username = f"@{getattr(user, 'username', None)}" if getattr(user, 'username', None) else "یوزرنیم ندارد"
        user_id = getattr(user, "id", "ناشناخته")
        user_info = f"👤 نام: {name}\n🔗 یوزرنیم: {username}\n🆔 آیدی: {user_id}"

        # متن
        if msg.text:
            text = msg.text
            context.bot.send_message(chat_id=ADMIN_ID, text=f"{user_info}\n\n💬 پیام:\n{text}")
            return

        # مستندات/فایل‌ها — فقط اطلاع رسانی و فوروارد
        if msg.document:
            context.bot.send_message(chat_id=ADMIN_ID, text=f"{user_info}\n📂 فایل:")
            msg.forward(chat_id=ADMIN_ID)
            return

        if msg.photo:
            context.bot.send_message(chat_id=ADMIN_ID, text=f"{user_info}\n🖼 عکس:")
            msg.forward(chat_id=ADMIN_ID)
            return

        if msg.video:
            context.bot.send_message(chat_id=ADMIN_ID, text=f"{user_info}\n🎥 ویدیو:")
            msg.forward(chat_id=ADMIN_ID)
            return

        if msg.voice:
            context.bot.send_message(chat_id=ADMIN_ID, text=f"{user_info}\n🎤 ویس:")
            msg.forward(chat_id=ADMIN_ID)
            return

        # fallback
        context.bot.send_message(chat_id=ADMIN_ID, text=f"{user_info}\n⚠️ یک پیام ناشناس ارسال شد.")
    except Exception as e:
        logger.exception("Error in forward_with_info: %s", e)

def main():
    logger.info("Starting bot...")
    updater = Updater(TOKEN, use_context=True)
    dp = updater.dispatcher

    dp.add_handler(CommandHandler("start", start))
    dp.add_handler(MessageHandler(Filters.all, forward_with_info))

    updater.start_polling()
    logger.info("Polling started.")
    updater.idle()

if __name__ == "__main__":
    main()

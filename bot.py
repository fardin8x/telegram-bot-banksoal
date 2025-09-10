import os
from telegram.ext import Updater, MessageHandler, Filters, CommandHandler

# گرفتن توکن و چت آیدی از Environment Variables
TOKEN = os.getenv("TOKEN")
ADMIN_ID = int(os.getenv("ADMIN_ID"))

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
    update.message.reply_text(WELCOME_MSG)

def forward_with_info(update, context):
    user = update.message.from_user
    name = user.first_name
    username = f"@{user.username}" if user.username else "یوزرنیم ندارد"
    user_info = f"👤 نام: {name}\n🔗 یوزرنیم: {username}\n🆔 آیدی: {user.id}"

    if update.message.text:
        text = update.message.text
        context.bot.send_message(
            chat_id=ADMIN_ID,
            text=f"{user_info}\n\n💬 پیام:\n{text}"
        )

    elif update.message.document:
        context.bot.send_message(chat_id=ADMIN_ID, text=f"{user_info}\n📂 فایل:")
        update.message.forward(chat_id=ADMIN_ID)

    elif update.message.photo:
        context.bot.send_message(chat_id=ADMIN_ID, text=f"{user_info}\n🖼 عکس:")
        update.message.forward(chat_id=ADMIN_ID)

    elif update.message.video:
        context.bot.send_message(chat_id=ADMIN_ID, text=f"{user_info}\n🎥 ویدیو:")
        update.message.forward(chat_id=ADMIN_ID)

    elif update.message.voice:
        context.bot.send_message(chat_id=ADMIN_ID, text=f"{user_info}\n🎤 ویس:")
        update.message.forward(chat_id=ADMIN_ID)

    else:
        context.bot.send_message(chat_id=ADMIN_ID, text=f"{user_info}\n⚠️ یک پیام ناشناس ارسال شد.")

updater = Updater(TOKEN, use_context=True)
dp = updater.dispatcher

dp.add_handler(CommandHandler("start", start))
dp.add_handler(MessageHandler(Filters.all, forward_with_info))

updater.start_polling()
updater.idle()

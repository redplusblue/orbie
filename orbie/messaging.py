from telegram import Bot

TELEGRAM_API_KEY = "YOUR_TELEGRAM_API_KEY"

bot = Bot(token=TELEGRAM_API_KEY)

def send_message(chat_id, text):
    bot.send_message(chat_id=chat_id, text=text)

#telegram_bot.py

import os
import logging
from telegram.ext import ApplicationBuilder, CommandHandler, CallbackQueryHandler, MessageHandler, filters
from dotenv import load_dotenv
from telegram_bot.handlers.handlers import start, button_handler, handle_input


load_dotenv()

TELEGRAM_TOKEN = os.getenv('TELEGRAM_TOKEN')


def start_telegram_bot():
    logging.basicConfig(level=logging.INFO)

    application = ApplicationBuilder().token(TELEGRAM_TOKEN).build()

    application.add_handler(CommandHandler('start', start))
    application.add_handler(CallbackQueryHandler(button_handler))
    application.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, handle_input))

    application.run_polling()

if __name__ == "__main__":
    start_telegram_bot()
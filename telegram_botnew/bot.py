import os
import logging
from telegram import Update
from telegram.ext import ApplicationBuilder, CommandHandler, CallbackQueryHandler, MessageHandler, filters
from dotenv import load_dotenv


from telegram_botnew.keyboards.main_menu import cmd_start, handler_menu_principale
from telegram_botnew.keyboards.search_product.search_product_menu import conv_cerca_prodotto
from telegram_botnew.keyboards.settings.settings_menu import settings_menu
from telegram_botnew.keyboards.settings.admin_settings import admin_menu

load_dotenv()

TELEGRAM_TOKEN = os.getenv('TELEGRAM_TOKEN')

logging.basicConfig(
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    level=logging.INFO
)

def start_telegram_bot():
    logging.basicConfig(level=logging.INFO)

    application = ApplicationBuilder().token(TELEGRAM_TOKEN).build()

    application.add_handler(conv_cerca_prodotto)
    
    application.add_handler(CommandHandler('start', cmd_start))

    application.add_handler(CallbackQueryHandler(handler_menu_principale, pattern=r"^back_to_main$"))

    application.add_handler(CallbackQueryHandler(settings_menu, pattern=r"^settings$"))
    application.add_handler(CallbackQueryHandler(admin_menu, pattern=r"^admin_settings$"))
    

    application.run_polling(allowed_updates=Update.ALL_TYPES)

if __name__ == "__main__":
    start_telegram_bot()
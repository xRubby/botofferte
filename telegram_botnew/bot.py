import os
import logging
from telegram import Update
from telegram.ext import ApplicationBuilder, CommandHandler, CallbackQueryHandler, MessageHandler, filters
from dotenv import load_dotenv


from telegram_botnew.keyboards.channel_offers.channel_offers_main import channeloffers_main, conv_add_channel
from telegram_botnew.keyboards.main_menu import cmd_start, handler_menu_principale
from telegram_botnew.keyboards.search_product.search_product_menu import conv_cerca_prodotto
from telegram_botnew.keyboards.settings.settings_menu import settings_menu
from telegram_botnew.keyboards.settings.admin_settings import admin_menu, attiva_licenza_ok, disattiva_licenza_confirm, disattiva_licenza_ok, conv_genera_licenza, visualizza_licenze, dettagli_licenza
from telegram_botnew.keyboards.channel_offers.channels_offers_info import channel_info
from telegram_botnew.keyboards.channel_offers.channel_offers_addLink import conv_insert_link
from telegram_botnew.keyboards.channel_offers.channel_offers_showLinks import insert_link_entry, publish_link, remove_link

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
    application.add_handler(conv_genera_licenza)
    application.add_handler(conv_add_channel)
    application.add_handler(conv_insert_link)
    
    application.add_handler(CommandHandler('start', cmd_start))

    application.add_handler(CallbackQueryHandler(handler_menu_principale, pattern=r"^back_to_main$"))

    application.add_handler(CallbackQueryHandler(settings_menu, pattern=r"^settings$"))

    application.add_handler(CallbackQueryHandler(admin_menu, pattern=r"^admin_settings$"))
    application.add_handler(CallbackQueryHandler(visualizza_licenze, pattern=r"^admin_settings_visualizzalicenze_\d+$"))
    application.add_handler(CallbackQueryHandler(dettagli_licenza,   pattern=r"^admin_settings_dettaglilicenza_.+$"))
    application.add_handler(CallbackQueryHandler(attiva_licenza_ok, pattern=r"^admin_settings_attivalicenza_.+$"))
    application.add_handler(CallbackQueryHandler(disattiva_licenza_confirm, pattern=r"^admin_settings_disattivalicenza_.+$"))
    application.add_handler(CallbackQueryHandler(disattiva_licenza_ok,      pattern=r"^admin_settings_disattiva_ok_.+$"))

    application.add_handler(CallbackQueryHandler(channeloffers_main, pattern=r"^channeloffers_main$"))
    application.add_handler(CallbackQueryHandler(insert_link_entry, pattern=r"^channeloffers_link_\d+_-?\d+$"))
    application.add_handler(CallbackQueryHandler(publish_link, pattern=r"channeloffers_publishlink_\d+_.+$"))
    application.add_handler(CallbackQueryHandler(remove_link, pattern=r"channeloffers_removelink_\d+_.+$"))
    application.add_handler(CallbackQueryHandler(channel_info, pattern="^channeloffers_info_.+$"))
    

    

    application.run_polling(allowed_updates=Update.ALL_TYPES)

if __name__ == "__main__":
    start_telegram_bot()
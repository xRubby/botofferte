import os
import logging
from telegram import Update
from telegram.ext import ApplicationBuilder, CommandHandler, CallbackQueryHandler, MessageHandler, filters
from dotenv import load_dotenv

from telegram_bot.keyboards.channel_offers.channel_offers_adminpanel import admin_delete_channel, admin_delete_channel_confirm, admin_invite_member, admin_invite_member_createlink, admin_invite_member_removelink, admin_license_info, admin_manage_members, admin_panel, conv_edit_admin_affiliateid
from telegram_bot.keyboards.channel_offers.channel_offers_layout_img import activate_attr_img, activate_immagine, confirm_delete_immagine, delete_immagine, edit_immagine, edit_immagini, immagine_menu, conv_add_immagine, layoutimg_attr_menu, layoutimg_prodotto_menu, show_immagini, conv_set_pos, conv_set_size
from telegram_bot.keyboards.channel_offers.channel_offers_layout_keyboard import activate_keyboard, confirm_delete_keyboard, delete_keyboard, edit_keyboard, edit_keyboards, keyboard_menu, show_keyboards
from telegram_bot.keyboards.channel_offers.channel_offers_layout_tags import edit_tags, edit_tags_spedito, conv_edit_tag, conv_edit_tag_spedito
from telegram_bot.keyboards.channel_offers.channel_offers_main import channeloffers_main, conv_add_channel
from telegram_bot.keyboards.channel_offers.channel_offers_settings import channel_settings_menu, exit_channel, exit_channel_confirm
from telegram_bot.keyboards.main_menu import cmd_start, handler_menu_principale
from telegram_bot.keyboards.search_product.search_product_menu import conv_cerca_prodotto
from telegram_bot.keyboards.settings.settings_menu import settings_menu
from telegram_bot.keyboards.settings.admin_settings import admin_menu, attiva_licenza_ok, disattiva_licenza_confirm, disattiva_licenza_ok, conv_genera_licenza, visualizza_licenze, dettagli_licenza
from telegram_bot.keyboards.channel_offers.channels_offers_info import channel_info
from telegram_bot.keyboards.channel_offers.channel_offers_addLink import conv_insert_link
from telegram_bot.keyboards.channel_offers.channel_offers_showLinks import insert_link_entry, publish_link, remove_link
from telegram_bot.keyboards.channel_offers.channel_offers_affiliateID import conv_insert_affiliateID
from telegram_bot.keyboards.channel_offers.channel_offers_layout import activate_layout, confirm_delete_layout, conv_layout, delete_layout, edit_layout, edit_layouts, layout_menu, show_layouts, conv_edit_messaggio_layout
from telegram_bot.keyboards.channel_offers.channel_offers_layout_keyboard import conv_keyboard, conv_edit_messaggio_keyboard
from utils.channel_offers_utils import delete_preview

load_dotenv()

TELEGRAM_TOKEN = os.getenv('TELEGRAM_TOKEN')

logging.basicConfig(
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    level=logging.INFO
)

def start_telegram_bot():
    logging.basicConfig(level=logging.INFO)

    application = ApplicationBuilder().token(TELEGRAM_TOKEN).concurrent_updates(10).build()

    application.add_handler(conv_cerca_prodotto)
    application.add_handler(conv_genera_licenza)
    application.add_handler(conv_add_channel)
    application.add_handler(conv_insert_link)
    application.add_handler(conv_insert_affiliateID)
    application.add_handler(conv_layout)
    application.add_handler(conv_edit_messaggio_layout)
    application.add_handler(conv_edit_tag_spedito)
    application.add_handler(conv_edit_tag)
    application.add_handler(conv_edit_admin_affiliateid)
    application.add_handler(conv_add_immagine)
    application.add_handler(conv_set_pos)
    application.add_handler(conv_set_size)
    application.add_handler(conv_keyboard)
    application.add_handler(conv_edit_messaggio_keyboard)
    
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

    application.add_handler(CallbackQueryHandler(layout_menu, pattern="^channeloffers_layout_.+$"))
    application.add_handler(CallbackQueryHandler(show_layouts, pattern="^channeloffers_showlayouts_.+$"))
    application.add_handler(CallbackQueryHandler(activate_layout, pattern=r'^channeloffers_activatelayout_(-?\d+)_(\d+)$'))
    application.add_handler(CallbackQueryHandler(edit_layouts, pattern="^channeloffers_editlayouts_.+$"))
    application.add_handler(CallbackQueryHandler(edit_layout, pattern=r'^channeloffers_editlayout_(-?\d+)_(\d+)$'))
    application.add_handler(CallbackQueryHandler(delete_layout,         pattern=r'^channeloffers_deletelayout_-?\d+_\d+$'))
    application.add_handler(CallbackQueryHandler(confirm_delete_layout, pattern=r'^channeloffers_confirmdeletelayout_-?\d+_\d+$'))
    application.add_handler(CallbackQueryHandler(edit_tags, pattern=r'^co_edittags_-?\d+$'))
    application.add_handler(CallbackQueryHandler(edit_tags_spedito, pattern=r'^co_edittags_(-\d+)_sp$'))
    
    application.add_handler(CallbackQueryHandler(admin_panel, pattern="^channeloffers_adminpanel_.+$"))
    application.add_handler(CallbackQueryHandler(admin_license_info, pattern="^channeloffers_adminlicenseinfo_.+$"))
    application.add_handler(CallbackQueryHandler(admin_delete_channel_confirm, pattern="^channeloffers_admindeletechannelconfirm_.+$"))
    application.add_handler(CallbackQueryHandler(admin_delete_channel, pattern="^channeloffers_admindeletechannel_.+$"))
    application.add_handler(CallbackQueryHandler(admin_invite_member, pattern="^channeloffers_invitemember_.+$"))
    application.add_handler(CallbackQueryHandler(admin_invite_member_createlink, pattern="^channeloffers_admincreatelinkmember_.+$"))
    application.add_handler(CallbackQueryHandler(admin_invite_member_removelink, pattern="^channeloffers_adminremovelinkmember_.+$"))
    application.add_handler(CallbackQueryHandler(admin_manage_members, pattern=r"^channeloffers_managemembers_[^_]+_\d+$"))

    application.add_handler(CallbackQueryHandler(channel_settings_menu, pattern="^channeloffers_settings_.+$"))
    application.add_handler(CallbackQueryHandler(exit_channel, pattern="^channeloffers_exitchannel_.+$"))
    application.add_handler(CallbackQueryHandler(exit_channel_confirm, pattern="^channeloffers_exitchannelconfirm_.+$"))

    application.add_handler(CallbackQueryHandler(immagine_menu, pattern=r'^layoutimg_menu_-?\d+$'))
    application.add_handler(CallbackQueryHandler(show_immagini, pattern=r'^layoutimg_show_-?\d+$'))
    application.add_handler(CallbackQueryHandler(activate_immagine, pattern=r'^layoutimg_activate_-?\d+_\d+$'))
    application.add_handler(CallbackQueryHandler(edit_immagini,           pattern=r'^layoutimg_edit_-?\d+$'))
    application.add_handler(CallbackQueryHandler(edit_immagine,           pattern=r'^layoutimg_editone_-?\d+_\d+$'))
    application.add_handler(CallbackQueryHandler(delete_immagine,         pattern=r'^layoutimg_delete_-?\d+_\d+$'))
    application.add_handler(CallbackQueryHandler(confirm_delete_immagine, pattern=r'^layoutimg_confirmdelete_-?\d+_\d+$'))
    application.add_handler(CallbackQueryHandler(activate_attr_img, pattern=r'^layoutimg_activateattr_-?\d+_\d+_[a-zA-Z]+$'))
    application.add_handler(CallbackQueryHandler(layoutimg_prodotto_menu, pattern=r'^layoutimg_prodottomenu_-?\d+_\d+$'))
    application.add_handler(CallbackQueryHandler(layoutimg_attr_menu, pattern=r'^layoutimg_(prezzomenu|prezzooldmenu|scontomenu)_-?\d+_\d+$'))

    application.add_handler(CallbackQueryHandler(keyboard_menu, pattern="^channeloffers_keyboards_.+$"))
    application.add_handler(CallbackQueryHandler(show_keyboards, pattern="^channeloffers_showkeyboards_.+$"))
    application.add_handler(CallbackQueryHandler(activate_keyboard, pattern=r'^channeloffers_activatekeyboard_(-?\d+)_(\d+)$'))
    application.add_handler(CallbackQueryHandler(edit_keyboards, pattern="^channeloffers_editkeyboards_.+$"))
    application.add_handler(CallbackQueryHandler(edit_keyboard, pattern=r'^channeloffers_editkeyboard_(-?\d+)_(\d+)$'))
    application.add_handler(CallbackQueryHandler(delete_keyboard,         pattern=r'^channeloffers_deletekeyboard_-?\d+_\d+$'))
    application.add_handler(CallbackQueryHandler(confirm_delete_keyboard, pattern=r'^channeloffers_confirmdeletekeyboard_-?\d+_\d+$'))

    application.add_handler(CallbackQueryHandler(delete_preview, pattern="^delete_preview$"))

    

    application.run_polling(allowed_updates=Update.ALL_TYPES)

if __name__ == "__main__":
    start_telegram_bot()
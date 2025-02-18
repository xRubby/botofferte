#handlers.py

import logging
import time

from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import ContextTypes

from telegram_bot.keyboards.main_menu import create_main_menu

from telegram_bot.keyboards.search_product.search_product_menu import *

from telegram_bot.keyboards.channel_offers.channel_offers_addLink import *
from telegram_bot.keyboards.channel_offers.channel_offers_affiliateID import *
from telegram_bot.keyboards.channel_offers.channel_offers_editChannelMenu import *
from telegram_bot.keyboards.channel_offers.channel_offers_main import *
from telegram_bot.keyboards.channel_offers.channel_offers_showLink import *
from telegram_bot.keyboards.channel_offers.channel_offers_layout import *
from telegram_bot.keyboards.channel_offers.channel_offers_adminpanel import *

from telegram_bot.keyboards.settings.settings_menu import *
from telegram_bot.keyboards.settings.admin_bot_menu.admin_settings import *

from database.DAO.UtenteDAO import UtenteDAO
from database.DAO.CanaleDAO import CanaleDAO
from database.DAO.GestisceDAO import GestisceDAO
from database.DAO.LayoutDAO import LayoutDAO

from utils.generate_license import *

from telegram_bot.functions.send_message import search_offer


async def start(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    query = update.callback_query
    if query:
        await query.answer()

    user = update.effective_user

    with UtenteDAO() as utente_dao:
        if not utente_dao.get(user.id):
            utente_dao.insert(user.id, user.first_name)

    await create_main_menu(update, context)

    

async def doNothing(query):
    await query.answer()


async def button_handler(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    query = update.callback_query

    user_id = update.effective_user.id 

    if user_id not in context.user_data:
        context.user_data[user_id] = {}

    if 'message_id' not in context.user_data[user_id]:
        context.user_data[user_id] = {'message_id': query.message.message_id} 
    
    if 'awaiting_input' in context.user_data[user_id]:
        context.user_data[user_id]['awaiting_input'] = False

    if 'awaiting_license' in context.user_data[user_id]:
        context.user_data[user_id]['awaiting_license'] = False

    if 'adding_channel' in context.user_data[user_id]:
        context.user_data[user_id]['adding_channel'] = False
    
    if 'awaiting_link' in context.user_data[user_id]:
        context.user_data[user_id]['awaiting_link'] = False
    
    if 'awaiting_affiliate_id' in context.user_data[user_id]:
        context.user_data[user_id]['awaiting_affiliate_id'] = False

    if 'awaiting_newmessage_layout' in context.user_data[user_id]:
        context.user_data[user_id]['awaiting_newmessage_layout'] = False

        

    data_parts = query.data.split("_")
    
    license_code = data_parts[1] if data_parts[0] == 'views' or data_parts[0] == "confirmdelete" and len(data_parts) >= 2 else None

    channel_id = data_parts[2] if data_parts[0] == 'edit' or data_parts[0]=="channel" or data_parts[0] == "delete" and len(data_parts) >= 3 else None

    layout_id = data_parts[3] if len(data_parts) >= 4 and data_parts[1] in ['activatelayout', 'editlayout', 'deletelayout', 'editmessagelayout']  else None

    if data_parts[0] == 'publish' or data_parts[0] == 'remove' or data_parts[0] == 'prev' or data_parts[0] == 'next' and len(data_parts) >=3:
        channel_id=data_parts[1]
        list_index=data_parts[2]
    else:
        list_index=None

    actions = {
        'back_to_main': lambda: start(update, context),

        'search_product': lambda: search_product(query, context, user_id),
        'offerte_canale': lambda: handle_offers(query, context, user_id),
        'settings': lambda: settings_menu(user_id,query),
        
        'admin_settings': lambda: admin_menu(query, context, user_id),
        'generate_license': lambda: generate_new_license(query, context, user_id),
        'view_licenses': lambda: view_licenses(query),
        f'views_{license_code}': lambda: view_license_details(query, license_code),
        f'confirmdelete_{license_code}': lambda: delete_license_confirm(query, license_code),
        
        'add_channel': lambda: add_channel_start(query, update, context),
        'add_license': lambda: add_license_start(query,context,user_id),
        f'edit_channel_{channel_id}': lambda: edit_channel(query, context, user_id, channel_id),
        f'delete_channel_{channel_id}': lambda: delete_channel(query, channel_id, user_id),
        f'channel_link_{channel_id}': lambda: insert_link(query,context,user_id,channel_id),
        f'channel_listlinks_{channel_id}': lambda: show_links(query,context,channel_id),

        f'channel_affiliateid_{channel_id}': lambda: insert_affiliate_id(query,context,user_id,channel_id),
        f'channel_removeaffiliateid_{channel_id}': lambda: remove_affiliate_id(query, context, channel_id, user_id),

        
        f'publish_{channel_id}_{list_index}': lambda: publish_message(query, update, context, channel_id, int(list_index)),
        f'remove_{channel_id}_{list_index}': lambda: remove_product(query, context, channel_id, int(list_index)),
        f'prev_{channel_id}_{list_index}': lambda: navigate_links(query, context, channel_id, 'prev', int(list_index)),
        f'next_{channel_id}_{list_index}': lambda: navigate_links(query, context, channel_id, 'next', int(list_index)),

        f'channel_layout_{channel_id}': lambda: layout_menu(query, context, channel_id, user_id),
        f"channel_addlayout_{channel_id}": lambda: add_layout(query, context, channel_id, user_id),
        f'channel_showlayouts_{channel_id}': lambda: select_layouts(query, channel_id),
        f'channel_activatelayout_{channel_id}_{layout_id}': lambda: activate_layout(query, layout_id),
        f"channel_editlayouts_{channel_id}": lambda: edit_layouts(query, channel_id),
        f"channel_editlayout_{channel_id}_{layout_id}": lambda: edit_layout(query, context, user_id, layout_id),
        f"channel_editmessagelayout_{channel_id}_{layout_id}": lambda: edit_layout_message(query, context, user_id, layout_id, channel_id),
        f"channel_deletelayout_{channel_id}_{layout_id}": lambda: delete_layout(query, layout_id, channel_id),
        f'channel_resetlayout_{channel_id}': lambda: reset_layout(query, channel_id),

        f'channel_adminpanel_{channel_id}': lambda: admin_panel(query, context, channel_id, user_id),
        f'channel_adminaffiliateid_{channel_id}': lambda: admin_edit_affiliateid(query, context, channel_id, user_id),
        f'channel_adminremoveaffiliateid_{channel_id}': lambda: admin_remove_affiliateid(query, context, channel_id, user_id),

        'none': lambda: doNothing(query)
    }

    #try:
    action = actions.get(query.data, lambda: None)
    await action()
    #except Exception as e:
    #    logging.error(f"Errone nell'hanling dei bottoni: {e}")

async def handle_input(update: Update, context: ContextTypes.DEFAULT_TYPE):
    
    user_id = update.effective_user.id

    if user_id not in context.user_data:
        context.user_data[user_id] = {}

    message_id = context.user_data.get(user_id, {}).get('message_id')
    
    
    if context.user_data.get(user_id, {}).get('awaiting_input'):
        keyword = update.message.text
        await update.message.delete()
        await context.bot.edit_message_text(chat_id=update.effective_chat.id,
                message_id=message_id,
                text=f"<b>🔍 Cerca prodotto</b>"
                    "\n\n"
                    "Sto elaborando il tuo link...",
                parse_mode="HTML")
        
        time.sleep(2)

        from telegram_bot.functions.send_message import search_and_send_offer
        await search_and_send_offer(update, context, keyword)
        context.user_data[user_id]['awaiting_input'] = False
        
    elif context.user_data.get(user_id, {}).get('awaiting_link'):
        link = update.message.text
        await update.message.delete()

        channel_id = context.user_data[user_id].get('channel_id')

        
        await context.bot.edit_message_text(chat_id=update.effective_chat.id,
                message_id=message_id,
                text=f"Sto elaborando il tuo link...")
        
        try:
            await search_offer(update, context, channel_id, link)

            keyboard=[
            [InlineKeyboardButton("Lista link", callback_data=f'channel_listlinks_{channel_id}')],
            [InlineKeyboardButton("⬅️ Indietro", callback_data=f'edit_channel_{channel_id}')]
            ]

            reply_markup=InlineKeyboardMarkup(keyboard)

            time.sleep(2)

            await context.bot.edit_message_text(chat_id=update.effective_chat.id,
                message_id=message_id,
                text=f"Link aggiunto con successo.", 
                reply_markup=reply_markup)
            
        except Exception as e:
            logging.error(e)

        context.user_data[user_id]['awaiting_link'] = False

    elif context.user_data.get(user_id, {}).get('awaiting_license'):
        
        license_code = update.message.text.strip()
        await update.message.delete()


        keyboard = [
        [InlineKeyboardButton("⬅️ Indietro", callback_data=f'offerte_canale')]
        ]
        reply_markup = InlineKeyboardMarkup(keyboard)

        with LicenzaDAO() as licenza_dao:
            license_details = licenza_dao.get(license_code)
            if license_details:
                with CanaleDAO() as canale_dao, GestisceDAO() as gestisce_dao:
                    if(not canale_dao.is_license_used(license_code)):

                        channel_data = context.user_data[user_id].get('channel_data')
                        if channel_data:
                            channel_id = channel_data['id']
                            channel_name = channel_data['name']

                            canale_dao.insert(channel_id, channel_name, "", license_code)
                            gestisce_dao.insert(user_id, channel_id, "", 1)

                            licenza_dao.activate_licenza(license_code)

                            await context.bot.edit_message_text(
                                chat_id=update.effective_chat.id,
                                message_id=message_id,
                                text=f"Canale '{channel_name}' aggiunto con la licenza '{license_code}'!",
                                reply_markup=reply_markup
                            )
                        else:
                            await context.bot.edit_message_text(
                                chat_id=update.effective_chat.id,
                                message_id=message_id,
                                text="Errore: nessun canale da associare alla licenza.",
                                reply_markup=reply_markup
                            )
                    
                    else:
                        await context.bot.edit_message_text(
                            chat_id=update.effective_chat.id,
                            message_id=message_id,
                            text="Licenza già in uso. Riprova.",
                            reply_markup=reply_markup)
            else:
            
                await context.bot.edit_message_text(
                    chat_id=update.effective_chat.id,
                    message_id=message_id,
                    text="Licenza non valida. Riprova.",
                    reply_markup=reply_markup)
                

        context.user_data[user_id]['awaiting_license'] = None
        context.user_data[user_id]['channel_data'] = None


    elif context.user_data[user_id].get('adding_channel'):

        keyboard = [
        [InlineKeyboardButton("⬅️ Indietro", callback_data=f'offerte_canale')]
        ]
        reply_markup = InlineKeyboardMarkup(keyboard)

        if update.message and update.message.forward_origin:
            original_message = update.message.forward_origin
            original_chat = original_message.chat
        
            if original_chat.type == 'channel':
                channel_id = original_chat.id 
                channel_name = original_chat.title

                try:
                    administrators = await context.bot.get_chat_administrators(channel_id)
                    is_admin = any(admin.user.id == user_id for admin in administrators)

                    if is_admin:
                        
                        context.user_data[user_id]['channel_data'] = {'id': channel_id, 'name': channel_name}
                        context.user_data[user_id]['awaiting_license'] = True


                        await context.bot.edit_message_text(
                            chat_id=update.effective_chat.id,
                            message_id=message_id,
                            text=f"Ora invia la licenza per completare il processo.",
                            reply_markup=reply_markup)
                    else:
                        await context.bot.edit_message_text(
                            chat_id=update.effective_chat.id,
                            message_id=message_id,
                            text="Errore: devi essere amministratore del canale!",
                            reply_markup=reply_markup)
                except Exception as e:
                    await context.bot.edit_message_text(
                        chat_id=update.effective_chat.id,
                        message_id=message_id,
                        text=f"Errore nel verificare i permessi: {str(e)}",
                        reply_markup=reply_markup)
            else:
                await context.bot.edit_message_text(
                    chat_id=update.effective_chat.id,
                    message_id=message_id,
                    text="Errore: il messaggio non proviene da un canale valido.",
                    reply_markup=reply_markup)
        else:
            await context.bot.edit_message_text(
                chat_id=update.effective_chat.id,
                message_id=message_id,
                text="Errore: devi inoltrare un messaggio da un canale.",
                reply_markup=reply_markup)
        await update.message.delete()
        context.user_data[user_id]['adding_channel'] = False 

    elif context.user_data[user_id].get('awaiting_name_layout'):
        name_layout = update.message.text
        channel_id = context.user_data[user_id].get('channel_id')

        await update.message.delete()


        context.user_data[user_id]['awaiting_name_layout'] = False

        context.user_data[user_id]['name_layout'] = name_layout
        context.user_data[user_id]['awaiting_message_layout'] = True

        keyboard = [
            [InlineKeyboardButton("⬅️ Indietro", callback_data=f'channel_layout_{channel_id}')]
        ]  
        reply_markup = InlineKeyboardMarkup(keyboard)

        await context.bot.edit_message_text(
            chat_id=update.effective_chat.id,
            message_id=message_id,
            text="Crea Layout\n\n"
             "Tag disponibili:\n"
             "- <code>{titolo}</code>\n"
             "- <code>{prezzo_nuovo}</code>\n"
             "- <code>{prezzo_vecchio}</code>\n"
             "- <code>{sconto}</code>\n"
             "- <code>{link}</code>\n"
             "- <code>{linkfull}</code>\n"
             "- <code>{valuta}</code>\n"
             "- <code>{spedito}</code>\n"
             "- <code>{prime}</code>\n"
             "- <code>{preorder}</code>\n"
             "- <code>{preorderdate}</code>\n"
             "- <code>{warehouse}</code>\n"
             "- <code>{condition}</code>\n"
             "- <code>{conditioncomm}</code>\n"
             "- <code>{minimo}</code>\n\n"
             "TAG Speciale:\n"
            "I TAG speciali {_ e _} permettono di collegare la Frase compresa tra i due TAG Speciali al TAG Post" 
            "inserito all'interno dei due tag speciali. In caso in cui il TAG Post sia nullo (ovvero manca" 
            "l'informazione su Amazon) la frase non viene visualizzata. Inoltre è possibile inserire più TAG Post," 
            "tra i due TAG Speciali, in caso manca UNO dei TAG Post la frase non viene visualizzata.",
            parse_mode="HTML",
            reply_markup=reply_markup
        )

    elif context.user_data[user_id].get('awaiting_message_layout'):
        message_layout = update.message.text
        channel_id = context.user_data[user_id].get('channel_id')
        name_layout = context.user_data[user_id].get('name_layout')

        await update.message.delete()

        with LayoutDAO() as layout_dao:
            layout_dao.insert(name_layout, message_layout, 0, channel_id)

        keyboard = [
            [InlineKeyboardButton("⬅️ Indietro", callback_data=f'channel_layout_{channel_id}')]
        ]
        reply_markup = InlineKeyboardMarkup(keyboard)

        await context.bot.edit_message_text(
                            chat_id=update.effective_chat.id,
                            message_id=message_id,
                            text=f"Layout aggiunto con successo!",
                            reply_markup=reply_markup)

        context.user_data[user_id]['awaiting_message_layout'] = False
    
    elif context.user_data[user_id].get('awaiting_newmessage_layout'):
        new_message_layout = update.message.text
        channel_id = context.user_data[user_id].get('channel_id')
        layout_id = context.user_data[user_id].get('layout_id')

        await update.message.delete()

        with LayoutDAO() as layout_dao:
            layout_dao.update_messaggio(new_message_layout, layout_id)
        
        keyboard = [
            [InlineKeyboardButton("⬅️ Indietro", callback_data=f'channel_editlayout_{channel_id}_{layout_id}')]
        ]
        reply_markup = InlineKeyboardMarkup(keyboard)
        
        await context.bot.edit_message_text(
                            chat_id=update.effective_chat.id,
                            message_id=message_id,
                            text=f"Layout modificato con successo!",
                            reply_markup=reply_markup)

        context.user_data[user_id]['awaiting_newmessage_layout'] = False

    elif context.user_data[user_id].get('awaiting_admin_affiliateid'):
        affiliate_id = update.message.text
        channel_id = context.user_data[user_id].get('channel_id')

        await update.message.delete()

        with CanaleDAO() as canale_dao:
            canale_dao.update_id_affiliato(channel_id, affiliate_id)
        
        keyboard = [
            [InlineKeyboardButton("⬅️ Indietro", callback_data=f'channel_adminpanel_{channel_id}')]
        ]
        reply_markup = InlineKeyboardMarkup(keyboard)
        
        await context.bot.edit_message_text(
                            chat_id=update.effective_chat.id,
                            message_id=message_id,
                            text=f"ID affiliato modificato correttamente!",
                            reply_markup=reply_markup)

        context.user_data[user_id]['awaiting_admin_affiliateid'] = False

    elif context.user_data[user_id].get('awaiting_affiliate_id'):
        affiliate_id = update.message.text
        channel_id = context.user_data[user_id].get('channel_id')

        await update.message.delete()

        with GestisceDAO() as gestisce_dao:
            gestisce_dao.update_id_affiliato(user_id, channel_id, affiliate_id)
        
        keyboard = [
            [InlineKeyboardButton("⬅️ Indietro", callback_data=f'edit_channel_{channel_id}')]
        ]
        reply_markup = InlineKeyboardMarkup(keyboard)
        
        await context.bot.edit_message_text(
                            chat_id=update.effective_chat.id,
                            message_id=message_id,
                            text=f"ID affiliato modificato correttamente!",
                            reply_markup=reply_markup)

        context.user_data[user_id]['awaiting_affiliate_id'] = False

    
    elif context.user_data[user_id].get('awaiting_tipo_license'):
        tipo_licenza = update.message.text
        channel_id = context.user_data[user_id].get('channel_id')

        await update.message.delete()

        if(calcola_tipo_scadenza(tipo_licenza)):

            codice_licenza = generate_license()
            with LicenzaDAO() as licenza_dao:
                licenza_dao.insert(codice_licenza, tipo_licenza)

            text = f"Licenza con codice {codice_licenza} aggiunta correttamente!"
        else:
            text = f"Il tipo della licenza è errato!"

        
        keyboard = [
            [InlineKeyboardButton("⬅️ Indietro", callback_data=f'admin_settings')]
        ]
        reply_markup = InlineKeyboardMarkup(keyboard)
        
        await context.bot.edit_message_text(
                            chat_id=update.effective_chat.id,
                            message_id=message_id,
                            text=text,
                            reply_markup=reply_markup)

        context.user_data[user_id]['awaiting_tipo_license'] = False

    elif context.user_data[user_id].get('awaiting_newlicense'):
        new_licenza = update.message.text
        channel_id = context.user_data[user_id].get('channel_id')

        await update.message.delete()

        with LicenzaDAO() as licenza_dao, CanaleDAO() as canale_dao:
            licenza = licenza_dao.get(new_licenza)

            if licenza:
                if not canale_dao.is_license_used(new_licenza):
                    canale_dao.update_codice_licenza(channel_id, new_licenza)
                    licenza_dao.activate_licenza(new_licenza)
                    text = "Licenza aggiornata con successo!"
                else:
                    text = "La licenza è già in uso su un altro canale."
            else:
                text = "La licenza non esiste."
                
        
        keyboard = [
            [InlineKeyboardButton("⬅️ Indietro", callback_data=f'offerte_canale')]
        ]
        reply_markup = InlineKeyboardMarkup(keyboard)
        
        await context.bot.edit_message_text(
                            chat_id=update.effective_chat.id,
                            message_id=message_id,
                            text=text,
                            reply_markup=reply_markup)

        context.user_data[user_id]['awaiting_newlicense'] = False
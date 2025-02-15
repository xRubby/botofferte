#handlers.py

import logging
from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import ContextTypes

from telegram_bot.messages.messages_it import getTemplateMessage
from telegram_bot.functions.send_message import search_offer

from telegram_bot.keyboards.main_menu import create_main_menu

from telegram_bot.keyboards.search_product.search_product_menu import *

from telegram_bot.keyboards.channel_offers.channel_offers_addLink import *
from telegram_bot.keyboards.channel_offers.channel_offers_affiliateID import *
from telegram_bot.keyboards.channel_offers.channel_offers_editChannelMenu import *
from telegram_bot.keyboards.channel_offers.channel_offers_main import *
from telegram_bot.keyboards.channel_offers.channel_offers_showLink import *
from telegram_bot.keyboards.channel_offers.channel_offers_layout import *

from telegram_bot.keyboards.settings.settings_menu import *
from telegram_bot.keyboards.settings.admin_bot_menu.admin_settings import *

from database.Entity.Utente import Utente

from database.DAO.UtenteDAO import UtenteDAO
from database.DAO.LicenzaDAO import LicenzaDAO
from database.DAO.CanaleDAO import CanaleDAO
from database.DAO.LinkDAO import add_link_to_channel



async def start(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    
    user = update.effective_user

    if not UtenteDAO().get(user.id):
        UtenteDAO().insert(Utente(user.id, user.first_name, 0))

    await create_main_menu(update, context)

    




async def button_handler(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    query = update.callback_query
    await query.answer()

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

    if data_parts[0] == 'publish' or data_parts[0] == 'remove' or data_parts[0] == 'prev' or data_parts[0] == 'next' and len(data_parts) >=3:
        channel_id=data_parts[1]
        list_index=data_parts[2]
    else:
        list_index=None

    actions = {
        'back_to_main': lambda: start(update, context),

        'search_product': lambda: search_product(query, context, user_id),
        'offerte_canale': lambda: handle_offers(query, user_id),
        'settings': lambda: settings_menu(user_id,query),
        
        'admin_settings': lambda: admin_menu(query),
        'generate_license': lambda: generate_new_license(query),
        'view_licenses': lambda: view_licenses(query),
        f'views_{license_code}': lambda: view_license_details(query, license_code),
        f'confirmdelete_{license_code}': lambda: delete_license_confirm(query, license_code),
        
        'add_channel': lambda: add_channel_start(query, update, context),
        'add_license': lambda: add_license_start(query,context,user_id),
        f'edit_channel_{channel_id}': lambda: edit_channel(query, channel_id),
        f'delete_channel_{channel_id}': lambda: delete_channel(query, channel_id, user_id),
        f'channel_link_{channel_id}': lambda: insert_link(query,context,user_id,channel_id),
        f'channel_listlinks_{channel_id}': lambda: show_links(query,context,channel_id),
        f'channel_affiliateid_{channel_id}': lambda: insert_affiliate_id(query,context,user_id,channel_id),

        
        f'publish_{channel_id}_{list_index}': lambda: publish_message(query, update, context, channel_id, int(list_index)),
        f'remove_{channel_id}_{list_index}': lambda: remove_product(query, context, channel_id, int(list_index)),
        f'prev_{channel_id}_{list_index}': lambda: navigate_links(query, context, channel_id, 'prev', int(list_index)),
        f'next_{channel_id}_{list_index}': lambda: navigate_links(query, context, channel_id, 'next', int(list_index)),

        f'channel_layout_{channel_id}': lambda: layout_menu(query, channel_id),
        f'channel_editmessage_{channel_id}': lambda: edit_message(query, context, user_id, channel_id),
        f'channel_resetlayout_{channel_id}': lambda: reset_layout(query, channel_id)
    }

    
    action = actions.get(query.data, lambda: None)
    await action()

async def handle_input(update: Update, context: ContextTypes.DEFAULT_TYPE):
    
    user_id = update.effective_user.id

    message_id = context.user_data.get(user_id, {}).get('message_id')
    
    
    if context.user_data.get(user_id, {}).get('awaiting_input'):
        keyword = update.message.text
        await update.message.delete()
        from telegram_bot.functions.send_message import search_and_send_offer
        await search_and_send_offer(update, context, keyword)
        context.user_data[user_id]['awaiting_input'] = False
        


    elif context.user_data.get(user_id, {}).get('awaiting_license'):
        
        license_code = update.message.text.strip()
        await update.message.delete()


        keyboard = [
        [InlineKeyboardButton("⬅️ Indietro", callback_data=f'offerte_canale')]
        ]
        reply_markup = InlineKeyboardMarkup(keyboard)

        canale_dao = CanaleDAO()

        
        license_details = LicenzaDAO().get(license_code)
        if license_details:
            if(not canale_dao.is_license_used(license_code)):

                channel_data = context.user_data[user_id].get('channel_data')
                if channel_data:
                    channel_id = channel_data['id']
                    channel_name = channel_data['name']

                    canale_dao.insert(channel_id, channel_name, "", license_code, user_id)

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
            
        canale_dao.close()

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


    elif context.user_data[user_id].get('awaiting_link'):
        link = update.message.text
        await update.message.delete()
        channel_id = context.user_data[user_id].get('channel_id')

        try:
            messaggio = await search_offer(update, context, channel_id, link)
            add_link_to_channel(channel_id, link, messaggio)

            keyboard=[
            [InlineKeyboardButton("Lista link", callback_data=f'channel_listlinks_{channel_id}')],
            [InlineKeyboardButton("⬅️ Indietro", callback_data=f'edit_channel_{channel_id}')]
            ]

            reply_markup=InlineKeyboardMarkup(keyboard)

            await context.bot.edit_message_text(chat_id=update.effective_chat.id,
                message_id=message_id,
                text=f"Link aggiunto con successo: {link}", 
                reply_markup=reply_markup)
            
        except Exception as e:
            logging.error(e)

        context.user_data[user_id]['awaiting_link'] = False

        


    elif context.user_data[user_id].get('awaiting_affiliate_id'):
        affiliate_id = update.message.text
        await update.message.delete()
        channel_id = context.user_data[user_id].get('channel_id')

        set_affiliate_id(channel_id, affiliate_id)

        keyboard = [
            [InlineKeyboardButton("⬅️ Indietro", callback_data=f'edit_channel_{channel_id}')]
        ]
        reply_markup = InlineKeyboardMarkup(keyboard)

        context.user_data[user_id]['awaiting_affiliate_id'] = False

        await context.bot.edit_message_text(
                            chat_id=update.effective_chat.id,
                            message_id=message_id,
                            text=f"ID affiliato aggiunto con successo: {affiliate_id}",
                            reply_markup=reply_markup)
    
    elif context.user_data[user_id].get('awaiting_newmessage_layout'):
        new_message = update.message.text
        channel_id = context.user_data[user_id].get('channel_id')

        await update.message.delete()

        set_message_template(channel_id, new_message)

        keyboard = [
            [InlineKeyboardButton("⬅️ Indietro", callback_data=f'channel_layout_{channel_id}')]
        ]
        reply_markup = InlineKeyboardMarkup(keyboard)

        await context.bot.edit_message_text(
                            chat_id=update.effective_chat.id,
                            message_id=message_id,
                            text=f"Messaggio modificato con successo!",
                            reply_markup=reply_markup)

        context.user_data[user_id]['awaiting_affiliate_id'] = False
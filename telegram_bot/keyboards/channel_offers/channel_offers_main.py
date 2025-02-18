from telegram import *
from telegram.ext import *

from database.Entity.Canale import Canale

from database.DAO.CanaleDAO import CanaleDAO


async def handle_offers(query: CallbackQuery, context: ContextTypes.DEFAULT_TYPE, user_id: int):
        
        if context.user_data[user_id].get('awaiting_newlicense'):
            context.user_data[user_id]['awaiting_newlicense'] = False
        
        with CanaleDAO() as canale_dao:
            channels = canale_dao.get_user_channels(user_id)

        keyboard = []

        if not channels:
            text = "Non hai canali. Aggiungi un canale per iniziare!"
        else:
            text = "I tuoi canali:\n"
            for channel in channels:
                channel_id = channel.canale_id
                channel_name = channel.nome_canale
                text += f"\n- {channel_name}"

                keyboard.append([
                    InlineKeyboardButton(
                        channel_name, 
                        callback_data=f'edit_channel_{channel_id}'
                    )
                ])

        keyboard.append([InlineKeyboardButton("Aggiungi Canale", callback_data='add_channel')]),
        keyboard.append([InlineKeyboardButton("⬅️ Indietro", callback_data='back_to_main')])
        reply_markup = InlineKeyboardMarkup(keyboard)

        await query.edit_message_text(text=text, reply_markup=reply_markup)

        await query.answer()





async def add_license_start(query, context, user_id):
   
    keyboard = [
            [InlineKeyboardButton("⬅️ Indietro", callback_data='offerte_canale')]
        ]

    reply_markup = InlineKeyboardMarkup(keyboard)


    await query.edit_message_text(
        text="Inserisci la tua licenza:",
        reply_markup=reply_markup
    )

    messageid=query.message.id
    context.user_data[user_id] = {'awaiting_license': True, 'message_id': messageid}

    await query.answer()


async def add_channel_start(query,update,context):

    user_id = update.effective_user.id
    message_id=query.message.id

    keyboard = [
        [InlineKeyboardButton("⬅️ Indietro", callback_data='offerte_canale')]
    ]
    reply_markup = InlineKeyboardMarkup(keyboard)

    context.user_data[user_id] = {'adding_channel': True, 'message_id': message_id}
    
    await context.bot.edit_message_text(
                    chat_id=update.effective_chat.id,
                    message_id=message_id,
                    text="Inoltra un messaggio dal canale che vuoi aggiungere. "
                    "Il bot aspetterà che tu invii il messaggio dal canale corretto.",
                    reply_markup=reply_markup
                )
    
    await query.answer()
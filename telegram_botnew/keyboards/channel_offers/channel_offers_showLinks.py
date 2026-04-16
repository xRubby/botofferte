from telegram import InlineKeyboardButton, InlineKeyboardMarkup, Update
from telegram.ext import ContextTypes

from database.DAO.PubblicaDAO import PubblicaDAO
from utils.channel_offers_utils import check_channel_id



async def insert_link_entry(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()

    channel_id = check_channel_id(query, context)

    links = context.user_data.get("links")

    if not links:
        with PubblicaDAO() as pubblicaDAO:
            links = pubblicaDAO.get_channel_link_non_pubblicati(channel_id)
            context.user_data["links"] = links

    if not links:
        await query.edit_message_text(
            text="Non ci sono link nel database.",
            reply_markup=InlineKeyboardMarkup([[
                InlineKeyboardButton("🔙 Torna indietro", callback_data=f'channeloffers_info_{channel_id}')
            ]])
        )
        return
    
    current_index = int(query.data.split("_")[-2])
    link = links[current_index]

    text = f"Link corrente: {current_index+1}\n\n{link.messaggio}"

    keyboard = []

    if len(links) > 1:
        keyboard.extend([
            [InlineKeyboardButton("⏮️", callback_data=f'channeloffers_link_0_{channel_id}' if current_index != 0 else f'none'),
            InlineKeyboardButton("⬅️", callback_data=f'channeloffers_link_{current_index + 1}_{channel_id}'),
            InlineKeyboardButton("➡️", callback_data=f'channeloffers_link_{current_index - 1}_{channel_id}_{current_index}'),
            InlineKeyboardButton("⏭️", callback_data=f'channeloffers_link_{len(links)-1}_{channel_id}' if current_index != len(links)-1 else f'none')],
        ]
        )

    keyboard.extend( [
        [InlineKeyboardButton("Pubblica messaggio", callback_data=f'publish_{channel_id}_{link.id}')],
        [InlineKeyboardButton("Rimuovi prodotto", callback_data=f'remove_{channel_id}_{link.id}')]
    ])

    

    keyboard.append([InlineKeyboardButton("🔙 Indietro", callback_data=f'channeloffers_info_{channel_id}')])

    reply_markup = InlineKeyboardMarkup(keyboard)

    await query.edit_message_text(text=text, reply_markup=reply_markup, parse_mode='HTML')



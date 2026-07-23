from telegram import CallbackQuery, Update
from telegram.ext import ContextTypes

def check_channel_id(query: CallbackQuery, context: ContextTypes.DEFAULT_TYPE):
    channel_id = context.user_data.get("channel_id", None)
    if not channel_id:
        channel_id = int(query.data.split("_")[-1])
        context.user_data['channel_id'] = channel_id

    return str(channel_id)

async def delete_preview(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()

    try:
        await query.message.delete()
    except Exception as e:
        print(f"Errore eliminazione preview: {e}")

    context.user_data.pop("preview_message_id", None)

async def delete_preview_message(chat_id, context):
    preview_id = context.user_data.get("preview_message_id")

    if preview_id:
        try:
            await context.bot.delete_message(
                chat_id=chat_id,
                message_id=preview_id
            )
        except Exception:
            # magari il messaggio è già stato eliminato
            pass

        context.user_data.pop("preview_message_id", None)
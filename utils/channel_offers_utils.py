from telegram import CallbackQuery
from telegram.ext import ContextTypes

def check_channel_id(query: CallbackQuery, context: ContextTypes.DEFAULT_TYPE):
    channel_id = context.user_data.get("channel_id", None)
    if not channel_id:
        channel_id = int(query.data.split("_")[-1])
        context.user_data['channel_id'] = channel_id

    return channel_id
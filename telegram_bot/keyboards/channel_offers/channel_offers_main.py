from telegram import InlineKeyboardButton, InlineKeyboardMarkup, Update
from telegram.ext import CallbackQueryHandler, ContextTypes, ConversationHandler, MessageHandler, filters

from database.session import SessionLocal
from enums.StatoLicenza import StatoLicenza
from models.canale import Canale
from models.gestisce import Gestisce
from services.canale_service import CanaleService
from services.gestisce_service import GestisceService
from services.licenza_service import LicenzaService

ATTESA_FORWARD  = 1
ATTESA_LICENZA  = 2

BTN_INDIETRO = [[InlineKeyboardButton("⬅️ Indietro", callback_data="channeloffers_main")]]

async def channeloffers_main(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()
    telegram_id = update.effective_user.id

    context.user_data.pop("channel_id", None)

    with SessionLocal() as session:
        canale_service = CanaleService(session)
        canali = canale_service.ottieni_canale_utente(telegram_id)


    keyboard = []

    if not canali:
        text = "Non hai canali. Aggiungi un canale per iniziare!"
    else:
        text = "📢 <b>I tuoi canali</b>\n\nScegli un canale per gestirlo 👇\n"
        for canale in canali:
            canale_id = canale.canale_id
            nome_canale = canale.nome_canale
            text += f"\n- {nome_canale}"

            keyboard.append([
                InlineKeyboardButton(
                    nome_canale, 
                    callback_data=f'channeloffers_info_{canale_id}'
                )
            ])

    keyboard.append([InlineKeyboardButton("➕ Aggiungi Canale", callback_data='channeloffers_addchannel')]),
    keyboard.append([InlineKeyboardButton("⬅️ Indietro", callback_data='back_to_main')])
    reply_markup = InlineKeyboardMarkup(keyboard)

    await query.edit_message_text(text=text, reply_markup=reply_markup, parse_mode="HTML")

# ── Entry point ───────────────────────────────────────────────────────────────

async def channeloffers_addchannel(update: Update, ctx: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()

    ctx.user_data['add_channel_message_id'] = query.message.message_id
    ctx.user_data['add_channel_chat_id']    = query.message.chat_id

    await query.edit_message_text(
        text=(
            "📢 <b>Aggiungi un canale</b>\n\n"
            "Inoltra un messaggio dal canale che vuoi aggiungere.\n\n"
            "<i>Devi essere amministratore del canale.</i>"
        ),
        parse_mode="HTML",
        reply_markup=InlineKeyboardMarkup(BTN_INDIETRO)
    )
    return ATTESA_FORWARD


# ── Stato 1: riceve il forward ────────────────────────────────────────────────

async def received_forward(update: Update, ctx: ContextTypes.DEFAULT_TYPE):
    await update.message.delete()

    chat_id    = ctx.user_data['add_channel_chat_id']
    message_id = ctx.user_data['add_channel_message_id']
    user_id    = update.effective_user.id

    reply_markup = InlineKeyboardMarkup(BTN_INDIETRO)

    if not (update.message and update.message.forward_origin):
        await ctx.bot.edit_message_text(
            chat_id=chat_id, message_id=message_id,
            text="❌ Devi inoltrare un messaggio da un canale.",
            parse_mode="HTML", reply_markup=reply_markup
        )
        return ATTESA_FORWARD

    origin = update.message.forward_origin
    if not hasattr(origin, 'chat') or origin.chat.type != 'channel':
        await ctx.bot.edit_message_text(
            chat_id=chat_id, message_id=message_id,
            text="❌ Il messaggio non proviene da un canale valido.",
            parse_mode="HTML", reply_markup=reply_markup
        )
        return ATTESA_FORWARD

    channel_id   = origin.chat.id
    channel_name = origin.chat.title

    with SessionLocal() as session:
        canale_service = CanaleService(session)
        esistente = canale_service.ottieni_canale(str(channel_id))

    if esistente:
        await ctx.bot.edit_message_text(
            chat_id=chat_id, message_id=message_id,
            text=f"❌ Il canale <b>{channel_name}</b> è già registrato nel sistema.",
            parse_mode="HTML", reply_markup=reply_markup
        )
        return ATTESA_FORWARD

    try:
        administrators = await ctx.bot.get_chat_administrators(channel_id)
        is_admin = any(admin.user.id == user_id for admin in administrators)
    except Exception as e:
        await ctx.bot.edit_message_text(
            chat_id=chat_id, message_id=message_id,
            text=f"❌ Errore nel verificare i permessi: {e}",
            parse_mode="HTML", reply_markup=reply_markup
        )
        return ATTESA_FORWARD

    if not is_admin:
        await ctx.bot.edit_message_text(
            chat_id=chat_id, message_id=message_id,
            text="❌ Devi essere amministratore del canale per aggiungerlo.",
            parse_mode="HTML", reply_markup=reply_markup
        )
        return ATTESA_FORWARD

    ctx.user_data['channel_data'] = {'id': channel_id, 'name': channel_name}

    await ctx.bot.edit_message_text(
        chat_id=chat_id, message_id=message_id,
        text=(
            f"✅ Canale <b>{channel_name}</b> verificato!\n\n"
            f"Ora invia il codice licenza per completare l'attivazione."
        ),
        parse_mode="HTML",
        reply_markup=reply_markup
    )
    return ATTESA_LICENZA


# ── Stato 2: riceve la licenza ────────────────────────────────────────────────

async def received_licenza(update: Update, ctx: ContextTypes.DEFAULT_TYPE):
    await update.message.delete()

    chat_id      = ctx.user_data['add_channel_chat_id']
    message_id   = ctx.user_data['add_channel_message_id']
    channel_data = ctx.user_data.get('channel_data', {})
    channel_id   = str(channel_data.get('id'))
    channel_name = channel_data.get('name')
    codice       = update.message.text.strip()

    reply_markup = InlineKeyboardMarkup(BTN_INDIETRO)

    with SessionLocal() as session:
        licenza_service = LicenzaService(session)
        licenza = licenza_service.ottieni_licenza(codice)

        stato_licenza = None
        if licenza:
            stato_licenza = licenza_service.get_stato(licenza)

        if stato_licenza not in(StatoLicenza.ATTIVA, StatoLicenza.NON_ATTIVATA, StatoLicenza.NESSUN_CANALE) or licenza.canale:
                try:
                    await ctx.bot.edit_message_text(
                        chat_id=chat_id, message_id=message_id,
                        text="❌ Licenza non valida o già utilizzata.\n\nRiprova con un codice diverso.",
                        parse_mode="HTML", reply_markup=reply_markup
                    )
                    return ATTESA_LICENZA
                except:
                    return ATTESA_LICENZA


    with SessionLocal() as session:
        canale_service = CanaleService(session)
        gestisce_service = GestisceService(session)
        licenza_service = LicenzaService(session)

        try:

            canale = Canale(
                canale_id = channel_id,
                nome_canale = channel_name,
                id_affiliato = None,
                codice_licenza = codice
            )

            gestisce = Gestisce(
                telegram_id = int(update.effective_user.id),
                canale_id = channel_id,
                id_affiliato = None,
                is_creator = True
            )

            canale_service.aggiungi_canale(canale)
            gestisce_service.aggiungi_gestione(gestisce)

            licenza_service.activate_licenza(codice)

            session.commit()

        except Exception as e:
            session.rollback()
            await ctx.bot.edit_message_text(
                chat_id=chat_id, message_id=message_id,
                text=f"❌ Errore durante il salvataggio del canale: {e}",
                parse_mode="HTML", reply_markup=reply_markup
            )
            return ATTESA_LICENZA

    await ctx.bot.edit_message_text(
        chat_id=chat_id, message_id=message_id,
        text=(
            f"🎉 <b>Canale aggiunto con successo!</b>\n\n"
            f"📢 {channel_name}\n"
            f"🔑 Licenza: <code>{codice}</code>"
        ),
        parse_mode="HTML",
        reply_markup=InlineKeyboardMarkup([
            [InlineKeyboardButton("🔙 Torna ai canali", callback_data="channeloffers_main")]
        ])
    )

    ctx.user_data.pop('channel_data', None)
    ctx.user_data.pop('add_channel_message_id', None)
    ctx.user_data.pop('add_channel_chat_id', None)

    return ConversationHandler.END

# ── Annulla ───────────────────────────────────────────────────────────────────

async def annulla_add_channel(update: Update, ctx: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()
    ctx.user_data.pop('channel_data', None)
    ctx.user_data.pop('add_channel_message_id', None)
    ctx.user_data.pop('add_channel_chat_id', None)
    await channeloffers_main(update, ctx)
    return ConversationHandler.END


# ── ConversationHandler ───────────────────────────────────────────────────────

conv_add_channel = ConversationHandler(
    entry_points=[
        CallbackQueryHandler(channeloffers_addchannel, pattern='^channeloffers_addchannel$')
    ],
    states={
        ATTESA_FORWARD: [
            MessageHandler(filters.ALL & ~filters.COMMAND, received_forward),
            CallbackQueryHandler(annulla_add_channel, pattern='^channeloffers_main$'),
        ],
        ATTESA_LICENZA: [
            MessageHandler(filters.TEXT & ~filters.COMMAND, received_licenza),
            CallbackQueryHandler(annulla_add_channel, pattern='^channeloffers_main$'),
        ],
    },
    fallbacks=[
        CallbackQueryHandler(annulla_add_channel, pattern='^channeloffers_main$')
    ],
    per_message=False,
    per_chat=True,
)
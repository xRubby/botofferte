def get_benvenuto(user_link):
    msg = (
        f"🔸 <b>Benvenuto</b> {user_link}"
        "\n\n"
        "Scegli ciò di cui hai bisogno dai tasti in basso ⤵️"
        "\n\n"
        "🔍 <b>Cerca prodotto</b> ti permette di ottenere il prodotto desiderato da Amazon e scoprire se è in sconto."
        "\n\n"
        "⚙️ <b>Impostazioni</b> ti permette di modificare le impostazioni di questa chat <b>(IN LAVORAZIONE)</b>."
        )
    return msg

def get_cerca_prodotto():
    msg=(
        "<b>🔍 Cerca prodotto</b>"
        "\n\n"
        "Per favore, inviami il nome oppure il link del prodotto che vuoi cercare."
    )
    return msg

def get_impostazioni():
    msg=(
        "<b>⚙️ Impostazioni</b>"
        "\n\n"
        "<b>IN LAVORAZIONE</b> 🏗️"
    )
    return msg

def get_licenza_non_attiva():
    msg=("<b>Licenza non attiva</b>")

    return msg

def get_admin_message():
    msg=("PANNELLO ADMIN")
    return msg

def get_licenza_generata(licenza):
    msg=("Licenza generata\n"
        "\n"
        f"<b>{licenza}</b>")
    return msg

def getTemplateMessage():
    msg=("📦 <b>{titolo}</b>\n"
        "💲 <i>Prezzo vecchio:</i> {old_prezzo}{valuta}\n"
        "💰 <i>Prezzo nuovo:</i> <b>{prezzo}{valuta}</b>\n"
        "📉 <i>Sconto:</i> {sconto}%\n\n"
        "🚚 {spedito}\n\n"
        "🔗 <b>Scopri l'offerta:</b> <a href=\"{link}\">Clicca qui!</a>")
    return msg
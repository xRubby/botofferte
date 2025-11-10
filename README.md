# Bot Telegram per la ricerca e pubblicazione di offerte Amazon

Un bot per Telegram che aiuta a preparare rapidamente messaggi di offerte Amazon da pubblicare manualmente su canali.

## 🧠 Caratteristiche principali

- Inserisci manualmente il link di un prodotto Amazon.  
- Il bot raccoglie automaticamente le informazioni principali:
  - Titolo del prodotto
  - Prezzo
  - Venditore
  - Spedizione Prime
- Genera un messaggio pronto per essere pubblicato su Telegram, risparmiando tempo.  

## 💡 Perché usarlo

- Risparmio di tempo nella creazione di messaggi promozionali.  
- Facilita la pubblicazione di offerte Amazon su uno o più canali Telegram.  
- Evita errori di copia/incolla e formato incoerente dei messaggi.

## 🚀 Installazione & configurazione

1. Clona il repository:  
   ```bash
   git clone https://github.com/xRubby/botofferte.git
   cd botofferte
   ```
2. Crea e attiva un ambiente virtuale Python:  
   ```bash
   python3 -m venv venv
   source venv/bin/activate    # su Linux/macOS
   ```
3. Installa le dipendenze:  
   ```bash
   pip install -r requirements.txt
   ```
4. Configura il bot Telegram e altri servizi tramite il file `.env`.  
   Crea un file `.env` nella cartella principale con questo formato:

   ```env
   # TELEGRAM
   TELEGRAM_TOKEN=""
   USER_ID_ADMIN=""

   # AMAZON
   ACCESS_KEY=""
   SECRET_KEY=""
   ASSOCIATE_TAG=""
   REGION=""

   # BITLY
   BITLY_TOKEN=""

   # DISCORD
   DISCORD_TOKEN=""
   ```
   - `TELEGRAM_TOKEN` → token del bot Telegram (da BotFather)  
   - `USER_ID_ADMIN` → ID Telegram dell’amministratore  
   - `ACCESS_KEY` / `SECRET_KEY` / `ASSOCIATE_TAG` / `REGION` → credenziali Amazon API  
   - `BITLY_TOKEN` → token per accorciare link (opzionale)  
   - `DISCORD_TOKEN` → token bot Discord (opzionale)

5. Avvia il bot:  
   ```bash
   python main.py
   ```

## 📁 Struttura delle cartelle

```
botofferte/
├── scraper/          # logica per estrarre informazioni dai link Amazon
├── telegram_bot/     # gestione bot Telegram e messaggi
├── utils/            # funzioni di supporto
├── main.py           # punto di ingresso
├── requirements.txt  # dipendenze Python
├── .env              # file di configurazione
└── README.md
```

## ✅ Come funziona

1. L’utente invia il link di un prodotto Amazon al bot Telegram.  
2. Il bot estrae titolo, prezzo, condizione e spedizione.  
3. Viene generato un messaggio pronto da pubblicare sul canale Telegram. 

## ❗ Avvertenze

- Il bot non monitora automaticamente le offerte: tutte le pubblicazioni sono manuali.  
- Lo scraping può essere soggetto a modifiche del sito Amazon, quindi potrebbe richiedere aggiornamenti futuri.  
- Assicurati di rispettare i termini di servizio di Amazon e Telegram.


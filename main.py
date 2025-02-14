from multiprocessing import Process
from telegram_bot.bot import start_telegram_bot
#from bot.discord_bot import start_discord_bot
from database.Connessione import Connessione

def main():

    Connessione().create_tables()

    print("Avvio dei bot Telegram e Discord...")

    # Avvia il bot Telegram in un processo separato
    telegram_process = Process(target=start_telegram_bot)
    telegram_process.start()

    # Avvia il bot Discord in un processo separato
    #discord_process = Process(target=start_discord_bot)
    #discord_process.start()

    # Attendi la terminazione dei processi
    try:
        telegram_process.join()
    except KeyboardInterrupt:
        print("\nSto terminando i processi")
        telegram_process.terminate()
    
    #discord_process.join()

if __name__ == "__main__":
    main()
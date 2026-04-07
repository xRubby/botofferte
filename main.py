from multiprocessing import Process
from telegram_botnew.bot import start_telegram_bot
#from bot.discord_bot import start_discord_bot
from database.Connessione import Connessione

def main():

    #Connessione().create_tables()

    start_telegram_bot()

if __name__ == "__main__":
    main()
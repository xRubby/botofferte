from multiprocessing import Process
from telegram_bot.bot import start_telegram_bot
#from bot.discord_bot import start_discord_bot

from database.connection import engine
from database.base import Base

import models

def main():

    Base.metadata.create_all(engine)

    start_telegram_bot()

if __name__ == "__main__":
    main()
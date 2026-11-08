import asyncio
from multiprocessing import Process
from functions.worker_prezzi import worker_aggiorna_prezzi
from telegram_bot.bot import start_telegram_bot
#from bot.discord_bot import start_discord_bot

from database.connection import engine
from database.base import Base

import models

def main():

    Base.metadata.create_all(engine)

    #asyncio.run(worker_aggiorna_prezzi(None))
    start_telegram_bot()

if __name__ == "__main__":
    main()
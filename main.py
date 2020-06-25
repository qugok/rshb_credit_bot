#!/usr/bin/python3
from bot import MyBot
import logging

from static_info import TELEGRAM_TOKEN, LOGGING_LEVEL, LOG_FILENAME

FORMAT = '%(asctime)s - %(name)s - %(levelname)s - %(message)s'
logging.basicConfig(filename=LOG_FILENAME, format=FORMAT, level=LOGGING_LEVEL)

if __name__ == "__main__":
    bank_bot = MyBot(TELEGRAM_TOKEN)
    bank_bot.start()


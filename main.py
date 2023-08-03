#!/usr/bin/env python3
# -*- coding: utf-8 -*-

__author__ = "ipetrash"


import os
import time

# pip install python-telegram-bot
from telegram.ext import Updater, Defaults

from config import TOKEN
from bot.common import log
from bot import commands


def main():
    log.debug("Start")

    cpu_count = os.cpu_count()
    workers = cpu_count
    log.debug(f"System: CPU_COUNT={cpu_count}, WORKERS={workers}")

    updater = Updater(
        TOKEN,
        workers=workers,
        defaults=Defaults(run_async=True),
    )
    bot = updater.bot
    log.debug(f"Bot name {bot.first_name!r} ({bot.name})")

    dp = updater.dispatcher
    commands.setup(dp)

    updater.start_polling()
    updater.idle()

    log.debug("Finish")


if __name__ == "__main__":
    while True:
        try:
            main()
        except:
            log.exception("")

            timeout = 15
            log.info(f"Restarting the bot after {timeout} seconds")
            time.sleep(timeout)

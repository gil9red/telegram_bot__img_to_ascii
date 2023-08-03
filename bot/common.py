#!/usr/bin/env python3
# -*- coding: utf-8 -*-

__author__ = "ipetrash"


import enum
import functools
import logging
import sys

from logging.handlers import RotatingFileHandler
from pathlib import Path
from typing import Union

from telegram import Update, ReplyMarkup, Message
from telegram.ext import CallbackContext

import config
from config import DIR_LOGS


def get_logger(
    name: str,
    file: Union[str, Path] = "log.txt",
    encoding="utf-8",
    log_stdout=True,
    log_file=True,
) -> "logging.Logger":
    log = logging.getLogger(name)
    log.setLevel(logging.DEBUG)

    formatter = logging.Formatter(
        "[%(asctime)s] %(filename)s:%(lineno)d %(levelname)-8s %(message)s"
    )

    if log_file:
        fh = RotatingFileHandler(
            file, maxBytes=10000000, backupCount=5, encoding=encoding
        )
        fh.setFormatter(formatter)
        log.addHandler(fh)

    if log_stdout:
        sh = logging.StreamHandler(stream=sys.stdout)
        sh.setFormatter(formatter)
        log.addHandler(sh)

    return log


def log_func(log: logging.Logger):
    def actual_decorator(func):
        @functools.wraps(func)
        def wrapper(update: Update, context: CallbackContext):
            if update:
                chat_id = user_id = first_name = last_name = username = language_code = None

                if update.effective_chat:
                    chat_id = update.effective_chat.id

                if update.effective_user:
                    user_id = update.effective_user.id
                    first_name = update.effective_user.first_name
                    last_name = update.effective_user.last_name
                    username = update.effective_user.username
                    language_code = update.effective_user.language_code

                try:
                    message = update.effective_message.text
                except:
                    message = ""

                try:
                    query_data = update.callback_query.data
                except:
                    query_data = ""

                msg = (
                    f"[chat_id={chat_id}, user_id={user_id}, "
                    f"first_name={first_name!r}, last_name={last_name!r}, "
                    f"username={username!r}, language_code={language_code}, "
                    f"message={message!r}, query_data={query_data!r}]"
                )
                msg = func.__name__ + msg

                log.debug(msg)

            return func(update, context)

        return wrapper

    return actual_decorator


class SeverityEnum(enum.Enum):
    NONE = "{text}"
    INFO = "ℹ️ {text}"
    ERROR = "⚠ {text}"

    def get_text(self, text: str) -> str:
        return self.value.format(text=text)


def reply_message(
    text: str,
    update: Update,
    severity: SeverityEnum = SeverityEnum.NONE,
    reply_markup: ReplyMarkup = None,
    quote: bool = True,
    **kwargs,
) -> list[Message]:
    message = update.effective_message

    text = severity.get_text(text)

    result = []
    for n in range(0, len(text), config.MAX_MESSAGE_LENGTH):
        mess = text[n: n + config.MAX_MESSAGE_LENGTH]
        result.append(
            message.reply_text(
                mess,
                reply_markup=reply_markup,
                quote=quote,
                **kwargs
            )
        )

    return result


def process_error(log: logging.Logger, update: Update, context: CallbackContext):
    log.error("Error: %s\nUpdate: %s", context.error, update, exc_info=context.error)
    if update:
        reply_message(config.ERROR_TEXT, update, severity=SeverityEnum.ERROR)


log = get_logger(__file__, DIR_LOGS / "log.txt")

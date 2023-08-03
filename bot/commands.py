#!/usr/bin/env python3
# -*- coding: utf-8 -*-

__author__ = "ipetrash"


from functools import partial

import requests

from telegram import (
    Update,
    InlineKeyboardMarkup,
    InlineKeyboardButton,
)
from telegram.ext import (
    Dispatcher,
    CallbackContext,
    MessageHandler,
    CommandHandler,
    Filters,
    CallbackQueryHandler,
)

from bot.common import reply_message, log_func, process_error, log, SeverityEnum
from bot.regexp_patterns import (
    COMMAND_START,
    COMMAND_HELP,
    PATTERN_CHANGE_SIZE,
    fill_string_pattern,
)
from third_party.auto_in_progress_message import (
    show_temp_message_decorator,
    ProgressValue,
)
from config import SIZES, DEFAULT_SIZE, FORMAT_BUTTON_SIZE, FORMAT_BUTTON_SIZE_SELECTED


# Decorator
show_temp_message_decorator_on_progress = partial(
    show_temp_message_decorator,
    text=SeverityEnum.INFO.get_text("In progress {value}"),
    progress_value=ProgressValue.RECTS_SMALL,
)


@log_func(log)
def on_start(update: Update, context: CallbackContext):
    text = "Bot for converting image to ascii art."
    reply_message(text, update)


@log_func(log)
@show_temp_message_decorator_on_progress()
def on_request(update: Update, context: CallbackContext):
    message = update.effective_message
    # reply_playlist(message.text, update, context, show_full=False)


@log_func(log)
@show_temp_message_decorator_on_progress()
def on_photo(update: Update, context: CallbackContext):
    message = update.effective_message
    # chat_id = message.chat_id
    #
    # url = message.photo[-1].get_file().file_path
    # rs = requests.get(url)
    #
    # file_name = get_file_name_image(chat_id)
    # file_name.write_bytes(rs.content)
    #
    # message.reply_text(
    #     _('COMMANDS_ARE_NOW_AVAILABLE'),
    #     reply_markup=REPLY_KEYBOARD_MARKUP
    # )


@log_func(log)
def on_callback_change_size(update: Update, context: CallbackContext):
    query = update.callback_query
    if query:
        query.answer()

    size = int(context.match.group(1))
    # playlist_id = context.match.group(1)
    # reply_playlist(playlist_id, update, context, show_full=True)


def on_error(update: Update, context: CallbackContext):
    process_error(log, update, context)


def setup(dp: Dispatcher):
    dp.add_handler(CommandHandler(COMMAND_START, on_start))
    dp.add_handler(CommandHandler(COMMAND_HELP, on_start))

    dp.add_handler(MessageHandler(Filters.text, on_request))
    dp.add_handler(MessageHandler(Filters.photo, on_photo))

    dp.add_handler(
        CallbackQueryHandler(on_callback_change_size, pattern=PATTERN_CHANGE_SIZE)
    )

    dp.add_error_handler(on_error)

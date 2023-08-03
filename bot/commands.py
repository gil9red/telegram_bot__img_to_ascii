#!/usr/bin/env python3
# -*- coding: utf-8 -*-

__author__ = "ipetrash"


import html

from functools import partial

# pip install ascii-magic
from ascii_magic import AsciiArt

from telegram import (
    Update,
    InlineKeyboardMarkup,
    InlineKeyboardButton,
    Message,
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
from config import (
    MAX_MESSAGE_LENGTH,
    SIZES,
    DEFAULT_SIZE,
    IGNORE_SIZE,
    SIZES_COLUMNS,
    FORMAT_BUTTON_SIZE,
    FORMAT_BUTTON_SIZE_SELECTED,
)


def reply_ascii(
    update: Update,
    url: str,
    selected_size: int = DEFAULT_SIZE,
    as_new_message: bool = True,
):
    try:
        my_art = AsciiArt.from_url(url)
    except Exception as e:
        reply_message(text=f"Error: {e}", update=update, severity=SeverityEnum.ERROR)
        return

    text = my_art.to_ascii(columns=selected_size, monochrome=True)
    text = "\n".join(map(str.rstrip, text.splitlines()))
    text = html.escape(text)

    header = "<pre>"
    footer = "</pre>"
    placeholder = "..."

    if MAX_MESSAGE_LENGTH - len(header) - len(footer) > MAX_MESSAGE_LENGTH:
        text = text[: MAX_MESSAGE_LENGTH - len(placeholder) - len(header) - len(footer)] + placeholder
        text = html.escape(text)

    text = header + text + footer

    buttons = []
    for i in range(0, len(SIZES), SIZES_COLUMNS):
        row = []
        for size in SIZES[i : i + SIZES_COLUMNS]:
            if selected_size == size:
                button_text = FORMAT_BUTTON_SIZE_SELECTED.format(size)
                callback_data = fill_string_pattern(PATTERN_CHANGE_SIZE, IGNORE_SIZE)
            else:
                button_text = FORMAT_BUTTON_SIZE.format(size)
                callback_data = fill_string_pattern(PATTERN_CHANGE_SIZE, size)

            row.append(
                InlineKeyboardButton(
                    text=button_text,
                    callback_data=callback_data,
                )
            )

        buttons.append(row)

    reply_message(
        text=text,
        update=update,
        reply_markup=InlineKeyboardMarkup(buttons),
        as_new_message=as_new_message,
    )


# Decorator
show_temp_message_decorator_on_progress = partial(
    show_temp_message_decorator,
    text=SeverityEnum.INFO.get_text("In progress {value}"),
    progress_value=ProgressValue.RECTS_SMALL,
)


def get_url(message: Message) -> str:
    if message.photo:
        return message.photo[-1].get_file().file_path

    return message.text


@log_func(log)
def on_start(update: Update, _: CallbackContext):
    text = (
        "Bot for converting image to ascii art.\n"
        "Send me the url with the image or the image itself"
    )
    reply_message(text, update)


@log_func(log)
@show_temp_message_decorator_on_progress()
def on_request(update: Update, _: CallbackContext):
    message = update.effective_message
    reply_ascii(update, url=get_url(message))


@log_func(log)
@show_temp_message_decorator_on_progress()
def on_photo(update: Update, _: CallbackContext):
    message = update.effective_message
    reply_ascii(update, url=get_url(message))


@log_func(log)
@show_temp_message_decorator_on_progress()
def on_callback_change_size(update: Update, context: CallbackContext):
    query = update.callback_query
    if query:
        query.answer()

    size = int(context.match.group(1))
    if size == IGNORE_SIZE:  # Для уже выбранного размера
        return

    # Watch previous message
    message = update.effective_message
    if message.reply_to_message:
        message = message.reply_to_message

    url = get_url(message)
    reply_ascii(update, url=url, selected_size=size, as_new_message=False)


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

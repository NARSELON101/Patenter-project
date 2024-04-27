from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton
from aiogram.utils.callback_data import CallbackData

import query_processor as qp

processor = CallbackData('select_processor', 'action', 'processor_number')
yandex_gpt = CallbackData('select_yandex_gpt', 'action', 'use_yandex_gpt')


async def select_processor():
    markup = InlineKeyboardMarkup()
    for index, query_processor_cls in enumerate(qp.query_processors):
        markup.add(InlineKeyboardButton(query_processor_cls.get_name(),
                                        callback_data=processor.new("get_processor", str(index))))
    return markup


async def select_use_yandex_gpt():
    markup = InlineKeyboardMarkup()
    markup.add(InlineKeyboardButton("Да", callback_data=yandex_gpt.new("get_yagpt", True)))
    markup.add(InlineKeyboardButton("Нет", callback_data=yandex_gpt.new("get_yagpt", False)))
    return markup

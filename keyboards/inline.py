from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton
from aiogram.utils.callback_data import CallbackData

import query_processor as qp
import utils.db_commands as db


processor = CallbackData('select_processor', 'action', 'processor_number')
yandex_gpt = CallbackData('select_yandex_gpt', 'action', 'use_yandex_gpt')


async def select_processor():
    markup = InlineKeyboardMarkup()

    user = await db.get_user()
    for file in await db.get_users_files(user):
        markup.add(InlineKeyboardButton(file.name or file.document,
                                        callback_data=processor.new("get_user_processor", file.id)))

    for index, query_processor_cls in enumerate(qp.query_processors):
        markup.add(InlineKeyboardButton(query_processor_cls.get_name(),
                                        callback_data=processor.new("get_processor", str(index))))
    return markup


async def select_use_yandex_gpt():
    markup = InlineKeyboardMarkup()
    markup.add(InlineKeyboardButton("Да", callback_data=yandex_gpt.new("get_yagpt", True)))
    markup.add(InlineKeyboardButton("Нет", callback_data=yandex_gpt.new("get_yagpt", False)))
    return markup

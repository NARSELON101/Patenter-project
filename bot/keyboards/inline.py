from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton
from aiogram.utils.callback_data import CallbackData

processor = CallbackData('select_processor', 'action', 'processor_number')
yandex_gpt = CallbackData('select_yandex_gpt', 'action', 'use_yandex_gpt')

async def select_processor():
    markup = InlineKeyboardMarkup()
    markup.add(InlineKeyboardButton("Соглашение об обработке персональных данных", callback_data=processor.new("get_processor", "1")))
    markup.add(InlineKeyboardButton("Обработка писем", callback_data=processor.new("get_processor", "2")))
    return markup

async def select_use_yandex_gpt():
    markup = InlineKeyboardMarkup()
    markup.add(InlineKeyboardButton("Да", callback_data=yandex_gpt.new("get_yagpt", True)))
    markup.add(InlineKeyboardButton("Нет", callback_data=yandex_gpt.new("get_yagpt", False)))
    return markup
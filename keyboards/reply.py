from aiogram.types import ReplyKeyboardMarkup, KeyboardButton

async def start_menu():
    markup = ReplyKeyboardMarkup(resize_keyboard=True)
    markup.add(KeyboardButton("Создать документ"))
    return markup

async def cancel_menu():
    markup = ReplyKeyboardMarkup(resize_keyboard=True)
    markup.add(KeyboardButton("Отмена"))
    return markup
from aiogram.types import ReplyKeyboardMarkup, KeyboardButton

buttons = [
    "Создать документ",
    "Добавить документ",
    "Мои документы",
    "FAQ"
]


async def start_menu():
    markup = ReplyKeyboardMarkup(resize_keyboard=True)
    for button_text in buttons:
        markup.add(KeyboardButton(button_text))
    return markup


async def cancel_menu():
    markup = ReplyKeyboardMarkup(resize_keyboard=True)
    markup.add(KeyboardButton("Отмена"))
    return markup

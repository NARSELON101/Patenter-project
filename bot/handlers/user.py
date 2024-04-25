
from aiogram import Dispatcher
from aiogram.dispatcher import FSMContext
from aiogram.types import Message, CallbackQuery, InlineKeyboardMarkup, InlineKeyboardButton
from aiogram.utils.markdown import hbold, hcode, hlink
from bot.keyboards import inline, reply

async def echo_handler(messasge: Message) -> None:
    try:
        await messasge.answer(messasge.text, reply_markup=await reply.start_menu())
    except TypeError:
        await messasge.answer("!")


def register_user(dp: Dispatcher):
    dp.register_message_handler(echo_handler)
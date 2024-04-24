
from aiogram import Router
from aiogram.fsm.context import FSMContext
from aiogram.types import Message, CallbackQuery, InlineKeyboardMarkup, InlineKeyboardButton
from aiogram.utils.markdown import hbold, hcode, hlink
from keyboards import inline, reply

async def echo_handler(messasge: Message) -> None:
    try:
        await messasge.send_copy(chat_id=messasge.chat.id)
    except TypeError:
        await messasge.answer("!")


def register_user(router: Router):
    router.message.register(echo_handler)
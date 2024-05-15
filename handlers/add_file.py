import pathlib

from aiogram import Bot
from aiogram.dispatcher import FSMContext
from aiogram.types import Message

from keyboards import inline, reply
from loader import config
from misc.states import AddFile
import utils.db_commands as db
from utils.models import User


async def add_user_file(message: Message, state: FSMContext) -> None:
    await state.reset_state()
    await message.answer("Отправьте файл", reply_markup=await reply.cancel_menu())
    await AddFile.AddUserFile.set()


async def cancel_file(message: Message, state: FSMContext) -> None:
    await state.reset_state()
    await message.answer("Привет!", reply_markup=await reply.start_menu())


def generate_destination(message: Message) -> pathlib.Path:
    user_data_path = config.user_file_storage.path
    return user_data_path / message.document.file_name


async def get_user_file(message: Message, state: FSMContext) -> None:
    new_file_name = generate_destination(message)
    bot = Bot.get_current()
    await bot.download_file(message.document.file_id,
                            destination=new_file_name)
    await db.add_file_to_user(str(new_file_name))

import pathlib

from aiogram.dispatcher import FSMContext
from aiogram.types import Message

import utils.db_commands as db
from keyboards import reply
from loader import config
from misc.states import AddFile
from query_processor.new_file_processor import process_new_file


async def add_user_file(message: Message, state: FSMContext) -> None:
    await state.reset_state()
    await message.answer("Отправьте файл", reply_markup=await reply.cancel_menu())
    await AddFile.AddUserFile.set()


async def cancel_file(message: Message, state: FSMContext) -> None:
    await state.reset_state()
    await message.answer("Привет!", reply_markup=await reply.start_menu())


# TODO переделать генерацию имён для загружаемых файлов
def generate_destination(message: Message) -> pathlib.Path:
    user_data_path = config.user_file_storage.path
    return user_data_path / message.document.file_name


async def get_user_file(message: Message, state: FSMContext) -> None:
    new_file_name = generate_destination(message)
    await message.document.download(new_file_name)
    doc_in_db = await db.add_file_to_user(str(new_file_name))
    if doc_in_db is None:
        await message.answer("Произошла ошибка. Нужно зарегистрироваться, чтобы добавлять файлы")
    else:
        fields = await process_new_file(new_file_name, doc_in_db)
        fields_txt = '\n'.join(fields)
        await message.answer(f"Файл {message.document.file_name} добавлен. \nПоля: {fields_txt}",
                             reply_markup=await reply.start_menu())

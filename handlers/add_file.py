import json
import pathlib

from aiogram.dispatcher import FSMContext
from aiogram.types import Message, ReplyKeyboardMarkup, KeyboardButton

import utils.db_commands as db
from keyboards import reply
from loader import config
from misc.states import AddFile, ViewFile
from query_processor.new_file_processor import process_new_file
from utils.models import Document
from utils.telegram_input import telegram_input


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


async def fetch_user_file(message: Message, state: FSMContext) -> None:
    new_file_name = generate_destination(message)
    await message.document.download(new_file_name)
    name = message.text
    doc_in_db = await db.add_file_to_user(str(new_file_name), name)
    if doc_in_db is None:
        await message.answer("Произошла ошибка. Нужно зарегистрироваться, чтобы добавлять файлы")
    else:
        fields = await process_new_file(new_file_name, doc_in_db)
        fields_txt = '\n'.join(fields)
        await message.answer(f"Файл {message.document.file_name} добавлен. \nПоля: {fields_txt}",
                             reply_markup=await reply.start_menu())


async def user_file_selection(message: Message, state: FSMContext) -> None:
    user = await db.get_user()
    if user is None:
        await message.answer("Произошла ошибка. Нужно зарегистрироваться, чтобы добавлять файлы",
                             reply_markup=await reply.start_menu())
        return

    user_files: list[Document] = await db.get_users_files(user)
    if user_files is None or len(user_files) == 0:
        await message.answer("Нет файлов :(",
                             reply_markup=await reply.start_menu())
        return

    markup = ReplyKeyboardMarkup(resize_keyboard=True)
    for button_text in user_files:
        markup.add(KeyboardButton(button_text.name or button_text.document))

    markup.add(KeyboardButton("Отмена"))
    
    await message.answer("Выберите файл для просмотра", reply_markup=markup)
    await ViewFile.SelectFile.set()
    
    
async def view_selected_file(message: Message, state: FSMContext) -> None:
    user = await db.get_user()
    if user is None:
        await message.answer("Произошла ошибка. Нужно зарегистрироваться, чтобы добавлять файлы",
                             reply_markup=await reply.start_menu())
        return
    user_files = await db.get_users_files(user)
    if user_files is None or len(user_files) == 0:
        await message.answer("Нет файлов :(",
                             reply_markup=await reply.start_menu())
        return

    if message.text == "Отмена":
        await state.reset_state()
        await message.answer("Привет!", reply_markup=await reply.start_menu())
        return

    for file in user_files:
        if file.document == message.text or file.name == message.text:
            try:
                fields_metadata = json.loads(file.fields_metadata)
            except TypeError:
                fields_metadata = []
            fields_list: list[str] = []
            for field in fields_metadata:
                field_repr = field['field']
                if field['gpt_description'] != 'null':
                    field_repr = f"{field_repr} - {field['gpt_description']}"
                fields_list.append(field_repr)
            fields_str = '\n'.join(fields_list)

            markup = ReplyKeyboardMarkup(resize_keyboard=True)
            markup.add(KeyboardButton("Отмена"))
            markup.add(KeyboardButton("Изменить имя"))
            for button_text in fields_list:
                markup.add(KeyboardButton(button_text))

            await message.answer(f"Документ {file.document} \n{fields_str}",
                                 reply_markup=markup)

            await state.set_data({
                "file": file,
                "fields_metadata": fields_metadata
            })

            await ViewFile.ViewSelectedFile.set()
            break
    else:
        await message.answer("Нет такого файла :(")
        await state.reset_state()
        await message.answer("Привет!", reply_markup=await reply.start_menu())
        return


async def change_field(message: Message, state: FSMContext) -> None:
    file: Document = (await state.get_data()).get("file")
    fields_metadata = (await state.get_data()).get("fields_metadata")

    if message.text == "Отмена":
        await state.reset_state()
        await message.answer("Привет!", reply_markup=await reply.start_menu())
        return

    if message.text == "Изменить имя":
        new_name = await telegram_input("Введите новое:")
        await file.update(name=new_name).apply()
        await message.answer("Имя изменено")
        await state.reset_state()
        await message.answer("Привет!", reply_markup=await reply.start_menu())
        return

    markup = ReplyKeyboardMarkup(resize_keyboard=True)
    markup.add(KeyboardButton("Отмена"))

    for field in fields_metadata:
        if field['field'] == message.text:
            await message.answer(f"Текущее описание: {field['gpt_description']}\n",
                                 reply_markup=markup)
            new_description = await telegram_input("Введите новое:")
            if new_description == 'Отмена':
                await state.reset_state()
                await message.answer("Привет!", reply_markup=await reply.start_menu())
                return
            field['gpt_description'] = new_description
            for i in range(len(fields_metadata)):
                if fields_metadata[i]['field'] == field["field"]:
                    fields_metadata[i] = field
                    break

            await file.update(fields_metadata=json.dumps(fields_metadata)).apply()
            await message.answer("Описание изменено")
            await state.reset_state()
            await message.answer("Привет!", reply_markup=await reply.start_menu())
            break

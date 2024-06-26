import asyncio
import logging

from aiogram import Dispatcher
from aiogram.dispatcher import FSMContext
from aiogram.types import Message, InlineKeyboardMarkup

import utils.db_commands as db
from handlers.add_file import add_user_file, fetch_user_file, cancel_file, user_file_selection, view_selected_file, \
    change_field
from handlers.query_processing import init_process_query, user_cancel_query_processing, select_query_processor, \
    select_use_yandex_gpt, select_user_query_processor
from keyboards import inline
from keyboards import reply
from misc.states import CreateDocument, AddFile, ViewFile
from utils import telegram_input

logger = logging.getLogger(__name__)


async def user_start(message: Message, state: FSMContext) -> None:
    await state.reset_state()
    user = await db.get_user()
    if not user:
        await db.add_new_user()
    await message.answer(f"Привет!", reply_markup=await reply.start_menu())


async def create_document(message: Message, state: FSMContext) -> None:
    await state.reset_state()

    query_processors_buttons: InlineKeyboardMarkup = await inline.select_processor()

    await message.answer("Выберите процессор", reply_markup=query_processors_buttons)
    await CreateDocument.Processor.set()


async def process_input(message: Message, state: FSMContext) -> None:
    data = await state.get_data()
    telegram_input_queue_index: int = data.get("telegram_input_queue_index")
    queue: asyncio.Queue = telegram_input.telegram_input_queues[telegram_input_queue_index]
    await queue.put(message.text)
    await CreateDocument.ProcessQuery.set()


async def get_user_query_for_gpt(message: Message, state: FSMContext) -> None:
    query = message.text
    data = await state.get_data()
    query_processor = data.get('query_processor')
    bot = Dispatcher.get_current().bot

    await bot.send_message(chat_id=state.chat, text="Обращение к yagpt займёт некоторое время",
                           reply_markup=await reply.cancel_menu())
    await init_process_query(bot, query, True, query_processor, state)


async def faq(message: Message) -> None:
    await message.answer(
        "Загружаемый документ должен быть docx. Поля, которые нужно заполнить должны быть  в формате {{ имя поля }}")


def register_user(dp: Dispatcher):
    dp.register_message_handler(faq, text="FAQ", state="*")

    dp.register_message_handler(user_start, commands=["start"], state="*")
    dp.register_message_handler(user_cancel_query_processing, text="Отмена", state="*")
    dp.register_message_handler(create_document, text="Создать документ", state="*")

    dp.register_message_handler(add_user_file, text="Добавить документ", state="*")
    dp.register_message_handler(fetch_user_file, content_types=["document"], state=AddFile.AddUserFile)
    dp.register_message_handler(cancel_file, text="Отмена", state=AddFile.AddUserFile)

    dp.register_message_handler(user_file_selection, text="Мои документы", state="*")
    dp.register_message_handler(view_selected_file, state=ViewFile.SelectFile)
    dp.register_message_handler(change_field, state=ViewFile.ViewSelectedFile)

    dp.register_callback_query_handler(select_user_query_processor,
                                       inline.processor.filter(action="get_user_processor"),
                                       state=CreateDocument.Processor)
    dp.register_callback_query_handler(select_query_processor, inline.processor.filter(action="get_processor"),
                                       state=CreateDocument.Processor)
    dp.register_callback_query_handler(select_use_yandex_gpt, inline.yandex_gpt.filter(action="get_yagpt"),
                                       state=CreateDocument.UseYandexGPT)
    dp.register_message_handler(get_user_query_for_gpt, state=CreateDocument.GetUserQueryForGpt)
    dp.register_message_handler(process_input, state=CreateDocument.GetInput)

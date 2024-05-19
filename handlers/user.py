import asyncio
import logging

from aiogram import Dispatcher, types
from aiogram.dispatcher import FSMContext
from aiogram.types import Message

import utils.db_commands as db
from handlers.add_file import add_user_file, get_user_file, cancel_file
from handlers.query_processing import init_process_query, user_cancel_query_processing, select_query_processor, \
    select_use_yandex_gpt
from keyboards import inline
from keyboards import reply
from misc.states import CreateDocument, AddFile
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

    await message.answer("Выберите процессор", reply_markup=await inline.select_processor())
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


def register_user(dp: Dispatcher):
    dp.register_message_handler(user_start, commands=["start"], state="*")
    dp.register_message_handler(user_cancel_query_processing, text="Отмена", state="*")
    dp.register_message_handler(create_document, text="Создать документ", state="*")

    dp.register_message_handler(add_user_file, text="Добавить документ", state="*")
    dp.register_message_handler(get_user_file, content_types=["document"], state=AddFile.AddUserFile)
    dp.register_message_handler(cancel_file, text="Отмена", state=AddFile.AddUserFile)

    dp.register_callback_query_handler(select_query_processor, inline.processor.filter(action="get_processor"),
                                       state=CreateDocument.Processor)
    dp.register_callback_query_handler(select_use_yandex_gpt, inline.yandex_gpt.filter(action="get_yagpt"),
                                       state=CreateDocument.UseYandexGPT)
    dp.register_message_handler(get_user_query_for_gpt, state=CreateDocument.GetUserQueryForGpt)
    dp.register_message_handler(process_input, state=CreateDocument.GetInput)





import asyncio
import logging

from aiogram import Dispatcher
from aiogram.dispatcher import FSMContext
from aiogram.types import Message, CallbackQuery

import query_processor as qp
import utils.db_commands as db
from keyboards import inline
from keyboards import reply
from misc.states import CreateDocument

from loader import dp

from utils import telegram_input

logger = logging.getLogger(__name__)


async def user_start(message: Message, state: FSMContext) -> None:
    await state.reset_state()
    user = await db.get_user()
    if not user:
        await db.add_new_user()
    await message.answer("Привет!", reply_markup=await reply.start_menu())


async def create_document(message: Message, state: FSMContext) -> None:
    await state.reset_state()

    await message.answer("Выберите процессор", reply_markup=await inline.select_processor())
    await CreateDocument.Processor.set()


@dp.message_handler(state=CreateDocument.GetInput)
async def process_input(message: Message, state: FSMContext) -> None:
    data = await state.get_data()
    await state.update_data(telegram_input=message.text)
    telegram_input_lock_index: int = data.get("telegram_input_lock_index")
    lock: asyncio.Lock = telegram_input.telegram_input_locks[telegram_input_lock_index]
    lock.release()
    await CreateDocument.ProcessQuery.set()


@dp.message_handler(state=CreateDocument.GetUserQueryForGpt)
async def get_user_query_for_gpt(message: Message, state: FSMContext) -> None:
    query = message.text
    data = await state.get_data()
    query_processor = data.get('query_processor')
    bot = Dispatcher.get_current().bot
    await process_query(bot, query_processor, state.chat, use_gpt=True, query_gpt=query)


async def select_use_yandex_gpt(call: CallbackQuery, state: FSMContext, callback_data: dict | None = None) -> None:
    chosen_use_yagpt = callback_data.get('use_yandex_gpt') == "True"
    await state.update_data(use_yandex_gpt=chosen_use_yagpt)

    bot = Dispatcher.get_current().bot
    data = await state.get_data()
    query_processor = data.get('query_processor')
    if chosen_use_yagpt:
        await bot.send_message(chat_id=state.chat, text="Введите запрос для GPT: ")
        await CreateDocument.GetUserQueryForGpt.set()
    else:
        await process_query(bot, query_processor, state.chat, use_gpt=chosen_use_yagpt)


async def process_query(bot, query_processor, chat, use_gpt: bool = False, query_gpt: str | None = None):
    CreateDocument.ProcessQuery.set()
    result_files = None
    try:
        result_files: list[str] | None = await query_processor(use_gpt=use_gpt).async_process_query(query_gpt)
    except Exception as e:
        logger.error(f"Возникла ошибка при обработке запроса: {e}")
    if result_files is not None:
        await bot.send_message(chat_id=chat, text=f"Результат: {result_files}")
        for result_file in result_files:
            await bot.send_document(chat_id=chat, document=open(result_file, 'rb'))
    else:
        await bot.send_message(chat_id=chat, text=f"Ошибка при обработке запроса")



async def select_query_processor(call: CallbackQuery, callback_data: dict, state: FSMContext) -> None:
    chosen_query_processor_index = int(callback_data.get('processor_number'))
    await state.update_data(query_processor=qp.query_processors[chosen_query_processor_index])
    await CreateDocument.UseYandexGPT.set()
    await call.message.edit_text(f"Выбран процессор: {qp.query_processors[chosen_query_processor_index].get_name()}"
                                 f"\n Использовать Яндекс GPT-3?",
                                 reply_markup=await inline.select_use_yandex_gpt())


def register_user(dp: Dispatcher):
    dp.register_message_handler(user_start, commands=["start"], state="*")
    dp.register_message_handler(user_start, text="Отмена", state="*")
    dp.register_message_handler(create_document, text="Создать документ", state="*")

    dp.register_callback_query_handler(select_query_processor, inline.processor.filter(action="get_processor"),
                                       state=CreateDocument.Processor)
    dp.register_callback_query_handler(select_use_yandex_gpt, inline.yandex_gpt.filter(action="get_yagpt"),
                                       state=CreateDocument.UseYandexGPT)

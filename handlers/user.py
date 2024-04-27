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
from query_processor.gpt.yagpt import YaGptTimer
from query_processor.processors.processor import QueryProcessor
from utils import telegram_input

logger = logging.getLogger(__name__)

query_process_tasks: dict[int, asyncio.Task] = {}


async def user_start(message: Message, state: FSMContext) -> None:
    await state.reset_state()
    user = await db.get_user()
    if not user:
        await db.add_new_user()
    await message.answer("Привет!", reply_markup=await reply.start_menu())


async def user_cancel_query_processing(message: Message, state: FSMContext) -> None:
    data = await state.get_data()
    query_process_task_index = data.get('query_process_task_index')
    # Если это пользователь не начал обработку запроса, то отменять нечего
    if query_process_task_index is None:
        await CreateDocument.Processor.set()
        await message.answer("Привет!", reply_markup=await reply.start_menu())
        return
    query_process_task = query_process_tasks[query_process_task_index]
    query_process_task.cancel()
    await message.reply("Запрос отменён", reply_markup=await reply.start_menu())
    await CreateDocument.Processor.set()


async def create_document(message: Message, state: FSMContext) -> None:
    await state.reset_state()

    await message.answer("Выберите процессор", reply_markup=await inline.select_processor())
    await CreateDocument.Processor.set()


async def process_input(message: Message, state: FSMContext) -> None:
    data = await state.get_data()
    await state.update_data(telegram_input=message.text)
    telegram_input_lock_index: int = data.get("telegram_input_lock_index")
    lock: asyncio.Lock = telegram_input.telegram_input_locks[telegram_input_lock_index]
    lock.release()
    await CreateDocument.ProcessQuery.set()


async def get_user_query_for_gpt(message: Message, state: FSMContext) -> None:
    query = message.text
    data = await state.get_data()
    query_processor = data.get('query_processor')
    bot = Dispatcher.get_current().bot

    await bot.send_message(chat_id=state.chat, text="Обращение к yagpt может займёт некоторое время",
                           reply_markup=await reply.cancel_menu())
    await init_process_query(bot, query, True, query_processor, state)


async def init_process_query(bot, query, use_gpt, query_processor: QueryProcessor, state):
    # Запоминаем текущую задачу, чтобы если пользователь отменит запрос, то мы могли её отменить
    current_task = asyncio.current_task()
    current_task.set_name(f"Process_query {query_processor.get_name()} for {state.chat}")
    query_process_tasks[state.chat] = asyncio.current_task()
    await state.update_data(query_process_task_index=state.chat)
    if use_gpt:
        # Необходимо подождать минимум минут после каждого обращения к yagpt, таску, которая
        # захотела обратиться к yagpt в перерыв, ставим на паузу на YAGPT_TIME_TO_SLEEP секунд
        async with YaGptTimer():
            await process_query(bot, query_processor, state.chat, use_gpt=use_gpt, query_gpt=query)
    else:
        await process_query(bot, query_processor, state.chat, use_gpt=use_gpt, query_gpt=query)


async def select_use_yandex_gpt(call: CallbackQuery, state: FSMContext, callback_data: dict | None = None) -> None:
    chosen_use_yagpt = callback_data.get('use_yandex_gpt') == "True"
    await state.update_data(use_yandex_gpt=chosen_use_yagpt)

    bot = Dispatcher.get_current().bot
    data = await state.get_data()
    query_processor = data.get('query_processor')
    await call.message.answer("Начинаю обработку...", reply_markup=await reply.cancel_menu())
    if chosen_use_yagpt:
        await bot.send_message(chat_id=state.chat, text="Введите запрос для GPT: ",
                               reply_markup=await reply.cancel_menu())
        await CreateDocument.GetUserQueryForGpt.set()
    else:
        async with YaGptTimer():
            await init_process_query(bot, "", False, query_processor, state)


async def process_query(bot, query_processor, chat, use_gpt: bool = False, query_gpt: str | None = None):
    CreateDocument.ProcessQuery.set()
    result_files = None
    try:
        result_files: list[str] | None = await query_processor(use_gpt=use_gpt).async_process_query(query_gpt)
    except Exception as e:
        logger.error(f"Возникла ошибка при обработке запроса: {e}")
    if result_files is not None:
        await bot.send_message(chat_id=chat, text=f"Результат: {result_files}")
        # Если вернулся список предполагаем, что это список сгенерированных файлов
        if isinstance(result_files, list):
            for result_file in result_files:
                await bot.send_document(chat_id=chat, document=open(result_file, 'rb'))
    else:
        await bot.send_message(chat_id=chat, text=f"Ошибка при обработке запроса")

    await CreateDocument.Processor.set()


async def select_query_processor(call: CallbackQuery, callback_data: dict, state: FSMContext) -> None:
    chosen_query_processor_index = int(callback_data.get('processor_number'))
    await state.update_data(query_processor=qp.query_processors[chosen_query_processor_index])
    await CreateDocument.UseYandexGPT.set()
    await call.message.edit_text(f"Выбран процессор: {qp.query_processors[chosen_query_processor_index].get_name()}"
                                 f"\n Использовать Яндекс GPT-3?",
                                 reply_markup=await inline.select_use_yandex_gpt())


def register_user(dp: Dispatcher):
    dp.register_message_handler(user_start, commands=["start"], state="*")
    dp.register_message_handler(user_cancel_query_processing, text="Отмена", state="*")
    dp.register_message_handler(create_document, text="Создать документ", state="*")

    dp.register_callback_query_handler(select_query_processor, inline.processor.filter(action="get_processor"),
                                       state=CreateDocument.Processor)
    dp.register_callback_query_handler(select_use_yandex_gpt, inline.yandex_gpt.filter(action="get_yagpt"),
                                       state=CreateDocument.UseYandexGPT)
    dp.register_message_handler(get_user_query_for_gpt, state=CreateDocument.GetUserQueryForGpt)
    dp.register_message_handler(process_input, state=CreateDocument.GetInput)

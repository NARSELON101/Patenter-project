import asyncio
import logging
import traceback

from aiogram import Dispatcher
from aiogram.dispatcher import FSMContext
from aiogram.types import CallbackQuery, Message

import query_processor as qp
from keyboards import inline, reply
from loader import config
from misc.states import CreateDocument
from query_processor.processors.processor import QueryProcessor

logger = logging.getLogger(__name__)


async def select_query_processor(call: CallbackQuery, callback_data: dict, state: FSMContext) -> None:
    chosen_query_processor_index = int(callback_data.get('processor_number'))
    await state.update_data(query_processor=qp.query_processors[chosen_query_processor_index])
    await CreateDocument.UseYandexGPT.set()
    await call.message.edit_text(f"Выбран процессор: {qp.query_processors[chosen_query_processor_index].get_name()}"
                                 f"\n Использовать Яндекс GPT-3?",
                                 reply_markup=await inline.select_use_yandex_gpt())


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
        await init_process_query(bot, "", False, query_processor, state)


query_process_tasks: dict[int, asyncio.Task] = {}


async def init_process_query(bot, query, use_gpt, query_processor: QueryProcessor, state):
    # Запоминаем текущую задачу, чтобы если пользователь отменит запрос, то мы могли её отменить
    current_task = asyncio.current_task()
    current_task.set_name(f"Process_query {query_processor.get_name()} for {state.chat}")
    query_process_tasks[state.chat] = asyncio.current_task()
    await state.update_data(query_process_task_index=state.chat)
    if use_gpt:
        # Необходимо подождать минимум минут после каждого обращения к yagpt, таску, которая
        # захотела обратиться к yagpt в перерыв, ставим на паузу на YAGPT_TIME_TO_SLEEP секунд
        await CreateDocument.WaitForYandexGPT.set()
        await process_query(bot, query_processor, state.chat, use_gpt=use_gpt, query_gpt=query)
    else:
        await process_query(bot, query_processor, state.chat, use_gpt=use_gpt, query_gpt=query)


async def process_query(bot, query_processor, chat, use_gpt: bool = False, query_gpt: str | None = None):
    CreateDocument.ProcessQuery.set()
    result_files = None
    try:
        result_files: list[str] | None = await query_processor(use_gpt=use_gpt).async_process_query(query_gpt)
    except Exception as e:
        logger.error(f"Возникла ошибка при обработке запроса: {e}")
        if config.debug:
            await bot.send_message(chat_id=chat,
                                   text=f"Возникла ошибка при обработке запроса: {e} \n {traceback.format_exc()}")
    if result_files is not None:
        await bot.send_message(chat_id=chat, text=f"Результат: {result_files}", reply_markup=await reply.start_menu())
        # Если вернулся список предполагаем, что это список сгенерированных файлов
        if isinstance(result_files, list):
            for result_file in result_files:
                await bot.send_document(chat_id=chat, document=open(result_file, 'rb'),
                                        reply_markup=await reply.start_menu())
    else:
        await bot.send_message(chat_id=chat, text=f"Ошибка при обработке запроса",
                               reply_markup=await reply.start_menu())

    await CreateDocument.Processor.set()


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
    del query_process_tasks[query_process_task_index]
    await message.reply("Запрос отменён", reply_markup=await reply.start_menu())
    await CreateDocument.Processor.set()

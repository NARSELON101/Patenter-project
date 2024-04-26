from aiogram import Dispatcher
from aiogram.dispatcher import FSMContext
from aiogram.types import Message, CallbackQuery
from aiogram.utils.markdown import hcode

import utils.db_commands as db
from keyboards import inline
from keyboards import reply
from misc.states import CreateDocument


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


async def select_use_yandex_gpt(call: CallbackQuery, state: FSMContext, callback_data: dict | None = None) -> None:
    await state.update_data(processor_number=callback_data.get('processor_number'))
    await call.message.edit_text("Использовать Yandex GPT?", reply_markup=await inline.select_use_yandex_gpt())
    await CreateDocument.UseYandexGPT.set()


async def push_data(call: CallbackQuery, callback_data: dict, state: FSMContext) -> None:
    await state.update_data(use_yandex_gpt=callback_data.get('use_yandex_gpt'))
    await call.message.delete()
    data = await state.get_data()
    processor_number = data.get('processor_number')
    use_yandex_gpt = data.get('use_yandex_gpt')
    await call.message.answer(f"{hcode(processor_number)}, ЯГПТ: {'Да' if use_yandex_gpt else 'Нет'}"
                              f"\nНачинаю создание документа", reply_markup=await reply.cancel_menu())


def register_user(dp: Dispatcher):
    dp.register_message_handler(user_start, commands=["start"], state="*")
    dp.register_message_handler(user_start, text="Отмена", state="*")
    dp.register_message_handler(create_document, text="Создать документ", state="*")

    dp.register_callback_query_handler(select_use_yandex_gpt, inline.processor.filter(action="get_processor"),
                                       state=CreateDocument.Processor)
    dp.register_callback_query_handler(push_data, inline.yandex_gpt.filter(action="get_yagpt"),
                                       state=CreateDocument.UseYandexGPT)

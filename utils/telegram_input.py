import asyncio

from aiogram import Dispatcher

from misc.states import CreateDocument

telegram_input_locks = dict()


class TelegramInput:
    reply_markup = None


async def telegram_input(prompt: str) -> str:
    dp = Dispatcher.get_current()
    bot = dp.bot
    state = dp.current_state()
    await bot.send_message(chat_id=state.chat, text=prompt, reply_markup=TelegramInput.reply_markup)
    await CreateDocument.GetInput.set()
    lock = asyncio.Lock()
    telegram_input_locks[state.chat] = lock
    await state.update_data(telegram_input_lock_index=state.chat)
    await lock.acquire()
    pass
    async with lock:
        new_state = dp.current_state()
        return (await new_state.get_data()).get('telegram_input')

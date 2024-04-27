import asyncio

from aiogram import Dispatcher

from misc.states import CreateDocument

telegram_input_queues = dict()


class TelegramInput:
    reply_markup = None


async def telegram_input(prompt: str) -> str:
    dp = Dispatcher.get_current()
    bot = dp.bot
    state = dp.current_state()
    await bot.send_message(chat_id=state.chat, text=prompt, reply_markup=TelegramInput.reply_markup)
    await CreateDocument.GetInput.set()
    queue = asyncio.Queue(1)
    telegram_input_queues[state.chat] = queue
    await state.update_data(telegram_input_queue_index=state.chat)
    return await queue.get()

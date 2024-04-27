import asyncio

from aiogram import Dispatcher

from query_processor.data_source.source import DataSource
from utils.telegram_input import telegram_input


class TelegramDataSource(DataSource):
    def __init__(self, prompt):
        self.prompt = prompt

    async def get(self):
        return await telegram_input(self.prompt)
from aiogram import Bot, Dispatcher, Router
from aiogram.fsm.storage.memory import MemoryStorage
from data.config import load_config

config = load_config(".env")
storage = MemoryStorage()
bot = Bot(token=config.tg_bot.token, parse_mode="HTML")
dp = Dispatcher(storage=storage)

# bot['config'] = config
from aiogram.dispatcher.filters.state import StatesGroup, State

class CreateDocument(StatesGroup):
    Processor = State()
    UseYandexGPT = State()

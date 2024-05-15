from aiogram.dispatcher.filters.state import StatesGroup, State


class CreateDocument(StatesGroup):
    Processor = State()
    GetInput = State()
    UseYandexGPT = State()
    WaitForYandexGPT = State()
    ProcessQuery = State()
    GetUserQueryForGpt = State()


class AddFile(StatesGroup):
    AddUserFile = State()

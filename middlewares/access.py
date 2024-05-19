from aiogram import types
from aiogram.dispatcher.middlewares import BaseMiddleware

import utils.db_commands as db


class AccessMiddleware(BaseMiddleware):
    def __init__(self):
        super().__init__()

    async def on_process_message(self, message: types.Message, t):
        user = await db.get_user()
        if not user:
            await db.add_new_user()

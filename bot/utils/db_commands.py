from bot.utils.database import User
from aiogram import types

async def get_user():
    user = types.User.get_current()
    return await User.query.where(User.telegram_id == user.id).gino.first()
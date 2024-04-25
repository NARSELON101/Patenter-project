from utils.models import User
from aiogram import types

async def get_user():
    user = types.User.get_current()
    return await User.query.where(User.telegram_id == user.id).gino.first()


async def add_new_user():
    telegram = types.User.get_current()
    old_user = await get_user()
    if not old_user:
        return False

    user = User()
    user.telegram_id = telegram.id
    await user.create()
    return user
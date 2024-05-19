from aiogram import types

from utils.models import User, Document


async def get_user():
    user = types.User.get_current()
    return await User.query.where(User.telegram_id == user.id).gino.first()


async def add_new_user():
    telegram = types.User.get_current()
    old_user = await get_user()
    if old_user:
        return False

    user = User()
    user.telegram_id = telegram.id
    await user.create()
    return user


async def add_file_to_user(document: str) -> Document | None:
    user = await get_user()
    if user is None:
        return None
    doc = Document()
    doc.document = document
    doc.user_id = user.id
    await doc.create()
    return doc

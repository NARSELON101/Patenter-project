import datetime
from gino import Gino
from bot.loader import config
from sqlalchemy import (Column, Integer, String, DateTime, ARRAY)


datab = Gino()

class User(datab.Model):
    __tablename__ = "users"
    id = Column(Integer, autoincrement=True, primary_key=True, unique=True)
    telegram_id = Column(Integer, default=0)
    registation_date = Column(DateTime, default=datetime.datetime.now())


async def create_db():
    await datab.set_bind(config.db.postgres_uri)

    await datab.gino.create_all()

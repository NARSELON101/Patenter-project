import datetime
from gino import Gino
from loader import config


db = Gino()


async def create_db():
    await db.set_bind(config.db.postgres_uri)

    await db.gino.create_all()

import asyncio
import logging

from handlers.user import register_user
from middlewares.environment import EnvironmentMiddleware
from loader import bot, config, dp
from utils.database import create_db

logger = logging.getLogger(__name__)

def register_all_middlewares(dp, config):
    dp.setup_middleware(EnvironmentMiddleware(config=config))

def register_all_handlers(dp):
    register_user(dp)


async def main():
    logging.basicConfig(
        level=logging.INFO,
        format=u'%(filename)s:%(lineno)d #%(levelname)-8s [%(asctime)s] - %(name)s - %(message)s',
    )
    logger.info("Starting bot")

    register_all_middlewares(dp, config)
    register_all_handlers(dp)
    await create_db()
    try:
        await dp.start_polling(bot)
    finally:
        await dp.storage.close()
        await dp.storage.wait_closed()
        await bot.session.close()


if __name__ == '__main__':
    try:
        asyncio.run(main())
    except (KeyboardInterrupt, SystemExit):
        logger.error("Bot stopped!")
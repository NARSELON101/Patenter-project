import asyncio
import logging

from handlers.user import register_user
from loader import bot, dp, storage, config
from middlewares.environment import EnvironmentMiddleware
from utils.database import create_db

logger = logging.getLogger(__name__)


def register_all_middlewares(dp, config):
    dp.setup_middleware(EnvironmentMiddleware(config=config))


def register_all_handlers(dp):
    register_user(dp)


async def main():
    logging.basicConfig(
        level=logging.DEBUG if config.get('debug', False) else logging.INFO,
        format=u'%(filename)s:%(lineno)d #%(levelname)-8s [%(asctime)s] - %(name)s - %(message)s',
    )
    logger.info("Starting bot")

    register_all_middlewares(dp, config)
    register_all_handlers(dp)
    await create_db()
    try:
        await dp.start_polling(bot, allowed_updates=['message', 'callback_query'])
    finally:
        await dp.storage.close()
        await dp.storage.wait_closed()
        await bot.session.close()


if __name__ == '__main__':
    try:
        asyncio.run(main())
    except (KeyboardInterrupt, SystemExit):
        logger.error("Bot stopped!")

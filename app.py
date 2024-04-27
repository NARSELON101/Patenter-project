import asyncio
import logging

from handlers.user import register_user
from keyboards import reply
from loader import bot, dp, config
from middlewares.environment import EnvironmentMiddleware
from utils.database import create_db
from utils.telegram_input import TelegramInput

logger = logging.getLogger(__name__)


def register_all_middlewares(dp, config):
    dp.setup_middleware(EnvironmentMiddleware(config=config))


def register_all_handlers(dp):
    register_user(dp)


async def setup_telegram_input():
    TelegramInput.reply_markup = await reply.cancel_menu()


async def main():
    logging.basicConfig(
        level=logging.DEBUG if config.get('debug', False) else logging.INFO,
        format=u'%(filename)s:%(lineno)d #%(levelname)-8s [%(asctime)s] - %(name)s - %(message)s',
    )
    logger.info("Starting bot")

    register_all_middlewares(dp, config)
    register_all_handlers(dp)
    await setup_telegram_input()
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

import asyncio
import logging
from aiogram import Bot, Dispatcher
from aiogram.fsm.storage.memory import MemoryStorage
from aiogram.client.default import DefaultBotProperties
from aiogram.enums import ParseMode

from config import BOT_TOKEN
from db import Database
import start, courses, about, contact, register, admin
from logging_middleware import LoggingMiddleware

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s"
)
logger = logging.getLogger(__name__)


async def main():
    bot = Bot(
        token=BOT_TOKEN,
        default=DefaultBotProperties(parse_mode=ParseMode.HTML)
    )
    storage = MemoryStorage()
    dp = Dispatcher(storage=storage)

    # Init DB
    db = Database()
    await db.create_tables()

    # Middleware
    dp.message.middleware(LoggingMiddleware(db))
    dp.callback_query.middleware(LoggingMiddleware(db))

    # Routers
    dp.include_router(start.router)
    dp.include_router(register.router)
    dp.include_router(courses.router)
    dp.include_router(about.router)
    dp.include_router(contact.router)
    dp.include_router(admin.router)

    logger.info("🚀 BestEnglish Bot ishga tushdi!")
    await bot.delete_webhook(drop_pending_updates=True)
    await dp.start_polling(bot, db=db)


if __name__ == "__main__":
    asyncio.run(main())

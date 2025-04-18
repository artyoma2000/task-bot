import asyncio
import logging
from aiogram import Bot, Dispatcher
from config import load_config
from db import create_pool
from handlers import register_handlers

config = load_config()
logging.basicConfig(level=logging.INFO)

bot = Bot(token=config.bot.token)
dp = Dispatcher()

async def main():
    db_pool = await create_pool(config)
    register_handlers(dp, db_pool)
    await dp.start_polling(bot)

if __name__ == "__main__":
    asyncio.run(main())

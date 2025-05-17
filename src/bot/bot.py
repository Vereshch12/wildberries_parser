import asyncio
import os
from dotenv import load_dotenv
from aiogram import Bot, Dispatcher
from .handlers import dp
from .config import logger

load_dotenv()
TOKEN = os.getenv('TELEGRAM_TOKEN')
if not TOKEN:
    raise ValueError("TELEGRAM_TOKEN не задан в .env")

bot = Bot(token=TOKEN)

async def main():
    logger.info("Starting bot polling")
    await dp.start_polling(bot)

if __name__ == "__main__":
    asyncio.run(main())
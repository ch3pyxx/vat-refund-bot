import asyncio
import logging
import sys
from pathlib import Path

from aiogram import Bot, Dispatcher

sys.path.insert(0, str(Path(__file__).parent.parent))

from config import settings
from handlers import router


async def main():
    bot = Bot(token=settings.TOKEN)
    dp = Dispatcher()
    dp.include_router(router)
    await dp.start_polling(bot)


if __name__ == "__main__":
    logging.basicConfig(level=logging.INFO)
    try:
        asyncio.run(main())
    except KeyboardInterrupt:
        print("Exit")

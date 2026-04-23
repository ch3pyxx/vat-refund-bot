from aiogram import Bot, Dispatcher 
import asyncio
import logging
from config import TOKEN

from aiogram.filters import CommandStart
from aiogram.types import Message

bot = Bot(token=TOKEN)
dp = Dispatcher()


@dp.message(CommandStart())
async def cmd_start(message: Message):
    await message.answer("oxae котахбас")

async def main():
    await dp.start_polling(bot)

if __name__ == '__main__':
    logging.basicConfig(level=logging.INFO)
    try:
        asyncio.run(main())    
    except KeyboardInterrupt:
        print("Exit")

from aiogram import Bot, Dispatcher, F 
import asyncio
import logging
from config import TOKEN

from aiogram.filters import CommandStart, Command
from aiogram.types import Message

bot = Bot(token=TOKEN)
dp = Dispatcher()



@dp.message(CommandStart())
async def cmd_start(message: Message):
    await message.answer("Доброго времени суток!")

@dp.message(Command('help'))
async def cmd_help(message: Message):
    await message.answer("Это команда help")

@dp.message(F.text == "Сколько будет 10 + 10?")
async def calculatebot(message: Message):
    value = get_twenty()
    await message.answer(str(value))


def get_twenty()-> int:
    return 20

async def main():
    await dp.start_polling(bot)

if __name__ == '__main__':
    logging.basicConfig(level=logging.INFO)
    try:
        asyncio.run(main())    
    except KeyboardInterrupt:
        print("Exit")

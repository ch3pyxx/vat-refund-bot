from aiogram import Router, F
from aiogram.filters import CommandStart, Command
from aiogram.types import Message

router = Router()

@router.message(CommandStart())
async def cmd_start(message: Message):
    await message.answer("Доброго времени суток!")


#---------------------------------------------------------------------------------------------------
@router.message(Command('help'))
async def cmd_help(message: Message):
    await message.answer("Это команда help")

@router.message(Command('go'))
async def cmd_help(message: Message):
    await message.answer("Отправьте фото QR кода. Постарайтесь сделать фото как можно чётче")
# -----------------------------------------------------------------------------


@router.message(F.text == "Сколько будет 10 + 10?")
async def calculatebot(message: Message):
    value = get_twenty()
    await message.answer(str(value))


@router.message(F.photo)
async def get_photo(message: Message):
    await message.answer("фото получено успешно")
#---------------------------------------------------------------------------

def get_twenty()-> int:
    return 20
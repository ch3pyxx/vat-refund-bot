from aiogram.types import ReplyKeyboardMarkup, KeyboardButton

main_keyboard = ReplyKeyboardMarkup(
    keyboard=[
        [KeyboardButton(text="Отправить чек")],
        [KeyboardButton(text="Получить отчёт"), KeyboardButton(text="Помощь")],
    ],
    resize_keyboard=True,
)

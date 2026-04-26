import logging
import sys
from io import BytesIO
from pathlib import Path
from datetime import datetime

from aiogram import Router, F, Bot
from aiogram.filters import CommandStart, Command
from aiogram.types import Message, FSInputFile

sys.path.insert(0, str(Path(__file__).parent.parent))

from recognition.decoder import decode_qr
from recognition.parsep import parse_receipt
from reports.excel_report import (
    add_receipt,
    clear_user_reports,
    get_user_report_path,
    DuplicateReceiptError,
)
from keybord import main_keyboard

router = Router()
logger = logging.getLogger(__name__)

WELCOME = (
    "Добро пожаловать!\n\n"
    "Я автоматически распознаю чеки и сохраняю данные в Excel-реестр НДС.\n\n"
    "<b>Что умею:</b>\n"
    "• Распознаю QR-коды с чеков\n"
    "• Достаю данные чека с soliq.uz\n"
    "• Веду реестр в Excel\n\n"
    "Просто отправьте фото QR-кода."
)

HELP = (
    "<b>Инструкция:</b>\n\n"
    "1. Нажмите <b>Отправить чек</b> или просто пришлите фото\n"
    "2. Сфотографируйте QR-код на чеке как можно чётче\n"
    "3. Дождитесь подтверждения\n\n"
    "<b>Получить отчёт</b> — пришлю Excel-файл за текущий месяц.\n\n"
    "По вопросам: @ch3pyxx"
)


@router.message(CommandStart())
async def cmd_start(message: Message):
    await message.answer(WELCOME, parse_mode="HTML", reply_markup=main_keyboard)


@router.message(Command("help"))
@router.message(F.text == "Помощь")
async def cmd_help(message: Message):
    await message.answer(HELP, parse_mode="HTML")


@router.message(Command("report"))
@router.message(F.text == "Получить отчёт")
async def cmd_report(message: Message):
    report_path = get_user_report_path(message.from_user.id)
    if not report_path.exists():
        await message.answer("Отчёт за текущий месяц пока пуст — чеков не добавлено.")
        return
    await message.answer_document(
        FSInputFile(report_path, filename=f"НДС_{datetime.now():%Y-%m}.xlsx"),
        caption=f"Реестр НДС за {datetime.now():%B %Y}",
    )


@router.message(Command("clear"))
@router.message(F.text == "Очистить реестр")
async def cmd_clear(message: Message):
    deleted = clear_user_reports(message.from_user.id)
    if deleted == 0:
        await message.answer("Реестр уже пуст — удалять нечего.")
    else:
        await message.answer(
            f"Реестр очищен. Удалено файлов: {deleted}.\n"
            f"При следующей отправке чека будет создан новый чистый реестр."
        )


@router.message(F.text == "Отправить чек")
async def prompt_photo(message: Message):
    await message.answer("Отправьте фото QR-кода с чека.")


@router.message(F.photo)
async def handle_photo(message: Message, bot: Bot):
    await message.answer("Обрабатываю чек...")

    # Скачиваем фото (берём наибольшее разрешение)
    photo = message.photo[-1]
    file = await bot.get_file(photo.file_id)
    buf = BytesIO()
    await bot.download_file(file.file_path, destination=buf)
    image_bytes = buf.getvalue()

    # 1. Декодируем QR-код → получаем URL чека
    try:
        qr_data = await decode_qr(image_bytes)
    except NotImplementedError:
        await message.answer("Модуль распознавания QR ещё не подключён.")
        return
    except Exception:
        logger.exception("Ошибка декодирования QR")
        await message.answer("Не удалось распознать QR-код. Попробуйте сфотографировать чётче.")
        return

    # 2. Парсим данные чека с soliq.uz
    try:
        receipt = await parse_receipt(qr_data)
    except Exception:
        logger.exception("Ошибка парсинга чека")
        await message.answer("Не удалось получить данные чека с soliq.uz.")
        return

    # 3. Сохраняем в Excel-реестр (отдельно для каждого пользователя)
    try:
        add_receipt(
            user_id=message.from_user.id,
            org_name=receipt.org_name,
            amount=receipt.amount,
            vat=receipt.vat,
            payment_date=receipt.payment_date,
            receipt_id=receipt.receipt_id,
        )
    except DuplicateReceiptError:
        await message.answer("Этот чек уже добавлен в реестр.")
        return
    except Exception:
        logger.exception("Ошибка записи в Excel")
        await message.answer("Чек распознан, но не удалось сохранить в реестр.")
        return

    await message.answer(
        f"Чек добавлен в реестр!\n\n"
        f"<b>{receipt.org_name}</b>\n"
        f"Сумма: {receipt.amount:,.0f} сум\n"
        f"НДС: {receipt.vat:,.2f} сум\n"
        f"Дата: {receipt.payment_date:%d.%m.%Y}",
        parse_mode="HTML",
    )

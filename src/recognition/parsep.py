import re
from dataclasses import dataclass
from datetime import datetime

import requests
from bs4 import BeautifulSoup


@dataclass
class ReceiptData:
    org_name: str
    amount: float
    vat: float
    payment_date: datetime
    receipt_id: str


async def parse_receipt(qr_data: str) -> ReceiptData:
    """
    Принимает URL чека (из QR-кода).
    Скачивает страницу, парсит HTML, возвращает ReceiptData.
    """
    response = requests.get(qr_data, timeout=10)
    response.raise_for_status()
    soup = BeautifulSoup(response.text, "html.parser")

    # Наименование организации: жирный h3
    org_name = soup.find("h3", style=lambda x: x and "font-weight: bold" in x)
    if not org_name:
        raise ValueError("Не найдено наименование организации")
    org_name = org_name.text.strip()

    # Сумма (Jami to`lov)
    amount = _find_value_after_text(soup, "Jami to`lov:")
    if amount is None:
        raise ValueError("Не найдена сумма чека")

    # НДС (Umumiy QQS qiymati)
    vat = _find_value_after_text(soup, "Umumiy QQS qiymati")
    if vat is None:
        raise ValueError("Не найден размер НДС")

    # Дата: <i>21.04.2026, 18:46</i>
    date_tag = _find_date_tag(soup)
    if not date_tag:
        raise ValueError("Не найдена дата чека")
    date_str = date_tag.split(",")[0].strip()
    payment_date = datetime.strptime(date_str, "%d.%m.%Y")

    # Receipt ID: <b>YZ231006034714</b>
    receipt_id = soup.find("b")
    if not receipt_id:
        raise ValueError("Не найден ID чека")
    receipt_id = receipt_id.text.strip()

    return ReceiptData(
        org_name=org_name,
        amount=amount,
        vat=vat,
        payment_date=payment_date,
        receipt_id=receipt_id,
    )


def _find_value_after_text(soup: BeautifulSoup, text: str) -> float | None:
    """Ищет значение в <td> после строки с текстом."""
    for td in soup.find_all("td"):
        if text in td.text:
            next_td = td.find_next("td")
            if next_td:
                value_str = next_td.text.strip().replace(",", "")
                try:
                    return float(value_str)
                except ValueError:
                    pass
    return None


def _find_date_tag(soup: BeautifulSoup) -> str | None:
    """Ищет дату в формате DD.MM.YYYY, HH:MM"""
    for i_tag in soup.find_all("i"):
        text = i_tag.text.strip()
        if re.match(r"\d{2}\.\d{2}\.\d{4},\s*\d{2}:\d{2}", text):
            return text
    return None

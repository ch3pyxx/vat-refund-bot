from dataclasses import dataclass
from datetime import datetime


@dataclass
class ReceiptData:
    org_name: str
    amount: float
    vat: float
    payment_date: datetime
    receipt_id: str


async def parse_receipt(qr_data: str) -> ReceiptData:
    """
    Принимает данные QR-кода (URL чека soliq.uz).
    Возвращает распарсенные данные чека.
    """
    raise NotImplementedError

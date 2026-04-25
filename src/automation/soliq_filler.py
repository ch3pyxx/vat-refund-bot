import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).parent.parent))

from recognition.parsep import ReceiptData


async def register_receipt(receipt: ReceiptData) -> bool:
    """
    Регистрирует чек на soliq.uz через Playwright.
    Возвращает True при успешной регистрации.
    """
    raise NotImplementedError

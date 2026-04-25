import numpy as np
import cv2
from pyzbar.pyzbar import decode


async def decode_qr(image_bytes: bytes) -> str:
    """
    Декодирует QR-код с изображения.
    Возвращает URL чека (или текстовые данные QR-кода).
    Кидает ValueError если QR-код не найден.
    """
    arr = np.frombuffer(image_bytes, dtype=np.uint8)
    image = cv2.imdecode(arr, cv2.IMREAD_COLOR)
    if image is None:
        raise ValueError("Не удалось прочитать изображение")

    # 1. Пробуем декодировать оригинал
    result = _decode(image)
    if result:
        return result

    # 2. Пробуем чёрно-белую версию
    gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)
    result = _decode(gray)
    if result:
        return result

    # 3. Пробуем с бинаризацией (пороговое преобразование)
    _, binary = cv2.threshold(gray, 0, 255, cv2.THRESH_BINARY + cv2.THRESH_OTSU)
    result = _decode(binary)
    if result:
        return result

    raise ValueError("QR-код не найден на изображении")


def _decode(image) -> str | None:
    codes = decode(image)
    for code in codes:
        if code.type == "QRCODE":
            return code.data.decode("utf-8")
    return None

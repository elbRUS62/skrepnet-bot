import re


def sanitize_email(username: str, telegram_id: int) -> str:
    """Формирует email для 3x-ui.
    Приоритет: username (если есть) → user{telegram_id}."""
    if username:
        # Telegram username всегда латиница, цифры и _
        cleaned = re.sub(r'[^a-zA-Z0-9_\-]', '', username)
        if cleaned:
            return cleaned[:32]

    # Нет username или после очистки пусто — используем ID
    return f"user{telegram_id}"


import io
import qrcode
from aiogram.types import BufferedInputFile


def make_qr_image(data: str) -> BufferedInputFile:
    """Генерирует QR-код и возвращает как файл для отправки в Telegram."""
    qr = qrcode.QRCode(
        version=None,
        error_correction=qrcode.constants.ERROR_CORRECT_M,
        box_size=10,
        border=2,
    )
    qr.add_data(data)
    qr.make(fit=True)

    img = qr.make_image(fill_color="black", back_color="white")

    buf = io.BytesIO()
    img.save(buf, format="PNG")
    buf.seek(0)

    return BufferedInputFile(buf.read(), filename="skrepnet_qr.png")

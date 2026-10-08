import re


def sanitize_email(text: str) -> str:
    """Очистить имя для использования как email в 3x-ui."""
    text = re.sub(r'[^a-zA-Z0-9_\-]', '_', text)
    return text[:32] or "user"


TERMS_TEXT = (
    "📜 <b>Пользовательское соглашение SkrepNet</b>\n\n"
    "Перед получением подписки, пожалуйста, ознакомься с условиями:\n\n"
    "1. <b>Бесплатность.</b> Сервис предоставляется бесплатно. "
    "Проект существует на донаты пользователей.\n\n"
    "2. <b>Запрещено.</b> Использовать VPN для:\n"
    "   • Спама и мошенничества\n"
    "   • Распространения запрещённого контента\n"
    "   • Атак на другие серверы\n"
    "   • Любых действий, нарушающих законодательство РФ\n\n"
    "3. <b>Лимиты.</b> Максимум 3 IP-адреса одновременно. "
    "Подписка действует 30 дней, продление — вручную.\n\n"
    "4. <b>Ответственность.</b> Администрация не несёт ответственности "
    "за действия пользователей. При нарушении правил — блокировка без предупреждения.\n\n"
    "5. <b>Данные.</b> Бот хранит только твой Telegram ID, имя "
    "и статус подписки. Данные не передаются третьим лицам.\n\n"
    "Нажимая «✅ Согласен», ты подтверждаешь, что ознакомился "
    "с условиями и принимаешь их."
)

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
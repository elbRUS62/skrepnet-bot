"""Отрисовка прогресса сбора средств на сервер."""

from datetime import datetime

from config import SERVER_COST
from database import get_donations_total


MONTHS_GENITIVE = [
    "январе", "феврале", "марте", "апреле", "мае", "июне",
    "июле", "августе", "сентябре", "октябре", "ноябре", "декабре",
]


def _next_month_name() -> str:
    """Название СЛЕДУЮЩЕГО месяца в предложном падеже (в ноябре, в декабре...).
    Сбор всегда идёт на следующий месяц (оплата сервера вперёд)."""
    now = datetime.now()
    next_month = now.month % 12  # 12 → 0, потом 0 → январь
    return MONTHS_GENITIVE[next_month]


async def render_progress(short: bool = False) -> str:
    """Отрисовать полоску прогресса сбора.

    Args:
        short: если True — только строка для напоминаний
    """
    if SERVER_COST <= 0:
        return ""

    donated = await get_donations_total(currency="RUB")
    percent = min(int(donated / SERVER_COST * 100), 100)
    filled = min(percent // 10, 10)
    bar = "🟩" * filled + "⬜" * (10 - filled)

    if short:
        return (
            f"📊 Собрано на работу сервера в {_next_month_name()}:\n"
            f"\u00A0\n"
            f"{bar} {percent}%\n"
            f"❤️ Проект держится на донатах — помоги, если можешь."
        )

    # Полный формат
    if percent >= 100:
        return (
            f"📊 <b>Собрано на работу сервера в {_next_month_name()}</b>\n\n"
            f"{bar} <b>100%</b>\n\n"
            f"🎉 Спасибо всем, кто помог!"
        )

    return (
        f"📊 <b>Собрано на работу сервера в {_next_month_name()}</b>\n\n"
        f"{bar} <b>{percent}%</b>\n\n"
        f"❤️ Проект держится на донатах — помоги, если можешь."
    )
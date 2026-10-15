import logging
import aiosqlite

from aiogram import Router
from aiogram.types import Message
from aiogram.filters import CommandStart, CommandObject

from config import DB_PATH
from database import (
    get_user,
    increment_invites,
    add_invite,
)
from .utils import sanitize_email
from .menu import show_main_menu

router = Router()
logger = logging.getLogger(__name__)


@router.message(CommandStart(deep_link=True))
async def cmd_start_deeplink(message: Message, command: CommandObject):
    """Обработка /start с deep-link:
       - ?start=ref_<id> — реферальная ссылка
       - ?start=link_<token> — привязка веб-пользователя
    """
    from .web_link import handle_web_link

    args = command.args or ""

    # Ветка 1: веб-привязка
    if args.startswith("link_"):
        token = args[5:]
        await handle_web_link(message, token)
        return

    # Ветка 2: реферальная (существующая логика)
    invited_by = None
    if args.startswith("ref_"):
        try:
            invited_by = int(args[4:])
        except ValueError:
            pass

    if invited_by == message.from_user.id:
        invited_by = None

    existing = await get_user(message.from_user.id)

    if existing is None and invited_by:
        async with aiosqlite.connect(DB_PATH) as db:
            await db.execute("""
                INSERT OR REPLACE INTO users
                (telegram_id, username, first_name, xui_email, status, invited_by)
                VALUES (?, ?, ?, ?, 'new', ?)
            """, (
                message.from_user.id,
                message.from_user.username or "",
                message.from_user.first_name or "",
                sanitize_email(message.from_user.username, message.from_user.id),
                invited_by
            ))
            await db.commit()

        await increment_invites(invited_by)
        await add_invite(
            inviter_id=invited_by,
            invited_user_id=message.from_user.id,
            invited_username=message.from_user.username,
            invited_first_name=message.from_user.first_name,
            invite_type="ref"
        )

        try:
            await message.bot.send_message(
                invited_by,
                f"🎉 По твоей ссылке пришёл новый пользователь: "
                f"{message.from_user.full_name}!\n\n"
                f"Спасибо, что помогаешь проекту расти ❤️"
            )
        except Exception as e:
            logger.warning(f"Не удалось уведомить пригласившего {invited_by}: {e}")

    # Ветка 3: обычный deep-link (не ref, не link) — просто показать меню
    await show_main_menu(message)
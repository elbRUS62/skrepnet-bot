import logging
import aiosqlite
from config import DB_PATH

from aiogram import Router, F
from aiogram.types import Message
from aiogram.filters import CommandStart, CommandObject

from config import ADMIN_IDS
from database import get_user, create_user_request, increment_invites, add_invite
from keyboards import main_menu, admin_menu
from .utils import sanitize_email

router = Router()
logger = logging.getLogger(__name__)


@router.message(CommandStart(deep_link=True))
async def cmd_start_ref(message: Message, command: CommandObject):
    args = command.args or ""
    invited_by = None

    if args.startswith("ref_"):
        try:
            invited_by = int(args[4:])
        except ValueError:
            pass

    if invited_by == message.from_user.id:
        invited_by = None

    existing = await get_user(message.from_user.id)

    # Если пользователь НЕ в базе и пришёл по рефералке — просто показываем старт
    # invited_by сохраним в accept_terms через deep_link
    if existing is None and invited_by:
        # Запоминаем в базе со статусом 'new'
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
        except Exception:
            pass

    await _show_start(message)

@router.message(CommandStart())
async def cmd_start(message: Message):
    await _show_start(message)


async def _show_start(message: Message):
    user = await get_user(message.from_user.id)
    admin = message.from_user.id in ADMIN_IDS
    menu = admin_menu() if admin else main_menu()

    if user and user["status"] == "active":
        await message.answer(
            f"👋 С возвращением, {message.from_user.first_name}!\n\n"
            f"У тебя активная подписка. Проверить статус — «🔑 Моя подписка».",
            reply_markup=menu
        )
    elif user and user["status"] == "pending":
        await message.answer(
            "⏳ Твоя заявка на рассмотрении. Скоро админ её одобрит.",
            reply_markup=menu
        )
    else:
        await message.answer(
            f"👋 Привет, {message.from_user.first_name}!\n\n"
            f"Это бот для выдачи бесплатных подписок SkrepNet.\n\n"
            f"⚠️ Проект бесплатный, но сервер стоит ~3000 ₽/мес. "
            f"Если хочешь помочь — жми «❤️ Поддержать проект».\n\n"
            f"📢 Хочешь помочь проекту расти? Жми «👥 Пригласить друга» — "
            f"чем больше людей, тем стабильнее сервер.\n\n"
            f"Нажми «📦 Получить подписку», чтобы начать.",
            reply_markup=menu
        )
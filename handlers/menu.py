"""Обработчики главного inline-меню."""

import logging
from aiogram import Router, F
from aiogram.types import CallbackQuery, Message
from aiogram.filters import CommandStart

from config import ADMIN_IDS, DONATE_TEXT, DONATE_URL, BOT_NAME
from database import get_user, is_in_waitlist, get_waitlist_position
from keyboards import main_inline_menu, main_menu, admin_menu
from handlers.progress import render_progress

router = Router()
logger = logging.getLogger(__name__)


async def show_main_menu(message: Message):
    """Показать главное меню (ReplyKeyboard + InlineKeyboard).
    Вызывается из cmd_start и из cmd_start_ref (start.py)."""
    user = await get_user(message.from_user.id)
    is_admin = message.from_user.id in ADMIN_IDS
    menu = admin_menu() if is_admin else main_menu()

    in_waitlist = await is_in_waitlist(message.from_user.id)
    if in_waitlist:
        position = await get_waitlist_position(message.from_user.id)
        await message.answer(
            f"⏳ <b>Ты в листе ожидания</b>\n\n"
            f"📋 Твоя позиция: <b>{position}</b>\n\n"
            f"Мы напишем, когда освободится место.",
            parse_mode="HTML",
            reply_markup=menu
        )
        await message.answer(
            "📋 <b>Меню</b>",
            parse_mode="HTML",
            reply_markup=main_inline_menu(is_admin)
        )
        return

    progress_line = await render_progress(short=True)

    if user and user["status"] == "active":
        text = (
            f"👋 С возвращением, {message.from_user.first_name}!\n\n"
            f"У тебя активная подписка.\n\n"
            f"{progress_line}"
        )
    elif user and user["status"] == "pending":
        text = "⏳ Твоя заявка на рассмотрении. Скоро админ её одобрит."
    else:
        text = (
            f"👋 Привет, {message.from_user.first_name}!\n\n"
            f"Это бот для выдачи бесплатных подписок {BOT_NAME}.\n\n"
            f"{progress_line}\n\n"
            f"⚠️ Проект бесплатный, но сервер стоит ~3000 ₽/мес. "
            f"Если хочешь помочь — жми «❤️ Поддержать проект»."
        )

    await message.answer(text, parse_mode="HTML", reply_markup=menu)

    await message.answer(
        "📋 <b>Меню</b>\n\nВыбери действие:",
        parse_mode="HTML",
        reply_markup=main_inline_menu(is_admin)
    )


@router.message(CommandStart(deep_link=False))
async def cmd_start(message: Message):
    """Обычный /start БЕЗ deep-link.

    Сначала проверяем АВТОПРИВЯЗКУ по TG ID:
      - если для этого TG есть активная ссылка (friend_user_id)
      - и она не привязана → привязываем автоматически
    Потом показываем меню.
    """
    from database import find_pending_web_link_for_tg
    from handlers.web_link import bind_by_tg_id

    tg_id = message.from_user.id

    # Ищем активную ссылку для этого TG
    link = await find_pending_web_link_for_tg(tg_id)

    if link:
        logger.info(f"🔗 Найдена автопривязка для TG={tg_id}: token={link['token']}")
        await bind_by_tg_id(message, link)
        return

    # Обычное меню
    await show_main_menu(message)


@router.callback_query(F.data == "back_to_main")
async def back_to_main(callback: CallbackQuery):
    """Возврат в главное меню. Работает и с текстом, и с фото."""
    is_admin = callback.from_user.id in ADMIN_IDS

    try:
        # Пробуем отредактировать текст (если сообщение текстовое)
        await callback.message.edit_text(
            "🏠 <b>Главное меню</b>\n\nВыбери действие:",
            parse_mode="HTML",
            reply_markup=main_inline_menu(is_admin)
        )
    except Exception:
        # Сообщение с фото (или другое не текстовое) — удаляем и шлём новое
        try:
            await callback.message.delete()
        except Exception:
            pass
        await callback.message.answer(
            "🏠 <b>Главное меню</b>\n\nВыбери действие:",
            parse_mode="HTML",
            reply_markup=main_inline_menu(is_admin)
        )

    await callback.answer()


@router.callback_query(F.data == "menu_get_sub")
async def menu_get_sub(callback: CallbackQuery):
    await _handle_get_sub(callback)


@router.callback_query(F.data == "menu_my_sub")
async def menu_my_sub(callback: CallbackQuery):
    await _handle_my_sub(callback)


@router.callback_query(F.data == "menu_invite")
async def menu_invite(callback: CallbackQuery):
    await _handle_invite(callback)


@router.callback_query(F.data == "menu_invite_no_tg")
async def menu_invite_no_tg(callback: CallbackQuery):
    await _handle_invite_no_tg(callback)


@router.callback_query(F.data == "menu_docs")
async def menu_docs(callback: CallbackQuery):
    from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton
    from docs_config import DOCS
    await callback.message.edit_text(
        f"📚 <b>Документы {BOT_NAME}</b>\n\n"
        "Выбери документ для просмотра:",
        parse_mode="HTML",
        reply_markup=InlineKeyboardMarkup(inline_keyboard=[
            [InlineKeyboardButton(text=DOCS["rules"]["title"], url=DOCS["rules"]["url"])],
            [InlineKeyboardButton(text=DOCS["privacy"]["title"], url=DOCS["privacy"]["url"])],
            [InlineKeyboardButton(text=DOCS["terms"]["title"], url=DOCS["terms"]["url"])],
            [InlineKeyboardButton(text="⬅️ В главное меню", callback_data="back_to_main")]
        ])
    )
    await callback.answer()


@router.callback_query(F.data == "menu_progress")
async def menu_progress(callback: CallbackQuery):
    progress = await render_progress(short=False)
    from keyboards import donate_keyboard
    await callback.message.edit_text(
        progress,
        parse_mode="HTML",
        reply_markup=donate_keyboard()
    )
    await callback.answer()


# ============================================================
# ВНУТРЕННИЕ ФУНКЦИИ
# ============================================================

async def _handle_get_sub(callback: CallbackQuery):
    """📦 Получить подписку."""
    from config import MAX_USERS
    from database import (
        count_active_users, is_limit_reached,
    )
    from keyboards import terms_keyboard, waitlist_keyboard

    user = await get_user(callback.from_user.id)

    if user and user["status"] == "active":
        await callback.answer("У тебя уже есть активная подписка", show_alert=True)
        return

    if user and user["status"] == "pending":
        await callback.answer("⏳ Заявка уже отправлена", show_alert=True)
        return

    if await is_limit_reached(MAX_USERS):
        if await is_in_waitlist(callback.from_user.id):
            position = await get_waitlist_position(callback.from_user.id)
            await callback.message.edit_text(
                f"⏳ <b>Ты в листе ожидания</b>\n\n"
                f"📋 Твоя позиция: <b>{position}</b>\n\n"
                f"Мы напишем, когда освободится место.",
                parse_mode="HTML",
                reply_markup=waitlist_keyboard()
            )
            await callback.answer()
            return

        active = await count_active_users()
        await callback.message.edit_text(
            f"⚠️ <b>Свободных мест нет</b>\n\n"
            f"📊 Занято: {active} из {MAX_USERS}\n\n"
            f"Ты можешь встать в лист ожидания — мы напишем тебе, "
            f"как только освободится место.",
            parse_mode="HTML",
            reply_markup=waitlist_keyboard()
        )
        await callback.answer()
        return

    await callback.message.edit_text(
        "📜 <b>Для получения подписки ознакомься с документами:</b>\n\n"
        "1. 📜 Правила использования\n"
        "2. 🔒 Политика конфиденциальности\n"
        "3. 📋 Пользовательское соглашение\n\n"
        "Нажимая «✅ Я согласен со всеми условиями», ты подтверждаешь, "
        "что ознакомился со всеми документами.",
        reply_markup=terms_keyboard(),
        parse_mode="HTML"
    )
    await callback.answer()


async def _handle_my_sub(callback: CallbackQuery):
    """🔑 Моя подписка."""
    from datetime import datetime
    from xui_client import XUIClient
    from keyboards import subscription_keyboard

    user = await get_user(callback.from_user.id)

    if not user or user["status"] != "active":
        await callback.answer("У тебя нет активной подписки", show_alert=True)
        return

    async with XUIClient() as xui:
        sub_url = xui.build_sub_url(user["sub_id"])
        client = await xui.get_client(user["xui_email"])

        expiry = client.get("expiryTime", 0)
        if expiry > 0:
            exp_dt = datetime.fromtimestamp(expiry / 1000)
            exp_date = exp_dt.strftime("%d.%m.%Y")
            days_left = (exp_dt - datetime.now()).days
            if days_left < 0:
                status_line = f"⚠️ Истекла {exp_date}"
            elif days_left <= 3:
                status_line = f"⏳ Истекает через {days_left} дн. ({exp_date})"
            else:
                status_line = f"📅 До {exp_date} ({days_left} дн.)"
        else:
            status_line = "📅 Бессрочно"

        traffic_up = client.get("up", 0) / (1024**3)
        traffic_down = client.get("down", 0) / (1024**3)

    await callback.message.edit_text(
        f"🔑 <b>Твоя подписка</b>\n\n"
        f"🔗 Ссылка:\n<code>{sub_url}</code>\n\n"
        f"{status_line}\n"
        f"📱 Лимит: 3 IP одновременно\n"
        f"📊 Трафик: ↓{traffic_down:.2f} GB / ↑{traffic_up:.2f} GB\n\n"
        f"{DONATE_TEXT}",
        reply_markup=subscription_keyboard(),
        parse_mode="HTML"
    )
    await callback.answer()


async def _handle_invite(callback: CallbackQuery):
    """👥 Пригласить пользователя."""
    from keyboards import share_keyboard
    from config import BOT_USERNAME

    user = await get_user(callback.from_user.id)

    if not user:
        await callback.answer("Сначала получи подписку", show_alert=True)
        return

    invites = user["invites_count"] if user["invites_count"] else 0
    ref_link = f"https://t.me/{BOT_USERNAME}?start=ref_{callback.from_user.id}"

    await callback.message.edit_text(
        f"👥 <b>Пригласи пользователя</b>\n\n"
        f"Твоя ссылка:\n<code>{ref_link}</code>\n\n"
        f"📊 Ты уже пригласил: {invites} чел.\n\n"
        f"💡 Отправь ссылку друзьям — они получат бесплатный VPN.",
        reply_markup=share_keyboard(BOT_USERNAME, callback.from_user.id),
        parse_mode="HTML"
    )
    await callback.answer()


async def _handle_invite_no_tg(callback: CallbackQuery):
    """➕ Добавить без Telegram — показываем ReplyKeyboard для выбора контакта."""
    from keyboards import invite_contact_keyboard

    user = await get_user(callback.from_user.id)

    if not user or user["status"] != "active":
        await callback.answer("Сначала получи подписку", show_alert=True)
        return

    # Удаляем сообщение с inline-меню, отправляем новое с ReplyKeyboard
    await callback.message.delete()
    await callback.message.answer(
        "➕ <b>Добавить пользователя без Telegram</b>\n\n"
        "Нажми «👤 Выбрать из контактов» — выбери человека из списка Telegram.\n"
        "Я получу его ID и username автоматически.\n\n"
        "⏳ После выбора создам одноразовую ссылку на 7 дней.",
        parse_mode="HTML",
        reply_markup=invite_contact_keyboard()
    )
    await callback.answer()
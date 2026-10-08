import logging
from datetime import datetime

import aiosqlite
from aiogram import Router, F, Bot
from aiogram.types import Message, CallbackQuery
from aiogram.fsm.context import FSMContext

from config import ADMIN_IDS, DONATE_TEXT, DB_PATH
from database import (
    get_user, create_user_request, approve_user, renew_user
)
from xui_client import XUIClient
from keyboards import (
    admin_approve_keyboard, subscription_keyboard, donate_keyboard,
    terms_keyboard
)
from .utils import sanitize_email, TERMS_TEXT
from .states import RegStates

router = Router()
logger = logging.getLogger(__name__)


# ============================================================
# ЗАЯВКА НА ПОДПИСКУ
# ============================================================

@router.message(F.text == "📦 Получить подписку")
async def request_subscription(message: Message, state: FSMContext):
    user = await get_user(message.from_user.id)

    if user and user["status"] == "active":
        await message.answer("У тебя уже есть активная подписка. Используй «🔑 Моя подписка».")
        return

    if user and user["status"] == "pending":
        await message.answer("⏳ Заявка уже отправлена. Жди одобрения админа.")
        return

    # Показываем соглашение
    await message.answer(
        TERMS_TEXT,
        reply_markup=terms_keyboard(),
        parse_mode="HTML"
    )


@router.callback_query(F.data == "accept_terms")
async def accept_terms(callback: CallbackQuery):
    user = await get_user(callback.from_user.id)

    if user and user["status"] == "active":
        await callback.answer("У тебя уже есть подписка", show_alert=True)
        return

    if user and user["status"] == "pending":
        await callback.answer("Заявка уже отправлена", show_alert=True)
        return

    name = callback.from_user.username or callback.from_user.first_name or f"user{callback.from_user.id}"
    xui_email = sanitize_email(name)

    invited_by = user["invited_by"] if user else None

    await create_user_request(
        callback.from_user.id,
        callback.from_user.username or "",
        callback.from_user.first_name or "",
        xui_email,
        invited_by=invited_by
    )

    for admin_id in ADMIN_IDS:
        try:
            await callback.bot.send_message(
                admin_id,
                f"🆕 Новая заявка на подписку\n\n"
                f"Пользователь: {callback.from_user.full_name}\n"
                f"Username: @{callback.from_user.username or 'нет'}\n"
                f"ID: {callback.from_user.id}\n"
                f"Email в 3x-ui: {xui_email}\n"
                f"✅ Согласие с условиями: да",
                reply_markup=admin_approve_keyboard(callback.from_user.id)
            )
        except Exception as e:
            logger.error(f"❌ Ошибка уведомления админу {admin_id}: {e}")

    await callback.message.edit_text(
        "✅ Спасибо! Заявка отправлена.\n\n"
        "Жди одобрения админа — обычно это занимает несколько минут."
    )
    await callback.answer()


@router.callback_query(F.data == "decline_terms")
async def decline_terms(callback: CallbackQuery):
    await callback.message.edit_text(
        "❌ Ты не принял условия. Подписка не может быть выдана.\n\n"
        "Если передумаешь — нажми «📦 Получить подписку» снова."
    )
    await callback.answer()


@router.callback_query(F.data.startswith("approve:"))
async def approve_callback(callback: CallbackQuery):
    if callback.from_user.id not in ADMIN_IDS:
        await callback.answer("Не твоя кнопка", show_alert=True)
        return

    telegram_id = int(callback.data.split(":")[1])
    user = await get_user(telegram_id)

    if not user:
        await callback.answer("Пользователь не найден", show_alert=True)
        return

    if user["status"] == "active":
        await callback.answer("⚠️ Заявка уже одобрена", show_alert=True)
        await callback.message.edit_text(
            f"⚠️ Заявка уже одобрена\n\n"
            f"Пользователь: {user['first_name']}\n"
            f"Email: {user['xui_email']}"
        )
        return

    if user["status"] != "pending":
        await callback.answer(f"Неверный статус: {user['status']}", show_alert=True)
        return

    try:
        async with XUIClient() as xui:
            sub_id = await xui.add_client(user["xui_email"])
            await approve_user(telegram_id, sub_id)
            sub_url = xui.build_sub_url(sub_id)

        await callback.message.edit_text(
            f"✅ Заявка одобрена\n\n"
            f"Пользователь: {user['first_name']}\n"
            f"Email: {user['xui_email']}\n"
            f"Sub ID: {sub_id}"
        )

        await callback.bot.send_message(
            telegram_id,
            f"🎉 Твоя подписка готова!\n\n"
            f"🔗 Ссылка на подписку:\n`{sub_url}`\n\n"
            f"📱 Лимит: 3 IP одновременно.\n"
            f"⏳ Срок: 30 дней. Продлить можно через «🔑 Моя подписка».\n\n"
            f"📢 Помоги проекту расти — пригласи друзей.\n\n"
            f"{DONATE_TEXT}",
            reply_markup=subscription_keyboard(),
            parse_mode="Markdown"
        )

    except Exception as e:
        logger.error(f"❌ Ошибка при одобрении {user['xui_email']}: {e}")
        await callback.message.edit_text(f"❌ Ошибка: {e}")
        await callback.answer("Ошибка при создании клиента", show_alert=True)


@router.callback_query(F.data.startswith("reject:"))
async def reject_callback(callback: CallbackQuery):
    if callback.from_user.id not in ADMIN_IDS:
        await callback.answer("Не твоя кнопка", show_alert=True)
        return

    telegram_id = int(callback.data.split(":")[1])
    await callback.message.edit_text("❌ Заявка отклонена")
    await callback.answer("Отклонено")


# ============================================================
# МОЯ ПОДПИСКА И ПРОДЛЕНИЕ
# ============================================================

@router.message(F.text == "🔑 Моя подписка")
async def my_subscription(message: Message):
    user = await get_user(message.from_user.id)

    if not user or user["status"] != "active":
        await message.answer("У тебя нет активной подписки. Нажми «📦 Получить подписку».")
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

    await message.answer(
        f"🔑 Твоя подписка\n\n"
        f"🔗 Ссылка:\n`{sub_url}`\n\n"
        f"{status_line}\n"
        f"📱 Лимит: 3 IP одновременно\n"
        f"📊 Трафик: ↓{traffic_down:.2f} GB / ↑{traffic_up:.2f} GB\n\n"
        f"Хочешь продлить — жми «🔄 Продлить».\n"
        f"Первый раз подключаешься? Жми «📖 Как подключиться».\n\n"
        f"{DONATE_TEXT}",
        reply_markup=subscription_keyboard(),
        parse_mode="Markdown"
    )


@router.callback_query(F.data == "renew")
async def renew_callback(callback: CallbackQuery):
    user = await get_user(callback.from_user.id)

    if not user or user["status"] != "active":
        await callback.answer("Нет активной подписки", show_alert=True)
        return

    try:
        async with XUIClient() as xui:
            new_expiry = await xui.update_expiry(user["xui_email"])

        await renew_user(callback.from_user.id, new_expires=new_expiry)
        exp_date = new_expiry.strftime("%d.%m.%Y")

        await callback.message.edit_text(
            f"✅ Подписка продлена!\n\n"
            f"📅 Новая дата окончания: {exp_date}\n"
            f"🔗 Ссылка та же.\n\n"
            f"{DONATE_TEXT}",
            reply_markup=donate_keyboard()
        )

    except Exception as e:
        await callback.answer(f"Ошибка: {e}", show_alert=True)
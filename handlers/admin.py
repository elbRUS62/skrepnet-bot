import asyncio
import logging
from datetime import datetime, timedelta

import aiosqlite
from aiogram import Router, F, Bot
from aiogram.types import Message, CallbackQuery
from aiogram.fsm.context import FSMContext
from aiogram.filters import Command

from config import ADMIN_IDS, DB_PATH
from database import (
    get_user_by_username, is_admin, add_admin, remove_admin,
    get_all_admins, delete_user, renew_user
)
from xui_client import XUIClient
from keyboards import (
    admin_menu, admin_manage_keyboard, admin_approve_keyboard,
    admin_panel_keyboard
)
from .states import AdminStates

router = Router()
logger = logging.getLogger(__name__)


# ============================================================
# СТАТИСТИКА
# ============================================================

@router.message(Command("stats"))
@router.message(F.text == "📊 Статистика")
async def cmd_stats(message: Message):
    if message.from_user.id not in ADMIN_IDS:
        return

    async with aiosqlite.connect(DB_PATH) as db:
        db.row_factory = aiosqlite.Row

        async with db.execute("SELECT COUNT(*) as c FROM users") as cur:
            total = (await cur.fetchone())["c"]

        async with db.execute("SELECT COUNT(*) as c FROM users WHERE status = 'active'") as cur:
            active = (await cur.fetchone())["c"]

        async with db.execute("SELECT COUNT(*) as c FROM users WHERE status = 'pending'") as cur:
            pending = (await cur.fetchone())["c"]

        async with db.execute(
            "SELECT COUNT(*) as c FROM users WHERE status = 'active' AND DATE(expires_at) <= DATE('now', '+3 days')"
        ) as cur:
            expiring = (await cur.fetchone())["c"]

        async with db.execute("SELECT SUM(invites_count) as s FROM users") as cur:
            row = await cur.fetchone()
            total_invites = row["s"] or 0

    await message.answer(
        f"📊 <b>Статистика SkrepNet</b>\n\n"
        f"👥 Всего: {total}\n"
        f"✅ Активных: {active}\n"
        f"⏳ Ожидают: {pending}\n"
        f"⏰ Истекают через 3 дня: {expiring}\n"
        f"📢 Приглашений: {total_invites}",
        parse_mode="HTML"
    )


# ============================================================
# МЕНЮ УПРАВЛЕНИЯ
# ============================================================

@router.message(F.text == "🛠 Управление")
async def admin_manage(message: Message):
    if message.from_user.id not in ADMIN_IDS:
        return
    await message.answer(
        "🛠 <b>Управление ботом</b>\n\nВыбери действие:",
        reply_markup=admin_manage_keyboard(),
        parse_mode="HTML"
    )


@router.callback_query(F.data == "admin_close")
async def admin_close(callback: CallbackQuery):
    if callback.from_user.id not in ADMIN_IDS:
        return
    await callback.message.delete()
    await callback.answer()


# ============================================================
# ДОБАВЛЕНИЕ АДМИНА
# ============================================================

@router.callback_query(F.data == "admin_add")
async def admin_add_start(callback: CallbackQuery, state: FSMContext):
    if callback.from_user.id not in ADMIN_IDS:
        return
    await callback.message.edit_text(
        "👤 Введи <b>username</b> пользователя (без @):\n\n"
        "Например: <code>ivan_petrov</code>",
        parse_mode="HTML"
    )
    await state.set_state(AdminStates.waiting_add_admin)
    await callback.answer()


@router.message(AdminStates.waiting_add_admin)
async def admin_add_process(message: Message, state: FSMContext):
    if message.from_user.id not in ADMIN_IDS:
        return

    username = message.text.strip().lstrip("@")
    user = await get_user_by_username(username)

    if not user:
        await message.answer(
            f"❌ @{username} не найден в базе.\n"
            f"Он должен сначала написать боту /start.",
            reply_markup=admin_menu()
        )
        await state.clear()
        return

    # Проверка, не из .env ли этот админ
    if user["telegram_id"] in ADMIN_IDS:
        await message.answer(
            f"⚠️ @{username} уже является основным админом (из .env).",
            reply_markup=admin_menu()
        )
        await state.clear()
        return

    await add_admin(user["telegram_id"], username, message.from_user.id)
    await message.answer(
        f"✅ @{username} (ID {user['telegram_id']}) добавлен в админы.",
        reply_markup=admin_menu()
    )

    try:
        await message.bot.send_message(
            user["telegram_id"],
            "🎉 Тебя назначили админом SkrepNet!\n\n"
            "В меню появится кнопка «🛠 Управление»."
        )
    except Exception:
        pass

    await state.clear()


# ============================================================
# УДАЛЕНИЕ АДМИНА
# ============================================================

@router.callback_query(F.data == "admin_del")
async def admin_del_start(callback: CallbackQuery, state: FSMContext):
    if callback.from_user.id not in ADMIN_IDS:
        return
    await callback.message.edit_text(
        "🗑 Введи <b>username</b> админа для удаления (без @):",
        parse_mode="HTML"
    )
    await state.set_state(AdminStates.waiting_del_admin)
    await callback.answer()


@router.message(AdminStates.waiting_del_admin)
async def admin_del_process(message: Message, state: FSMContext):
    if message.from_user.id not in ADMIN_IDS:
        return

    username = message.text.strip().lstrip("@")
    user = await get_user_by_username(username)

    if user and user["telegram_id"] in ADMIN_IDS:
        await message.answer(
            f"⚠️ @{username} — основной админ (из .env).\n\n"
            f"Его нельзя удалить через бота. Убери его ID из ADMIN_ID в .env "
            f"и перезапусти бота.",
            reply_markup=admin_menu()
        )
        await state.clear()
        return

    success = await remove_admin(username)

    if success:
        await message.answer(f"✅ @{username} удалён из админов.", reply_markup=admin_menu())
    else:
        await message.answer(
            f"❌ @{username} не найден в списке админов, добавленных через бота.",
            reply_markup=admin_menu()
        )

    await state.clear()


# ============================================================
# СПИСОК АДМИНОВ
# ============================================================

@router.callback_query(F.data == "admin_list")
async def admin_list(callback: CallbackQuery):
    if callback.from_user.id not in ADMIN_IDS:
        return

    text = "👤 <b>Список админов</b>\n\n"
    text += "<b>Основные (.env):</b>\n"
    for aid in ADMIN_IDS:
        text += f"  • <code>{aid}</code>\n"

    extra = await get_all_admins()
    if extra:
        text += "\n<b>Добавленные через бота:</b>\n"
        for adm in extra:
            text += f"  • @{adm['username']} (<code>{adm['telegram_id']}</code>)\n"

    await callback.message.edit_text(
        text,
        parse_mode="HTML",
        reply_markup=admin_manage_keyboard()
    )
    await callback.answer()


# ============================================================
# ОБНОВЛЕНИЕ ПОДПИСКИ
# ============================================================

@router.callback_query(F.data == "admin_extend")
async def admin_extend_start(callback: CallbackQuery, state: FSMContext):
    if callback.from_user.id not in ADMIN_IDS:
        return
    await callback.message.edit_text(
        "🔄 Введи <b>username</b> пользователя, которому хочешь обновить подписку (без @):",
        parse_mode="HTML"
    )
    await state.set_state(AdminStates.waiting_extend_username)
    await callback.answer()


@router.message(AdminStates.waiting_extend_username)
async def admin_extend_get_days(message: Message, state: FSMContext):
    if message.from_user.id not in ADMIN_IDS:
        return

    username = message.text.strip().lstrip("@")
    user = await get_user_by_username(username)

    if not user:
        await message.answer(f"❌ @{username} не найден.", reply_markup=admin_menu())
        await state.clear()
        return

    if user["status"] != "active":
        await message.answer(f"❌ У @{username} нет активной подписки.", reply_markup=admin_menu())
        await state.clear()
        return

    await state.update_data(target_username=username, target_user=dict(user))
    await message.answer(
        f"👤 Пользователь: @{username}\n\n"
        f"На сколько <b>дней</b> обновить подписку?",
        parse_mode="HTML"
    )
    await state.set_state(AdminStates.waiting_extend_days)


@router.message(AdminStates.waiting_extend_days)
async def admin_extend_process(message: Message, state: FSMContext):
    if message.from_user.id not in ADMIN_IDS:
        return

    try:
        days = int(message.text.strip())
        if days < 1 or days > 3650:
            raise ValueError
    except ValueError:
        await message.answer("❌ Введи число от 1 до 3650.")
        return

    data = await state.get_data()
    user = data["target_user"]

    try:
        async with XUIClient() as xui:
            client = await xui.get_client(user["xui_email"])
            current_expiry = client.get("expiryTime", 0)

            if current_expiry and current_expiry > 0:
                current_dt = datetime.fromtimestamp(current_expiry / 1000)
                new_expiry = max(current_dt, datetime.now()) + timedelta(days=days)
            else:
                new_expiry = datetime.now() + timedelta(days=days)

            expires_ms = int(new_expiry.timestamp() * 1000)
            await xui._post(f"/panel/api/clients/update/{user['xui_email']}", {
                "email": user["xui_email"],
                "expiryTime": expires_ms,
                "limitIp": 3,
                "enable": True,
                "totalGB": 0
            })

        await renew_user(user["telegram_id"], new_expires=new_expiry)

        await message.answer(
            f"✅ @{user['username']}: подписка обновлена — {days} дней.\n"
            f"📅 Новая дата окончания: {new_expiry.strftime('%d.%m.%Y')}",
            reply_markup=admin_menu()
        )

        try:
            await message.bot.send_message(
                user["telegram_id"],
                f"🎁 Админ обновил твою подписку на {days} дней!\n"
                f"📅 Новая дата: {new_expiry.strftime('%d.%m.%Y')}"
            )
        except Exception:
            pass

    except Exception as e:
        await message.answer(f"❌ Ошибка: {e}", reply_markup=admin_menu())

    await state.clear()


# ============================================================
# СБРОС ЗАЯВКИ
# ============================================================

@router.callback_query(F.data == "admin_reset")
async def admin_reset_start(callback: CallbackQuery, state: FSMContext):
    if callback.from_user.id not in ADMIN_IDS:
        return
    await callback.message.edit_text(
        "♻️ Введи <b>username</b> пользователя (без @):",
        parse_mode="HTML"
    )
    await state.set_state(AdminStates.waiting_reset_username)
    await callback.answer()


@router.message(AdminStates.waiting_reset_username)
async def admin_reset_process(message: Message, state: FSMContext):
    if message.from_user.id not in ADMIN_IDS:
        return

    username = message.text.strip().lstrip("@")
    user = await get_user_by_username(username)

    if not user:
        await message.answer(f"❌ @{username} не найден.", reply_markup=admin_menu())
        await state.clear()
        return

    await delete_user(user["telegram_id"])
    await message.answer(
        f"✅ @{username} удалён из базы.\n\n"
        f"⚠️ Не забудь удалить клиента в панели 3x-ui.",
        reply_markup=admin_menu()
    )
    await state.clear()


# ============================================================
# РАССЫЛКА
# ============================================================

@router.callback_query(F.data == "admin_broadcast")
async def admin_broadcast_start(callback: CallbackQuery, state: FSMContext):
    if callback.from_user.id not in ADMIN_IDS:
        return
    await callback.message.edit_text("📢 Введи текст для рассылки:")
    await state.set_state(AdminStates.waiting_broadcast_text)
    await callback.answer()


@router.message(AdminStates.waiting_broadcast_text)
async def admin_broadcast_process(message: Message, state: FSMContext):
    if message.from_user.id not in ADMIN_IDS:
        return

    text = message.text.strip()

    async with aiosqlite.connect(DB_PATH) as db:
        db.row_factory = aiosqlite.Row
        async with db.execute("SELECT telegram_id FROM users WHERE status = 'active'") as cur:
            users = await cur.fetchall()

    sent = 0
    failed = 0
    for u in users:
        try:
            await message.bot.send_message(u["telegram_id"], text, disable_notification=True)
            sent += 1
        except Exception:
            failed += 1
        await asyncio.sleep(0.05)

    await message.answer(
        f"📢 Рассылка завершена\n\n"
        f"✅ Отправлено: {sent}\n"
        f"❌ Не доставлено: {failed}",
        reply_markup=admin_menu()
    )
    await state.clear()

# ============================================================
# ССЫЛКА НА ПАНЕЛЬ 3x-ui
# ============================================================

@router.callback_query(F.data == "admin_panel")
async def admin_panel_link(callback: CallbackQuery):
    if callback.from_user.id not in ADMIN_IDS:
        await callback.answer("Не твоя кнопка", show_alert=True)
        return

    await callback.message.answer(
        "🔐 <b>Вход в панель 3x-ui</b>\n\n"
        "Нажми кнопку ниже — браузер откроет страницу входа.\n"
        "Пароль подставит менеджер паролей, если он у тебя есть.",
        reply_markup=admin_panel_keyboard(),
        parse_mode="HTML"
    )
    await callback.answer()

# ============================================================
# УДАЛЕНИЕ ПОЛЬЗОВАТЕЛЯ (БД + 3x-ui)
# ============================================================

@router.callback_query(F.data == "admin_delete_user")
async def admin_delete_user_start(callback: CallbackQuery, state: FSMContext):
    if callback.from_user.id not in ADMIN_IDS:
        return
    await callback.message.edit_text(
        "🗑 Введи <b>username</b> пользователя, которого хочешь удалить (без @):\n\n"
        "⚠️ Он будет удалён из базы бота и из панели 3x-ui.",
        parse_mode="HTML"
    )
    await state.set_state(AdminStates.waiting_delete_username)
    await callback.answer()


@router.message(AdminStates.waiting_delete_username)
async def admin_delete_user_process(message: Message, state: FSMContext):
    if message.from_user.id not in ADMIN_IDS:
        return

    username = message.text.strip().lstrip("@")
    user = await get_user_by_username(username)

    if not user:
        await message.answer(
            f"❌ @{username} не найден в базе.",
            reply_markup=admin_menu()
        )
        await state.clear()
        return

    xui_email = user["xui_email"]
    telegram_id = user["telegram_id"]

    # Удаляем из 3x-ui
    xui_ok = False
    xui_error = None
    try:
        async with XUIClient() as xui:
            xui_ok = await xui.delete_client(xui_email)
    except Exception as e:
        xui_error = str(e)

    # Удаляем из базы бота
    await delete_user(telegram_id)

    # Формируем отчёт
    text = f"🗑 <b>Удаление @{username}</b>\n\n"
    text += f"📧 Email в 3x-ui: <code>{xui_email}</code>\n"
    text += f"🆔 Telegram ID: <code>{telegram_id}</code>\n\n"

    if xui_ok:
        text += "✅ Удалён из 3x-ui\n"
    elif xui_error:
        text += f"⚠️ Ошибка 3x-ui: {xui_error}\n"
    else:
        text += "⚠️ В 3x-ui клиент не найден (возможно, уже удалён)\n"

    text += "✅ Удалён из базы бота"

    await message.answer(text, reply_markup=admin_menu(), parse_mode="HTML")
    await state.clear()
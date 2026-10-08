from aiogram import Router, F
from aiogram.types import Message, CallbackQuery
from aiogram.filters import Command

from config import ADMIN_IDS
from keyboards import changelog_keyboard

router = Router()


CHANGELOG = [
    {
        "version": "1.4",
        "date": "08.10.2026",
        "changes": [
            "📜 Соглашение с пользователем при получении подписки",
            "🛠 Отдельное меню «Управление» для админов (всё на кнопках)",
            "👤 Добавление админов по username",
            "🗑 Удаление админов по username (с защитой .env-админов)",
            "📋 Просмотр списка админов",
            "🔄 Обновление подписки по username",
            "🗑 Удаление пользователя по username (из БД и 3x-ui одновременно)",
            "♻️ Сброс заявки по username",
            "📢 Рассылка по кнопке",
            "🔐 Кнопка входа в панель 3x-ui из бота",
            "📋 История обновлений бота",
            "🧩 Разбивка handlers на модули (start, subscription, donate, connect, admin, changelog)",
        ]
    },
    {
        "version": "1.3",
        "date": "07.10.2026",
        "changes": [
            "⭐ Донат через Telegram Stars (10, 25, 50, 100 звёзд)",
            "📖 Инструкции для 6 платформ: Android, iOS, Windows, macOS, Android TV, Linux",
            "🍎 Happ — основное рекомендуемое приложение",
            "📺 Отдельные инструкции для Android TV (через v2rayTun или Happ APK)",
            "🐧 Linux — сборки Happ (.deb, .rpm, .AppImage)",
            "🛡️ Защита от спама при заявке (по статусу pending)",
            "🗑 Автоудаление неактивных пользователей (30+ дней)",
            "📦 Кастомная страница подписки с автообновлением",
        ]
    },
    {
        "version": "1.2",
        "date": "07.10.2026",
        "changes": [
            "📊 Админ-команда /stats",
            "👥 Реферальная система с кнопкой «Поделиться»",
            "❤️ Плашка доната при каждом взаимодействии",
            "🔔 Напоминания за 3 дня и в день окончания (тихие)",
            "💾 Ежедневные бэкапы базы (в 3:00, хранение 30 дней)",
            "🔧 Systemd-автозапуск (бот сам поднимается после падения)",
            "📝 Логирование уведомлений админам",
            "👥 Второй админ получает уведомления",
        ]
    },
    {
        "version": "1.1",
        "date": "07.10.2026",
        "changes": [
            "🤖 Бот перенесён на зарубежный сервер (нет блокировок Telegram)",
            "🔑 API-токен 3x-ui (Bearer) вместо логина по паролю",
            "🆔 Генерация subId вручную (обход бага 3x-ui)",
            "⚙️ Продление подписки по кнопке (без автопродления)",
            "🔗 Ссылка на подписку через встроенную систему 3x-ui",
        ]
    },
    {
        "version": "1.0",
        "date": "07.10.2026",
        "changes": [
            "🎉 Первая версия бота",
            "📦 Выдача подписок Hysteria2 (2 сервера: 🇬🇧 + 🇱🇻)",
            "👤 Одобрение админом при первой заявке",
            "📱 Лимит 3 IP одновременно",
            "⏳ Срок подписки — 30 дней",
        ]
    },
]


@router.message(Command("changelog"))
@router.message(F.text == "📋 История обновлений")
async def cmd_changelog(message: Message):
    if message.from_user.id not in ADMIN_IDS:
        return
    await message.answer(
        "📋 <b>История обновлений SkrepNet</b>\n\n"
        "Нажми кнопку ниже, чтобы посмотреть все версии и изменения.",
        reply_markup=changelog_keyboard(),
        parse_mode="HTML"
    )


@router.callback_query(F.data == "show_changelog")
async def show_changelog(callback: CallbackQuery):
    if callback.from_user.id not in ADMIN_IDS:
        await callback.answer("Не твоя кнопка", show_alert=True)
        return

    text = "📋 <b>История обновлений SkrepNet</b>\n\n"
    for entry in CHANGELOG:
        text += f"<b>v{entry['version']}</b> — {entry['date']}\n"
        for change in entry["changes"]:
            text += f"  • {change}\n"
        text += "\n"

    # Если текст слишком длинный — Telegram может не принять (>4096 символов)
    # Разбиваем на части, если нужно
    if len(text) > 4000:
        parts = []
        current = "📋 <b>История обновлений SkrepNet</b>\n\n"
        for entry in CHANGELOG:
            block = f"<b>v{entry['version']}</b> — {entry['date']}\n"
            for change in entry["changes"]:
                block += f"  • {change}\n"
            block += "\n"

            if len(current) + len(block) > 4000:
                parts.append(current)
                current = block
            else:
                current += block

        if current:
            parts.append(current)

        await callback.message.edit_text(parts[0], parse_mode="HTML")
        for part in parts[1:]:
            await callback.message.answer(part, parse_mode="HTML")
    else:
        await callback.message.edit_text(text, parse_mode="HTML")

    await callback.answer()
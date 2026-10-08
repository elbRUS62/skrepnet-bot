from apscheduler.schedulers.asyncio import AsyncIOScheduler
from aiogram import Bot

from database import (
    get_expiring_users, get_expired_today, mark_notified,
    get_inactive_users, delete_user
)
from keyboards import renew_keyboard
from xui_client import XUIClient
from config import DONATE_TEXT, ADMIN_ID

scheduler = AsyncIOScheduler()


def setup_scheduler(bot: Bot):
    # Напоминания о продлении — каждый день в 10:00
    scheduler.add_job(
        check_subscriptions,
        "cron",
        hour=10,
        minute=0,
        args=[bot],
        id="check_subscriptions"
    )

    # Автоочистка неактивных — каждый день в 4:00
    scheduler.add_job(
        cleanup_inactive_users,
        "cron",
        hour=4,
        minute=0,
        args=[bot],
        id="cleanup_inactive_users"
    )

    scheduler.start()


async def check_subscriptions(bot: Bot):
    """Напоминания за 3 дня и в день окончания. НЕ продлеваем автоматически."""

    # За 3 дня
    for user in await get_expiring_users(3):
        try:
            await bot.send_message(
                user["telegram_id"],
                f"⏳ Привет! Твоя подписка SkrepNet истекает через 3 дня.\n\n"
                f"Чтобы продолжить пользоваться — зайди и продли её. "
                f"Это займёт 5 секунд.\n\n"
                f"💡 Проект бесплатный, но сервер стоит ~3000 ₽/мес. "
                f"Если есть возможность — поддержи ❤️\n\n"
                f"{DONATE_TEXT}",
                reply_markup=renew_keyboard(),
                disable_notification=True
            )
            await mark_notified(user["telegram_id"], "notified_3d")
        except Exception:
            pass

    # В день окончания
    for user in await get_expired_today():
        try:
            await bot.send_message(
                user["telegram_id"],
                f"🔔 Сегодня последний день твоей подписки SkrepNet!\n\n"
                f"После полуночи доступ отключится. Продли прямо сейчас, "
                f"чтобы не остаться без VPN.\n\n"
                f"💡 И помни: проект держится только на поддержке. "
                f"Если можешь — помоги серверу ❤️\n\n"
                f"{DONATE_TEXT}",
                reply_markup=renew_keyboard(),
                disable_notification=True
            )
            await mark_notified(user["telegram_id"], "notified_0d")
        except Exception as e:
            try:
                await bot.send_message(
                    ADMIN_ID,
                    f"⚠️ Ошибка напоминания для {user['xui_email']}: {e}"
                )
            except Exception:
                pass


async def cleanup_inactive_users(bot: Bot):
    """Удаляет пользователей, у которых подписка истекла более 30 дней назад."""
    users = await get_inactive_users(days=30)

    if not users:
        return

    deleted = 0
    for user in users:
        try:
            # Удаляем клиента из 3x-ui
            async with XUIClient() as xui:
                try:
                    await xui._post(f"/panel/api/clients/del/{user['xui_email']}")
                except Exception:
                    pass

            await delete_user(user["telegram_id"])
            deleted += 1
        except Exception as e:
            print(f"Ошибка удаления {user['xui_email']}: {e}")

    if deleted:
        try:
            await bot.send_message(
                ADMIN_ID,
                f"🗑 Автоочистка: удалено {deleted} неактивных пользователей "
                f"(подписка истекла 30+ дней назад).",
                disable_notification=True
            )
        except Exception:
            pass
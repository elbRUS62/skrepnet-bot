import asyncio
import logging
import os
from aiogram import Bot, Dispatcher
from config import BOT_TOKEN, ADMIN_IDS
from handlers import router
from scheduler import setup_scheduler
from database import init_db
from donation_socket import start_donation_socket

logging.basicConfig(level=logging.INFO)

async def main():
    await init_db()

    bot = Bot(token=BOT_TOKEN)
    dp = Dispatcher()
    dp.include_router(router)

    setup_scheduler(bot)

    # Запускаем DonationAlerts WebSocket в фоне
    da_token = os.getenv("DONATION_ALERTS_TOKEN", "")
    if da_token:
        asyncio.create_task(start_donation_socket(bot, ADMIN_IDS, da_token))
        logging.info("? DonationAlerts Socket запущен в фоне")
    else:
        logging.warning("?? DONATION_ALERTS_TOKEN не задан — сокет не запущен")

    await dp.start_polling(bot)

if __name__ == "__main__":
    asyncio.run(main())
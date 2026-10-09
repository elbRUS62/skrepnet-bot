import asyncio
import json
import logging
import websockets
import httpx
from aiogram import Bot

logger = logging.getLogger(__name__)


class DonationAlertsCentrifugo:
    def __init__(self, access_token: str):
        self.access_token = access_token
        self.bot = None
        self.admin_ids = []
        self.user_id = None
        self.socket_token = None
        self.centrifugo_url = "wss://centrifugo.donationalerts.com/connection/websocket"
        self.api_base = "https://www.donationalerts.com/api/v1"
        self.headers = {"Authorization": f"Bearer {access_token}"}

    async def _get_user_info(self):
        async with httpx.AsyncClient() as client:
            resp = await client.get(f"{self.api_base}/user/oauth", headers=self.headers)
            resp.raise_for_status()
            data = resp.json()["data"]
            self.user_id = data["id"]
            self.socket_token = data["socket_connection_token"]
            logger.info(f"Получен user_id: {self.user_id}")

    async def _subscribe_to_channel(self, ws, client_id: str):
        channel = f"$alerts:donation_{self.user_id}"

        async with httpx.AsyncClient() as client:
            resp = await client.post(
                f"{self.api_base}/centrifuge/subscribe",
                headers=self.headers,
                json={"channels": [channel], "client": client_id}
            )
            resp.raise_for_status()
            sub_data = resp.json()

            if "channels" not in sub_data:
                raise Exception(f"Нет channels: {sub_data}")

            channel_token = sub_data["channels"][0]["token"]

        await ws.send(json.dumps({
            "params": {"channel": channel, "token": channel_token},
            "method": 1,
            "id": 2
        }))
        logger.info(f"Подписка на канал: {channel}")

    async def _handle_donation(self, data: dict):
        try:
            logger.info(f"Донат data: {data}")
            username = data.get("username") or "Аноним"
            amount = data.get("amount", 0)
            currency = data.get("currency", "RUB")
            message = data.get("message", "")

            currency_emoji = {
                "RUB": "₽",
                "USD": "$",
                "EUR": "€",
                "BYN": "Br",
                "KZT": "₸",
                "UAH": "₴",
            }.get(currency, currency)

            logger.info(f"Новый донат: {username} - {amount} {currency}")
            logger.info(f"Admin IDs: {self.admin_ids}")

            text = (
                f"💰 <b>Новый донат!</b>\n"
                f"━━━━━━━━━━━━━━━━━━━━\n\n"
                f"👤 <b>От:</b> {username}\n"
                f"💵 <b>Сумма:</b> <code>{amount} {currency_emoji}</code>\n"
            )

            if message:
                text += f"\n💬 <b>Сообщение:</b>\n<i>{message}</i>"

            for admin_id in self.admin_ids:
                logger.info(f"Отправляю админу {admin_id}...")
                try:
                    result = await self.bot.send_message(
                        admin_id,
                        text,
                        parse_mode="HTML",
                        disable_notification=True
                    )
                    logger.info(f"✅ Отправлено админу {admin_id}: message_id={result.message_id}")
                except Exception as e:
                    logger.error(f"❌ Ошибка отправки админу {admin_id}: {type(e).__name__}: {e}")
        except Exception as e:
            logger.error(f"❌ Ошибка обработки доната: {type(e).__name__}: {e}")

    async def start(self, bot: Bot, admin_ids: list):
        self.bot = bot
        self.admin_ids = admin_ids

        await self._get_user_info()

        async with websockets.connect(self.centrifugo_url) as ws:
            logger.info("Подключен к Centrifugo WebSocket")

            await ws.send(json.dumps({
                "params": {"token": self.socket_token},
                "id": 1
            }))

            auth_response = json.loads(await ws.recv())
            client_id = auth_response["result"]["client"]
            logger.info(f"Авторизован. Client ID: {client_id}")

            await self._subscribe_to_channel(ws, client_id)

            async for message in ws:
                try:
                    # Centrifugo может присылать несколько JSON через \n
                    for line in message.strip().split("\n"):
                        if not line.strip():
                            continue

                        data = json.loads(line)

                        result = data.get("result", {})
                        channel = result.get("channel", "")
                        if not channel.startswith("$alerts:donation_"):
                            continue

                        inner_data = result.get("data", {})
                        if "data" not in inner_data:
                            continue

                        donation = inner_data["data"]
                        await self._handle_donation(donation)

                except Exception as e:
                    logger.error(f"Ошибка обработки сообщения: {e}")


async def start_donation_socket(bot: Bot, admin_ids: list, token: str):
    if not token:
        logger.warning("DONATION_ALERTS_TOKEN не задан")
        return

    client = DonationAlertsCentrifugo(token)
    while True:
        try:
            await client.start(bot, admin_ids)
        except Exception as e:
            logger.error(f"Ошибка Centrifugo: {e}. Переподключение через 10 сек...")
            await asyncio.sleep(10)
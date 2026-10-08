import aiohttp
import random
import string
from datetime import datetime, timedelta
from config import (
    XUI_HOST, XUI_BASE_PATH, XUI_API_TOKEN,
    INBOUND_GB, INBOUND_LV, LIMIT_IP, SUBSCRIPTION_DAYS,
    SUB_BASE_URL, SUB_PATH
)

class XUIClient:
    def __init__(self):
        self.base_url = f"{XUI_HOST}{XUI_BASE_PATH}"
        self.session = None
        self.headers = {
            "Authorization": f"Bearer {XUI_API_TOKEN}",
            "Content-Type": "application/json"
        }

    async def __aenter__(self):
        self.session = aiohttp.ClientSession(headers=self.headers)
        return self

    async def __aexit__(self, *args):
        if self.session:
            await self.session.close()

    async def _post(self, path: str, data: dict = None):
        url = f"{self.base_url}{path}"
        async with self.session.post(url, json=data) as resp:
            if resp.status == 401:
                raise Exception("Unauthorized: API token is invalid or expired")
            return await resp.json()

    async def _get(self, path: str):
        url = f"{self.base_url}{path}"
        async with self.session.get(url) as resp:
            if resp.status == 401:
                raise Exception("Unauthorized: API token is invalid or expired")
            return await resp.json()

    async def add_client(self, email: str) -> str:
        """Создать клиента сразу в двух инбаундах."""
        expires_ms = int((datetime.now() + timedelta(days=SUBSCRIPTION_DAYS)).timestamp() * 1000)

        # Генерируем subId вручную (16 символов [0-9a-z])
        sub_id = ''.join(random.choices(string.ascii_lowercase + string.digits, k=16))

        payload = {
            "client": {
                "email": email,
                "enable": True,
                "expiryTime": expires_ms,
                "limitIp": LIMIT_IP,
                "totalGB": 0,
                "tgId": 0,
                "subId": sub_id
            },
            "inboundIds": [INBOUND_GB, INBOUND_LV]
        }
        result = await self._post("/panel/api/clients/add", payload)
        if not result.get("success"):
            raise Exception(f"Add client failed: {result}")
        return sub_id

    async def get_client(self, email: str) -> dict:
        """Получить данные клиента, включая subId."""
        result = await self._get(f"/panel/api/clients/get/{email}")
        if not result.get("success"):
            raise Exception(f"Get client failed: {result}")
        return result["obj"]

    async def update_expiry(self, email: str, days: int = SUBSCRIPTION_DAYS):
        """Продлить подписку."""
        client = await self.get_client(email)
        current_expiry = client.get("expiryTime", 0)
        if current_expiry and current_expiry > 0:
            current_dt = datetime.fromtimestamp(current_expiry / 1000)
            new_expiry = max(current_dt, datetime.now()) + timedelta(days=days)
        else:
            new_expiry = datetime.now() + timedelta(days=days)
        expires_ms = int(new_expiry.timestamp() * 1000)
        payload = {
            "email": email,
            "expiryTime": expires_ms,
            "limitIp": LIMIT_IP,
            "enable": True,
            "totalGB": 0
        }
        result = await self._post(f"/panel/api/clients/update/{email}", payload)
        if not result.get("success"):
            raise Exception(f"Update failed: {result}")
        return new_expiry

    async def delete_client(self, email: str) -> bool:
        """Удалить клиента из 3x-ui по email."""
        result = await self._post(f"/panel/api/clients/del/{email}")
        return result.get("success", False)
        
    def build_sub_url(self, sub_id: str) -> str:
        """Собрать ссылку на подписку."""
        return f"{SUB_BASE_URL}{SUB_PATH}{sub_id}"
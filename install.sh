#!/bin/bash
set -e

echo "============================================"
echo "  Установка SkrepNet Bot"
echo "============================================"
echo ""

# Проверка на root
if [ "$EUID" -ne 0 ]; then
    echo "⚠️  Запусти скрипт от root (sudo su)"
    exit 1
fi

# Проверка, что мы в правильной папке
if [ ! -f "bot.py" ]; then
    echo "❌ Файл bot.py не найден. Запусти скрипт из папки бота."
    exit 1
fi

# Проверка, что .env ещё нет
if [ -f ".env" ]; then
    echo "⚠️  Файл .env уже существует."
    read -p "Перезаписать? (y/N): " overwrite
    if [ "$overwrite" != "y" ] && [ "$overwrite" != "Y" ]; then
        echo "Отменено."
        exit 0
    fi
fi

echo ""
echo "--- Telegram ---"
read -p "BOT_TOKEN (от @BotFather): " BOT_TOKEN
read -p "ADMIN_ID (твой Telegram ID, можно несколько через запятую): " ADMIN_ID
read -p "BOT_USERNAME (без @, например skrepnet_bot): " BOT_USERNAME

echo ""
echo "--- 3x-ui Панель ---"
read -p "XUI_HOST (например https://ru-skrepnet.duckdns.org:3775): " XUI_HOST
read -p "XUI_BASE_PATH (например /MASbquuCRx18QVK8l6): " XUI_BASE_PATH
read -p "XUI_API_TOKEN (из Settings → Security): " XUI_API_TOKEN

echo ""
echo "--- Инбаунды 3x-ui ---"
read -p "XUI_INBOUND_GB (ID основного Hysteria2, например 5): " XUI_INBOUND_GB
read -p "XUI_INBOUND_LV (ID резервного, например 6): " XUI_INBOUND_LV

echo ""
echo "--- Подписка ---"
read -p "SUB_BASE_URL (например https://ru-skrepnet.duckdns.org:9913): " SUB_BASE_URL
read -p "SUB_PATH (например /subs_77dfgjn5jk78mkldxp77/): " SUB_PATH

echo ""
echo "--- Лимиты ---"
read -p "LIMIT_IP (по умолчанию 3): " LIMIT_IP_INPUT
LIMIT_IP=${LIMIT_IP_INPUT:-3}
read -p "SUBSCRIPTION_DAYS (по умолчанию 30): " SUBSCRIPTION_DAYS_INPUT
SUBSCRIPTION_DAYS=${SUBSCRIPTION_DAYS_INPUT:-30}

echo ""
echo "--- Донат ---"
read -p "DONATE_URL (ссылка на DonationAlerts): " DONATE_URL
read -p "DONATE_TEXT (текст плашки): " DONATE_TEXT

echo ""
echo "--- Создаю .env ---"

cat > .env <<EOF
# Telegram
BOT_TOKEN=$BOT_TOKEN
ADMIN_ID=$ADMIN_ID
BOT_USERNAME=$BOT_USERNAME

# 3x-ui Panel
XUI_API_TOKEN=$XUI_API_TOKEN
XUI_HOST=$XUI_HOST
XUI_BASE_PATH=$XUI_BASE_PATH

# Inbounds
XUI_INBOUND_GB=$XUI_INBOUND_GB
XUI_INBOUND_LV=$XUI_INBOUND_LV

# Subscription
SUB_BASE_URL=$SUB_BASE_URL
SUB_PATH=$SUB_PATH

# Limits
LIMIT_IP=$LIMIT_IP
SUBSCRIPTION_DAYS=$SUBSCRIPTION_DAYS

# Donate
DONATE_URL=$DONATE_URL
DONATE_TEXT=$DONATE_TEXT

# Database
DB_PATH=skrepnet.db
EOF

chmod 600 .env
echo "✅ .env создан"

echo ""
echo "--- Устанавливаю зависимости ---"
if [ ! -d "venv" ]; then
    python3 -m venv venv
fi
source venv/bin/activate
pip install --upgrade pip -q
pip install -r requirements.txt -q
echo "✅ Зависимости установлены"

echo ""
echo "--- Настраиваю systemd ---"
cat > /etc/systemd/system/skrepnet-bot.service <<EOF
[Unit]
Description=SkrepNet Telegram Bot
After=network.target

[Service]
Type=simple
User=root
WorkingDirectory=$(pwd)
Environment="PYTHONUNBUFFERED=1"
ExecStart=$(pwd)/venv/bin/python $(pwd)/bot.py
Restart=always
RestartSec=10
StandardOutput=journal
StandardError=journal

[Install]
WantedBy=multi-user.target
EOF

systemctl daemon-reload
systemctl enable skrepnet-bot
systemctl restart skrepnet-bot
echo "✅ Сервис настроен и запущен"

echo ""
echo "============================================"
echo "  ✅ Установка завершена!"
echo "============================================"
echo ""
echo "Проверить статус:"
echo "  systemctl status skrepnet-bot"
echo ""
echo "Логи:"
echo "  journalctl -u skrepnet-bot -f"
echo ""

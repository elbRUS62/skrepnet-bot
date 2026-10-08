#!/bin/bash
set -e

# ============================================================
#  SkrepNet Bot — Installer
#  Author: @elbRUS62
#  Repo:   https://github.com/elbRUS62/skrepnet-bot
# ============================================================

# Цвета
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
CYAN='\033[0;36m'
BOLD='\033[1m'
NC='\033[0m' # No Color

# Функция для рисования рамки
line() {
    echo -e "${CYAN}════════════════════════════════════════════════════════${NC}"
}

header() {
    echo ""
    line
    echo -e "${BOLD}${BLUE}  $1${NC}"
    line
}

success() {
    echo -e "${GREEN}  ✅ $1${NC}"
}

error() {
    echo -e "${RED}  ❌ $1${NC}"
}

warning() {
    echo -e "${YELLOW}  ⚠️  $1${NC}"
}

info() {
    echo -e "${CYAN}  ➜  $1${NC}"
}

# Приветствие
clear
echo ""
line
echo -e "${BOLD}${BLUE}"
echo "        🛡️  SkrepNet Bot — Installer"
echo "        Автор: @elbRUS62"
echo "        GitHub: github.com/elbRUS62/skrepnet-bot"
echo -e "${NC}"
line
echo ""

# Проверка на root
if [ "$EUID" -ne 0 ]; then
    error "Запусти скрипт от root (sudo su)"
    exit 1
fi

# Проверка, что мы в правильной папке
if [ ! -f "bot.py" ]; then
    error "Файл bot.py не найден. Запусти скрипт из папки бота."
    exit 1
fi

# Проверка Python
header "Проверка Python"
if ! command -v python3 &> /dev/null; then
    error "Python 3 не найден. Установи: apt install python3"
    exit 1
fi

# Установка системных зависимостей
if ! python3 -m venv --help &> /dev/null; then
    warning "Устанавливаю python3-venv..."
    apt update -qq
    apt install -y python3-venv python3-pip
fi

PYTHON_VERSION=$(python3 --version | awk '{print $2}')
success "Python $PYTHON_VERSION"

# Проверка .env
if [ -f ".env" ]; then
    warning "Файл .env уже существует."
    read -p "  Перезаписать? (y/N): " overwrite
    if [ "$overwrite" != "y" ] && [ "$overwrite" != "Y" ]; then
        info "Отменено."
        exit 0
    fi
fi

# ============================================================
#  Telegram
# ============================================================
header "Telegram"
read -p "  BOT_TOKEN (от @BotFather): " BOT_TOKEN
read -p "  ADMIN_ID (твой Telegram ID, можно несколько через запятую): " ADMIN_ID
read -p "  BOT_USERNAME (без @, например skrepnet_bot): " BOT_USERNAME

# ============================================================
#  3x-ui Панель
# ============================================================
header "3x-ui Панель"
read -p "  XUI_HOST (например https://ru-skrepnet.duckdns.org:3775): " XUI_HOST
read -p "  XUI_BASE_PATH (например /MASbquuCRx18QVK8l6): " XUI_BASE_PATH
read -p "  XUI_API_TOKEN (из Settings → Security): " XUI_API_TOKEN

# ============================================================
#  Инбаунды
# ============================================================
header "Инбаунды 3x-ui"
read -p "  XUI_INBOUND_GB (ID основного Hysteria2, например 5): " XUI_INBOUND_GB
read -p "  XUI_INBOUND_LV (ID резервного, например 6): " XUI_INBOUND_LV

# ============================================================
#  Подписка
# ============================================================
header "Подписка"
read -p "  SUB_BASE_URL (например https://ru-skrepnet.duckdns.org:9913): " SUB_BASE_URL
read -p "  SUB_PATH (например /subs_77dfgjn5jk78mkldxp77/): " SUB_PATH

# ============================================================
#  Лимиты
# ============================================================
header "Лимиты"
read -p "  LIMIT_IP (по умолчанию 3): " LIMIT_IP_INPUT
LIMIT_IP=${LIMIT_IP_INPUT:-3}
read -p "  SUBSCRIPTION_DAYS (по умолчанию 30): " SUBSCRIPTION_DAYS_INPUT
SUBSCRIPTION_DAYS=${SUBSCRIPTION_DAYS_INPUT:-30}

# ============================================================
#  Донат
# ============================================================
header "Донат"
read -p "  DONATE_URL (ссылка на DonationAlerts): " DONATE_URL
read -p "  DONATE_TEXT (текст плашки): " DONATE_TEXT

# ============================================================
#  Создание .env
# ============================================================
header "Создаю .env"

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
success ".env создан (права 600)"

# ============================================================
#  Зависимости
# ============================================================
header "Устанавливаю зависимости"
if [ ! -d "venv" ]; then
    python3 -m venv venv
fi
source venv/bin/activate
pip install --upgrade pip -q
pip install -r requirements.txt -q

if ! pip show qrcode &> /dev/null; then
    pip install "qrcode[pil]" -q
fi

success "Зависимости установлены"

# ============================================================
#  Бэкапы
# ============================================================
header "Настраиваю бэкапы"
mkdir -p backups
success "Папка backups создана"

BACKUP_CRON="0 3 * * * $(pwd)/backup.sh >> $(pwd)/backups/backup.log 2>&1"

if crontab -l 2>/dev/null | grep -q "backup.sh"; then
    warning "Задача бэкапа уже в cron"
else
    (crontab -l 2>/dev/null; echo "$BACKUP_CRON") | crontab -
    success "Бэкапы настроены (ежедневно в 3:00)"
fi

# ============================================================
#  Systemd
# ============================================================
header "Настраиваю systemd"
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
success "Сервис настроен и запущен"

# ============================================================
#  Финал
# ============================================================
echo ""
line
echo -e "${BOLD}${GREEN}"
echo "        ✅ Установка завершена!"
echo -e "${NC}"
line
echo ""
echo -e "${BOLD}  📋 Полезные команды:${NC}"
echo ""
echo -e "  ${CYAN}Статус бота:${NC}"
echo "    systemctl status skrepnet-bot"
echo ""
echo -e "  ${CYAN}Логи в реальном времени:${NC}"
echo "    journalctl -u skrepnet-bot -f"
echo ""
echo -e "  ${CYAN}Перезапуск:${NC}"
echo "    systemctl restart skrepnet-bot"
echo ""
echo -e "  ${CYAN}Бэкапы:${NC}"
echo "    ls -la $(pwd)/backups/"
echo ""
echo -e "  ${CYAN}Папка бота:${NC}"
echo "    cd $(pwd)"
echo ""
line
echo -e "${BOLD}  🛡️  SkrepNet Bot · @elbRUS62${NC}"
line
echo ""

#!/bin/bash
set -e

# ============================================================
#  SkrepNet Bot — Web Installer
#  Author: @elbRUS62
#  Repo:   https://github.com/elbRUS62/skrepnet-bot
# ============================================================

RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
CYAN='\033[0;36m'
BOLD='\033[1m'
NC='\033[0m'

line()    { echo -e "${CYAN}════════════════════════════════════════════════════════${NC}"; }
header()  { echo ""; line; echo -e "${BOLD}${BLUE}  $1${NC}"; line; }
success() { echo -e "${GREEN}  ✅ $1${NC}"; }
error()   { echo -e "${RED}  ❌ $1${NC}"; }
warning() { echo -e "${YELLOW}  ⚠️  $1${NC}"; }
info()    { echo -e "${CYAN}  ➜  $1${NC}"; }

clear
echo ""
line
echo -e "${BOLD}${BLUE}"
echo "        🛡️  SkrepNet Bot — Web Installer"
echo "        Автор: @elbRUS62"
echo "        GitHub: github.com/elbRUS62/skrepnet-bot"
echo -e "${NC}"
line
echo ""

if [ "$EUID" -ne 0 ]; then
    error "Запусти скрипт от root (sudo su)"
    exit 1
fi

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
cd "$SCRIPT_DIR/.."

if [ ! -f "web_app.py" ]; then
    error "Файл web_app.py не найден. Запусти скрипт из папки проекта."
    exit 1
fi

if [ ! -f ".env" ]; then
    error "Файл .env не найден. Сначала запусти scripts/install-bot.sh"
    exit 1
fi

header "Проверка Python и venv"
if [ ! -d "venv" ]; then
    warning "venv не найден — создаю"
    python3 -m venv venv
fi
source venv/bin/activate
success "venv активирован"

header "Параметры веб-сайта"
read -p "  Домен (например gb-skrepnet.duckdns.org): " WEB_DOMAIN
read -p "  Порт (по умолчанию 8443): " WEB_PORT_INPUT
WEB_PORT=${WEB_PORT_INPUT:-8443}

SSL_CERT_DIR="/root/cert/${WEB_DOMAIN}"
SSL_CERT="${SSL_CERT_DIR}/fullchain.pem"
SSL_KEY="${SSL_CERT_DIR}/privkey.pem"

header "Проверка SSL-сертификатов"
if [ -f "$SSL_CERT" ] && [ -f "$SSL_KEY" ]; then
    success "Сертификаты найдены: $SSL_CERT_DIR"
else
    warning "Сертификаты не найдены в $SSL_CERT_DIR"
    read -p "  Получить через certbot? (y/N): " use_certbot
    if [ "$use_certbot" = "y" ] || [ "$use_certbot" = "Y" ]; then
        read -p "  Email для Let's Encrypt: " LE_EMAIL

        if ! command -v certbot &> /dev/null; then
            info "Устанавливаю certbot..."
            apt update -qq
            apt install -y certbot
        fi

        info "Получаю сертификат для $WEB_DOMAIN (standalone, порт 80)..."
        systemctl stop nginx 2>/dev/null || true

        certbot certonly --standalone \
            -d "$WEB_DOMAIN" \
            --email "$LE_EMAIL" \
            --agree-tos --non-interactive

        mkdir -p "$SSL_CERT_DIR"
        cp "/etc/letsencrypt/live/${WEB_DOMAIN}/fullchain.pem" "$SSL_CERT"
        cp "/etc/letsencrypt/live/${WEB_DOMAIN}/privkey.pem" "$SSL_KEY"
        chmod 600 "$SSL_KEY"

        success "Сертификаты получены и скопированы в $SSL_CERT_DIR"
    else
        warning "Сайт будет запущен БЕЗ HTTPS (порт ${WEB_PORT} без TLS)"
    fi
fi

header "Обновляю web_app.py (пути к сертификатам)"
# Меняем пути SSL в web_app.py под текущий домен
sed -i "s|SSL_CERT = '.*'|SSL_CERT = '${SSL_CERT}'|" web_app.py
sed -i "s|SSL_KEY = '.*'|SSL_KEY = '${SSL_KEY}'|" web_app.py
sed -i "s|app.run(host='0.0.0.0', port=[0-9]*|app.run(host='0.0.0.0', port=${WEB_PORT}|" web_app.py
success "web_app.py обновлён под $WEB_DOMAIN:$WEB_PORT"

header "Устанавливаю зависимости (если нужно)"
pip install flask qrcode[pil] aiosqlite aiohttp python-dotenv -q
success "Зависимости на месте"

header "Настраиваю systemd (сайт)"
cat > /etc/systemd/system/skrepnet-web.service <<EOF
[Unit]
Description=SkrepNet Web (Flask)
After=network.target

[Service]
Type=simple
User=root
WorkingDirectory=$(pwd)
Environment="PYTHONUNBUFFERED=1"
ExecStart=$(pwd)/venv/bin/python $(pwd)/web_app.py
Restart=always
RestartSec=10
StandardOutput=journal
StandardError=journal

[Install]
WantedBy=multi-user.target
EOF

systemctl daemon-reload
systemctl enable skrepnet-web
systemctl restart skrepnet-web
success "Сервис skrepnet-web настроен и запущен"

echo ""
line
echo -e "${BOLD}${GREEN}"
echo "        ✅ Установка веб-сайта завершена!"
echo -e "${NC}"
line
echo ""
echo -e "${BOLD}  🌐 Адрес сайта:${NC}"
if [ -f "$SSL_CERT" ]; then
    echo "    https://${WEB_DOMAIN}:${WEB_PORT}/invite/<token>"
else
    echo "    http://${WEB_DOMAIN}:${WEB_PORT}/invite/<token>"
fi
echo ""
echo -e "${BOLD}  📋 Полезные команды:${NC}"
echo ""
echo -e "  ${CYAN}Статус сайта:${NC}"
echo "    systemctl status skrepnet-web"
echo ""
echo -e "  ${CYAN}Логи:${NC}"
echo "    journalctl -u skrepnet-web -f"
echo ""
echo -e "  ${CYAN}Перезапуск:${NC}"
echo "    systemctl restart skrepnet-web"
echo ""
line
echo -e "${BOLD}  🛡️  SkrepNet Bot · @elbRUS62${NC}"
line
echo ""
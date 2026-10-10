<div align="center">

# 🛡️ SkrepNet Bot

**Telegram-бот для выдачи бесплатных подписок Hysteria2 через панель 3x-ui, с реферальной системой, донатами и веб-выдачей без Telegram.**

[![Python](https://img.shields.io/badge/Python-3.10%2B-blue?logo=python&logoColor=white)](https://www.python.org/)
[![aiogram](https://img.shields.io/badge/aiogram-3.31-2CA5E0?logo=telegram&logoColor=white)](https://aiogram.dev/)
[![3x-ui](https://img.shields.io/badge/3x--ui-API-green)](https://github.com/MHSanaei/3x-ui)
[![Stars](https://img.shields.io/badge/⭐_Telegram_Stars-поддержка-yellow)]()

- 🤖 **Бот в Telegram:** [@skrepnet_bot](https://t.me/skrepnet_bot)
- 🆘 **Поддержка:** [@SkrepNet_support](https://t.me/SkrepNet_support)


<img width="400" alt="SkrepNet banner" src="https://github.com/user-attachments/assets/27dd6763-7b5e-4222-aa1f-d22a91094bee" />

</div>

## ✨ Возможности

### Для пользователей
- 📦 Получение подписки Hysteria2
- 📜 Согласие с правилами, политикой и пользовательским соглашением
- 📱 Лимит 3 IP одновременно, срок подписки 30 дней
- 🔄 Ручное продление подписки по кнопке, в боте
- 📷 QR-код для быстрого подключения
- 🔔 Напоминания о продлении подписки (за 3 дня и в день окончания, без звука)
- 👥 Реферальная система: рефералы одобряются **автоматически**
- ➕ Приглашение пользователя если у него нет доступа к **Telegram** — одноразовая ссылка на веб-сайт (действуют 7 дней, срабатывают 1 раз)
- 💰 Донат: Telegram Stars + DonationAlerts
- 📖 Инструкции по подключению для 6 платформ (Android, iOS, Windows, macOS, Android TV, Linux)
- 🍎 Happ — рекомендуемое приложение

### Для админов
- 🛠 Меню «Управление»
- 👤 Добавление/удаление админов по username (с защитой .env-админов)
- 📋 Список админов (основные + добавленные)
- 🔄 Обновление подписки по username
- 🗑 Удаление пользователей (из БД и 3x-ui одновременно)
- ♻️ Сброс заявки
- 📢 Рассылка всем активным
- 📊 Статистика + топ-5 приглашающих
- 🔐 Кнопка входа в панель 3x-ui
- 📋 История обновлений 

### Веб-сайт (для выдачи подписки пользователю без Telegram)
- 🌐 Flask-приложение на HTTPS (порт 8443)
- 🔗 Одноразовые ссылки-приглашения (действуют 7 дней, срабатывают 1 раз)
- ✅ Согласие с правилами, политикой и пользовательским соглашением → мгновенная выдача подписки
- 📷 QR-код прямо на странице
- ➡️ Кнопка перехода в Telegram-бот

### Автоматика
- ⏰ Проверка окончания подписок — ежедневно в 10:00 (без звука)
- 🗑 Автоудаление неактивных пользователей (30+ дней) из БД и 3x-ui одновременно — ежедневно в 4:00
- 💾 Бэкапы базы данных — ежедневно в 3:00, хранение 30 дней
- 🔧 Systemd-автозапуск (Restart=always)
- 🔌 DonationAlerts WebSocket через Centrifugo (автопереподключение)

---

## 🏗️ Архитектура

- **Бот** работает на зарубежном VPS (прямой доступ к Telegram API)
- **Панель 3x-ui** — на российском VPS
- Связь между ними — через **API-токен (Bearer)** по HTTPS
- **Веб-сайт** (`web_app.py`) — Flask на HTTPS, отдельный порт
- **Донаты** — Telegram Stars (инвойсы) + DonationAlerts через Centrifugo WebSocket

## 📋 Требования

- VPS за рубежом (для бота)
- VPS с 3x-ui + Hysteria2 (для панели)
- Python 3.10+
- API-токен 3x-ui (Settings → Security → API Tokens)
- Бот в Telegram (создаётся через @BotFather)
- Токен DonationAlerts (для приёма донатов)
- SSL-сертификат для веб-сайта (например, Let's Encrypt)

## 🚀 Быстрая установка

    git clone https://github.com/elbRUS62/skrepnet-bot.git
    cd skrepnet-bot

    # Установка бота
    bash scripts/install-bot.sh

    # Установка веб-сайта (опционально)
    bash scripts/install-web.sh

Скрипт задаст все вопросы (BOT_TOKEN, ADMIN_ID, XUI_HOST, XUI_API_TOKEN, инбаунд, SUB_BASE_URL, лимиты, донат) и настроит бота автоматически: создаст `.env` с правами 600, поставит зависимости в venv, настроит cron для бэкапов и systemd-сервис.

Для веб-сайта: `scripts/install-web.sh` настроит Flask-сервис, проверит SSL, при необходимости получит сертификат через certbot и создаст отдельный `skrepnet-web.service`.

### Полезные команды

    systemctl status skrepnet-bot      # статус
    journalctl -u skrepnet-bot -f      # логи в реальном времени
    systemctl restart skrepnet-bot     # перезапуск
    ls -la backups/                    # бэкапы


---

## 📁 Структура проекта

    bot.py                  # точка входа
    config.py               # чтение .env, валидация
    database.py             # SQLite (users, admins, invite_links, invites)
    xui_client.py           # API 3x-ui (add/get/update/delete client)
    keyboards.py            # кнопки и меню
    scheduler.py            # напоминания + автоочистка
    docs_config.py          # ссылки на документы в telegra.ph
    donation_socket.py      # DonationAlerts через Centrifugo WebSocket
    web_app.py              # Flask-сайт для выдачи без Telegram
    backup.sh               # бэкап базы
    handlers/               # обработчики по модулям
    scripts/                # install-bot.sh, install-web.sh
    web/                    # templates + static


---

## 🔄 Как работает выдача подписки

**Обычный пользователь:**
1. `/start` → «📦 Получить подписку»
2. Принятие правил, политики и соглашения перед получением подписки
3. Админ жмёт «✅ Одобрить» → клиент создаётся в 3x-ui, пользователь получает ссылку

**Реферал (по ссылке `?start=ref_<id>`):**
1. `/start` по deep-link → автоматически записывается `invited_by`
2. Принятие правил, политики и соглашения перед получением → **автоодобрение** (без одобрения админа)
3. Админ и пригласивший получают уведомление
   
**Друг без Telegram:**
1. Пользователь → «➕ Добавить без Telegram»
2. Выбирает контакт или вводит @username/ID вручную
3. Получает одноразовую ссылку `https://<host>:8443/invite/<token>` (действуют 7 дней, срабатывают 1 раз)
4. Новый пользователь открывает ссылку в браузере → принимает условия → получает подписку + QR + кнопки на телеграмм бота
5. Ручное продление подписки по кнопке, в боте

## 🔒 Безопасность

- `.env` в `.gitignore`, права 600
- API-токен 3x-ui вместо логина/пароля
- Systemd с `Restart=always`
- Валидация обязательных переменных при старте (`config.py`)

---

@elbRUS62

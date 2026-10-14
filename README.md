<div align="center">

# 🛡️ SkrepNet Bot

**Telegram-бот для выдачи бесплатных подписок Hysteria2 через панель 3x-ui, с реферальной системой, донатами, листом ожидания и веб-выдачей без Telegram.**

[![Python](https://img.shields.io/badge/Python-3.10%2B-blue?logo=python&logoColor=white)](https://www.python.org/)
[![aiogram](https://img.shields.io/badge/aiogram-3.31-2CA5E0?logo=telegram&logoColor=white)](https://aiogram.dev/)
[![3x-ui](https://img.shields.io/badge/3x--ui-API-green)](https://github.com/MHSanaei/3x-ui)
[![Stars](https://img.shields.io/badge/⭐_Telegram_Stars-поддержка-yellow)]()

- 🤖 **Бот в Telegram:** [@skrepnet_bot](https://t.me/skrepnet_bot)
- 🆘 **Поддержка:** [@SkrepNet_support](https://t.me/SkrepNet_support)

<img width="400" alt="SkrepNet banner" src="https://github.com/user-attachments/assets/27dd6763-7b5e-4222-aa1f-d22a91094bee" />

</div>

---

## ✨ Возможности

### Для пользователей
- 📦 Получение подписки Hysteria2
- 📜 Согласие с правилами, политикой и пользовательским соглашением
- 📱 Лимит 3 IP одновременно, срок подписки 30 дней
- 🔄 Ручное продление подписки по кнопке
- 📷 QR-код для быстрого подключения
- 🔔 Напоминания о продлении (за 3 дня и в день окончания, без звука)
- 📊 Прогресс сбора донатов (полоска в `/start` и напоминаниях)
- 👥 Реферальная система: рефералы одобряются **автоматически**
- ➕ Приглашение друзей **без Telegram** — одноразовая ссылка на веб-сайт (7 дней, срабатывает 1 раз)
- 📋 Лист ожидания, если достигнут лимит пользователей
- 💰 Донат: Telegram Stars + DonationAlerts
- 📖 Инструкции для 6 платформ (Android, iOS, Windows, macOS, Android TV, Linux)
- 🍎 Happ — рекомендуемое приложение

### Для админов
- 🛠 Меню «Управление» — всё на кнопках
- 📋 Список заявок с карточкой пользователя (одобрение, отклонение, удаление)
- 👥 Список пользователей с пагинацией и сортировкой (кириллица → латиница)
- 🔄 Обновление подписки (выбор из списка, ввод дней)
- 🗑 Удаление пользователей (из БД и 3x-ui одновременно)
- ♻️ Сброс заявки
- 📢 Рассылка всем активным
- 📊 Расширенная статистика: пользователи, лист ожидания, свободные места, топ-5 приглашающих
- 🔐 Кнопка входа в панель 3x-ui
- 📝 Комментарии к клиентам в 3x-ui (TG ID, username, источник, счётчик продлений)
- 💬 Лист ожидания с автоуведомлением при освобождении места

### Веб-сайт (для выдачи подписки без Telegram)
- 🌐 Flask-приложение на HTTPS (порт 8443)
- 🔗 Одноразовые ссылки-приглашения (7 дней, срабатывают 1 раз)
- ✅ Согласие с документами → мгновенная выдача подписки
- 📷 QR-код прямо на странице
- ➡️ Кнопка перехода в Telegram-бот

### Автоматика
- ⏰ Напоминания о продлении — ежедневно в 10:00 (без звука)
- 🗑 Автоудаление неактивных (30+ дней) — ежедневно в 4:00
- 📋 Автоочистка листа ожидания (30+ дней) — 1-го числа каждого месяца
- 💾 Бэкапы базы данных — ежедневно в 3:00, хранение 30 дней
- 🔧 Systemd-автозапуск (Restart=always)
- 🔌 DonationAlerts WebSocket через Centrifugo (автопереподключение)

---

## 🏗️ Архитектура

- **Бот** работает на зарубежном VPS (прямой доступ к Telegram API)
- **Панель 3x-ui** — на российском VPS
- Связь между ними — через **API-токен (Bearer)** по HTTPS
- **Веб-сайт** (`web_app.py`) — Flask на HTTPS, отдельный порт
- **Донаты** — Telegram Stars + DonationAlerts через Centrifugo WebSocket

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

Скрипт задаст все вопросы (BOT_TOKEN, ADMIN_ID, BOT_USERNAME, BOT_NAME, SUPPORT_USERNAME, XUI_HOST, XUI_API_TOKEN, инбаунд, SUB_BASE_URL, лимиты, донат) и настроит бота автоматически: создаст `.env` с правами 600, поставит зависимости в venv, настроит cron для бэкапов и systemd-сервис.

Для веб-сайта: `scripts/install-web.sh` настроит Flask-сервис, проверит SSL, при необходимости получит сертификат через certbot и создаст отдельный `skrepnet-web.service`.

### Полезные команды

    systemctl status skrepnet-bot      # статус
    journalctl -u skrepnet-bot -f      # логи в реальном времени
    systemctl restart skrepnet-bot     # перезапуск
    ls -la backups/                    # бэкапы

---

## 🔧 Переменные `.env`

### Telegram
- `BOT_TOKEN` — токен бота от @BotFather
- `ADMIN_ID` — Telegram ID админов (через запятую)
- `BOT_USERNAME` — username бота (без @)
- `BOT_NAME` — отображаемое имя бота (по умолчанию `SkrepNet`)
- `SUPPORT_USERNAME` — username поддержки (без @, по умолчанию `SkrepNet_support`)

### 3x-ui
- `XUI_HOST` — адрес панели 3x-ui
- `XUI_BASE_PATH` — путь панели
- `XUI_API_TOKEN` — API-токен
- `XUI_INBOUND_GB` — ID инбаунда Hysteria2

### Подписка
- `SUB_BASE_URL` — базовый URL подписок
- `SUB_PATH` — путь подписок
- `LIMIT_IP` — лимит IP (по умолчанию 3)
- `SUBSCRIPTION_DAYS` — срок подписки в днях (по умолчанию 30)
- `MAX_USERS` — максимум активных пользователей (по умолчанию 100)

### Донаты
- `DONATE_URL` — ссылка на DonationAlerts
- `DONATE_TEXT` — текст плашки
- `SERVER_COST` — стоимость сервера в ₽/мес (для прогресса сбора)
- `DONATION_ALERTS_TOKEN` — токен DonationAlerts (для WebSocket)

### Прочее
- `DB_PATH` — путь к базе данных (по умолчанию `skrepnet.db`)

---

## 📁 Структура проекта

    bot.py                  # точка входа
    config.py               # чтение .env, валидация
    database.py             # SQLite (users, admins, invite_links, invites, donations, waitlist)
    xui_client.py           # API 3x-ui (add/get/update/delete client, comment)
    keyboards.py            # кнопки и меню
    scheduler.py            # напоминания + автоочистка + лист ожидания
    docs_config.py          # ссылки на документы в telegra.ph
    donation_socket.py      # DonationAlerts через Centrifugo WebSocket
    web_app.py              # Flask-сайт для выдачи без Telegram
    backup.sh               # бэкап базы
    handlers/               # обработчики по модулям
    ├── start.py            # /start, реферальные deep-link
    ├── subscription.py     # заявка, одобрение, продление, QR, лист ожидания
    ├── donate.py           # Stars + DonationAlerts + приглашения
    ├── connect.py          # инструкции для 6 платформ
    ├── admin.py            # меню «Управление», статистика
    ├── invite.py           # приглашения без Telegram
    ├── progress.py         # прогресс сбора донатов
    ├── waitlist.py         # уведомление следующего из очереди
    ├── states.py           # FSM-состояния
    └── utils.py            # sanitize_email, QR-генератор
    scripts/                # install-bot.sh, install-web.sh
    web/                    # templates + static

---

## 🔄 Как работает выдача подписки

**Обычный пользователь:**
1. `/start` → «📦 Получить подписку»
2. Принятие правил, политики и соглашения
3. Админ жмёт «✅ Одобрить» → клиент создаётся в 3x-ui, пользователь получает ссылку

**Реферал (по ссылке `?start=ref_<id>`):**
1. `/start` по deep-link → автоматически записывается `invited_by`
2. Принятие правил, политики и соглашения → **автоодобрение**
3. Админ и пригласивший получают уведомление

**Друг без Telegram:**
1. Пользователь → «➕ Добавить без Telegram»
2. Выбирает контакт или вводит @username/ID вручную
3. Получает одноразовую ссылку `https://<host>:8443/invite/<token>` (7 дней, 1 раз)
4. Новый пользователь открывает ссылку в браузере → принимает условия → получает подписку + QR

**Если достигнут лимит пользователей:**
1. Новый пользователь видит «⚠️ Свободных мест нет»
2. Может встать в **лист ожидания** (кнопка «📝 Встать в лист ожидания»)
3. Когда место освобождается (админ удаляет юзера или автоочистка) → бот уведомляет первого из очереди

## 🔒 Безопасность

- `.env` в `.gitignore`, права 600
- API-токен 3x-ui вместо логина/пароля
- Systemd с `Restart=always`
- Валидация обязательных переменных при старте (`config.py`)
- Dependabot, CodeQL, Secret scanning — включены

---

## 🗺️ Roadmap

- [x] Выдача подписок Hysteria2
- [x] Одобрение админом
- [x] Автоодобрение рефералов
- [x] Ручное продление
- [x] Напоминания
- [x] Реферальная система + топ-5
- [x] Приглашения без Telegram (веб-выдача)
- [x] Донат: Stars + DonationAlerts
- [x] Прогресс сбора донатов
- [x] Инструкции для 6 платформ
- [x] Меню «Управление»
- [x] Соглашение с пользователем
- [x] Автоудаление неактивных
- [x] Лимит пользователей + лист ожидания
- [x] Счётчик продлений в comment 3x-ui
- [x] Настраиваемое имя бота (`BOT_NAME`)
- [ ] Второй сервер (🇱🇻) в подписке
- [ ] Онлайн-клиенты
- [ ] Мониторинг панели 3x-ui
- [ ] Статистика донатов через API
- [ ] Инструкции для Apple TV, Samsung TV, LG TV

---

@elbRUS62
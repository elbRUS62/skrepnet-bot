<div align="center">

# 🛡️ SkrepNet Bot

**Telegram-бот для выдачи бесплатных VPN-подписок на базе 3x-ui (Hysteria2)**

[![Python](https://img.shields.io/badge/Python-3.10%2B-blue?logo=python&logoColor=white)](https://www.python.org/)
[![aiogram](https://img.shields.io/badge/aiogram-3.13-2CA5E0?logo=telegram&logoColor=white)](https://aiogram.dev/)
[![3x-ui](https://img.shields.io/badge/3x--ui-3.9.0-green)](https://github.com/MHSanaei/3x-ui)
[![License](https://img.shields.io/badge/License-Private-red)]()

</div>

---

## 📖 О проекте

**SkrepNet Bot** — это полностью автоматизированный Telegram-бот для выдачи бесплатных VPN-подписок через панель **3x-ui**. Бот работает с протоколом **Hysteria2**, поддерживает несколько серверов в одной подписке, лимитирует количество устройств и напоминает пользователям о продлении.

Проект создан для дружеского круга: **VPN бесплатный**, но пользователи могут поддержать сервер донатами.

---

## ⚡ Быстрая установка (2 минуты)

```bash
git clone https://github.com/elbRUS62/skrepnet-bot.git
cd skrepnet-bot
./install.sh
```
Скрипт задаст все вопросы и настроит бота автоматически.

✨ Возможности
👤 Для пользователей
Функция	Описание
📦 Получение подписки	Hysteria2, 2 сервера (🇬🇧 основной + 🇱🇻 резервный) в одной ссылке
📜 Соглашение	Ознакомление с правилами перед первой заявкой
📱 Лимит 3 IP	Одновременно с 3 устройств
⏳ Срок 30 дней	Продление вручную по кнопке
🔔 Напоминания	За 3 дня и в день окончания (тихие уведомления)
👥 Реферальная система	Приглашай друзей, следи за статистикой
💰 Донат	Telegram Stars (10–100 ⭐) + DonationAlerts
📖 Инструкции	Для 6 платформ: Android, iOS, Windows, macOS, Android TV, Linux
🍎 Happ в приоритете	Рекомендуемое приложение для всех платформ
🛠️ Для админов
Функция	Описание
🛠 Меню «Управление»	Всё на кнопках — без команд
👤 Добавить админа	По username
🗑 Удалить админа	С защитой .env-админов
📋 Список админов	С разделением на основные и добавленные
🔄 Обновить подписку	По username, любое количество дней
🗑 Удалить пользователя	Сразу из БД и 3x-ui
♻️ Сбросить заявку	По username
📢 Рассылка	Всем активным пользователям
📊 Статистика	Всего, активных, ожидающих, истекающих
🔐 Панель 3x-ui	Кнопка входа из бота
📋 История обновлений	Все версии и изменения
🤖 Автоматика
Задача	Время	Что делает
⏰ Напоминания	10:00	За 3 дня и в день окончания
🗑 Автоочистка	04:00	Удаляет неактивных 30+ дней
💾 Бэкапы	03:00	Копия БД, хранение 30 дней
🔧 Systemd	—	Автозапуск при перезагрузке
🏗️ Архитектура
text
┌─────────────────────┐         ┌──────────────────────┐
│  Зарубежный сервер  │         │  Российский сервер   │
│  (Бот)              │◄───────►│  (3x-ui + Hysteria2) │
│                     │  HTTPS  │                      │
│  • Telegram Bot     │         │  • Панель 3x-ui      │
│  • SQLite           │         │  • 🇬🇧 + 🇱🇻 серверы  │
│  • Бэкапы           │         │  • Subscription page │
└─────────────────────┘         └──────────────────────┘
Бот — на зарубежном VPS (прямой доступ к Telegram API)

3x-ui — на российском VPS (там, где VPN)

Связь — через API-токен 3x-ui по HTTPS

📋 Требования
VPS за рубежом (для доступа к Telegram API без блокировок) — ~200–500 ₽/мес

VPS с 3x-ui (Hysteria2) — ~3000 ₽/мес

Python 3.10+

API-токен 3x-ui (Settings → Security → API Tokens)

Бот в Telegram (создаётся через @BotFather)

🔧 Ручная настройка
1. Виртуальное окружение
bash
python3 -m venv venv
source venv/bin/activate
pip install -r requirements.txt
2. Файл .env
bash
cp .env.example .env
nano .env
Заполни переменные:

env
# Telegram
BOT_TOKEN=токен_от_BotFather
ADMIN_ID=твой_telegram_id
BOT_USERNAME=skrepnet_bot

# 3x-ui Panel
XUI_HOST=https://твой-сервер:3775
XUI_BASE_PATH=/твой_секретный_путь
XUI_API_TOKEN=токен_из_панели

# Inbounds
XUI_INBOUND_GB=5
XUI_INBOUND_LV=6

# Subscription
SUB_BASE_URL=https://твой-сервер:9913
SUB_PATH=/subs_твой_путь/

# Limits
LIMIT_IP=3
SUBSCRIPTION_DAYS=30

# Donate
DONATE_URL=https://www.donationalerts.com/r/твой_ник
DONATE_TEXT=Текст плашки доната

# Database
DB_PATH=skrepnet.db
3. Systemd
bash
sudo nano /etc/systemd/system/skrepnet-bot.service
ini
[Unit]
Description=SkrepNet Telegram Bot
After=network.target

[Service]
Type=simple
User=root
WorkingDirectory=/root/skrepnet-bot
Environment="PYTHONUNBUFFERED=1"
ExecStart=/root/skrepnet-bot/venv/bin/python /root/skrepnet-bot/bot.py
Restart=always
RestartSec=10
StandardOutput=journal
StandardError=journal

[Install]
WantedBy=multi-user.target
bash
sudo systemctl daemon-reload
sudo systemctl enable skrepnet-bot
sudo systemctl start skrepnet-bot
4. Бэкапы
bash
crontab -e
Добавь:

text
0 3 * * * /root/skrepnet-bot/backup.sh >> /root/skrepnet-bot/backups/backup.log 2>&1
📁 Структура проекта
text
skrepnet-bot/
├── bot.py                      # Точка входа
├── config.py                   # Чтение .env
├── database.py                 # SQLite: пользователи, админы
├── xui_client.py               # API 3x-ui (Bearer-токен)
├── keyboards.py                # Все кнопки и меню
├── scheduler.py                # Напоминания + автоочистка
├── install.sh                  # Интерактивный установщик
├── backup.sh                   # Скрипт бэкапа
├── requirements.txt            # Зависимости Python
├── handlers/                   # Обработчики по модулям
│   ├── __init__.py             # Сборка роутеров
│   ├── utils.py                # sanitize_email + TERMS_TEXT
│   ├── states.py               # FSM-состояния
│   ├── start.py                # /start и рефералка
│   ├── subscription.py         # Заявки, соглашение, подписка
│   ├── donate.py               # Донат + приглашения
│   ├── connect.py              # 6 инструкций
│   ├── admin.py                # Меню «Управление»
│   └── changelog.py            # История обновлений
├── sub_templates/              # Кастомная страница подписки
│   └── skrepnet/
│       └── index.html
├── backups/                    # Бэкапы БД
└── .env                        # Секреты (в .gitignore)
🔒 Безопасность
✅ .env в .gitignore — секреты не попадают в Git

✅ Права 600 на .env — только владелец может читать

✅ API-токен 3x-ui вместо логина/пароля — обходит CSRF-защиту

✅ Systemd с Restart=always — бот сам поднимается при падении

⚠️ Смени токены после первой настройки:

@BotFather → /revoke

Панель 3x-ui → сменить пароль и URI Path

Security → новый API-токен

💰 Экономика
Для покрытия ~3000 ₽/мес (сервер) нужно:

Способ доната	Комиссия	Собрать
⭐ Telegram Stars	~30%	~4300 ₽
💸 DonationAlerts	~8,5%	~3300 ₽
🔀 Смешанно (50/50)	—	~3800 ₽
Итого: ~30 активных пользователей × 110–150 ₽/мес — и сервер покрыт.

🛠️ Технологии
Python 3.12 — язык разработки

aiogram 3.13 — Telegram Bot API

SQLite (aiosqlite) — база данных

APScheduler — планировщик задач

aiohttp — HTTP-запросы к 3x-ui API

Hysteria2 — протокол VPN

3x-ui — панель управления VPN

🗺️ Roadmap
☑ Выдача подписок Hysteria2
☑ Одобрение админом
☑ Ручное продление
☑ Напоминания
☑ Реферальная система
☑ Донат: Stars + DonationAlerts
☑ Инструкции для 6 платформ
☑ Меню «Управление» на кнопках
☑ Соглашение с пользователем
☑ Автоудаление неактивных
□ Статистика донатов через API
□ Онлайн-клиенты в статистике
□ Мониторинг панели 3x-ui
□ Инструкции для Apple TV / Samsung TV / LG TV
📄 Лицензия
Приватный проект. Все права защищены.

<div align="center">
Сделано с ❤️ для своих

@elbRUS62

</div> ```
💾 Загрузи в Git
bash
cd /root/skrepnet-bot
git add README.md
git commit -m "Обновлён README"
git push
Скинь результат — если всё прошло, README обновится на GitHub. 🚀

This response is AI-generated, for reference only.
вот здесь нет знаки разделения для форматирования, весь текст идет одним стилем
Вижу проблему — на скриншоте видно, что блок кода «съел» разметку, и текст идёт одним стилем. Скорее всего, при копировании в README сбилась разметка — либо блок кода не закрылся, либо съехали отступы.

🔍 Что проверить
Открой README на сервере:

bash
head -30 /root/skrepnet-bot/README.md
Что должно быть:

markdown
<div align="center">

# 🛡️ SkrepNet Bot

**Telegram-бот для выдачи бесплатных VPN-подписок на базе 3x-ui (Hysteria2)**

[![Python](...)](...)
...
🔧 Исправление — перезапиши README
Возможно, при копировании в nano слетели обратные кавычки (```). Проверим и перезапишем.

1. Открой README:

bash
nano /root/skrepnet-bot/README.md
2. Удали всё (Ctrl + K много раз, пока файл не станет пустым).

3. Вставь заново — скопируй весь блок из моего предыдущего сообщения (от <div align="center"> до последнего </div>).

4. Сохрани: Ctrl + O → Enter → Ctrl + X.

⚠️ Проверь, что блоки кода закрыты
Самая частая проблема — не закрыт блок кода (```). Открой README и проверь все блоки:

bash
grep -n '```' /root/skrepnet-bot/README.md
Что должно быть — каждая строка с ``` идёт парой (открывающая и закрывающая). Если где-то одна — текст «съедается» и идёт одним стилем.

Пример правильного чередования:

text
15:```bash
19:```
30:```bash
35:```
48:```env
70:```
Если видишь, что количество ``` нечётное — где-то пропущена закрывающая.

🚀 После исправления — загрузи в Git
bash
cd /root/skrepnet-bot
git add README.md
git commit -m "Исправлена разметка README"
git push
✅ Проверь на GitHub
Открой https://github.com/elbRUS62/skrepnet-bot — разметка должна отобразиться:

Заголовок 🛡️ SkrepNet Bot — крупным шрифтом

Бейджи (Python, aiogram, 3x-ui) — цветными плашками

Таблицы — с рамками

Блоки кода — серым фоном

Скинь результат — если разметка не отобразилась, покажи head -50 /root/skrepnet-bot/README.md, разберёмся.

This response is AI-generated, for reference only.
нет, вот здесь что то с форматом

```bash
git clone https://github.com/elbRUS62/skrepnet-bot.git
cd skrepnet-bot
./install.sh
```

Скрипт задаст все вопросы и настроит бота автоматически.

✨ Возможности
👤 Для пользователей
Функция	Описание
Понял! Вижу проблему: блок кода не закрылся, и весь последующий текст оказался «внутри» него.

🔍 Что случилось
В README после строки ./install.sh не стоит закрывающая ```. Из-за этого весь остальной текст воспринимается как часть кодового блока — а внутри кода Markdown-разметка (таблицы, заголовки, бейджи) не работает.

🔧 Как исправить
Открой README:

bash
nano /root/skrepnet-bot/README.md
Найди блок «Быстрая установка»:

markdown
## ⚡ Быстрая установка (2 минуты)

```bash
git clone https://github.com/elbRUS62/skrepnet-bot.git
cd skrepnet-bot
./install.sh
Скрипт задаст все вопросы и настроит бота автоматически.

text

**Ключевой момент:** после `./install.sh` **должна быть** строка с тремя обратными кавычками ```` ``` ```` (закрывающая). Без неё весь текст ниже «проваливается» в код.

### 🔍 Проверь все блоки кода

Выполни:

```bash
grep -c '```' /root/skrepnet-bot/README.md
Что должно быть: чётное число (2, 4, 6, 8...). Если нечётное — где-то пропущена закрывающая ```.

📄 Гарантированный способ — скачай готовый README
Чтобы не мучиться с ручной правкой, я могу прислать готовый файл одним куском, который ты просто вставишь. Но проблема в том, что в чате форматирование тоже может сбиться.

Лучший вариант: создай README прямо на сервере через cat, а не через nano — тогда копирование не собьёт разметку.

Выполни одну команду:

bash
cat > /root/skrepnet-bot/README.md << 'READMEEOF'
<div align="center">

# 🛡️ SkrepNet Bot

**Telegram-бот для выдачи бесплатных VPN-подписок на базе 3x-ui (Hysteria2)**

[![Python](https://img.shields.io/badge/Python-3.10%2B-blue?logo=python&logoColor=white)](https://www.python.org/)
[![aiogram](https://img.shields.io/badge/aiogram-3.13-2CA5E0?logo=telegram&logoColor=white)](https://aiogram.dev/)
[![3x-ui](https://img.shields.io/badge/3x--ui-3.9.0-green)](https://github.com/MHSanaei/3x-ui)
[![License](https://img.shields.io/badge/License-Private-red)]()

*Проект существует на донаты пользователей. Сервер стоит ~3000 ₽/мес.*

</div>

---

## 📖 О проекте

**SkrepNet Bot** — это полностью автоматизированный Telegram-бот для выдачи бесплатных VPN-подписок через панель **3x-ui**. Бот работает с протоколом **Hysteria2**, поддерживает несколько серверов в одной подписке, лимитирует количество устройств и напоминает пользователям о продлении.

Проект создан для дружеского круга: **VPN бесплатный**, но пользователи могут поддержать сервер донатами.

---

## ⚡ Быстрая установка (2 минуты)

```bash
git clone https://github.com/elbRUS62/skrepnet-bot.git
cd skrepnet-bot
./install.sh
Скрипт задаст все вопросы и настроит бота автоматически.

✨ Возможности
👤 Для пользователей
Функция	Описание
📦 Получение подписки	Hysteria2, 2 сервера (🇬🇧 основной + 🇱🇻 резервный) в одной ссылке
📜 Соглашение	Ознакомление с правилами перед первой заявкой
📱 Лимит 3 IP	Одновременно с 3 устройств
⏳ Срок 30 дней	Продление вручную по кнопке
🔔 Напоминания	За 3 дня и в день окончания (тихие уведомления)
👥 Реферальная система	Приглашай друзей, следи за статистикой
💰 Донат	Telegram Stars (10–100 ⭐) + DonationAlerts
📖 Инструкции	Для 6 платформ: Android, iOS, Windows, macOS, Android TV, Linux
🍎 Happ в приоритете	Рекомендуемое приложение для всех платформ
🛠️ Для админов
Функция	Описание
🛠 Меню «Управление»	Всё на кнопках — без команд
👤 Добавить админа	По username
🗑 Удалить админа	С защитой .env-админов
📋 Список админов	С разделением на основные и добавленные
🔄 Обновить подписку	По username, любое количество дней
🗑 Удалить пользователя	Сразу из БД и 3x-ui
♻️ Сбросить заявку	По username
📢 Рассылка	Всем активным пользователям
📊 Статистика	Всего, активных, ожидающих, истекающих
🔐 Панель 3x-ui	Кнопка входа из бота
📋 История обновлений	Все версии и изменения
🤖 Автоматика
Задача	Время	Что делает
⏰ Напоминания	10:00	За 3 дня и в день окончания
🗑 Автоочистка	04:00	Удаляет неактивных 30+ дней
💾 Бэкапы	03:00	Копия БД, хранение 30 дней
🔧 Systemd	—	Автозапуск при перезагрузке
🏗️ Архитектура
text
┌─────────────────────┐         ┌──────────────────────┐
│  Зарубежный сервер  │         │  Российский сервер   │
│  (Бот)              │◄───────►│  (3x-ui + Hysteria2) │
│                     │  HTTPS  │                      │
│  • Telegram Bot     │         │  • Панель 3x-ui      │
│  • SQLite           │         │  • 🇬🇧 + 🇱🇻 серверы  │
│  • Бэкапы           │         │  • Subscription page │
└─────────────────────┘         └──────────────────────┘
Бот — на зарубежном VPS (прямой доступ к Telegram API)

3x-ui — на российском VPS (там, где VPN)

Связь — через API-токен 3x-ui по HTTPS

📋 Требования
VPS за рубежом (для доступа к Telegram API без блокировок) — ~200–500 ₽/мес

VPS с 3x-ui (Hysteria2) — ~3000 ₽/мес

Python 3.10+

API-токен 3x-ui (Settings → Security → API Tokens)

Бот в Telegram (создаётся через @BotFather)

🔧 Ручная настройка
1. Виртуальное окружение
bash
python3 -m venv venv
source venv/bin/activate
pip install -r requirements.txt
2. Файл .env
bash
cp .env.example .env
nano .env
Заполни переменные:

env
# Telegram
BOT_TOKEN=токен_от_BotFather
ADMIN_ID=твой_telegram_id
BOT_USERNAME=skrepnet_bot

# 3x-ui Panel
XUI_HOST=https://твой-сервер:3775
XUI_BASE_PATH=/твой_секретный_путь
XUI_API_TOKEN=токен_из_панели

# Inbounds
XUI_INBOUND_GB=5
XUI_INBOUND_LV=6

# Subscription
SUB_BASE_URL=https://твой-сервер:9913
SUB_PATH=/subs_твой_путь/

# Limits
LIMIT_IP=3
SUBSCRIPTION_DAYS=30

# Donate
DONATE_URL=https://www.donationalerts.com/r/твой_ник
DONATE_TEXT=Текст плашки доната

# Database
DB_PATH=skrepnet.db
3. Systemd
bash
sudo nano /etc/systemd/system/skrepnet-bot.service
ini
[Unit]
Description=SkrepNet Telegram Bot
After=network.target

[Service]
Type=simple
User=root
WorkingDirectory=/root/skrepnet-bot
Environment="PYTHONUNBUFFERED=1"
ExecStart=/root/skrepnet-bot/venv/bin/python /root/skrepnet-bot/bot.py
Restart=always
RestartSec=10
StandardOutput=journal
StandardError=journal

[Install]
WantedBy=multi-user.target
bash
sudo systemctl daemon-reload
sudo systemctl enable skrepnet-bot
sudo systemctl start skrepnet-bot
4. Бэкапы
bash
crontab -e
Добавь:

text
0 3 * * * /root/skrepnet-bot/backup.sh >> /root/skrepnet-bot/backups/backup.log 2>&1
📁 Структура проекта
text
skrepnet-bot/
├── bot.py                      # Точка входа
├── config.py                   # Чтение .env
├── database.py                 # SQLite: пользователи, админы
├── xui_client.py               # API 3x-ui (Bearer-токен)
├── keyboards.py                # Все кнопки и меню
├── scheduler.py                # Напоминания + автоочистка
├── install.sh                  # Интерактивный установщик
├── backup.sh                   # Скрипт бэкапа
├── requirements.txt            # Зависимости Python
├── handlers/                   # Обработчики по модулям
│   ├── __init__.py             # Сборка роутеров
│   ├── utils.py                # sanitize_email + TERMS_TEXT
│   ├── states.py               # FSM-состояния
│   ├── start.py                # /start и рефералка
│   ├── subscription.py         # Заявки, соглашение, подписка
│   ├── donate.py               # Донат + приглашения
│   ├── connect.py              # 6 инструкций
│   ├── admin.py                # Меню «Управление»
│   └── changelog.py            # История обновлений
├── sub_templates/              # Кастомная страница подписки
│   └── skrepnet/
│       └── index.html
├── backups/                    # Бэкапы БД
└── .env                        # Секреты (в .gitignore)
🔒 Безопасность
✅ .env в .gitignore — секреты не попадают в Git

✅ Права 600 на .env — только владелец может читать

✅ API-токен 3x-ui вместо логина/пароля — обходит CSRF-защиту

✅ Systemd с Restart=always — бот сам поднимается при падении

⚠️ Смени токены после первой настройки:

@BotFather → /revoke

Панель 3x-ui → сменить пароль и URI Path

Security → новый API-токен

💰 Экономика
Для покрытия ~3000 ₽/мес (сервер) нужно:

Способ доната	Комиссия	Собрать
⭐ Telegram Stars	~30%	~4300 ₽
💸 DonationAlerts	~8,5%	~3300 ₽
🔀 Смешанно (50/50)	—	~3800 ₽
Итого: ~30 активных пользователей × 110–150 ₽/мес — и сервер покрыт.

🛠️ Технологии
Python 3.12 — язык разработки

aiogram 3.13 — Telegram Bot API

SQLite (aiosqlite) — база данных

APScheduler — планировщик задач

aiohttp — HTTP-запросы к 3x-ui API

Hysteria2 — протокол VPN

3x-ui — панель управления VPN

🗺️ Roadmap
☑ Выдача подписок Hysteria2
☑ Одобрение админом
☑ Ручное продление
☑ Напоминания
☑ Реферальная система
☑ Донат: Stars + DonationAlerts
☑ Инструкции для 6 платформ
☑ Меню «Управление» на кнопках
☑ Соглашение с пользователем
☑ Автоудаление неактивных
□ Статистика донатов через API
□ Онлайн-клиенты в статистике
□ Мониторинг панели 3x-ui
□ Инструкции для Apple TV / Samsung TV / LG TV
📄 Лицензия
Приватный проект. Все права защищены.

<div align="center">
Сделано с ❤️ для своих

@elbRUS62

</div> READMEEOF ```
Эта команда создаст README целиком через cat — без риска сбить разметку при копировании в nano.

✅ Проверь, что всё правильно
bash
grep -c '```' /root/skrepnet-bot/README.md
Должно быть чётное число (например, 20, 22). Если нечётное — где-то сломалась разметка.

🚀 Загрузи в Git
bash
cd /root/skrepnet-bot
git add README.md
git commit -m "Исправлена разметка README"
git push
Скинь результат — если разметка на GitHub отображается правильно, README готов. 🚀

This response is AI-generated, for reference only.


🏗️ Архитектура
text
┌─────────────────────┐         ┌──────────────────────┐
│  Зарубежный сервер  │         │  Российский сервер   │
│  (Бот)              │◄───────►│  (3x-ui + Hysteria2) │
│                     │  HTTPS  │                      │
│  • Telegram Bot     │         │  • Панель 3x-ui      │
│  • SQLite           │         │  • 🇬🇧 + 🇱🇻 серверы  │
│  • Бэкапы           │         │  • Subscription page │
└─────────────────────┘         └──────────────────────┘
Бот — на зарубежном VPS (прямой доступ к Telegram API)

3x-ui — на российском VPS (там, где VPN)

Связь — через API-токен 3x-ui по HTTPS

📋 Требования
VPS за рубежом (для доступа к Telegram API без блокировок) — ~200–500 ₽/мес

VPS с 3x-ui (Hysteria2) — ~3000 ₽/мес

Python 3.10+

API-токен 3x-ui (Settings → Security → API Tokens)

Бот в Telegram (создаётся через @BotFather)

🔧 Ручная настройка
1. Виртуальное окружение
bash
python3 -m venv venv
source venv/bin/activate
pip install -r requirements.txt
2. Файл .env
bash
cp .env.example .env
nano .env
Заполни переменные:

env
# Telegram
BOT_TOKEN=токен_от_BotFather
ADMIN_ID=твой_telegram_id
BOT_USERNAME=skrepnet_bot

# 3x-ui Panel
XUI_HOST=https://твой-сервер:3775
XUI_BASE_PATH=/твой_секретный_путь
XUI_API_TOKEN=токен_из_панели

# Inbounds
XUI_INBOUND_GB=5
XUI_INBOUND_LV=6

# Subscription
SUB_BASE_URL=https://твой-сервер:9913
SUB_PATH=/subs_твой_путь/

# Limits
LIMIT_IP=3
SUBSCRIPTION_DAYS=30

# Donate
DONATE_URL=https://www.donationalerts.com/r/твой_ник
DONATE_TEXT=Текст плашки доната

# Database
DB_PATH=skrepnet.db
3. Systemd
bash
sudo nano /etc/systemd/system/skrepnet-bot.service
ini
[Unit]
Description=SkrepNet Telegram Bot
After=network.target

[Service]
Type=simple
User=root
WorkingDirectory=/root/skrepnet-bot
Environment="PYTHONUNBUFFERED=1"
ExecStart=/root/skrepnet-bot/venv/bin/python /root/skrepnet-bot/bot.py
Restart=always
RestartSec=10
StandardOutput=journal
StandardError=journal

[Install]
WantedBy=multi-user.target
bash
sudo systemctl daemon-reload
sudo systemctl enable skrepnet-bot
sudo systemctl start skrepnet-bot
4. Бэкапы
bash
crontab -e
Добавь:

text
0 3 * * * /root/skrepnet-bot/backup.sh >> /root/skrepnet-bot/backups/backup.log 2>&1
📁 Структура проекта
text
skrepnet-bot/
├── bot.py                      # Точка входа
├── config.py                   # Чтение .env
├── database.py                 # SQLite: пользователи, админы
├── xui_client.py               # API 3x-ui (Bearer-токен)
├── keyboards.py                # Все кнопки и меню
├── scheduler.py                # Напоминания + автоочистка
├── install.sh                  # Интерактивный установщик
├── backup.sh                   # Скрипт бэкапа
├── requirements.txt            # Зависимости Python
├── handlers/                   # Обработчики по модулям
│   ├── __init__.py             # Сборка роутеров
│   ├── utils.py                # sanitize_email + TERMS_TEXT
│   ├── states.py               # FSM-состояния
│   ├── start.py                # /start и рефералка
│   ├── subscription.py         # Заявки, соглашение, подписка
│   ├── donate.py               # Донат + приглашения
│   ├── connect.py              # 6 инструкций
│   ├── admin.py                # Меню «Управление»
│   └── changelog.py            # История обновлений
├── sub_templates/              # Кастомная страница подписки
│   └── skrepnet/
│       └── index.html
├── backups/                    # Бэкапы БД
└── .env                        # Секреты (в .gitignore)
🔒 Безопасность
✅ .env в .gitignore — секреты не попадают в Git

✅ Права 600 на .env — только владелец может читать

✅ API-токен 3x-ui вместо логина/пароля — обходит CSRF-защиту

✅ Systemd с Restart=always — бот сам поднимается при падении

⚠️ Смени токены после первой настройки:

@BotFather → /revoke

Панель 3x-ui → сменить пароль и URI Path

Security → новый API-токен

💰 Экономика
Для покрытия ~3000 ₽/мес (сервер) нужно:

Способ доната	Комиссия	Собрать
⭐ Telegram Stars	~30%	~4300 ₽
💸 DonationAlerts	~8,5%	~3300 ₽
🔀 Смешанно (50/50)	—	~3800 ₽
Итого: ~30 активных пользователей × 110–150 ₽/мес — и сервер покрыт.

🛠️ Технологии
Python 3.12 — язык разработки

aiogram 3.13 — Telegram Bot API

SQLite (aiosqlite) — база данных

APScheduler — планировщик задач

aiohttp — HTTP-запросы к 3x-ui API

Hysteria2 — протокол VPN

3x-ui — панель управления VPN

🗺️ Roadmap
☑ Выдача подписок Hysteria2
☑ Одобрение админом
☑ Ручное продление
☑ Напоминания
☑ Реферальная система
☑ Донат: Stars + DonationAlerts
☑ Инструкции для 6 платформ
☑ Меню «Управление» на кнопках
☑ Соглашение с пользователем
☑ Автоудаление неактивных
□ Статистика донатов через API
□ Онлайн-клиенты в статистике
□ Мониторинг панели 3x-ui
□ Инструкции для Apple TV / Samsung TV / LG TV
📄 Лицензия
Приватный проект. Все права защищены.

<div align="center">
Сделано с ❤️ для своих

@elbRUS62

</div> ```

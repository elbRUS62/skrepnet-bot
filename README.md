🛡️ SkrepNet Bot
Telegram-бот для выдачи бесплатных подписок Hysteria2 через панель 3x-ui, с реферальной системой, донатами и веб-выдачей без Telegram.

🤖 Бот в Telegram: @skrepnet_bot
🆘 Поддержка: @SkrepNet_support

✨ Возможности
Для пользователей
📦 Получение подписки Hysteria2 (сервер 🇬🇧)

📜 Соглашение с документами перед первой заявкой (telegra.ph)

📱 Лимит 3 IP одновременно, срок подписки 30 дней

🔄 Ручное продление по кнопке

📷 QR-код для быстрого подключения

🔔 Напоминания о продлении (за 3 дня и в день окончания, тихие)

👥 Реферальная система: рефералы одобряются автоматически

➕ Приглашение друзей без Telegram — одноразовая ссылка на веб-сайт

💰 Донат: Telegram Stars + DonationAlerts

📖 Инструкции для 6 платформ (Android, iOS, Windows, macOS, Android TV, Linux)

🍎 Happ — рекомендуемое приложение

Для админов
🛠 Меню «Управление» — всё на кнопках

👤 Добавление/удаление админов по username (с защитой .env-админов)

📋 Список админов (основные + добавленные)

🔄 Обновление подписки по username

🗑 Удаление пользователей (из БД и 3x-ui одновременно)

♻️ Сброс заявки

📢 Рассылка всем активным

📊 Статистика + топ-5 приглашающих

🔐 Кнопка входа в панель 3x-ui

📋 История обновлений

Веб-сайт (для друзей без Telegram)
🌐 Flask-приложение на HTTPS (порт 8443)

🔗 Одноразовые ссылки-приглашения (действуют 7 дней, срабатывают 1 раз)

✅ Согласие с документами → мгновенная выдача подписки

📷 QR-код прямо на странице

Автоматика
⏰ Напоминания о продлении — ежедневно в 10:00 (без звука)

🗑 Автоудаление неактивных (30+ дней) — ежедневно в 4:00

💾 Бэкапы базы данных — ежедневно в 3:00, хранение 30 дней

🔧 Systemd-автозапуск (Restart=always)

🔌 DonationAlerts WebSocket через Centrifugo (автопереподключение)

🏗️ Архитектура
Бот работает на зарубежном VPS (прямой доступ к Telegram API)

Панель 3x-ui — на российском VPS

Связь между ними — через API-токен (Bearer) по HTTPS

Веб-сайт (web_app.py) — Flask на HTTPS, отдельный порт

Донаты — Telegram Stars (инвойсы) + DonationAlerts через Centrifugo WebSocket

📋 Требования
VPS за рубежом (для бота)

VPS с 3x-ui + Hysteria2 (для панели)

Python 3.10+

API-токен 3x-ui (Settings → Security → API Tokens)

Бот в Telegram (создаётся через @BotFather)

Токен DonationAlerts (для приёма донатов)

SSL-сертификат для веб-сайта (например, Let's Encrypt)

🚀 Быстрая установка
git clone https://github.com/elbRUS62/skrepnet-bot.git
cd skrepnet-bot
./install.sh

Скрипт задаст все вопросы (BOT_TOKEN, ADMIN_ID, XUI_HOST, XUI_API_TOKEN, инбаунды, SUB_BASE_URL, лимиты, донат) и настроит бота автоматически: создаст .env с правами 600, поставит зависимости в venv, настроит cron для бэкапов и systemd-сервис.

Полезные команды
systemctl status skrepnet-bot # статус
journalctl -u skrepnet-bot -f # логи в реальном времени
systemctl restart skrepnet-bot # перезапуск
ls -la backups/ # бэкапы

📁 Структура проекта
bot.py — точка входа
config.py — чтение .env, валидация
database.py — SQLite (users, admins, invite_links, invites)
xui_client.py — API 3x-ui (add/get/update/delete client)
keyboards.py — кнопки и меню
scheduler.py — напоминания + автоочистка
docs_config.py — ссылки на документы в telegra.ph
donation_socket.py — DonationAlerts через Centrifugo WebSocket
web_app.py — Flask-сайт для выдачи без Telegram
install.sh — установщик
backup.sh — бэкап базы
handlers/ — обработчики по модулям (start, subscription, donate, connect, admin, changelog, invite, states, utils)
web/ — templates (invite.html, error.html, index.html) и static (style.css)

🔄 Как работает выдача подписки
Обычный пользователь:

/start → «📦 Получить подписку»

Принимает документы → заявка уходит админам

Админ жмёт «✅ Одобрить» → клиент создаётся в 3x-ui, пользователь получает ссылку

Реферал (по ссылке ?start=ref_<id>):

/start по deep-link → автоматически записывается invited_by

Принял документы → автоодобрение, клиент создаётся сразу

Пригласивший получает уведомление

Друг без Telegram:

Пользователь → «➕ Добавить без Telegram»

Выбирает контакт или вводит @username/ID вручную

Получает одноразовую ссылку https://<host>:8443/invite/<token>

Друг открывает в браузере → принимает условия → получает подписку + QR

🔒 Безопасность
.env в .gitignore, права 600

API-токен 3x-ui вместо логина/пароля

Systemd с Restart=always

Валидация обязательных переменных при старте (config.py)

Смени токены после первой настройки

🗺️ Roadmap
☑ Выдача подписок Hysteria2
☑ Одобрение админом
☑ Автоодобрение рефералов
☑ Ручное продление
☑ Напоминания
☑ Реферальная система + топ-5
☑ Приглашения без Telegram (веб-выдача)
☑ Донат: Stars + DonationAlerts
☑ Инструкции для 6 платформ
☑ Меню «Управление»
☑ Соглашение с пользователем
☑ Автоудаление неактивных
□ Второй сервер (🇱🇻) в подписке
□ Статистика донатов через API
□ Онлайн-клиенты
□ Мониторинг панели
□ Apple TV / Samsung TV / LG TV
@elbRUS62

<div align="center">

# 🛡️ SkrepNet Bot

### Бесплатный VPN для своих

**Telegram-бот для выдачи подписок Hysteria2 через панель 3x-ui**

[![Python](https://img.shields.io/badge/Python-3.10%2B-blue?logo=python&logoColor=white)](https://www.python.org/)
[![aiogram](https://img.shields.io/badge/aiogram-3.13-2CA5E0?logo=telegram&logoColor=white)](https://aiogram.dev/)
[![3x-ui](https://img.shields.io/badge/3x--ui-3.9.0-green)](https://github.com/MHSanaei/3x-ui)
[![Stars](https://img.shields.io/badge/⭐_Telegram_Stars-поддержка-yellow)]()

</div>

---

## ✨ Возможности

## ✨ Возможности

### Для пользователей
- 📦 Получение подписки Hysteria2 (2 сервера: 🇬🇧 + 🇱🇻 в одной ссылке)
- 📜 Соглашение с правилами перед первой заявкой
- 📱 Лимит 3 IP одновременно, срок 30 дней
- 🔔 Напоминания о продлении (за 3 дня и в день окончания)
- 👥 Реферальная система с приглашениями
- 💰 Донат: Telegram Stars + DonationAlerts
- 📖 Инструкции для 6 платформ (Android, iOS, Windows, macOS, Android TV, Linux)
- 🍎 Happ — рекомендуемое приложение

### Для админов
- 🛠 Меню «Управление» — всё на кнопках
- 👤 Добавление/удаление админов по username
- 🔄 Обновление подписок по username
- 🗑 Удаление пользователей (из БД и 3x-ui)
- 📢 Рассылка всем активным
- 📊 Статистика
- 🔐 Кнопка входа в панель 3x-ui
- 📋 История обновлений

### Автоматика
- ⏰ Напоминания о продлении — каждый день в 10:00
- 🗑 Автоудаление неактивных (30+ дней) — в 4:00
- 💾 Бэкапы базы — ежедневно в 3:00, хранение 30 дней
- 🔧 Systemd-автозапуск

## 🏗️ Архитектура

Бот работает на зарубежном VPS (прямой доступ к Telegram API), а панель 3x-ui — на российском. Связь между ними — через API-токен по HTTPS.

## 📋 Требования

- VPS за рубежом — ~200–500 руб/мес
- VPS с 3x-ui (Hysteria2) — ~3000 руб/мес
- Python 3.10+
- API-токен 3x-ui (Settings -> Security -> API Tokens)
- Бот в Telegram (создаётся через @BotFather)

## 🚀 Быстрая установка

Скопируй команды и выполни на сервере:

```
git clone https://github.com/elbRUS62/skrepnet-bot.git
 skrepnet-bot
cd skrepnet-bot                                          
./install.sh                                             
```

Скрипт задаст все вопросы и настроит бота автоматически.

## 📁 Структура проекта

- bot.py — точка входа
- config.py — чтение .env
- database.py — SQLite
- xui_client.py — API 3x-ui
- keyboards.py — кнопки и меню
- scheduler.py — напоминания + автоочистка
- install.sh — установщик
- backup.sh — бэкап
- handlers/ — обработчики по модулям

## 🔒 Безопасность

- .env в .gitignore
- Права 600 на .env
- API-токен вместо пароля
- Systemd с Restart=always
- Смени токены после первой настройки

## 🗺️ Roadmap

- [x] Выдача подписок Hysteria2
- [x] Одобрение админом
- [x] Ручное продление
- [x] Напоминания
- [x] Реферальная система
- [x] Донат: Stars + DonationAlerts
- [x] Инструкции для 6 платформ
- [x] Меню «Управление»
- [x] Соглашение с пользователем
- [x] Автоудаление неактивных
- [ ] Статистика донатов через API
- [ ] Онлайн-клиенты
- [ ] Мониторинг панели
- [ ] Apple TV / Samsung TV / LG TV

## 📄 Лицензия

Приватный проект. Все права защищены.

---

**Сделано с ❤️ для своих**

@elbRUS62

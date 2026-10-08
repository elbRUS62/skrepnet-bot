from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton, ReplyKeyboardMarkup, KeyboardButton
from config import DONATE_URL


def main_menu():
    return ReplyKeyboardMarkup(
        keyboard=[
            [KeyboardButton(text="❤️ Поддержать проект")],
            [KeyboardButton(text="📦 Получить подписку"), KeyboardButton(text="🔑 Моя подписка")],
            [KeyboardButton(text="👥 Пригласить друга")]
        ],
        resize_keyboard=True,
        is_persistent=True
    )


def admin_menu():
    return ReplyKeyboardMarkup(
        keyboard=[
            [KeyboardButton(text="❤️ Поддержать проект")],
            [KeyboardButton(text="📦 Получить подписку"), KeyboardButton(text="🔑 Моя подписка")],
            [KeyboardButton(text="👥 Пригласить друга"), KeyboardButton(text="📊 Статистика")],
            [KeyboardButton(text="🛠 Управление"), KeyboardButton(text="📋 История обновлений")]
        ],
        resize_keyboard=True,
        is_persistent=True
    )


def admin_manage_keyboard():
    return InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(text="👤 Добавить админа", callback_data="admin_add")],
        [InlineKeyboardButton(text="🗑 Удалить админа", callback_data="admin_del")],
        [InlineKeyboardButton(text="📋 Список админов", callback_data="admin_list")],
        [InlineKeyboardButton(text="🔄 Обновить подписку", callback_data="admin_extend")],
        [InlineKeyboardButton(text="♻️ Сбросить заявку", callback_data="admin_reset")],
        [InlineKeyboardButton(text="🗑 Удалить пользователя", callback_data="admin_delete_user")],
        [InlineKeyboardButton(text="📢 Рассылка", callback_data="admin_broadcast")],
        [InlineKeyboardButton(text="🔐 Панель 3x-ui", callback_data="admin_panel")],
        [InlineKeyboardButton(text="⬅️ Закрыть", callback_data="admin_close")]
    ])


def admin_approve_keyboard(telegram_id: int):
    return InlineKeyboardMarkup(inline_keyboard=[
        [
            InlineKeyboardButton(text="✅ Одобрить", callback_data=f"approve:{telegram_id}"),
            InlineKeyboardButton(text="❌ Отклонить", callback_data=f"reject:{telegram_id}")
        ]
    ])


def donate_keyboard():
    return InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(text="⭐ Поддержать звёздами", callback_data="donate_stars")],
        [InlineKeyboardButton(text="💸 DonationAlerts", url=DONATE_URL)]
    ])


def donate_stars_keyboard():
    return InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(text="⭐ 10 звёзд", callback_data="stars_10")],
        [InlineKeyboardButton(text="⭐ 25 звёзд", callback_data="stars_25")],
        [InlineKeyboardButton(text="⭐ 50 звёзд", callback_data="stars_50")],
        [InlineKeyboardButton(text="⭐ 100 звёзд", callback_data="stars_100")],
        [InlineKeyboardButton(text="⬅️ Назад", callback_data="back_to_donate")]
    ])


def renew_keyboard():
    return InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(text="🔄 Продлить подписку", callback_data="renew")],
        [InlineKeyboardButton(text="❤️ Поддержать проект", url=DONATE_URL)]
    ])


def subscription_keyboard():
    return InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(text="📖 Как подключиться", callback_data="connect_help")],
        [InlineKeyboardButton(text="🔄 Продлить", callback_data="renew")],
        [InlineKeyboardButton(text="❤️ Поддержать", url=DONATE_URL)]
    ])


def share_keyboard(bot_username: str, telegram_id: int):
    share_text = "Присоединяйся к SkrepNet — бесплатный VPN для своих!"
    share_url = f"https://t.me/share/url?url=https://t.me/{bot_username}?start=ref_{telegram_id}&text={share_text}"
    return InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(text="📤 Поделиться с друзьями", url=share_url)]
    ])


def connect_keyboard():
    return InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(text="📱 Android", callback_data="connect_android")],
        [InlineKeyboardButton(text="🍎 iOS", callback_data="connect_ios")],
        [InlineKeyboardButton(text="💻 Windows", callback_data="connect_windows")],
        [InlineKeyboardButton(text="🖥 macOS", callback_data="connect_macos")],
        [InlineKeyboardButton(text="📺 Android TV", callback_data="connect_androidtv")],
        [InlineKeyboardButton(text="🐧 Linux", callback_data="connect_linux")]
    ])


def back_to_connect_keyboard():
    return InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(text="⬅️ Назад", callback_data="connect_help")]
    ])


def changelog_keyboard():
    return InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(text="📋 Показать историю", callback_data="show_changelog")]
    ])


def terms_keyboard():
    return InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(text="✅ Согласен", callback_data="accept_terms")],
        [InlineKeyboardButton(text="❌ Отмена", callback_data="decline_terms")]
    ])

def admin_panel_keyboard():
    panel_url = "https://ru-skrepnet.duckdns.org:3775/MASbquuCRx18QVK8l6/panel"
    return InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(text="🔐 Войти в 3x-ui", url=panel_url)]
    ])
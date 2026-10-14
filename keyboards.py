
from docs_config import DOCS
from aiogram.types import (
    InlineKeyboardMarkup, InlineKeyboardButton,
    ReplyKeyboardMarkup, KeyboardButton,
    KeyboardButtonRequestUsers
)
from config import DONATE_URL


def main_menu():
    return ReplyKeyboardMarkup(
        keyboard=[
            [KeyboardButton(text="❤️ Поддержать проект")],
            [KeyboardButton(text="📦 Получить подписку"), KeyboardButton(text="🔑 Моя подписка")],
            [KeyboardButton(text="👥 Пригласить друга"), KeyboardButton(text="🆘 Техподдержка")],
            [KeyboardButton(text="➕ Добавить без Telegram"), KeyboardButton(text="📚 Документы")]
        ],
        resize_keyboard=True,
        is_persistent=True
    )


def admin_menu():
    return ReplyKeyboardMarkup(
        keyboard=[
            [KeyboardButton(text="❤️ Поддержать проект")],
            [KeyboardButton(text="📦 Получить подписку"), KeyboardButton(text="🔑 Моя подписка")],
            [KeyboardButton(text="👥 Пригласить друга"), KeyboardButton(text="🆘 Техподдержка")],
            [KeyboardButton(text="➕ Добавить без Telegram"), KeyboardButton(text="📚 Документы")],
            [KeyboardButton(text="📊 Статистика"), KeyboardButton(text="🛠 Управление")],
            [KeyboardButton(text="📋 История обновлений")]
        ],
        resize_keyboard=True,
        is_persistent=True
    )


def admin_manage_keyboard():
    return InlineKeyboardMarkup(inline_keyboard=[
        [
            InlineKeyboardButton(text="📋 Список заявок", callback_data="admin_list_requests"),
            InlineKeyboardButton(text="🔄 Обновить подписку", callback_data="admin_extend"),
        ],
        [
            InlineKeyboardButton(text="📢 Рассылка", callback_data="admin_broadcast"),
            InlineKeyboardButton(text="👥 Пользователи", callback_data="admin_menu_users"),
        ],
        [
            InlineKeyboardButton(text="🔐 Панель 3x-ui", callback_data="admin_panel"),
        ],
        [
            InlineKeyboardButton(text="⬅️ Закрыть", callback_data="admin_close"),
        ],
    ])


def admin_submenu_users():
    return InlineKeyboardMarkup(inline_keyboard=[
        [
            InlineKeyboardButton(text="♻️ Сбросить заявку", callback_data="admin_reset"),
        ],
        [
            InlineKeyboardButton(text="🗑 Удалить пользователя", callback_data="admin_delete_user"),
        ],
        [
            InlineKeyboardButton(text="⬅️ Назад", callback_data="admin_manage_back"),
        ],
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
        [InlineKeyboardButton(text="📷 QR-код", callback_data="show_qr")],
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

def support_keyboard():
    return InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(text="🆘 Техподдержка", url="https://t.me/skrepnet_support")]
    ])

def documents_keyboard():
    return InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(text=DOCS["rules"]["title"], url=DOCS["rules"]["url"])],
        [InlineKeyboardButton(text=DOCS["privacy"]["title"], url=DOCS["privacy"]["url"])],
        [InlineKeyboardButton(text=DOCS["terms"]["title"], url=DOCS["terms"]["url"])],
        [InlineKeyboardButton(text="🏠 В главное меню", callback_data="back_to_main")]
    ])


def terms_keyboard():
    return InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(text=DOCS["rules"]["title"], url=DOCS["rules"]["url"])],
        [InlineKeyboardButton(text=DOCS["privacy"]["title"], url=DOCS["privacy"]["url"])],
        [InlineKeyboardButton(text=DOCS["terms"]["title"], url=DOCS["terms"]["url"])],
        [InlineKeyboardButton(text="✅ Я согласен со всеми условиями", callback_data="accept_terms")],
        [InlineKeyboardButton(text="❌ Отмена", callback_data="decline_terms")]
    ])

def back_to_documents_keyboard():
    return InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(text="🏠 В главное меню", callback_data="back_to_main")]
    ])

def invite_no_tg_keyboard():
    """Клавиатура для добавления друга без Telegram."""
    return ReplyKeyboardMarkup(
        keyboard=[
            [KeyboardButton(
                text="👤 Выбрать из контактов",
                request_users=KeyboardButtonRequestUsers(
                    request_id=1,
                    user_is_bot=False,
                    max_quantity=1,
                    request_name=True,
                    request_username=True
                )
            )],
            [KeyboardButton(text="✍️ Ввести @username или ID вручную")],
            [KeyboardButton(text="❌ Отмена")]
        ],
        resize_keyboard=True,
        one_time_keyboard=True
    )


def invite_share_keyboard(invite_url: str):
    """Кнопка «Поделиться» с готовой ссылкой."""
    share_text = "Присоединяйся к SkrepNet — бесплатный VPN!"
    share_url = f"https://t.me/share/url?url={invite_url}&text={share_text}"
    return InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(text="📤 Поделиться ссылкой", url=share_url)]
    ])


def email_conflict_keyboard(telegram_id: int, base_email: str):
    """Клавиатура для выбора нового email при конфликте."""
    suggested = [
        f"{base_email}_2",
        f"{base_email}_3",
        f"{base_email}_4",
    ]
    id_email = f"{base_email}_{telegram_id}"

    buttons = []
    # Использовать существующего клиента с тем же email
    buttons.append([InlineKeyboardButton(
        text=f"♻️ Использовать существующий {base_email}",
        callback_data=f"use_existing:{telegram_id}"
    )])
    # Суффиксы
    for email in suggested:
        buttons.append([InlineKeyboardButton(
            text=f"📧 {email}",
            callback_data=f"retry_email:{telegram_id}:{email}"
        )])
    buttons.append([InlineKeyboardButton(
        text=f"🆔 {id_email}",
        callback_data=f"retry_email:{telegram_id}:{id_email}"
    )])
    buttons.append([InlineKeyboardButton(
        text="✍️ Ввести вручную",
        callback_data=f"manual_email:{telegram_id}"
    )])
    buttons.append([InlineKeyboardButton(
        text="❌ Отменить заявку",
        callback_data=f"cancel_email:{telegram_id}"
    )])
    return InlineKeyboardMarkup(inline_keyboard=buttons)


def users_list_keyboard(users: list, action: str, page: int, total: int, per_page: int = 10):
    """Клавиатура со списком пользователей и пагинацией.

    action: 'extend' | 'delete' | 'reset'
    """
    buttons = []

    for user in users:
        # Приоритет: username > first_name > telegram_id
        if user["username"]:
            display = f"@{user['username']}"
            if user["first_name"]:
                display += f" — {user['first_name']}"
        elif user["first_name"]:
            display = f"{user['first_name']} — {user['telegram_id']}"
        else:
            display = str(user["telegram_id"])

        # Обрезаем до 60 символов (Telegram ограничивает 64)
        if len(display) > 60:
            display = display[:60] + "…"

        buttons.append([InlineKeyboardButton(
            text=display,
            callback_data=f"user_action:{action}:{user['telegram_id']}"
        )])

    # Пагинация
    nav = []
    if page > 0:
        nav.append(InlineKeyboardButton(
            text="⬅️",
            callback_data=f"users_page:{action}:{page - 1}"
        ))

    total_pages = (total + per_page - 1) // per_page
    nav.append(InlineKeyboardButton(
        text=f"{page + 1}/{total_pages}",
        callback_data="noop"
    ))

    if (page + 1) * per_page < total:
        nav.append(InlineKeyboardButton(
            text="➡️",
            callback_data=f"users_page:{action}:{page + 1}"
        ))

    if nav:
        buttons.append(nav)

    buttons.append([InlineKeyboardButton(
        text="⬅️ Назад",
        callback_data="admin_manage_back"
    )])

    return InlineKeyboardMarkup(inline_keyboard=buttons)
import logging
from aiogram import Router, F
from aiogram.types import Message, CallbackQuery
from aiogram.fsm.context import FSMContext
from aiogram.fsm.state import State, StatesGroup

from config import ADMIN_IDS
from database import get_user, create_invite_link, increment_invites, add_invite
from keyboards import invite_no_tg_keyboard, invite_share_keyboard, main_menu

router = Router()
logger = logging.getLogger(__name__)

# Ссылка на твой сайт (заменишь позже, когда сделаем сайт)
SITE_URL = "https://gb-skrepnet.duckdns.org:8443/invite"


class InviteStates(StatesGroup):
    waiting_username = State()


@router.message(F.text == "➕ Добавить без Telegram")
async def invite_no_tg_start(message: Message):
    user = await get_user(message.from_user.id)

    if not user or user["status"] != "active":
        await message.answer("Сначала получи подписку через «📦 Получить подписку».")
        return

    await message.answer(
        "➕ <b>Добавить друга без Telegram</b>\n\n"
        "Выбери способ:\n"
        "• Выбрать из контактов Telegram\n"
        "• Или ввести @username / ID вручную\n\n"
        "После этого я создам одноразовую ссылку, "
        "которую ты передашь любым способом.",
        reply_markup=invite_no_tg_keyboard(),
        parse_mode="HTML"
    )


@router.message(F.users_shared)
async def handle_shared_user(message: Message):
    """Обрабатывает выбранного пользователя из контактов."""
    shared = message.users_shared

    if not shared or not shared.users:
        await message.answer("❌ Никто не выбран")
        return

    friend = shared.users[0]
    friend_id = friend.user_id
    friend_username = friend.username
    friend_first_name = friend.first_name or ""

    if friend_id == message.from_user.id:
        await message.answer("❌ Нельзя пригласить самого себя")
        return

    existing = await get_user(friend_id)
    if existing and existing["status"] == "active":
        await message.answer(f"❌ @{friend_username or friend_id} уже в SkrepNet")
        return

    token = await create_invite_link(
        message.from_user.id,
        friend_user_id=friend_id,
        friend_username=friend_username
    )

    invite_url = f"{SITE_URL}/{token}"

    await increment_invites(message.from_user.id)
    await add_invite(
        inviter_id=message.from_user.id,
        invited_user_id=friend_id,
        invited_username=friend_username,
        invited_first_name=friend_first_name,
        invite_type="no_tg"
    )

    display_name = f"@{friend_username}" if friend_username else friend_first_name or str(friend_id)

    await message.answer(
        f"✅ <b>Ссылка для друга готова!</b>\n\n"
        f"👤 Друг: {display_name}\n\n"
        f"🔗 <b>Ссылка:</b>\n"
        f"<code>{invite_url}</code>\n\n"
        f"📌 <b>Что делать:</b>\n"
        f"1. Отправь эту ссылку другу любым способом "
        f"(MAX, SMS, WhatsApp, голосом)\n"
        f"2. Друг откроет её в браузере\n"
        f"3. Согласится с документами\n"
        f"4. Получит подписку и QR-код\n\n"
        f"⏳ Ссылка действует 7 дней и срабатывает 1 раз.",
        parse_mode="HTML",
        reply_markup=invite_share_keyboard(invite_url)
    )


@router.message(F.text == "✍️ Ввести @username или ID вручную")
async def invite_manual_start(message: Message, state: FSMContext):
    await message.answer(
        "✍️ Введи <b>@username</b> или <b>ID</b> друга:\n\n"
        "Например: <code>@ivan_petrov</code> или <code>123456789</code>",
        parse_mode="HTML"
    )
    await state.set_state(InviteStates.waiting_username)


@router.message(InviteStates.waiting_username)
async def invite_manual_process(message: Message, state: FSMContext):
    raw = message.text.strip()

    friend_username = None
    friend_id = None

    if raw.startswith("@"):
        friend_username = raw.lstrip("@")
    elif raw.isdigit():
        friend_id = int(raw)
    else:
        friend_username = raw

    token = await create_invite_link(
        message.from_user.id,
        friend_user_id=friend_id,
        friend_username=friend_username
    )

    invite_url = f"{SITE_URL}/{token}"

    await increment_invites(message.from_user.id)
    await add_invite(
        inviter_id=message.from_user.id,
        invited_user_id=friend_id,
        invited_username=friend_username,
        invited_first_name=None,
        invite_type="no_tg"
    )

    await message.answer(
        f"✅ <b>Ссылка для друга готова!</b>\n\n"
        f"👤 Друг: {raw}\n\n"
        f"🔗 <b>Ссылка:</b>\n"
        f"<code>{invite_url}</code>\n\n"
        f"📌 Отправь её другу любым способом.\n"
        f"⏳ Действует 7 дней, срабатывает 1 раз.",
        parse_mode="HTML",
        reply_markup=invite_share_keyboard(invite_url)
    )

    await state.clear()


@router.message(F.text == "❌ Отмена")
async def invite_cancel(message: Message, state: FSMContext):
    await state.clear()
    await message.answer(
        "Отменено.",
        reply_markup=main_menu()
    )

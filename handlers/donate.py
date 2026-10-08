import logging

from aiogram import Router, F
from aiogram.types import Message, CallbackQuery, LabeledPrice, PreCheckoutQuery

from config import ADMIN_IDS, DONATE_TEXT, DONATE_URL, BOT_USERNAME
from database import get_user
from keyboards import donate_keyboard, donate_stars_keyboard, share_keyboard, support_keyboard

router = Router()
logger = logging.getLogger(__name__)


@router.message(F.text == "❤️ Поддержать проект")
async def donate(message: Message):
    await message.answer(
        f"{DONATE_TEXT}\n\n"
        f"Ссылка для доната: {DONATE_URL}",
        reply_markup=donate_keyboard()
    )


@router.callback_query(F.data == "donate_stars")
async def donate_stars_menu(callback: CallbackQuery):
    await callback.message.edit_text(
        "⭐ <b>Поддержать проект звёздами</b>\n\n"
        "Выбери сумму. Звёзды зачислятся мгновенно.\n\n"
        "1 ⭐ ≈ 1.5–2 ₽",
        reply_markup=donate_stars_keyboard(),
        parse_mode="HTML"
    )
    await callback.answer()


@router.callback_query(F.data == "back_to_donate")
async def back_to_donate(callback: CallbackQuery):
    await callback.message.edit_text(
        f"{DONATE_TEXT}\n\n"
        f"Ссылка для доната: {DONATE_URL}",
        reply_markup=donate_keyboard()
    )
    await callback.answer()


@router.callback_query(F.data.startswith("stars_"))
async def donate_stars_invoice(callback: CallbackQuery):
    amount = int(callback.data.split("_")[1])
    prices = [LabeledPrice(label="Поддержка SkrepNet", amount=amount)]

    await callback.bot.send_invoice(
        chat_id=callback.from_user.id,
        title="Поддержка SkrepNet",
        description=f"Донат {amount} ⭐ на оплату сервера",
        payload=f"donate_{callback.from_user.id}_{amount}",
        provider_token="",
        currency="XTR",
        prices=prices
    )
    await callback.answer()


@router.pre_checkout_query()
async def process_pre_checkout(pre_checkout_query: PreCheckoutQuery):
    await pre_checkout_query.answer(ok=True)


@router.message(F.successful_payment)
async def process_successful_payment(message: Message):
    payment = message.successful_payment
    amount = payment.total_amount

    for admin_id in ADMIN_IDS:
        try:
            await message.bot.send_message(
                admin_id,
                f"⭐ <b>Новый донат звёздами!</b>\n\n"
                f"От: {message.from_user.full_name}\n"
                f"ID: {message.from_user.id}\n"
                f"Сумма: {amount} ⭐",
                parse_mode="HTML",
                disable_notification=True
            )
        except Exception:
            pass

    await message.answer(
        f"⭐ <b>Спасибо за поддержку!</b>\n\n"
        f"Ты отправил {amount} звёзд. Это помогает серверу работать.\n\n"
        f"❤️ Ты лучший!",
        parse_mode="HTML"
    )


@router.message(F.text == "👥 Пригласить друга")
async def invite_friend(message: Message):
    user = await get_user(message.from_user.id)

    if not user:
        await message.answer("Сначала получи подписку через «📦 Получить подписку».")
        return

    invites = user["invites_count"] if user["invites_count"] else 0
    ref_link = f"https://t.me/{BOT_USERNAME}?start=ref_{message.from_user.id}"

    await message.answer(
        f"👥 Пригласи друга — помоги проекту расти!\n\n"
        f"Твоя ссылка:\n`{ref_link}`\n\n"
        f"📊 Ты уже пригласил: {invites} чел.\n\n"
        f"💡 Отправь ссылку друзьям — они получат бесплатный VPN.",
        reply_markup=share_keyboard(BOT_USERNAME, message.from_user.id),
        parse_mode="Markdown"
    )

@router.message(F.text == "🆘 Поддержка")
async def support_button(message: Message):
    await message.answer(
        "🆘 <b>Поддержка SkrepNet</b>\n\n"
        "Если у тебя возникли вопросы, проблемы с подключением "
        "или ты хочешь сообщить о сбое — напиши нам.\n\n"
        "📢 Канал поддержки: @skrepnet_support",
        reply_markup=support_keyboard(),
        parse_mode="HTML"
    )
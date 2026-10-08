from aiogram import Router, F
from aiogram.types import CallbackQuery

from keyboards import connect_keyboard, back_to_connect_keyboard

router = Router()


@router.callback_query(F.data == "connect_help")
async def connect_help(callback: CallbackQuery):
    await callback.message.edit_text(
        "📖 <b>Как подключиться к SkrepNet</b>\n\n"
        "Выбери своё устройство:",
        reply_markup=connect_keyboard(),
        parse_mode="HTML"
    )
    await callback.answer()


@router.callback_query(F.data == "connect_android")
async def connect_android(callback: CallbackQuery):
    await callback.message.edit_text(
        "📱 <b>Android</b>\n\n"
        "<b>Рекомендуем: Happ — Proxy Utility</b>\n"
        "1. Установи <b>Happ</b> из <a href='https://play.google.com/store/apps/details?id=com.happproxy'>Google Play</a>\n"
        "2. Скопируй ссылку из «🔑 Моя подписка»\n"
        "3. В Happ: «+» → «Добавить подписку»\n"
        "4. Вставь ссылку → сохрани\n"
        "5. Выбери сервер → «Подключиться»\n\n"
        "<i>Альтернатива:</i> Hysteria, v2rayNG\n\n"
        "✅ Готово!",
        reply_markup=back_to_connect_keyboard(),
        parse_mode="HTML"
    )
    await callback.answer()


@router.callback_query(F.data == "connect_ios")
async def connect_ios(callback: CallbackQuery):
    await callback.message.edit_text(
        "🍎 <b>iOS (iPhone / iPad)</b>\n\n"
        "<b>Рекомендуем: Happ — Proxy Utility</b>\n"
        "1. Установи <b>Happ</b> из <a href='https://apps.apple.com/us/app/happ-proxy-utility/id6504287215'>App Store</a>\n"
        "2. Скопируй ссылку из «🔑 Моя подписка»\n"
        "3. В Happ: «+» → «Добавить подписку»\n"
        "4. Вставь ссылку → сохрани\n"
        "5. Выбери сервер → включи VPN\n\n"
        "<i>Если нет в российском App Store — смени регион Apple ID на США.</i>\n\n"
        "<i>Альтернатива:</i> Streisand, Shadowrocket\n\n"
        "✅ Готово!",
        reply_markup=back_to_connect_keyboard(),
        parse_mode="HTML"
    )
    await callback.answer()


@router.callback_query(F.data == "connect_windows")
async def connect_windows(callback: CallbackQuery):
    await callback.message.edit_text(
        "💻 <b>Windows</b>\n\n"
        "<b>Рекомендуем: Happ — Proxy Utility</b>\n"
        "1. Скачай <b>Happ</b> с <a href='https://www.happ.su/main/'>официального сайта</a>\n"
        "2. Скопируй ссылку из «🔑 Моя подписка»\n"
        "3. В Happ: «+» → «Добавить подписку»\n"
        "4. Вставь ссылку → сохрани\n"
        "5. Выбери сервер → «Подключиться»\n\n"
        "<i>Альтернатива:</i> Hysteria для Windows\n\n"
        "✅ Готово!",
        reply_markup=back_to_connect_keyboard(),
        parse_mode="HTML"
    )
    await callback.answer()


@router.callback_query(F.data == "connect_macos")
async def connect_macos(callback: CallbackQuery):
    await callback.message.edit_text(
        "🖥 <b>macOS</b>\n\n"
        "<b>Рекомендуем: Happ — Proxy Utility</b>\n"
        "1. Установи <b>Happ</b> из <a href='https://apps.apple.com/us/app/happ-proxy-utility/id6504287215'>App Store</a>\n"
        "2. Скопируй ссылку из «🔑 Моя подписка»\n"
        "3. В Happ: «+» → «Добавить подписку»\n"
        "4. Вставь ссылку → сохрани\n"
        "5. Выбери сервер → включи VPN\n\n"
        "<i>Альтернатива:</i> Streisand, Clash Verge\n\n"
        "✅ Готово!",
        reply_markup=back_to_connect_keyboard(),
        parse_mode="HTML"
    )
    await callback.answer()


@router.callback_query(F.data == "connect_androidtv")
async def connect_androidtv(callback: CallbackQuery):
    await callback.message.edit_text(
        "📺 <b>Android TV</b>\n\n"
        "<b>Способ 1: Через телефон</b>\n"
        "1. Установи <b>Happ</b> на телефон\n"
        "2. Импортируй подписку\n"
        "3. Установи <b>v2rayTun</b> на ТВ из Google Play\n"
        "4. Открой v2rayTun на ТВ → «Импорт с телефона»\n"
        "5. Отсканируй QR-код\n\n"
        "<b>Способ 2: Happ на ТВ (вручную)</b>\n"
        "1. Скачай APK <b>Happ</b> с <a href='https://www.happ.su/main/'>happ.su</a>\n"
        "2. Установи через Send Files to TV или флешку\n"
        "3. Включи «Установка из неизвестных источников»\n"
        "4. Импортируй подписку\n\n"
        "✅ Готово!",
        reply_markup=back_to_connect_keyboard(),
        parse_mode="HTML"
    )
    await callback.answer()


@router.callback_query(F.data == "connect_linux")
async def connect_linux(callback: CallbackQuery):
    await callback.message.edit_text(
        "🐧 <b>Linux</b>\n\n"
        "<b>Рекомендуем: Happ — Proxy Utility</b>\n"
        "1. Скачай <b>Happ</b> для Linux с <a href='https://www.happ.su/main/'>happ.su</a>\n"
        "2. Выбери сборку:\n"
        "   • <code>.deb</code> — Ubuntu / Debian\n"
        "   • <code>.rpm</code> — Fedora / CentOS\n"
        "   • <code>.AppImage</code> — универсальный\n"
        "3. Установи и запусти\n"
        "4. Скопируй ссылку из «🔑 Моя подписка»\n"
        "5. В Happ: «+» → «Добавить подписку»\n"
        "6. Выбери сервер → «Подключиться»\n\n"
        "<i>Альтернатива:</i> Hysteria, Nekoray, Clash Verge\n\n"
        "✅ Готово!",
        reply_markup=back_to_connect_keyboard(),
        parse_mode="HTML",
        disable_web_page_preview=True
    )
    await callback.answer()
import asyncio
import logging
import sys
import os
from datetime import datetime

from flask import Flask, render_template, request, jsonify
import aiosqlite

sys.path.insert(0, '/root/skrepnet-bot')

from database import init_db, get_invite_link, use_invite_link, get_user
from xui_client import XUIClient
from config import DB_PATH, SUBSCRIPTION_DAYS, BOT_TOKEN, ADMIN_IDS, BOT_NAME
from handlers.utils import sanitize_email

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

app = Flask(__name__, template_folder='web/templates', static_folder='web/static')


async def notify_admin_new_web_user(friend_username: str, telegram_id: int, inviter_id: int, sub_url: str):
    """Отправить уведомление админам о новом пользователе через веб-выдачу."""
    from aiogram import Bot
    from aiogram.client.default import DefaultBotProperties

    bot = Bot(token=BOT_TOKEN, default=DefaultBotProperties(parse_mode="HTML"))
    try:
        text = (
            f"🆕 <b>Новый пользователь (веб-выдача)</b>\n\n"
            f"👤 @{friend_username or 'без username'}\n"
            f"🆔 <code>{telegram_id}</code>\n"
            f"👥 Пригласил: <code>{inviter_id}</code>\n\n"
            f"🔗 {sub_url}"
        )
        for admin_id in ADMIN_IDS:
            try:
                await bot.send_message(admin_id, text, disable_notification=True)
            except Exception as e:
                logger.error(f"Ошибка отправки админу {admin_id}: {e}")
    finally:
        await bot.session.close()


@app.route('/invite/<token>')
def invite_page(token):
    """Страница активации приглашения."""
    invite = asyncio.run(get_invite_link(token))

    if not invite:
        return render_template('error.html',
            message="Ссылка недействительна или уже использована"), 404

    inviter = asyncio.run(get_user(invite["created_by"]))
    inviter_name = "друг"
    if inviter:
        if inviter["username"]:
            inviter_name = f"@{inviter['username']}"
        elif inviter["first_name"]:
            inviter_name = inviter["first_name"]

    return render_template('invite.html',
        token=token,
        inviter_name=inviter_name,
        friend_username=invite["friend_username"] or "друг")


@app.route('/api/activate/<token>', methods=['POST'])
def activate(token):
    """Активация — создаёт клиента в 3x-ui."""
    data = request.json or {}

    if not data.get('accepted_terms'):
        return jsonify({'error': 'Необходимо принять условия'}), 400

    async def process():
        invite = await get_invite_link(token)
        if not invite:
            return {'error': 'Ссылка недействительна'}

        if invite["friend_username"]:
            name = invite["friend_username"]
        else:
            name = f"guest_{invite['created_by']}_{int(datetime.now().timestamp())}"

        telegram_id = invite["friend_user_id"] or 0
        xui_email = sanitize_email(name, telegram_id)

        try:
            async with XUIClient() as xui:
                auto_comment = f"web | inviter TG: {invite['created_by']}"
                if invite["friend_username"]:
                    auto_comment = f"@{invite['friend_username']} | " + auto_comment

                sub_id = await xui.add_client(
                    xui_email,
                    days=SUBSCRIPTION_DAYS,
                    comment=auto_comment
                )
                sub_url = xui.build_sub_url(sub_id)
        except Exception as e:
            logger.error(f"Ошибка создания клиента: {e}")
            return {'error': f'Ошибка создания подписки: {e}'}

        await use_invite_link(token, xui_email, sub_id)

        # Уведомляем админов
        try:
            await notify_admin_new_web_user(
                friend_username=invite["friend_username"],
                telegram_id=invite["friend_user_id"] or 0,
                inviter_id=invite["created_by"],
                sub_url=sub_url
            )
        except Exception as e:
            logger.error(f"Ошибка уведомления админа: {e}")

        # Генерируем QR-код
        import base64
        import io
        import qrcode

        qr = qrcode.QRCode(
            version=None,
            error_correction=qrcode.constants.ERROR_CORRECT_M,
            box_size=10,
            border=2,
        )
        qr.add_data(sub_url)
        qr.make(fit=True)
        img = qr.make_image(fill_color="black", back_color="white")

        buf = io.BytesIO()
        img.save(buf, format="PNG")
        buf.seek(0)
        qr_base64 = base64.b64encode(buf.read()).decode('utf-8')

        return {
            'sub_url': sub_url,
            'sub_id': sub_id,
            'email': xui_email,
            'qr_base64': qr_base64
        }

    result = asyncio.run(process())

    if 'error' in result:
        return jsonify(result), 400
    return jsonify(result)


if __name__ == '__main__':
    asyncio.run(init_db())

    SSL_CERT = '/root/cert/gb-skrepnet.duckdns.org/fullchain.pem'
    SSL_KEY = '/root/cert/gb-skrepnet.duckdns.org/privkey.pem'

    if os.path.exists(SSL_CERT) and os.path.exists(SSL_KEY):
        app.run(host='0.0.0.0', port=8443,
                ssl_context=(SSL_CERT, SSL_KEY))
    else:
        logger.warning("SSL сертификаты не найдены — запуск без HTTPS")
        app.run(host='0.0.0.0', port=8443)
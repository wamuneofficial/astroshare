"""
Утилиты для отправки email.

Если MAIL_USERNAME не задан в .env — письма не отправляются,
код/ссылка выводится в консоль (удобно при разработке).
"""
from flask import current_app
from flask_mail import Message
from ..extensions import mail


def _send(subject: str, recipients: list, body: str, html: str = None):
    """Внутренняя функция отправки. При ошибке логирует, не падает."""
    if not current_app.config.get('MAIL_ENABLED'):
        # Режим разработки: просто выводим в консоль
        print('\n' + '=' * 55)
        print(f'  📧 ПИСЬМО (MAIL_USERNAME не задан, отправка отключена)')
        print(f'  Кому: {", ".join(recipients)}')
        print(f'  Тема: {subject}')
        print('-' * 55)
        print(body)
        print('=' * 55 + '\n')
        return

    try:
        msg = Message(
            subject=subject,
            recipients=recipients,
            body=body,
            html=html,
        )
        mail.send(msg)
    except Exception as e:
        current_app.logger.error(f'Ошибка отправки письма на {recipients}: {e}')
        # Fallback: выводим в консоль чтобы не блокировать регистрацию
        print(f'[EMAIL FALLBACK] Кому: {recipients} | {body}')


def send_confirmation_email(to_email: str, username: str, code: str):
    """Отправляет 6-значный код подтверждения email."""
    subject = 'Подтверждение email — Astroshare'
    body = (
        f'Привет, {username}!\n\n'
        f'Твой код подтверждения для Astroshare:\n\n'
        f'  {code}\n\n'
        f'Введи его на странице подтверждения.\n'
        f'Код действителен до следующего входа на сайт.\n\n'
        f'Если ты не регистрировался — просто проигнорируй это письмо.\n\n'
        f'— Команда Astroshare'
    )
    html = f'''
    <div style="font-family:Inter,system-ui,sans-serif;max-width:480px;margin:0 auto;
                background:#000810;color:#e8f0ff;padding:40px 32px;border-radius:16px;
                border:1px solid rgba(0,200,160,0.2);">
        <h2 style="color:#00c8a0;margin-top:0;">🌌 Astroshare</h2>
        <p>Привет, <strong>{username}</strong>!</p>
        <p>Твой код подтверждения email:</p>
        <div style="text-align:center;margin:28px 0;">
            <span style="font-size:36px;font-weight:700;letter-spacing:10px;
                         color:#ffffff;background:rgba(0,200,160,0.1);
                         padding:16px 28px;border-radius:12px;
                         border:1px solid rgba(0,200,160,0.3);display:inline-block;">
                {code}
            </span>
        </div>
        <p style="color:#8899bb;font-size:13px;">
            Введи его на странице подтверждения.<br>
            Если ты не регистрировался — просто проигнорируй это письмо.
        </p>
        <hr style="border:none;border-top:1px solid rgba(255,255,255,0.08);margin:24px 0;">
        <p style="color:#556677;font-size:12px;margin:0;">— Команда Astroshare</p>
    </div>
    '''
    _send(subject, [to_email], body, html)


def send_reset_email(to_email: str, username: str, reset_url: str):
    """Отправляет ссылку для сброса пароля."""
    subject = 'Сброс пароля — Astroshare'
    body = (
        f'Привет, {username}!\n\n'
        f'Ты запросил сброс пароля на Astroshare.\n\n'
        f'Перейди по ссылке для установки нового пароля:\n'
        f'{reset_url}\n\n'
        f'Ссылка одноразовая. Если ты ничего не запрашивал — проигнорируй письмо.\n\n'
        f'— Команда Astroshare'
    )
    html = f'''
    <div style="font-family:Inter,system-ui,sans-serif;max-width:480px;margin:0 auto;
                background:#000810;color:#e8f0ff;padding:40px 32px;border-radius:16px;
                border:1px solid rgba(0,200,160,0.2);">
        <h2 style="color:#00c8a0;margin-top:0;">🌌 Astroshare</h2>
        <p>Привет, <strong>{username}</strong>!</p>
        <p>Ты запросил сброс пароля. Нажми кнопку ниже:</p>
        <div style="text-align:center;margin:28px 0;">
            <a href="{reset_url}"
               style="display:inline-block;padding:14px 32px;
                      background:rgba(0,200,160,0.12);
                      border:1px solid rgba(0,200,160,0.35);
                      color:#7fe8d0;text-decoration:none;
                      border-radius:10px;font-weight:600;font-size:15px;">
                Сбросить пароль
            </a>
        </div>
        <p style="color:#8899bb;font-size:13px;">
            Ссылка одноразовая. Если ты ничего не запрашивал — проигнорируй это письмо.
        </p>
        <hr style="border:none;border-top:1px solid rgba(255,255,255,0.08);margin:24px 0;">
        <p style="color:#556677;font-size:12px;margin:0;">— Команда Astroshare</p>
    </div>
    '''
    _send(subject, [to_email], body, html)

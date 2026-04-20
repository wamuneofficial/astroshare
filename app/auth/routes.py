import random
import secrets
from flask import render_template, redirect, url_for, flash, request, session
from flask_login import login_user, logout_user, login_required, current_user
from flask_babel import gettext as _
from . import auth
from .forms import (RegistrationForm, LoginForm, ForgotPasswordForm,
                    ResetPasswordForm, VerifyEmailForm)
from ..extensions import db
from ..models import User
from ..utils.email import send_confirmation_email, send_reset_email


@auth.route('/register', methods=['GET', 'POST'])
def register():
    """Регистрация нового пользователя."""
    if current_user.is_authenticated:
        return redirect(url_for('main.index'))

    form = RegistrationForm()
    if form.validate_on_submit():
        user = User(
            username=form.username.data,
            email=form.email.data.lower()
        )
        user.set_password(form.password.data)

        # Генерируем 6-значный числовой код подтверждения
        code = str(random.randint(100000, 999999))
        user.email_confirm_token = code

        # Первый пользователь — администратор, сразу подтверждён
        if User.query.count() == 0:
            user.is_admin = True
            user.email_confirmed = True
            user.email_confirm_token = ''

        db.session.add(user)
        db.session.commit()

        if not user.email_confirmed:
            session['pending_verify_email'] = user.email
            # Отправляем настоящее письмо (или выводим в консоль если MAIL не настроен)
            send_confirmation_email(user.email, user.username, code)
            flash(_('flash_confirm_sent'), 'info')
            return redirect(url_for('auth.verify_email'))

        flash(_('flash_register_success_admin'), 'success')
        return redirect(url_for('auth.login'))

    return render_template('auth/register.html', form=form)


@auth.route('/verify-email', methods=['GET', 'POST'])
def verify_email():
    """Страница ввода 6-значного кода подтверждения email."""
    email = session.get('pending_verify_email')

    if not email:
        return redirect(url_for('auth.login'))

    user = User.query.filter_by(email=email).first()
    if not user or user.email_confirmed:
        session.pop('pending_verify_email', None)
        return redirect(url_for('auth.login'))

    form = VerifyEmailForm()
    if form.validate_on_submit():
        entered_code = form.code.data.strip()

        if entered_code == user.email_confirm_token:
            user.email_confirmed = True
            user.email_confirm_token = ''
            db.session.commit()
            session.pop('pending_verify_email', None)
            flash(_('flash_confirm_success'), 'success')
            return redirect(url_for('auth.login'))
        else:
            flash(_('flash_code_invalid'), 'danger')

    return render_template('auth/verify_email.html', form=form, email=email)


@auth.route('/verify-email/resend', methods=['POST'])
def resend_code():
    """Повторная отправка кода подтверждения."""
    email = session.get('pending_verify_email')
    if not email:
        return redirect(url_for('auth.login'))

    user = User.query.filter_by(email=email).first()
    if user and not user.email_confirmed:
        code = str(random.randint(100000, 999999))
        user.email_confirm_token = code
        db.session.commit()
        send_confirmation_email(user.email, user.username, code)
        flash('Код отправлен повторно.', 'info')

    return redirect(url_for('auth.verify_email'))


@auth.route('/login', methods=['GET', 'POST'])
def login():
    """Вход в аккаунт."""
    if current_user.is_authenticated:
        return redirect(url_for('main.index'))

    form = LoginForm()
    if form.validate_on_submit():
        user = User.query.filter_by(email=form.email.data.lower()).first()

        if user is None or not user.check_password(form.password.data):
            flash(_('flash_login_invalid'), 'danger')
            return redirect(url_for('auth.login'))

        if user.is_banned:
            flash(_('flash_login_banned'), 'danger')
            return redirect(url_for('auth.login'))

        if not user.email_confirmed:
            session['pending_verify_email'] = user.email
            code = str(random.randint(100000, 999999))
            user.email_confirm_token = code
            db.session.commit()
            send_confirmation_email(user.email, user.username, code)
            flash(_('flash_login_not_confirmed'), 'warning')
            return redirect(url_for('auth.verify_email'))

        login_user(user, remember=form.remember_me.data)

        next_page = request.args.get('next')
        if not next_page or not next_page.startswith('/'):
            next_page = url_for('main.index')
        return redirect(next_page)

    return render_template('auth/login.html', form=form)


@auth.route('/logout')
@login_required
def logout():
    """Выход из аккаунта."""
    logout_user()
    flash(_('flash_logout'), 'info')
    return redirect(url_for('main.index'))


@auth.route('/forgot-password', methods=['GET', 'POST'])
def forgot_password():
    """Запрос сброса пароля."""
    if current_user.is_authenticated:
        return redirect(url_for('main.index'))

    form = ForgotPasswordForm()
    if form.validate_on_submit():
        user = User.query.filter_by(email=form.email.data.lower()).first()

        if user:
            user.password_reset_token = secrets.token_urlsafe(32)
            db.session.commit()
            reset_url = url_for(
                'auth.reset_password',
                token=user.password_reset_token,
                _external=True
            )
            send_reset_email(user.email, user.username, reset_url)

        flash(_('flash_forgot_sent'), 'info')
        return redirect(url_for('auth.login'))

    return render_template('auth/forgot_password.html', form=form)


@auth.route('/reset-password/<token>', methods=['GET', 'POST'])
def reset_password(token):
    """Установка нового пароля по токену."""
    if current_user.is_authenticated:
        return redirect(url_for('main.index'))

    user = User.query.filter_by(password_reset_token=token).first()
    if user is None:
        flash(_('flash_reset_invalid'), 'danger')
        return redirect(url_for('auth.forgot_password'))

    form = ResetPasswordForm()
    if form.validate_on_submit():
        user.set_password(form.password.data)
        user.password_reset_token = ''
        db.session.commit()
        flash(_('flash_reset_success'), 'success')
        return redirect(url_for('auth.login'))

    return render_template('auth/reset_password.html', form=form)

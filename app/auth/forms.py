from flask_wtf import FlaskForm
from wtforms import StringField, PasswordField, BooleanField, SubmitField
from wtforms.validators import (
    DataRequired, Email, Length, EqualTo, ValidationError, Regexp
)


class RegistrationForm(FlaskForm):
    """Форма регистрации нового пользователя."""

    username = StringField('username', validators=[
        DataRequired(),
        Length(min=3, max=64),
        # Только латинские буквы и цифры (без пробелов и спецсимволов)
        Regexp('^[A-Za-z0-9]+$', message='only_latin')
    ])
    email = StringField('email', validators=[
        DataRequired(),
        Email()
    ])
    password = PasswordField('password', validators=[
        DataRequired(),
        Length(min=8, message='password_too_short')
    ])
    confirm_password = PasswordField('confirm_password', validators=[
        DataRequired(),
        EqualTo('password', message='passwords_mismatch')
    ])
    submit = SubmitField('register')

    def validate_username(self, field):
        """Проверяем, что такой username ещё не занят."""
        from app.models import User
        if User.query.filter_by(username=field.data).first():
            raise ValidationError('username_taken')

    def validate_email(self, field):
        """Проверяем, что такой email ещё не зарегистрирован."""
        from app.models import User
        if User.query.filter_by(email=field.data.lower()).first():
            raise ValidationError('email_taken')


class LoginForm(FlaskForm):
    """Форма входа."""

    email = StringField('email', validators=[DataRequired(), Email()])
    password = PasswordField('password', validators=[DataRequired()])
    # "Запомнить меня" — сессия будет жить дольше
    remember_me = BooleanField('remember_me')
    submit = SubmitField('login')


class ForgotPasswordForm(FlaskForm):
    """Форма запроса сброса пароля — пользователь вводит только email."""

    email = StringField('email', validators=[DataRequired(), Email()])
    submit = SubmitField('send_reset_link')


class ResetPasswordForm(FlaskForm):
    """Форма установки нового пароля (после перехода по ссылке из email)."""

    password = PasswordField('password', validators=[
        DataRequired(),
        Length(min=8, message='password_too_short')
    ])
    confirm_password = PasswordField('confirm_password', validators=[
        DataRequired(),
        EqualTo('password', message='passwords_mismatch')
    ])
    submit = SubmitField('set_new_password')


class VerifyEmailForm(FlaskForm):
    """Форма ввода 6-значного кода подтверждения email."""

    code = StringField('code', validators=[
        DataRequired(),
        Length(min=6, max=6, message='code_length')
    ])
    submit = SubmitField('verify')

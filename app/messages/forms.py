from flask_wtf import FlaskForm
from wtforms import StringField, TextAreaField, SubmitField
from wtforms.validators import DataRequired, Length


class ComposeForm(FlaskForm):
    """Форма написания нового личного сообщения."""
    recipient = StringField(
        'Получатель',
        validators=[DataRequired(), Length(max=64)]
    )
    subject = StringField(
        'Тема',
        validators=[DataRequired(), Length(max=256)]
    )
    body = TextAreaField(
        'Сообщение',
        validators=[DataRequired(), Length(max=5000)]
    )
    submit = SubmitField('Отправить')


class ReplyForm(FlaskForm):
    """Форма быстрого ответа на сообщение."""
    body = TextAreaField(
        'Ответ',
        validators=[DataRequired(), Length(max=5000)]
    )
    submit = SubmitField('Ответить')

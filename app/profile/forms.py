from flask_wtf import FlaskForm
from flask_wtf.file import FileField, FileAllowed
from wtforms import StringField, TextAreaField, SubmitField
from wtforms.validators import Length, Optional, URL, Regexp


class EditProfileForm(FlaskForm):
    """Форма редактирования профиля пользователя."""

    bio = TextAreaField('bio', validators=[
        Optional(),
        Length(max=500)
    ])
    telescopes = StringField('telescopes', validators=[
        Optional(),
        Length(max=256)
    ])
    location = StringField('location', validators=[
        Optional(),
        Length(max=128)
    ])
    website = StringField('website', validators=[
        Optional(),
        Length(max=256)
    ])
    twitter = StringField('twitter', validators=[
        Optional(),
        Length(max=128),
        # Только латиница, цифры и подчёркивание — стандартный формат Twitter
        Regexp('^[A-Za-z0-9_]*$', message='invalid_twitter')
    ])
    instagram = StringField('instagram', validators=[
        Optional(),
        Length(max=128),
        Regexp('^[A-Za-z0-9_.]*$', message='invalid_instagram')
    ])

    # Аватар — разрешаем только JPG и PNG
    avatar = FileField('avatar', validators=[
        FileAllowed(['jpg', 'jpeg', 'png'], 'images_only')
    ])

    submit = SubmitField('save')

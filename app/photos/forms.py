from flask_wtf import FlaskForm
from flask_wtf.file import FileField, FileRequired, FileAllowed
from wtforms import (StringField, TextAreaField, DateField, BooleanField,
                     SelectField, IntegerField, FloatField, SubmitField)
from wtforms.validators import DataRequired, Optional, Length, NumberRange


# Типы объектов для выпадающего списка
OBJECT_TYPE_CHOICES = [
    ('',            '— Выбери тип —'),
    ('galaxy',      'Галактика'),
    ('nebula',      'Туманность'),
    ('planet',      'Планета'),
    ('star_cluster','Звёздное скопление'),
    ('solar',       'Объект Солнечной системы'),
    ('double_star', 'Двойная звезда'),
    ('other',       'Другое'),
]

# Шкала Бортля: 1 = идеальное тёмное небо, 9 = центр города
BORTLE_CHOICES = [('', '—')] + [(str(i), f'{i}') for i in range(1, 10)]


class PhotoUploadForm(FlaskForm):
    """Форма загрузки снимка со всеми метаданными."""

    # --- Файл ---
    photo = FileField('photo', validators=[
        FileRequired(),
        FileAllowed(['jpg', 'jpeg', 'png', 'tiff', 'tif'], 'format_not_allowed')
    ])

    # --- Основное ---
    title = StringField('title', validators=[
        DataRequired(), Length(max=256)
    ])
    description = TextAreaField('description', validators=[
        Optional(), Length(max=2000)
    ])
    observation_date = DateField('observation_date', validators=[DataRequired()])
    is_public = BooleanField('is_public', default=True)

    # --- Астрономические данные ---
    object_name = StringField('object_name', validators=[Optional(), Length(max=128)])
    object_type = SelectField('object_type', choices=OBJECT_TYPE_CHOICES,
                              validators=[Optional()])
    constellation = StringField('constellation', validators=[Optional(), Length(max=64)])
    # Формат: HH:MM:SS
    ra  = StringField('ra',  validators=[Optional(), Length(max=32)])
    # Формат: ±DD:MM:SS
    dec = StringField('dec', validators=[Optional(), Length(max=32)])

    # --- Технические данные ---
    telescope    = StringField('telescope',    validators=[Optional(), Length(max=128)])
    focal_length = IntegerField('focal_length', validators=[Optional(),
                                                            NumberRange(min=1)])
    camera       = StringField('camera',       validators=[Optional(), Length(max=128)])
    # Время экспозиции одного кадра в секундах
    exposure_time = FloatField('exposure_time', validators=[Optional(),
                                                            NumberRange(min=0)])
    iso_gain    = StringField('iso_gain',    validators=[Optional(), Length(max=32)])
    frame_count = IntegerField('frame_count', validators=[Optional(),
                                                          NumberRange(min=1)])

    # --- Условия съёмки ---
    location_name = StringField('location_name', validators=[Optional(), Length(max=128)])
    bortle_scale  = SelectField('bortle_scale', choices=BORTLE_CHOICES,
                                validators=[Optional()])

    # --- Теги ---
    tags = StringField('tags', validators=[Optional(), Length(max=512)])

    submit = SubmitField('upload')

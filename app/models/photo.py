from datetime import datetime
from ..extensions import db


class Photo(db.Model):
    """Модель астрофотографии со всеми метаданными."""
    __tablename__ = 'photos'

    id = db.Column(db.Integer, primary_key=True)
    # Внешний ключ — ссылка на автора снимка
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)

    # --- Файл ---
    # Сохраняем UUID-имя (случайное), не оригинальное название файла от пользователя.
    # Это нужно для безопасности: пользователь не может угадать путь чужого файла.
    filename = db.Column(db.String(256), nullable=False)
    original_filename = db.Column(db.String(256), default='')   # оригинальное имя для отображения
    thumbnail_filename = db.Column(db.String(256), default='')  # уменьшенная копия 400x400
    file_format = db.Column(db.String(16), default='')          # JPG, PNG, TIFF, FITS

    # --- Основные поля ---
    title = db.Column(db.String(256), nullable=False)
    description = db.Column(db.Text, default='')
    observation_date = db.Column(db.Date, nullable=False)

    # --- Астрономические данные ---
    object_name = db.Column(db.String(128), default='')    # M31, NGC 7000, Сатурн...
    object_type = db.Column(db.String(64), default='')     # галактика, туманность, планета...
    constellation = db.Column(db.String(64), default='')   # созвездие
    ra = db.Column(db.String(32), default='')              # прямое восхождение: HH:MM:SS
    dec = db.Column(db.String(32), default='')             # склонение: ±DD:MM:SS

    # --- Технические данные ---
    telescope = db.Column(db.String(128), default='')
    focal_length = db.Column(db.Integer, nullable=True)    # фокусное расстояние в мм
    camera = db.Column(db.String(128), default='')
    exposure_time = db.Column(db.Float, nullable=True)     # время экспозиции в секундах
    iso_gain = db.Column(db.String(32), default='')        # ISO (для DSLR) или gain (для CCD)
    frame_count = db.Column(db.Integer, nullable=True)     # количество кадров при стэкинге

    # --- Условия съёмки ---
    location_name = db.Column(db.String(128), default='')
    # Шкала Бортля: 1 — идеально тёмное небо вдали от цивилизации, 9 — центр мегаполиса
    bortle_scale = db.Column(db.Integer, nullable=True)

    # --- Настройки публикации ---
    tags = db.Column(db.String(512), default='')           # теги через запятую
    is_public = db.Column(db.Boolean, default=True, nullable=False)
    is_hidden = db.Column(db.Boolean, default=False, nullable=False)  # скрыт модератором

    # --- Plate solving ---
    # Автоматическое определение точных координат по звёздному полю на снимке
    plate_solved = db.Column(db.Boolean, default=False)
    # Результаты plate solving хранятся как строка в формате JSON
    plate_solve_data = db.Column(db.Text, default='')

    # --- Статистика ---
    likes_count = db.Column(db.Integer, default=0)

    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    # --- Связи ---
    comments = db.relationship(
        'Comment',
        backref='photo',
        lazy='dynamic',
        cascade='all, delete-orphan'
    )
    likes = db.relationship(
        'Like',
        backref='photo',
        lazy='dynamic',
        cascade='all, delete-orphan'
    )

    def __repr__(self):
        return f'<Photo {self.title}>'


class Like(db.Model):
    """
    Лайк — может быть поставлен как снимку, так и текстовому посту.
    Ровно одно из полей photo_id / post_id должно быть заполнено.
    """
    __tablename__ = 'likes'

    id = db.Column(db.Integer, primary_key=True)
    user_id  = db.Column(db.Integer, db.ForeignKey('users.id'),  nullable=False)
    photo_id = db.Column(db.Integer, db.ForeignKey('photos.id'), nullable=True)
    post_id  = db.Column(db.Integer, db.ForeignKey('posts.id'),  nullable=True)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)

    __table_args__ = (
        db.UniqueConstraint('user_id', 'photo_id', name='unique_user_photo_like'),
        db.UniqueConstraint('user_id', 'post_id',  name='unique_user_post_like'),
    )

    def __repr__(self):
        return f'<Like user={self.user_id} photo={self.photo_id} post={self.post_id}>'

from datetime import datetime
from ..extensions import db


class Notification(db.Model):
    """
    Уведомление для пользователя.
    Создаётся когда кто-то лайкнул или прокомментировал его снимок.
    Хранится в базе данных — никаких email не отправляется.
    """
    __tablename__ = 'notifications'

    id = db.Column(db.Integer, primary_key=True)

    # Кому предназначено уведомление
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)

    # Тип уведомления: 'like' или 'comment'
    type = db.Column(db.String(32), nullable=False)

    # Текст уведомления, например: "stargazer42 оставил комментарий к вашему снимку M31"
    message = db.Column(db.String(256), nullable=False)

    # Ссылка на снимок, к которому относится уведомление
    photo_id = db.Column(db.Integer, db.ForeignKey('photos.id'), nullable=True)

    # Прочитано ли уведомление пользователем
    is_read = db.Column(db.Boolean, default=False)

    created_at = db.Column(db.DateTime, default=datetime.utcnow)

    def __repr__(self):
        return f'<Notification {self.type} for user={self.user_id}>'

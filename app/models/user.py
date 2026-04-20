from datetime import datetime
from flask_login import UserMixin
from werkzeug.security import generate_password_hash, check_password_hash
from ..extensions import db, login_manager


class User(UserMixin, db.Model):
    """
    Модель пользователя.

    UserMixin — это вспомогательный класс от Flask-Login.
    Он добавляет свойства is_authenticated, is_active и метод get_id(),
    которые Flask-Login требует от любой модели пользователя.
    """
    __tablename__ = 'users'

    id = db.Column(db.Integer, primary_key=True)

    # index=True ускоряет поиск по этим полям (поиск пользователя по email/username)
    username = db.Column(db.String(64), unique=True, nullable=False, index=True)
    email = db.Column(db.String(120), unique=True, nullable=False, index=True)

    # Храним только хеш пароля. Настоящий пароль нигде не сохраняется.
    password_hash = db.Column(db.String(256), nullable=False)

    # --- Поля профиля ---
    bio = db.Column(db.Text, default='')
    avatar_filename = db.Column(db.String(256), default='')
    # Список телескопов пользователя, перечисленных через запятую
    telescopes = db.Column(db.Text, default='')
    location = db.Column(db.String(128), default='')
    website = db.Column(db.String(256), default='')
    twitter = db.Column(db.String(128), default='')
    instagram = db.Column(db.String(128), default='')

    # --- Системные поля ---
    # Первый зарегистрированный пользователь станет администратором
    is_admin = db.Column(db.Boolean, default=False, nullable=False)
    is_banned = db.Column(db.Boolean, default=False, nullable=False)
    email_confirmed = db.Column(db.Boolean, default=False, nullable=False)

    # Токены для подтверждения email и сброса пароля.
    # Генерируются случайно, отправляются пользователю, после использования сбрасываются.
    email_confirm_token = db.Column(db.String(256), default='')
    password_reset_token = db.Column(db.String(256), default='')

    created_at = db.Column(db.DateTime, default=datetime.utcnow)

    # --- Связи с другими таблицами ---
    # backref='author' означает: у объекта Photo появится атрибут photo.author,
    # который вернёт пользователя-автора.
    # cascade='all, delete-orphan' — при удалении пользователя автоматически
    # удаляются все его снимки, комментарии и уведомления.
    photos = db.relationship(
        'Photo',
        backref='author',
        lazy='dynamic',
        cascade='all, delete-orphan'
    )
    comments = db.relationship(
        'Comment',
        backref='author',
        lazy='dynamic',
        cascade='all, delete-orphan'
    )
    notifications = db.relationship(
        'Notification',
        backref='recipient',
        lazy='dynamic',
        cascade='all, delete-orphan'
    )
    posts = db.relationship(
        'Post',
        backref='author',
        lazy='dynamic',
        cascade='all, delete-orphan'
    )

    # ---- Методы системы друзей ----

    def friendship_status(self, other):
        """
        Статус отношений с пользователем other:
          'none'             — не связаны
          'friends'          — дружба принята
          'pending_sent'     — я отправил запрос, жду
          'pending_received' — other отправил мне запрос
        """
        from .friendship import Friendship
        from sqlalchemy import or_, and_
        f = Friendship.query.filter(
            or_(
                and_(Friendship.requester_id == self.id,
                     Friendship.addressee_id == other.id),
                and_(Friendship.requester_id == other.id,
                     Friendship.addressee_id == self.id),
            )
        ).first()
        if f is None:
            return 'none'
        if f.status == 'accepted':
            return 'friends'
        return 'pending_sent' if f.requester_id == self.id else 'pending_received'

    def get_friends(self):
        """Список принятых друзей (объекты User)."""
        from .friendship import Friendship
        from sqlalchemy import or_, and_
        rows = Friendship.query.filter(
            or_(
                and_(Friendship.requester_id == self.id,
                     Friendship.status == 'accepted'),
                and_(Friendship.addressee_id == self.id,
                     Friendship.status == 'accepted'),
            )
        ).all()
        result = []
        for row in rows:
            result.append(row.addressee if row.requester_id == self.id else row.requester)
        return result

    def get_friends_count(self):
        from .friendship import Friendship
        from sqlalchemy import or_, and_
        return Friendship.query.filter(
            or_(
                and_(Friendship.requester_id == self.id,
                     Friendship.status == 'accepted'),
                and_(Friendship.addressee_id == self.id,
                     Friendship.status == 'accepted'),
            )
        ).count()

    def get_pending_in(self):
        """Входящие неотвеченные запросы на дружбу."""
        from .friendship import Friendship
        return Friendship.query.filter_by(
            addressee_id=self.id, status='pending'
        ).all()

    def get_pending_in_count(self):
        from .friendship import Friendship
        return Friendship.query.filter_by(
            addressee_id=self.id, status='pending'
        ).count()

    # ---- Конец методов дружбы ----

    def set_password(self, password):
        """Хешируем пароль перед сохранением. Оригинальный пароль нигде не хранится."""
        self.password_hash = generate_password_hash(password)

    def check_password(self, password):
        """Сравниваем введённый пароль с сохранённым хешем."""
        return check_password_hash(self.password_hash, password)

    def __repr__(self):
        # Этот метод определяет, как объект выглядит при печати в консоли/логах
        return f'<User {self.username}>'


@login_manager.user_loader
def load_user(user_id):
    """
    Flask-Login вызывает эту функцию при каждом запросе для загрузки
    текущего пользователя из базы данных по id, сохранённому в сессии.
    """
    return User.query.get(int(user_id))

from datetime import datetime
from ..extensions import db


class News(db.Model):
    """Новость из внешнего источника (NASA APOD, Spaceflight News и т.д.)"""
    __tablename__ = 'news'

    id = db.Column(db.Integer, primary_key=True)

    title = db.Column(db.String(512), nullable=False)
    description = db.Column(db.Text, default='')

    # Источник: 'nasa_apod', 'spaceflight', 'nasa_neo'
    # index=True ускоряет фильтрацию новостей по источнику
    source = db.Column(db.String(64), default='', index=True)

    # Ссылка на оригинальную статью (будет открываться в новой вкладке)
    url = db.Column(db.String(1024), default='')

    # Ссылка на изображение к новости
    image_url = db.Column(db.String(1024), default='')

    # Дата публикации в источнике (не дата загрузки в нашу БД)
    published_at = db.Column(db.DateTime, nullable=False, index=True)

    # Когда мы загрузили эту новость в нашу БД
    fetched_at = db.Column(db.DateTime, default=datetime.utcnow)

    def __repr__(self):
        return f'<News {self.title[:50]}>'

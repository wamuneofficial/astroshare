import os
from dotenv import load_dotenv

# Загружаем переменные из файла .env в переменные окружения
load_dotenv()


class Config:
    """Базовые настройки, общие для всех окружений."""

    # Секретный ключ для подписи сессий и CSRF-токенов.
    # В разработке можно оставить заглушку, в продакшене ОБЯЗАТЕЛЬНО менять.
    SECRET_KEY = os.environ.get('SECRET_KEY', 'dev-secret-key-change-in-production')

    # Отключаем лишние уведомления SQLAlchemy об изменениях объектов
    SQLALCHEMY_TRACK_MODIFICATIONS = False

    # Flask-Babel: язык по умолчанию и список поддерживаемых языков
    BABEL_DEFAULT_LOCALE = 'ru'
    BABEL_SUPPORTED_LOCALES = ['ru', 'en']

    # Максимальный размер загружаемого файла: 20 МБ
    MAX_CONTENT_LENGTH = 20 * 1024 * 1024

    # Папка для хранения загруженных файлов пользователей.
    # os.path.abspath(__file__) — полный путь к этому файлу (config.py)
    # два раза dirname — поднимаемся на два уровня вверх (app/ -> корень проекта)
    UPLOAD_FOLDER = os.path.join(
        os.path.dirname(os.path.dirname(os.path.abspath(__file__))),
        'uploads'
    )

    # NASA API ключ для загрузки новостей
    NASA_API_KEY = os.environ.get('NASA_API_KEY', 'DEMO_KEY')


class DevelopmentConfig(Config):
    """Настройки для локальной разработки."""
    DEBUG = True
    SQLALCHEMY_DATABASE_URI = os.environ.get(
        'DATABASE_URL',
        'sqlite:///astroshare_dev.db'
    )


class ProductionConfig(Config):
    """Настройки для продакшена (Render.com / Railway.app)."""
    DEBUG = False
    # Railway/Render возвращают URL начинающийся с postgres://, SQLAlchemy требует postgresql://
    _db_url = os.environ.get('DATABASE_URL', '')
    SQLALCHEMY_DATABASE_URI = (
        _db_url.replace('postgres://', 'postgresql://', 1)
        if _db_url else None
    )


# Словарь для выбора нужной конфигурации по имени строки
config = {
    'development': DevelopmentConfig,
    'production': ProductionConfig,
    'default': DevelopmentConfig,
}

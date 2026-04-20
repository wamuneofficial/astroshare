import os
from flask import Flask, session, request
from .config import config
from .extensions import db, migrate, login_manager, csrf, babel


def get_locale():
    """
    Определяем язык интерфейса для текущего запроса.
    Flask-Babel вызывает эту функцию перед каждым рендерингом шаблона.
    """
    # Сначала проверяем, выбрал ли пользователь язык вручную (сохранён в сессии)
    lang = session.get('lang')
    if lang in ['ru', 'en']:
        return lang
    # Иначе — смотрим на настройки языка в браузере пользователя
    return request.accept_languages.best_match(['ru', 'en']) or 'ru'


def create_app(config_name=None):
    """
    Фабрика приложения — создаёт и настраивает экземпляр Flask.

    Принимает: config_name — 'development', 'production' или None (тогда читает
    переменную окружения FLASK_ENV, по умолчанию 'development').
    """
    if config_name is None:
        config_name = os.environ.get('FLASK_ENV', 'default')

    app = Flask(__name__)
    app.config.from_object(config[config_name])

    # Подключаем все расширения к этому конкретному экземпляру приложения
    db.init_app(app)
    migrate.init_app(app, db)
    login_manager.init_app(app)
    csrf.init_app(app)
    babel.init_app(app, locale_selector=get_locale)

    # Если пользователь попытается зайти на закрытую страницу без авторизации,
    # Flask-Login перенаправит его сюда. 'auth.login' — это имя маршрута,
    # который создадим в следующем этапе.
    login_manager.login_view = 'auth.login'
    login_manager.login_message_category = 'warning'

    # Создаём папку uploads/ если её нет (нужна для хранения снимков)
    os.makedirs(app.config['UPLOAD_FOLDER'], exist_ok=True)

    # Импортируем модели ВНУТРИ фабрики — это критически важно!
    # Flask-Migrate должен "видеть" все классы моделей, чтобы генерировать миграции.
    # Импорт здесь гарантирует, что модели зарегистрированы в нужный момент.
    from .models import User, Photo, Comment, News, Like, Notification, Post, Message, Friendship, Material, GroupChat, GroupChatMember, GroupChatMessage  # noqa: F401

    # Регистрируем blueprints
    from .main import main as main_blueprint
    app.register_blueprint(main_blueprint)

    from .auth import auth as auth_blueprint
    app.register_blueprint(auth_blueprint)

    from .profile import profile as profile_blueprint
    app.register_blueprint(profile_blueprint)

    from .photos import photos as photos_blueprint
    app.register_blueprint(photos_blueprint)

    from .posts import posts as posts_blueprint
    app.register_blueprint(posts_blueprint)

    from .gallery import gallery as gallery_blueprint
    app.register_blueprint(gallery_blueprint)

    from .news import news as news_blueprint
    app.register_blueprint(news_blueprint)

    from .identify import identify as identify_blueprint
    app.register_blueprint(identify_blueprint)

    from .catalog import catalog as catalog_blueprint
    app.register_blueprint(catalog_blueprint)

    from .messages import messages as messages_blueprint
    app.register_blueprint(messages_blueprint)

    from .materials import materials as materials_blueprint
    app.register_blueprint(materials_blueprint)

    from .groupchat import groupchat as groupchat_blueprint
    app.register_blueprint(groupchat_blueprint)

    # Делаем функцию get_locale доступной во всех Jinja2-шаблонах.
    # Без этого {{ get_locale() }} в base.html выдаст ошибку "UndefinedError".
    @app.context_processor
    def inject_template_globals():
        from flask_login import current_user
        unread_count = 0
        friend_requests_count = 0
        if current_user.is_authenticated:
            from .models.message import Message
            from .models.friendship import Friendship
            unread_count = Message.query.filter_by(
                recipient_id=current_user.id, is_read=False
            ).count()
            friend_requests_count = Friendship.query.filter_by(
                addressee_id=current_user.id, status='pending'
            ).count()
        return {
            'get_locale': get_locale,
            'unread_count': unread_count,
            'friend_requests_count': friend_requests_count,
        }

    return app

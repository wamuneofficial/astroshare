# Здесь создаём экземпляры расширений БЕЗ привязки к конкретному приложению Flask.
#
# Зачем так делать?
# Flask поддерживает паттерн "фабрика приложения": функция create_app() создаёт
# приложение и передаёт его расширениям через .init_app(app).
# Это позволяет создавать несколько экземпляров приложения — например, один
# для тестов с тестовой БД, другой для продакшена с реальной БД.

from flask_sqlalchemy import SQLAlchemy
from flask_migrate import Migrate
from flask_login import LoginManager
from flask_wtf.csrf import CSRFProtect
from flask_babel import Babel
from flask_mail import Mail

# ORM для работы с базой данных через Python-объекты вместо SQL-запросов
db = SQLAlchemy()

# Управление миграциями — отслеживает изменения в моделях и обновляет структуру БД
migrate = Migrate()

# Управление сессиями пользователей: вход, выход, проверка авторизации
login_manager = LoginManager()

# Защита форм от CSRF-атак (подделка межсайтовых запросов)
csrf = CSRFProtect()

# Поддержка нескольких языков интерфейса
babel = Babel()

# Отправка email-сообщений (подтверждение, сброс пароля)
mail = Mail()

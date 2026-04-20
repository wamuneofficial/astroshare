from flask import Blueprint

# Blueprint — это мини-приложение внутри Flask.
# Позволяет разбить маршруты на логические группы:
# main (главная), auth (авторизация), gallery (галерея) и т.д.
# 'main' — имя blueprint, используется в url_for('main.index')
main = Blueprint('main', __name__)

# Импортируем маршруты ПОСЛЕ создания объекта Blueprint.
# Если сделать наоборот — routes.py попытается импортировать 'main',
# которого ещё не существует (circular import).
from . import routes  # noqa: E402, F401

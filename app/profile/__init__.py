from flask import Blueprint

# Без url_prefix — маршруты прописаны полностью в routes.py
profile = Blueprint('profile', __name__)

from . import routes  # noqa: E402, F401

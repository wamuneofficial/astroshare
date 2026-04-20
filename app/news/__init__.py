from flask import Blueprint

news = Blueprint('news', __name__)

from . import routes  # noqa: F401, E402

from flask import Blueprint

posts = Blueprint('posts', __name__)

from . import routes  # noqa: E402, F401

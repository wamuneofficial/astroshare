from flask import Blueprint

messages = Blueprint('messages', __name__)

from . import routes  # noqa: F401, E402

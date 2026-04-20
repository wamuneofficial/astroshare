from flask import Blueprint

groupchat = Blueprint('groupchat', __name__)

from . import routes  # noqa: E402, F401

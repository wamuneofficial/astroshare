from flask import Blueprint

gallery = Blueprint('gallery', __name__)

from . import routes  # noqa: E402, F401

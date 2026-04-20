from flask import Blueprint

photos = Blueprint('photos', __name__)

from . import routes  # noqa: E402, F401

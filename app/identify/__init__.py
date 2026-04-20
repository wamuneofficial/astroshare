from flask import Blueprint

identify = Blueprint('identify', __name__)

from . import routes  # noqa: F401, E402

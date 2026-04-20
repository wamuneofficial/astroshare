from flask import Blueprint

catalog = Blueprint('catalog', __name__)

from . import routes  # noqa: F401, E402

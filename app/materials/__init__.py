from flask import Blueprint

materials = Blueprint('materials', __name__)

from . import routes  # noqa: E402, F401

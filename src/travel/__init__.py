from flask import Blueprint

travel = Blueprint("travel", __name__)

from . import routes

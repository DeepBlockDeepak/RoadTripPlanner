from flask import Blueprint

utility = Blueprint("utility", __name__)

from . import routes

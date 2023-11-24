from flask import Blueprint

user_profile = Blueprint("user_profile", __name__)

from . import routes

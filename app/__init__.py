from flask import Flask
from flask_login import LoginManager

from config import Config
from database import db  # import the db instance


def create_app():
	# init Flask app
	app = Flask(__name__)
	app.config.from_object(Config)  # load custom config

	# init SQLAlchemy with the app
	db.init_app(app)

	# init Flask-Login manager
	login_manager = LoginManager()
	login_manager.init_app(app)
	login_manager.login_view = "auth.login"  # specify route for unauthenticated users

	# load user function for Flask-Login
	from app.models import User

	@login_manager.user_loader
	def load_user(user_id):
		return User.query.get(int(user_id))

	# register blueprints, routes, and error handlers
	from .auth import auth as auth_bp
	from .dashboard import dashboard as dashboard_bp
	from .places import places as places_bp
	from .travel import travel as travel_bp
	from .user_profile import user_profile as user_profile_bp
	from .utility import utility as utility_bp

	app.register_blueprint(auth_bp)
	app.register_blueprint(dashboard_bp)
	app.register_blueprint(places_bp)
	app.register_blueprint(travel_bp)
	app.register_blueprint(user_profile_bp)
	app.register_blueprint(utility_bp)

	return app

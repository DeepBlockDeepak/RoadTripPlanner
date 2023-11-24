from flask import Flask
from flask_login import LoginManager
from config import Config
from database import db  # import the db instance


def create_app():
	# Initialize Flask app
	app = Flask(__name__)
	app.config.from_object(Config)  # Load configuration from config.py

	# Initialize SQLAlchemy with the app
	db.init_app(app)

	# Initialize Flask-Login manager
	login_manager = LoginManager()
	login_manager.init_app(app)
	login_manager.login_view = (
		"auth.login"  # Specify the route for unauthenticated users
	)

	# Load user function for Flask-Login
	from src.models import User

	@login_manager.user_loader
	def load_user(user_id):
		return User.query.get(int(user_id))

	# Register blueprints, routes, and error handlers
	from .auth import auth as auth_bp
	from .dashboard import dashboard as dashboard_bp
	from .places import places as places_bp
	from .travel import travel as travel_bp
	from .user_profile import user_profile as user_profile_db
	from .utility import utility as utility_db

	app.register_blueprint(auth_bp)
	app.register_blueprint(dashboard_bp)
	app.register_blueprint(places_bp)
	app.register_blueprint(travel_bp)
	app.register_blueprint(user_profile_db)
	app.register_blueprint(utility_db)

	return app

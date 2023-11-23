from flask import Flask
from flask_login import LoginManager
from src.config import Config
from database import db  # import the db instance
from src.views import welcome_page, not_found


def create_app():
	# Initialize Flask app
	app = Flask(__name__)
	app.config.from_object(Config)  # Load configuration from config.py

	# Initialize SQLAlchemy with the app
	db.init_app(app)

	# Initialize Flask-Login manager
	login_manager = LoginManager()
	login_manager.init_app(app)
	login_manager.login_view = "login"  # Specify the route for unauthenticated users

	# Load user function for Flask-Login
	from src.models import User

	@login_manager.user_loader
	def load_user(user_id):
		return User.query.get(int(user_id))

	# Register blueprints, routes, and error handlers
	app.add_url_rule("/", "welcome_page", welcome_page)
	app.add_url_rule("/index", "welcome_page", welcome_page)
	app.add_url_rule("/home", "welcome_page", welcome_page)

	# Register error handlers
	app.register_error_handler(404, not_found)

	return app

from flask import Flask, render_template
from flask_login import LoginManager
from flask_sqlalchemy import SQLAlchemy
from src.config import Config

# Initialize Flask app
app = Flask(__name__)
app.config.from_object(Config)  # Load configuration from config.py

# Initialize Flask-Login manager
login_manager = LoginManager()
login_manager.init_app(app)
login_manager.login_view = "login"  # Specify the route for unauthenticated users

# Initialize SQLAlchemy with the Flask app
db = SQLAlchemy(app)


# Define route for the homepage
@app.route("/")
@app.route("/index")
@app.route("/home")
def welcome_page():
	# Render the welcome page template
	return render_template("welcome_page.html")


# Define custom error handler for 404 errors
@app.errorhandler(404)
def not_found(_):  # Unused error argument can be indicated with an underscore
	# Render the 404 error page template
	return render_template("404.html")


# Import routes from the routes module
# Note: This import is placed here to avoid circular import issues
from src.routes import *

# Conditional to run the app in standalone mode
if __name__ == "__main__":
	app.run()  # Start the Flask application

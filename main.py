import os

from flask import Flask, render_template
from flask_login import LoginManager
from flask_sqlalchemy import SQLAlchemy

# attempting to create/read/write the .db in the top project directory, whether on replit or local
cwd = os.getcwd()


# use the following as a second paramter to dictate where you want the database to exist. Default is /instance
# ,instance_path='/home/runner/computroniumflaskapp'
app = Flask(__name__, instance_path=cwd)

# create login_manager and initialize login_manager here:
login_manager = LoginManager()
login_manager.init_app(app)
# testing to see whether unlogged in viewers are auto-sent to the register page
# @BUG -> This auto-routing to /register doesn't work
login_manager.login_view = "register"

# set the SQLALCHEMY_DATABASE_URI key
app.config["SQLALCHEMY_DATABASE_URI"] = "sqlite:///travel_library.db"
app.config["SQLALCHEMY_TRACK_MODIFICATIONS"] = False
app.config["SECRET_KEY"] = "i-dont-know"
# create an SQLAlchemy object named `db` and bind it to your app
db = SQLAlchemy(app)


# a simple initial greeting
@app.route("/")
@app.route("/index")
@app.route("/home")
def welcome_page():
	# render a login page before entering this page!
	return render_template("welcome_page.html")


# app name
@app.errorhandler(404)
def not_found(e):  # is this var, e, needed?
	return render_template("404.html")


# I still don't get why routes must be imported here!!!
from src.routes import *

# Need to use this boiler plate so that other functions can be tested in Shell without triggering the Flask App to run
if __name__ == "__main__":
	app.run(host="0.0.0.0", port=81)

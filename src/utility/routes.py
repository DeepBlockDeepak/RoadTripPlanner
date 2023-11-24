from flask import redirect, url_for, render_template
from flask_login import login_required
from database import db
from src.models import Place
from src.routing_helper_functions import delete_removed_place_from_users_lists
from src.utility import utility


# Remove a Place from the available Place() visible from the prospective dashboard, available to only an Admin, perhaps?
# Redirects back to the dashboard
@utility.route("/remove_place/<int:place_id>")
@login_required
def remove_place(place_id):
	# from the Favitem model, fetch the item with primary key item_id to be deleted
	removed_place = Place.query.get(place_id)
	# using db.session delete the item
	db.session.delete(removed_place)
	# commit the deletion
	db.session.commit()

	# call this function in order to remove any list Items() which contain the deleted place
	delete_removed_place_from_users_lists(place_id)

	return redirect(url_for("dashboard.dashboard"))


# Routes the "DB SCHEMA" navbar button to the image of our DB Schema
@utility.route("/display_schema")
@login_required
def display_schema():
	return render_template("schema_diagram.html")


@utility.route("/")
@utility.route("/index")
@utility.route("/home")
def welcome_page():
	return render_template("welcome_page.html")


@utility.app_errorhandler(404)
def not_found(_):
	return render_template("404.html")

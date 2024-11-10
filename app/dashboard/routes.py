from flask import redirect, render_template, request, url_for
from flask_login import current_user, login_required

from app.dashboard import dashboard as dashboard_bp
from app.models import Blurb, Place, User
from database import db


# Sets up the dashboard functionality for the navbar button and renders the dashboard page
@dashboard_bp.route("/dashboard", methods=["GET"])
def dashboard():
	users = User.query.all()
	most_favorited_places = Place.query.order_by(Place.times_favorited.desc())[:5]
	most_searched_places = Place.query.order_by(Place.times_searched.desc())[:5]

	# query all blurbs for the dashboard rendering
	blurbs = Blurb.query.all()

	return render_template(
		"dashboard.html",
		users=users,
		most_favorited_places=most_favorited_places,
		most_searched_places=most_searched_places,
		blurbs=blurbs,
	)


# Allows the user to enter a blurb
@dashboard_bp.route("/submit_blurb", methods=["POST"])
@login_required
def submit_blurb():
	# obtain the User's blurb content and create the Blurb instance for the db transaction
	content = request.form["blurb"]
	blurb = Blurb(content=content, author=current_user)

	db.session.add(blurb)
	db.session.commit()

	return redirect(url_for("dashboard.dashboard"))

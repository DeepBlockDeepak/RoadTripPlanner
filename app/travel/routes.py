from flask import render_template
from flask_login import login_required

from app.models import Place, Travel, User
from app.travel import travel


# Displays/anchors the User's list of Travels
@travel.route("/travel_profile/<int:user_id>/<int:travel_id>")
@login_required
def travel_profile(user_id, travel_id):
	# Grab specific user
	user = User.query.filter_by(id=user_id).first_or_404(
		description="No such user found."
	)

	# find specific Travel belonging to that user
	travel = Travel.query.get(travel_id)
	# travel = Travel.query.filter_by(id=travel_id).first_or_404(description ="No Travel found!")

	# Send all Places to the template for matching with the travelplaceitems
	places = Place.query.all()

	return render_template(
		"profile_travels.html", user=user, travel=travel, places=places
	)

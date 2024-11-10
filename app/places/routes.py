import json

from flask import render_template
from flask_login import login_required

from app.models import Place
from app.places import places
from app.scraping_functions.wiki_places import get_main_image


# Renders page detailing the Place()
# used for anchoring Place items within html
@places.route("/place_info/<int:place_id>", methods=["POST", "GET"])
@login_required
def place_info(place_id):
	# get the unique place by id
	place = Place.query.get(place_id)

	try:
		place_wiki = json.loads(place.wiki)
	except json.decoder.JSONDecodeError:
		place_wiki = json.dumps('{"error": "wiki not availble"}')

	url_string = get_main_image(place.city, place.state)
	if not url_string:
		url_string = "https://en.wikipedia.org/static/images/icons/wikipedia.png"

	# render the place template
	return render_template(
		"place.html",
		place=place,
		wiki_content=place_wiki,
		url_string=url_string,
	)

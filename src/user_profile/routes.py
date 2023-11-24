from flask import flash, redirect, render_template, request, session, url_for
from flask_login import login_required

from database import db
from src.forms import BudgetForm, OriginDestinationForm
from src.map_requests import APIError, get_cities_list
from src.models import (
	Favoriteitem,
	Favoritelist,
	Place,
	Searchitem,
	Searchlist,
	Travel,
	Travellist,
	Travelplaceitem,
	User,
)

# from map_requests import APIError
from src.routing_helper_functions import (
	add_search_item,
	create_places_from_scraped_place_dict,
	exists,
	obtain_travel_price,
	parse_travel_form_data,
	place_generator,
)

from src.user_profile import user_profile

# constant; key for the session to store the logged-in user-id
CURRENT_SESSION_USER = "current_session_user"


# Lists all the users currently in the database
# renders the users.html template providing the list of current users
@user_profile.route("/profiles")
@login_required
def profiles():
	# grab all users
	current_users = User.query.all()

	return render_template("users.html", current_users=current_users)


# Displays a specific User's profile page
# renders the profile.html template for the User
@user_profile.route("/profile/<int:user_id>", methods=["GET", "POST"])
@login_required
def profile(user_id):
	# grab the specific user
	user = User.query.filter_by(id=user_id).first_or_404(
		description="No such user found."
	)

	# Redirect the logged-in intruder back to their own page
	if (logged_in_user_id := session[CURRENT_SESSION_USER]) != user.id:
		logged_in_user = User.query.filter_by(id=logged_in_user_id).first_or_404(
			description="No such user found."
		)
		flash(f"Sorry, {logged_in_user.username}. You're not {user.username}!")
		return redirect(url_for("user_profile.profile", user_id=logged_in_user.id))

	# create the Travel Form, allowing the User to send POST request to database
	travel_form = OriginDestinationForm(csrf_enabled=False)
	# create the BudgetForm, allowing the User to enter their travel budget
	budget_form = BudgetForm(csrf_enabled=False)

	# logic for obtaining User's budget
	if request.method == "POST" and budget_form.validate():
		# obtain the budget value and store into the User's budet attr, then commit
		user.budget = budget_form.budget.data
		db.session.commit()

	# logic for when the user submits the POST request with filled input fields
	if request.method == "POST" and travel_form.validate():
		# Obtain both city,state fields for Origin & Dest from the TravelForm
		origin_city, origin_state = parse_travel_form_data(
			travel_form, form_field="origin"
		)
		destination_city, destination_state = parse_travel_form_data(
			travel_form, form_field="destination"
		)

		# query the Place table for the potentially cached Org/Dest Places
		# a new Place will be returned if Place doesn't contain the Places already
		origin_place = place_generator(origin_city, "", origin_state)
		dest_place = place_generator(destination_city, "", destination_state)

		# Since the User searched these two locations, add them to their search list
		# call add_search_item()
		add_search_item(user.id, origin_place.id, user.searchlist_id)
		add_search_item(user.id, dest_place.id, user.searchlist_id)

		# Create the Travel entity which identifies the origin/destination travel
		# TODO: method for ensuring that a Travel() object doesn't already exist (unique city and state val tuples)

		new_Travel = Travel(
			origin_place_id=origin_place.id,
			destination_place_id=dest_place.id,
			travellist_id=user.travellist_id,
			price=obtain_travel_price(
				f"{origin_city}, {origin_state}",
				f"{destination_city}, {destination_state}",
			),
		)
		db.session.add(new_Travel)

		# Format: route = {cityID1: [city, county, state], cityID2: [city, county, state]}
		route = get_cities_list(
			f"{origin_city}, {origin_state}", f"{destination_city}, {destination_state}"
		)
		try:
			# route_str = ";".join([f"{city[0]}, {city[2]}" for city in route.values()])
			route_places_list = create_places_from_scraped_place_dict(route)
		except APIError:
			# TODO: Handle in some way
			print("Some garbage happened with get_cities_list")

		# transform the route_places string repr into a list of Place() elements

		# now create TravelPlaceItem for each route city, which will be mappable from the User's Travel List
		for place in route_places_list:
			new_travel_place_item = Travelplaceitem(
				place_id=place.id, travel_id=new_Travel.id
			)
			db.session.add(new_travel_place_item)

		# commit all changes !
		db.session.commit()

	# obtain all Places, which now contain the Origin and Destination Places
	places = Place.query.all()
	# query the user's Lists for rendering purposes
	favorite_list = Favoritelist.query.get(user.favoritelist_id)
	search_list = Searchlist.query.get(user.searchlist_id)
	travel_list = Travellist.query.get(user.travellist_id)

	return render_template(
		"profile.html",
		template_user=user,
		template_places=places,
		template_favorite_list=favorite_list,
		template_search_list=search_list,
		template_travel_list=travel_list,
		travel_form=travel_form,
		budget_form=budget_form,
	)


# When a user clicks the 'Add' button next to a Place,
#   that Place is added to their Favorite List (as represented by a FavoriteItem)
# redirects back to the User's profile.html page
@user_profile.route(
	"/add_favorite_item/<int:user_id>/<int:place_id>/<int:favoritelist_id>"
)
@login_required
def add_favorite_item(user_id, place_id, favoritelist_id):
	# create the new Item
	new_favorite_item = Favoriteitem(place_id=place_id, favoritelist_id=favoritelist_id)
	user = User.query.filter_by(id=user_id).first_or_404(
		description=f"No user with id = {user_id} found!"
	)
	favoritelist = Favoritelist.query.filter_by(
		id=user.favoritelist_id
	).first()  # use first_or_404 here?

	# If the place's associated FavoriteItem doesn't already exist, make one
	if not exists(new_favorite_item, favoritelist.favoriteplaces):
		place = Place.query.get(place_id)
		# add the new item to the db
		db.session.add(new_favorite_item)
		# increase the times favorited counter for the Place associated with the new item
		place.times_favorited += 1
		# commit the database changes here
		db.session.commit()

	return redirect(url_for("user_profile.profile", user_id=user_id))


# single function which can either remove item from either the Favorites or the Searched Items, depending on the value passed to the 'item_type' parameter.
@user_profile.route("/remove_item/<int:user_id>/<int:item_id>/<string:item_type>")
@login_required
def remove_item(user_id, item_id, item_type):
	# item_handler returns either the Favorite or Search item Classes depending on the value passed
	item_handler = {"favorite": Favoriteitem, "search": Searchitem}

	# obtain the appropriate table based on the item-type in question
	item_table = item_handler[item_type]

	removed_item = item_table.query.get(item_id)

	# find the place associated with this item-record, and decrement it's attribute
	associated_place = Place.query.get(removed_item.place_id)

	# decrement the appropriate metric based on which remove_item operation occurred
	if item_type == "favorite":
		associated_place.times_favorited -= 1
	# when item_type == "search"
	else:
		associated_place.times_searched -= 1

	# remove the appropriate item
	db.session.delete(removed_item)
	db.session.commit()

	return redirect(url_for("user_profile.profile", user_id=user_id))

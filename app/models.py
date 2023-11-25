"""
SQLAlchemy Classes stored in the database.
Think of these classes as SQL tables.
"""

from datetime import datetime

import pytz
from flask_login import UserMixin
from werkzeug.security import check_password_hash, generate_password_hash

from database import db


class Blurb(db.Model):
	"""Represents a short message or 'tweet' that a user can post to the dashboard.

	Attributes:
	        id (int): Primary key.
	        content (str): The content of the blurb, limited to 120 characters.
	        author_id (int): Foreign key linking to the user who authored the blurb.
	        author (User): Relationship linking to the User model.
	"""

	id = db.Column(db.Integer, primary_key=True)
	content = db.Column(db.String(120), nullable=False)
	author_id = db.Column(db.Integer, db.ForeignKey("user.id"), nullable=False)
	author = db.relationship("User", backref=db.backref("blurbs", lazy=True))


class User(db.Model, UserMixin):
	"""Represents a user of the application, including their authentication and profile details.

	Attributes:
	        id (int): Primary key.
	        username (str): The user's chosen username, unique among all users.
	        budget (Numeric): The user's travel budget.
	        favoritelist_id (int): Foreign key linking to the user's list of favorited Places.
	        searchlist_id (int): Foreign key linking to the user's list of searched Places.
	        travellist_id (int): Foreign key linking to the user's list of Travels.
	        email (str): The user's email address, unique among all users.
	        password_hash (str): Hash of the user's password for secure storage.
	        joined_at (DateTime): Timestamp when the user joined, in Mountain Time.

	Methods:
	        set_password(password): Hashes a password and stores it.
	        check_password(password): Verifies a given password against the stored hash.
	"""

	id = db.Column(db.Integer, primary_key=True)
	username = db.Column(db.String(50), index=True, unique=True)
	budget = db.Column(db.Numeric(precision=10, scale=2), nullable=False)
	favoritelist_id = db.Column(db.Integer, db.ForeignKey("favoritelist.id"))
	searchlist_id = db.Column(db.Integer, db.ForeignKey("searchlist.id"))
	travellist_id = db.Column(db.Integer, db.ForeignKey("travellist.id"))
	email = db.Column(db.String(120), index=True, unique=True)
	password_hash = db.Column(db.String(128))
	joined_at = db.Column(
		db.DateTime(), index=True, default=datetime.now(pytz.timezone("America/Denver"))
	)

	def set_password(self, password):
		self.password_hash = generate_password_hash(password)

	def check_password(self, password):
		return check_password_hash(self.password_hash, password)

	# saves time in the html representation (can just use 'user' instead of 'user.username')
	def __repr__(self):
		return f"{self.username}"


class Place(db.Model):
	"""Represents a City or geographic location.

	Attributes:
	        id (int): Primary key.
	        city (str): Name of the city.
	        state (str): Name of the state.
	        population (int): Population of the place.
	        activities (str): String of activities available at the place.
	        wiki (str): Wiki information about the place.
	        times_favorited (int): Number of times this place has been favorited.
	        times_searched (int): Number of times this place has been searched.
	"""

	id = db.Column(db.Integer, primary_key=True)
	city = db.Column(db.String(80), index=True, unique=False)
	state = db.Column(db.String(80), index=True, unique=False)
	population = db.Column(db.Integer, index=False, unique=False)
	activities = db.Column(db.String(1000), index=False, unique=False)
	wiki = db.Column(db.String(5000), index=False, unique=False)
	times_favorited = db.Column(db.Integer, index=False, unique=False)
	times_searched = db.Column(db.Integer, index=False, unique=False)

	# custom representation for html
	def __repr__(self):
		return f"{self.city}, {self.state}"


class Favoriteitem(db.Model):
	"""Links a Place to a User's list of favorites, representing a favorited place.

	Attributes:
	        id (int): Primary key.
	        place_id (int): Foreign key to the associated Place.
	        favoritelist_id (int): Foreign key to the user's Favoritelist.
	"""

	id = db.Column(db.Integer, primary_key=True)
	place_id = db.Column(db.Integer, db.ForeignKey("place.id"))
	favoritelist_id = db.Column(db.Integer, db.ForeignKey("favoritelist.id"))

	def __repr__(self):
		return (
			f"Item's Place associated with -> {Place.query.filter_by(id=self.place_id)}"
		)


class Searchitem(db.Model):
	"""Links a Place to a User's list of searched items, representing a searched Place.

	Attributes:
	        id (int): Primary key.
	        place_id (int): Foreign key to the associated Place.
	        searchlist_id (int): Foreign key to the User's Searchlist.
	"""

	id = db.Column(db.Integer, primary_key=True)
	place_id = db.Column(db.Integer, db.ForeignKey("place.id"))
	searchlist_id = db.Column(db.Integer, db.ForeignKey("searchlist.id"))


# Like the other *item classes, this class is for abstracting a Place() with the list Class that stores it.
# That way, if a 'place' needs to ever be removed from a list, the Place() entity itself isn't removed from the db, just the abstracted item class.
class Travelplaceitem(db.Model):
	"""Links a Place to a Travel itinerary, representing a stop or destination on a Travel route.

	Attributes:
	        id (int): Primary key.
	        place_id (int): Foreign key to the associated place.
	        travel_id (int): Foreign key to the associated travel itinerary.
	"""

	id = db.Column(db.Integer, primary_key=True)
	place_id = db.Column(db.Integer, db.ForeignKey("place.id"))
	travel_id = db.Column(db.Integer, db.ForeignKey("travel.id"))


# ___ NOTES ON db.relationship() ____
"""
1. the first argument denotes which model is to be on the 'many' side of the relationship: Favoriteitem.
2. backref = 'favoritelist' establishes a favoritelist attribute in the related class (in our case, class Favoriteitem) which will serve to refer back to the related Favoritelist object.
3. lazy = dynamic makes related objects load as SQLAlchemy's query objects.
4. cascade="all, delete, delete-orphan" helps to delete all downstream objects when a parent Entity is deleted
"""


class Favoritelist(db.Model):
	"""Represents a User's list of favorited Places.

	Attributes:
	        id (int): Primary key.
	        favoriteplaces (relationship): Dynamically loaded list of Favoriteitems.
	"""

	id = db.Column(db.Integer, primary_key=True)
	favoriteplaces = db.relationship(
		"Favoriteitem",
		backref="favoritelist",
		lazy="dynamic",
		cascade="all, delete, delete-orphan",
	)


class Searchlist(db.Model):
	"""Represents a User's list of searched Places.

	Attributes:
	        id (int): Primary key.
	        searchplaces (relationship): Dynamically loaded list of Searchitems.
	"""

	id = db.Column(db.Integer, primary_key=True)
	searchplaces = db.relationship(
		"Searchitem",
		backref="searchlist",
		lazy="dynamic",
		cascade="all, delete, delete-orphan",
	)


class Travel(db.Model):
	"""Represents a User's travel plan, including origin, destination, and route.

	Attributes:
	        id (int): Primary key.
	        origin_place_id (int): Foreign key to the Place of origin.
	        destination_place_id (int): Foreign key to the destination Place.
	        travellist_id (int): Foreign key to the user's Travellist.
	        price (Numeric): Estimated cost of the travel.
	        route_places (relationship): Dynamically loaded list of Places on the travel route.
	"""

	id = db.Column(db.Integer, primary_key=True)
	origin_place_id = db.Column(db.Integer, db.ForeignKey("place.id"))
	destination_place_id = db.Column(db.Integer, db.ForeignKey("place.id"))
	travellist_id = db.Column(db.Integer, db.ForeignKey("travellist.id"))
	price = db.Column(db.Numeric(precision=10, scale=2), nullable=False)

	# 1 Travel() -> Many TravelPlaceItem()'s where each TravelPlaceItem has a foreign key to the Travel entity and a Place entity
	route_places = db.relationship(
		"Travelplaceitem",
		backref="travel",
		lazy="dynamic",
		cascade="all, delete, delete-orphan",
	)

	def __repr__(self) -> str:
		# return super().__repr__()
		origin_place = Place.query.filter_by(id=self.origin_place_id).first()
		dest_place = Place.query.filter_by(id=self.destination_place_id).first()
		return f"{origin_place}   --->   {dest_place}"


class Travellist(db.Model):
	"""Represents a User's list of Travel plans.

	Attributes:
	        id (int): Primary key.
	        travels (relationship): Dynamically loaded list of Travel objects.
	"""

	id = db.Column(db.Integer, primary_key=True)
	travels = db.relationship(
		"Travel",
		backref="travellist",
		lazy="dynamic",
		cascade="all, delete, delete-orphan",
	)

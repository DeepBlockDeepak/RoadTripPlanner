"""
SQLAlchemy Classes stored in the database.
Think of these classes as SQL tables.
"""

from main import db
from flask_login import UserMixin
from werkzeug.security import generate_password_hash, check_password_hash
from datetime import datetime
import pytz


# Allows a User to write a "tweet" on the Dashboard
class Blurb(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    content = db.Column(db.String(120), nullable=False)
    author_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)

    author = db.relationship('User', backref=db.backref('blurbs', lazy=True))

# A User has a list of favorited Destinations, as well as a list of searched ones
class User(db.Model, UserMixin):
  id = db.Column(db.Integer, primary_key = True)
  
  username = db.Column(db.String(50), index = True, unique = True)

  # stores the user's budget
  budget = db.Column(db.Numeric(precision=10, scale=2), nullable=False)
  
  # keep a list of favorited Destinations
  favoritelist_id = db.Column(db.Integer, db.ForeignKey('favoritelist.id'))

  # keep a list of searched destinations
  searchlist_id = db.Column(db.Integer, db.ForeignKey('searchlist.id'))

  # a list of Travels for each User
  travellist_id = db.Column(db.Integer, db.ForeignKey('travellist.id'))

  # user-sign-in/registration attributes
  email = db.Column(db.String(120), index = True, unique = True)
  
  password_hash = db.Column(db.String(128))
  
  # format the joined_at to use Mountain Time
  joined_at = db.Column(db.DateTime(), index = True, default= datetime.now(pytz.timezone('America/Denver')))

  # pass word hashing and authentication functions
  def set_password(self, password):
    self.password_hash = generate_password_hash(password)

  def check_password(self, password):
    return check_password_hash(self.password_hash, password)

  # saves time in the html representation (can just use 'user' instead of 'user.username')
  def __repr__(self):
    return f"{self.username}"


# Each City will be modeled here
class Place(db.Model):
  id = db.Column(db.Integer, primary_key = True)

  city = db.Column(db.String(80), index=True, unique=False)
  state = db.Column(db.String(80), index=True, unique=False)
  population = db.Column(db.Integer, index=False, unique=False)


# maybe semicolon delimit the activities, and parse them later on, hence a larger String value here
  activities = db.Column(db.String(1000), index=False, unique=False)
  
  wiki = db.Column(db.String(5000), index=False, unique=False)

  times_favorited = db.Column(db.Integer, index=False, unique=False)

  times_searched = db.Column(db.Integer, index=False, unique=False)

  # custom representation for html
  def __repr__(self):
    return f"{self.city}, {self.state}"    


# creates a union of a Favorited Place and the the Favorite list it is associated with 
class Favoriteitem(db.Model):
  id = db.Column(db.Integer, primary_key = True)

  place_id = db.Column(db.Integer, db.ForeignKey('place.id'))

  favoritelist_id = db.Column(db.Integer, db.ForeignKey('favoritelist.id'))  

  def __repr__(self):
    return f"Item's Place associated with -> {Place.query.filter_by(id=self.place_id)}"
    

class Searchitem(db.Model):
  id = db.Column(db.Integer, primary_key = True)

  place_id = db.Column(db.Integer, db.ForeignKey('place.id'))

  searchlist_id = db.Column(db.Integer, db.ForeignKey('searchlist.id'))  


# Like the other *item classes, this class is for abstracting a Place() with the list Class that stores it. 
# That way, if a 'place' needs to ever be removed from a list, the Place() entity itself isn't removed from the db, just the abstracted item class.
class Travelplaceitem(db.Model):
  id = db.Column(db.Integer, primary_key = True)

  place_id = db.Column(db.Integer, db.ForeignKey('place.id'))

  travel_id = db.Column(db.Integer, db.ForeignKey('travel.id'))  


# ___ NOTES ON db.relationship() ____
"""
1. the first argument denotes which model is to be on the 'many' side of the relationship: Favoriteitem.
2. backref = 'favoritelist' establishes a favoritelist attribute in the related class (in our case, class Favoriteitem) which will serve to refer back to the related Favoritelist object.
3. lazy = dynamic makes related objects load as SQLAlchemy's query objects.
4. cascade="all, delete, delete-orphan" helps to delete all downstream objects when a parent Entity is deleted
"""
# acts as a list of Favorited places
class Favoritelist(db.Model):
  id = db.Column(db.Integer, primary_key = True)

  favoriteplaces = db.relationship('Favoriteitem', backref = 'favoritelist', lazy = 'dynamic', cascade = "all, delete, delete-orphan")


# acts as a list of Searched places
class Searchlist(db.Model):
  id = db.Column(db.Integer, primary_key = True)

  searchplaces = db.relationship('Searchitem', backref = 'searchlist', lazy = 'dynamic', cascade = "all, delete, delete-orphan")


# Travel class belonging to A User who Submitted an Origin/Destination request.
class Travel(db.Model):
  id = db.Column(db.Integer, primary_key = True)

  # origin and dest Places are pointed to
  origin_place_id = db.Column(db.Integer, db.ForeignKey('place.id'))
  
  destination_place_id = db.Column(db.Integer, db.ForeignKey('place.id'))

  # Travel belongs a specific User's specific TravelList
  travellist_id = db.Column(db.Integer, db.ForeignKey('travellist.id')) 
  
  # stores the expense of this particular road-trip/Travel
  price = db.Column(db.Numeric(precision=10, scale=2), nullable=False)

  
  # 1 Travel() -> Many TravelPlaceItem()'s where each TravelPlaceItem has a foreign key to the Travel entity and a Place entity
  route_places = db.relationship('Travelplaceitem', backref='travel', lazy='dynamic', cascade="all, delete, delete-orphan")


  def __repr__(self) -> str:
    #return super().__repr__()
    origin_place = Place.query.filter_by(id=self.origin_place_id).first()
    dest_place = Place.query.filter_by(id=self.destination_place_id).first()
    return f"{origin_place}   --->   {dest_place}"
    

# One User's Travellist can hold many Travels
class Travellist(db.Model):
  id = db.Column(db.Integer, primary_key = True)

  travels = db.relationship('Travel', backref = 'travellist', lazy = 'dynamic', cascade = "all, delete, delete-orphan")


  
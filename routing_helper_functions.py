"""
Stores the non-route, helper functions needed in routes.py
"""

from main import db
from models import Favoriteitem, Place, Searchitem, Searchlist, User
from scraping_functions.wiki_places import create_place_with_wiki
from scraping_functions.state_abbreviations import state_abbr
from scraping_functions.gas_price_extractor import obtain_avg_gas_price
from scraping_functions.population import get_place_pop
from log_manager import global_logger as log
from map_requests import get_nearby_activities, get_route_distance_meters, APIError
import json

# used for parsing the Travel Form data
TRAVEL_FORM_DELIMITER = ", "
ROUTE_PLACES_DELIMITER = ";"
LACKING_MSG = "information not available for"
# calculate the average gas price scrape once per Flask session
avg_gas_price = obtain_avg_gas_price()


# currently only uses a gas price calculation to estimate price
def obtain_travel_price(origin_place, dest_place, avg_gas_mileage=26):

  # find the org->dest distance; convert to miles
  distance = 0.00062137 * float(
    get_route_distance_meters(origin_place, dest_place))

  # unit-conversion: miles * gal/mile * $/gal = $'s
  gas_cost = round(distance / avg_gas_mileage * avg_gas_price, 2)

  return gas_cost


#Function which will check each user's list.item.place's and see if it matches a newly deleted place from the admin page\
# if found, remove it from the list
def delete_removed_place_from_users_lists(deleted_place_id):

  #query all the FavoriteList() objects
  fav_items = Favoriteitem.query.all()

  #search each item's place_id attr, and delete accordingly
  for item in fav_items:
    if item.place_id == deleted_place_id:
      db.session.delete(item)
      db.session.commit()


# query Place() for the potentially cached Org/Dest locations
# if the query results in an empty list (Place doesn't already exist), then create the new Place entity
def place_generator(city: str, county: str, state: str) -> 'Place':
  # TODO: "City,State" need to be sent to scraping method and that info
  #         needs to be placed in the Place attrs here for instancing
  if not (place := Place.query.filter(Place.city == city, Place.state
                                      == state).all()):
    place_pop = get_place_pop(city, state)  # addd in

    # TODO: The Activities-Scraper Developer needs to format the activities textblock and render the material within the Place.html so that it's cleanly displayed
    if len(state) == 2:
      try:
        state = state_abbr[state]
      except:
        print("Invalid State")

    place_wiki = create_place_with_wiki(city, county, state, LACKING_MSG)

    if place_wiki is None or not place_wiki:
      wiki_json = '{"error": "Wiki Not Availble!"}'
    else:
      wiki_json = json.dumps(place_wiki)
    #note: old place for GPT implimentation DEPRECATED

    try:
      act_list = get_nearby_activities(city + ", " + state)
    except APIError:
      log.warn(f"No nearby results for '{city}, {state}\'")
      act_list = []

    org_acts = ""

    for act in act_list:
      org_acts = org_acts + act[0] + "^"

    org_acts = org_acts[0:-1]

    place = Place(
      city=city,
      state=state,
      population=place_pop,
      activities=org_acts,
      wiki=wiki_json,
      times_favorited=0,
      times_searched=0,
    )
    # add the new Place to the db
    db.session.add(place)
  else:
    # if the original query resulted in a match, then 'place' was a list object.
    # so convert the queried 'place' list into its first obtained element from the cached search
    place = place[0]

  # commit the changes to the db.
  db.session.commit()

  return place


# Helper function for parsing User-inputted data in the travel form
# returns -> Tuple(str,str) -> (city,state)
# TODO: Input-validate the Form info. Right now a comma+space is used as a delimeter for a "City, State" format only
def parse_travel_form_data(travel_form,
                           form_field: str,
                           delimiter=TRAVEL_FORM_DELIMITER):
  if form_field == "origin":
    city, state = travel_form.origin_city_state.data.split(delimiter)
  elif form_field == "destination":
    city, state = travel_form.destination_city_state.data.split(delimiter)
  else:
    # Catch an error here?
    city, state = None, None

  return city, state


# Helper function for accepting strings of delimited city,state strings
#   and returning a list of Place objects for Places along the RoadTrip route
def create_places_from_scraped_place_dict(route_places):
    #indent here

      # turns route_places into a list of tuples where each tuple is a (city, state) representing a Place's city,state info
      route_places = [
          place_generator(city[0], city[1], city[2]) for city in route_places.values()
      ]
    
      # city_county_state_list = route_places.split(ROUTE_PLACES_DELIMITER)
      # for i, city_state_combo in enumerate(city_county_state_list):
      #   city_county_state_list[i] = city_state_combo.split(", ")
    
      # # route places then creates a list of Places
      # route_places = [
      #   place_generator(item[0], item[1], item[2]) for item in city_county_state_list
      # ]
    
      return route_places


# Checks if an item to be added is already in a list
def exists(item, list_items) -> bool:

  for i in list_items:
    #check if the primary key is equal, indicating a match
    if i.place_id == item.place_id:
      return True
  return False


# This adds a Searched Place Item to the User's Searched Places List if
#   a Place doesn't already exist in that List (as represented by a SearchedItem)
# Similar to how the add_favorite_item() function works, just without re-routing or rendering
def add_search_item(user_id, place_id, searchlist_id):

  # create the new Item
  new_search_item = Searchitem(place_id=place_id, searchlist_id=searchlist_id)
  user = User.query.filter_by(id=user_id).first_or_404(
    description=f"No user with id = {user_id} found!")
  searchlist = Searchlist.query.filter_by(
    id=user.searchlist_id).first()  # use first_or_404 here?

  # If the place's associated SearchItem doesn't already exist, make one
  if not exists(new_search_item, searchlist.searchplaces):
    place = Place.query.get(place_id)
    # add the new item to the db
    db.session.add(new_search_item)
    #increase the counter for the Place's number of times searched
    place.times_searched += 1
    #commit the database changes here
    db.session.commit()

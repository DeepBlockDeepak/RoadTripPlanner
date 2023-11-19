from flask import session, render_template, request, url_for, redirect, flash
from main import app, db
from src.models import User, Place, Favoritelist, Favoriteitem, Searchlist, Searchitem, Travel, Travellist, Travelplaceitem, Blurb
from src.forms import OriginDestinationForm, RegistrationForm, LoginForm, SummarizeForm, BudgetForm
from flask_login import current_user, login_user, logout_user, login_required
from src.map_requests import get_cities_list, APIError
#from map_requests import APIError
from src.routing_helper_functions import delete_removed_place_from_users_lists, place_generator, parse_travel_form_data, create_places_from_scraped_place_dict, exists, add_search_item, obtain_travel_price
from src.chat_gpt_tools.gpt import SumChatGPT
import json
from src.scraping_functions.wiki_places import get_main_image


# constant; key for the session to store the logged-in user-id
CURRENT_SESSION_USER = "current_session_user"


# handles the user login
@app.route("/login", methods=['GET', 'POST'])
def login():

  # immediately check if the user is logged in, and if so, redirect them
  if current_user.is_authenticated:
    flash("You must logout before you can log back in.")
    return render_template("welcome_page.html")

  # make a login form
  form = LoginForm(csrf_enabled=False)

  if form.validate_on_submit():
    # find the user based on their sign-in email
    user = User.query.filter_by(email=form.email.data).first()

    # check for bad log-ins, notifying the user
    if user is None or not user.check_password(form.password.data):
      flash('You used an invalid username or invalid password')
      return redirect(url_for('login'))

    # log the verified user into the app, and store them into the session
    login_user(user, remember=form.remember.data)
    session[CURRENT_SESSION_USER] = user.id

    # not sure how to use this yet
    # next_page = request.args.get('next')

    # redirect the valid login to the profiles page
    #return redirect(next_page) if next_page else redirect(url_for('profiles', _external=True, _scheme='http'))
    flash(f"Successful login, {user.username}.")
    return redirect(url_for('profile', user_id=user.id))

  # if a failed form attempt occurred
  return render_template('login.html', form=form)


# handles logout functionality
@app.route("/logout")
@login_required
def logout():
  # find who the logged-in user is
  logged_in_user_id = session[CURRENT_SESSION_USER]
  logged_in_user = User.query.filter_by(id=logged_in_user_id).first_or_404(
    description="No such user found.")
  logout_user()
  # reset the current session user to None
  session[CURRENT_SESSION_USER] = "None"
  flash(f"Successfully logged out, {logged_in_user.username}.")
  return render_template("welcome_page.html")


#OLD PLACE_INFO ROUTE
# Renders page detailing the Place()
# used for anchoring Place items within html
#@app.route("/place_info/<int:place_id>")
#@login_required
#def place_info(place_id):
# get the unique place by id
#place = Place.query.get(place_id)

#return render_template('place.html', place=place)


# Renders page detailing the Place()
# used for anchoring Place items within html
@app.route("/place_info/<int:place_id>", methods=["POST", "GET"])
@login_required
def place_info(place_id):
  # get the unique place by id
  place = Place.query.get(place_id)

  try:
    place_wiki = json.loads(place.wiki)
  except json.decoder.JSONDecodeError:
    place_wiki = json.dumps('{"error": "wiki not availble"}')



  # instantiate the summary_form
  summary_form = SummarizeForm(csrf_enabled=False)

  # when user clicks the button, they trigger the logic below
  if summary_form.validate():
    # starts instance of chatGPT
    gpt = SumChatGPT()
    # pulls city and state name from Places entity
    city = place.city
    state = place.state
    gpt_dest = city + ", " + state
    # pulls scraped wiki from Places entity
    wiki = place.wiki
    #deconstructs wiki json to extract history header
    json_wiki_data = json.loads(wiki)
    gpt_output = ""

    #checks to see if wiki is null or history section is null
    if not json_wiki_data or "History" not in json_wiki_data:
      gpt_output = f"{gpt_dest} information isn't Available."
    else:
      #if data wiki present, proceed
      gpt_data = json_wiki_data['History']
      # sends city-state and scraped history to be processed by GPT API
      try:
        print("GPT CURRENT QUERY: " + gpt_dest)
        gpt_output = gpt.gptWrapper(gpt_dest, gpt_data)
      except Exception as e:
        print(e)
        print("GPT EXCEPTION ERROR")
        #places default message if exception occoured
        gpt_output = f"{gpt_dest} information isn't Available."
    # places gpt output in Places atribute to be sent to the template
    place.gpt_text = gpt_output

    # render the gpt summary template
    return render_template('place_sum.html', place=place, form=summary_form)

  url_string = get_main_image(place.city, place.state)
  if not url_string:
    url_string = "https://en.wikipedia.org/static/images/icons/wikipedia.png"
    
  # render the place template
  return render_template(
    'place.html',
    place=place,
    form=summary_form,
    wiki_content=place_wiki,
    url_string = url_string
  )


# Displays/anchors the User's list of Travels
@app.route("/travel_profile/<int:user_id>/<int:travel_id>")
@login_required
def travel_profile(user_id, travel_id):

  # Grab specific user
  user = User.query.filter_by(id=user_id).first_or_404(
    description="No such user found.")

  # find specific Travel belonging to that user
  travel = Travel.query.get(travel_id)
  # travel = Travel.query.filter_by(id=travel_id).first_or_404(description ="No Travel found!")

  # Send all Places to the template for matching with the travelplaceitems
  places = Place.query.all()

  return render_template('profile_travels.html',
                         user=user,
                         travel=travel,
                         places=places)

# Routes the "REGISTER" navbar button to the registration form
@app.route('/register', methods=['GET', 'POST'])
def register():

  # immediately check if the user is logged in, and if so, redirect them
  if current_user.is_authenticated:
    flash("You must logout before you can register.")
    return render_template("welcome_page.html")
  # instance the registration form
  form = RegistrationForm(csrf_enabled=False)

  # upon valid Post submission create a new User with their associated new Lists!
  if request.method == 'POST' and form.validate_on_submit():
    # create new User Lists and commit to DB
    new_travel_list = Travellist()
    new_fav_list = Favoritelist()
    new_search_list = Searchlist()

    db.session.add(new_travel_list)
    db.session.add(new_fav_list)
    db.session.add(new_search_list)
    # MUST COMMIT BEFORE INSTANCING new USER
    db.session.commit()

    # define user with data from form here:
    user = User(username=form.username.data,
                email=form.email.data,
                budget=0,
                travellist_id=new_travel_list.id,
                favoritelist_id=new_fav_list.id,
                searchlist_id=new_search_list.id)

    # set user's password here and then add the new user to the db
    user.set_password(form.password.data)

    db.session.add(user)
    db.session.commit()

    # Log the Newly Registered User into the Travel App,
    #     thereby allowing the login-protected profiles route!
    login_user(user, remember=False)
    session[CURRENT_SESSION_USER] = user.id

    # a succesful submission redirects the new user's profile page
    return redirect(url_for('profile', user_id=user.id))

  return render_template('registration.html', title='Register', form=form)


# Routes the "DB SCHEMA" navbar button to the image of our DB Schema
@app.route("/display_schema")
@login_required
def display_schema():
  return render_template("schema_diagram.html")


# Lists all the users currently in the database
# renders the users.html template providing the list of current users
@app.route('/profiles')
@login_required
def profiles():
  # grab all users
  current_users = User.query.all()

  return render_template('users.html', current_users=current_users)


# Displays a specific User's profile page
# renders the profile.html template for the User
@app.route('/profile/<int:user_id>', methods=['GET', 'POST'])
@login_required
def profile(user_id):

  # grab the specific user
  user = User.query.filter_by(id=user_id).first_or_404(
    description="No such user found.")

  # Redirect the logged-in intruder back to their own page
  if (logged_in_user_id := session[CURRENT_SESSION_USER]) != user.id:
    logged_in_user = User.query.filter_by(id=logged_in_user_id).first_or_404(
      description="No such user found.")
    flash(f"Sorry, {logged_in_user.username}. You're not {user.username}!")
    return redirect(url_for('profile', user_id=logged_in_user.id))

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
  if request.method == 'POST' and travel_form.validate():

    # Obtain both city,state fields for Origin & Dest from the TravelForm
    origin_city, origin_state = parse_travel_form_data(travel_form,
                                                       form_field="origin")
    destination_city, destination_state = parse_travel_form_data(
      travel_form, form_field="destination")

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

    new_Travel = Travel(origin_place_id=origin_place.id,
                        destination_place_id=dest_place.id,
                        travellist_id=user.travellist_id,
                        price=obtain_travel_price(
                          f"{origin_city}, {origin_state}",
                          f"{destination_city}, {destination_state}"))
    db.session.add(new_Travel)

    # Format: route = {cityID1: [city, county, state], cityID2: [city, county, state]}
    route = get_cities_list(f"{origin_city}, {origin_state}",
                            f"{destination_city}, {destination_state}")
    try:
      # route_str = ";".join([f"{city[0]}, {city[2]}" for city in route.values()])
      route_places_list = create_places_from_scraped_place_dict(route)
    except APIError:
      # TODO: Handle in some way
      print("Some garbage happened with get_cities_list")

    # transform the route_places string repr into a list of Place() elements

    # now create TravelPlaceItem for each route city, which will be mappable from the User's Travel List
    for place in route_places_list:
      new_travel_place_item = Travelplaceitem(place_id=place.id,
                                              travel_id=new_Travel.id)
      db.session.add(new_travel_place_item)

    # commit all changes !
    db.session.commit()

  # obtain all Places, which now contain the Origin and Destination Places
  places = Place.query.all()
  # query the user's Lists for rendering purposes
  favorite_list = Favoritelist.query.get(user.favoritelist_id)
  search_list = Searchlist.query.get(user.searchlist_id)
  travel_list = Travellist.query.get(user.travellist_id)

  return render_template('profile.html',
                         template_user=user,
                         template_places=places,
                         template_favorite_list=favorite_list,
                         template_search_list=search_list,
                         template_travel_list=travel_list,
                         travel_form=travel_form,
                         budget_form=budget_form)


# When a user clicks the 'Add' button next to a Place,
#   that Place is added to their Favorite List (as represented by a FavoriteItem)
# redirects back to the User's profile.html page
@app.route(
  '/add_favorite_item/<int:user_id>/<int:place_id>/<int:favoritelist_id>')
@login_required
def add_favorite_item(user_id, place_id, favoritelist_id):

  # create the new Item
  new_favorite_item = Favoriteitem(place_id=place_id,
                                   favoritelist_id=favoritelist_id)
  user = User.query.filter_by(id=user_id).first_or_404(
    description=f"No user with id = {user_id} found!")
  favoritelist = Favoritelist.query.filter_by(
    id=user.favoritelist_id).first()  # use first_or_404 here?

  # If the place's associated FavoriteItem doesn't already exist, make one
  if not exists(new_favorite_item, favoritelist.favoriteplaces):
    place = Place.query.get(place_id)
    # add the new item to the db
    db.session.add(new_favorite_item)
    #increase the times favorited counter for the Place associated with the new item
    place.times_favorited += 1
    #commit the database changes here
    db.session.commit()

  return redirect(url_for('profile', user_id=user_id))


# single function which can either remove item from either the Favorites or the Searched Items, depending on the value passed to the 'item_type' parameter.
@app.route('/remove_item/<int:user_id>/<int:item_id>/<string:item_type>')
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

  return redirect(url_for('profile', user_id=user_id))


#Remove a Place from the available Place() visible from the prospective dashboard, available to only an Admin, perhaps?
#Redirects back to the dashboard
@app.route('/remove_place/<int:place_id>')
@login_required
def remove_place(place_id):

  #from the Favitem model, fetch the item with primary key item_id to be deleted
  removed_place = Place.query.get(place_id)
  #using db.session delete the item
  db.session.delete(removed_place)
  #commit the deletion
  db.session.commit()

  #call this function in order to remove any list Items() which contain the deleted place
  delete_removed_place_from_users_lists(place_id)

  return redirect(url_for('dashboard'))


# Sets up the dashboard functionality for the navbar button and renders the dashboard page
@app.route('/dashboard', methods=['GET'])
def dashboard():
  users = User.query.all()
  most_favorited_places = Place.query.order_by(
    Place.times_favorited.desc())[:5]
  most_searched_places = Place.query.order_by(Place.times_searched.desc())[:5]

  # query all blurbs for the dashboard rendering
  blurbs = Blurb.query.all()

  return render_template('dashboard.html',
                         users=users,
                         most_favorited_places=most_favorited_places,
                         most_searched_places=most_searched_places,
                         blurbs=blurbs)


# Allows the user to enter a blurb
@app.route('/submit_blurb', methods=['POST'])
@login_required
def submit_blurb():
  # obtain the User's blurb content and create the Blurb instance for the db transaction
  content = request.form['blurb']
  blurb = Blurb(content=content, author=current_user)

  db.session.add(blurb)
  db.session.commit()

  return redirect(url_for('dashboard'))

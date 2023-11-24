from flask import flash, redirect, render_template, request, session, url_for
from flask_login import current_user, login_required, login_user, logout_user
from app.routing_helper_functions import authenticate_user
from app.models import User, Travellist, Favoritelist, Searchlist
from app.forms import LoginForm, RegistrationForm
from app.auth import auth
from database import db

# constant; key for the session to store the logged-in user-id
CURRENT_SESSION_USER = "current_session_user"


@auth.route("/login", methods=["GET", "POST"])
def login():
	# Redirect already authenticated users to the home page
	if current_user.is_authenticated:
		flash("You are already logged in.")
		return redirect(url_for("utility.welcome_page"))

	# Create and process the login form
	form = LoginForm(csrf_enabled=False)
	if form.validate_on_submit():
		# Authenticate user
		user = authenticate_user(form.email.data, form.password.data)
		if user:
			# Login user and set session variable
			login_user(user, remember=form.remember.data)
			session[CURRENT_SESSION_USER] = user.id

			# Redirect to the requested page or to the user's profile
			next_page = request.args.get("next")
			flash(f"Welcome back, {user.username}!")
			return redirect(
				next_page or url_for("user_profile.profile", user_id=user.id)
			)
		flash("Invalid username or password.")

	return render_template("login.html", form=form)


# handles logout functionality
@auth.route("/logout", methods=["GET", "POST"])
@login_required
def logout():
	# find who the logged-in user is
	logged_in_user_id = session[CURRENT_SESSION_USER]
	logged_in_user = User.query.filter_by(id=logged_in_user_id).first_or_404(
		description="No such user found."
	)
	logout_user()
	# reset the current session user to None
	session[CURRENT_SESSION_USER] = "None"
	flash(f"Successfully logged out, {logged_in_user.username}.")
	return render_template("welcome_page.html")


# Routes the "REGISTER" navbar button to the registration form
@auth.route("/register", methods=["GET", "POST"])
def register():
	# immediately check if the user is logged in, and if so, redirect them
	if current_user.is_authenticated:
		flash("You must logout before you can register.")
		return render_template("welcome_page.html")
	# instance the registration form
	form = RegistrationForm(csrf_enabled=False)

	# upon valid Post submission create a new User with their associated new Lists!
	if request.method == "POST" and form.validate_on_submit():
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
		user = User(
			username=form.username.data,
			email=form.email.data,
			budget=0,
			travellist_id=new_travel_list.id,
			favoritelist_id=new_fav_list.id,
			searchlist_id=new_search_list.id,
		)

		# set user's password here and then add the new user to the db
		user.set_password(form.password.data)

		db.session.add(user)
		db.session.commit()

		# Log the Newly Registered User into the Travel App,
		#     thereby allowing the login-protected profiles route!
		login_user(user, remember=False)
		session[CURRENT_SESSION_USER] = user.id

		# a succesful submission redirects the new user's profile page
		return redirect(url_for("user_profile.profile", user_id=user.id))

	return render_template("registration.html", title="Register", form=form)

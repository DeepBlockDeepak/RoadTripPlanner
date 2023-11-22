from flask import render_template


# Define route for the homepage
def welcome_page():
	# Render the welcome page template
	return render_template("welcome_page.html")


# Define custom error handler for 404 errors
def not_found(_):  # Unused error argument can be indicated with an underscore
	# Render the 404 error page template
	return render_template("404.html")

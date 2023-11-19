"""
Login Manager functions placed here. 
They are necessary for tracking the App User
"""

from main import login_manager
from src.models import User


# for help managing the logged in Users
@login_manager.user_loader
def load_user(id):
	return User.query.get(int(id))


# loads the same message for any error page
@login_manager.unauthorized_handler
def unauthorized():
	return "<h1>Login to Access.</h1>"

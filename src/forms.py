from flask_wtf import FlaskForm
from wtforms import StringField, SubmitField, PasswordField, BooleanField
from wtforms.validators import DataRequired, Email, EqualTo


# Text form for allowing a User to enter their travel budget
class BudgetForm(FlaskForm):
  budget = StringField(label ="Enter Amount", validators=[DataRequired()])
  submit = SubmitField("Submit")


# Simple Text Boxes for allowing user input
class PlaceForm(FlaskForm):
  city = StringField(label = "City", validators=[DataRequired()])
  state = StringField(label ="State", validators=[DataRequired()])

  submit = SubmitField("Search Place")


# allows a user to enter origin and destination cities
class OriginDestinationForm(FlaskForm):
  origin_city_state = StringField(label = "Origin: \"City, State\"", validators=[DataRequired()])
  destination_city_state = StringField(label = "Destination: \"City, State\"", validators=[DataRequired()])
  
  submit = SubmitField("Search a Road Trip Route")


# registration form for creating new user
class RegistrationForm(FlaskForm):
  username = StringField('Username', validators=[DataRequired()])
  # add email field here:
  email = StringField("Email", validators = [DataRequired(), Email()])
  # add password fields here:
  password = PasswordField("Password", validators = [DataRequired()])
  password2 = PasswordField("Repeat Password", validators = [DataRequired(), EqualTo("password")])
  
  submit = SubmitField('Register')


# form for tracking valid logged-in, registered Users
class LoginForm(FlaskForm):
  email = StringField('Email', validators=[DataRequired(), Email()])
  password = PasswordField('Password', validators=[DataRequired()])
  remember = BooleanField('Remember Me')
  submit = SubmitField('Login')

class SummarizeForm(FlaskForm):
  submit = SubmitField("Summarize Content")

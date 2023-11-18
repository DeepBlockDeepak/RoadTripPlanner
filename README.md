`_____ TO RUN & TEST LOCALLY ON UNIX _____`
* 1.) Download the zipfile and unzip it in your local folder.
* 2.) If it's your machine's first time running this project, install Poetry following the instructions from [Poetry's official website](https://python-poetry.org/docs/#installation). Then, navigate to the project's root directory and run `poetry install` to set up the project's virtual environment and install necessary packages.
* 3.) To bootstrap the database (recommended when trying new things), run `poetry run python add_db_data.py`. After setting up the database, start the application with `poetry run python main.py`. Access the app by navigating to the provided URL in your web browser.


<br />
<br />

  

`_____ TODO _____`
  * Make the app work for the User:
      * **Display at least 1 image of the Place on its page.**
  * Input Validation/Error Handling for poorly formed user input and for Places which don't exist in the Google maps searches!
  * Spruce up the _base.html and other templates with 
a better a looking design where needed. (colors, themes, banners, backgrounds)
  * Create functionality for  SearchedPlaces/SearchList methods -> SEE HOW CURRENT `remove_list_item()` and `add_item()` functions work for help with saving time by reusing this code. They're currently called in `profile.html`.
  * Ensure that a repeated road-trip search doesn't take place (similar to how the current place_generator() won't create a new Place if that Place already exists in the db)
  * Remove all of the OpenAI material from this project
  * Update the google_map_api material, including obtaining new key

<br />
<br />



`_____ CAUTIONS _____`
  * sometimes the *instance/* directory is auto-generated after running `python3 add_db_data.py` in the replit shell. The *travel_library.db* within is the persistent database for this application. Within *main.py*, I've configured the **db location to be within the root directory**, via this line *app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///travel_library.db'*.\
  * If you need to **reset the database**, run `python3 add_db_data.py` in the Shell.

<br />
<br />
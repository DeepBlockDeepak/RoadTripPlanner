# ****************** 1 ******************
# DO AWAY WITH THE HISTORY ATTR
# USE THE NEW 'wiki' ONE INSTEAD
from main import db
from sqlalchemy.ext.mutable import MutableDict
class Place(db.Model):
  
  id = db.Column(db.Integer, primary_key = True)

  city = db.Column(db.String(80), index=True, unique=False)
  #history = db.Column(db.String(1000), index=False, unique=False)
  wiki = db.Column(MutableDict.as_mutable(db.JSON), index=False, unique=False)
  """
  REST OF ATTRIBUTES FOR PLACE
  """


# ****************** 2 ******************
#FOR DOING WIKI SCRAPING -> REPLACES get_sections()
import wikipedia
def get_wiki_sections(city, state):

    # constant for non-existing section data
    BAD_DATA = "information not available for"

    # Normalize city and state names
    city = city.strip().title()
    state = state.strip().title()

    # Search for the Wikipedia page
    search_query = f"{city}, {state}"
    
    try:
        page = wikipedia.page(search_query)
    except wikipedia.exceptions.PageError:
        print(f"No Wikipedia page found for {search_query}")
        return None
    except wikipedia.exceptions.DisambiguationError as e:
        print(f"Disambiguation page found for {search_query}. Selecting the first option.")
        try:
            page = wikipedia.page(e.options[0])
        except Exception as e:
            print(f"Error fetching the disambiguation option: {e}")
            return None
    except Exception as e:
        print(f"Error fetching the Wikipedia page for {search_query}: {e}")
        return None

    # Get the content and split it into sections
    try:
        content = page.content
        sections = content.split("\n== ")
    except Exception as e:
        print(f"Error parsing the content of the Wikipedia page for {search_query}: {e}")
        return None

    # Define the target sections
    article_secs = [
        "History",
        "Geography",
        "Demographics",
        "Economy",
        "Arts and Culture",
        "Sports",
        "Parks and Recreation",
        "Notable People",
    ]

    # Extract the content for the target sections
    result = {}
    for sec in article_secs:
        sec_content = [s for s in sections if s.startswith(sec + " ==")]
        if sec_content:
            result[sec] = sec_content[0].replace(sec + " ==", "").strip()
        else:
            result[sec] = f"{sec} {BAD_DATA} {search_query}"

    return result


# ****************** 3 ******************
# NOW WHEN STORING THE RETURN OF THIS DICTIONARY, INSTEAD OF USING create_places_from_scraped_place_strings() AS IT'S CURRENTLY BEING USED WITHIN @app.route('/profile'), USE JSON.DUMPS
import json
# Assuming the wiki_content is the dictionary returned by get_wiki_sections()
place = Place(city=city, state=state, wiki = json.dumps(wiki_content)
db.session.add(place)
db.session.commit()



# ****************** 4 ******************
In the place.html template, you can convert the JSON string back to a dictionary and loop through the key-value pairs like this:

html
{% extends "_base.html" %}

{% block content %}
{# ... #}

<div class="column" style="background-color:#ECBAF3;">
    <h2>Wiki:</h2>
    <ul>
        {% set wiki_dict = place.wiki|tojson %}
        {% for key, value in wiki_dict.items() %}
            <li>
                <h3>{{ key }}:</h3>
                <p>{{ value }}</p>
            </li>
        {% endfor %}
    </ul>
</div>

{% endblock %}
Here, we use the tojson filter to convert the JSON string back to a dictionary and then loop through the key-value pairs with a for loop.

This way, you can store the wiki content as a JSON string in the Place model and still be able to parse it easily in the template.



if __name__ == '__main__':
    d = get_wiki_sections("St. Louis", "Missouri")
    BAD_DATA = "information not available for"

    print(
        [k for k,v in d.items() if not BAD_DATA in v]
    )
    


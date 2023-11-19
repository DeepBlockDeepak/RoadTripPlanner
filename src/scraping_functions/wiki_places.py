import wikipedia
import re


def get_subsections(section_content):
  subsections = {}

  # Find all subsection titles using regular expressions
  subsec_pattern = re.compile(r'(=== ([\w\s]+) ===)')
  matches = subsec_pattern.findall(section_content)

  # If there are no subsections, return the section content as is
  if not matches:
    return section_content

  # Iterate through the matches and extract subsection content
  for i, match in enumerate(matches):
    # For each match, find the start and end positions of the subsection content
    if i < len(matches) - 1:
      start = section_content.index(match[0]) + len(match[0])
      end = section_content.index(matches[i + 1][0])
      subsection_content = section_content[start:end].strip()
    else:
      start = section_content.index(match[0]) + len(match[0])
      subsection_content = section_content[start:].strip()

    # Add the subsection content to the dictionary
    subsections[match[1]] = subsection_content

  return subsections


def get_wiki_sections(city, county, state, article_secs, LACKING_MSG):
  # Search for the Wikipedia page
  page_name = f"{city}, {county}, {state}" if county else f"{city}, {state}"
  try:
    page_py = wikipedia.page(page_name)
  except wikipedia.exceptions.PageError:
    return None
  except wikipedia.exceptions.DisambiguationError:
    return None

  # Split the page content into sections
  content = page_py.content
  sections = content.split("\n== ")

  wiki_content = {}
  for sec in article_secs:
    # Find the content for the target sections
    sec_content = [s for s in sections if s.startswith(sec + " ==")]
    if sec_content:
      # Remove the section title and process the subsections
      sec_content_text = sec_content[0].replace(sec + " ==", "").strip()
      wiki_content[sec] = get_subsections(sec_content_text)
    """
    Removing this to filter out missing sections from appearing on place.html template
    
    else:
      # Add a default message if the section is not available
      wiki_content[sec] = f"{sec} {LACKING_MSG} {page_name}"
    """

  return wiki_content


def create_place_with_wiki(city, county, state, LACKING_MSG):
  article_secs = [
    "History",
    "Geography",
    "Demographics",
    "Economy",
    "Arts and Culture",
    "Arts",
    "Culture",
    "Sports",
    "Parks and Recreation",
    "Notable People",
  ]

  wiki_dict = get_wiki_sections(city, county, state, article_secs, LACKING_MSG)

  return wiki_dict


# returns the url string, for href'ing in the template or a None
def get_main_image(city, state) -> str | None:
  # sanitize dat ass
  city = city.strip().title()
  state = state.strip().title()

  # create a search query string
  search_query = f"{city}, {state}"

  # find the wiki page
  try:
    page = wikipedia.page(search_query)
  except wikipedia.exceptions.PageError as e:
    # no wiki page found
    print(
      error :=
      f"No Wikipedia page found for {search_query}: {type(e).__name__}: {e}")
    return None
  except wikipedia.exceptions.DisambiguationError as e:
    # disambiguation page
    print(
      error :=
      f"Disambiguation page found for {search_query}: {type(e).__name__}: {e}. Selecting the first option."
    )
    try:
      page = wikipedia.page(e.options[0])
    except Exception as e:
      # error getting the disambiguation option
      print(
        error :=
        f"Error fetching the disambiguation option {search_query}: {type(e).__name__}: {e}"
      )
      return None
  except Exception as e:
    # general error fetching the Wikipedia page
    print(f"Error fetching the Wikipedia page for {search_query}: {e}")
    return None

  # get the main image URL
  try:
    # Get the first image URL
    image_url = page.images[0]

  except IndexError as e:
    # no main image
    print(error :=
          f"No main image found for {search_query}: {type(e).__name__}: {e}")
    return None

  except Exception as e:
    # there's an error getting the main image
    print(
      error :=
      f"Error getting the main image for {search_query}: {type(e).__name__}: {e}"
    )
    return None

  return image_url

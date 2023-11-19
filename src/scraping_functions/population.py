from src.scraping_functions.population_dictionary import pop_dictionary
from src.scraping_functions.state_abbreviations import state_abbr

# USE THIS FUNCTION to get a city's population. Enter in string format the city name, and the state (abbreviated or
# full works)


def get_place_pop(city, state):
	if len(state) == 2:
		try:
			state = state_abbr[state]
		except KeyError:  # Catching specific exception for missing dictionary key
			return -1
	elif state not in state_abbr.values():
		return -1

	place = city + ", " + state

	if "Saint" in place:
		place = place.replace("Saint", "St.")

	try:
		population = pop_dictionary[place]
	except KeyError:  # Again, catching a specific exception for a missing key
		return -1

	return population

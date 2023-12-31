import asyncio
import json

import aiohttp
import requests
from geopy.distance import geodesic

from app.log_manager import global_logger as log

# @TODO update google map api key
API_KEY = "REDACTED"


def get_cities_list(origin: str, destination: str) -> dict[str, list]:
	"""Returns list of cities and their IDs in between origin and destination (inclusive)"""
	log.info(f"Fetching route from {origin} to {destination}")

	path = _get_coord_path(origin, destination)
	placeIDs = get_placeids_from_path(path)
	cities = asyncio.run(build_cities_list(placeIDs))

	return cities  # {cityA_id: [city,county,state], cityB_id: [city,county,state]}


def _get_coord_path(origin: str, destination: str) -> str:
	"""
	Calculate route and return as list of pipe delimited coordinate points.

	Parameters:
	origin (str): The starting point of the route.
	destination (str): The endpoint of the route.

	Returns:
	str: A string of pipe-delimited coordinates representing the route.

	Raises:
	APIError: If the Directions API returns an error status.
	"""
	url = f"https://maps.googleapis.com/maps/api/directions/json?origin={origin}&destination={destination}&key={API_KEY}"
	response = requests.get(url)
	route_response = response.json()

	if route_response["status"] != "OK":
		if route_response["status"] == "ZERO_RESULTS":
			trimmed_origin = simplify_city_name(origin)
			trimmed_destination = simplify_city_name(destination)

			if trimmed_origin != origin or trimmed_destination != destination:
				return _get_coord_path(trimmed_origin, trimmed_destination)

		raise APIError(f"Directions API Error: {route_response['status']}", url)

	# Extracts coordinates from the route steps
	legs = route_response["routes"][0]["legs"]
	path = "|".join(
		f"{step['end_location']['lat']},{step['end_location']['lng']}"
		for leg in legs
		for step in leg["steps"]
	)

	return path


def get_route_distance_meters(
	origin: str, destination: str, spangled: bool = False
) -> float:
	url = f"https://maps.googleapis.com/maps/api/directions/json?origin={origin}&destination={destination}&key={API_KEY}"
	response = requests.get(url)
	route_response = json.loads(response.text)

	if (status := route_response["status"]) != "OK":
		if status == "ZERO_RESULTS":
			n_origin = simplify_city_name(origin)
			n_destination = simplify_city_name(destination)

			if n_origin != origin or n_destination != destination:
				return get_route_distance_meters(n_origin, n_destination)

		log.critical(f"Directions API Error: {status}")
		raise APIError(f"Directions API returned status: {status}", url)

	legs = route_response["routes"][0]["legs"]

	total_distance_meters = sum([leg["distance"]["value"] for leg in legs])
	return (
		total_distance_meters if not spangled else total_distance_meters * 0.000621371
	)


def simplify_city_name(name: str) -> str:
	"""
	Simplifies city names by keeping only the first word before the comma.
	For example, converts 'Tampa Bay, FL' to 'Tampa, FL'.
	If there is no comma in the name, returns the original name.
	"""
	parts = name.split(",", 1)  # Split only at the first comma
	first_part = parts[0].split()[0]  # Take the first word before the comma

	return first_part + "," + parts[1] if len(parts) > 1 else name


async def build_cities_list(placeIDs: list[str]) -> dict:
	"""
	Asynchronously fetches city information for each place ID and trims duplicate entries.

	Args:
	placeIDs: A list of place IDs for which to fetch city information.

	Returns:
	A dictionary mapping place IDs to a list containing city, county, and state names.

	"""

	# Asynchronously fetch city information for each placeID
	city_info_futures = [get_city_from_id(placeID) for placeID in placeIDs]
	unfiltered_cities_list = await asyncio.gather(*city_info_futures)

	# Optimize duplicate trimming using a set for faster lookups
	seen_city_names = set()
	cities = {}
	for placeID, city_info in unfiltered_cities_list:
		if city_info and city_info[0] not in seen_city_names:
			seen_city_names.add(city_info[0])
			cities[placeID] = city_info

	return cities


async def get_city_from_id(placeID: str) -> tuple[str, list[str]]:
	"""Returns city name (ID, [City, County, State]) from given place ID"""
	url = f"https://maps.googleapis.com/maps/api/geocode/json?place_id={placeID}&key={API_KEY}"
	async with aiohttp.ClientSession() as session:
		async with session.get(url) as response:
			geocode_response = await response.json()

	if (status := geocode_response["status"]) != "OK":
		raise APIError(f"Geocoding API error for ID '{placeID}': {status}", url)

	return placeID, get_city_name(geocode_response["results"][0]["address_components"])


def get_placeids_from_path(path: str) -> list:
	"""
	Returns a list of place IDs from a given path of coordinates.
	Filters out closely spaced points (less than 5 km apart).
	"""
	place_response = fetch_snapped_points(path)
	if "warningMessage" in place_response:
		# Handle the warning appropriately, e.g., log it or alert the user
		handle_api_warning(place_response["warningMessage"])

	points = place_response.get("snappedPoints", [])
	placeIDs = filter_distant_points(points)

	return placeIDs


def fetch_snapped_points(path: str) -> dict:
	"""
	Fetches snapped points from Google Maps Snap-to-Roads API.
	"""
	url = f"https://roads.googleapis.com/v1/snapToRoads?path={path}&interpolate=true&key={API_KEY}"
	response = requests.get(url)
	if response.status_code != 200:
		# Handle non-200 responses here, e.g., by raising an exception
		raise APIError(
			f"API request failed with status code: {response.status_code}", url
		)
	return json.loads(response.text)


def filter_distant_points(points: list) -> list:
	"""
	Filters out points that are less than 5 km apart.
	"""
	placeIDs = []
	for i, point in enumerate(points):
		if (
			i == 0
			or get_point_distance(points[i - 1]["location"], point["location"]) > 5
		):
			placeIDs.append(point["placeId"])
	return placeIDs


def handle_api_warning(warning_message: str):
	# Implement the warning handling logic here
	# For example, log the warning message
	print(f"Warning Message from within `handle_api_warning`:\n{warning_message}")


def get_place_images(name: str, input_type: str = "name") -> list | None:
	"""Requests list of images for a place (name) from google."""

	log.info(f"Fetching images for {name}")

	url = "https://maps.googleapis.com/maps/api/place/"
	photos_path: str

	match input_type:
		case "name":
			url += f"findplacefromtext/json?input={name}&inputtype=textquery&fields=photo&key={API_KEY}"
			photos_path = "image_response['candidates'][0]['photos']"
		case "id":
			url += f"details/json?place_id={name}&fields=photo&key={API_KEY}"
			photos_path = "image_response['result']['photos']"
		case _:
			log.error(f"Invalid image search input type: {input_type}")
			return None

	image_response = json.loads(requests.get(url).text)

	if (status := image_response["status"]) != "OK":
		raise APIError(f"Image API returned status: {status}", url)

	photo_codes = eval(photos_path)
	photos = []

	base_url = "https://maps.googleapis.com/maps/api/place/photo?"
	for photo in photo_codes:
		url = (
			base_url
			+ f"photo_reference={photo['photo_reference']}&maxheight=1600&maxwidth=1600&key={API_KEY}"
		)

		photo_response = requests.get(url)
		if photo_response.status_code == 400:
			log.error(
				f"An unknown error occured grabbing image with reference {photo['photo_reference']}"
			)
		photos.append(photo_response.content)

	return photos


def get_nearby_activities(city: str) -> list[tuple[str, str]]:
	"""
	Gets list of nearby activities given a city name.
	Weird behavior, use with caution
	"""
	lat, lng = get_coordinates(city)
	url = f"https://maps.googleapis.com/maps/api/place/nearbysearch/json?location={lat},{lng}&radius=50000&type=tourist_attraction&key={API_KEY}"
	activity_list_response = json.loads(requests.get(url).text)

	if (status := activity_list_response["status"]) != "OK":
		log.critical(f"Nearby Search Error ({city}): {status}")
		raise APIError(f"Nearby Search API returned status: {status}", url)

	activities = []
	for activity in activity_list_response["results"]:
		activities.append((activity["name"], activity["place_id"]))

	return activities


def get_coordinates(city: str) -> tuple[float, float]:
	"""Returns tuple containing lat/lng coords of given city"""
	url = f"https://maps.googleapis.com/maps/api/place/findplacefromtext/json?input={city}&inputtype=textquery&fields=geometry&key={API_KEY}"
	city_id_response = json.loads(requests.get(url).text)

	if (status := city_id_response["status"]) != "OK":
		raise APIError(f"Place API returned status: {status}", url)

	location = city_id_response["candidates"][0]["geometry"]["location"]
	return (location["lat"], location["lng"])


def get_point_distance(
	coord1: tuple[float, float], coord2: tuple[float, float]
) -> float:
	"""
	Calculates the geodesic distance between two geographical points.

	Args:
	coord1: A tuple containing the latitude and longitude of the first point in decimal degrees.
	coord2: A tuple containing the latitude and longitude of the second point in decimal degrees.

	Returns:
	The distance between the two points in kilometers.

	Raises:
	ValueError: If the input coordinates are not in the correct format.
	"""
	try:
		dist = geodesic(coord1, coord2).km
		return dist
	except ValueError as e:
		raise ValueError(f"Invalid coordinate format: {e}")


def get_city_name(address_components: list[dict]) -> list[str] | None:
	"""
	Extracts city, county, and state names from address components.

	Args:
	    address_components: A list of dictionaries, each containing address details.

	Returns:
	    A list containing the city name, county name, and state name if available.
	    Returns None if either city or state name cannot be determined.

	Note:
	    Uses list comprehension and 'next' to efficiently find the required components.
	    'next' returns the first match or 'None' if not found.
	"""
	city_name = next(
		(cmp["long_name"] for cmp in address_components if "locality" in cmp["types"]),
		None,
	)
	state_name = next(
		(
			cmp["long_name"]
			for cmp in address_components
			if "administrative_area_level_1" in cmp["types"]
		),
		None,
	)
	county_name = next(
		(
			cmp["long_name"]
			for cmp in address_components
			if "administrative_area_level_2" in cmp["types"]
		),
		None,
	)

	if city_name and state_name:
		return [city_name, county_name, state_name]
	return None


class APIError(Exception):
	def __init__(self, message, endpoint):
		self.message = message
		self.endpoint = endpoint
		super().__init__(f"APIError: {self.message} URL: {self.endpoint}")

	def __str__(self):
		return f"{self.message} (Endpoint: {self.endpoint})"

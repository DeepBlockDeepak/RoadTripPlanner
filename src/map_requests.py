import requests
import json
import os
import time
import asyncio
import aiohttp
from geopy.distance import geodesic
from src.log_manager import global_logger as log

# @TODO update google map api key
API_KEY = "REDACTED"

def get_cities_list(origin: str, destination: str) -> dict[str, list]:
    """Returns list of cities and their IDs in between origin and destination (inclusive)"""
    log.info(f"Fetching route from {origin} to {destination}")

    path = _get_coord_path(origin, destination)
    placeIDs = _get_placeids_from_path(path)
    cities = asyncio.run(_build_cities_list(placeIDs))
        
    log.info("Done!")
    log.debug(f"Summary: {len(placeIDs)} placeIDs -> {len(cities)} unique cities.")

    return cities # {cityA_id: [city,county,state], cityB_id: [city,county,state]}


def _get_coord_path(origin: str, destination: str) -> str:
    """Calculate route and return as list of pipe delimited coordinate points"""
    log.debug(f"Building coordinate path from {origin} to {destination}")

    url = f"https://maps.googleapis.com/maps/api/directions/json?origin={origin}&destination={destination}&key={API_KEY}"
    route_response = json.loads(requests.get(url).text)

    if (status := route_response["status"]) != "OK":
        if status == "ZERO_RESULTS":
          n_origin = _trim_place_name(origin)
          n_destination = _trim_place_name(destination)

          if n_origin != origin or n_destination != destination:
            return _get_coord_path(n_origin, n_destination)
          
        log.critical(f"Directions API Error: {status}")
        raise APIError(f"Directions API returned status: {status}", url)

    legs = route_response["routes"][0]["legs"]

    # Constructs 'path' string to be passed to API - Contains coords of each step along route
    path = "|".join([f"{step['end_location']['lat']},{step['end_location']['lng']}" for leg in legs for step in leg['steps']])

    log.debug(f"Path string: \'{path}\'")
    return path

def get_route_distance_meters(origin: str, destination: str, spangled: bool=False) -> float:
    url = f"https://maps.googleapis.com/maps/api/directions/json?origin={origin}&destination={destination}&key={API_KEY}"
    response = requests.get(url)
    route_response = json.loads(response.text)

    if (status := route_response["status"]) != "OK":
        if status == "ZERO_RESULTS":
          n_origin = _trim_place_name(origin)
          n_destination = _trim_place_name(destination)
          
          if n_origin  != origin or n_destination != destination:
            return get_route_distance_meters(n_origin, n_destination)
            
        log.critical(f"Directions API Error: {status}")
        raise APIError(f"Directions API returned status: {status}", url)

    legs = route_response["routes"][0]["legs"]

    total_distance_meters = sum([leg["distance"]["value"] for leg in legs])
    return total_distance_meters if not spangled else total_distance_meters * 0.000621371

def _trim_place_name(name: str) -> str:
    """Removes subsequent words in city name (Tampa Bay, FL -> Tampa, FL)"""
    comma = name.find(",")
    space = name.find(" ")

    if space != -1 and space < comma:
        trimmed_name = name[:space] + name[comma:]
    else:
        trimmed_name = name
    
    log.info(f"Trimmed place name: \'{name}\' to \'{trimmed_name}\'")
    return trimmed_name


async def _build_cities_list(placeIDs: list[str]) -> list:
    """Calls _get_city_from_id asyncronously on all given place IDs to get city names, then trims duplicates"""
    log.info("Building cities list from placeIDs")
    unfiltered_cities_list = await asyncio.gather(*[_get_city_from_id(placeID) for placeID in placeIDs])
    
    log.debug("Trimming duplicate cities")
    
    # cities = {city: placeID for city, placeID in unfiltered_cities_list if city and city not in cities}
    cities = {}
    city_names = []
    for city in unfiltered_cities_list:
      if city and city[1]:
        if (city_name := city[1][0]) not in city_names:
            city_names.append(city_name)
            cities[city[0]] = city[1]

    return cities

async def _get_city_from_id(placeID: str, retry: int=0) -> tuple[str, str]:
    """Returns city name (name, ID) from given place ID"""

    url = f"https://maps.googleapis.com/maps/api/geocode/json?place_id={placeID}&key={API_KEY}"
    async with aiohttp.ClientSession() as session:
        async with session.get(url) as response:
            geocode_response = await response.json()

    if (status := geocode_response["status"]) != "OK":
        log.error(f"Geocoding error, skipping ID \'{placeID}\' with status: {status}")
        # raise APIError(f"Geocoding API error for ID \'{placeID}\': {status}", url)
        return None

    return (placeID, _get_city_name(geocode_response['results'][0]['address_components']))


def _get_placeids_from_path(path: str) -> list:
    """Returns list of placeIDs given list of coordinate points formatted as 'lat1,lng1|lat2,lng2|...' """
    log.info("Plotting route points")

    url = f"https://roads.googleapis.com/v1/snapToRoads?path={path}&interpolate=true&key={API_KEY}"
    place_response = json.loads(requests.get(url).text)

    if 'warningMessage' in place_response:
        log.warning(f"Snap-to-Roads API: {place_response['warningMessage']}")

    points = place_response['snappedPoints']

    log.info("Trimming closely spaced points")

    placeIDs = [points[0]['placeId']]  # Initializes list with first point
    first_loc = (points[0]['location']['latitude'],
                 points[0]['location']['longitude'])

    locations = [first_loc]

    # Iterates over the other points, checking distance to previous point
    for point in points[1:]:
        placeID = point['placeId']

        location = (point['location']['latitude'], 
                    point['location']['longitude'])

        if placeID not in placeIDs:
            point_distance = _get_point_distance(location, locations[-1])  # Comparing lat/lng of current point to lat/lng of current last element of final locations list

            if point_distance == -1:
                log.error(f"Point distance error: ID {placeID}")
                continue

            if point_distance > 5:
                placeIDs.append(placeID)
                locations.append(location)

    return placeIDs


def get_place_images(name: str, input_type: str = 'name') -> list | None:
    """Requests list of images for a place (name) from google."""

    log.info(f"Fetching images for {name}")

    url = "https://maps.googleapis.com/maps/api/place/"
    photos_path: str

    match input_type:
        case 'name':
            url += f"findplacefromtext/json?input={name}&inputtype=textquery&fields=photo&key={API_KEY}"
            photos_path = "image_response['candidates'][0]['photos']"
        case 'id':
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
        url = base_url + f"photo_reference={photo['photo_reference']}&maxheight=1600&maxwidth=1600&key={API_KEY}"

        photo_response = requests.get(url)
        if photo_response.status_code == 400:
            log.error(f"An unknown error occured grabbing image with reference {photo['photo_reference']}")
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

    if (status := activity_list_response['status']) != "OK":
        log.critical(f"Nearby Search Error ({city}): {status}")
        raise APIError(f"Nearby Search API returned status: {status}", url)

    activities = []
    for activity in activity_list_response['results']:
        activities.append((activity['name'], activity['place_id']))

    return activities


def get_coordinates(city: str) -> tuple[float, float]:
    """Returns tuple containing lat/lng coords of given city"""
    url = f"https://maps.googleapis.com/maps/api/place/findplacefromtext/json?input={city}&inputtype=textquery&fields=geometry&key={API_KEY}"
    city_id_response = json.loads(requests.get(url).text)

    if (status := city_id_response["status"]) != "OK":
        raise APIError(f"Place API returned status: {status}", url)

    location = city_id_response['candidates'][0]['geometry']['location']
    return (location['lat'], location['lng'])


def _get_point_distance(coord1: tuple[float, float], coord2: tuple[float, float]) -> float:
    """Accepts 2 tuples (lat,lng) and returns distance between them in km"""
    dist = geodesic(coord1, coord2).km
    return dist


def _get_city_name(address_components: list[dict]) -> list[str] | None:
    """Returns name of place as [City, County, State]" only if both components exist"""
    city_name: str = None
    state_name: str = None
    county_name: str = None

    for cmp in address_components:
        if 'types' not in cmp: 
            log.error("'types' field not present in address component")
            continue

        if 'locality' in cmp['types']:
            city_name = cmp['long_name']
        elif 'administrative_area_level_1' in cmp['types']:
            state_name = cmp['long_name']
        elif 'administrative_area_level_2' in cmp['types']:
            county_name = cmp['long_name']

    if city_name and state_name:
        if not county_name:
            log.warning(f"Unknown county for \'{city_name, state_name}\'")
        return [city_name, county_name, state_name]  # Typical return
    else:
        log.error(f"Unknown city element: \'{city_name if city_name else '-'}\', \'{county_name if county_name else '-'}\', \'{state_name if state_name else '-'}\'")
        return None  # No match found (Unknown city)


def time_function(func, *args):
    """Accepts a function and its arguments, prints out execution time and returns function's return value(s)"""
    start_time = time.time()
    values = func(*args)
    end_time = time.time()

    print(f"Function {func.__name__} executed in {round(end_time - start_time, 3)} seconds.")
    return values
 

def _test_route() -> None:
    origin = "Socorro, New Mexico"
    destination = "New York City, New York"

    print(f"Running route test from \'{origin}\' to \'{destination}\'...")
    cities = get_cities_list(origin, destination)

    if cities != None:
        print("Response:")
        print("\n".join([f"{city[0]}, {city[1]}, {city[2]}" for city in cities.values()]))


def _test_images() -> None:
    photo_source = "Microsoft Headquarters, Redmond, WA"
    
    print(f"Retrieving photos for {photo_source}")
    photos = get_place_images(photo_source)
    if photos != None:
        print(f"Found {len(photos)} pictures")
        i = 1
        for photo in photos:
            with open(f'photo_{i}.jpg', 'wb') as file:
                file.write(photo)


class APIError(ValueError):
    def __init__(self, msg, endpoint):
        self.endpoint = endpoint
        self.msg = msg
        super().__init__(self.msg)
    
    def __str__(self):
        return str(self.msg)


if __name__ == "__main__":
    # Test module
    time_function(_test_route)
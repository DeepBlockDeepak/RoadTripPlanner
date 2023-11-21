import time
from src.map_requests import get_cities_list


def timing(func):
	"""Decorator to measure execution time of a function."""

	def wrapper(*args, **kwargs):
		start_time = time.time()
		result = func(*args, **kwargs)
		end_time = time.time()
		print(
			f"Function {func.__name__} executed in {round(end_time - start_time, 3)} seconds."
		)
		return result

	return wrapper


@timing
def test_route():
	"""Test for the route functionality."""
	origin = "Socorro, New Mexico"
	destination = "New York City, New York"

	print(f"Testing route from '{origin}' to '{destination}'...")
	cities = get_cities_list(origin, destination)

	if cities:
		print("Test Response:")
		print(
			"\n".join([f"{city[0]}, {city[1]}, {city[2]}" for city in cities.values()])
		)


if __name__ == "__main__":
	test_route()

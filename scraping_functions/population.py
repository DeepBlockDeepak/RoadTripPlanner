import csv
from scraping_functions.population_dictionary import pop_dictionary
from scraping_functions.state_abbreviations import state_abbr
from log_manager import global_logger as log


# USE THIS FUNCTION to get a city's population. Enter in string format the city name, and the state (abbreviated or
# full works)
def get_place_pop(city, state):
  if len(state) == 2:
    try:
      state = state_abbr[state]
    except:
      return -1
  elif not (state in state_abbr.values()):
    return -1

  place = city + ", " + state

  if "Saint" in place:
    place = place.replace("Saint", "St.")

  try:
    population = pop_dictionary[place]
  except:
    return -1

  return population


# DO NOT USE: Legacy function that reads in CSV file to get population
def get_city_pop(city, state):
  with open("./scraping_functions/clean_us_pop.csv", "r") as file:
    csvreader = csv.reader(file)
    for row in csvreader:
      if (city == row[0]) and (state == row[1]):
        return row[2]
      else:
        continue

  return "Population Not Found"


# Used to parse data from CSV. Creates list from us.csv Only needed when population data had been updated from the csv file.
def get_population():
  country_population = []
  with open("./scraping_functions/us.csv", "r") as file:
    csvreader = csv.reader(file)
    counter = 0
    for row in csvreader:
      if counter == 0:
        counter = 1

      else:
        place = [None] * 3
        row[0] = row[0].replace("village", "")
        row[0] = row[0].replace("city and borough", "")
        row[0] = row[0].replace("town", "")
        row[0] = row[0].replace("city", "")
        row[0] = row[0].replace("corporation", "")
        row[0] = row[0].replace("borough", "")
        row[0] = row[0].replace("municipality", "")
        city_state = row[0].split(" , ")

        place[0] = city_state[0]
        place[1] = city_state[1]
        place[2] = row[3]
        country_population.append(place)

  for obj in country_population:
    print(obj)
    print("\n")

  return country_population


# Creates cleaned up list of city population from clean_us_pop.csv
def create_clean(city_list):
  with open('./scraping_functions/clean_us_pop.csv', 'w', newline='') as file:
    writer = csv.writer(file)
    writer.writerows(city_list)


if __name__ == '__main__':
  print(get_place_pop("Trinidad", "CO"))

from statistics import mean

from src.scraping_functions.gas import Gas
from src.scraping_functions.state_abbreviations import state_abbr


def obtain_avg_gas_price():
	"""
	Finds the average gas price and returns it
	"""

	g = Gas()

	states = [s.lower() for s in state_abbr.values()]

	str_prices = list(map(g.getPrice, states))

	# filters out locations like Washington D.C. which don't have gas prices
	str_prices = [float(s) for s in str_prices if s]

	return round(mean(str_prices), 2)


def get_gas_average():
	states = state_abbr.values()
	average = 0.0
	gas = Gas()

	for state in states:
		state = state.lower()
		# print(state)
		output = gas.getPrice(state)
		if output:
			output = float(output)
			# print(output)
			average = average + output
	average = round(average / 50, 2)
	return average

#!python3
# accessing openai's API with developer account
import openai

from src.chat_gpt_tools.open_ai_api_config import API_KEY  # from api file


class SumChatGPT:
	# use LRU_Cache to store user_prompt -> gpt_responses?
	def __init__(self) -> None:
		self.api_key = openai.api_key = API_KEY
		self.chatgpt_responses = []  # for storing the responses

		self.prompt_to_response_map = {}  # lookup the mapping {prompt:response}

		self.origin_city_state = ""  # store the current user's origin
		self.destination_city_state = ""
		self.user_prompt = ""  # user's origin and dest will init the formatted prompt for sending to ChatGPT
		self.information = ""

	# store the user's input into the Class's formatted user_prompt attr
	def init_prompt(self) -> None:
		self.user_prompt = (
			f"{self.destination_city_state}"
			+ " is a location on a road trip."
			+ "Based on the following information, summarize important things a traveler/tourist can do in this city. Highlight main attactions they can see or other interesting facts about the place. Return NULL if there is no data. Information:\n"
			+ f"{self.information}"
		)

	# queries ChatGPT with the formatted user prompt
	def obtain_chatGPT_response(self, user_prompt) -> None:
		completion = openai.Completion.create(
			engine="text-davinci-003", prompt=user_prompt, max_tokens=1000
		)

		chatgpt_response = completion.choices[0]["text"]

		# store the response, and map the user's prompt to this response
		self.chatgpt_responses.append(chatgpt_response)
		self.prompt_to_response_map[user_prompt] = chatgpt_response

	# Obtains the most recent ChatGPT response
	def get_most_recent_response_string(self) -> str:
		return self.chatgpt_responses[-1]

	# Wrapps important funtions into one simple request
	def gptWrapper(self, destination, scrape_info):
		self.destination_city_state = destination
		self.information = scrape_info
		self.init_prompt()
		self.obtain_chatGPT_response(self.user_prompt)
		return self.get_most_recent_response_string()

#!python3
# accessing openai's API with developer account
from gpt import SumChatGPT
from postprocess import postWrapper

if __name__ == "__main__":
	chatgpt = SumChatGPT()

	place, data = postWrapper("data.txt")

	# print(place)
	# print(data)

	output = chatgpt.gptWrapper(place, data)
	print(output)

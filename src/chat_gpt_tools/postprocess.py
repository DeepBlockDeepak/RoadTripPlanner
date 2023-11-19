import tiktoken

# Postproccesing functions to help with formating scraped data


def token_count(string: str, encoding_name: str) -> int:
	encoding = tiktoken.get_encoding(encoding_name)
	num_tokens = len(encoding.encode(string))
	return num_tokens


def token_refactor(token_count, text):
	return None


def place_grab(file_name):
	with open(file_name, "rt", encoding="utf-8") as file:
		return file.readline()
		# print(file.readline())


def info_grab(file_name):
	lines = []
	flag = False

	with open(file_name, "rt", encoding="utf-8") as file:
		for line in file:
			if line.strip().startswith("Raw Result--------:"):
				flag = not flag
			if flag:
				if "== History ==" in line.strip():
					break
				lines.append(line)

	data = "".join(lines)
	return data


def postWrapper(file_name):
	place = place_grab(file_name)
	data = info_grab(file_name)
	return place, data

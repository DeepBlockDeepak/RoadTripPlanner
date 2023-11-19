import wikipedia
import re


def get_wikiheader_regex(level):
    '''The top wikiheader level has two = signs, so add 1 to the level to get the correct number.'''
    assert isinstance(level, int) and level > -1
    header_regex = f"^={{{level+1}}}\s(?P<section>.*?)\s={{{level+1}}}$"

    return header_regex

def get_toc(raw_page, level=1):
    '''For a single raw wiki page, return the level 1 section headers as a table of contents.'''
    toc = []
    header_regex = get_wikiheader_regex(level=level)
    for line in raw_page.splitlines():
        if line.startswith('=') and re.search(header_regex, line):
            toc.append(re.search(header_regex, line).group('section'))

    return toc



page = wikipedia.page("Albert Einstein")
text = page.content
# using the number 2 for '=' means you can easily find sub-headers too by increasing the value 
regex_result = re.findall("\n={2}\s(?P<header>.+?)\s={2}\n", text)

print(
    get_toc(text)
)


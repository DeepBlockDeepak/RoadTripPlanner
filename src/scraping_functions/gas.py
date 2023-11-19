import requests
from bs4 import BeautifulSoup


class Gas:
  def __init__(self):
    self.lookup_state = {"data":[]}
    self.URL = "https://www.gasbuddy.com/usa"
    self.page = ""
    
    page = requests.get(self.URL)
    soup = BeautifulSoup(page.content, "html.parser")
    state_attrib = soup.find_all("div", class_="col-sm-12 col-xs-12")
    
    for state in state_attrib:
      name = state.find("div", class_="col-sm-6 col-xs-6 siteName")
      price = state.find("div", class_="col-sm-2 col-xs-3 text-right")
      self.lookup_state[name.text.strip().lower()] = price.text.strip().lower()

  def getPrice(self, state):
    value = self.lookup_state.get(state.lower())
    return value

    
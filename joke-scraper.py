import requests
import pandas as pd
import matplotlib.pyplot as plt
from bs4 import BeautifulSoup, Tag
import sys

page = requests.get("https://bestlifeonline.com/knock-knock-jokes/")
soup = BeautifulSoup(page.content, 'html.parser')
all_lists = soup.findAll('li')

jokes = []

for lst in all_lists:
    strongs = lst.findAll('strong')
    if strongs:
        jokes.append([strong.contents[0] for strong in strongs[1:]])


with open('knock-knock.txt', 'w+') as f:
    for joke in jokes:
        if joke and not isinstance(joke[0], Tag) and not isinstance(joke[1], Tag):
            joke = [joke[0].strip().replace('.', ''), joke[1].strip().replace('.', '')]
            f.write("{} | {}\n".format(*joke))
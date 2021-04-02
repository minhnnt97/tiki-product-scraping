# SCRAPER FUNCTIONS

import requests
import time
import random as rd
from bs4 import BeautifulSoup as bs

url = 'https://tiki.vn/hang-quoc-te/c17166?'

def get_url(url):
    """Get parsed HTML from url
      Input: url to the webpage
      Output: Parsed HTML text of the webpage
    """

    page_num = 1
    url += f'&page={page_num}'
    r = requests.get(url)
    time.sleep(rd.randint(5)) # Sleep randomly to avoid trouble

    # Parse HTML text
    soup = BeautifulSoup(r.text, 'html.parser')
    return soup

def get_products(url):
    pass

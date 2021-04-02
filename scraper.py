# SCRAPER FUNCTIONS

import requests
from bs4 import BeautifulSoup as bs


def get_url(url):
    """Get parsed HTML from url
      Input: url to the webpage
      Output: Parsed HTML text of the webpage
    """
    # Send GET request
    r = requests.get(url)

    # Parse HTML text
    soup = BeautifulSoup(r.text, 'html.parser')
    return soup

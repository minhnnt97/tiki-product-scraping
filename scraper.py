# SCRAPER FUNCTIONS

import requests
from bs4 import BeautifulSoup as bs


def get_url(url):
    """Get parsed HTML from url
      Input: url to the webpage
      Output: Parsed HTML text of the webpage
    """
    page_num = 1
    url += '&page={page_num}'
    r = requests.get(url)

    # Parse HTML text
    soup = BeautifulSoup(r.text, 'html.parser')
    return soup

def get_products(url):


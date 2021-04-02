# SCRAPER FUNCTIONS

import requests
import time
import random as rd
from bs4 import BeautifulSoup as bs

INTERNATIONAL_GOODS_URL = 'https://tiki.vn/hang-quoc-te/c17166?'

def get_url(url):
    """Get parsed HTML from url
      Input: url to the webpage
      Output: Parsed HTML text of the webpage
    """
    
    header = {'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/70.0.3538.77 Safari/537.36'}
    r = requests.get(url, headers=header)
    time.sleep(rd.randint(3,6)) # Sleep randomly to avoid trouble

    # Parse HTML text
    soup = bs(r.text, 'html.parser')
    return soup

def get_products(url=INTERNATIONAL_GOODS_URL):
    page_num = 1
    url += f'&page={page_num}'
    print(url)
    product_page = get_url(url)

    products = product_page.find_all('a',{'class':'product-item'})
    return products



### Check if this script is run by itself (compared to being imported)
if __name__ == '__main__':
    print(get_products())

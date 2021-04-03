# SCRAPER FUNCTIONS

### IMPORTS ###
import requests
import time
import random as rd
import pandas as pd
from bs4 import BeautifulSoup as bs


### GLOBALS ###
HEADER = {'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/70.0.3538.77 Safari/537.36'}
URL_SMART_DEVICES = 'https://tiki.vn/dien-thoai-may-tinh-bang/c1789?'
URL_INTERNATIONAL_GOODS = 'https://tiki.vn/hang-quoc-te/c17166?'


### FUNCTIONS ###
def get_url(url):
    """
    Get parsed HTML from url
      
    Input: url to the webpage
    Output: Parsed HTML text of the webpage
    """
    
    time.sleep(rd.randint(5,10)) # Sleep randomly to avoid trouble
    r = requests.get(url, headers=HEADER)

    # Parse HTML text
    soup = bs(r.text, 'html.parser')
    return soup


def get_page(url=URL_INTERNATIONAL_GOODS,page_num=1):
    '''
    Scrape for products on one page.

    Input:  url: (string) url of a category
            page_num: (int) the page number of the category
    Output: a list of HTML element of each product.
    '''
    page_url = url + f'page={page_num}'
    print(page_url)
    product_page = get_url(page_url)
    
    tags = [ 'a',
            { 'class' : 'product-item' } ]

    products = product_page.find_all(*tags)
    return products


def get_all_pages(url=URL_INTERNATIONAL_GOODS):
    '''
    Scrape for multiple pages of products of a category.
    Uses the function get_page() for each page.

    Input: url: (string) url of a category
    Output: a dictionary with format { page_number : get_page(url,page_number) }
    '''
    page_n = 1
    prod = get_page(page_num=page_n)
    products = {}

    while len(prod)>0: # BUG: This check is not working since tiki.vn apparently gives the same list of products when scraping different pages, including (supposedly) empty pages.
        products[page_n] = prod
        page_n += 1
        prod = get_page(page_num=page_n)
    
    return products


def get_product_info(html_ele):
    pass


### Check if this script is run by itself (compared to being imported)
if __name__ == '__main__':
    print(get_page(url=URL_SMART_DEVICES,page_num=2)[2])

    ''' Check if data from different pages are dupes '''
    # page2 = get_page(page_num=2)[2]
    # page3 = get_page(page_num=3)[2]
    # for i,(p2,p3) in enumerate(zip(page2,page3)):
    #     if p2 != p3:
    #         print(i)


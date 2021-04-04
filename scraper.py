# SCRAPER FUNCTIONS

### IMPORTS ###
import requests
import time
import re
import random as rd
import pandas as pd
from bs4 import BeautifulSoup as bs
from selenium import webdriver
from webdriver_manager.chrome import ChromeDriverManager


### GLOBALS ###
HEADER = {'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/70.0.3538.77 Safari/537.36'}
URL_TIKI = 'https://tiki.vn'
URL_SMART_DEVICES = URL_TIKI + '/dien-thoai-may-tinh-bang/c1789?'
URL_INTERNATIONAL_GOODS = URL_TIKI + '/hang-quoc-te/c17166?'


### FUNCTIONS ###
def get_url(url):
    """
    Get parsed HTML from url
      
    Input: url to the webpage
    Output: Parsed HTML text of the webpage
    """

    # Setting up the driver
    options = webdriver.ChromeOptions()
    options.add_argument('-headless') # we don't want a chrome browser opens, so it will run in the background
    options.add_argument('-no-sandbox')
    options.add_argument('-disable-dev-shm-usage')

    driver = webdriver.Chrome('chromedriver',options=options)
    driver.implicitly_wait(30)
    time.sleep(rd.randint(4,6))
    driver.get(url)
    
    soup = bs(driver.page_source,'html.parser')
    driver.close()
    return soup


def get_page(url=URL_INTERNATIONAL_GOODS, page_num=1):
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
            { 'class' : 'product-item'} ]

    products = product_page.find_all(*tags)
    return products


def get_product_info(product):
    product_info = {}

    product_info['product_url'] = URL_TIKI + product['href']
    product_info['name'] = product.find('div', {'class','name'}).span.text
    product_info['image_url'] = product.find('img',{'alt':product_info['name']})['src']
    price = product.find('div', {'class','price-discount__price'}).text
    product_info['price'] = ''.join(re.findall(r'\d+',price))

    return product_info


# HAVEN'T TESTED THIS YET
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

    while len(prod)>0:
        products[page_n] = prod
        page_n += 1
        prod = get_page(page_num=page_n)
    
    return products


### Check if this script is run by itself (compared to being imported)
if __name__ == '__main__':
    page_n = rd.randint(1,5)
    prod_n = rd.randint(1,5)
    prod_page = get_page(url=URL_SMART_DEVICES, page_num=page_n)[prod_n]
    
    print(prod_page)
    print(get_product_info(prod_page))



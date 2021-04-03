# SCRAPER FUNCTIONS

import requests
import time
import random as rd
from bs4 import BeautifulSoup as bs

SMART_DEVICES_URL = 'https://tiki.vn/dien-thoai-may-tinh-bang/c1789?'
INTERNATIONAL_GOODS_URL = SMART_DEVICES_URL #'https://tiki.vn/hang-quoc-te/c17166?'

def get_url(url):
    """Get parsed HTML from url
      Input: url to the webpage
      Output: Parsed HTML text of the webpage
    """
    
    header = {'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/70.0.3538.77 Safari/537.36'}
    time.sleep(rd.randint(5,10)) # Sleep randomly to avoid trouble
    r = requests.get(url, headers=header)

    # Parse HTML text
    soup = bs(r.text, 'html.parser')
    return soup

def get_page(url=INTERNATIONAL_GOODS_URL,page_num=1):
    page_url = url + f'page={page_num}'
    print(page_url)
    product_page = get_url(page_url)

    products = product_page.find_all('script',{'type':'application/ld+json'})
    #product_list = product_page.find('div',{'data-view-id':'product_list_container'})
    #products = product_list.find_all('a',{'class':'product-item'})
    return products

def get_all_pages(url=INTERNATIONAL_GOODS_URL):
    prod = get_page()
    products = [prod]
    page_n = 2
    while len(prod)>0:
        prod = get_page(page_num=page_n)
        products.extend(prod)
        page_n += 1
    
    return products



### Check if this script is run by itself (compared to being imported)
if __name__ == '__main__':
    page2 = get_page(page_num=2)[2]
    page3 = get_page(page_num=3)[2]
    for i,(p2,p3) in enumerate(zip(page2,page3)):
        if p2 != p3:
            print(i)

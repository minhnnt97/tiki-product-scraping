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

# URLS
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
    time.sleep(rd.randint(4,6)) # Not sure if this line is needed anymore
    driver.get(url)
    
    soup = bs(driver.page_source,'html.parser')
    driver.close()
    return soup


def get_page(url, page_num=1):
    '''
    Scrape for products on one page.

    Input:  url: (string) url of a category
            page_num: (int) the page number of the category
    Output: a list of HTML element of each product.
    '''
    page_url = url + f'page={page_num}'
    print('Scraping', page_url)
    product_page = get_url(page_url)
    
    tags = [ 'a',
            { 'class' : 'product-item'} ]

    products = product_page.find_all(*tags)
    return products


# Might expand this for a list of products
def get_product_info(product):
    '''
    Extract information from an html element of one product tag.

    Input: a BeautifulSoup object of the product tag
    Output: a dictionary of the information of the products
    '''
    product_info = {}

    # Product URL
    if product['href'][:2] == '//':
        product_info['Product URL'] = 'https:' + product['href']
    else:
        product_info['Product URL'] = URL_TIKI + product['href']

    # Image URL
    thumbnail = product.find('div',{'class':'thumbnail'})
    product_info['Image URL'] = thumbnail.img['src']
    
    # Freeship?
    item_top = thumbnail.span
    if item_top and item_top.text == 'Freeship':
        product_info['Freeship'] = 'Yes'
    else:
        product_info['Freeship'] = 'No'

    # Product ID
    product_info['Product ID'] = int(re.search(r'.+-p(\d+).html.*', product['href']).group(1))

    # Name
    product_info['Name'] = product.find('div', {'class','name'}).span.text

    # Price
    price = product.find('div',{'class','price-discount__price'}).text
    product_info['Price'] = int(''.join(re.findall(r'\d+',price)))

    # Discount percent
    discount = product.find('div', {'class','price-discount__discount'})
    if discount:
        product_info['Discount Percentage'] = int(re.search(r'(\d+)',discount.text).group(0))
    else:
        product_info['Discount Percentage'] = 0

    # Ratings & Reviews
    rating_review = product.find('div',{'class','rating-review'})
    try:
        rating = rating_review.find('div',{'class','rating__average'})
        product_info['Rating'] = (int(re.search(r'^width: (\d+)%;$',rating['style']).group(1))/100)*5
    except:
        product_info['Rating'] = 0 

    try:
        review = rating_review.find('div',{'class','review'})
        product_info['Reviews'] = int(re.search(r'(\d+)',review.text).group(0))
    except:
        product_info['Reviews'] = 0

    # Badge under price
    under_price = product.find('div', {'class':'badge-under-price'}).div
    if under_price:
        product_info['Badge Under Price'] = 'Yes'
    else:
        product_info['Badge Under Price'] = 'No'

    # Paid by installments
    installments = product.find('div', {'class':'badge-benefits'}).img
    if installments:
        product_info['Paid by Installments'] = 'Yes'
    else:
        product_info['Paid by Installments'] = 'No'

    # Free Gifts
    free_gifts = product.find('div', {'class':'freegift-list'})
    if free_gifts:
        product_info['Free Gifts'] = 'Yes'
    else:
        product_info['Free Gifts'] = 'No'


    return product_info


def get_multiple_pages(url, max_page=0):
    '''
    Scrape for multiple pages of products of a category.
    Uses get_page() and get_product_info().

    Input:  url: (string) a url string of a category
            max_page: (int) an integer denoting the maximum number of pages to scrape.
                      Default value is 0 to scrape all pages.
    Output: a list in which every element is a dictionary of one product's information
    '''
    products = []

    page_n = 1
    prod_list = get_page(url=url, page_num=page_n)

    while len(prod_list)>0:
        products.extend([get_product_info(prod) for prod in prod_list])
        page_n += 1
        stop_flag = False if max_page <= 0 else page_n > max_page # For stopping the scrape according to max_page
        if stop_flag:
            break
        prod_list = get_page(url=url, page_num=page_n)
    
    return products


### Check if this script is run by itself (compared to being imported)
if __name__ == '__main__':
    num_max_page = 5
    my_url = URL_INTERNATIONAL_GOODS

    prod_data = get_multiple_pages(url=my_url, max_page=num_max_page)
    df = pd.DataFrame(data=prod_data, columns=prod_data[0].keys())
    df.to_csv('tiki_products_data_table.csv')

# to_csv function
def to_csv(my_url = URL_INTERNATIONAL_GOODS, num_max_page = 5, name='tiki_products_data_table.csv'):
  prod_data = get_multiple_pages(url=my_url, max_page=num_max_page)
  df = pd.DataFrame(data=prod_data, columns=prod_data[0].keys())
  df.to_csv(name)
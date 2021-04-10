### IMPORTS ###
import requests
import time
import re
import json
import sqlite3
import random as rd
import pandas as pd
from bs4 import BeautifulSoup as bs
from selenium import webdriver
from webdriver_manager.chrome import ChromeDriverManager


### GLOBALS ###
HEADER = {'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/70.0.3538.77 Safari/537.36'}

# URLS
MAIN_CATEGORIES = [
    {'Name': 'Điện Thoại - Máy Tính Bảng', 'URL': 'https://tiki.vn/dien-thoai-may-tinh-bang/c1789?src=c.1789.hamburger_menu_fly_out_banner'},
    {'Name': 'Điện Tử - Điện Lạnh', 'URL': 'https://tiki.vn/tivi-thiet-bi-nghe-nhin/c4221?src=c.4221.hamburger_menu_fly_out_banner'}, 
    {'Name': 'Phụ Kiện - Thiết Bị Số', 'URL': 'https://tiki.vn/thiet-bi-kts-phu-kien-so/c1815?src=c.1815.hamburger_menu_fly_out_banner'},
    {'Name': 'Laptop - Thiết bị IT', 'URL': 'https://tiki.vn/laptop-may-vi-tinh/c1846?src=c.1846.hamburger_menu_fly_out_banner'},
    {'Name': 'Máy Ảnh - Quay Phim', 'URL': 'https://tiki.vn/may-anh/c1801?src=c.1801.hamburger_menu_fly_out_banner'}, 
    {'Name': 'Điện Gia Dụng', 'URL': 'https://tiki.vn/dien-gia-dung/c1882?src=c.1882.hamburger_menu_fly_out_banner'}, 
    {'Name': 'Nhà Cửa Đời Sống', 'URL': 'https://tiki.vn/nha-cua-doi-song/c1883?src=c.1883.hamburger_menu_fly_out_banner'}, 
    {'Name': 'Hàng Tiêu Dùng - Thực Phẩm', 'URL': 'https://tiki.vn/bach-hoa-online/c4384?src=c.4384.hamburger_menu_fly_out_banner'}, 
    {'Name': 'Đồ chơi, Mẹ & Bé', 'URL': 'https://tiki.vn/me-va-be/c2549?src=c.2549.hamburger_menu_fly_out_banner'},
    {'Name': 'Làm Đẹp - Sức Khỏe', 'URL': 'https://tiki.vn/lam-dep-suc-khoe/c1520?src=c.1520.hamburger_menu_fly_out_banner'},
    {'Name': 'Thể Thao - Dã Ngoại', 'URL': 'https://tiki.vn/the-thao/c1975?src=c.1975.hamburger_menu_fly_out_banner'},
    {'Name': 'Xe Máy, Ô tô, Xe Đạp', 'URL': 'https://tiki.vn/o-to-xe-may-xe-dap/c8594?src=c.8594.hamburger_menu_fly_out_banner'},
    {'Name': 'Hàng quốc tế', 'URL': 'https://tiki.vn/hang-quoc-te/c17166?src=c.17166.hamburger_menu_fly_out_banner'}, 
    {'Name': 'Sách, VPP & Quà Tặng', 'URL': 'https://tiki.vn/nha-sach-tiki/c8322?src=c.8322.hamburger_menu_fly_out_banner'}, 
    {'Name': 'Voucher - Dịch Vụ - Thẻ Cào', 'URL': 'https://tiki.vn/voucher-dich-vu/c11312?src=c.11312.hamburger_menu_fly_out_banner'}]

MAIN_CATEGORIES = MAIN_CATEGORIES[:9]


### GLOBAL FUNCTIONS ###
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

###### CATEGORY CLASS ######
class Category:
    def __init__(self, name, url, parent_id=None, cat_id=None):
        self.cat_id     = cat_id
        self.name       = name
        self.url        = url
        self.parent_id  = parent_id

    def __repr__(self):
        return f"ID: {self.cat_id}, Name: {self.name}, URL: {self.url}, Parent: {self.parent_id}"

    def save_into_db(self):
        query = """
            INSERT INTO categories (name, url, parent_id)
            VALUES (?, ?, ?);
        """
        val = (self.name, self.url, self.parent_id)
        try:
            cur.execute(query, val)
            self.cat_id = cur.lastrowid
            conn.commit()
        except Exception as err:
            print('ERROR BY INSERT:', err)

    def get_page(self, page_num):
        '''
        Scrape for products on one page.
    
        Input:  url: (string) url of a category
                page_num: (int) the page number of the category
        Output: a list of HTML element of each product.
        '''
        page_url = self.url + f'page={page_num}'
        print('Scraping', page_url)
        product_page = get_url(page_url)
        
        tags = [ 'a',
                { 'class' : 'product-item'} ]
    
        products = product_page.find_all(*tags)
        return products
    
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

###### PRODUCT CLASS ######
class Product:
    def __init__(self, cat_id, name, price, product_url, image, tiki_now, freeship, review, under_price, discount, installment, gift, product_sku, rating):
        self.cat_id      = cat_id
        self.url         = product_url
        self.name        = name
        self.image       = image
        self.tiki_now    = tiki_now
        self.freeship    = freeship
        self.review      = review
        self.under_price = under_price
        self.discount    = discount
        self.installment = installment
        self.gift        = gift
        self.product_sku = product_sku
        self.rating      = rating

    def __repr__(self):
        return f"Name: {self.name}, SKU: {self.product_sku}, URL: {self.url}, Category: {self.cat_id}"

    def extract_tiki_info(url):
        """ Extract info from all products of a specfic category on Tiki website
            Input: url
            Output: info of products, saved as list of dictionary. If no products shown, return empty list.
        """
        data = []
        index = 1
        soup = get_url(url)
    
        # FIND ALL PRODUCT ITEMS
        products = soup.find_all('a', {'class':'product-item'})
        all_script = soup.find_all('script', {'type':'application/ld+json'})
        print("BATCH SIZE:", len(products))
    
        if (soup.find('div', {'class':'style__StyledNotFoundProductView-sc-1uz0b49-0'})):
            print("END PAGE")
        elif len(products):
            # EXTRACT INFO TO DICTIONARY
            for i in products: 
                d = {'name':'','price':'','product_url':'','image':'', 'product_sku':'',
                   'tiki_now':'','freeship':'','review':'','rating':'','under_price':'',
                   'discount':'','installment':'','gift':''}
              
                try:
                    d['name']         = i.find('div',{'class' : 'name'}).text
                    d['price']        = int(re.sub('[. ₫]','', i.find('div',{'class':'price-discount__price'}).text))
                    d['product_url']  = 'https://tiki.vn' + i['href'] 
                    thumbnail         = i.find('div',{'class':'thumbnail'})
                    d['image']        = thumbnail.img['src']        
                    d['tiki_now']     = bool(i.find('div',{'class':'badge-service'}).find('div',{'class':'item'})) 
                    d['freeship']     = bool(i.find('div',{'class':'badge-top'}).text == "Freeship")
                    
                    if i.find('div',{'class':'review'}):
                        d['review']   = int(i.find('div',{'class':'review'}).text.strip('(').strip(')'))
                    else:
                        d['review'] = "N/A"
                    
                    d['under_price']  = bool(i.find('div',{'class':'badge-under-price'}).find('div',{'class':'item'}))
    
                    if i.find('div', {'class':'price-discount__discount'}):
                        d['discount'] = int(re.sub('[-%]','', i.find('div',{'class':'price-discount__discount'}).text))
                    else:
                        d['discount'] = "N/A"
                    
                    d['installment']  = bool(i.find('div',{'class':'badge-benefits'}).img)
                    d['gift']         = bool(i.find('div',{'class':'freegift-list'}))
    
                    script = all_script[index]
                    dict_content = json.loads(script.text)
                    d['product_sku']  = dict_content['sku']
                    
                    if 'aggregateRating' in dict_content:
                        d['rating']   = float(dict_content['aggregateRating']['ratingValue'])
                    else:
                      d['rating']     = "N/A"
    
                except Exception as e:
                    print(e)
    
                index += 1
                data.append(d)
              
        return data
    def save_into_db(self):
        query = """
            INSERT INTO products (cat_id, url, name, image, tiki_now, freeship, review, under_price, discount, installment, gift, product_sku, rating)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?);
        """
        val = (self.cat_id, self.url, self.name, self.image, self.tiki_now, self.freeship, self.review, self.under_price, self.discount, self.installment, self.gift, self.product_sku, self.rating)
        try:
            cur.execute(query, val)
            self.cat_id = cur.lastrowid
            conn.commit()
        except Exception as err:
            print('ERROR BY INSERT:', err)







# to_csv function
def make_csv(my_url = URL_INTERNATIONAL_GOODS, num_max_page = 5, name='tiki_products_data_table.csv'):
    prod_data = get_multiple_pages(url=my_url, max_page=num_max_page)
    df = pd.DataFrame(data=prod_data, columns=prod_data[0].keys())
    df.to_csv(name)


### Check if this script is run by itself (compared to being imported)
if __name__ == '__main__':
    num_max_page = 5
    my_url = URL_INTERNATIONAL_GOODS

    prod_data = get_multiple_pages(url=my_url, max_page=num_max_page)
    df = pd.DataFrame(data=prod_data, columns=prod_data[0].keys())
    df.to_csv('tiki_products_data_table.csv')


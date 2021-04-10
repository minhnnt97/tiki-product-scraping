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

MAIN_CATEGORIES = MAIN_CATEGORIES[:3]
CATEGORY_SET = set()
PRODUCT_SET = set()


################## GLOBAL FUNCTIONS ##################
def create_categories_table():
    query = """
        CREATE TABLE IF NOT EXISTS categories (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            name VARCHAR(255),
            url TEXT, 
            parent_id INTEGER, 
            create_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )
    """
    try:
        cur.execute(query)
        conn.commit()
    except Exception as err:
        print('ERROR BY CREATE TABLE', err)

def create_products_table():
    query = """
        CREATE TABLE IF NOT EXISTS products (
            ID          INTEGER PRIMARY KEY AUTOINCREMENT,
            cat_id      INTEGER,
            Name        VARCHAR(255),
            Price       INTEGER,
            URL         TEXT, 
            Image       TEXT,
            SKU         INTEGER,
            Tiki_Now    BOOLEAN,
            Freeship    BOOLEAN,
            Review      INTEGER,
            Rating      FLOAT,
            Under_Price BOOLEAN,
            Discount    INTEGER,
            Installment BOOLEAN,
            Gift        BOOLEAN,
            Created_At  TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )
    """
    try:
        cur.execute(query)
        conn.commit()
    except Exception as err:
        print('ERROR BY CREATE TABLE', err)

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

def get_lowest_subcat():
    query = '''
    
    SELECT A.id, A.name, A.url
    FROM Categories A
        LEFT JOIN Categories B ON A.id = B.parent_id
    
        WHERE B.id IS NULL
    
    '''
    return pd.read_sql_query(query, conn)

##################################################################
######################## CATEGORY CLASS ########################
##################################################################

class Category:
    def __init__(self, Name, URL, cat_id=None, parent_id=None):
        self.name       = Name
        self.url        = URL
        self.cat_id     = cat_id
        self.parent_id  = parent_id

    def __repr__(self):
        return f"ID: {self.cat_id}, Name: {self.name}, URL: {self.url}, Parent: {self.parent_id}"
    
    def __eq__(self,other):
        return  self.name       == other.name and\
                self.URL        == other.URL and\
                self.cat_id     == other.cat_id and\
                self.parent_id  == other.parent_id


    def can_add_to_cat_set(self,save=False):
        if self.name not in CATEGORY_SET:
            if save:
                CATEGORY_SET.add(self.name)
                print(f'Added "{self.name}" to CATEGORY_SET')
            return True
        return False


    def get_main_cat(self):
        main_cat_id = re.search(r'src=c\.(\d+)', self.url).group(1)
        pattern = f'c{main_cat_id}?src=c.{main_cat_id}'
        for main_cat in MAIN_CATEGORIES:
            if pattern in main_cat['URL']:
                return Category(**main_cat)


    def get_product_info(self, max_page=0, save=False):
        """ Extract info from all products of a specfic category on Tiki website
            Input: url
            Output: info of products, saved as list of dictionary. If no products shown, return empty list.
        """
        data = []
        index = 1
        soup = get_url(self.url)
    
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
                        d['review']   = "N/A"
                    
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
                        d['rating']   = "N/A"
    
                except Exception as e:
                    print(e)
    
                index += 1
                prod = Product(self.cat_id, **d)
                if save and prod.can_add_to_prod_set(save=save):
                    prod.save_into_db()
                data.append(prod)
              
        return data


    def scrape_tiki(self, max_page=0):
        base_url = self.url

        result = []
        page_number = 1
        main, opt = base_url.split('?')
        
        stop_flag = False if max_page <= 0 else page_number > max_page # For stopping the scrape at max_page

        while not stop_flag:
            page = f'?page={page_number}&'
            url = main + page + opt
            print("url =", url)
            data = get_product_info(url)

            if len(data)>0:
                result.extend(data)
            else:
                break

            page_number += 1
            sleep(rd.randint(1,2))
    
        print("****TOTAL = ",len(result))


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

##################################################################


##################################################################
######################## PRODUCT CLASS ########################
##################################################################

class Product:
    def __init__(self, cat_id, name, price, product_url, image, product_sku, tiki_now, freeship, review, rating, under_price, discount, installment, gift):
        self.cat_id      = cat_id
        self.name        = name
        self.price       = price
        self.url         = product_url
        self.image       = image
        self.product_sku = product_sku
        self.tiki_now    = tiki_now
        self.freeship    = freeship
        self.review      = review
        self.rating      = rating
        self.under_price = under_price
        self.discount    = discount
        self.installment = installment
        self.gift        = gift

    def __repr__(self):
        return f"Name: {self.name}, SKU: {self.product_sku}, URL: {self.url}, Category: {self.cat_id}"

    def can_add_to_prod_set(self,save=False):
        if self.product_sku not in PRODUCT_SET:
            if save:
                PRODUCT_SET.add(self.product_sku)
                print(f'Added "{self.product_sku}" to PRODUCT_SET')
            return True
        return False

    def save_into_db(self):
        query = """
            INSERT INTO products (cat_id, name, price, product_url, image, product_sku, tiki_now, freeship, review, rating, under_price, discount, installment, gift)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?);
        """
        val = (self.cat_id, self.name, self.price, self.url, self.image, self.product_sku, self.tiki_now, self.freeship, self.review, self.rating, self.under_price, self.discount, self.installment, self.gift)
        try:
            cur.execute(query, val)
            self.cat_id = cur.lastrowid
            conn.commit()
        except Exception as err:
            print('ERROR BY INSERT:', err)

##################################################################






####################################################################
############################### MAIN ###############################
####################################################################

if __name__ == '__main__':
    db_path = './tiki_2.db'

    conn = sqlite3.connect(db_path)
    cur = conn.cursor()
    
    # Do database stuff here


    conn.close()

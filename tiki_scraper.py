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

limit = 3
MAIN_CATEGORIES = MAIN_CATEGORIES[:limit]


################## GLOBAL FUNCTIONS ##################
def create_categories_table(conn, cur):
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

def create_products_table(conn, cur):
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

def drop_table(table_name, conn, cur):
    print(f'Dropping table {table_name} from database...')
    cur.execute(f'DROP TABLE {table_name};')
    conn.commit()

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
    driver.get(url)
    
    soup = bs(driver.page_source,'html.parser')
    driver.close()
    return soup

def get_lowest_subcat(conn):
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
    CATEGORY_SET = set()

    def __init__(self, Name, URL, cat_id=None, parent_id=None):
        self.name       = Name
        self.url        = URL
        self.cat_id     = cat_id
        self.parent_id  = parent_id

    def __repr__(self):
        return f"ID: {self.cat_id}, Name: {self.name}, URL: {self.url}, Parent: {self.parent_id}"
    
    def __eq__(self,other):
        return  self.name       == other.name and\
                self.url        == other.url and\
                self.cat_id     == other.cat_id and\
                self.parent_id  == other.parent_id

    def __ne__(self,other):
        return not self.__eq__(other)

    def __hash__(self):
        return hash((self.name, self.url))

    def can_add_to_cat_set(self,save=False):
        if self not in Category.CATEGORY_SET:
            if save:
                Category.CATEGORY_SET.add(self)
                print(f'Added "{self.name}" to CATEGORY_SET')
            return True
        return False


    def get_main_cat(self):
        main_cat_id = re.search(r'src=c\.(\d+)', self.url).group(1)
        pattern = f'c{main_cat_id}?src=c.{main_cat_id}'
        for main_cat in MAIN_CATEGORIES:
            if pattern in main_cat['URL']:
                return Category(**main_cat)


    def get_sub_cat(self,conn,cur, save=False):
        parent_url = self.url
        result = []
    
        try:
            soup = get_url(parent_url)
            sub_cat_list = soup.find_all('a', class_='item item--category')
            for a in sub_cat_list:
                name = a.text.strip()
                sub_url = a['href']
                cat = Category(name, sub_url, parent_id=self.cat_id) # parent_id is cat_id of parent category

                if cat.can_add_to_cat_set(save=save) and save:
                    cat.save_into_db(conn, cur)

                result.append(cat)

        except Exception as err:
            print('ERROR IN GETTING SUB CATEGORIES:', err)
        return result


    @staticmethod
    def get_main_categories(main_categories,conn,cur, save=False):
        for i in main_categories:
            main_cat = Category(i['Name'],i['URL'])
            _=main_cat.can_add_to_cat_set(save=save)

            if save:
                main_cat.save_into_db(conn,cur)

    @staticmethod
    def get_all_categories(conn, cur, save=False):
        categories = list(Category.CATEGORY_SET)
        while len(categories):
            cat_to_crawl = categories[0]

            print(f'Getting sub-categories of {cat_to_crawl}...')
            sub_categories = cat_to_crawl.get_sub_cat(conn, cur, save=save)

            print(f'Finished! {cat_to_crawl.name} has {len(sub_categories)} sub-categories')
            categories += sub_categories

            del categories[0]


    def get_product_info(self,conn,cur, save=False):
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
                    dict_content = json.loads(script.string)
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
                    prod.save_into_db(conn, cur)
                data.append(prod)
              
        return data


    def scrape_all_products(self,conn,cur, save=False, max_page=0):
        base_url = self.url

        result = []
        page_number = 1
        main, opt = base_url.split('?')
        

        while True:
            page = f'?page={page_number}&'
            url = main + page + opt
            print("url =", url)
            data = self.get_product_info(conn, cur, save=save)

            stop_flag = False if max_page <= 0 else page_number > max_page # For stopping the scrape at max_page
            if stop_flag or len(data)<=0:
                break

            result.extend(data)

            page_number += 1
            time.sleep(rd.randint(1,2))
    
        print("****TOTAL = ",len(result))

    @staticmethod
    def scrape_all_categories(conn, cur, save=False, max_page=0):
        for cat in Category.CATEGORY_SET:
            cat.scrape_all_products(conn, cur, save=save, max_page=max_page)

    def save_into_db(self, conn, cur):
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
    PRODUCT_SET = set()

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

    def __eq__(self,other):
        return self.product_sku == other.product_sku

    def __ne__(self,other):
        return not self.__eq__(other)

    def __hash__(self):
        return hash((self.product_sku))

    def can_add_to_prod_set(self,save=False):
        if self not in Product.PRODUCT_SET:
            if save:
                Product.PRODUCT_SET.add(self)
                print(f'Added "{self.product_sku}" to PRODUCT_SET')
            return True
        return False

    def save_into_db(self,conn,cur):
        query = """
            INSERT INTO products (cat_id, Name, Price, URL, Image, SKU, Tiki_Now, Freeship, Review, Rating, Under_Price, Discount, Installment, Gift)
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
    pass

from selenium import webdriver
from webdriver_manager.chrome import ChromeDriverManager
# Set driver for Chrome
options = webdriver.ChromeOptions()
options.add_argument('-headless') # since we run selenium on Google Colab so we don't want a chrome browser opens, so it will run in the background
options.add_argument('-no-sandbox')
options.add_argument('-disable-dev-shm-usage')
options.add_argument("--incognito")
from bs4 import BeautifulSoup

def selenium_scrap(tiki_url, page):
  driver = webdriver.Chrome('chromedriver',options=options)        # Define the chrome drivers with setting options we define above  
  driver.implicitly_wait(30)                                       # We let selenium to wait for 30 seconds for all javascript script done before return the result of HTML
  tiki_url += f'page={page}'                                   
  driver.get(tiki_url)                                             # Open the browser again to get web page
  html_data = driver.page_source                                   # After driver.get() is done, you can get back HTML string by using .page_source
  driver.close()                                                   # Close the driver after retrieving the web page
  soup = BeautifulSoup(html_data, 'html.parser')                   # do your beautifulsoup business like the usual
  return soup

def get_products(url):
  page = 1                                        
  all_products = {}
  while True:
    soup = selenium_scrap(url, page)                 
    products = soup.find_all('a', {'class':'product-item'})
    # p = {'name':'', 'url':'', 'img':'', 'product-id':'', 'price':''}
    p = {}
    p['name'] = products['name']
    p['url'] = products['href']
    p['img'] = products.img['src']
    p['price'] = products.find('div', {'class': 'price-discount__price'})
    all_products[page] = p
    page += 1
    if len(products) == 0:
      return p

url = 'https://tiki.vn/hang-quoc-te/c17166?'
get_products(url)

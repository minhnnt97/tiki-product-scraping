# !pip install selenium
# !apt install chromium-chromedriver
# !cp /usr/lib/chromium-browser/chromedriver /usr/bin
# !pip install webdriver-manager
from selenium import webdriver
from webdriver_manager.chrome import ChromeDriverManager
from bs4 import BeautifulSoup

def selenium_scrap(url, page):
  # Set driver for Chrome
  options = webdriver.ChromeOptions()
  options.add_argument('-headless') # since we run selenium on Google Colab so we don't want a chrome browser opens, so it will run in the background
  options.add_argument('-no-sandbox')
  options.add_argument('-disable-dev-shm-usage')
  options.add_argument("--incognito")

  driver = webdriver.Chrome('chromedriver',options=options)        # Define the chrome drivers with setting options we define above  
  driver.implicitly_wait(30)                                       # We let selenium to wait for 30 seconds for all javascript script done before return the result of HTML
  tiki_url = url + 'page={page}'                                   
  driver.get(tiki_url)                                             # Open the browser again to get web page
  html_data = driver.page_source                                   # After driver.get() is done, you can get back HTML string by using .page_source
  driver.close()                                                   # Close the driver after retrieving the web page
  soup = BeautifulSoup(html_data, 'html.parser')                   # do your beautifulsoup business like the usual
  return soup

def get_products(url):
  page = 1                                        
  all_products = {}
  while True:
    try:
      soup = selenium_scrap(url, page)                 
      products = soup.find_all('a', {'class':'product-item'})
      # p = {'name':'', 'url':'', 'img':'', 'product-id':'', 'price':''}
      product_info = dict({})
      product_info['Name'] = products['name']
      product_info['Url'] = products['href']
      product_info['Img'] = products.img['src']
      product_info['Price'] = products.find('div', {'class': 'price-discount__price'})
      all_products[page] = product_info #unclear why this doesn't work
      page += 1
    except:
      print("error")
    if len(products) == 0:
      return p

url = 'https://tiki.vn/hang-quoc-te/c17166?'
get_products(url)
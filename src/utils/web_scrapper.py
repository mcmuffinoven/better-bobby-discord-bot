from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.by import By

from babel.numbers import parse_decimal, get_currency_symbol
import re
import locale
from datetime import datetime

from product import Product


# """General Use
# 1. User gives a website 
# 2. Inserts the category
# 3. User can choose an amount to alert them on. (Or just alert when price drops)
# 4. Create new objects for the items 
# 5. Push into database 
# 6. Periodically, check against the website and database 
# 7. If lower, update database, and alert user.
# 8. Else, wait until next check period. 
# """
import sys
sys.path.append('../')

class WebScrapper:
    # Define Chrome Options
	chrome_options = Options()
	chrome_options.add_argument('--no-sandbox')
	chrome_options.add_argument('--disable-dev-shm-usage')
	# Ignore SSL error when selenium makes handshake with chrome. 
	chrome_options.add_argument('--ignore-certificate-errors-spki-list')
	# chrome_options.add_argument('--headless')
	chrome_options.add_argument('--log-level=3')
	decimal_point_char = locale.localeconv()['decimal_point']
 
	def __init__(self):
		self.browser = webdriver.Chrome(options=WebScrapper.chrome_options)
		# url to scrape
		self.__scrape_url = ""
		self.retry_limit = 5
  

	def load_browser(self):
		# Load browser
		self.browser.get(self.__scrape_url)


	@staticmethod
	def check_support_url(scrape_url:str):
		# Dict of all supported links
  
		valid_url_dict = {
			"Amazon": {
							"product_price": "/html/body/div[2]/div/div[7]/div[4]/div[4]/div[12]/div/div/div[1]/div/div[3]/div[1]/span[3]/span[2]/span[2]/text()",
							"product_name": "/html/body/div[2]/div/div[7]/div[4]/div[4]/div[1]/div/h1/span[1]/text()"
            },
			"Best Buy": {
       						"product_price": "/html/body/div[1]/div/div[2]/div[3]/section[4]/div[1]/div/div[1]/span/div/div",
                			"product_name":'//*[@id="root"]/div/div[2]/div[3]/section[3]/div[1]/h1'
                   		}
   }
  
		# Not en efficient way, when there are many supported urls
		if scrape_url.find("amazon") != -1:
			value = valid_url_dict["Amazon"]
		elif scrape_url.find("bestbuy") != -1:
			value = valid_url_dict["Best Buy"]

		
		if value:
			return value
		else:
			raise Exception("URL is not supported!")
   
	def find_element(self, attribute, value):

		retry = 0	
		while retry <= self.retry_limit:
			try:
				# print("printing", self.browser.find_element(attribute, value))
				element = self.browser.find_element(attribute, value).get_attribute("innerHTML")
				break
			except Exception as e:
				print(e)
				retry += 1
				continue
		if not element:
			raise Exception("Element not found from given XPATH. Check if XPATH is correct")
		
		return element
   
	def get_product_current_price(self):
		# self.browser.get(self.__scrape_url)
		XPATH = WebScrapper.check_support_url(self.__scrape_url)['product_price']
		retry = 0
		product_price_raw = 0
		while retry <= self.retry_limit:
			try:
				product_price_raw = self.find_element(attribute=By.XPATH, value=XPATH)
				break
			except Exception as e:
				print(e)
				retry += 1
				continue
			
  
		# Strip everything except decimal and digit, then convert to float
		product_price = float(re.sub(r'[^0-9'+self.decimal_point_char+r']+', '', product_price_raw))
		if product_price == 0:
			raise Exception("Failed to find product price. Please check XPATH.")
		return product_price
  
	# Might not be needed, since the user could provide an alias 
	def get_product_name(self):
		# self.browser.get(self.__scrape_url)

		XPATH = WebScrapper.check_support_url(self.__scrape_url)['product_name']
		product_name = ""
		retry = 0
		while retry <= self.retry_limit:
			try:
				product_name = self.find_element(attribute=By.XPATH, value=XPATH)
				break
			except Exception as e:
				print(e)
				retry += 1
				continue
  
		# self.browser.close()
  
		if not product_name:
			raise Exception("Product name not found. Please check HTML value is correct.")
		
		return product_name
  
  
	def set_scrape_url(self, url):
		self.__scrape_url = url

	def get_scrape_url(self):
		return self.__scrape_url
  
	def scrape_product_data(self, product_category, product_url, user_id):
		self.set_scrape_url(product_url)
		self.load_browser()
      
		# Only applicable for the first time
		# This should be changed
		# Check database if this item has been added. Otherwise only fetch for current price. 
  

		product = Product()
		product.product_category = product_category
		product.product_url = product_url
		product.product_user_id = user_id
		product.product_start_price = self.get_product_current_price()
		product.product_cur_price = self.get_product_current_price()
		product.product_lowest_price = self.get_product_current_price()
		product.product_name = self.get_product_name()

		product.product_lowest_price_date = datetime.now().strftime("%Y-%m-%d")
		product.product_tracked_since_date = datetime.now().strftime("%Y-%m-%d")
		

		self.terminate_session()
		
		return product
  
	def terminate_session(self):
		self.browser.quit()


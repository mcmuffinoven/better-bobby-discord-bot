from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.by import By

from babel.numbers import parse_decimal, get_currency_symbol
import re
import locale


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
 
	def __init__(self, scrape_url):
		self.browser = webdriver.Chrome(options=WebScrapper.chrome_options)
		# url to scrape
		self.scrape_url = scrape_url
		# Load browser on instantiation
		self.browser.get(self.scrape_url)
		self.retry_limit = 5
  
	@staticmethod
	def check_support_url(scrape_url:str):
		# Dict of all supported links
  
		valid_url_dict = {
			"Amazon": "",
			"Best Buy": {
       						"product_price": ".//span[@data-automation='product-price']/span"
                			,"product_name":"productName_2KoPa"
                   		}
   }
  
		# Not en efficient way, when there are many supported urls
		if scrape_url.find("amazon") != -1:
			XPATH = valid_url_dict["Amazon"]
		elif scrape_url.find("bestbuy") != -1:
			XPATH = valid_url_dict["Best Buy"]
  
		if XPATH:
			return XPATH
		else:
			raise Exception("URL is not supported!")
   
	def find_XPATH(self, XPATH):

		retry = 0	
		while retry <= self.retry_limit:
			try:
				element = self.browser.find_element(By.XPATH, XPATH).get_attribute("innerHTML")
				break
			except Exception as e:
				print(e)
				retry += 1
				continue
				
		return element
   
	def get_product_current_price(self):
		# self.browser.get(self.scrape_url)
		XPATH = WebScrapper.check_support_url(self.scrape_url)['product_price']

		retry = 0
		while retry <= self.retry_limit:
			try:
				product_price_raw = self.find_XPATH(XPATH)
				break
			except Exception as e:
				print(e)
				retry += 1
				continue
			
  
		# Strip everything except decimal and digit, then convert to float
		product_price = float(re.sub(r'[^0-9'+self.decimal_point_char+r']+', '', product_price_raw))
	
		return product_price
  
	# Might not be needed, since the user could provide an alias 
	def get_product_name(self):
		# self.browser.get(self.scrape_url)

		XPATH = WebScrapper.check_support_url(self.scrape_url)['product_name']

		retry = 0
		while retry <= self.retry_limit:
			try:
				product_name = self.find_XPATH(XPATH)
				break
			except Exception as e:
				print(e)
				retry += 1
				continue
  
		print(product_name)
		# self.browser.close()
  
	def terminate_session(self):
		self.browser.quit()


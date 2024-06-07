from selenium import webdriver
from selenium.webdriver.firefox.options import Options
from selenium.webdriver.common.by import By
from selenium.webdriver.firefox.service import Service
from selenium.webdriver.support.wait import WebDriverWait

import re
import locale
import logging
import atexit

from typing import Self

import sys
sys.path.append('../')
log = logging.getLogger(__name__)

class WebScrapper:
	'''
	WebScrapper class contains methods used for setting up Selenium and scrapping the web
	Note: Firefox-esr is the browser being used along with geckodriver.
		  Chrome cannot be used as arm7 does not currently have official support
	'''

	# Define Firefox Service
	service = Service('/usr/bin/geckodriver') # CHANGE THIS IF NECASSARY. Binary location of the geckodriver.

	# Define Firefox Options
	firefox_options = Options()
	firefox_options.binary_location = r'/usr/bin/firefox-esr' # CHANGE THIS IF NECASSARY. Binary location of the firefox browser.
	firefox_options.add_argument('--headless') # Hides the browser
	decimal_point_char = locale.localeconv()['decimal_point']

	def __init__(self):
		self.browser = webdriver.Firefox(service=WebScrapper.service, options=WebScrapper.firefox_options)
		self.__scrape_url = ""
		self.retry_limit = 2
		# Terminate the browser on exit to prevent memory leaks
		atexit.register(self.terminate_browser)

	def begin_scrape(func):
		'''
		Decorator for general webscrapping
		1. Sets the url to scrape
		2. Loads the browser to scrape

		Note: Browser cannot be terminated until the function returns, hence it is not included in the decorator
		'''
		def command(self:Self, *args, **kwargs):
			self.set_scrape_url(args[0])
			self.load_browser()
			result = func(self,args[0])
			return result
		return command

	def terminate_browser(self):
		try:
			self.browser.quit()
		except Exception as e:
			log.error(e)

	def close_browser(self):
		try:
			self.browser.close()
		except Exception as e:
			log.error(e)

	def load_browser(self):
		try:
			self.browser.get(self.__scrape_url)
		except Exception as e:
			log.error(e)

	def set_scrape_url(self, url):
		self.__scrape_url = url

	def get_scrape_url(self):
		return self.__scrape_url

	@staticmethod
	def check_support_url(scrape_url:str):
		'''
		Verifies the url against the list of currently supported urls

		Args:
			scrape_url (str): url to be scrapped

		Returns:
			value (dict): dictionary containing XPATHs for currently support websites
		'''

		# Move these to a separate file eventually
		valid_url_dict = {
			"Amazon": {
							"product_price": "/html/body/div[2]/div/div[7]/div[4]/div[4]/div[12]/div/div/div[1]/div/div[3]/div[1]/span[3]/span[2]/span[2]/text()",
							"product_name": "/html/body/div[2]/div/div[7]/div[4]/div[4]/div[1]/div/h1/span[1]/text()"
			},
			"Best Buy": {
	   						"product_price": "/html/body/div[1]/div/div[2]/div[3]/section[4]/div[1]/div/div[1]/span/div/div",
							"product_name":'/html/body/div[1]/div/div[2]/div[3]/section[3]/div[1]/h1'
				   		}
   }

		# Not en efficient way, if there are many supported urls (Use match case)
		if scrape_url.find("amazon") != -1:
			value = valid_url_dict["Amazon"]
		elif scrape_url.find("bestbuy") != -1:
			value = valid_url_dict["Best Buy"]


		if value:
			return value
		else:
			log.error("URL is not supported!")
			raise Exception("URL is not supported!")

	def find_element(self, attribute:By, value:str):
		'''
		Scrapes the current browser for a given attribute and value

		Args:
			attribute (selenium.webdriver.common.by): By class from selenium (XPATH, CSS, CLASS, etc)
			value (str): Value of the attribute to scrape by. E.g. (For XPATH attribute, value = /html/body/div[1])

		Returns:
			element : element scrapped
		'''
		retry = 0
		while retry <= self.retry_limit:
			try:
				element = WebDriverWait(self.browser, 10).until(lambda x: x.find_element(attribute, value)).get_attribute("innerHTML")
				break
			except Exception as e:
				log.error(e)
				retry += 1
				continue
		if not element:
			raise Exception("Element not found from given XPATH. Check if XPATH is correct")

		return element

	@begin_scrape
	def get_product_current_price(self, product_url):
		'''
		Scrapes for the current price of the product from the product_url

		Args:
			product_url (str): url of product to be scrapped

		Returns:
			product_price (float): price of the product
		'''
		XPATH = WebScrapper.check_support_url(self.__scrape_url)['product_price']
		retry = 0
		product_price_raw = 0
		while retry <= self.retry_limit:
			try:
				product_price_raw = self.find_element(attribute=By.XPATH, value=XPATH)
				break
			except Exception as e:
				log.error(e)
				retry += 1
				continue


		# Strip everything except decimal and digit, then convert to float
		product_price = float(re.sub(r'[^0-9'+self.decimal_point_char+r']+', '', product_price_raw))
		if product_price == 0:
			raise Exception("Failed to find product price. Please check XPATH.")
		return product_price

	@begin_scrape
	def get_product_name(self, product_url):
		'''
		Scrapes for the name of the product from the product_url

		Args:
			product_url (str): url of product to be scrapped

		Returns:
			product_name (str): name of the product
		'''

		XPATH = WebScrapper.check_support_url(self.__scrape_url)['product_name']
		product_name = ""
		retry = 0
		while retry <= self.retry_limit:
			try:
				product_name = self.find_element(attribute=By.XPATH, value=XPATH)
				break
			except Exception as e:
				log.error(e)
				retry += 1
				continue

		if not product_name:
			raise Exception("Product name not found. Please check HTML value is correct.")

		return product_name


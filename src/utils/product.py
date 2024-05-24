# Product class
# Product details 
# Product Auto Fetching
# Product logic to check sales
from datetime import datetime
from utils.web_scrapper import WebScrapper
from utils.postgres import Postgres

# import discord
# from discord.ext import commands
# from bot import CustomContext
from enum import Enum

class Product_category(Enum):
    TECH = 1
    GROCERY = 2
    FASHION = 3
    COSEMETICS = 4
    
class Product():
    @staticmethod
    def create_product(value, properties):
        product = Product()
        
        for property_name, value in zip(properties,value):
            setattr(product, "product_"+property_name, value)
            
        return product
    
    def __init__(self):
        self.product_user_id = None
        self.product_category = None
        self.product_name = None
        self.product_start_price = None
        self.product_cur_price = None
        self.product_lowest_price = None
        self.product_lowest_price_date = None
        self.product_tracked_since_date = None
        self.product_url = None
        self.product_sale_bool = None
        
        # # Scrape Related Functions
        # self.product_name = WebScrapper.get_product_name()
        # self.product_start_price = WebScrapper.get_product_current_price()
        # self.product_cur_price = WebScrapper.get_product_current_price()
        # self.product_lowest_price, self.product_lowest_price_date = self.get_lowest_price()
        # self.product_sale = self.is_product_sale()


    def scrape_product(self, product_category, product_url, user_id):
        # Create a scrapper to scrape for the current product details
        scrapper = WebScrapper()
        
        initial_price = scrapper.get_product_current_price(product_url)
        current_date = datetime.now().strftime("%Y-%m-%d")
        
        self.product_category = product_category
        self.product_url = product_url
        self.product_user_id = user_id
        self.product_start_price = initial_price
        self.product_cur_price = initial_price
        self.product_lowest_price = initial_price
        self.product_name = scrapper.get_product_name(product_url)

        self.product_lowest_price_date = current_date
        self.product_tracked_since_date = current_date
        
        # Can't terminate browser before returing the data. Need to do it after
        scrapper.terminate_browser()
    
    def is_product_sale(self):

        scrapper = WebScrapper()
        scraped_curr_price = scrapper.get_product_current_price(self.product_url)

        if int(self.product_cur_price) > int(scraped_curr_price):
            db = Postgres()
            db.update_product_info()
            return True

        else:
            return False
        
    
    def get_lowest_price(self):
        # 1. Get Current Price 
        # 2. Check Database for lowest price
        # 3. Return Lowest
        return
    
    
            
        
        
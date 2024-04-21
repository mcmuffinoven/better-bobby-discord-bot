# Product class
# Product details 
# Product Auto Fetching
# Product logic to check sales
from datetime import datetime
from utils.web_scrapper import WebScrapper

import discord
from discord.ext import commands
from bot import CustomContext
from enum import Enum

class Product_category(Enum):
    TECH = 1
    GROCERY = 2
    FASHION = 3
    COSEMETICS = 4
    
class Product():
    def __init__(self, product_category, product_link, user_id=None):
        # self.user_id = user_id
        self.product_category = product_category
        self.product_link = product_link
        self.product_tracked_date = datetime.now()
        
        # Scrape Related Functions
        self.product_name = WebScrapper.get_product_name()
        self.product_starting_price = WebScrapper.get_product_current_price()
        self.product_current_price = WebScrapper.get_product_current_price()
        self.product_lowest_price, self.product_lowest_price_date = self.get_lowest_price()
        self.product_sale = self.is_product_sale()
        
    def is_product_sale(self):
        # 1. Get Current Price 
        # 2. Check database of latest price 
        # 3. Check if lower
        return
    
    def get_lowest_price(self):
        # 1. Get Current Price 
        # 2. Check Database for lowest price
        # 3. Return Lowest
        return
    
            
        
        
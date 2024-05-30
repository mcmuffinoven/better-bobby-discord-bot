from datetime import datetime
from utils.web_scrapper import WebScrapper
from utils.postgres import Postgres

from enum import Enum

class Product_category(Enum):
    TECH = 1
    GROCERY = 2
    FASHION = 3
    COSEMETICS = 4

class Product():
    '''
    Product class to hold attributes related to a product
    '''

    @staticmethod
    def create_product(value, properties):
        '''
        Used to convert data fetched back from database into a Product object
        '''
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

    def scrape_product(self, product_category:str, product_url:str, user_id:int):
        '''
        Scrapes details related to the product from a url

        Args:
            product_category (str): Category of the product
            product_url (str): url to be scrapped
            user_id (int): id of the user that made the request

        '''
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

        self.product_lowest_price_date = current_date # This needs to be changed later
        self.product_tracked_since_date = current_date

    def is_product_sale(self):
        '''
        Checks if the current product is on sale

        Args:
            None

        Returns:
            bool: True if product is on sale, False otherwise
        '''

        scrapper = WebScrapper()
        scraped_curr_price = scrapper.get_product_current_price(self.product_url)

        if int(self.product_cur_price) > int(scraped_curr_price):
            db = Postgres(filename="utils/db_info.ini", section="postgres")
            db.update_product_info()
            return True

        else:
            return False


    def get_lowest_price(self):
        # 1. Get Current Price
        # 2. Check Database for lowest price
        # 3. Return Lowest
        return





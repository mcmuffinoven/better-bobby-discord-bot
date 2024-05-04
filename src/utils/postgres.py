# Postgres Connection Class

# ----- Imports ----- #
import psycopg
from psycopg import OperationalError
from utils.db_parser import get_db_info
from datetime import datetime
from utils.web_scrapper import WebScrapper
import logging
# from schedule import every, repeat, run_pending

log = logging.getLogger(__name__)

class Postgres():
    # Class defaults for products
    default_table_name = "products"
    users_table = "users"
    
    def __init__(self, filename='db_info.ini', section='postgres'):
        params = get_db_info(filename,section)
        try:
            self.connection = psycopg.connect(**params)
            log.info("Successfully connected to the database.")

        except OperationalError:
            log.info("Error connecting to the database :/")
        pass

    
    @staticmethod
    def generic_insert(connection, query, parameters):
        
        with connection.cursor() as cur:

            try:
                cur.execute(query,(*parameters,))
            
            except Exception as error:
                print ("Oops! An exception has occured:", error)
                print ("Exception TYPE:", type(error))
                            
            connection.commit()
        return
    
    @staticmethod
    def generic_fetch(connection, query, parameters):
        data = None
        with connection.cursor() as cur:
            try:
                # print(query, parameters)
                cur.execute(query,(*parameters,))
                data = cur.fetchall()
                colnames = [desc[0] for desc in cur.description]
            except Exception as error:
                print ("Oops! An exception has occured:", error)
                print ("Exception TYPE:", type(error))
        return data, colnames

    # ----- Create  ----- #
    def insert_user(self, user_id):
        query = f"""
                    INSERT INTO {Postgres.users_table}
                    (user_id) values (%s) ON CONFLICT DO NOTHING;
        """
        print("Inserting user", user_id)
        Postgres.generic_insert(connection=self.connection, query=query, parameters=[user_id])
        return
    
    # Add new product
    def insert_product(self, product_category, product_url, user_id):
        scrapper = WebScrapper()
        product = scrapper.scrape_product_data(product_category=product_category, product_url=product_url, user_id=user_id)
        
        query = f"""
            insert into {self.default_table_name} (
            fk_user_id,
            category,
            product_name,
            starting_product_price,
            current_product_price,
            lowest_product_price,
            lowest_product_price_date,
            tracked_since_date,
            product_link,
            sale_bool
            )
            values ((SELECT id from users where user_id=%s),%s, %s, %s, %s, %s, %s, %s, %s, %s);
            """
        
        # Parse Data
        fk_user_id = product.product_user_id   
        category = product.product_category    
        product_name = product.product_name       
        product_link = product.product_url
        prod_start_price = product.product_start_price
        prod_cur_price = product.product_cur_price
        prod_lowest_price = product.product_lowest_price
        lowest_prod_price_date = product.product_lowest_price_date
        tracked_since_data = product.product_tracked_since_date
        is_sale_bool = False
        
        parameters = (
                        fk_user_id, category, product_name, 
                        prod_start_price, prod_cur_price, 
                        prod_lowest_price, lowest_prod_price_date,
                        tracked_since_data, product_link, is_sale_bool
                        )     
        


        Postgres.generic_insert(connection=self.connection, query=query, parameters=list(parameters))
        
        return product


    # ----- Read ----- #
    def fetch_product(self, product_name, user_id):
        query = f"""
                    select * from {self.default_table_name} inner join users on products.fk_user_id = (select id from users where user_id = %s) and products.product_name = %s;
        """
        parameters = (user_id, product_name)
        data, colnames = Postgres.generic_fetch(connection=self.connection, query=query, parameters=list(parameters))
        return data, colnames
    
    def fetch_all_user_products(self, user_id):
        query = f"""
                select * from products inner join users on products.fk_user_id = (select id from users where user_id = %s) where users.user_id = %s;
            """
        parameters = (user_id, user_id)
        data, colnames = Postgres.generic_fetch(connection=self.connection, query=query, parameters=list(parameters))
        
        return data, colnames
    
    def fetch_all_users(self):
        query = f"""
                SELECT * FROM {self.users_table}
        """
        parameters = None
        data, colnames = Postgres.generic_fetch(connection=self.connection, query=query, parameters=list(parameters))
        
        return data, colnames

    # ----- Update ----- #

    # Update product price
    def update_current_product_price(self, product_name, user_id):
        
        # 1. Check DB for most recent product_price
        
        query_url = f"""
                select product_link, current_product_price from {self.default_table_name} where products.fk_user_id = (select id from users where user_id = %s) and products.product_name = %s;
        """
        
        parameters_url = (user_id, product_name)
        url, prev_product_price = Postgres.generic_fetch(connection=self.connection, query=query_url, parameters=list(parameters_url))[0]

        # 2. Get the current product price via scraping
        web_scrapper = WebScrapper(scrape_url=url)
        current_product_price = web_scrapper.get_product_current_price()
        web_scrapper.terminate_session()
        
        # 3. Check if there is a sale
        is_sale = float(current_product_price) < float(prev_product_price)
        
        # 4a. Update database with current sale price
        if is_sale:
            query = f"""
                    UPDATE {self.default_table_name}
                    SET current_product_price = %s
                    WHERE fk_user_id = (SELECT id from users where user_id=%s) AND product_name = %s
            """
            print("Sale!")
            parameters = (current_product_price,user_id, product_name)
            Postgres.generic_insert(connection=self.connection, query=query, parameters=list(parameters))
            
            # 5. Update sales column in DB
            self.update_product_sale(user_id, product_name, is_sale)
            
            # 6. Update lowest product price and date
            self.update_lowest_product_date(user_id, product_name, current_product_price)
            
            # 7. Alert user of sale via mail
            product = {}
            product["current_price"] = current_product_price
            product["prev_price"] = prev_product_price
            product["product_name"] = product_name
            product["user_id"] = "Test User"
            self.mailer.gmail_send_message(self.mailer_creds, product)
        
        # 4b. Do nothing if no sale
        else:
            print("No Sale!")
            return
        
        return
    
    # Update lowest_product_price and lowest_producT_price_date
    def update_lowest_product_date(self, user_id, product_name, current_product_price):
        
        # Set 0 precision to exclude milliseconds
        query = f"""
                    UPDATE {self.default_table_name}
                    SET lowest_product_price_date = NOW()::timestamptz(0)
                    WHERE fk_user_id = (SELECT id from users where user_id=%s) AND product_name = %s
        """
        parameters = (current_product_price, user_id, product_name)
        
        Postgres.generic_insert(connection=self.connection, query=query, parameters=parameters)
        return
    
    
    # Update is_sale bool
    def update_product_sale(self, user_id, product_name, is_sale):
        
        query = f"""
                    UPDATE {self.default_table_name}
                    SET sale_bool = %s
                    WHERE fk_user_id = (SELECT id from users where user_id=%s) AND product_name = %s
        """
        parameters = (is_sale, user_id, product_name)
        
        Postgres.generic_insert(connection=self.connection, query=query, parameters=parameters)
        
        return
    
    # Updates all products for all users
    def update_all_product_prices(self):
        """ Query for all products regardless of user and runs update_current_product_price on it
        """
        
        # Get all products
        query = f"""
                    SELECT * FROM {self.default_table_name};
        """        
        data, _ = Postgres.generic_fetch(connection=self.connection, query=query, parameters=())
        
        for row in data:
            user_id = row[1]
            product_name = row[3]
            
            self.update_current_product_price(product_name=product_name, user_id=user_id)
        return
    
    # Update entire row
    def update_product_info(self):
        return
    
    # ----- Delete  ----- #
    # Delete row
    def remove_product(self, user_id, product_name):
        
        query = f"""
                    DELETE FROM {self.default_table_name} 
                    WHERE fk_user_id = (SELECT id from users where user_id=%s) AND product_name = %s
        """
        
        parameters = (user_id, product_name)
        
        Postgres.generic_insert(connection=self.connection, query=query, parameters=parameters)
        
        return
    
    
    
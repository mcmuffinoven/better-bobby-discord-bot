import discord
from discord.ext import commands, tasks
from bot import CustomContext
import logging
from table2ascii import table2ascii as t2a, PresetStyle
import typing
import functools
import asyncio
import datetime
import os

from utils.product import Product, Product_category
from utils.postgres import Postgres
from utils.user import User


CHANNEL_ID = int(os.environ.get('CHANNEL_ID'))

log = logging.getLogger(__name__)
UTC = datetime.timezone.utc
ROUTINE_SCRAPE = datetime.time(hour=0,minute=00)
ALERT_MESSAGE = "Your product {product_name} is on sale for ${product_price}"

class Price_tracker(commands.Cog):
    def __init__(self, bot):
        self.bot:commands.Bot = bot
        self.db = Postgres(filename="utils/db_info.ini", section="postgres")
        self.routine_product_scrape.start() # Start the TASK LOOP

    async def alert_user(self, channel:discord.TextChannel, user:User, message:str):
        await channel.send(f"<@{user.user_id}> {message}")
        
    @tasks.loop(time=ROUTINE_SCRAPE)
    # @tasks.loop(minutes=5)
    async def routine_product_scrape(self):
        
        channel = self.bot.get_channel(CHANNEL_ID)
        users_list = self.get_all_users()

        for user in users_list:
            log.info(f"Scrapping {len(users_list)} users...")
            user_products = self.get_all_user_products(user_id=user.user_id)
            
            log.info(f"{user.user_name} has {len(user_products)} products...")
            
            for product in user_products:
                log.info(f"Checking {product.product_name} for sale...")
                if product.is_product_sale():
                    pass
                    await self.alert_user(channel, user, ALERT_MESSAGE.format(product_name = product.product_name, product_price = product.product_cur_price))
                    
        log.info("Routine Scrape Complete")

    
    def to_thread(func: typing.Callable) -> typing.Coroutine:
        @functools.wraps(func)
        async def wrapper(*args, **kwargs):
            return await asyncio.to_thread(func, *args, **kwargs)
        return wrapper


    # Offload the scrapping to the background to prevent task from pausing the bot while scrapping
    @to_thread
    def scrape_product(self, product_category, product_url:str, user_name, user_id):
        try:
            # Create a new Product object
            product = Product()
            
            # Create a new User object
            user = User()
            user.user_name = user_name
            user.user_id = user_id
            self.db.insert_user(user_name=user.user_name,user_id=user.user_id)
            product.scrape_product(product_category=product_category, product_url=product_url, user_id=user_id)            
            self.db.insert_product(**dict(product.__dict__|user.__dict__))
            
        except Exception as e:
            log.error(e)
        
        return product


    @commands.command(name="track_product")
    async def track_product(self, ctx: CustomContext, product_category:str = commands.parameter(default=None, description="Either one of Tech/Grocery/Fashion/Cosmetics"), product_url:str=commands.parameter(default=None, description="Link to the product. Only best buy for now.")):
        """Adds a product from a website to track for sales.
           Example: -track_product tech https:www.bestbuy.com/eggroll>bobby
        """
        # Validate user inputs before scrapping
        if not product_category:
            await ctx.send("You forgot the product category")
        else:
            if product_category.upper() not in list(Product_category.__members__.keys()):
                await ctx.send(f"Please choose a category from: {', '.join(list(Product_category.__members__.keys()))}")
        
        if not product_url:
            await ctx.send("You forgot the product link")
        
        try:            
            product:Product = await self.scrape_product(product_category, product_url, ctx.message.author.name, ctx.message.author.id)
            await ctx.send(f'<@{ctx.message.author.id}> Adding {product.product_name} with starting price {product.product_cur_price} to the database. You will receive a message when this item is on sale.' )
    
        except Exception as e:
            log.error(e)
            await ctx.send(f'Error adding {product.product_name}')
    
    
    def get_all_user_products(self, user_id:str):
        
        data, colnames = self.db.fetch_all_user_products(user_id)
        
        product_list:list[Product] = []
        for row in data:
            product_list.append(Product.create_product(value=row, properties=colnames))
            
        return product_list
    
    def get_all_users(self):
        
        data, colnames = self.db.fetch_all_users()
        
        users_list:list[User] = []
        for row in data:
            users_list.append(User.create_user(value=row, properties=colnames))
            
        return users_list
    
    @commands.command(name="get_my_products")
    async def get_all(self,ctx: CustomContext):
        """Returns a table of all your currently tracked items
        """
        cur_user_id = ctx.message.author.id
        
        # Fetch from Database
        data, colnames, url_list = self.db.fetch_all_user_products(cur_user_id, table_view=True)
        
        output = t2a(
            header = colnames,
            body = data,
            # header=["ID", "Product Name", "Category", "Current Price", "Starting Price", "Lowest Price", "Lowest Price Date", "Sale"],
            # body=[(1, 'Team A', 'Tech', 100, 50, 200, '2024-01-01', 'Yes'), [2, 'Team B', 'Fashion', 100, 50, 200, '2024-01-01', 'Yes'], [3, 'Team C', 'Grocery', 200, 50, 200, '2024-01-01', 'No']],
        )

        await ctx.send(f"<@{cur_user_id}>```Here are your tracked products \n{output}\n```")
        await ctx.send(f"Here are the urls for your products")
        
        for index, url in enumerate(url_list):
            await ctx.send(f"{index+1}. {url[0]}")
    
async def setup(bot):
    await bot.add_cog(Price_tracker(bot))
    
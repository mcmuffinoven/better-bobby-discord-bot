import discord
from discord.ext import commands, tasks
from bot import CustomContext
from utils.product import Product, Product_category
from utils.postgres import Postgres
import logging
from table2ascii import table2ascii as t2a, PresetStyle
from utils.user import User

from utils.web_scrapper import WebScrapper

import typing
import functools
import asyncio

import datetime


log = logging.getLogger(__name__)
UTC = datetime.timezone.utc
ROUTINE_SCRAPE = datetime.time(hour=8, tzinfo=UTC),

class Price_tracker(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        self.db = Postgres(filename="utils/db_info.ini", section="postgres")


    async def alert_user(self, ctx: CustomContext, user_id):
        await ctx.channel.send(f"<@mcmuffinoven>")

    @tasks.loop(time=ROUTINE_SCRAPE)
    async def routine_product_scrape(self):
        # multi thread
        # 10 users, 10 products. 100 scrapes a night 
        # time doesnt really matter i guess
        # 1. Get all products to be scraped from every user 
        # 2. Edit database
            # if there is a sale
                # overwrite sale bool 
                # overwrite price
                # overwrite cheapest date
                # overwrite cheapest price

        # 3. Alert user
        scrapper = WebScrapper()

        users_list = self.db.fetch_all_users()

        for user in users_list:
            user_products = self.db.fetch_all_user_products()

            for product in user_products:
                scrapper.scrape_product_data()

        pass
    
    def to_thread(func: typing.Callable) -> typing.Coroutine:
        @functools.wraps(func)
        async def wrapper(*args, **kwargs):
            return await asyncio.to_thread(func, *args, **kwargs)
        return wrapper


    @to_thread
    def scrape_product(self, product_category, product_url:str, user_id):
        try:
            self.db.insert_user(user_id=user_id)
            data = self.db.insert_product(product_category=product_category, product_url=product_url, user_id=user_id)
        except Exception as e:
            log.error(e)
        
        return data


    @commands.command(name="track_product")
    async def track_product(self, ctx: CustomContext, product_category:str=None, product_url:str=None):
        if not product_category:
            await ctx.send("You forgot the product category")
        else:
            if product_category.upper() not in list(Product_category.__members__.keys()):
                await ctx.send(f"Please choose a category from: {', '.join(list(Product_category.__members__.keys()))}")
        
        if not product_url:
            await ctx.send("You forgot the product link")
        
        try:
            
            data = await self.scrape_product(product_category,product_url, ctx.message.author.name)
            
            await ctx.send(f'Adding {data["productName"]} with starting price {data["prodCurPrice"]} to the database. You will receive a message when this item is on sale.' )
    
        except Exception as e:
            log.error(e)
            await ctx.send(f'Error adding {data["product_name"]}')
            
    @commands.command(name="get_product")
    async def get_all(self,ctx: CustomContext):
        cur_user = User(ctx.author)
        
        # Fetch from Database
        user_products = self.db.fetch_all_user_products(cur_user)
        
        output = t2a(
            header=["ID", "Product Name", "Category", "Current Price", "Starting Price", "Lowest Price", "Lowest Price Date", "Sale"],
            body=[[1, 'Team A', 'Tech', 100, 50, 200, '2024-01-01', 'Yes'], [2, 'Team B', 'Fashion', 100, 50, 200, '2024-01-01', 'Yes'], [3, 'Team C', 'Grocery', 200, 50, 200, '2024-01-01', 'No']],
            # first_col_heading=True
        )

        await ctx.send(f"```Hi {cur_user} Here are your tracked products \n{output}\n```")
    
async def setup(bot):
    await bot.add_cog(Price_tracker(bot))
    
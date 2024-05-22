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
import os

CHANNEL_ID = os.environ.get('CHANNEL_ID')

log = logging.getLogger(__name__)
UTC = datetime.timezone.utc
ROUTINE_SCRAPE = datetime.time(hour=1,minute=51, tzinfo=UTC)
ALERT_MESSAGE = "Your product {product_name} is on sale for ${product_price}"

class Price_tracker(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        self.db = Postgres(filename="utils/db_info.ini", section="postgres")
        self.routine_product_scrape.start() # Start the TASK LOOP
        log.info("Price Tracker Cog has started...")

    async def alert_user(self, channel:discord.TextChannel, user_id, message:str):
        await channel.send(f"@{user_id} {message}")

    @tasks.loop(time=ROUTINE_SCRAPE)
    async def routine_product_scrape(self):
        
        channel = self.bot.get_channel(CHANNEL_ID)
        await channel.send(f"@mcmuffinoven Hello")
        scrapper = WebScrapper()

        users_list = self.db.fetch_all_users()

        for user in users_list:
            log.info(f"Scrapping {len(users_list)} users...")
            user_products = self.db.fetch_all_user_products(user_id=user)
            

            for product in user_products:
                if scrapper.is_product_sale(product, product.product_cur_price):
                    self.alert_user(channel, user, ALERT_MESSAGE.format(product.product_name, product.product_cur_price))

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

        await ctx.send(f"```Hi @{cur_user} Here are your tracked products \n{output}\n```")
    
async def setup(bot):
    log.info(ROUTINE_SCRAPE.strftime("%H:%M"))
    await bot.add_cog(Price_tracker(bot))
    
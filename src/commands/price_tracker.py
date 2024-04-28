import discord
from discord.ext import commands
from bot import CustomContext
from utils.product import Product, Product_category
from utils.web_scrapper import WebScrapper
from utils.postgres import Postgres
import logging
from table2ascii import table2ascii as t2a, PresetStyle
from utils.user import User

import typing
import functools
import asyncio


log = logging.getLogger(__name__)

class Price_tracker(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        self.db = Postgres(filename="utils/db_info.ini", section="postgres")
    
    def to_thread(func: typing.Callable) -> typing.Coroutine:
        @functools.wraps(func)
        async def wrapper(*args, **kwargs):
            return await asyncio.to_thread(func, *args, **kwargs)
        return wrapper


    @to_thread
    def scrape_product(self, product_category, product_link:str, user_id):
        data = self.db.insert_product(product_category=product_category, product_link=product_link, user_id=user_id)
        log.info(data)
        
        return data


    @commands.command(name="track_product")
    async def track_product(self, ctx: CustomContext, product_category:str=None, product_link:str=None):
        if not product_category:
            await ctx.send("You forgot the product category")
        else:
            # print(Product_category.__members__)
            if product_category.upper() not in list(Product_category.__members__.keys()):
                await ctx.send(f"Please choose a category from: {', '.join(list(Product_category.__members__.keys()))}")
        
        if not product_link:
            await ctx.send("You forgot the product link")
        # init new product
        # product = Product(product_category=product_category, product_link=product_link)
        # log.info(ctx.message.author)
        
        try:
            
            data = await self.scrape_product(product_category,product_link, ctx.message.author.name)
            
            await ctx.send(f'Adding {data["productName"]} with starting price {data["prodCurPrice"]} to the database. You will receive a message when this item is on sale.' )
    
        except Exception as e:
            log.error(e)
            # await ctx.send(f"Error adding {product.product_name}" )
            
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
    
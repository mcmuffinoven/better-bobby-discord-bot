import discord
from discord.ext import commands
from bot import CustomContext
from utils.product import Product, Product_category
from utils.web_scrapper import WebScrapper
from utils.postgres import Postgres
import logging
from table2ascii import table2ascii as t2a, PresetStyle


log = logging.getLogger(__name__)

class Price_tracker(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        self.db = Postgres(filename="utils/db_info.ini", section="postgres")
                
    @commands.command(name="track_product")
    async def track_product(self, ctx: CustomContext, product_category:str=None, product_link:str=None):
        if not product_category:
            await ctx.send("You forgot the product category")
        else:
            if product_category.upper() not in Product_category.__members__:
                await ctx.send(f"Please choose a category from: {list(map(lambda c: c.value, Product_category.__members__.keys()))}")
        
        print(Product_category.__members__)
        if not product_link:
            await ctx.send("You forgot the product link")
        # init new product
        # product = Product(product_category=product_category, product_link=product_link)
        log.info(ctx.message.author)
        
        try:
            data = self.db.insert_product(product_category=product_category, product_link=product_link.upper())
            log.info(data)
            
            await ctx.send(f"Adding {data.product_name} with starting price {data.product_current_price} to the database. You will recieve a message when this item is on sale." )
            await ctx.send("Adding")
    
        except Exception as e:
            log.error(e)
            # await ctx.send(f"Error adding {product.product_name}" )
            
    @commands.command(name="get_product")
    async def get_all(self,ctx: CustomContext):
        output = t2a(
            header=["ID", "Product Name", "Category", "Current Price", "Starting Price", "Lowest Price", "Lowest Price Date", "Sale"],
            body=[[1, 'Team A', 'Tech', 100, 50, 200, '2024-01-01', 'Yes'], [2, 'Team B', 'Fashion', 100, 50, 200, '2024-01-01', 'Yes'], [3, 'Team C', 'Grocery', 200, 50, 200, '2024-01-01', 'No']],
            # first_col_heading=True
        )

        await ctx.send(f"```\n{output}\n```")
    
async def setup(bot):
    await bot.add_cog(Price_tracker(bot))
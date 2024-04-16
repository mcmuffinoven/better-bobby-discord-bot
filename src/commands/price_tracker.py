import discord
from discord.ext import commands
from bot import CustomContext
from utils.product import Product
from utils.web_scrapper import WebScrapper
from utils.postgres import Postgres
import logging

log = logging.getLogger(__name__)

class Price_tracker(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        self.db = Postgres(filename="utils/db_info.ini", section="postgres")
                
    @commands.command(name="track_product")
    async def track_product(self, ctx: CustomContext, product_category=None, product_link=None):
        if not product_category:
            await ctx.send("You forgot the product category")
            
        if not product_link:
            await ctx.send("You forgot the product link")
        # init new product
        # product = Product(product_category=product_category, product_link=product_link)
        log.info(ctx.message.author)
        
        try:
            data = self.db.insert_product(product_category=product_category, product_link=product_link)
            log.info(data)
            # await ctx.send(f"Adding {product.product_name} with starting price {product.product_current_price} to the database. You will recieve a message when this item is on sale." )
            await ctx.send("Adding")
    
        except Exception as e:
            log.error(e)
            # await ctx.send(f"Error adding {product.product_name}" )
            
    
async def setup(bot):
    await bot.add_cog(Price_tracker(bot))
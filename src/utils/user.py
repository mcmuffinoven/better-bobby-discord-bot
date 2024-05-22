from table2ascii import table2ascii as t2a, PresetStyle

from bot import CustomContext
from utils.product import Product, Product_category
import logging

log = logging.getLogger(__name__)


class User():
    
    @staticmethod
    def create_user(value, properties):
        user = User()
        
        for property_name, value in zip(properties,value):
            setattr(user, property_name, value)
            
        return user
    
    def __init__(self):
        self.user_id = None
        self.user_name = None
        self.user_products = []
    
    
    async def get_all_products_from_db(self):
        pass
        
    async def get_all_tracked_product(self, ctx:CustomContext):
        
        # In your command:
        output = t2a(
            header=["Rank", "Team", "Kills", "Position Pts", "Total"],
            body=[[1, 'Team A', 2, 4, 6], [2, 'Team B', 3, 3, 6], [3, 'Team C', 4, 2, 6]],
            first_col_heading=True
        )

        await ctx.send(f"```\n{output}\n```")

    
    
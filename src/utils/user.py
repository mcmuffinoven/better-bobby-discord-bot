from table2ascii import table2ascii as t2a, PresetStyle

from bot import CustomContext
from utils.product import Product, Product_category
from utils.postgres import Postgres
import logging

log = logging.getLogger(__name__)


class User():
    def __init__(self, user_id):
        self.user_id = user_id
        
        
    async def get_all_tracked_product(self, ctx:CustomContext):
        
        # In your command:
        output = t2a(
            header=["Rank", "Team", "Kills", "Position Pts", "Total"],
            body=[[1, 'Team A', 2, 4, 6], [2, 'Team B', 3, 3, 6], [3, 'Team C', 4, 2, 6]],
            first_col_heading=True
        )

        await ctx.send(f"```\n{output}\n```")

    
    
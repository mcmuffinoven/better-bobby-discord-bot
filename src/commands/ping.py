from discord.ext import commands
from bot import CustomContext
import logging

log = logging.getLogger(__name__)

class Ping(commands.Cog):
    # Ping test
    @commands.command()
    async def ping(self, ctx: CustomContext):
        """Ping test"""
        log.debug(f'Ping test')
        await ctx.tick(True)
        await ctx.reply("woof!")

# This function will be called by `load_extension` in main.py will register this Cog
async def setup(bot):
    await bot.add_cog(Ping(bot))
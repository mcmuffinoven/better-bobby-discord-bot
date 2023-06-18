from discord.ext import commands
from bot import CustomContext
import logging
import pytz
from datetime import datetime

log = logging.getLogger(__name__)

class Time(commands.Cog):
    @commands.command()
    async def time(self, ctx: CustomContext):
        """Get current time from different timezones. Copied from Walker's bot - thanks Walker."""
        now = datetime.now()
        hkt = datetime.strftime(now.astimezone(pytz.timezone("Asia/Hong_Kong")), "%I:%M %p")
        pdt = datetime.strftime(now.astimezone(pytz.timezone("America/Vancouver")), "%I:%M %p")
        aus = datetime.strftime(now.astimezone(pytz.timezone("Australia/Melbourne")), "%I:%M %p")
        use = datetime.strftime(now.astimezone(pytz.timezone("America/Toronto")), "%I:%M %p")
        ukt = datetime.strftime(now.astimezone(pytz.timezone("Europe/London")), "%I:%M %p")
        jpt = datetime.strftime(now.astimezone(pytz.timezone("Japan")), "%I:%M %p")

        # I don't know what the truck means. Amazon a.k.a Seattle time??
        await ctx.send(":truck:: %s | :flag_ca:: %s | :flag_gb:: %s | :flag_hk:: %s | :flag_jp:: %s | :flag_au:: %s" % (pdt, use, ukt, hkt, jpt, aus))

async def setup(bot):    
    await bot.add_cog(Time(bot))
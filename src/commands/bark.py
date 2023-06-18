import discord
from discord.ext import commands
from bot import CustomContext

class Bark(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        self.subscribed_channels = {}
    
    # "@here bark!" when the first user joins the voice channel.
    @commands.Cog.listener()
    async def on_voice_state_update(
        self,
        member: discord.Member,
        before: discord.VoiceState,
        after: discord.VoiceState
    ):
        joined_vc = before.channel is None and after.channel is not None
        switched_vc = before.channel is not None and after.channel is not None and before.channel != after.channel

        # User joined a voice channel OR switched from another voice channel
        if joined_vc or switched_vc:
            assert(after.channel is not None)
            # First person there
            if len(after.channel.members) == 1:
                guild_id = after.channel.guild.id
                
                if guild_id in self.subscribed_channels:
                    channel = self.subscribed_channels[guild_id]
                    await channel.send(f"@here bark! {after.channel.name}")
    
    @commands.command(name="subscribe")
    async def subscribe_current_channel(self, ctx: CustomContext):
        """Subscribes the text channel the user is currently in for barking notifications"""
        if ctx.guild:
            self.subscribed_channels[ctx.guild.id] = ctx.channel
            await ctx.reply("Bobby will now bark in this channel!")
        else:
            await ctx.reply("Bobby can't find this channel 🐶")


async def setup(bot):
    await bot.add_cog(Bark(bot))
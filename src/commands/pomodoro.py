import logging
import discord
from enum import Enum
from discord.ext import commands
from bot import CustomContext
import asyncio
from utils.voice_state import joined_vc, switched_vc, left_vc, vc_empty 

FOCUS_TIME_SECONDS = 25 * 60 # 25 minutes
REST_TIME_SECONDS = 5 * 60 # 5 minutes

log = logging.getLogger(__name__)

class PomodoroStates(Enum):
    FOCUS = 1
    REST = 0

class Pomodoro(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        self.pomodoro_channels = {}
        # Key = assigned_channel.id, value = [FOCUS/REST status, looping async task]
        self.pomodoro_channels_status = {}
    
    @commands.Cog.listener()
    async def on_voice_state_update(
        self,
        member: discord.Member,
        before: discord.VoiceState,
        after: discord.VoiceState
    ):
        guild_id = member.guild.id

        # Voice state change unrelated to pomodoro channel, skip
        if guild_id not in self.pomodoro_channels:
            return
        
        assigned_channel = self.pomodoro_channels[guild_id]
        await self.manage_session(before, after, assigned_channel)
        
        # Server unmute user before they leave, don't want user muted if they join other channels
        if before.channel is assigned_channel and (left_vc(before.channel, after.channel) or switched_vc(before.channel, after.channel)):
            if self.shouldServerUnmute(member):
                await member.edit(mute=False)
            return

        # No statuses relating to assigned pomodoro channel, meaning that no session is ongoing, exit
        if assigned_channel.id not in self.pomodoro_channels_status:
            return

        # If user joins an ongoing Pomodoro session OR if they attempt to unmute during a focus session
        # mute them.
        status, _ = self.pomodoro_channels_status[assigned_channel.id]
        if after.channel is assigned_channel:
            if status is PomodoroStates.FOCUS and self.shouldServerMute(member):
                await member.edit(mute=True)
            elif status is PomodoroStates.REST and self.shouldServerUnmute(member):
                await member.edit(mute=False)
    
    def shouldServerMute(self, member):
        return not member.voice.mute
    
    def shouldServerUnmute(self, member):
        return member.voice.mute
    
    async def manage_session(self, before: discord.VoiceState, after: discord.VoiceState, assigned_channel):
        # If user joined Pomodoro channel and they're the first one there
        if (joined_vc(before.channel, after.channel) or switched_vc(before.channel, after.channel)) and after.channel is assigned_channel and len(after.channel.members) == 1:
            task = asyncio.create_task(self.start_session(assigned_channel))
            self.pomodoro_channels_status[assigned_channel.id] = [PomodoroStates.FOCUS, task]
            await self.notify_vc(after.channel, "Pomodoro session started")
        # If user left the Pomodoro channel and it's empty
        elif (left_vc(before.channel, after.channel) or switched_vc(before.channel, after.channel)) and before.channel is assigned_channel and vc_empty(before.channel):
            _, task = self.pomodoro_channels_status.pop(assigned_channel.id)
            
            task.cancel()

            try:
                await self.notify_vc(before.channel, "Pomodoro session ended")
                await task
            except asyncio.CancelledError:
                log.info("Task was cancelled gracefully.")

    @commands.command(name="pomodoro")
    async def assign_channel(self, ctx: CustomContext):
        """Assigns the current voice channel the user is currently in for Pomodoro sessions. 
            If the voice channel has already been assigned, it is unassigned."""
        if ctx.guild:
            if ctx.author.voice:
                if ctx.guild.id not in self.pomodoro_channels:
                    vc = ctx.author.voice.channel
                    self.pomodoro_channels[ctx.guild.id] = vc
                    await ctx.reply("This channel has been assigned for Pomodoro")
                else:
                    self.pomodoro_channels.pop(ctx.guild.id)
                    await ctx.reply("This channel has been unassigned for Pomodoro")
            else:
                await ctx.reply("Can't assign a dedicated pomodoro in a voice channel because you're not in one!")
        else:
            await ctx.reply("Bobby can't find this channel 🐶")
    
    async def start_session(self, channel):
        async def start_focus_time():
            await asyncio.sleep(FOCUS_TIME_SECONDS)
        
        async def start_rest_time():
            await asyncio.sleep(REST_TIME_SECONDS)

        while True:
            status, _ = self.pomodoro_channels_status[channel.id]
            if status is PomodoroStates.FOCUS:
                await self.server_mute_channel(channel, True)
                await self.notify_vc(channel, "Focus time has begun")
                await start_focus_time()
                self.pomodoro_channels_status[channel.id][0] = PomodoroStates.REST
            elif status is PomodoroStates.REST:
                await self.server_mute_channel(channel, False)
                await self.notify_vc(channel, "Rest time has begun")
                await start_rest_time()
                self.pomodoro_channels_status[channel.id][0] = PomodoroStates.FOCUS
    
    async def server_mute_channel(self, channel, shouldMute):
        for member in channel.members:
            await member.edit(mute=shouldMute)
    
    async def notify_vc(self, channel, msg):
        notification = ""
        for member in channel.members:
            notification += f"{member.mention} "
        
        await channel.send(notification + msg)

async def setup(bot):
    await bot.add_cog(Pomodoro(bot))
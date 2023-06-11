# Copying example from https://github.com/Rapptz/discord.py/blob/master/examples/custom_context.py

import discord
from discord.ext import commands
import os

class CustomContext(commands.Context):
    async def tick(self, value):
        # reacts to the message with an emoji
        # depending on whether value is True or False
        # if its True, it'll add a green check mark
        # otherwise, it'll add a red cross mark
        emoji = '\N{WHITE HEAVY CHECK MARK}' if value else '\N{CROSS MARK}'
        try:
            # this will react to the command author's message
            await self.message.add_reaction(emoji)
        except discord.HTTPException:
            # sometimes errors occur during this, for example
            # maybe you don't have permission to do that
            # we don't mind, so we can just ignore them
            pass

class BobbyBot(commands.Bot):
    async def get_context(self, message, *, cls=CustomContext):
        # when you override this method, you pass your new Context
        # subclass to the super() method, which tells the bot to
        # use the new MyContext class
        return await super().get_context(message, cls=cls)

    async def on_ready(self):
        print(f'We have logged in as {self.user}')

        # Load all commands
        for file in os.listdir("commands"):
            if file.endswith(".py"):
                await self.load_extension(f"commands.{file[:-3]}")
import discord
import os
from bot import BobbyBot

intents = discord.Intents.default()
intents.message_content = True

bot = BobbyBot(command_prefix='$', intents=intents)

token = os.environ.get('API_TOKEN')
if token is not None:
    bot.run(token)
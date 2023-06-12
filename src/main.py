import discord
import os
from bot import BobbyBot
import logging

intents = discord.Intents.default()
intents.message_content = True

# Setup default logging configuration
discord.utils.setup_logging(level=logging.INFO)

log = logging.getLogger(__name__)

bot = BobbyBot(command_prefix='$', intents=intents)

token = os.environ.get('API_TOKEN')
if token is not None:
    bot.run(token)
else:
    log.error('No API token found')
import discord
import os
from bot import BobbyBot
import logging
from dotenv import load_dotenv

# Load environment variables from .env file defined at root directory
load_dotenv()

# Setup default logging configuration
discord.utils.setup_logging(level=logging.INFO)

log = logging.getLogger(__name__)

intents = discord.Intents.default()
intents.message_content = True

description = 'If you want to contribute: https://github.com/kwhk/bobby-discord-bot'

activity = discord.Activity(type=discord.ActivityType.listening, name="-help")
bot = BobbyBot(command_prefix='-', intents=intents, activity=activity, log_handler=False)

token = os.environ.get('API_TOKEN')
if token is not None:
    bot.run(token)
else:
    log.error('No API token found')
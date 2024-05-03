import logging
import os

import discord

from bot import Bot
from dotenv import load_dotenv
load_dotenv()

if __name__ == '__main__':
    if os.getenv('token') == None:
        with open('.env', 'w') as file:
            file.write('''
guild=
token=
basic_source=youtube 
leave_inactive_time=60
channel_id=
volume=30
lavalink_ip=127.0.0.1
lavalink_port=2333
lavalink_password=8642
command_sync=true
log_level=INFO
cache=100
''')
            exit(".env file was created. Please configurate bot!")

    logging.basicConfig(filename="last.log", level=os.getenv('log_level'), filemode='w',
        format='%(asctime)s - %(name)s - %(levelname)s - %(module)s - %(funcName)s: %(message)s', encoding='utf-8')
    discord.utils.setup_logging(level=os.getenv('log_level'))

    logging.info("Start bot...")
    discord_bot = Bot('!', discord.Intents.all(), os.getenv('token'))
    
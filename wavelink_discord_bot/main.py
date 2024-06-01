import logging
import os

import discord

from dotenv import load_dotenv
load_dotenv()
def check_env():
    if not os.path.isfile(".env"):
        with open('.env', 'w') as file:
            file.write(
'''
guild=
token=
basic_source=youtube 
leave_inactive_time=60
channel_id=
lavalink_ip=127.0.0.1
lavalink_port=2333
lavalink_password=8642
command_sync=true
log_level=INFO
cache=100
''')
        exit("File .env was created. Please configurate bot!")
    elif None in (os.getenv('token'), os.getenv('guild')):
        exit("Please configure the .env file!")

check_env()
from bot import Bot

if __name__ == '__main__':
    logging.basicConfig(filename="last.log", level=os.getenv('log_level'), filemode='w',
        format='%(asctime)s - %(name)s - %(levelname)s - %(module)s - %(funcName)s: %(message)s', encoding='utf-8')
    discord.utils.setup_logging(level=os.getenv('log_level'))

    logging.info("Start bot...")
    discord_bot = Bot('!', discord.Intents.all(), os.getenv('token'))
    
import logging
import time
import os
import asyncio

import discord

from discord.ext import commands
from discord.ext.commands import errors
from cogs.music import Music
from cogs.tools import Tools
from dotenv import load_dotenv
load_dotenv()

class Bot(commands.Bot):
    def __init__(self, prefix, intents, token) -> None:
        super().__init__(command_prefix=prefix, intents=intents)
        self.run(token)

    async def setup_hook(self) -> None:
        await self.add_cog(Music(self))
        await self.add_cog(Tools(self))
        if os.getenv('command_sync') != 'false':
            logging.info(f'Sync {len(await self.tree.sync(guild=discord.Object(id=os.getenv('guild'))))} commands')

    async def on_command_error(self, context: commands.Context, exception: commands.CommandError) -> None:
        match type(exception):
            case errors.CommandNotFound:
                ...
            case errors.MissingRequiredArgument:
                ...
            case errors.NotOwner:
                await context.reply('You are not a owner!')
            case _:
                logging.error(f'{type(exception)}: {exception}')
    
    async def on_ready(self):
        logging.info(f'Bot is ready! {os.getenv('guild')=}')

    async def check_channel_id(self, interaction:discord.Interaction):
        if os.getenv('channel_id') == '':
            return True
        elif int(os.getenv('channel_id')) == interaction.channel.id:
            return True
        else:
            await interaction.reply(f'Write in correct channel!')
            return False

import logging
import os

import discord

from discord.ext import commands
from discord import app_commands
from dotenv import load_dotenv
load_dotenv()

class Tools(commands.Cog):
    def __init__(self, bot:commands.Bot) -> None:
        logging.info('Load tools cog...')
        self.bot = bot

    @commands.is_owner()
    @commands.bot.hybrid_command(name='shutdown', with_app_command=True, description='Stops the bot')
    @app_commands.guilds(discord.Object(id=os.getenv('guild')))
    async def shutdown(self, interaction: discord.Interaction) -> None:
        await interaction.reply('Shuting down!')
        await self.bot.close()
   

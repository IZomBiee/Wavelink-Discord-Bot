import asyncio
import logging
import discord
from discord.ext import commands
from .emoji_menu import *

async def emoji_numeric_menu(bot:commands.Bot, interaction: discord.Interaction, title:str,
                       options: list[str]) -> int:
    '''
    Menu that recives reaction to numeric emoji as input and
    retrieve the option index. Retrives -1 after timeout
    '''
    logging.info(f'Using numeric emoji menu with title {title} with {len(options)} options')
    if len(options) > 9: raise ValueError("Too much options")
    emojies = ('1️⃣', '2️⃣', '3️⃣', '4️⃣', '5️⃣', '6️⃣', '7️⃣', '8️⃣', '9️⃣')
    emojies = emojies[0:len(options)]

    return await emoji_menu(bot, interaction, title, options, emojies)
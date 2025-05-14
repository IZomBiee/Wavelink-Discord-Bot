import asyncio
import logging
import discord
from discord.ext import commands

async def numeric_menu(bot:commands.bot, interaction: discord.Interaction, title:str, options: list[str], inline=False, timeout=10) -> int:
    '''
    Menu that recives just a sended author number as input and
    retrieve the option index. Retrives -1 after timeout
    '''
    logging.info(f'Using numeric menu with title {title} with {len(options)} options')
    embed = discord.Embed(title=title, color=0x336EFF)
    for index, option in enumerate(options):
        embed.add_field(name=f'{index+1}. {option}', value=f'', inline=inline)

    message = await interaction.reply(embed=embed)
    
    def check(message:discord.Message):
        if message.author.bot == False and message.author == interaction.message.author:
            return message

    try:
        while (True):
            message = await bot.wait_for('message', timeout=timeout, check=check)
            try:
                number = int(message.content)
                if 0 >= number or number > len(options):
                    await message.reply(f'Write number between 1 and {len(options)}!')
                else: return number
            except ValueError:
                await message.reply(f'Write number!')
    except asyncio.TimeoutError:
        await message.reply(f'No reaction in {timeout} sec')
    return -1
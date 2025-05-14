import asyncio
import logging
import discord
from discord.ext import commands

async def emoji_menu(bot:commands.Bot, interaction: discord.Interaction, title:str,
                       options: list[str], emojies: list[str]) -> int:
    '''
    Menu that recives reaction to emoji as input and
    retrieve the option index. Retrives -1 after timeout
    '''
    logging.info(f'Using emoji menu with title {title} with {len(options)} options')
    embed = discord.Embed(title=title, color=0x336EFF)
    for index, option in enumerate(options):
        embed.add_field(name=f'{index+1}. {option}', value=f'', inline=True)

    message: discord.InteractionMessage = await interaction.reply(embed=embed)
    for emoji in emojies:
        await message.add_reaction(emoji)
    
    def check(reaction: discord.Reaction, user):
        if reaction.emoji in emojies and user.bot == False:
            return reaction
        
    try:
        reaction = tuple(await bot.wait_for('reaction_add', timeout=10, check=check))[0]
        return emojies.index(reaction.emoji)
    except asyncio.TimeoutError:
        await message.reply(f'No reaction in 10 sec')
        return -1
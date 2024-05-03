import asyncio
import logging

import discord

from discord.ext import commands

class Menu():
    @staticmethod
    async def number(bot:commands.bot, interaction: discord.Interaction, title:str, options:list[dict], inline=False, timeout=10) -> int:
        logging.info(f'Menu {title=} {len(options)=} {inline=} {timeout=}...')
        embed = discord.Embed(title=title, color=0x336EFF)
        for index, option in enumerate(options):
            embed.add_field(name=f'{index+1}. {option['name']}', value=f'{option['value']}', inline=inline)

        message = await interaction.reply(embed=embed)
        
        def check(message:discord.Message):
            if message.author.bot == False:
                return message

        try:
            message = await bot.wait_for('message', timeout=timeout, check=check)
            try:
                number = int(message.content)
                if 0 >= number or number > len(options):
                    await message.reply(f'Write number between 1 and {len(options)}!')
                    number = None
            except ValueError:
                await message.reply(f'Write number!')
                number = None
        except asyncio.TimeoutError:
            await message.reply(f'No reaction in {timeout} sec')
            number = None
        logging.info(f'Return {number}')
        return number
    
    @staticmethod
    async def reaction_menu(bot:commands.bot, interaction: discord.Interaction, title:str,
                options:list[dict], inline=False, timeout=10) -> int:
        embed = discord.Embed(title=title, color=0x336EFF)
        for index, option in enumerate(options):
            embed.add_field(name=f'{index+1}. {option['name']}', value=f'{option['value']}', inline=inline)

        message = await interaction.reply(embed=embed)
        
        reactions = [i['emoji'] for i in options]

        def check(reaction, user):
            if reaction.emoji in reactions and user.bot == False:
                return reaction

        try:
            reaction = await bot.wait_for('reaction_add', timeout=timeout, check=check)
            number = [index+1 for index, i in enumerate(options)][str(reaction[0])]
        except asyncio.TimeoutError:
            await message.reply('No reaction in 10 sec')
            number = None
        return number

import logging
import subprocess
import time
import os

import wavelink
import discord

from discord.ext import commands
from menu import Menu

class MusicService():
    def __init__(self, bot:commands.Bot):
        self.bot = bot
        self.lavalink_start()
        
    def lavalink_start(self):
        logging.info('Start LavaLink...')
        p = subprocess.Popen('lavalink\\start.bat', creationflags=subprocess.CREATE_NEW_CONSOLE)
        time.sleep(5)
    
    async def _choose(self, interaction:discord.Interaction, tracks:list[wavelink.Playable]) -> wavelink.Playable:
        if len(tracks) == 0:
            await interaction.reply("Can't find track")
            return None
        
        elif len(tracks) == 1:
            await interaction.reply('One track was found')
            return tracks[0]
        
        elif len(tracks) > 5:
            tracks = tracks[0:5]
        
        index = await Menu.number(self.bot, interaction, f"Write number of track on {tracks[0].source}",
        [{'name':i.title, 'value':f'{MusicService.mil_to_time(i.length)}'} for i in tracks],
        False, 20)
        if index == None:
            return None
        else:
            return tracks[index-1]

    async def search(self, interaction:discord.Interaction, promt:str, source:str) -> wavelink.Playable:
        if source == None:
            source = os.getenv('basic_source')
        logging.info(f'Search {promt=} {source=}...')
        try:
            source = {'youtube':wavelink.TrackSource.YouTube,
                    'youtube music':wavelink.TrackSource.YouTubeMusic,
                    'soundcloud':wavelink.TrackSource.SoundCloud}[source.strip().lower()]
        except KeyError:
            await self.search(interaction, promt, None)
        
        tracks: wavelink.Search = await wavelink.Playable.search(promt, source=source)
        return await self._choose(interaction, tracks)
    
    @staticmethod
    def mil_to_time(ms):
        seconds = ms // 1000
        minutes, seconds = divmod(seconds, 60)
        hours, minutes = divmod(minutes, 60)
        return "{:02d}:{:02d}:{:02d}".format(hours, minutes, seconds)
    
    @staticmethod
    async def get_voice_channel(interaction: discord.Interaction):
        try:
            return interaction.author.voice.channel
        except AttributeError:
            await interaction.reply('You are not in the voice channel!')
            return None
        except Exception as e:
            await interaction.reply('Unexcepted error!')
            return None

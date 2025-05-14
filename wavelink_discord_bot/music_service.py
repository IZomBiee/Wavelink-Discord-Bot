import logging
import subprocess
import time
import os

import wavelink
import discord

from discord.ext import commands
import custom_inputs

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
        
        index = await custom_inputs.emoji_numeric_menu(self.bot, interaction, f"Write number of track on {tracks[0].source}",
        [i.title for i in tracks])
        if index == -1:
            return None
        else:
            return tracks[index]

    async def search(self, interaction:discord.Interaction, promt:str, source:str) -> wavelink.Playable:
        logging.info(f'Search {promt=} {source=}...')
        sources = {'youtube':wavelink.TrackSource.YouTube,
        'youtube_music':wavelink.TrackSource.YouTubeMusic,
        'soundcloud':wavelink.TrackSource.SoundCloud}
  
        try:
            if source == None: raise KeyError
            source = sources[source.strip().lower()]
        except KeyError:
            try:
                source = sources[os.getenv('basic_source')]
            except KeyError:
                logging.error('Base source not identified or misspelled!')
                return None
        
        tracks: wavelink.Search = await wavelink.Playable.search(promt, source=source)
        logging.debug(f'Searched tracks: {tracks}')
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

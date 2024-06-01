import logging
import os

import discord
import wavelink

from discord.ext import commands
from discord import app_commands
from music_service import MusicService
from dotenv import load_dotenv
load_dotenv()

class Music(commands.Cog):
    def __init__(self, bot:commands.Bot) -> None:
        logging.info('Load music cog...')
        self.bot = bot
        self.player: wavelink.player.Player = None
        self.music_service = MusicService(bot)
        self.last_interaction = None

    async def cog_load(self) -> None:
        logging.info('Setupe WaveLink...')
        nodes = [wavelink.Node(uri=f"http://{os.getenv('lavalink_ip')}:{os.getenv('lavalink_port')}",
                               password=f"{os.getenv('lavalink_password')}",
                               inactive_player_timeout=int(os.getenv('leave_inactive_time')))]
        await wavelink.Pool.connect(nodes=nodes, client=self.bot, cache_capacity=int(os.getenv('cache')))
    
    @commands.Cog.listener()
    async def on_wavelink_node_ready(self, payload: wavelink.NodeReadyEventPayload) -> None:
        logging.info(f'WaveLink connection established!')
        
    @commands.Cog.listener()
    async def on_wavelink_track_start(self, payload: wavelink.TrackStartEventPayload) -> None:
        logging.info(f'Playing track {payload.track.title}')
        embed = discord.Embed(title=f'Now play: {payload.track.title}',
                              description=f'Lenth: {MusicService.mil_to_time(payload.track.length)}\nURL: {payload.track.uri}',
                              color=0x336EFF)
        if payload.track.artwork:
            embed.set_image(url=payload.track.artwork)

        await self.last_interaction.channel.send(embed=embed)
        
    @commands.Cog.listener()
    async def on_wavelink_track_end(self, payload:wavelink.TrackEndEventPayload):   
        logging.info(f'Track {payload.track.title} ended')
        if len(self.player.queue):
            track = self.player.queue.get()
            await self.player.play(track, start=track.pass_sec*1000)

    @commands.Cog.listener()
    async def on_wavelink_inactive_player(self, payload:wavelink.Player):
        logging.info('Disconnect because inactive...')
        await self.stop(None)
    
    @commands.bot.hybrid_command(name='play', with_app_command=True, description='Add track from title or url to queue')
    @app_commands.guilds(discord.Object(id=os.getenv('guild')))
    @app_commands.describe(promt='Url or title of video',
                           source='Where find music. There are youtube, youtube music, soundcloud',
                           pass_sec='What amount of secounds skip')
    async def play(self, interaction: discord.Interaction, *, promt:str, source:str=None, pass_sec:int=0) -> None:
        if not await self.bot.check_channel_id(interaction):return
        logging.info(f'Command play {promt=}...')
        self.last_interaction = interaction
        if not await self.check_player(interaction):return

        track = await self.music_service.search(interaction, promt, source)
        if track == None:return
        track.pass_sec = pass_sec

        if self.player.current is None:
            await self.player.play(track, start=pass_sec*1000)
        else:
            await self.player.queue.put_wait(track)
            embed = discord.Embed(title=f'Added to queue: {track.title}',
                              description=f'Lenth: {MusicService.mil_to_time(track.length)}\nURL: {track.uri}',
                              color=0x336EFF)
            if track.artwork:
                embed.set_image(url=track.artwork)
            await self.last_interaction.channel.send(embed=embed)
    
    @commands.bot.hybrid_command(name='fplay', with_app_command=True, description='Play track from title or url to queue')
    @app_commands.guilds(discord.Object(id=os.getenv('guild')))
    @app_commands.describe(promt='Url or title of video',
                           source='Where find music. There are youtube, youtube music, soundcloud',
                           pass_sec='What amount of secounds skip') 
    async def fplay(self, interaction: discord.Interaction, *, promt:str, source:str=None, pass_sec:int=0) -> None:
        if not await self.bot.check_channel_id(interaction):return
        logging.info(f'Command fplay {promt=} {source=} {pass_sec=}...')
        self.last_interaction = interaction
        if not await self.check_player(interaction):return

        track = await self.music_service.search(interaction, promt, source)
        if track is not None:
            await self.player.stop()
            await self.player.play(track, start=pass_sec*1000)
    
    @commands.bot.hybrid_command(name='skip', with_app_command=True, description='Skip track')
    @app_commands.guilds(discord.Object(id=os.getenv('guild')))
    async def skip(self, interaction: discord.Interaction) -> None:
        if not await self.bot.check_channel_id(interaction):return
        logging.info('Command skip...')
        self.last_interaction = interaction
        if self.player == None or self.player.current == None:
            return await interaction.reply("Bot doesn't play anything!") 
        else:
            logging.info(f'{self.player.current.title} skiped')
            await self.player.skip(force=True)
            await interaction.reply('Track skiped!')

    @commands.bot.hybrid_command(name='stop', with_app_command=True, description='Stop bot')
    @app_commands.guilds(discord.Object(id=os.getenv('guild')))
    async def stop(self, interaction: discord.Interaction) -> None:
        if interaction != None:
            if not await self.bot.check_channel_id(interaction):return
        logging.info('Command stop...')
        if self.player == None:
            return await interaction.reply('Bot is already stoped!')
        else:
            logging.info('Stoped')
            await self.player.disconnect()
            await self.player.stop()
            self.player = None
            if interaction != None:
                return await interaction.reply('Bot is stoped!')

    @commands.bot.hybrid_command(name='volume', with_app_command=True, description='Set volume to bot')
    @app_commands.guilds(discord.Object(id=os.getenv('guild')))
    @app_commands.describe(volume='Volume from 0% to 1000%')
    async def volume(self, interaction: discord.Interaction, volume:int) -> None:
        if not await self.bot.check_channel_id(interaction):return
        logging.info(f'Command volume {volume=}...')
        if self.player == None:
            return await interaction.reply('Bot is stoped!')
        else:
            logging.info(f'Volume setted to {volume}')
            await wavelink.Player.set_volume(self.player, volume)
            await interaction.reply('Volume is changed')
    
    @commands.bot.hybrid_command(name='pause', with_app_command=True, description='Pause or resume bot')
    @app_commands.guilds(discord.Object(id=os.getenv('guild')))
    async def pause(self, interaction: discord.Interaction) -> None:
        if not await self.bot.check_channel_id(interaction):return
        logging.info(f'Command pause...')
        if self.player == None:
            return await interaction.reply('Bot is stoped!')
        else:
            if self.player.paused:
                self.player.pause(False)
                logging.info('Bot resumed')
                await interaction.reply('Bot is resumed!')
            else:
                self.player.pause(True)
                logging.info('Bot paused')
                await interaction.reply('Bot is paused!')

    @commands.bot.hybrid_command(name='queue', with_app_command=True, description='Show bot queue')
    @app_commands.guilds(discord.Object(id=os.getenv('guild')))
    async def queue(self, interaction: discord.Interaction) -> None:
        if not await self.bot.check_channel_id(interaction):return
        logging.info(f'Command queue {len(self.player.queue)=}...')
        if self.player == None:
            return await interaction.reply('Bot is stoped!')
        elif len(self.player.queue) == 0:
            return await interaction.reply('Queue is empty!')
        else:
            embed = discord.Embed(title=f"Queue", color=0x336EFF)
            for index, track in enumerate(self.player.queue):
                embed.add_field(name=f'{index+1}. {track.title}',
                                value=f"Lenth: {MusicService.mil_to_time(track.length)}", inline=True)
            await interaction.reply(embed=embed)
        
    @commands.bot.hybrid_command(name='filter', with_app_command=True,
                                 description='Add pitch, speed and rate divided by 100')
    @app_commands.guilds(discord.Object(id=os.getenv('guild')))
    async def filter(self, interaction: discord.Interaction,
                     pitch:int=100, speed:int=100, rate:int=100) -> None:
        if not await self.bot.check_channel_id(interaction):return
        logging.info(f'Command filter {pitch=} {speed=} {rate=}')
        if self.player == None:
            return await interaction.reply("Bot is stoped!")
        elif self.player.current == None:
            return await interaction.reply("Bot doesn't play anything!")
        else:
            filters: wavelink.Filters = self.player.filters
            filters.timescale.set(pitch=pitch/100, speed=speed/100, rate=rate/100)
            await self.player.set_filters(filters)
            await interaction.reply('Filters are active! (Maybe need wait few seconds)')

    @commands.bot.hybrid_command(name='time', with_app_command=True, description='Skips a certain number of seconds')
    @app_commands.guilds(discord.Object(id=os.getenv('guild')))
    @app_commands.describe(sec='Amount of seconds')
    async def time(self, interaction: discord.Interaction, sec:int) -> None:
        if not await self.bot.check_channel_id(interaction):return
        logging.info(f'Command time {sec=}...')
        if self.player == None:
            return await interaction.reply('Bot is stoped!')
        elif self.player.current == None:
            return await interaction.reply("Bot doesn't play anything!")
        else:
            await self.player.seek(sec*1000)
            await interaction.reply('A certain number of seconds was skiped')

    async def check_player(self, interaction:discord.Interaction) -> bool:
        voice_channel = await MusicService.get_voice_channel(interaction)
        if voice_channel == None:return False
        elif self.player == None:
            self.player = await voice_channel.connect(cls=wavelink.Player)
            return True
        elif self.player._connected:
            if len(self.player.channel.voice_states.keys()) <= 1:
                await self.player.move_to(voice_channel)
                return True
            elif self.player.channel == voice_channel: return True
            else: 
                await interaction.reply('Bot play in other channel')
                return False

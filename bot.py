import discord
from discord.ext import commands
from discord import FFmpegPCMAudio
from discord import app_commands
import yt_dlp
import os
from dotenv import load_dotenv

load_dotenv()
TOKEN = os.getenv('DISCORD_TOKEN')

intents = discord.Intents.default()
bot = commands.Bot(command_prefix='!', intents=intents)

FFMPEG_OPTIONS = {
    'before_options': '-reconnect 1 -reconnect_streamed 1 -reconnect_delay_max 5',
    'options': '-vn'
}

YDL_OPTIONS = {
    'format': 'bestaudio/best',
    'noplaylist': True,
    'quiet': True
}

@bot.event
async def on_ready():
    guild = discord.Object(id=1487741438774214730)
    bot.tree.copy_global_to(guild=guild)
    await bot.tree.sync(guild=guild)
    print(f'Bot connecté en tant que {bot.user}')

@bot.tree.command(name="play", description="Jouer une musique depuis YouTube")
async def play(interaction: discord.Interaction, url: str):
    if not interaction.user.voice:
        await interaction.response.send_message("Tu dois être dans un salon vocal !")
        return

    channel = interaction.user.voice.channel

    await interaction.response.defer()

    if interaction.guild.voice_client is None:
        await channel.connect()
    else:
        await interaction.guild.voice_client.move_to(channel)

    with yt_dlp.YoutubeDL(YDL_OPTIONS) as ydl:
        info = ydl.extract_info(url, download=False)
        url2 = info['url']
        title = info.get('title', 'Musique')

    interaction.guild.voice_client.stop()
    interaction.guild.voice_client.play(FFmpegPCMAudio(url2, **FFMPEG_OPTIONS))
    await interaction.followup.send(content=f'🎵 En cours de lecture : **{title}**')

@bot.tree.command(name="pause", description="Mettre en pause la musique")
async def pause(interaction: discord.Interaction):
    if interaction.guild.voice_client and interaction.guild.voice_client.is_playing():
        interaction.guild.voice_client.pause()
        await interaction.response.send_message('⏸️ Musique en pause')
    else:
        await interaction.response.send_message('Aucune musique en cours !')

@bot.tree.command(name="resume", description="Reprendre la musique")
async def resume(interaction: discord.Interaction):
    if interaction.guild.voice_client and interaction.guild.voice_client.is_paused():
        interaction.guild.voice_client.resume()
        await interaction.response.send_message('▶️ Lecture reprise')
    else:
        await interaction.response.send_message('Aucune musique en pause !')

@bot.tree.command(name="stop", description="Arrêter la musique et déconnecter le bot")
async def stop(interaction: discord.Interaction):
    if interaction.guild.voice_client:
        interaction.guild.voice_client.stop()
        await interaction.guild.voice_client.disconnect()
        await interaction.response.send_message('⏹️ Musique arrêtée et bot déconnecté')
    else:
        await interaction.response.send_message('Le bot nest pas dans un salon vocal !')

bot.run(TOKEN)

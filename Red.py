import discord
from discord.ext import commands, tasks
from discord import app_commands
import random
import logging
import datetime
import os
from dotenv import load_dotenv

# Load .env variables
load_dotenv()
TOKEN = os.getenv('TOKEN')

# Logging setup
handler = logging.FileHandler(filename='discord.log', encoding='utf-8', mode='w')

# Intents setup
intents = discord.Intents.default()
intents.message_content = True
intents.members = True

# Bot setup
bot = commands.Bot(command_prefix='!', intents=intents)

# Quote list
quotes = [
    "The progressive historical role of capitalism may be summed up in two brief propositions: increase in>
    "If democracy, in essence, means the abolition of class domination, then why should not a socialist mi>
    "Attention must be devoted principally to raising the workers to the level of revolutionaries; it is n>
    "Experience has proved that, on certain very important questions of the proletarian revolution, all co>
    "A revolutionary class cannot but wish for the defeat of its government in a reactionary war."
    "All forms of the state have democracy for their truth, and for that reason are false to the extent th>
    "The state is based on this contradiction. It is based on the contradiction between public and private>
    "Communism is the riddle of history solved, and it knows itself to be this solution."
    "The philosophers have only interpreted the world, in various ways; the point is to change it."
    "War unleashes  ^`^s at the same time as the reactionary forces of the capitalist world  ^`^s the gene>
    "It takes a loud voice to make the deaf hear..."
]

# Slash command
@bot.tree.command(name="quote", description="Get a random communist quote.")
async def quote_command(interaction: discord.Interaction):
    selected = random.choice(quotes)
    await interaction.response.send_message(selected)# Store per-guild daily quote channels
daily_quote_channels = {}

# Slash command: setup daily quotes
@bot.tree.command(name="dailyquote", description="Send a daily quote to a selected channel.")
@app_commands.describe(channel="Select the channel to receive daily quotes")
async def daily_quote(interaction: discord.Interaction, channel: discord.TextChannel):
    guild_id = interaction.guild_id
    daily_quote_channels[guild_id] = channel.id
    await interaction.response.send_message(f" ^|^e Daily quotes will be sent to {channel.mention}!", ephe>

# Background task to send daily quote
@tasks.loop(time=datetime.time(hour=9, minute=0))  # UTC 9:00 daily
async def send_daily_quotes():
    for guild_id, channel_id in daily_quote_channels.items():
        channel = bot.get_channel(channel_id)
        if channel:
            quote = random.choice(quotes)
            try:
                await channel.send(f" ^=^s^| Daily Quote:\n> {quote}")
            except Exception as e:
                print(f"Failed to send quote to {channel.name}: {e}")

# Sync commands & start loop
@bot.event
async def on_ready():
    await bot.tree.sync()
    send_daily_quotes.start()
    print(f"Bot ready as {bot.user}")


# Run bot
bot.run(TOKEN)

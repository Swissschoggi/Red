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

# Quote list
quotes = [
    "The progressive historical role of capitalism may be summed up in two brief propositions: increase in the productivity of labor and increase in the socialization of labor.",
    "If democracy, in essence, means the abolition of class domination, then why should not a socialist minister charm the whole bourgeois world by orations on class collaboration?",
    "Attention must be devoted principally to raising the workers to the level of revolutionaries; it is not enough to drag the revolution down to the level of the workers.",
    "Experience has proved that, on certain very important questions of the proletarian revolution, all countries will inevitably have to do what Russia has done.",
    "A revolutionary class cannot but wish for the defeat of its government in a reactionary war.",
    "All forms of the state have democracy for their truth, and for that reason are false to the extent that they are not democracy.",
    "The state is based on this contradiction. It is based on the contradiction between public and private life, between universal and particular interests. For this reason, the state must confine itself to formal, negative activities",
    "Communism is the riddle of history solved, and it knows itself to be this solution.",
    "The philosophers have only interpreted the world, in various ways; the point is to change it.",
    "War unleashes – at the same time as the reactionary forces of the capitalist world is the generating forces of social revolution which ferment in its depths.",
    "The seizure of power by armed force, the settlement of the issue by war, is the central task and the highest form of revolution.",
    "No matter how hard the reactionaries try to prevent the advance of the wheel of history, revolution will take place sooner or later and will surely triumph.",
    "There is no small enemy nor insignificant force, because no longer are there isolated peoples.",
    "At the risk of seeming ridiculous, let me say that the true revolutionary is guided by great feelings of love. It is impossible to think of a genuine revolutionary lacking this quality.",
    "Historical experience merits attention. A line or a viewpoint must be explained constantly and repeatedly. It won’t do to explain them only to a few people; they must be made known to the broad revolutionary masses.",
    "It takes a loud voice to make the deaf hear..."
]

facts = [
    "The Communist Manifesto was published in 1848 by Karl Marx and Friedrich Engels.",
    "Vladimir Lenin led the Bolshevik Revolution in Russia in 1917.",
    "Che Guevara was an Argentine revolutionary who played a major role in the Cuban Revolution.",
    "The Paris Commune of 1871 is often regarded as the first example of the working class taking power.",
    "The Red Army was established by Leon Trotsky during the Russian Civil War.",
    "Rosa Luxemburg was a Marxist theorist who opposed World War I and was executed in 1919.",
    "The hammer and sickle symbol originated in Soviet Russia and symbolizes the unity of workers and peasants.",
    "Mao Zedong led the Chinese Communist Party to victory in 1949, establishing the People's Republic of China.",
    "The phrase 'dictatorship of the proletariat' describes a transitional socialist state after revolution.",
    "Cuba became a socialist state after the 1959 revolution led by Fidel Castro and Che Guevara."
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

@bot.tree.command(name="stopdaily", description="Stop daily quotes in this server.")
async def stop_daily_command(interaction: discord.Interaction):
    guild_id = interaction.guild_id

    if guild_id in daily_quote_channels:
        del daily_quote_channels[guild_id]
        await interaction.response.send_message("🛑 Daily quotes have been stopped for this server.")
    else:
        await interaction.response.send_message("ℹ️ No daily quote is currently set for this server.")

@bot.tree.command(name="fact", description="Get a random communist or socialist historical fact.")
async def fact_command(interaction: discord.Interaction):
    selected_fact = random.choice(facts)
    await interaction.response.send_message(selected_fact)

# Sync commands & start loop
@bot.event
async def on_ready():
    await bot.tree.sync()
    send_daily_quotes.start()
    print(f"Bot ready as {bot.user}")


# Run bot
bot.run(TOKEN)

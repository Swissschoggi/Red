import discord
import asyncio
from discord.ext import commands, tasks
from discord import app_commands
import random
import logging
import datetime
import os
from dotenv import load_dotenv
import aiohttp
import json

DAILY_QUOTES_FILE = "daily_quote_channels.json"

def save_daily_quote_channels():
    with open(DAILY_QUOTES_FILE, "w", encoding="utf-8") as f:
        json.dump(daily_quote_channels, f)

def load_daily_quote_channels():
    global daily_quote_channels
    try:
        with open(DAILY_QUOTES_FILE, "r", encoding="utf-8") as f:
            daily_quote_channels = json.load(f)
    except (FileNotFoundError, json.JSONDecodeError):
        daily_quote_channels = {}

load_daily_quote_channels()

with open("data.json", "r", encoding="utf-8") as f:
    data = json.load(f)

quotes = data["quotes"]
facts = data["facts"]
reactionary_reactions = data["reactionary_reactions"]

load_dotenv()

OLLAMA_URL = os.getenv("OLLAMA_URL")
OLLAMA_MODEL = os.getenv("OLLAMA_MODEL")
OLLAMA_SYSTEM_PROMPT = os.getenv("OLLAMA_SYSTEM_PROMPT")

#Load .env variables
load_dotenv()
TOKEN = os.getenv('TOKEN')

#Logging setup
handler = logging.FileHandler(filename='discord.log', encoding='utf-8', mode='w')

#Intents setup
intents = discord.Intents.default()
intents.message_content = True
intents.members = True

#Bot setup
bot = commands.Bot(command_prefix='!', intents=intents)

daily_quote_channels = {}

readings = [
    {
        "title": "State and Revolution",
        "author": "Vladimir Lenin",
        "url": "https://www.marxists.org/archive/lenin/works/1917/staterev/"
    },
    {
        "title": "Wage-Labor and Capital",
        "author": "Karl Marx",
        "url": "https://www.marxists.org/archive/marx/works/1847/wage-labour/"
    },
    {
        "title": "Imperialism: The Highest Stage of Capitalism",
        "author": "Vladimir Lenin",
        "url": "https://www.marxists.org/archive/lenin/works/1916/imp-hsc/"
    },
    {
        "title": "On Practice",
        "author": "Mao Zedong",
        "url": "https://www.marxists.org/reference/archive/mao/selected-works/volume-1/mswv1_16.htm"
    },
    {
        "title": "Reform or Revolution",
        "author": "Rosa Luxemburg",
        "url": "https://www.marxists.org/archive/luxemburg/1900/reform-revolution/"
    },
    {
        "title": "Socialism: Utopian and Scientific",
        "author": "Friedrich Engels",
        "url": "https://www.marxists.org/archive/marx/works/1880/soc-utop/"
    },
    {
        "title": "'Left-Wing' Communism: An Infantile Disorder",
        "author": "Vladimir Lenin",
        "url": "https://www.marxists.org/archive/lenin/works/1920/lwc/"
    },
    {
        "title": "The Origin of the Family, Private Property and the State",
        "author": "Friedrich Engels",
        "url": "https://www.marxists.org/archive/marx/works/1884/origin-family/"
    },
    {
        "title": "Critique of the Gotha Programme",
        "author": "Karl Marx",
        "url": "https://www.marxists.org/archive/marx/works/1875/gotha/"
    },
    {
        "title": "What Is To Be Done?",
        "author": "Vladimir Lenin",
        "url": "https://www.marxists.org/archive/lenin/works/1901/witbd/"
    },
    {
        "title": "Dialectical and Historical Materialism",
        "author": "Joseph Stalin",
        "url": "https://www.marxists.org/reference/archive/stalin/works/1938/09.htm"
    },
    {
        "title": "Permanent Revolution",
        "author": "Leon Trotsky",
        "url": "https://www.marxists.org/archive/trotsky/1931/tpr/index.htm"
    },
]

import random

def get_random_quote():
    return random.choice(quotes)

def get_random_fact():
    return random.choice(facts)

def get_random_reaction():
    return random.choice(reactionary_reactions)

def get_random_figure():
    figure = random.choice(figures)
    return f"**{figure['name']}**\n{figure['bio']}"

def get_random_reading():
    return random.choice(readings)

#command for study group
@bot.tree.command(name="studygroup", description="Create a temporary study voice channel.")
@app_commands.describe(name="Name of the study group")
async def studygroup(interaction: discord.Interaction, name: str):
    guild = interaction.guild

    #Find a suitable category or create one if needed
    category = discord.utils.get(guild.categories, name="Study Groups")
    if category is None:
        category = await guild.create_category("Study Groups")

    #Create voice channel
    voice_channel = await guild.create_voice_channel(name=name, category=category)
    
    await interaction.response.send_message(
        f"✅ Created study group voice channel: **{voice_channel.name}**", ephemeral=True
    )
    
    #Background task to monitor the channel
    async def monitor_channel():
        await bot.wait_until_ready()
        while True:
            await asyncio.sleep(3600)
            channel = guild.get_channel(voice_channel.id)
            if channel and len(channel.members) == 0:
                await channel.delete(reason="Study group is empty.")
                break

    bot.loop.create_task(monitor_channel())
    
#command for figures
@bot.tree.command(name="randomfigure", description="Get a random revolutionary figure and short bio.")
async def random_figure_command(interaction: discord.Interaction):
    await interaction.response.send_message(get_random_figure())

@bot.command(name="figure")
async def figure_prefix(ctx):
    await ctx.send(get_random_figure())

#command for /reading
@bot.tree.command(name="reading", description="Get a recommended socialist or communist text to read.")
async def reading_command(interaction: discord.Interaction):
    item = get_random_reading()
    embed = discord.Embed(
        title=item["title"],
        url=item["url"],
        description=f"**Author:** {item['author']}\n[Read it here]({item['url']})",
        color=0xE00000
    )
    await interaction.response.send_message(embed=embed)

@bot.command(name="reading")
async def reading_prefix(ctx):
    item = get_random_reading()
    embed = discord.Embed(
        title=item["title"],
        url=item["url"],
        description=f"**Author:** {item['author']}\n[Read it here]({item['url']})",
        color=0xE00000
    )
    await ctx.send(embed=embed)

#command to get a Quote
@bot.tree.command(name="quote", description="Get a random communist quote.")
async def quote_command(interaction: discord.Interaction):
    await interaction.response.send_message(get_random_quote())

@bot.command(name="quote")
async def quote_prefix(ctx):
    await ctx.send(get_random_quote())

#command to get reactionary reactions
@bot.tree.command(name="reactionary", description="Get a random reactionary reaction.")
async def reactionary_command(interaction: discord.Interaction):
    await interaction.response.send_message(get_random_reaction())

@bot.command(name="reactionary")
async def reactionary_prefix(ctx):
    await ctx.send(get_random_reaction())

#command to setup daily quotes
@bot.tree.command(name="setdailyquotes", description="Set the channel and optional role for daily quotes.")
@app_commands.describe(channel="The channel for daily quotes", role="Optional role to mention")
@app_commands.checks.has_permissions(administrator=True)
async def set_daily_quotes(interaction: discord.Interaction, channel: discord.TextChannel, role: discord.Role = None):
    guild_id = str(interaction.guild_id)  # Use str for JSON keys consistency
    daily_quote_channels[guild_id] = {
        "channel_id": channel.id,
        "role_id": role.id if role else None
    }
    save_daily_quote_channels()  # <-- Save after change
    await interaction.response.send_message(
        f"✅ Daily quotes will be sent to {channel.mention}" + (f" and mention {role.mention}" if role else "")
    )

@bot.tree.command(name="stopdaily", description="Stop daily quotes in this server.")
@app_commands.checks.has_permissions(administrator=True)
async def stop_daily_command(interaction: discord.Interaction):
    guild_id = str(interaction.guild_id)
    if guild_id in daily_quote_channels:
        del daily_quote_channels[guild_id]
        save_daily_quote_channels()  # <-- Save after change
        await interaction.response.send_message("🛑 Daily quotes have been stopped for this server.")
    else:
        await interaction.response.send_message("ℹ️ No daily quote is currently set for this server.")
        
#command for a random communist fact
@bot.tree.command(name="fact", description="Get a random communist or socialist historical fact.")
async def fact_command(interaction: discord.Interaction):
    await interaction.response.send_message(get_random_fact())

@bot.command(name="fact")
async def fact_prefix(ctx):
    await ctx.send(get_random_fact())

#listening to /reading
@bot.event
async def on_ready():
    await bot.tree.sync()
    activity = discord.Activity(type=discord.ActivityType.listening, name="/reading")
    await bot.change_presence(activity=activity)
    print(f"Bot is ready. Logged in as {bot.user}")

#experimental LLM support
@bot.tree.command(name="asklenin", description="Ask Comrade Lenin a question.")
@app_commands.describe(question="Your question for Lenin")
async def ask_lenin(interaction: discord.Interaction, question: str):
    await interaction.response.defer()

    async with aiohttp.ClientSession() as session:
        try:
            payload = {
                "model": OLLAMA_MODEL,
                "prompt": question,
                "system": OLLAMA_SYSTEM_PROMPT,
                "stream": False
            }
            async with session.post(f"{OLLAMA_URL}/api/generate", json=payload) as resp:
                if resp.status == 200:
                    data = await resp.json()
                    response = data.get("response", "Lenin has no answer.")
                else:
                    response = f"⚠️ Ollama returned status code {resp.status}"
        except Exception as e:
            response = f"⚠️ Error querying Lenin: {str(e)}"

    # Send response safely, split if necessary
    if len(response) <= 2000:
        await interaction.followup.send(response)
    else:
        for i in range(0, len(response), 2000):
            chunk = response[i:i+2000]
            await interaction.followup.send(chunk)

#Sync commands & start loop
@bot.event
async def on_ready():
    await bot.tree.sync()
    send_daily_quotes.start()
    activity = discord.Activity(type=discord.ActivityType.listening, name="/reading")
    await bot.change_presence(activity=activity)
    print(f"Bot ready as {bot.user}")

#Run bot
bot.run(TOKEN)

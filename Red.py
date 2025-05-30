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
from datetime import timedelta
import urllib.parse

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

import hashlib

TANKIEMETER_FILE = "tankiemeter.json"

#load existing scores or initialize empty dict
try:
    with open(TANKIEMETER_FILE, "r", encoding="utf-8") as f:
        tankie_scores = json.load(f)
except (FileNotFoundError, json.JSONDecodeError):
    tankie_scores = {}

#save function
def save_tankie_scores():
    with open(TANKIEMETER_FILE, "w", encoding="utf-8") as f:
        json.dump(tankie_scores, f)

with open("data.json", "r", encoding="utf-8") as f:
    data = json.load(f)

quotes = data["quotes"]
facts = data["facts"]
reactionary_reactions = data["reactionary_reactions"]
debunks = data["debunks"]
figures = data["figures"]
crimes = data["crimes"]

quote_cycle = []
quote_index = 0

def load_data():
    with open("data.json", "r") as f:
        return json.load(f)

def save_data(data):
    with open("data.json", "w") as f:
        json.dump(data, f, indent=4)

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
    global quote_cycle, quote_index
    if not quote_cycle or quote_index >= len(quote_cycle):
        quote_cycle = random.sample(quotes, len(quotes))  # shuffled copy
        quote_index = 0
    quote = quote_cycle[quote_index]
    quote_index += 1
    return quote

fact_cycle = []
fact_index = 0

def get_random_fact():
    global fact_cycle, fact_index
    if not fact_cycle or fact_index >= len(fact_cycle):
        fact_cycle = random.sample(facts, len(facts))
        fact_index = 0
    fact = fact_cycle[fact_index]
    fact_index += 1
    return fact

def get_random_reaction():
    return random.choice(reactionary_reactions)

reaction_cycle = []
reaction_index = 0
def get_random_reaction():
    global reaction_cycle, reaction_index
    if not reaction_cycle or reaction_index >= len(reaction_cycle):
        reaction_cycle = random.sample(reactionary_reactions, len(reactionary_reactions))
        reaction_index = 0
    reaction = reaction_cycle[reaction_index]
    reaction_index += 1
    return reaction

figure_cycle = []
figure_index = 0
def get_random_figure():
    global figure_cycle, figure_index
    if not figure_cycle or figure_index >= len(figure_cycle):
        figure_cycle = random.sample(figures, len(figures))
        figure_index = 0
    figure = figure_cycle[figure_index]
    figure_index += 1
    return f"**{figure['name']}**\n{figure['bio']}"

reading_cycle = []
reading_index = 0
def get_random_reading():
    global reading_cycle, reading_index
    if not reading_cycle or reading_index >= len(reading_cycle):
        reading_cycle = random.sample(readings, len(readings))
        reading_index = 0
    reading = reading_cycle[reading_index]
    reading_index += 1
    return reading


debunk_cycle = []
debunk_index = 0
def get_random_debunk():
    global debunk_cycle, debunk_index
    if not debunk_cycle or debunk_index >= len(debunk_cycle):
        debunk_cycle = random.sample(debunks, len(debunks))
        debunk_index = 0
    debunk = debunk_cycle[debunk_index]
    debunk_index += 1
    return debunk

@bot.tree.command(name="reporttrotskyist", description="Report a Trotskyist and laugh at them.")
@app_commands.describe(user="The Trotskyist to report")
async def report_trotskyist(interaction: discord.Interaction, user: discord.Member):
    await interaction.response.send_message(f"HAHAHAHHAHAHAHA {user.mention} is a trotskyist laugh at them")

@bot.tree.command(name="reporttankie", description="Report a Tankie and laught at them.")
@app_commands.describe(user="The Tankie to report")
async def report_tankie(interaction: discord.Interaction, user: discord.Member):
    await interaction.response.send_message(f"HAHAHAHAHAHAHAHAH {user.mention} is a tankie, laught at them!")

def load_crimes():
    try:
        with open("data.json", "r") as f:
            data = json.load(f)
            return data["crimes"]
    except FileNotFoundError:
        print("Warning: data.json not found. Using default crimes.")
        return ["Counter-revolutionary activities"]  # Fallback crime
    
@bot.tree.command(name="gulag", description="send a counter revolutionary to the gulag working camps")
async def gulag(interaction: discord.Interaction, user: discord.Member, reason: str = "counterrevolutionary activities"):
    crimes = load_crimes()
    crime = random.choice(crimes)
    sentence_minutes = random.randint(1, 60)
    duration =discord.utils.utcnow() + datetime.timedelta(minutes=sentence_minutes)
    try:
        await user.timeout(duration, reason=f"gulag sentenced by {interaction.user.name}: {reason}")
    except discord.Forbidden:
        await interaction.response.send_message("the Red army lacks power to deal with this ciminal!")
        return
    await interaction.response.send_message(
        f" **soviet Tribunal verdict** \n"
        f"**{user.display_name}** has been sentenced to **{sentence_minutes} minutes** in the gulag!\n"
        f"**Crime:** {crime}\n"
        f"**Reason:** {reason}\n"
        f"*Glory to the party and the workers!*"
    )

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

@tasks.loop(hours=24)
async def send_daily_quotes():
    await bot.wait_until_ready()
    for guild_id, info in daily_quote_channels.items():
        channel = bot.get_channel(info["channel_id"])
        role_id = info.get("role_id")
        if channel:
            message = get_random_quote()
            if role_id:
                role_mention = f"<@&{role_id}>"
                await channel.send(f"{role_mention}\n{message}")
            else:
                await channel.send(message)

@bot.tree.command(name="stopdaily", description="Stop daily quotes in this server.")
@app_commands.checks.has_permissions(administrator=True)
async def stop_daily_command(interaction: discord.Interaction):
    guild_id = str(interaction.guild_id)
    if guild_id in daily_quote_channels:
        del daily_quote_channels[guild_id]
        save_daily_quote_channels()  # <-- Save after change
        await interaction.response.send_message("Daily quotes have been stopped for this server.")
    else:
        await interaction.response.send_message("No daily quote is currently set for this server.")
        
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

    #send response safely, split if necessary
    if len(response) <= 2000:
        await interaction.followup.send(response)
    else:
        for i in range(0, len(response), 2000):
            chunk = response[i:i+2000]
            await interaction.followup.send(chunk)

@bot.tree.command(name="debunk", description="Debunk a common anti-communist myth.")
async def debunk_command(interaction: discord.Interaction):
    await interaction.response.send_message(get_random_debunk())

@bot.command(name="debunk")
async def debunk_prefix(ctx):
    await ctx.send(get_random_debunk())

def load_scores():
    if os.path.exists(TANKIEMETER_FILE):
        with open(TANKIEMETER_FILE, "r") as f:
            return json.load(f)
    return {}

def save_scores(data):
    with open(TANKIEMETER_FILE, "w") as f:
        json.dump(data, f, indent=4)

tankiemeter_scores = load_scores()

@bot.tree.command(name="tankiemeter", description="Measure someone's tankie level.")
@app_commands.describe(user="The user to evaluate")
async def tankiemeter(interaction: discord.Interaction, user: discord.Member = None):
    user = user or interaction.user
    user_id = str(user.id)

    #check if already stored
    if user_id in tankiemeter_scores:
        entry = tankiemeter_scores[user_id]
        score = entry["score"]
        bonuses = entry["bonuses"]
    else:
        #generate deterministic base score
        hash_input = user.name + str(user.id)
        hash_digest = hashlib.md5(hash_input.encode()).hexdigest()
        base_score = int(hash_digest[:2], 16) % 101
        score = base_score
        bonuses = []

        #username-based bonuses
        username = user.name.lower()
        if "Lenin" in username:
            score += 10
            bonuses.append("Username contains 'Lenin'")
        elif "Marx" in username:
            score += 10
            bonuses.append("Username contains 'Marx'")
        elif "Mao" in username:
            score += 7
            bonuses.append("Username contains 'Mao'")
        elif "comrade" in username:
            score += 7
            bonuses.append("Username contains 'comrade'")
        elif "trotsky" in username:
            score -= 5
            bonuses.append("Username contains 'trotsky'")

        #role-based clues
        role_names = [role.name.lower() for role in user.roles]
        if any("Leninist" in r for r in role_names):
            score += 10
            bonuses.append("Role includes 'maoist'")
        if any("anarchist" in r for r in role_names):
            score -= 5
            bonuses.append("Role includes 'anarchist'")

        score = max(0, min(score, 100))

        #save result
        tankiemeter_scores[user_id] = {
            "username": user.name,
            "score": score,
            "bonuses": bonuses
        }
        save_scores(tankiemeter_scores)

    #tankie level description
    if score < 20:
        level = "🟩 Social Democrat – believes in healthcare but trusts NATO."
    elif score < 50:
        level = "🟨 Marxist-Leninist Curious – read Lenin once and liked the vibe."
    elif score < 80:
        level = "🟥 True Tankie – defends every 20th-century revolution."
    else:
        level = "🚩 Ultra Tankie – would defend the Berlin Wall with a hardcover Marx."

    bonus_msg = "\n".join(f"> {b}" for b in bonuses) if bonuses else "No bonus or penalty applied."

    await interaction.response.send_message(
        f"**{user.mention} scores {score}% on the Tankiemeter!**\n{level}\n\n**Analysis:**\n{bonus_msg}"
    )

#Election system

def save_elections():
    with open("elections.json", "w") as f:
        json.dump(elections, f)

def load_elections():
    global elections
    try:
        with open("elections.json", "r") as f:
            elections = json.load(f)
    except FileNotFoundError:
        elections = {}

elections = {}

@bot.tree.command(name="election_start", description="Start a new election for a role.")
@app_commands.describe(position="The position to elect for (e.g., moderator)")
@commands.has_permissions(administrator=True)
async def election_start(interaction: discord.Interaction, position: str):
    position = position.lower()
    if position in elections and elections[position]["open"]:
        await interaction.response.send_message(f"An election for '{position}' is already running.")
        return

    elections[position] = {
        "candidates": {},
        "open": True
    }
    await interaction.response.send_message(f"Election started for **{position}**! Use `/election_nominate` to join.")

@bot.tree.command(name="election_nominate", description="Nominate yourself or someone else as a candidate.")
@app_commands.describe(position="The position you're nominating for", user="The user you're nominating")
async def election_nominate(interaction: discord.Interaction, position: str, user: discord.Member = None):
    position = position.lower()
    nominee = user or interaction.user
    nominee_id = str(nominee.id)

    if position not in elections or not elections[position]["open"]:
        await interaction.response.send_message("No open election for that position.")
        return

    if nominee_id in elections[position]["candidates"]:
        await interaction.response.send_message(f"{nominee.display_name} is already nominated.")
        return

    elections[position]["candidates"][nominee_id] = 0
    await interaction.response.send_message(f"🗳️ {nominee.display_name} has been nominated for **{position}**.")

@bot.tree.command(name="election_vote", description="Vote for a candidate.")
@app_commands.describe(position="The position", user="The user you want to vote for")
async def election_vote(interaction: discord.Interaction, position: str, user: discord.Member):
    voter_id = str(interaction.user.id)
    candidate_id = str(user.id)
    position = position.lower()

    if position not in elections or not elections[position]["open"]:
        await interaction.response.send_message("No open election for that position.")
        return

    if candidate_id not in elections[position]["candidates"]:
        await interaction.response.send_message("That user is not a candidate.")
        return

    #prevent double vorting
    elections[position]["candidates"][candidate_id] += 1
    await interaction.response.send_message(f"Your vote for {user.display_name} has been counted.")

@bot.tree.command(name="election_close", description="Close election and announce winner.")
@app_commands.describe(position="The position to close election for")
@commands.has_permissions(administrator=True)
async def election_close(interaction: discord.Interaction, position: str):
    position = position.lower()

    if position not in elections or not elections[position]["open"]:
        await interaction.response.send_message("❌ No active election to close.")
        return

    elections[position]["open"] = False
    candidates = elections[position]["candidates"]
    if not candidates:
        await interaction.response.send_message("No candidates. Election void.")
        return

    winner_id = max(candidates, key=candidates.get)
    votes = candidates[winner_id]

    winner = await interaction.guild.fetch_member(int(winner_id))
    await interaction.response.send_message(f"🎉 {winner.mention} has won the **{position}** election with {votes} votes!")

    role = discord.utils.get(interaction.guild.roles, name="Moderator")
    if role and winner:
        await winner.add_roles(role)

@bot.tree.command(name="election_status", description="View current status of an ongoing election.")
@app_commands.describe(position="The position you want to check the election for")
async def election_status(interaction: discord.Interaction, position: str):
    position = position.lower()

    if position not in elections:
        await interaction.response.send_message("❌ There is no election by that name.")
        return

    election = elections[position]

    embed = discord.Embed(
        title=f"📊 Election Status – {position.title()}",
        description="Here are the current candidates and vote counts:",
        color=0xE00000
    )

    embed.set_footer(text="Election is currently open." if election["open"] else "Election is closed.")
    await interaction.response.send_message(embed=embed)

from bs4 import BeautifulSoup

@bot.tree.command(name="define", description="Get a definition from ProleWiki.")
@app_commands.describe(term="The term you'd like to look up (e.g. dialectical materialism)")
async def define_command(interaction: discord.Interaction, term: str):
    await interaction.response.defer()

    # Normalize the search term
    title = term.strip().lower().replace(" ", "_")
    url = f"https://en.prolewiki.org/wiki/{urllib.parse.quote(title)}"

    headers = {
        "User-Agent": "Mozilla/5.0 (compatible; RedBot/1.0; +https://github.com/yourbot)"
    }

    async with aiohttp.ClientSession() as session:
        async with session.get(url, headers=headers) as resp:
            if resp.status == 200:
                html = await resp.text()
                soup = BeautifulSoup(html, 'html.parser')
                p = soup.select_one("div.mw-parser-output > p")
                summary = p.text.strip() if p else "No summary found."

                await interaction.followup.send(
                    f"📖 **{term.title()}** — {summary}\n🔗 {url}"
                )
            else:
                await interaction.followup.send(
                    f"Could not find a ProleWiki article for **{term}**."
                )

#sync commands & start loop
@bot.event
async def on_ready():
    await bot.tree.sync()
    send_daily_quotes.start()
    activity = discord.Activity(type=discord.ActivityType.listening, name="/reading")
    await bot.change_presence(activity=activity)
    print(f"{bot.user.name} is ready to serve the Revolution!")

#Run bot
bot.run(TOKEN)

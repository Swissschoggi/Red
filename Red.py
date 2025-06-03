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
import hashlib

extensions = ["rank_system"]

async def load_extensions():
    for ext in extensions:
        await bot.load_extension(ext)

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
        json.dump(tankie_scores, f, indent=4)

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

READING_LOG_FILE = "reading_logs.json"

def load_reading_logs():
    try:
        with open(READING_LOG_FILE, "r", encoding="utf-8") as f:
            return json.load(f)
    except (FileNotFoundError, json.JSONDecodeError):
        return {}

def save_reading_logs(logs):
    with open(READING_LOG_FILE, "w", encoding="utf-8") as f:
        json.dump(logs, f, indent=4)

#Load .env variables
load_dotenv()
TOKEN = os.getenv('TOKEN')

#Logging setup
handler = logging.FileHandler(filename='discord.log', encoding='utf-8', mode='w')

#Intents setup
intents = discord.Intents.default()
intents.message_content = True
intents.members = True

def get_user_guilds():
    """Get the list of guild IDs the logged-in user belongs to"""
    return [str(g['id']) for g in session.get('guilds', [])]  # Ensure string IDs

def filter_for_user_guilds(data):
    """Filter elections/tankiemeter data to only show guilds the user can access"""
    user_guilds = get_user_guilds()
    return {
        key: value for key, value in data.items()
        if str(value.get("guild_id")) in user_guilds  # Match guild IDs
    }

# Tankiemeter functions
def load_tankiemeter():
    try:
        with open(TANKIEMETER_FILE, "r", encoding="utf-8") as f:
            return json.load(f)
    except (FileNotFoundError, json.JSONDecodeError):
        return []

def save_tankiemeter(data):
    with open(TANKIEMETER_FILE, "w", encoding="utf-8") as f:
        json.dump(data, f, indent=4)

# Initialize tankiemeter data
tankiemeter_data = load_tankiemeter()

with open("data.json", "r", encoding="utf-8") as f:
    data = json.load(f)

#Bot setup
bot = commands.Bot(command_prefix='!', intents=intents)

daily_quote_channels = {}

from aiohttp import web

async def handle_server_count(request):
    return web.json_response({"server_count": len(bot.guilds)})

async def start_web_server():
    app = web.Application()
    app.router.add_get('/servers', handle_server_count)
    runner = web.AppRunner(app)
    await runner.setup()
    site = web.TCPSite(runner, '0.0.0.0', 8346)
    await site.start()

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

elections = {}

def load_elections():
    global elections
    try:
        with open("elections.json", "r") as f:
            content = f.read().strip()
            elections = json.loads(content) if content else {}
    except (FileNotFoundError, json.JSONDecodeError):
        elections = {}

def save_elections():
    print("🧪 save_elections() CALLED")
    try:
        with open("elections.json", "w") as f:
            json.dump(elections, f, indent=2)
        print("✅ Elections saved to elections.json")
    except Exception as e:
        print("❌ Failed to save elections:", e)

load_elections()

reaction_cycle = {}
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
load_elections()

def get_user_guilds():
    """Returns list of guild IDs the user belongs to"""
    return [g['id'] for g in session.get('guilds', [])]

def get_shared_guilds():
    """Returns guilds where both user and bot have access"""
    user_guilds = get_user_guilds()
    with open('/app/elections.json') as f:
        elections_data = json.load(f)
    bot_guilds = {election['guild_id'] for election in elections_data.values()}
    return set(user_guilds) & bot_guilds

@bot.tree.command(name="tankiemeter", description="Measure someone's tankie level.")
@app_commands.describe(user="The user to evaluate")
async def tankiemeter(interaction: discord.Interaction, user: discord.Member = None):
    user = user or interaction.user
    user_id = str(user.id)
    guild_id = str(interaction.guild.id)

    # Load existing scores or initialize if needed
    if guild_id not in tankie_scores:
        tankie_scores[guild_id] = {}
    
    guild_scores = tankie_scores[guild_id]

    # Check if already stored
    if user_id in guild_scores:
        entry = guild_scores[user_id]
        score = entry["score"]
        bonuses = entry["bonuses"]
    else:
        # Generate deterministic base score
        hash_input = user.name + str(user.id)
        hash_digest = hashlib.md5(hash_input.encode()).hexdigest()
        base_score = int(hash_digest[:2], 16) % 101
        score = base_score
        bonuses = []

        # Username-based bonuses
        username = user.name.lower()
        if "lenin" in username:
            score += 10
            bonuses.append("Username contains 'Lenin'")
        elif "marx" in username:
            score += 10
            bonuses.append("Username contains 'Marx'")
        elif "mao" in username:
            score += 7
            bonuses.append("Username contains 'Mao'")
        elif "comrade" in username:
            score += 7
            bonuses.append("Username contains 'comrade'")
        elif "trotsky" in username:
            score -= 5
            bonuses.append("Username contains 'trotsky'")

        # Role-based clues
        role_names = [role.name.lower() for role in user.roles]
        if any("leninist" in r for r in role_names):
            score += 10
            bonuses.append("Role includes 'Leninist'")
        if any("maoist" in r for r in role_names):
            score += 10
            bonuses.append("Role includes 'Maoist'")
        if any("anarchist" in r for r in role_names):
            score -= 5
            bonuses.append("Role includes 'anarchist'")

        score = max(0, min(score, 100))

        # Add chaos-based random events
        chaotic_events = [
            ("called himself a trotskyist once", -5),
            ("named their cat after a commie", +10),
            ("Listens to capitalist music", -6),
            ("Memes about gulags too often", +3),
            ("Follows CIA on Twitter", -12),
            ("Once defended Gorbachev", -7),
            ("Correctly used the term 'dialectics'", +4),
            ("Runs a Trotskyist meme page", -10),
            ("Listens to DPRK music", +5),
            ("Leftcom.", -3),
            ("Is used to agree with liberals to appease them", -20)
        ]

        random.shuffle(chaotic_events)
        for event, delta in chaotic_events[:random.randint(1, 3)]:
            score += delta
            bonuses.append(f"{event} ({'+' if delta > 0 else ''}{delta})")


        # Save result with guild context
        guild_scores[user_id] = {
            "username": user.name,
            "score": score,
            "bonuses": bonuses,
            "guild_id": guild_id
        }
        save_tankie_scores()

    # Tankie level description
    if score < 10:
        level = "Left-liberal – believes in healthcare but LOVEEES NATO."
    elif score < 25:
        level = "Socdem – Got class conscious but cant part with the system"
    elif score < 50:
        level = "Online tankie – Doesnt organize and spends his time online arguing with other commies"
    elif score < 65:
        level = "Armchair revolutionary - Sees himself as superior to everyone else and only reads, a lot"
    elif score < 90:
        level = "Revolutionary - Swears on his life that the USSR was the pinecale of human existence"
    else:
        level = "🚩 Ultra Tankie – would defend the Berlin Wall with a hardcover Marx."

    bonus_msg = "\n".join(f"> {b}" for b in bonuses) if bonuses else "No bonus or penalty applied."

    await interaction.response.send_message(
        f"**{user.mention} scores {score}% on the Tankiemeter!**\n{level}\n\n**Analysis:**\n{bonus_msg}"
    )

@bot.tree.command(name="tankiemeter_chart", description="Display a leaderboard of top tankies in this server.")
async def tankiemeter_chart(interaction: discord.Interaction):
    await interaction.response.defer()
    guild_id = str(interaction.guild.id)
    
    # Get scores for this guild only
    guild_scores = tankie_scores.get(guild_id, {})
    
    if not guild_scores:
        await interaction.followup.send("No Tankiemeter scores found for this server.")
        return

    # Sort by score descending
    sorted_scores = sorted(guild_scores.items(), key=lambda x: x[1]["score"], reverse=True)[:10]

    embed = discord.Embed(
        title="Tankiemeter Leaderboard",
        description="Top 10 comrades in this server by Tankiemeter score.",
        color=0xE00000
    )

    medals = ["🥇", "🥈", "🥉"] + ["🔴"] * 7

    for i, (user_id, entry) in enumerate(sorted_scores):
        try:
            user = await interaction.guild.fetch_member(int(user_id))
            name = user.display_name
        except:
            name = entry["username"]
        score = entry["score"]
        embed.add_field(name=f"{medals[i]} {name}", value=f"**{score}% Tankie**", inline=False)

    await interaction.followup.send(embed=embed)

@bot.tree.command(name="election_start", description="Start a new election for a role.")
@app_commands.describe(position="The position to elect for (e.g., moderator)")
@commands.has_permissions(administrator=True)
async def election_start(interaction: discord.Interaction, position: str):
    position = position.lower()
    if position in elections and elections[position]["open"]:
        await interaction.response.send_message(f"An election for '{position}' is already running.")
        return

    elections[position] = {
        "guild_id": str(interaction.guild.id),
        "candidates": {},
        "open": True
    }
    save_elections()
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
    save_elections()
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

    # Check if user has already voted
    if voter_id in elections[position].get("voters", []):
        await interaction.response.send_message("You have already voted in this election!", ephemeral=True)
        return

    if candidate_id not in elections[position]["candidates"]:
        await interaction.response.send_message("That user is not a candidate.", ephemeral=True)
        return

    # Record the vote and mark voter as having voted
    elections[position]["candidates"][candidate_id] += 1
    if "voters" not in elections[position]:
        elections[position]["voters"] = []
    elections[position]["voters"].append(voter_id)
    save_elections()
    
    await interaction.response.send_message(
        f"Your vote for has been counted.", 
        ephemeral=True
    )

@bot.tree.command(name="election_close", description="Close election and announce winner.")
@app_commands.describe(position="The position to close election for")
@commands.has_permissions(administrator=True)
async def election_close(interaction: discord.Interaction, position: str):
    position = position.lower()

    if position not in elections or not elections[position]["open"]:
        save_elections()
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
    candidates = election.get("candidates", {})

    embed = discord.Embed(
        title=f"📊 Election Status – {position.title()}",
        color=0xE00000
    )

    if not candidates:
        embed.description = "No candidates yet."
    else:
        description_lines = []
        for uid, votes in candidates.items():
            try:
                member = await interaction.guild.fetch_member(int(uid))
                name = member.display_name
            except:
                name = f"User {uid}"
            description_lines.append(f"**{name}** – `{votes}` vote(s)")

        embed.description = "\n".join(description_lines)

    embed.set_footer(text="Election is currently open." if election["open"] else "Election is closed.")
    await interaction.response.send_message(embed=embed)

@bot.tree.command(name="logbook", description="Log a book you've read.")
@app_commands.describe(title="Book title", author="Book author")
async def logbook(interaction: discord.Interaction, title: str, author: str):
    user_id = str(interaction.user.id)
    logs = load_reading_logs()

    if user_id not in logs:
        logs[user_id] = []

    logs[user_id].append({"title": title, "author": author})
    save_reading_logs(logs)

    await interaction.response.send_message(
        f"📚 Logged **{title}** by *{author}* to your reading list."
    )
    
@bot.tree.command(name="readinglist", description="View a user's reading list.")
@app_commands.describe(user="The user whose reading list you want to see")
async def readinglist(interaction: discord.Interaction, user: discord.Member = None):
    user = user or interaction.user
    user_id = str(user.id)
    logs = load_reading_logs()

    entries = logs.get(user_id, [])

    if not entries:
        await interaction.response.send_message(f"{user.display_name} has no books logged yet.")
        return

    embed = discord.Embed(
        title=f"{user.display_name}'s Reading List",
        color=0xE00000
    )

    for entry in entries[:25]:  # Discord embed field limit
        embed.add_field(name=entry["title"], value=entry["author"], inline=False)

    await interaction.response.send_message(embed=embed)

@bot.event
async def on_ready():

    # Sync slash commands
    await bot.tree.sync()

    # Start background tasks
    send_daily_quotes.start()
    await start_web_server()

    # Set bot presence
    activity = discord.Activity(type=discord.ActivityType.listening, name="/reading")
    await bot.change_presence(activity=activity)

    # Print login info
    print(f"Bot is ready. Logged in as {bot.user}")

#Run bot
bot.run(TOKEN)

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
import psycopg2
from psycopg2.extras import RealDictCursor
import asyncpg
import time
import praw
import json

# Load environment variables first
load_dotenv()
TOKEN = os.getenv('TOKEN')

extensions = ["rank_system"]

async def load_extensions():
    for ext in extensions:
        await bot.load_extension(ext)

DAILY_QUOTES_FILE = "daily_quote_channels.json"

# Database pool with initialization tracking
pool = None
db_initialized = False
db_initialization_lock = asyncio.Lock()

async def init_db(retries=5, delay=2):
    global pool, db_initialized
    
    async with db_initialization_lock:
        if db_initialized:
            return True
            
        for attempt in range(retries):
            try:
                print(f"🔄 Attempting database connection (attempt {attempt + 1}/{retries})...")
                
                pool = await asyncpg.create_pool(
                    dsn=os.getenv('DATABASE_URL'),
                    min_size=1,
                    max_size=10,
                    command_timeout=60
                )
                
                # Test the connection
                async with pool.acquire() as conn:
                    await conn.execute("""
                        CREATE TABLE IF NOT EXISTS elections (
                            id SERIAL PRIMARY KEY,
                            guild_id TEXT NOT NULL,
                            position TEXT NOT NULL,
                            candidate_name TEXT NOT NULL,
                            candidate_id TEXT NOT NULL,
                            votes INTEGER DEFAULT 0,
                            open BOOLEAN DEFAULT TRUE,
                            created_at TIMESTAMP DEFAULT NOW(),
                            UNIQUE(guild_id, position, candidate_id)
                        );
                        
                        CREATE TABLE IF NOT EXISTS election_voters (
                            id SERIAL PRIMARY KEY,
                            election_id INTEGER REFERENCES elections(id) ON DELETE CASCADE,
                            voter_id TEXT NOT NULL,
                            voted_at TIMESTAMP DEFAULT NOW(),
                            UNIQUE(election_id, voter_id)
                        );
                        
                        CREATE TABLE IF NOT EXISTS tankiemeter (
                            id SERIAL PRIMARY KEY,
                            guild_id TEXT NOT NULL,
                            user_id TEXT NOT NULL,
                            username TEXT NOT NULL,
                            score INTEGER DEFAULT 0,
                            bonuses JSONB DEFAULT '[]'::jsonb,
                            updated_at TIMESTAMP DEFAULT NOW(),
                            UNIQUE(guild_id, user_id)
                        );
                        
                        CREATE TABLE IF NOT EXISTS reading_logs (
                            id SERIAL PRIMARY KEY,
                            user_id TEXT NOT NULL,
                            title TEXT NOT NULL,
                            author TEXT NOT NULL,
                            logged_at TIMESTAMP DEFAULT NOW()
                        );

                        CREATE INDEX IF NOT EXISTS idx_tankiemeter_guild_score ON tankiemeter(guild_id, score DESC);
                        CREATE INDEX IF NOT EXISTS idx_elections_guild_position ON elections(guild_id, position);
                        CREATE INDEX IF NOT EXISTS idx_reading_logs_user ON reading_logs(user_id);
                    """)
                
                db_initialized = True
                print("🎉 Database initialization complete!")
                return True
                
            except Exception as e:
                print(f"❌ Database connection failed (attempt {attempt + 1}/{retries}): {e}")
                if attempt < retries - 1:
                    await asyncio.sleep(delay)
                else:
                    print("💥 All database connection attempts failed")
                    return False

async def ensure_db_connection():
    """Ensure database connection is available"""
    global pool, db_initialized
    
    if db_initialized and pool is not None:
        try:
            # Test if pool is still alive
            async with pool.acquire() as conn:
                await conn.execute("SELECT 1")
            return True
        except Exception:
            print("🔄 Database pool is stale, reinitializing...")
            db_initialized = False
            pool = None
    
    return await init_db()

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

try:
    with open(TANKIEMETER_FILE, "r", encoding="utf-8") as f:
        tankie_scores = json.load(f)
except (FileNotFoundError, json.JSONDecodeError):
    tankie_scores = {}

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

#database connection
def get_db_connection():
    return psycopg2.connect(os.getenv('DATABASE_URL'))

#async database connection for bot commands
async def get_async_db_connection():
    return await asyncpg.connect(os.getenv('DATABASE_URL'))

#tankiemeter functions
def load_tankiemeter():
    try:
        with open(TANKIEMETER_FILE, "r", encoding="utf-8") as f:
            return json.load(f)
    except (FileNotFoundError, json.JSONDecodeError):
        return []

def save_tankiemeter(data):
    with open(TANKIEMETER_FILE, "w", encoding="utf-8") as f:
        json.dump(data, f, indent=4)

#initialize tankiemeter data
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

@bot.tree.command(name="setdailyquotes", description="Set the channel and optional role for daily quotes.")
@app_commands.describe(channel="The channel for daily quotes", role="Optional role to mention")
async def set_daily_quotes(interaction: discord.Interaction, channel: discord.TextChannel, role: discord.Role = None):
    guild_id = str(interaction.guild_id)  # ADD THIS LINE
    daily_quote_channels[guild_id] = {
        "channel_id": channel.id,
        "role_id": role.id if role else None
    }
    save_daily_quote_channels()
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


load_elections()

def get_user_guilds():
    """Returns list of guild IDs the user belongs to"""
    return [g['id'] for g in session.get('guilds', [])]

@bot.tree.command(name="tankiemeter", description="Measure someone's tankie level.")
@app_commands.describe(user="The user to evaluate")
async def tankiemeter(interaction: discord.Interaction, user: discord.Member = None):
    # Defer response immediately to avoid timeout
    await interaction.response.defer()
    
    # Ensure database connection
    db_ok = await ensure_db_connection()
    if not db_ok or pool is None:
        await interaction.followup.send("❌ Database connection unavailable. Please try again later.")
        return

    user = user or interaction.user
    guild_id = str(interaction.guild.id)
    user_id = str(user.id)

    try:
        async with pool.acquire() as conn:
            existing_score = await conn.fetchrow(
                'SELECT score, bonuses FROM tankiemeter WHERE guild_id = $1 AND user_id = $2',
                guild_id, user_id
            )

            if existing_score:
                score = existing_score['score']
                # FIX: Properly handle the bonuses JSON array
                bonuses = existing_score['bonuses'] or []
                # Ensure bonuses is a list, not a string
                if isinstance(bonuses, str):
                    try:
                        bonuses = json.loads(bonuses)
                    except:
                        bonuses = []
            else:
                # deterministic base score
                hash_input = user.name + str(user.id)
                hash_digest = hashlib.md5(hash_input.encode()).hexdigest()
                base_score = int(hash_digest[:2], 16) % 101
                score = base_score
                bonuses = []

                # username bonuses
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
                    bonuses.append("Username contains 'Trotsky'")

                # role-based bonuses
                role_names = [role.name.lower() for role in user.roles]
                if any("leninist" in r for r in role_names):
                    score += 10
                    bonuses.append("Role includes 'Leninist'")
                if any("maoist" in r for r in role_names):
                    score += 10
                    bonuses.append("Role includes 'Maoist'")
                if any("anarchist" in r for r in role_names):
                    score -= 5
                    bonuses.append("Role includes 'Anarchist'")

                # chaos events
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

                score = max(0, min(score, 100))

                # FIX: Store bonuses as proper JSON
                await conn.execute('''
                    INSERT INTO tankiemeter (guild_id, user_id, username, score, bonuses)
                    VALUES ($1, $2, $3, $4, $5::jsonb)
                    ON CONFLICT (guild_id, user_id) 
                    DO UPDATE SET score = $4, bonuses = $5::jsonb, updated_at = NOW()
                ''', guild_id, user_id, user.name, score, bonuses)

        # tankie level description
        if score < 10:
            level = "Left-liberal – believes in healthcare but LOVEEES NATO."
        elif score < 25:
            level = "Socdem – Got class conscious but can't part with the system"
        elif score < 50:
            level = "Online tankie – Doesn't organize and spends his time online arguing with other commies"
        elif score < 65:
            level = "Armchair revolutionary – Sees himself as superior to everyone else and only reads, a lot"
        elif score < 90:
            level = "Revolutionary – Swears on his life that the USSR was the pinnacle of human existence"
        else:
            level = "🚩 Ultra Tankie – would defend the Berlin Wall with a hardcover Marx."

        # FIX: Properly format bonuses
        if bonuses and isinstance(bonuses, list):
            bonus_msg = "\n".join(f"> {bonus}" for bonus in bonuses)
        else:
            bonus_msg = "No bonus or penalty applied."

        await interaction.followup.send(
            f"**{user.mention} scores {score}% on the Tankiemeter!**\n{level}\n\n**Analysis:**\n{bonus_msg}"
        )
    
    except Exception as e:
        print(f"Error in tankiemeter command: {e}")
        await interaction.followup.send("❌ Sorry, I encountered an error processing your request.")

# Add a debug command to check database status
@bot.tree.command(name="dbstatus", description="Check database connection status")
async def dbstatus(interaction: discord.Interaction):
    await interaction.response.defer()
    
    db_ok = await ensure_db_connection()
    if db_ok and pool is not None:
        try:
            async with pool.acquire() as conn:
                server_count = await conn.fetchval("SELECT COUNT(*) FROM tankiemeter")
            await interaction.followup.send(f"✅ Database connection is working! Tankiemeter records: {server_count}")
        except Exception as e:
            await interaction.followup.send(f"⚠️ Database connected but query failed: {e}")
    else:
        await interaction.followup.send("❌ Database connection failed")

@bot.tree.command(name="tankiemeter_chart", description="Display a leaderboard of top tankies in this server.")
async def tankiemeter_chart(interaction: discord.Interaction):
    await interaction.response.defer()
    guild_id = str(interaction.guild.id)
    
    conn = await get_async_db_connection()
    
    #Get top 10 scores for this guild
    scores = await conn.fetch('''
        SELECT username, score, bonuses 
        FROM tankiemeter 
        WHERE guild_id = $1 
        ORDER BY score DESC 
        LIMIT 10
    ''', guild_id)
    
    await conn.close()

    if not scores:
        await interaction.followup.send("No Tankiemeter scores found for this server.")
        return

    embed = discord.Embed(
        title="Tankiemeter Leaderboard",
        description="Top 10 comrades in this server by Tankiemeter score.",
        color=0xE00000
    )

    medals = ["🥇", "🥈", "🥉"] + ["🔴"] * 7

    for i, record in enumerate(scores):
        embed.add_field(
            name=f"{medals[i]} {record['username']}", 
            value=f"**{record['score']}% Tankie**", 
            inline=False
        )

    await interaction.followup.send(embed=embed)

@bot.tree.command(name="election_start", description="Start a new election for a role.")
@app_commands.describe(position="The position to elect for (e.g., moderator)")
async def election_start(interaction: discord.Interaction, position: str):
    position = position.lower()
    guild_id = str(interaction.guild.id)
    
    conn = await get_async_db_connection()
    
    #Check if election already exists and is open
    existing = await conn.fetchrow(
        'SELECT id FROM elections WHERE guild_id = $1 AND position = $2 AND open = TRUE',
        guild_id, position
    )
    
    if existing:
        await conn.close()
        await interaction.response.send_message(f"An election for '{position}' is already running.")
        return

    #Create new election
    await conn.execute(
        'INSERT INTO elections (guild_id, position, candidate_name, candidate_id, votes) VALUES ($1, $2, $3, $4, $5)',
        guild_id, position, 'placeholder', 'placeholder', 0
    )
    
    await conn.close()
    await interaction.response.send_message(f"Election started for **{position}**! Use `/election_nominate` to join.")

@bot.tree.command(name="election_nominate", description="Nominate yourself or someone else as a candidate.")
@app_commands.describe(position="The position you're nominating for", user="The user you're nominating")
async def election_nominate(interaction: discord.Interaction, position: str, user: discord.Member = None):
    position = position.lower()
    nominee = user or interaction.user
    guild_id = str(interaction.guild.id)
    
    conn = await get_async_db_connection()
    
    #check if election exists and is open
    election = await conn.fetchrow(
        'SELECT id FROM elections WHERE guild_id = $1 AND position = $2 AND open = TRUE',
        guild_id, position
    )
    
    if not election:
        await conn.close()
        await interaction.response.send_message("No open election for that position.")
        return

    election_id = election['id']
    
    #Check if already nominated
    existing = await conn.fetchrow(
        'SELECT id FROM elections WHERE guild_id = $1 AND position = $2 AND candidate_id = $3',
        guild_id, position, str(nominee.id)
    )
    
    if existing:
        await conn.close()
        await interaction.response.send_message(f"{nominee.display_name} is already nominated.")
        return

    #Add candidate
    await conn.execute(
        'INSERT INTO elections (guild_id, position, candidate_name, candidate_id, votes) VALUES ($1, $2, $3, $4, $5)',
        guild_id, position, nominee.display_name, str(nominee.id), 0
    )
    
    await conn.close()
    await interaction.response.send_message(f"🗳️ {nominee.display_name} has been nominated for **{position}**.")

@bot.tree.command(name="election_vote", description="Vote for a candidate.")
@app_commands.describe(position="The position", user="The user you want to vote for")
async def election_vote(interaction: discord.Interaction, position: str, user: discord.Member):
    voter_id = str(interaction.user.id)
    candidate_id = str(user.id)
    guild_id = str(interaction.guild.id)
    position = position.lower()

    conn = await get_async_db_connection()

    # Find the election
    election = await conn.fetchrow(
        'SELECT id FROM elections WHERE guild_id = $1 AND position = $2 AND open = TRUE',
        guild_id, position
    )
    if not election:
        await conn.close()
        await interaction.response.send_message("❌ No open election for that position.")
        return

    election_id = election['id']

    # Check if candidate is valid
    candidate = await conn.fetchrow(
        'SELECT id FROM elections WHERE guild_id = $1 AND position = $2 AND candidate_id = $3 AND open = TRUE',
        guild_id, position, candidate_id
    )
    if not candidate:
        await conn.close()
        await interaction.response.send_message("❌ That user is not nominated in this election.")
        return

    # Check if voter already voted
    already_voted = await conn.fetchrow(
        'SELECT id FROM election_voters WHERE election_id = $1 AND voter_id = $2',
        election_id, voter_id
    )
    if already_voted:
        await conn.close()
        await interaction.response.send_message("❌ You have already voted in this election.")
        return

    # Record the vote
    await conn.execute(
        'INSERT INTO election_voters (election_id, voter_id) VALUES ($1, $2)',
        election_id, voter_id
    )
    await conn.execute(
        'UPDATE elections SET votes = votes + 1 WHERE id = $1',
        candidate['id']
    )

    await conn.close()
    await interaction.response.send_message(f"✅ Your vote for **{user.display_name}** has been recorded!")


@bot.tree.command(name="election_close", description="Close election and announce winner.")
@app_commands.describe(position="The position to close election for")
async def election_close(interaction: discord.Interaction, position: str):
    position = position.lower()
    guild_id = str(interaction.guild.id)

    conn = await get_async_db_connection()
    
    #Check if election exists and is open
    election = await conn.fetchrow(
        'SELECT id FROM elections WHERE guild_id = $1 AND position = $2 AND open = TRUE',
        guild_id, position
    )
    
    if not election:
        await conn.close()
        await interaction.response.send_message("❌ No active election to close.")
        return

    election_id = election['id']
    
    #get all candidates and their votes for this election
    candidates = await conn.fetch(
        'SELECT candidate_name, candidate_id, votes FROM elections WHERE guild_id = $1 AND position = $2 AND candidate_name != $3',
        guild_id, position, 'placeholder'
    )
    
    if not candidates:
        await conn.close()
        await interaction.response.send_message("No candidates. Election void.")
        return

    #gind the winner
    winner = max(candidates, key=lambda x: x['votes'])
    winner_name = winner['candidate_name']
    winner_id = winner['candidate_id']
    votes = winner['votes']

    #close the election
    await conn.execute(
        'UPDATE elections SET open = FALSE WHERE guild_id = $1 AND position = $2',
        guild_id, position
    )
    
    await conn.close()

    try:
        winner_member = await interaction.guild.fetch_member(int(winner_id))
        winner_mention = winner_member.mention
    except:
        winner_mention = winner_name

    await interaction.response.send_message(f"🎉 {winner_mention} has won the **{position}** election with {votes} votes!")

    role_name = position.title()  # or use a mapping for specific roles
    role = discord.utils.get(interaction.guild.roles, name=role_name)
    if role and winner_member:
        try:
            await winner_member.add_roles(role)
            await interaction.followup.send(f"✅ {role_name} role assigned to {winner_mention}!")
        except discord.Forbidden:
            await interaction.followup.send("❌ Could not assign role (missing permissions).")

@bot.tree.command(name="logbook", description="Log a book you've read.")
@app_commands.describe(title="Book title", author="Book author")
async def logbook(interaction: discord.Interaction, title: str, author: str):
    user_id = str(interaction.user.id)
    
    conn = await get_async_db_connection()
    await conn.execute(
        'INSERT INTO reading_logs (user_id, title, author) VALUES ($1, $2, $3)',
        user_id, title, author
    )
    await conn.close()

    await interaction.response.send_message(f"📚 Logged **{title}** by *{author}* to your reading list.")

@bot.tree.command(name="readinglist", description="View a user's reading list.")
@app_commands.describe(user="The user whose reading list you want to see")
async def readinglist(interaction: discord.Interaction, user: discord.Member = None):
    user = user or interaction.user
    user_id = str(user.id)
    
    conn = await get_async_db_connection()
    entries = await conn.fetch(
        'SELECT title, author, logged_at FROM reading_logs WHERE user_id = $1 ORDER BY logged_at DESC LIMIT 25',
        user_id
    )
    await conn.close()

    if not entries:
        await interaction.response.send_message(f"{user.display_name} has no books logged yet.")
        return

    embed = discord.Embed(title=f"{user.display_name}'s Reading List", color=0xE00000)

    for entry in entries:
        embed.add_field(name=entry['title'], value=f"by {entry['author']}", inline=False)

    await interaction.response.send_message(embed=embed)

#Function to initialize praw after the bot starts
def init_reddit():
    reddit = praw.Reddit(client_id=CLIENT_ID, client_secret=CLIENT_SECRET, user_agent=USER_AGENT)
    return reddit

#Fetch meme function using praw (in a thread)
async def fetch_communist_meme(reddit):
    loop = asyncio.get_event_loop()
    hot_posts = await loop.run_in_executor(None, lambda: list(reddit.subreddit("CommunismMemes").hot(limit=10)))

    image_posts = [(post.url, post.author.name) for post in hot_posts if post.url.endswith(('jpg', 'jpeg', 'png', 'gif'))]

    if image_posts:
        meme_url, author = random.choice(image_posts)  # Correct unpacking
        return meme_url, author
    else:
        return None, None

@bot.tree.command(name="meme", description="Get a random meme from r/communismmemes")
async def meme_command(interaction: discord.Interaction):
    await interaction.response.defer()

    try:
        reddit = praw.Reddit(
            client_id=os.getenv("REDDIT_CLIENT_ID"),
            client_secret=os.getenv("REDDIT_CLIENT_SECRET"),
            user_agent=os.getenv("REDDIT_USER_AGENT")
        )

        subreddit = reddit.subreddit("communismmemes")
        posts = [post for post in subreddit.hot(limit=50) if not post.stickied]
        post = random.choice(posts)

        embed = discord.Embed(
            title=post.title,
            url=f"https://reddit.com{post.permalink}",
            color=0xE00000
        )
        if post.url.endswith((".jpg", ".jpeg", ".png", ".gif")):
            embed.set_image(url=post.url)
        else:
            embed.description = post.url  # fallback if it's not an image

        await interaction.followup.send(embed=embed)

    except Exception as e:
        await interaction.followup.send(f"⚠️ Failed to fetch meme: {e}")

def save_server_count_to_db(count):
    conn = psycopg2.connect(os.getenv("DATABASE_URL"))
    cur = conn.cursor()
    cur.execute("""
        INSERT INTO server_counts (server_count, updated_at)
        VALUES (%s, NOW())
        ON CONFLICT (id) DO UPDATE SET server_count = EXCLUDED.server_count, updated_at = NOW()
    """, (count,))
    conn.commit()
    cur.close()
    conn.close()


@bot.event
async def on_ready():
    print(f"✅ {bot.user} has connected to Discord!")
    
    # Initialize database first
    print("🔄 Initializing database...")
    db_success = await init_db()
    
    if db_success:
        print("✅ Database initialized successfully")
    else:
        print("❌ Database initialization failed - some features may not work")
    
    # Sync commands
    try:
        await bot.tree.sync()
        print("✅ Commands synced")
    except Exception as e:
        print(f"❌ Command sync failed: {e}")
    
    # Start background tasks
    if not send_daily_quotes.is_running():
        send_daily_quotes.start()
        print("✅ Daily quotes task started")
    
    # Start web server
    try:
        await start_web_server()
        print("✅ Web server started")
    except Exception as e:
        print(f"❌ Web server failed: {e}")

    activity = discord.Activity(type=discord.ActivityType.listening, name="/reading")
    await bot.change_presence(activity=activity)

    print(f"🎉 Bot is fully ready. Logged in as {bot.user}")

# Run bot
if __name__ == "__main__":
    print("🚀 Starting bot...")
    bot.run(TOKEN)
import discord
from discord.ext import commands
from discord import app_commands
import json
import os

RANK_DATA_FILE = "rank_data.json"

def load_rank_data():
    if os.path.exists(RANK_DATA_FILE):
        with open(RANK_DATA_FILE, "r", encoding="utf-8") as f:
            return json.load(f)
    return {}

def save_rank_data(data):
    with open(RANK_DATA_FILE, "w", encoding="utf-8") as f:
        json.dump(data, f, indent=4)

# Define rank thresholds and names
RANKS = [
    (0, "🪦 Apolitical Lumpen"),
    (10, "🧢 Curious Comrade"),
    (25, "📚 Theory Enjoyer"),
    (50, "🚩 Vanguard of the Revolution"),
    (100, "🧨 Marxist Superweapon")
]

def get_rank(points):
    for threshold, name in reversed(RANKS):
        if points >= threshold:
            return name

class RankSystem(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        self.data = load_rank_data()

    def is_enabled(self, guild_id):
        return self.data.get("settings", {}).get(str(guild_id), {}).get("enabled", False)

    def set_enabled(self, guild_id, enabled: bool):
        gid = str(guild_id)
        if "settings" not in self.data:
            self.data["settings"] = {}
        self.data["settings"][gid] = {"enabled": enabled}
        save_rank_data(self.data)

    def add_points(self, user: discord.Member, amount: int):
        gid = str(user.guild.id)
        uid = str(user.id)

        if not self.is_enabled(user.guild.id):
            return None  # system disabled

        if gid not in self.data:
            self.data[gid] = {}
        if uid not in self.data[gid]:
            self.data[gid][uid] = {"points": 0, "last_rank": ""}

        entry = self.data[gid][uid]
        old_points = entry["points"]
        new_points = old_points + amount
        entry["points"] = new_points

        old_rank = get_rank(old_points)
        new_rank = get_rank(new_points)

        entry["last_rank"] = new_rank
        save_rank_data(self.data)

        if new_rank != old_rank:
            return new_rank
        return None

    @app_commands.command(name="rank", description="Check your revolutionary rank.")
    async def rank(self, interaction: discord.Interaction):
        uid = str(interaction.user.id)
        gid = str(interaction.guild.id)

        if not self.is_enabled(interaction.guild.id):
            await interaction.response.send_message("📛 Rank system is currently disabled on this server.", ephemeral=True)
            return

        points = self.data.get(gid, {}).get(uid, {}).get("points", 0)
        rank = get_rank(points)
        await interaction.response.send_message(f"🎖️ **Your Rank:** {rank}\n📈 **Points:** {points}")

    @app_commands.command(name="rank_toggle", description="Enable or disable the rank system for this server.")
    @app_commands.checks.has_permissions(administrator=True)
    @app_commands.describe(enabled="Enable or disable")
    async def rank_toggle(self, interaction: discord.Interaction, enabled: bool):
        self.set_enabled(interaction.guild.id, enabled)
        save_rank_data(self.data)
        state = "enabled" if enabled else "disabled"
        await interaction.response.send_message(f"✅ Rank system {state}.")

    async def reward_user(self, user: discord.Member, amount: int, channel=None):
        new_rank = self.add_points(user, amount)
        if new_rank and channel:
            await channel.send(f"🎉 {user.mention} has ranked up to **{new_rank}**! Glory to the revolution!")

async def setup(bot: commands.Bot):
    cog = RankSystem(bot)
    await bot.add_cog(cog)  # ✅ This is enough

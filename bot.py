import discord
from discord.ext import commands
import asyncio
import os
from dotenv import load_dotenv
from utils.config import delete_server_settings

load_dotenv()

TOKEN = os.getenv("DISCORD_TOKEN")
APPLICATION_ID = int(os.getenv("APPLICATION_ID"))

if not TOKEN or not APPLICATION_ID:
    print("❌ Error: Missing DISCORD_TOKEN or APPLICATION_ID in .env file")
    exit(1)

intents = discord.Intents.default()
intents.guilds = True
intents.messages = True

bot = commands.Bot(
    command_prefix=commands.when_mentioned,
    intents=intents,
    application_id=APPLICATION_ID
)

@bot.event
async def on_ready():
    print(f"✅ Logged in as {bot.user} (ID: {bot.user.id})")
    print("━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━")
    
    try:
        synced = await bot.tree.sync()
        print(f"✅ Synced {len(synced)} slash commands")
    except Exception as e:
        print(f"❌ Error syncing commands: {e}")
    await bot.change_presence(
        status=discord.Status.online,
        activity=discord.Activity(
            type=discord.ActivityType.watching, 
            name="for daily wisdom"
        )
    )
    print("━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━")
    print("✅ Bot is running!")

@bot.event
async def on_guild_join(guild):
    print(f"✅ Joined new server: {guild.name} (ID: {guild.id})")

@bot.event
async def on_guild_remove(guild):
    print(f"❌ Removed from server: {guild.name} (ID: {guild.id})")
    delete_server_settings(guild.id)

async def load_cogs():
    """Load all cog files"""
    cogs = ["cogs.setup", "cogs.quotes"]
    
    for cog in cogs:
        try:
            await bot.load_extension(cog)
            print(f"✅ Loaded {cog}")
        except Exception as e:
            print(f"❌ Failed to load {cog}: {e}")

async def main():
    async with bot:
        await load_cogs()
        await bot.start(TOKEN)

if __name__ == "__main__":
    try:
        asyncio.run(main())
    except KeyboardInterrupt:
        print("\n👋 Bot shutting down...")

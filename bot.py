import discord
from discord.ext import commands
import asyncio

from config import delete_server_settings

TOKEN = "MTM3Nzk5Njk1OTg5MzE2NDA1Mg.G7dbwN.grOXScpaAx4CSQ-3TCpaG0StehCRsM5285qDYo"
APPLICATION_ID = 1377996959893164052  # Replace with your actual application ID

intents = discord.Intents.default()

def no_prefix(bot, message):
    return []

bot = commands.Bot(
    command_prefix=no_prefix,
    intents=intents,
    application_id=APPLICATION_ID
)

@bot.event
async def on_ready():
    try:
        synced = await bot.tree.sync()
        print(f"✅ Synced {len(synced)} slash commands!")
    except Exception as e:
        print("❌ Error syncing commands:", e)

    print(f"✅ Logged in as {bot.user}")
    await bot.change_presence(
        status=discord.Status.online,
        activity=discord.Activity(type=discord.ActivityType.watching, name="New Daily Quotes")
    )

@bot.event
async def on_guild_remove(guild):
    delete_server_settings(guild.id)

async def main():
    try:
        await bot.load_extension("commands")
        await bot.load_extension("dailyquote")
    except Exception as e:
        print(f"❌ Error loading cogs: {e}")

    await bot.start(TOKEN)

asyncio.run(main())

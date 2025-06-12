import discord
from discord.ext import commands, tasks
from datetime import datetime, timedelta
import pytz
import asyncio
import json
import os
from config import get_server_settings
from quote_fetcher import fetch_quote

ERROR_DIR = "error-files"
os.makedirs(ERROR_DIR, exist_ok=True)

class DailyQuote(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        self.last_sent = {}
        self.send_daily_quote.start()

    def cog_unload(self):
        self.send_daily_quote.cancel()

    async def log_error(self, guild_id, error_message):
        """Logs errors into errors-{server-id}.json"""
        error_file = os.path.join(ERROR_DIR, f"errors-{guild_id}.json")
        errors = []

        if os.path.exists(error_file):
            with open(error_file, "r") as file:
                errors = json.load(file)

        errors.append({
            "timestamp": datetime.utcnow().isoformat(),
            "error": error_message
        })

        with open(error_file, "w") as file:
            json.dump(errors, file, indent=4)

    @tasks.loop(minutes=1)  # Main loop runs every minute
    async def send_daily_quote(self):
        await self.bot.wait_until_ready()
        now = datetime.utcnow()

        tasks_to_run = []
        for guild in self.bot.guilds:
            tasks_to_run.append(self.process_guild(guild, now))

        await asyncio.gather(*tasks_to_run)

    async def process_guild(self, guild, now):
        config = get_server_settings(guild.id)
        channel_id = config.get("channel_id")
        if not channel_id:
            return

        tz_name = config.get("timezone", "Europe/Brussels")
        try:
            tz = pytz.timezone(tz_name)
        except Exception:
            tz = pytz.timezone("Europe/Brussels")

        local_now = datetime.now(tz)
        quote_time = config.get("quote_time", "08:00")
        interval = config.get("interval", 24)

        try:
            hour, minute = map(int, quote_time.split(":"))
        except Exception:
            hour, minute = 8, 0  

        scheduled = local_now.replace(hour=hour, minute=minute, second=0, microsecond=0)
        if local_now < scheduled:
            scheduled -= timedelta(days=1)

        last_sent = self.last_sent.get(guild.id)
        should_send = False

        if last_sent is None:
            if local_now.hour == hour and local_now.minute == minute:
                should_send = True
        else:
            next_send = last_sent + timedelta(hours=interval)
            if local_now >= next_send:
                should_send = True

        if should_send:
            await self.precise_send(guild, channel_id)

    async def precise_send(self, guild, channel_id):
        """Ensures the message is sent **exactly at HH:MM:00**"""
        target_time = datetime.utcnow().replace(second=0, microsecond=0) + timedelta(minutes=1)

        while datetime.utcnow() < target_time:
            await asyncio.sleep(0.5)  # Check twice per second to ensure accuracy

        await self.send_quote(guild, channel_id)

    async def send_quote(self, guild, channel_id):
        try:
            channel = self.bot.get_channel(channel_id)
            if not channel:
                await self.log_error(guild.id, f"Channel ID {channel_id} not found.")
                return

            config = get_server_settings(guild.id)
            role_id = config.get("role_id")
            mention = f"<@&{role_id}>\n" if role_id else ""
            quote = fetch_quote()

            await channel.send(f"{mention}{quote}")
            self.last_sent[guild.id] = datetime.utcnow()

        except Exception as e:
            await self.log_error(guild.id, f"Error sending quote: {str(e)}")

async def setup(bot):
    await bot.add_cog(DailyQuote(bot))

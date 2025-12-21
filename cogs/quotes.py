import discord
from discord.ext import commands, tasks
from datetime import datetime, timedelta
import pytz
import json
import os
from utils.config import get_server_settings
from utils.quote_fetcher import fetch_quote

LAST_SENT_FILE = "last_sent.json"
ERROR_DIR = "error-files"
os.makedirs(ERROR_DIR, exist_ok=True)

class QuoteScheduler(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        self.last_sent = self.load_last_sent()
        self.quote_loop.start()

    def cog_unload(self):
        self.quote_loop.cancel()
        self.save_last_sent()

    def load_last_sent(self):
        """Load last sent timestamps from file"""
        if not os.path.exists(LAST_SENT_FILE):
            return {}
        
        try:
            with open(LAST_SENT_FILE, "r") as f:
                data = json.load(f)
                # Convert ISO strings to datetime objects
                return {
                    int(guild_id): datetime.fromisoformat(timestamp)
                    for guild_id, timestamp in data.items()
                }
        except Exception as e:
            print(f"❌ Error loading last_sent.json: {e}")
            return {}

    def save_last_sent(self):
        """Save last sent timestamps to file"""
        try:
            # Convert datetime objects to ISO strings
            data = {
                str(guild_id): timestamp.isoformat()
                for guild_id, timestamp in self.last_sent.items()
            }
            with open(LAST_SENT_FILE, "w") as f:
                json.dump(data, f, indent=4)
        except Exception as e:
            print(f"❌ Error saving last_sent.json: {e}")

    async def log_error(self, guild_id, error_message):
        """Log errors to guild-specific error file"""
        error_file = os.path.join(ERROR_DIR, f"errors-{guild_id}.json")
        errors = []

        if os.path.exists(error_file):
            try:
                with open(error_file, "r") as f:
                    errors = json.load(f)
            except:
                errors = []

        errors.append({
            "timestamp": datetime.utcnow().isoformat(),
            "error": error_message
        })

        # Keep only last 50 errors
        errors = errors[-50:]

        try:
            with open(error_file, "w") as f:
                json.dump(errors, f, indent=4)
        except Exception as e:
            print(f"❌ Error saving error log: {e}")

    @tasks.loop(minutes=1)
    async def quote_loop(self):
        """Main loop that checks every minute if quotes should be sent"""
        await self.bot.wait_until_ready()
        
        for guild in self.bot.guilds:
            try:
                await self.check_and_send_quote(guild)
            except Exception as e:
                print(f"❌ Error processing guild {guild.name}: {e}")
                await self.log_error(guild.id, f"Loop error: {str(e)}")

    async def check_and_send_quote(self, guild):
        """Check if a quote should be sent for this guild"""
        config = get_server_settings(guild.id)
        channel_id = config.get("channel_id")
        
        if not channel_id:
            return  # No channel configured

        # Get timezone
        tz_name = config.get("timezone", "Europe/Brussels")
        try:
            tz = pytz.timezone(tz_name)
        except:
            tz = pytz.timezone("Europe/Brussels")
            await self.log_error(guild.id, f"Invalid timezone: {tz_name}, using Europe/Brussels")

        # Get current time in server's timezone
        now = datetime.now(tz)
        
        # Parse scheduled time
        quote_time_str = config.get("quote_time", "08:00")
        try:
            hour, minute = map(int, quote_time_str.split(":"))
        except:
            hour, minute = 8, 0
            await self.log_error(guild.id, f"Invalid quote_time: {quote_time_str}, using 08:00")

        # Check if we're in the right minute
        if now.hour != hour or now.minute != minute:
            return  # Not the right time

        # Get interval
        interval_hours = config.get("interval", 24)
        
        # Check last sent time
        last_sent = self.last_sent.get(guild.id)
        
        if last_sent is None:
            # Never sent before, send now
            await self.send_quote(guild, channel_id)
            return

        # Convert last_sent to the server's timezone
        if last_sent.tzinfo is None:
            last_sent = pytz.utc.localize(last_sent)
        last_sent_local = last_sent.astimezone(tz)
        
        # Calculate time since last send
        time_since_last = now - last_sent_local
        required_interval = timedelta(hours=interval_hours)
        
        # Send if enough time has passed
        if time_since_last >= required_interval:
            await self.send_quote(guild, channel_id)

    async def send_quote(self, guild, channel_id):
        """Send a quote to the specified channel"""
        try:
            channel = self.bot.get_channel(channel_id)
            if not channel:
                await self.log_error(guild.id, f"Channel {channel_id} not found")
                return

            # Get config for role mention
            config = get_server_settings(guild.id)
            role_id = config.get("role_id")
            mention = f"<@&{role_id}> " if role_id else ""

            # Fetch and send quote
            quote = fetch_quote()
            await channel.send(f"{mention}{quote}")

            # Update last sent time (in UTC)
            self.last_sent[guild.id] = datetime.now(pytz.utc)
            self.save_last_sent()

            print(f"✅ Sent quote to {guild.name} ({guild.id})")

        except discord.Forbidden:
            error_msg = f"Missing permissions in channel {channel_id}"
            print(f"❌ {guild.name}: {error_msg}")
            await self.log_error(guild.id, error_msg)
        except Exception as e:
            error_msg = f"Error sending quote: {str(e)}"
            print(f"❌ {guild.name}: {error_msg}")
            await self.log_error(guild.id, error_msg)

async def setup(bot):
    await bot.add_cog(QuoteScheduler(bot))

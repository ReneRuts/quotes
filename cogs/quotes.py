import discord
from discord.ext import commands, tasks
from datetime import datetime, timedelta
import pytz
import json
import os
from utils.config import get_server_settings
from utils.quote_fetcher import fetch_quote
from utils.database import is_favorites_enabled

LAST_SENT_FILE = "last_sent.json"

class Quotes(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        self.last_sent = self.load_last_sent()
        self.quote_loop.start()

    def cog_unload(self):
        self.quote_loop.cancel()
        self.save_last_sent()

    def load_last_sent(self):
        if not os.path.exists(LAST_SENT_FILE):
            return {}
        
        try:
            with open(LAST_SENT_FILE, "r") as f:
                data = json.load(f)
                result = {}
                for guild_id, timestamp_str in data.items():
                    try:
                        dt = datetime.fromisoformat(timestamp_str.replace('+00:00', ''))
                        if dt.tzinfo is None:
                            dt = pytz.utc.localize(dt)
                        result[int(guild_id)] = dt
                    except:
                        continue
                print(f"📂 Loaded {len(result)} last_sent timestamps")
                return result
        except Exception as e:
            print(f"❌ Error loading last_sent.json: {e}")
            return {}

    def save_last_sent(self):
        try:
            data = {}
            for guild_id, dt in self.last_sent.items():
                if dt.tzinfo is None:
                    dt = pytz.utc.localize(dt)
                else:
                    dt = dt.astimezone(pytz.utc)
                data[str(guild_id)] = dt.isoformat()
            
            with open(LAST_SENT_FILE, "w") as f:
                json.dump(data, f, indent=4)
        except Exception as e:
            print(f"❌ Error saving last_sent.json: {e}")

    @tasks.loop(seconds=60)
    async def quote_loop(self):
        await self.bot.wait_until_ready()
        
        now = datetime.now()
        seconds_to_wait = 60 - now.second
        if second_to_wait < 60:
            await asyncio.sleep(seconds_to_wait)

        for guild in self.bot.guilds:
            try:
                await self.check_and_send_quote(guild)
            except Exception as e:
                print(f"❌ Error in {guild.name}: {e}")

    async def check_and_send_quote(self, guild):
        config = get_server_settings(guild.id)
        channel_id = config.get("channel_id")
        
        if not channel_id:
            return

        tz_name = config.get("timezone", "Europe/Brussels")
        try:
            tz = pytz.timezone(tz_name)
        except:
            tz = pytz.timezone("Europe/Brussels")

        local_now = datetime.now(tz)
        
        quote_time_str = config.get("quote_time", "08:00")
        try:
            hour, minute = map(int, quote_time_str.split(":"))
        except:
            hour, minute = 8, 0

        interval_hours = config.get("interval", 24)
        last_sent = self.last_sent.get(guild.id)
        
        scheduled_today = local_now.replace(hour=hour, minute=minute, second=0, microsecond=0)
        
        # If never sent before
        if last_sent is None:
            if local_now >= scheduled_today:
                await self.send_quote(guild, channel_id, local_now)
            return

        # Convert last_sent to server timezone
        if last_sent.tzinfo is None:
            last_sent = pytz.utc.localize(last_sent)
        last_sent_local = last_sent.astimezone(tz)
        
        next_scheduled = last_sent_local + timedelta(hours=interval_hours)
        
        # Check all conditions
        if local_now >= next_scheduled and local_now >= scheduled_today and last_sent_local < scheduled_today:
            await self.send_quote(guild, channel_id, local_now)

    async def send_quote(self, guild, channel_id, local_now):
        try:
            channel = self.bot.get_channel(channel_id)
            if not channel:
                return

            config = get_server_settings(guild.id)
            role_id = config.get("role_id")
            mention = f"<@&{role_id}> " if role_id else ""

            quote = fetch_quote()
            message = await channel.send(f"{mention}{quote}")
            
            # Add star reaction if favorites enabled
            if await is_favorites_enabled(guild.id):
                await message.add_reaction("❤️")
            
            self.last_sent[guild.id] = datetime.now(pytz.utc)
            self.save_last_sent()
            config = get_server_settings(guild.id)
            interval_hours = config.get("interval",24)
            next_send = local_now + timedelta(hours=interval_hours)
            
            print(f"✅ Sent quote to {guild.name} ({guild.id}) at {local_now.strftime('%Y-%m-%d %H:%M:%S')}. Expected: {next_send.strftime('%Y-%m-%d %H:%M:%S')}")

        except Exception as e:
            print(f"❌ Error sending quote to {guild.name}: {e}")

async def setup(bot):
    await bot.add_cog(Quotes(bot))

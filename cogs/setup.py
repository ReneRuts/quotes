import discord
from discord.ext import commands
from discord import app_commands
import pytz
import re
from utils.config import get_server_settings, update_server_settings
from utils.quote_fetcher import fetch_quote

class Setup(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    async def check_permissions(self, interaction: discord.Interaction) -> bool:
        """Check if user has manage server permission"""
        if not interaction.user.guild_permissions.manage_guild:
            await interaction.response.send_message(
                "❌ You need **Manage Server** permissions to use this command.",
                ephemeral=True
            )
            return False
        return True

    @app_commands.command(
        name="setup",
        description="Configure daily quote settings for this server"
    )
    @app_commands.describe(
        timezone="Timezone (e.g., Europe/Brussels, America/New_York)",
        quote_time="Time in 24h format (e.g., 08:00, 13:30)",
        interval="Hours between quotes (24-168)",
        channel="Channel where quotes will be sent",
        role="Role to mention when quotes are sent (optional)"
    )
    async def setup(
        self,
        interaction: discord.Interaction,
        timezone: str = None,
        quote_time: str = None,
        interval: int = None,
        channel: discord.TextChannel = None,
        role: discord.Role = None
    ):
        if not await self.check_permissions(interaction):
            return

        guild_id = interaction.guild.id
        config = get_server_settings(guild_id)

        # If no parameters, show current config
        if all(v is None for v in [timezone, quote_time, interval, channel, role]):
            return await self.show_config(interaction, config)

        # Validate and update settings
        updates = {}
        messages = []

        if timezone:
            if timezone not in pytz.all_timezones:
                return await interaction.response.send_message(
                    f"❌ Invalid timezone: `{timezone}`\n"
                    f"Use a timezone like `Europe/Brussels` or `America/New_York`.\n"
                    f"See: https://en.wikipedia.org/wiki/List_of_tz_database_time_zones",
                    ephemeral=True
                )
            updates["timezone"] = timezone
            messages.append(f"🌍 **Timezone:** `{timezone}`")

        if quote_time:
            if not re.match(r"^([01]\d|2[0-3]):[0-5]\d$", quote_time):
                return await interaction.response.send_message(
                    "❌ Invalid time format. Use **HH:MM** in 24-hour format (e.g., `08:00` or `13:30`)",
                    ephemeral=True
                )
            updates["quote_time"] = quote_time
            messages.append(f"🕐 **Quote Time:** `{quote_time}`")

        if interval:
            if interval < 24 or interval > 168:
                return await interaction.response.send_message(
                    "❌ Interval must be between **24** and **168** hours (1-7 days)",
                    ephemeral=True
                )
            updates["interval"] = interval
            messages.append(f"⏰ **Interval:** `{interval}` hours")

        if channel:
            # Check bot permissions
            perms = channel.permissions_for(interaction.guild.me)
            if not perms.send_messages or not perms.embed_links:
                return await interaction.response.send_message(
                    f"❌ I don't have permission to send messages in {channel.mention}.\n"
                    f"Please give me **Send Messages** and **Embed Links** permissions.",
                    ephemeral=True
                )
            updates["channel_id"] = channel.id
            messages.append(f"📢 **Channel:** {channel.mention}")

        if role:
            updates["role_id"] = role.id
            messages.append(f"🔔 **Role Mention:** {role.mention}")

        # Save updates
        update_server_settings(guild_id, **updates)

        embed = discord.Embed(
            title="✅ Settings Updated",
            description="\n".join(messages),
            color=discord.Color.green()
        )
        await interaction.response.send_message(embed=embed, ephemeral=True)

    async def show_config(self, interaction: discord.Interaction, config: dict):
        """Display current server configuration"""
        channel_obj = self.bot.get_channel(config["channel_id"]) if config["channel_id"] else None
        role_obj = interaction.guild.get_role(config["role_id"]) if config.get("role_id") else None

        embed = discord.Embed(
            title="⚙️ Current Server Configuration",
            color=discord.Color.blue()
        )
        
        embed.add_field(
            name="🌍 Timezone",
            value=f"`{config['timezone']}`",
            inline=True
        )
        embed.add_field(
            name="🕐 Quote Time",
            value=f"`{config['quote_time']}`",
            inline=True
        )
        embed.add_field(
            name="⏰ Interval",
            value=f"`{config['interval']}` hours",
            inline=True
        )
        embed.add_field(
            name="📢 Channel",
            value=channel_obj.mention if channel_obj else "❌ *Not set*",
            inline=True
        )
        embed.add_field(
            name="🔔 Role Mention",
            value=role_obj.mention if role_obj else "*None*",
            inline=True
        )

        if not channel_obj:
            embed.set_footer(text="⚠️ Please set a channel to start receiving quotes!")

        await interaction.response.send_message(embed=embed, ephemeral=True)

    @app_commands.command(
        name="testquote",
        description="Send a test quote immediately to verify setup"
    )
    async def testquote(self, interaction: discord.Interaction):
        if not await self.check_permissions(interaction):
            return

        config = get_server_settings(interaction.guild.id)
        channel_id = config.get("channel_id")

        if not channel_id:
            return await interaction.response.send_message(
                "❌ No channel configured. Use `/setup channel:#your-channel` first.",
                ephemeral=True
            )

        channel = self.bot.get_channel(channel_id)
        if not channel:
            return await interaction.response.send_message(
                "❌ Configured channel not found. Please run `/setup` again.",
                ephemeral=True
            )

        await interaction.response.defer(ephemeral=True)

        try:
            role_id = config.get("role_id")
            mention = f"<@&{role_id}> " if role_id else ""
            quote = fetch_quote()
            
            await channel.send(f"{mention}{quote}")
            await interaction.followup.send(
                f"✅ Test quote sent to {channel.mention}!",
                ephemeral=True
            )
        except Exception as e:
            await interaction.followup.send(
                f"❌ Error sending quote: {str(e)}",
                ephemeral=True
            )

async def setup(bot):
    await bot.add_cog(Setup(bot))

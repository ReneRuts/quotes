import discord
from discord.ext import commands
from discord import app_commands
import pytz
import re

# Import config functions
from config import (
    get_server_settings,
    set_timezone,
    set_quote_time,
    set_interval,
    set_channel,
    set_role
)

class Setup(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    async def has_manage_server_permission(self, interaction: discord.Interaction) -> bool:
        return interaction.user.guild_permissions.manage_guild

    async def ensure_permissions(self, channel: discord.TextChannel, bot: discord.Client):
        """Ensure the bot has required permissions in the assigned channel."""
        try:
            overwrites = channel.overwrites_for(channel.guild.me)
            overwrites.send_messages = True
            overwrites.embed_links = True
            overwrites.attach_files = True
            overwrites.use_external_emojis = True

            await channel.set_permissions(channel.guild.me, overwrite=overwrites)
        except Exception as e:
            print(f"❌ Error setting permissions: {e}")

    @app_commands.command(
        name="setup",
        description="View current server setup and configure daily quote settings."
    )
    @app_commands.describe(
        timezone="Timezone (e.g. Europe/Brussels)",
        quote_time="Time (HH:MM, 24h format, 1AM = 13:00)",
        interval="Interval in hours (e.g. 24)",
        channel="Channel to send the daily quote to",
        role="Role to mention with the daily quote (optional)"
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
        if not await self.has_manage_server_permission(interaction):
            return await interaction.response.send_message("❌ You need **Manage Server** permissions.", ephemeral=True)
        if not interaction.guild:
            return await interaction.response.send_message("❌ This command must be used in a server.", ephemeral=True)

        guild_id = interaction.guild.id
        config = get_server_settings(guild_id)
        updates = []

        # If no options provided, show current config
        if timezone is None and quote_time is None and interval is None and channel is None:
            channel_obj = self.bot.get_channel(config["channel_id"]) if config["channel_id"] else None
            role_obj = interaction.guild.get_role(config.get("role_id")) if config.get("role_id") else None
            embed = discord.Embed(
                title="📋 Current Server Configuration",
                color=discord.Color.green()
            )
            embed.add_field(name="Timezone", value=f"`{config['timezone']}`", inline=False)
            embed.add_field(name="Quote Time", value=f"`{config['quote_time']}`", inline=False)
            embed.add_field(name="Interval", value=f"`{config['interval']}` hours", inline=False)
            embed.add_field(
                name="Channel",
                value=channel_obj.mention if channel_obj else "*Not set*",
                inline=False
            )
            embed.add_field(
                name="Role to Ping",
                value=role_obj.mention if role_obj else "*Not set*",
                inline=False
            )

            return await interaction.response.send_message(embed=embed, ephemeral=True)

        # Otherwise, update provided settings
        if timezone:
            if timezone not in pytz.all_timezones:
                return await interaction.response.send_message("❌ Invalid timezone.", ephemeral=True)
            set_timezone(guild_id, timezone)
            updates.append(f"**Timezone:** `{timezone}`")
        if quote_time:
            if not re.match(r"^(?:[01]\d|2[0-3]):[0-5]\d$", quote_time):
                return await interaction.response.send_message("❌ Invalid time format. Use HH:MM (24h).", ephemeral=True)
            set_quote_time(guild_id, quote_time)
            updates.append(f"**Time:** `{quote_time}`")
        if interval:
            if interval < 24 or interval > 168:
                return await interaction.response.send_message("❌ Interval must be between 24 and 168 (7 days) hours.", ephemeral=True)
            set_interval(guild_id, interval)
            updates.append(f"**Interval:** `{interval}` hours")
        if channel:
            set_channel(guild_id, channel.id)
            updates.append(f"**Channel:** {channel.mention}")

            # Auto-assign required bot permissions
            await self.ensure_permissions(channel, self.bot)

        if role:
            set_role(guild_id, role.id)
            updates.append(f"**Role:** {role.mention}")

        await interaction.response.send_message(
            "✅ Updated settings:\n" + "\n".join(updates),
            ephemeral=True
        )

async def setup(bot):
    await bot.add_cog(Setup(bot))

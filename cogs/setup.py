import discord
from discord.ext import commands
from discord import app_commands
import pytz
import re
from utils.config import get_server_settings, update_server_settings
from utils.database import is_favorites_enabled, set_favorites_enabled

class SetupView(discord.ui.View):
    def __init__(self, bot, guild_id):
        super().__init__(timeout=180)
        self.bot = bot
        self.guild_id = guild_id

    @discord.ui.button(label="⚙️ Quote Settings", style=discord.ButtonStyle.primary)
    async def quote_settings(self, interaction: discord.Interaction, button: discord.ui.Button):
        await interaction.response.send_modal(QuoteSettingsModal(self.guild_id))

    @discord.ui.button(label="✨ Feature Settings", style=discord.ButtonStyle.secondary)
    async def feature_settings(self, interaction: discord.Interaction, button: discord.ui.Button):
        favorites_enabled = await is_favorites_enabled(self.guild_id)
        
        embed = discord.Embed(
            title="✨ Feature Settings",
            description="Enable or disable bot features",
            color=discord.Color.blue()
        )
        
        embed.add_field(
            name="Favorites System",
            value=f"Status: {'✅ Enabled' if favorites_enabled else '❌ Disabled'}\n"
                  f"When enabled, the bot will react wit ❤️ to quotes.\n"
                  f"Users can click the ❤️ to save quotes to their favorites.",
            inline=False
        )
        
        view = FeatureToggleView(self.guild_id, favorites_enabled)
        await interaction.response.send_message(embed=embed, view=view, ephemeral=True)

class QuoteSettingsModal(discord.ui.Modal, title="Quote Settings"):
    def __init__(self, guild_id):
        super().__init__()
        self.guild_id = guild_id
        
        config = get_server_settings(guild_id)
        
        self.timezone = discord.ui.TextInput(
            label="Timezone",
            placeholder="e.g., Europe/Brussels, America/New_York",
            default=config.get("timezone", "Europe/Brussels"),
            required=True
        )
        self.add_item(self.timezone)
        
        self.quote_time = discord.ui.TextInput(
            label="Quote Time (24h format)",
            placeholder="e.g., 08:00, 13:30",
            default=config.get("quote_time", "08:00"),
            required=True,
            max_length=5
        )
        self.add_item(self.quote_time)
        
        self.interval = discord.ui.TextInput(
            label="Interval (hours)",
            placeholder="24 = daily, 168 = weekly",
            default=str(config.get("interval", 24)),
            required=True,
            max_length=3
        )
        self.add_item(self.interval)

    async def on_submit(self, interaction: discord.Interaction):
        timezone = self.timezone.value
        quote_time = self.quote_time.value
        interval = int(self.interval.value)
        
        # Validate timezone
        if timezone not in pytz.all_timezones:
            return await interaction.response.send_message(
                "❌ Invalid timezone. See: https://en.wikipedia.org/wiki/List_of_tz_database_time_zones",
                ephemeral=True
            )
        
        # Validate time format
        if not re.match(r"^([01]\d|2[0-3]):[0-5]\d$", quote_time):
            return await interaction.response.send_message(
                "❌ Invalid time format. Use HH:MM (24-hour format)",
                ephemeral=True
            )
        
        # Validate interval
        if interval < 24 or interval > 168:
            return await interaction.response.send_message(
                "❌ Interval must be between 24 and 168 hours",
                ephemeral=True
            )
        
        # Save settings
        update_server_settings(
            self.guild_id,
            timezone=timezone,
            quote_time=quote_time,
            interval=interval
        )
        
        embed = discord.Embed(
            title="✅ Settings Updated",
            color=discord.Color.green()
        )
        embed.add_field(name="Timezone", value=f"`{timezone}`", inline=False)
        embed.add_field(name="Quote Time", value=f"`{quote_time}`", inline=True)
        embed.add_field(name="Interval", value=f"`{interval}` hours", inline=True)
        
        await interaction.response.send_message(embed=embed, ephemeral=True)

class FeatureToggleView(discord.ui.View):
    def __init__(self, guild_id, favorites_enabled):
        super().__init__(timeout=180)
        self.guild_id = guild_id
        
        # Update button style based on current state
        self.favorites_button.style = discord.ButtonStyle.success if favorites_enabled else discord.ButtonStyle.danger
        self.favorites_button.label = "✅ Favorites Enabled" if favorites_enabled else "❌ Favorites Disabled"

    @discord.ui.button(label="Toggle", style=discord.ButtonStyle.primary)
    async def favorites_button(self, interaction: discord.Interaction, button: discord.ui.Button):
        current_state = await is_favorites_enabled(self.guild_id)
        new_state = not current_state
        
        await set_favorites_enabled(self.guild_id, new_state)
        
        # Update button
        button.style = discord.ButtonStyle.success if new_state else discord.ButtonStyle.danger
        button.label = "✅ Favorites Enabled" if new_state else "❌ Favorites Disabled"
        
        embed = discord.Embed(
            title="✨ Feature Settings",
            description="Enable or disable bot features",
            color=discord.Color.green() if new_state else discord.Color.red()
        )
        
        embed.add_field(
            name="Favorites System",
            value=f"Status: {'✅ Enabled' if new_state else '❌ Disabled'}\n"
                  f"When enabled, the bot will react with ❤️ to quotes.\n"
                  f"Users can clickee❤️e ❤️ to save quotes to their favorites.",
            inline=False
        )
        
        await interaction.response.edit_message(embed=embed, view=self)

class Setup(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @app_commands.command(name="setup", description="Configure bot settings")
    @app_commands.describe(
        channel="Channel to send quotes to",
        role="Role to mention (optional)"
    )
    async def setup(
        self,
        interaction: discord.Interaction,
        channel: discord.TextChannel = None,
        role: discord.Role = None
    ):
        if not interaction.user.guild_permissions.manage_guild:
            return await interaction.response.send_message(
                "❌ You need **Manage Server** permissions.",
                ephemeral=True
            )
        
        config = get_server_settings(interaction.guild.id)
        
        # If channel or role provided, update them
        if channel or role:
            updates = {}
            if channel:
                # Check permissions
                perms = channel.permissions_for(interaction.guild.me)
                if not perms.send_messages:
                    return await interaction.response.send_message(
                        f"❌ I don't have permission to send messages in {channel.mention}",
                        ephemeral=True
                    )
                updates["channel_id"] = channel.id
            
            if role:
                updates["role_id"] = role.id
            
            if updates:
                update_server_settings(interaction.guild.id, **updates)
                config = get_server_settings(interaction.guild.id)
        
        # Show current settings with buttons
        channel_obj = self.bot.get_channel(config["channel_id"]) if config["channel_id"] else None
        role_obj = interaction.guild.get_role(config["role_id"]) if config.get("role_id") else None
        
        embed = discord.Embed(
            title="⚙️ Server Configuration",
            description="Click the buttons below to configure settings",
            color=discord.Color.blue()
        )
        
        embed.add_field(
            name="📢 Channel",
            value=channel_obj.mention if channel_obj else "❌ Not set\nUse `/setup channel:#your-channel`",
            inline=False
        )
        
        embed.add_field(
            name="🔔 Role Mention",
            value=role_obj.mention if role_obj else "Not set",
            inline=True
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
        
        view = SetupView(self.bot, interaction.guild.id)
        await interaction.response.send_message(embed=embed, view=view, ephemeral=True)

    @app_commands.command(name="help", description="Show help and commands")
    async def help_cmd(self, interaction: discord.Interaction):
        embed = discord.Embed(
            title="📖 Quote Bot - Help",
            description="Daily quotes for your server!",
            color=discord.Color.blue()
        )
        
        embed.add_field(
            name="⚙️ Setup Commands",
            value=(
                "`/setup` - View and configure bot settings\n"
                "`/setup channel:#channel` - Set quote channel\n"
                "`/setup role:@role` - Set role to mention\n"
            ),
            inline=False
        )
        
        embed.add_field(
            name="✨ User Commands",
            value="`/favorites` - View your favorite quotes",
            inline=False
        )
        
        embed.add_field(
            name="💬 Support",
            value="Need help? Join our [Support Server](https://discord.gg/5jkADM2Wt5)",
            inline=False
        )
        
        embed.set_footer(text="Made with ❤️ by René Ruts")
        
        await interaction.response.send_message(embed=embed, ephemeral=True)

async def setup(bot):
    await bot.add_cog(Setup(bot))

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

    @app_commands.command(
        name="admin",
        description="Manage advanced server settings (Admin only)"
    )
    @app_commands.describe(
        feature="Feature to toggle",
        enabled="Enable or disable the feature"
    )
    @app_commands.choices(feature=[
        app_commands.Choice(name="Games & Stats System", value="games"),
        app_commands.Choice(name="Custom Quotes", value="custom_quotes"),
        app_commands.Choice(name="Quote Approval Required", value="approval")
    ])
    async def admin(
        self,
        interaction: discord.Interaction,
        feature: str,
        enabled: bool
    ):
        if not await self.check_permissions(interaction):
            return

        from utils.database import update_server_customization
        
        setting_map = {
            "games": "games_enabled",
            "custom_quotes": "custom_quotes_enabled",
            "approval": "require_approval"
        }
        
        setting_name = setting_map.get(feature)
        if not setting_name:
            return await interaction.response.send_message(
                "❌ Invalid feature selected.",
                ephemeral=True
            )
        
        await update_server_customization(interaction.guild.id, **{setting_name: enabled})
        
        feature_names = {
            "games": "Games & Stats System",
            "custom_quotes": "Custom Quotes",
            "approval": "Quote Approval Required"
        }
        
        status = "✅ Enabled" if enabled else "❌ Disabled"
        
        embed = discord.Embed(
            title="⚙️ Settings Updated",
            description=f"{feature_names[feature]}: {status}",
            color=discord.Color.green() if enabled else discord.Color.red()
        )
        
        await interaction.response.send_message(embed=embed, ephemeral=True)

    @app_commands.command(
        name="categories",
        description="Manage quote categories (Admin only)"
    )
    @app_commands.describe(
        action="Enable or disable a category",
        category="The category to manage"
    )
    @app_commands.choices(
        action=[
            app_commands.Choice(name="Enable", value="enable"),
            app_commands.Choice(name="Disable", value="disable"),
            app_commands.Choice(name="View Disabled", value="view")
        ],
        category=[
            app_commands.Choice(name="Motivational", value="motivational"),
            app_commands.Choice(name="Funny", value="funny"),
            app_commands.Choice(name="Inspirational", value="inspirational"),
            app_commands.Choice(name="Love", value="love"),
            app_commands.Choice(name="Life", value="life"),
            app_commands.Choice(name="Success", value="success"),
            app_commands.Choice(name="Wisdom", value="wisdom"),
            app_commands.Choice(name="Friendship", value="friendship"),
            app_commands.Choice(name="Happiness", value="happiness"),
            app_commands.Choice(name="Programming", value="programming"),
            app_commands.Choice(name="Gaming", value="gaming"),
            app_commands.Choice(name="Anime", value="anime"),
            app_commands.Choice(name="Movies", value="movies"),
            app_commands.Choice(name="Books", value="books"),
            app_commands.Choice(name="General", value="general")
        ]
    )
    async def categories_cmd(
        self,
        interaction: discord.Interaction,
        action: str,
        category: str = None
    ):
        if not await self.check_permissions(interaction):
            return

        from utils.database import get_disabled_categories, update_server_customization
        import json
        
        disabled = await get_disabled_categories(interaction.guild.id)
        
        if action == "view":
            if not disabled:
                embed = discord.Embed(
                    title="📂 Disabled Categories",
                    description="All categories are currently enabled!",
                    color=discord.Color.green()
                )
            else:
                embed = discord.Embed(
                    title="📂 Disabled Categories",
                    description="\n".join([f"• `{cat}`" for cat in disabled]),
                    color=discord.Color.orange()
                )
            return await interaction.response.send_message(embed=embed, ephemeral=True)
        
        if not category:
            return await interaction.response.send_message(
                "❌ Please specify a category.",
                ephemeral=True
            )
        
        if action == "disable":
            if category not in disabled:
                disabled.append(category)
                await update_server_customization(
                    interaction.guild.id,
                    disabled_categories=json.dumps(disabled)
                )
                await interaction.response.send_message(
                    f"✅ Category `{category}` has been disabled.",
                    ephemeral=True
                )
            else:
                await interaction.response.send_message(
                    f"❌ Category `{category}` is already disabled.",
                    ephemeral=True
                )
        
        elif action == "enable":
            if category in disabled:
                disabled.remove(category)
                await update_server_customization(
                    interaction.guild.id,
                    disabled_categories=json.dumps(disabled)
                )
                await interaction.response.send_message(
                    f"✅ Category `{category}` has been enabled.",
                    ephemeral=True
                )
            else:
                await interaction.response.send_message(
                    f"❌ Category `{category}` is already enabled.",
                    ephemeral=True
                )

async def setup(bot):
    await bot.add_cog(Setup(bot))

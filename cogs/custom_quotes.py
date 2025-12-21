import discord
from discord.ext import commands
from discord import app_commands
from utils.database import (
    add_custom_quote, delete_quote, get_pending_quotes,
    approve_quote, update_user_stats, get_server_customization
)
from utils.embed_builder import create_quote_list_embed
import aiosqlite

CATEGORIES = [
    "motivational", "funny", "inspirational", "love", "life",
    "success", "wisdom", "friendship", "happiness", "programming",
    "gaming", "anime", "movies", "books", "general"
]

class CustomQuotes(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @app_commands.command(name="addquote", description="Submit a custom quote")
    @app_commands.describe(
        quote="The quote text",
        author="Who said it",
        category="Quote category"
    )
    @app_commands.choices(category=[
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
    ])
    async def addquote(
        self,
        interaction: discord.Interaction,
        quote: str,
        author: str,
        category: str
    ):
        from utils.database import is_custom_quotes_enabled, get_disabled_categories
        
        if not await is_custom_quotes_enabled(interaction.guild.id):
            return await interaction.response.send_message(
                "❌ Custom quotes are disabled on this server.",
                ephemeral=True
            )
        
        disabled_categories = await get_disabled_categories(interaction.guild.id)
        if category in disabled_categories:
            return await interaction.response.send_message(
                f"❌ The category `{category}` is currently disabled on this server.",
                ephemeral=True
            )
        
        if len(quote) < 10:
            return await interaction.response.send_message(
                "❌ Quote must be at least 10 characters long.",
                ephemeral=True
            )
        
        if len(quote) > 500:
            return await interaction.response.send_message(
                "❌ Quote must be less than 500 characters.",
                ephemeral=True
            )
        
        # Check if approval is required
        customization = await get_server_customization(interaction.guild.id)
        require_approval = customization[4]
        
        quote_id = await add_custom_quote(
            interaction.guild.id,
            quote,
            author,
            category,
            interaction.user.id,
            approved=not require_approval
        )
        
        await update_user_stats(interaction.guild.id, interaction.user.id, "submit")
        
        if require_approval:
            embed = discord.Embed(
                title="✅ Quote Submitted!",
                description=(
                    f"Your quote has been submitted for review.\n\n"
                    f"**Quote:** {quote}\n"
                    f"**Author:** {author}\n"
                    f"**Category:** {category}\n"
                    f"**ID:** #{quote_id}\n\n"
                    f"A moderator will review it soon!"
                ),
                color=discord.Color.green()
            )
            await interaction.response.send_message(embed=embed, ephemeral=True)
        else:
            embed = discord.Embed(
                title="✅ Quote Added!",
                description=(
                    f"Your quote has been added to the server!\n\n"
                    f"**Quote:** {quote}\n"
                    f"**Author:** {author}\n"
                    f"**Category:** {category}\n"
                    f"**ID:** #{quote_id}"
                ),
                color=discord.Color.green()
            )
            await interaction.response.send_message(embed=embed, ephemeral=True)

    @app_commands.command(name="myquotes", description="View your submitted quotes")
    async def myquotes(self, interaction: discord.Interaction):
        await interaction.response.defer(ephemeral=True)
        
        async with aiosqlite.connect("data/quotes.db") as db:
            cursor = await db.execute(
                "SELECT * FROM custom_quotes WHERE guild_id = ? AND submitter_id = ? ORDER BY submitted_at DESC",
                (interaction.guild.id, interaction.user.id)
            )
            quotes = await cursor.fetchall()
        
        if not quotes:
            return await interaction.followup.send(
                "❌ You haven't submitted any quotes yet!\nUse `/addquote` to submit one.",
                ephemeral=True
            )
        
        embed = await create_quote_list_embed(
            quotes,
            f"📝 {interaction.user.display_name}'s Submitted Quotes",
            page=1,
            per_page=5
        )
        
        await interaction.followup.send(embed=embed, ephemeral=True)

    @app_commands.command(name="deletequote", description="Delete one of your quotes")
    @app_commands.describe(quote_id="The ID of the quote to delete")
    async def deletequote(self, interaction: discord.Interaction, quote_id: int):
        # Check if user owns this quote or is admin
        async with aiosqlite.connect("data/quotes.db") as db:
            cursor = await db.execute(
                "SELECT submitter_id FROM custom_quotes WHERE id = ? AND guild_id = ?",
                (quote_id, interaction.guild.id)
            )
            result = await cursor.fetchone()
        
        if not result:
            return await interaction.response.send_message(
                f"❌ Quote #{quote_id} not found.",
                ephemeral=True
            )
        
        submitter_id = result[0]
        
        if submitter_id != interaction.user.id and not interaction.user.guild_permissions.manage_guild:
            return await interaction.response.send_message(
                "❌ You can only delete your own quotes!",
                ephemeral=True
            )
        
        await delete_quote(quote_id)
        
        await interaction.response.send_message(
            f"✅ Quote #{quote_id} has been deleted.",
            ephemeral=True
        )

    @app_commands.command(name="pending", description="View pending quotes (Admin only)")
    async def pending(self, interaction: discord.Interaction):
        if not interaction.user.guild_permissions.manage_guild:
            return await interaction.response.send_message(
                "❌ You need **Manage Server** permissions to use this command.",
                ephemeral=True
            )
        
        await interaction.response.defer(ephemeral=True)
        
        quotes = await get_pending_quotes(interaction.guild.id)
        
        if not quotes:
            return await interaction.followup.send(
                "✅ No pending quotes to review!",
                ephemeral=True
            )
        
        embed = await create_quote_list_embed(
            quotes,
            "⏳ Pending Quotes for Approval",
            page=1,
            per_page=5
        )
        
        embed.set_footer(text="Use /approve <quote_id> to approve or /deletequote <quote_id> to reject")
        
        await interaction.followup.send(embed=embed, ephemeral=True)

    @app_commands.command(name="approve", description="Approve a pending quote (Admin only)")
    @app_commands.describe(quote_id="The ID of the quote to approve")
    async def approve_cmd(self, interaction: discord.Interaction, quote_id: int):
        if not interaction.user.guild_permissions.manage_guild:
            return await interaction.response.send_message(
                "❌ You need **Manage Server** permissions to use this command.",
                ephemeral=True
            )
        
        # Check if quote exists and is pending
        async with aiosqlite.connect("data/quotes.db") as db:
            cursor = await db.execute(
                "SELECT approved, submitter_id FROM custom_quotes WHERE id = ? AND guild_id = ?",
                (quote_id, interaction.guild.id)
            )
            result = await cursor.fetchone()
        
        if not result:
            return await interaction.response.send_message(
                f"❌ Quote #{quote_id} not found.",
                ephemeral=True
            )
        
        if result[0]:  # Already approved
            return await interaction.response.send_message(
                f"❌ Quote #{quote_id} is already approved.",
                ephemeral=True
            )
        
        await approve_quote(quote_id)
        
        # Notify submitter
        submitter_id = result[1]
        try:
            submitter = await self.bot.fetch_user(submitter_id)
            await submitter.send(
                f"✅ Your quote #{quote_id} has been approved in **{interaction.guild.name}**!"
            )
        except:
            pass
        
        await interaction.response.send_message(
            f"✅ Quote #{quote_id} has been approved!",
            ephemeral=True
        )

async def setup(bot):
    await bot.add_cog(CustomQuotes(bot))

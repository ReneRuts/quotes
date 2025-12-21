import discord
from discord.ext import commands
from discord import app_commands
from utils.database import get_user_stats, get_leaderboard
from utils.embed_builder import create_stats_embed, create_leaderboard_embed

class Games(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @app_commands.command(name="stats", description="View your statistics")
    @app_commands.describe(user="User to view stats for (optional)")
    async def stats(self, interaction: discord.Interaction, user: discord.Member = None):
        from utils.database import is_games_enabled
        
        if not await is_games_enabled(interaction.guild.id):
            return await interaction.response.send_message(
                "❌ Games & Stats features are disabled on this server.",
                ephemeral=True
            )
        
        target_user = user or interaction.user
        
        await interaction.response.defer(ephemeral=(user is None))
        
        user_data = await get_user_stats(interaction.guild.id, target_user.id)
        
        if not user_data:
            return await interaction.followup.send(
                f"❌ {target_user.mention} hasn't interacted with quotes yet!",
                ephemeral=True
            )
        
        # Get rank
        leaderboard = await get_leaderboard(interaction.guild.id, "xp", limit=999)
        rank = next((i + 1 for i, u in enumerate(leaderboard) if u[2] == target_user.id), None)
        
        embed = await create_stats_embed(user_data, interaction.guild, rank)
        
        await interaction.followup.send(embed=embed, ephemeral=(user is None))

    @app_commands.command(name="leaderboard", description="View server leaderboard")
    @app_commands.describe(
        type="Leaderboard type"
    )
    @app_commands.choices(type=[
        app_commands.Choice(name="XP", value="xp"),
        app_commands.Choice(name="Streak", value="current_streak"),
        app_commands.Choice(name="Quotes Viewed", value="quotes_viewed"),
        app_commands.Choice(name="Quotes Submitted", value="quotes_submitted")
    ])
    async def leaderboard(self, interaction: discord.Interaction, type: str = "xp"):
        from utils.database import is_games_enabled
        
        if not await is_games_enabled(interaction.guild.id):
            return await interaction.response.send_message(
                "❌ Games & Stats features are disabled on this server.",
                ephemeral=True
            )
        
        await interaction.response.defer()
        
        leaderboard = await get_leaderboard(interaction.guild.id, type, limit=10)
        
        if not leaderboard:
            return await interaction.followup.send(
                "❌ No leaderboard data available yet!",
                ephemeral=True
            )
        
        type_names = {
            "xp": "XP",
            "current_streak": "Current Streak",
            "quotes_viewed": "Quotes Viewed",
            "quotes_submitted": "Quotes Submitted"
        }
        
        embed = await create_leaderboard_embed(
            interaction.guild,
            leaderboard,
            type_names.get(type, "XP")
        )
        
        await interaction.followup.send(embed=embed)

    @app_commands.command(name="streak", description="View your current streak")
    async def streak(self, interaction: discord.Interaction):
        from utils.database import is_games_enabled
        
        if not await is_games_enabled(interaction.guild.id):
            return await interaction.response.send_message(
                "❌ Games & Stats features are disabled on this server.",
                ephemeral=True
            )
        
        await interaction.response.defer(ephemeral=True)
        
        user_data = await get_user_stats(interaction.guild.id, interaction.user.id)
        
        if not user_data:
            return await interaction.followup.send(
                "❌ You haven't started a streak yet! View a quote with `/quote` to begin.",
                ephemeral=True
            )
        
        current_streak = user_data[7]
        longest_streak = user_data[8]
        
        embed = discord.Embed(
            title=f"🔥 {interaction.user.display_name}'s Streak",
            color=discord.Color.orange()
        )
        
        embed.add_field(name="Current Streak", value=f"**{current_streak}** days 🔥", inline=True)
        embed.add_field(name="Longest Streak", value=f"**{longest_streak}** days 🏅", inline=True)
        
        if current_streak == 0:
            embed.add_field(
                name="💡 Tip",
                value="View a quote daily to build your streak!",
                inline=False
            )
        elif current_streak >= 7:
            embed.add_field(
                name="🎉 Amazing!",
                value="You're on fire! Keep it up!",
                inline=False
            )
        
        await interaction.followup.send(embed=embed, ephemeral=True)

    @app_commands.command(name="level", description="View your level and XP progress")
    async def level(self, interaction: discord.Interaction):
        from utils.database import is_games_enabled
        
        if not await is_games_enabled(interaction.guild.id):
            return await interaction.response.send_message(
                "❌ Games & Stats features are disabled on this server.",
                ephemeral=True
            )
        
        await interaction.response.defer(ephemeral=True)
        
        user_data = await get_user_stats(interaction.guild.id, interaction.user.id)
        
        if not user_data:
            return await interaction.followup.send(
                "❌ You haven't earned any XP yet! Interact with quotes to start leveling up.",
                ephemeral=True
            )
        
        xp = user_data[3]
        level = user_data[4]
        
        # Calculate XP needed for next level
        xp_for_next = level * 100
        xp_progress = xp % 100
        
        embed = discord.Embed(
            title=f"⭐ {interaction.user.display_name}'s Level",
            color=discord.Color.gold()
        )
        
        embed.add_field(name="Level", value=f"**{level}**", inline=True)
        embed.add_field(name="Total XP", value=f"**{xp:,}**", inline=True)
        embed.add_field(
            name="Progress to Next Level",
            value=f"**{xp_progress}/{xp_for_next}** XP\n{'█' * (xp_progress // 10)}{'░' * (10 - xp_progress // 10)}",
            inline=False
        )
        
        embed.set_footer(text="Earn XP by viewing quotes (+5), submitting quotes (+10), and more!")
        
        await interaction.followup.send(embed=embed, ephemeral=True)

async def setup(bot):
    await bot.add_cog(Games(bot))

import discord
from discord.ext import commands
from discord import app_commands
from utils.database import (
    get_random_custom_quote, get_quotes_by_author, search_quotes,
    add_reaction, remove_reaction, add_favorite, remove_favorite,
    get_user_favorites, update_user_stats, log_quote_sent
)
from utils.embed_builder import create_quote_embed, create_quote_list_embed, create_help_embed
from utils.quote_fetcher import fetch_quote
import random

class QuoteCommands(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @app_commands.command(name="quote", description="Get a quote instantly")
    @app_commands.describe(
        type="Type of quote to get",
        author="Get quotes by specific author",
        category="Get quotes from a category",
        keyword="Search for quotes containing a keyword"
    )
    async def quote(
        self,
        interaction: discord.Interaction,
        type: str = "random",
        author: str = None,
        category: str = None,
        keyword: str = None
    ):
        await interaction.response.defer()
        
        guild_id = interaction.guild.id
        quote_data = None
        
        try:
            if author:
                quotes = await get_quotes_by_author(guild_id, author)
                if quotes:
                    quote_data = random.choice(quotes)
                else:
                    return await interaction.followup.send(
                        f"❌ No quotes found by **{author}**",
                        ephemeral=True
                    )
            
            elif keyword:
                quotes = await search_quotes(guild_id, keyword)
                if quotes:
                    quote_data = random.choice(quotes)
                else:
                    return await interaction.followup.send(
                        f"❌ No quotes found matching **{keyword}**",
                        ephemeral=True
                    )
            
            elif category:
                quote_data = await get_random_custom_quote(guild_id, category)
                if not quote_data:
                    return await interaction.followup.send(
                        f"❌ No quotes found in category **{category}**",
                        ephemeral=True
                    )
            
            else:
                # Try custom quotes first
                quote_data = await get_random_custom_quote(guild_id)
                
                # If no custom quotes, use API
                if not quote_data:
                    api_quote = fetch_quote()
                    await interaction.followup.send(api_quote)
                    await update_user_stats(guild_id, interaction.user.id, "view")
                    return
            
            if quote_data:
                quote_id, _, text, author, category, _, _, _, likes, dislikes = quote_data
                
                embed = await create_quote_embed(
                    text, author,
                    quote_id=quote_id,
                    likes=likes,
                    dislikes=dislikes
                )
                
                message = await interaction.followup.send(embed=embed)
                
                # Add reactions
                await message.add_reaction("👍")
                await message.add_reaction("👎")
                await message.add_reaction("⭐")
                
                # Update stats
                await update_user_stats(guild_id, interaction.user.id, "view")
                await log_quote_sent(guild_id, text, author, quote_id)
        
        except Exception as e:
            print(f"Error in quote command: {e}")
            await interaction.followup.send(
                "❌ An error occurred while fetching the quote.",
                ephemeral=True
            )

    @app_commands.command(name="favorites", description="View your favorite quotes")
    async def favorites(self, interaction: discord.Interaction):
        await interaction.response.defer(ephemeral=True)
        
        favorites = await get_user_favorites(interaction.user.id)
        
        if not favorites:
            return await interaction.followup.send(
                "❌ You don't have any favorite quotes yet!\nReact with ⭐ to add quotes to your favorites.",
                ephemeral=True
            )
        
        embed = await create_quote_list_embed(
            favorites,
            f"⭐ {interaction.user.display_name}'s Favorite Quotes",
            page=1,
            per_page=5
        )
        
        await interaction.followup.send(embed=embed, ephemeral=True)

    @app_commands.command(name="search", description="Search for quotes")
    @app_commands.describe(keyword="Keyword to search for")
    async def search_cmd(self, interaction: discord.Interaction, keyword: str):
        await interaction.response.defer()
        
        quotes = await search_quotes(interaction.guild.id, keyword)
        
        if not quotes:
            return await interaction.followup.send(
                f"❌ No quotes found matching **{keyword}**",
                ephemeral=True
            )
        
        embed = await create_quote_list_embed(
            quotes,
            f"🔍 Search Results for '{keyword}'",
            page=1,
            per_page=5
        )
        
        await interaction.followup.send(embed=embed)

    @app_commands.command(name="help", description="Show all available commands")
    async def help_cmd(self, interaction: discord.Interaction):
        embed = await create_help_embed()
        await interaction.response.send_message(embed=embed, ephemeral=True)

    @commands.Cog.listener()
    async def on_raw_reaction_add(self, payload):
        """Handle reactions on quotes"""
        if payload.user_id == self.bot.user.id:
            return
        
        channel = self.bot.get_channel(payload.channel_id)
        if not channel:
            return
        
        try:
            message = await channel.fetch_message(payload.message_id)
        except:
            return
        
        # Check if it's a quote message with embeds
        if not message.embeds or not message.author.id == self.bot.user.id:
            return
        
        embed = message.embeds[0]
        
        # Extract quote ID from embed
        quote_id = None
        for field in embed.fields:
            if field.name == "Quote ID":
                quote_id = int(field.value.strip("`#"))
                break
        
        if not quote_id:
            return
        
        user_id = payload.user_id
        emoji = str(payload.emoji)
        
        if emoji == "👍":
            await add_reaction(quote_id, user_id, "like")
        elif emoji == "👎":
            await add_reaction(quote_id, user_id, "dislike")
        elif emoji == "⭐":
            success = await add_favorite(user_id, quote_id)
            if success:
                try:
                    user = await self.bot.fetch_user(user_id)
                    await user.send(f"⭐ Quote #{quote_id} added to your favorites!")
                except:
                    pass

    @commands.Cog.listener()
    async def on_raw_reaction_remove(self, payload):
        """Handle reaction removal"""
        if payload.user_id == self.bot.user.id:
            return
        
        channel = self.bot.get_channel(payload.channel_id)
        if not channel:
            return
        
        try:
            message = await channel.fetch_message(payload.message_id)
        except:
            return
        
        if not message.embeds or not message.author.id == self.bot.user.id:
            return
        
        embed = message.embeds[0]
        quote_id = None
        for field in embed.fields:
            if field.name == "Quote ID":
                quote_id = int(field.value.strip("`#"))
                break
        
        if not quote_id:
            return
        
        user_id = payload.user_id
        emoji = str(payload.emoji)
        
        if emoji in ["👍", "👎"]:
            await remove_reaction(quote_id, user_id)
        elif emoji == "⭐":
            await remove_favorite(user_id, quote_id)

async def setup(bot):
    await bot.add_cog(QuoteCommands(bot))

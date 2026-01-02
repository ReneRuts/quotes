import discord
from discord.ext import commands
from discord import app_commands
from utils.database import add_favorite, get_user_favorites, remove_favorite, is_favorites_enabled
import re

class FavoritesView(discord.ui.View):
    def __init__(self, user_id, favorites, page=0):
        super().__init__(timeout=180)
        self.user_id = user_id
        self.favorites = favorites
        self.page = page
        self.per_page = 5
        
        # Update button states
        self.update_buttons()
    
    def update_buttons(self):
        total_pages = (len(self.favorites) + self.per_page - 1) // self.per_page
        
        self.prev_button.disabled = self.page == 0
        self.next_button.disabled = self.page >= total_pages - 1
    
    def get_embed(self):
        start = self.page * self.per_page
        end = start + self.per_page
        page_favorites = self.favorites[start:end]
        
        embed = discord.Embed(
            title="❤️ Your Favorite Quotes",
            color=discord.Color.gold()
        )
        
        if not page_favorites:
            embed.description = "You don't have any favorite quotes yet!\nReact wit ❤️ to quotes to save them."
            return embed
        
        for fav_id, quote_text, quote_author, added_at in page_favorites:
            # Truncate long quotes
            display_text = quote_text[:150] + "..." if len(quote_text) > 150 else quote_text
            embed.add_field(
                name=f"#{fav_id} - {quote_author}",
                value=f"_{display_text}_",
                inline=False
            )
        
        total_pages = (len(self.favorites) + self.per_page - 1) // self.per_page
        embed.set_footer(text=f"Page {self.page + 1}/{total_pages} • {len(self.favorites)} total favorites")
        
        return embed
    
    @discord.ui.button(label="◀️ Previous", style=discord.ButtonStyle.gray)
    async def prev_button(self, interaction: discord.Interaction, button: discord.ui.Button):
        if interaction.user.id != self.user_id:
            return await interaction.response.send_message("❌ This is not your menu!", ephemeral=True)
        
        self.page -= 1
        self.update_buttons()
        await interaction.response.edit_message(embed=self.get_embed(), view=self)
    
    @discord.ui.button(label="▶️ Next", style=discord.ButtonStyle.gray)
    async def next_button(self, interaction: discord.Interaction, button: discord.ui.Button):
        if interaction.user.id != self.user_id:
            return await interaction.response.send_message("❌ This is not your menu!", ephemeral=True)
        
        self.page += 1
        self.update_buttons()
        await interaction.response.edit_message(embed=self.get_embed(), view=self)

class Favorites(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @app_commands.command(name="favorites", description="View your favorite quotes")
    async def favorites(self, interaction: discord.Interaction):
        favorites = await get_user_favorites(interaction.user.id, interaction.guild.id)
        
        view = FavoritesView(interaction.user.id, favorites)
        await interaction.response.send_message(embed=view.get_embed(), view=view, ephemeral=True)

    @commands.Cog.listener()
    async def on_raw_reaction_add(self, payload):
        if payload.user_id == self.bot.user.id:
            return
        
        if str(payload.emoji) != "❤️":
            return
        
        # Check if favorites are enabled
        if not await is_favorites_enabled(payload.guild_id):
            return
        
        channel = self.bot.get_channel(payload.channel_id)
        if not channel:
            return
        
        try:
            message = await channel.fetch_message(payload.message_id)
        except:
            return
        
        if not hasattr(message, "content") or not message.content:
            return

        if message.author.id != self.bot.user.id:
            return

        content = message.content.strip()

        content = re.sub(r'<@&\d+>\s*', '', content).strip()

        pattern = r'["“]?_?(?P<quote>.+?)_?["”]?\s*[\n\r]+[-—]\s*\*?\*?(?P<author>.+?)\*?\*?$'

        match = re.search(pattern, content, re.DOTALL)

        if not match:
            return

        quote_text = match.group("quote").strip()
        quote_author = match.group("author").strip()

        quote_author = re.sub(r'\[([^\]]+)\]\([^\)]+\)', r'\1', quote_author)

            
        success = await add_favorite(payload.user_id, quote_text, quote_author, payload.guild_id)
            
        if success:
            try:
                user = await self.bot.fetch_user(payload.user_id)
                await user.send(f"❤️ Quote saved to your favorites!\n\n_{quote_text}_\n— **{quote_author}**")
            except:
                pass  # User has DMs disabled

async def setup(bot):
    await bot.add_cog(Favorites(bot))

import discord
from datetime import datetime

async def create_quote_embed(quote_text: str, author: str, color: str = "#667eea", footer: str = None, quote_id: int = None, likes: int = 0, dislikes: int = 0):
    """Create a beautiful embed for a quote"""
    try:
        color_int = int(color.replace("#", ""), 16)
    except:
        color_int = 0x667eea
    
    embed = discord.Embed(
        description=f"*{quote_text}*",
        color=color_int,
        timestamp=datetime.utcnow()
    )
    
    embed.set_author(name="📖 Daily Quote", icon_url="https://i.imgur.com/your-icon.png")
    embed.add_field(name="Author", value=f"**{author}**", inline=False)
    
    if quote_id:
        embed.add_field(name="Quote ID", value=f"`#{quote_id}`", inline=True)
        embed.add_field(name="Reactions", value=f"👍 {likes} | 👎 {dislikes}", inline=True)
    
    if footer:
        embed.set_footer(text=footer)
    else:
        embed.set_footer(text="React with 👍 or 👎 • Add to favorites with ⭐")
    
    return embed

async def create_stats_embed(user, guild, rank: int = None):
    """Create stats embed for a user"""
    embed = discord.Embed(
        title=f"📊 Stats for {user.display_name}",
        color=discord.Color.blue(),
        timestamp=datetime.utcnow()
    )
    
    embed.set_thumbnail(url=user.display_avatar.url)
    
    if rank:
        embed.add_field(name="🏆 Server Rank", value=f"#{rank}", inline=True)
    
    embed.add_field(name="⭐ XP", value=f"{user[3]:,}", inline=True)
    embed.add_field(name="📈 Level", value=f"{user[4]}", inline=True)
    embed.add_field(name="👀 Quotes Viewed", value=f"{user[5]:,}", inline=True)
    embed.add_field(name="📝 Quotes Submitted", value=f"{user[6]:,}", inline=True)
    embed.add_field(name="🔥 Current Streak", value=f"{user[7]} days", inline=True)
    embed.add_field(name="🏅 Longest Streak", value=f"{user[8]} days", inline=True)
    
    return embed

async def create_leaderboard_embed(guild, leaderboard, leaderboard_type: str = "XP"):
    """Create leaderboard embed"""
    embed = discord.Embed(
        title=f"🏆 {guild.name} - Top 10 {leaderboard_type}",
        color=discord.Color.gold(),
        timestamp=datetime.utcnow()
    )
    
    medals = ["🥇", "🥈", "🥉"]
    
    description = ""
    for i, user_data in enumerate(leaderboard, 1):
        user_id = user_data[2]
        value = user_data[3] if leaderboard_type == "XP" else user_data[7]  # XP or streak
        
        medal = medals[i-1] if i <= 3 else f"`#{i}`"
        description += f"{medal} <@{user_id}> - **{value:,}** {leaderboard_type}\n"
    
    embed.description = description
    embed.set_footer(text=f"Keep grinding! • Use /stats to see your stats")
    
    return embed

async def create_quote_list_embed(quotes, title: str, page: int = 1, per_page: int = 5):
    """Create paginated quote list embed"""
    embed = discord.Embed(
        title=title,
        color=discord.Color.purple(),
        timestamp=datetime.utcnow()
    )
    
    start = (page - 1) * per_page
    end = start + per_page
    page_quotes = quotes[start:end]
    
    for quote in page_quotes:
        quote_id, guild_id, text, author, category, submitter, submitted_at, approved, likes, dislikes = quote
        embed.add_field(
            name=f"#{quote_id} - {author}",
            value=f"{text[:100]}{'...' if len(text) > 100 else ''}\n👍 {likes} | 👎 {dislikes} | 📂 {category}",
            inline=False
        )
    
    total_pages = (len(quotes) + per_page - 1) // per_page
    embed.set_footer(text=f"Page {page}/{total_pages} • {len(quotes)} total quotes")
    
    return embed

async def create_help_embed():
    """Create help embed with all commands"""
    embed = discord.Embed(
        title="📖 Quote Bot - Command Guide",
        description="Your ultimate daily motivation companion!",
        color=discord.Color.blue(),
        timestamp=datetime.utcnow()
    )
    
    # Setup Commands
    embed.add_field(
        name="⚙️ Setup Commands",
        value=(
            "`/setup` - View/configure server settings\n"
            "`/testquote` - Send a test quote\n"
            "`/customize` - Customize embed appearance\n"
        ),
        inline=False
    )
    
    # Quote Commands
    embed.add_field(
        name="📖 Quote Commands",
        value=(
            "`/quote random` - Get a random quote\n"
            "`/quote author:<name>` - Quotes by author\n"
            "`/quote category:<cat>` - Quotes by category\n"
            "`/quote search:<keyword>` - Search quotes\n"
        ),
        inline=False
    )
    
    # Custom Quotes
    embed.add_field(
        name="✏️ Custom Quotes",
        value=(
            "`/addquote` - Add a custom quote\n"
            "`/myquotes` - View your submitted quotes\n"
            "`/deletequote` - Delete your quote\n"
            "`/favorites` - View favorite quotes\n"
        ),
        inline=False
    )
    
    # Games
    embed.add_field(
        name="🎮 Games & Stats",
        value=(
            "`/stats` - View your stats\n"
            "`/leaderboard` - Server leaderboard\n"
            "`/level` - View your level progress\n"
            "`/streak` - View your streak\n"
        ),
        inline=False
    )
    
    # Moderation
    embed.add_field(
        name="🛡️ Moderation (Admin Only)",
        value=(
            "`/approve` - Approve pending quotes\n"
            "`/pending` - View pending quotes\n"
            "`/quotestats` - Server quote statistics\n"
            "`/history` - Recent quote history\n"
        ),
        inline=False
    )
    
    embed.set_footer(text="Made with ❤️ by René Ruts")
    
    return embed

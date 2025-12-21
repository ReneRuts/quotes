import aiosqlite
import os
from datetime import datetime

DB_PATH = "data/quotes.db"

async def init_database():
    """Initialize the database with all required tables"""
    os.makedirs("data", exist_ok=True)
    
    async with aiosqlite.connect(DB_PATH) as db:
        # Custom quotes table
        await db.execute("""
            CREATE TABLE IF NOT EXISTS custom_quotes (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                guild_id INTEGER NOT NULL,
                quote TEXT NOT NULL,
                author TEXT NOT NULL,
                category TEXT DEFAULT 'general',
                submitter_id INTEGER,
                submitted_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                approved BOOLEAN DEFAULT 0,
                likes INTEGER DEFAULT 0,
                dislikes INTEGER DEFAULT 0
            )
        """)
        
        # Quote reactions (likes/dislikes)
        await db.execute("""
            CREATE TABLE IF NOT EXISTS quote_reactions (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                quote_id INTEGER NOT NULL,
                user_id INTEGER NOT NULL,
                reaction_type TEXT NOT NULL,
                UNIQUE(quote_id, user_id),
                FOREIGN KEY (quote_id) REFERENCES custom_quotes(id)
            )
        """)
        
        # User stats and games
        await db.execute("""
            CREATE TABLE IF NOT EXISTS user_stats (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                guild_id INTEGER NOT NULL,
                user_id INTEGER NOT NULL,
                xp INTEGER DEFAULT 0,
                level INTEGER DEFAULT 1,
                quotes_viewed INTEGER DEFAULT 0,
                quotes_submitted INTEGER DEFAULT 0,
                current_streak INTEGER DEFAULT 0,
                longest_streak INTEGER DEFAULT 0,
                last_view_date DATE,
                UNIQUE(guild_id, user_id)
            )
        """)
        
        # Achievements
        await db.execute("""
            CREATE TABLE IF NOT EXISTS achievements (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                name TEXT UNIQUE NOT NULL,
                description TEXT NOT NULL,
                icon TEXT NOT NULL,
                requirement_type TEXT NOT NULL,
                requirement_value INTEGER NOT NULL
            )
        """)
        
        # User achievements
        await db.execute("""
            CREATE TABLE IF NOT EXISTS user_achievements (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                guild_id INTEGER NOT NULL,
                user_id INTEGER NOT NULL,
                achievement_id INTEGER NOT NULL,
                earned_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                UNIQUE(guild_id, user_id, achievement_id),
                FOREIGN KEY (achievement_id) REFERENCES achievements(id)
            )
        """)
        
        # Quote history (what was sent when)
        await db.execute("""
            CREATE TABLE IF NOT EXISTS quote_history (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                guild_id INTEGER NOT NULL,
                quote_id INTEGER,
                quote_text TEXT NOT NULL,
                author TEXT NOT NULL,
                sent_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                views INTEGER DEFAULT 0
            )
        """)
        
        # Favorites
        await db.execute("""
            CREATE TABLE IF NOT EXISTS favorites (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                user_id INTEGER NOT NULL,
                quote_id INTEGER NOT NULL,
                added_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                UNIQUE(user_id, quote_id)
            )
        """)
        
        # Server customization
        await db.execute("""
            CREATE TABLE IF NOT EXISTS server_customization (
                guild_id INTEGER PRIMARY KEY,
                embed_color TEXT DEFAULT '#667eea',
                show_images BOOLEAN DEFAULT 0,
                custom_footer TEXT,
                require_approval BOOLEAN DEFAULT 1
            )
        """)
        
        await db.commit()
        print("✅ Database initialized successfully")

# Custom Quotes Functions
async def add_custom_quote(guild_id: int, quote: str, author: str, category: str, submitter_id: int, approved: bool = False):
    """Add a custom quote to the database"""
    async with aiosqlite.connect(DB_PATH) as db:
        await db.execute(
            "INSERT INTO custom_quotes (guild_id, quote, author, category, submitter_id, approved) VALUES (?, ?, ?, ?, ?, ?)",
            (guild_id, quote, author, category, submitter_id, approved)
        )
        await db.commit()
        cursor = await db.execute("SELECT last_insert_rowid()")
        quote_id = (await cursor.fetchone())[0]
        return quote_id

async def get_random_custom_quote(guild_id: int, category: str = None):
    """Get a random approved custom quote"""
    async with aiosqlite.connect(DB_PATH) as db:
        if category:
            cursor = await db.execute(
                "SELECT * FROM custom_quotes WHERE guild_id = ? AND category = ? AND approved = 1 ORDER BY RANDOM() LIMIT 1",
                (guild_id, category)
            )
        else:
            cursor = await db.execute(
                "SELECT * FROM custom_quotes WHERE guild_id = ? AND approved = 1 ORDER BY RANDOM() LIMIT 1",
                (guild_id,)
            )
        return await cursor.fetchone()

async def get_quotes_by_author(guild_id: int, author: str):
    """Get all quotes by a specific author"""
    async with aiosqlite.connect(DB_PATH) as db:
        cursor = await db.execute(
            "SELECT * FROM custom_quotes WHERE guild_id = ? AND author LIKE ? AND approved = 1",
            (guild_id, f"%{author}%")
        )
        return await cursor.fetchall()

async def search_quotes(guild_id: int, keyword: str):
    """Search quotes by keyword"""
    async with aiosqlite.connect(DB_PATH) as db:
        cursor = await db.execute(
            "SELECT * FROM custom_quotes WHERE guild_id = ? AND (quote LIKE ? OR author LIKE ?) AND approved = 1",
            (guild_id, f"%{keyword}%", f"%{keyword}%")
        )
        return await cursor.fetchall()

async def get_pending_quotes(guild_id: int):
    """Get all pending quotes for approval"""
    async with aiosqlite.connect(DB_PATH) as db:
        cursor = await db.execute(
            "SELECT * FROM custom_quotes WHERE guild_id = ? AND approved = 0",
            (guild_id,)
        )
        return await cursor.fetchall()

async def approve_quote(quote_id: int):
    """Approve a pending quote"""
    async with aiosqlite.connect(DB_PATH) as db:
        await db.execute("UPDATE custom_quotes SET approved = 1 WHERE id = ?", (quote_id,))
        await db.commit()

async def delete_quote(quote_id: int):
    """Delete a quote"""
    async with aiosqlite.connect(DB_PATH) as db:
        await db.execute("DELETE FROM custom_quotes WHERE id = ?", (quote_id,))
        await db.commit()

# Reaction Functions
async def add_reaction(quote_id: int, user_id: int, reaction_type: str):
    """Add or update a reaction to a quote"""
    async with aiosqlite.connect(DB_PATH) as db:
        # Remove existing reaction
        await db.execute("DELETE FROM quote_reactions WHERE quote_id = ? AND user_id = ?", (quote_id, user_id))
        # Add new reaction
        await db.execute(
            "INSERT INTO quote_reactions (quote_id, user_id, reaction_type) VALUES (?, ?, ?)",
            (quote_id, user_id, reaction_type)
        )
        # Update quote counts
        if reaction_type == "like":
            await db.execute("UPDATE custom_quotes SET likes = likes + 1 WHERE id = ?", (quote_id,))
        else:
            await db.execute("UPDATE custom_quotes SET dislikes = dislikes + 1 WHERE id = ?", (quote_id,))
        await db.commit()

async def remove_reaction(quote_id: int, user_id: int):
    """Remove a reaction"""
    async with aiosqlite.connect(DB_PATH) as db:
        cursor = await db.execute(
            "SELECT reaction_type FROM quote_reactions WHERE quote_id = ? AND user_id = ?",
            (quote_id, user_id)
        )
        result = await cursor.fetchone()
        if result:
            reaction_type = result[0]
            await db.execute("DELETE FROM quote_reactions WHERE quote_id = ? AND user_id = ?", (quote_id, user_id))
            if reaction_type == "like":
                await db.execute("UPDATE custom_quotes SET likes = likes - 1 WHERE id = ?", (quote_id,))
            else:
                await db.execute("UPDATE custom_quotes SET dislikes = dislikes - 1 WHERE id = ?", (quote_id,))
            await db.commit()

# User Stats Functions
async def update_user_stats(guild_id: int, user_id: int, action: str):
    """Update user statistics"""
    async with aiosqlite.connect(DB_PATH) as db:
        # Get or create user
        cursor = await db.execute(
            "SELECT * FROM user_stats WHERE guild_id = ? AND user_id = ?",
            (guild_id, user_id)
        )
        user = await cursor.fetchone()
        
        today = datetime.now().date()
        
        if not user:
            await db.execute(
                "INSERT INTO user_stats (guild_id, user_id, xp, quotes_viewed, last_view_date, current_streak) VALUES (?, ?, 5, 1, ?, 1)",
                (guild_id, user_id, today)
            )
        else:
            xp_gain = 5 if action == "view" else 10
            last_view = datetime.fromisoformat(user[9]).date() if user[9] else None
            current_streak = user[6]
            longest_streak = user[7]
            
            # Update streak
            if last_view and (today - last_view).days == 1:
                current_streak += 1
                longest_streak = max(longest_streak, current_streak)
            elif last_view and (today - last_view).days > 1:
                current_streak = 1
            
            if action == "view":
                await db.execute(
                    "UPDATE user_stats SET xp = xp + ?, quotes_viewed = quotes_viewed + 1, last_view_date = ?, current_streak = ?, longest_streak = ? WHERE guild_id = ? AND user_id = ?",
                    (xp_gain, today, current_streak, longest_streak, guild_id, user_id)
                )
            elif action == "submit":
                await db.execute(
                    "UPDATE user_stats SET xp = xp + ?, quotes_submitted = quotes_submitted + 1 WHERE guild_id = ? AND user_id = ?",
                    (xp_gain, guild_id, user_id)
                )
        
        await db.commit()

async def get_user_stats(guild_id: int, user_id: int):
    """Get user statistics"""
    async with aiosqlite.connect(DB_PATH) as db:
        cursor = await db.execute(
            "SELECT * FROM user_stats WHERE guild_id = ? AND user_id = ?",
            (guild_id, user_id)
        )
        return await cursor.fetchone()

async def get_leaderboard(guild_id: int, sort_by: str = "xp", limit: int = 10):
    """Get server leaderboard"""
    async with aiosqlite.connect(DB_PATH) as db:
        cursor = await db.execute(
            f"SELECT * FROM user_stats WHERE guild_id = ? ORDER BY {sort_by} DESC LIMIT ?",
            (guild_id, limit)
        )
        return await cursor.fetchall()

# Favorites Functions
async def add_favorite(user_id: int, quote_id: int):
    """Add a quote to favorites"""
    async with aiosqlite.connect(DB_PATH) as db:
        try:
            await db.execute(
                "INSERT INTO favorites (user_id, quote_id) VALUES (?, ?)",
                (user_id, quote_id)
            )
            await db.commit()
            return True
        except:
            return False

async def remove_favorite(user_id: int, quote_id: int):
    """Remove a quote from favorites"""
    async with aiosqlite.connect(DB_PATH) as db:
        await db.execute("DELETE FROM favorites WHERE user_id = ? AND quote_id = ?", (user_id, quote_id))
        await db.commit()

async def get_user_favorites(user_id: int):
    """Get user's favorite quotes"""
    async with aiosqlite.connect(DB_PATH) as db:
        cursor = await db.execute(
            """SELECT cq.* FROM custom_quotes cq 
               JOIN favorites f ON cq.id = f.quote_id 
               WHERE f.user_id = ?""",
            (user_id,)
        )
        return await cursor.fetchall()

# Quote History Functions
async def log_quote_sent(guild_id: int, quote_text: str, author: str, quote_id: int = None):
    """Log when a quote was sent"""
    async with aiosqlite.connect(DB_PATH) as db:
        await db.execute(
            "INSERT INTO quote_history (guild_id, quote_id, quote_text, author) VALUES (?, ?, ?, ?)",
            (guild_id, quote_id, quote_text, author)
        )
        await db.commit()

async def get_quote_history(guild_id: int, limit: int = 10):
    """Get recent quote history"""
    async with aiosqlite.connect(DB_PATH) as db:
        cursor = await db.execute(
            "SELECT * FROM quote_history WHERE guild_id = ? ORDER BY sent_at DESC LIMIT ?",
            (guild_id, limit)
        )
        return await cursor.fetchall()

# Server Customization Functions
async def get_server_customization(guild_id: int):
    """Get server customization settings"""
    async with aiosqlite.connect(DB_PATH) as db:
        cursor = await db.execute(
            "SELECT * FROM server_customization WHERE guild_id = ?",
            (guild_id,)
        )
        result = await cursor.fetchone()
        if not result:
            # Create default
            await db.execute(
                "INSERT INTO server_customization (guild_id) VALUES (?)",
                (guild_id,)
            )
            await db.commit()
            return (guild_id, '#667eea', 0, None, 1)
        return result

async def update_server_customization(guild_id: int, **kwargs):
    """Update server customization"""
    async with aiosqlite.connect(DB_PATH) as db:
        for key, value in kwargs.items():
            await db.execute(
                f"UPDATE server_customization SET {key} = ? WHERE guild_id = ?",
                (value, guild_id)
            )
        await db.commit()

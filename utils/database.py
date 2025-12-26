import aiosqlite
import os

DB_PATH = "data/quotes.db"

async def init_database():
    """Initialize database with only favorites"""
    os.makedirs("data", exist_ok=True)
    
    async with aiosqlite.connect(DB_PATH) as db:
        # Favorites table
        await db.execute("""
            CREATE TABLE IF NOT EXISTS favorites (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                user_id INTEGER NOT NULL,
                quote_text TEXT NOT NULL,
                quote_author TEXT NOT NULL,
                added_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                guild_id INTEGER NOT NULL
            )
        """)
        
        # Server settings for favorites feature toggle
        await db.execute("""
            CREATE TABLE IF NOT EXISTS server_features (
                guild_id INTEGER PRIMARY KEY,
                favorites_enabled BOOLEAN DEFAULT 1
            )
        """)
        
        await db.commit()
        print("✅ Database initialized")

async def add_favorite(user_id: int, quote_text: str, quote_author: str, guild_id: int):
    """Add a quote to user's favorites"""
    async with aiosqlite.connect(DB_PATH) as db:
        # Check if already favorited
        cursor = await db.execute(
            "SELECT id FROM favorites WHERE user_id = ? AND quote_text = ? AND guild_id = ?",
            (user_id, quote_text, guild_id)
        )
        exists = await cursor.fetchone()
        
        if exists:
            return False  # Already favorited
        
        await db.execute(
            "INSERT INTO favorites (user_id, quote_text, quote_author, guild_id) VALUES (?, ?, ?, ?)",
            (user_id, quote_text, quote_author, guild_id)
        )
        await db.commit()
        return True

async def remove_favorite(user_id: int, favorite_id: int):
    """Remove a favorite by ID"""
    async with aiosqlite.connect(DB_PATH) as db:
        await db.execute(
            "DELETE FROM favorites WHERE id = ? AND user_id = ?",
            (favorite_id, user_id)
        )
        await db.commit()

async def get_user_favorites(user_id: int, guild_id: int = None):
    """Get user's favorite quotes"""
    async with aiosqlite.connect(DB_PATH) as db:
        if guild_id:
            cursor = await db.execute(
                "SELECT id, quote_text, quote_author, added_at FROM favorites WHERE user_id = ? AND guild_id = ? ORDER BY added_at DESC",
                (user_id, guild_id)
            )
        else:
            cursor = await db.execute(
                "SELECT id, quote_text, quote_author, added_at FROM favorites WHERE user_id = ? ORDER BY added_at DESC",
                (user_id,)
            )
        return await cursor.fetchall()

async def is_favorites_enabled(guild_id: int):
    """Check if favorites feature is enabled for this server"""
    async with aiosqlite.connect(DB_PATH) as db:
        cursor = await db.execute(
            "SELECT favorites_enabled FROM server_features WHERE guild_id = ?",
            (guild_id,)
        )
        result = await cursor.fetchone()
        
        if result is None:
            # Create default
            await db.execute(
                "INSERT INTO server_features (guild_id, favorites_enabled) VALUES (?, 1)",
                (guild_id,)
            )
            await db.commit()
            return True
        
        return bool(result[0])

async def set_favorites_enabled(guild_id: int, enabled: bool):
    """Enable or disable favorites feature"""
    async with aiosqlite.connect(DB_PATH) as db:
        await db.execute(
            "INSERT OR REPLACE INTO server_features (guild_id, favorites_enabled) VALUES (?, ?)",
            (guild_id, enabled)
        )
        await db.commit()

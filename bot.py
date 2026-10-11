import asyncio
import os
import sys
import time
import logging
import sqlite3
import threading
from datetime import datetime, timezone
from http.server import HTTPServer, BaseHTTPRequestHandler
from functools import lru_cache

# Ensure event loop exists before pyrogram import on modern Python versions
try:
    asyncio.get_event_loop()
except RuntimeError:
    loop = asyncio.new_event_loop()
    asyncio.set_event_loop(loop)

from pyrogram import Client, filters, idle
from pyrogram.types import (
    InlineKeyboardMarkup,
    InlineKeyboardButton,
    CallbackQuery,
    Message,
    BotCommand
)
from pyrogram.errors import FloodWait, UserIsBlocked, InputUserDeactivated

from deep_translator import GoogleTranslator

try:
    from dotenv import load_dotenv
    load_dotenv()
except ImportError:
    pass

# ==================== CONFIGURATION ====================
BOT_TOKEN = "8829083195:AAGbeSFojihT6R0V8Pi-pUYWui__e6QINW8"
API_ID = 36971153
API_HASH = "e5e4c9c88d0c5c2654d8fbe985523c9c"
OWNER_ID = int(os.getenv("OWNER_ID", "5650859707"))
DB_CHANNEL_ID = int(os.getenv("DB_CHANNEL_ID", "-1004440598458"))
DATABASE_CHANNEL_ID = int(os.getenv("DATABASE_CHANNEL_ID", str(DB_CHANNEL_ID)))
DATABASE_GROUP_ID = int(os.getenv("DATABASE_GROUP_ID", str(DB_CHANNEL_ID)))
PORT = int(os.getenv("PORT", "8080"))
DB_PATH = os.path.join(os.path.dirname(os.path.abspath(__file__)), "brahmacharya.db")

# Setup Logging
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - [%(levelname)s] - %(name)s - %(message)s"
)
logger = logging.getLogger("BrahmacharyaBot")

# ==================== DATABASE LAYER ====================
class Database:
    def __init__(self, db_path: str = DB_PATH):
        self.db_path = db_path
        # Ensure parent directory exists
        db_dir = os.path.dirname(os.path.abspath(self.db_path))
        if db_dir and not os.path.exists(db_dir):
            os.makedirs(db_dir, exist_ok=True)
        self._init_db()

    def _get_connection(self):
        conn = sqlite3.connect(
            self.db_path,
            timeout=30,
            isolation_level=None,
            check_same_thread=False
        )
        conn.row_factory = sqlite3.Row
        try:
            conn.execute("PRAGMA journal_mode=WAL;")
            conn.execute("PRAGMA busy_timeout=30000;")
        except Exception:
            pass
        return conn

    def _init_db(self):
        with self._get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute("""
                CREATE TABLE IF NOT EXISTS users (
                    user_id INTEGER PRIMARY KEY,
                    first_name TEXT,
                    last_name TEXT,
                    username TEXT,
                    streak_start TEXT,
                    longest_streak_days INTEGER DEFAULT 0,
                    relapses_count INTEGER DEFAULT 0,
                    language TEXT DEFAULT 'en',
                    pledge_days INTEGER DEFAULT 30,
                    joined_at TEXT,
                    last_active TEXT
                )
            """)
            cursor.execute("""
                CREATE TABLE IF NOT EXISTS files (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    message_id INTEGER,
                    channel_id INTEGER,
                    category TEXT DEFAULT '',
                    file_id TEXT,
                    file_name TEXT,
                    file_size INTEGER DEFAULT 0,
                    file_type TEXT DEFAULT '',
                    caption TEXT DEFAULT '',
                    mime_type TEXT DEFAULT '',
                    created_at TEXT
                )
            """)
            cursor.execute("""
                CREATE TABLE IF NOT EXISTS channel_media (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    message_id INTEGER,
                    channel_id INTEGER,
                    category TEXT DEFAULT '',
                    file_id TEXT,
                    file_name TEXT,
                    file_size INTEGER DEFAULT 0,
                    caption TEXT,
                    mime_type TEXT DEFAULT '',
                    created_at TEXT
                )
            """)
            cursor.execute("""
                CREATE TABLE IF NOT EXISTS bot_settings (
                    key TEXT PRIMARY KEY,
                    value TEXT
                )
            """)
            # Ensure 'category', 'file_size', and 'mime_type' columns exist in files & channel_media tables
            for col, col_def in [
                ("category", "TEXT DEFAULT ''"),
                ("file_size", "INTEGER DEFAULT 0"),
                ("mime_type", "TEXT DEFAULT ''"),
                ("file_type", "TEXT DEFAULT ''"),
                ("caption", "TEXT DEFAULT ''")
            ]:
                try:
                    cursor.execute(f"ALTER TABLE files ADD COLUMN {col} {col_def}")
                except Exception:
                    pass
                try:
                    cursor.execute(f"ALTER TABLE channel_media ADD COLUMN {col} {col_def}")
                except Exception:
                    pass

            cursor.execute("CREATE UNIQUE INDEX IF NOT EXISTS idx_files_chat_msg ON files(channel_id, message_id);")
            cursor.execute("CREATE UNIQUE INDEX IF NOT EXISTS idx_channel_media_chat_msg ON channel_media(channel_id, message_id);")
            conn.commit()

    def set_setting(self, key: str, value: str):
        with self._get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute("INSERT OR REPLACE INTO bot_settings (key, value) VALUES (?, ?)", (key, str(value)))
            conn.commit()

    def get_setting(self, key: str, default: str = "") -> str:
        with self._get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute("SELECT value FROM bot_settings WHERE key = ?", (key,))
            row = cursor.fetchone()
            return row["value"] if row else default

    def set_index_mode(self, mode: str):
        self.set_setting("channel_index_mode", mode.lower().strip())

    def get_index_mode(self, default: str = "books") -> str:
        return self.get_setting("channel_index_mode", default)

    def save_file(self, message_id: int, channel_id: int, category: str, file_id: str, file_name: str, file_size: int = 0, file_type: str = "", caption: str = "", mime_type: str = ""):
        now_iso = datetime.now(timezone.utc).isoformat()
        cat_norm = category.lower().strip()
        with self._get_connection() as conn:
            cursor = conn.cursor()
            existing_id = None
            if message_id and channel_id:
                cursor.execute("""
                    SELECT id FROM files
                    WHERE message_id = ? AND channel_id = ?
                """, (message_id, channel_id))
                row = cursor.fetchone()
                if row:
                    existing_id = row["id"]
            elif file_id:
                cursor.execute("SELECT id FROM files WHERE file_id = ?", (file_id,))
                row = cursor.fetchone()
                if row:
                    existing_id = row["id"]

            is_new = (existing_id is None)

            # Insert or REPLACE into SQLite database table 'files' (file_id, file_name, file_size, category, caption, mime_type)
            cursor.execute("""
                INSERT OR REPLACE INTO files (
                    channel_id, message_id, file_id, file_name, file_size, file_type, category, caption, mime_type, created_at
                ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            """, (
                channel_id,
                message_id,
                file_id or "",
                file_name or "",
                file_size or 0,
                file_type or "",
                cat_norm,
                caption or "",
                mime_type or "",
                now_iso
            ))
            row_id = cursor.lastrowid

            # Synchronize with channel_media table for legacy compatibility
            cursor.execute("""
                INSERT OR REPLACE INTO channel_media (
                    channel_id, message_id, file_id, file_name, file_size, category, caption, mime_type, created_at
                ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
            """, (
                channel_id,
                message_id,
                file_id or "",
                file_name or "",
                file_size or 0,
                cat_norm,
                caption or "",
                mime_type or "",
                now_iso
            ))

            conn.commit()
            return row_id, is_new

    def save_media(self, message_id: int, channel_id: int, category: str, file_id: str, file_name: str, caption: str = "", file_size: int = 0, mime_type: str = ""):
        res_id, _ = self.save_file(message_id, channel_id, category, file_id, file_name, file_size, "", caption, mime_type)
        return res_id

    def get_media_by_id(self, media_id: int):
        with self._get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute("SELECT * FROM files WHERE id = ?", (media_id,))
            row = cursor.fetchone()
            if row:
                return dict(row)
            cursor.execute("SELECT * FROM channel_media WHERE id = ?", (media_id,))
            row = cursor.fetchone()
            return dict(row) if row else None

    def get_category_media(self, category: str):
        cat = category.lower().strip()
        cats = [cat]
        if cat in ["book", "books"]:
            cats = ["book", "books"]
        elif cat in ["song", "songs"]:
            cats = ["song", "songs"]
        elif cat in ["quote", "quotes"]:
            cats = ["quote", "quotes"]
        elif cat in ["workout", "workouts"]:
            cats = ["workout", "workouts"]

        placeholders = ",".join("?" for _ in cats)
        with self._get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute(f"""
                SELECT id, message_id, channel_id, file_id, file_name, category, caption
                FROM files 
                WHERE LOWER(category) IN ({placeholders})
                ORDER BY id ASC
            """, cats)
            rows = [dict(row) for row in cursor.fetchall()]
            if not rows:
                cursor.execute(f"""
                    SELECT id, message_id, channel_id, file_id, file_name, category, caption
                    FROM channel_media 
                    WHERE LOWER(category) IN ({placeholders})
                    ORDER BY id ASC
                """, cats)
                rows = [dict(row) for row in cursor.fetchall()]
            return rows

    def get_saved_media(self, category: str, limit: int = 50):
        return self.get_category_media(category)

    def get_user(self, user_id: int):
        with self._get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute("SELECT * FROM users WHERE user_id = ?", (user_id,))
            row = cursor.fetchone()
            return dict(row) if row else None

    def add_or_update_user(self, user_id: int, first_name: str, last_name: str, username: str):
        now_iso = datetime.now(timezone.utc).isoformat()
        with self._get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute("SELECT user_id, streak_start FROM users WHERE user_id = ?", (user_id,))
            row = cursor.fetchone()
            is_new = False
            if not row:
                cursor.execute("""
                    INSERT INTO users (user_id, first_name, last_name, username, streak_start, longest_streak_days, relapses_count, language, pledge_days, joined_at, last_active)
                    VALUES (?, ?, ?, ?, ?, 0, 0, 'en', 30, ?, ?)
                """, (user_id, first_name or "", last_name or "", username or "", now_iso, now_iso, now_iso))
                is_new = True
            else:
                cursor.execute("""
                    UPDATE users
                    SET first_name = ?, last_name = ?, username = ?, last_active = ?
                    WHERE user_id = ?
                """, (first_name or "", last_name or "", username or "", now_iso, user_id))
            conn.commit()
            return is_new

    def set_language(self, user_id: int, lang_code: str):
        with self._get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute("UPDATE users SET language = ? WHERE user_id = ?", (lang_code, user_id))
            conn.commit()

    def get_language(self, user_id: int) -> str:
        user = self.get_user(user_id)
        return user.get("language", "en") if user else "en"

    def set_pledge(self, user_id: int, days: int):
        with self._get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute("UPDATE users SET pledge_days = ? WHERE user_id = ?", (days, user_id))
            conn.commit()

    def record_relapse(self, user_id: int):
        user = self.get_user(user_id)
        if not user:
            return None, 0
        
        now = datetime.now(timezone.utc)
        now_iso = now.isoformat()
        
        # Calculate ended streak
        streak_start = datetime.fromisoformat(user["streak_start"])
        ended_days = max(0, (now - streak_start).days)
        longest = max(user.get("longest_streak_days", 0), ended_days)
        relapses = user.get("relapses_count", 0) + 1

        with self._get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute("""
                UPDATE users
                SET streak_start = ?, longest_streak_days = ?, relapses_count = ?, last_active = ?
                WHERE user_id = ?
            """, (now_iso, longest, relapses, now_iso, user_id))
            conn.commit()

        return ended_days, relapses

    def reset_user_streak(self, user_id: int):
        now_iso = datetime.now(timezone.utc).isoformat()
        with self._get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute("""
                UPDATE users
                SET streak_start = ?, last_active = ?
                WHERE user_id = ?
            """, (now_iso, now_iso, user_id))
            conn.commit()
            return cursor.rowcount > 0

    def get_all_user_ids(self):
        with self._get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute("SELECT user_id FROM users")
            return [row["user_id"] for row in cursor.fetchall()]

    def get_stats(self):
        with self._get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute("SELECT COUNT(*) as total_users FROM users")
            total_users = cursor.fetchone()["total_users"]

            cursor.execute("SELECT COUNT(*) as active_count FROM users")
            active_users = cursor.fetchone()["active_count"]

            cursor.execute("SELECT MAX(longest_streak_days) as max_streak FROM users")
            max_streak = cursor.fetchone()["max_streak"] or 0

            cursor.execute("SELECT SUM(relapses_count) as total_relapses FROM users")
            total_relapses = cursor.fetchone()["total_relapses"] or 0

            cursor.execute("SELECT language, COUNT(*) as count FROM users GROUP BY language")
            lang_stats = {row["language"]: row["count"] for row in cursor.fetchall()}

            return {
                "total_users": total_users,
                "active_users": active_users,
                "max_streak": max_streak,
                "total_relapses": total_relapses,
                "languages": lang_stats
            }

    def get_top_leaderboard(self, limit: int = 10):
        now = datetime.now(timezone.utc)
        with self._get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute("SELECT user_id, first_name, username, streak_start, longest_streak_days FROM users")
            rows = cursor.fetchall()

            board = []
            for r in rows:
                try:
                    start_dt = datetime.fromisoformat(r["streak_start"])
                    diff = now - start_dt
                    days = max(0, diff.days)
                    hours = int((diff.total_seconds() % 86400) // 3600)
                    board.append({
                        "user_id": r["user_id"],
                        "name": r["first_name"] or "Brahmachari",
                        "username": r["username"] or "",
                        "days": days,
                        "hours": hours,
                        "total_seconds": diff.total_seconds(),
                        "longest": r["longest_streak_days"]
                    })
                except Exception:
                    continue

            board.sort(key=lambda x: x["total_seconds"], reverse=True)
            return board[:limit]

db = Database()

# ==================== TRANSLATION SYSTEM ====================
SUPPORTED_LANGUAGES = {
    "en": {"name": "English", "flag": "🇬🇧"},
    "hi": {"name": "हिन्दी (Hindi)", "flag": "🇮🇳"},
    "hinglish": {"name": "Hinglish", "flag": "🔤"},
    "or": {"name": "ଓଡ଼ିଆ (Odia)", "flag": "🇮🇳"},
    "bn": {"name": "বাংলা (Bengali)", "flag": "🇮🇳"},
    "te": {"name": "తెలుగు (Telugu)", "flag": "🇮🇳"},
    "ta": {"name": "தமிழ் (Tamil)", "flag": "🇮🇳"},
    "mr": {"name": "मराठी (Marathi)", "flag": "🇮🇳"},
    "gu": {"name": "ગુજરાતી (Gujarati)", "flag": "🇮🇳"},
    "kn": {"name": "ಕನ್ನಡ (Kannada)", "flag": "🇮🇳"},
    "ml": {"name": "മലയാളം (Malayalam)", "flag": "🇮🇳"},
    "pa": {"name": "ਪੰਜਾਬੀ (Punjabi)", "flag": "🇮🇳"},
    "es": {"name": "Español (Spanish)", "flag": "🇪🇸"},
    "ru": {"name": "Русский (Russian)", "flag": "🇷🇺"},
    "fr": {"name": "Français (French)", "flag": "🇫🇷"},
    "de": {"name": "Deutsch (German)", "flag": "🇩🇪"},
    "ar": {"name": "العربية (Arabic)", "flag": "🇸🇦"}
}

# Pre-crafted core templates for instant zero-latency responses in main languages
STATIC_TEXTS = {
    "greeting": {
        "en": "Ram Ram Brahmachari {name} 🙏\n\nWelcome to the Sacred Brahmacharya & NoFap Sanctum.\nPreserve your divine energy (Veerya), awaken your spiritual luster (Ojas), and conquer your lower senses.",
        "hi": "राम राम ब्रह्मचारी {name} 🙏\n\nपवित्र ब्रह्मचर्य एवं संकल्प साधना में आपका स्वागत है।\nअपने वीर्य की रक्षा करें, दिव्य ओज शक्ति को जागृत करें और अपनी इंद्रियों पर विजय प्राप्त करें।",
        "hinglish": "Ram Ram Brahmachari {name} 🙏\n\nPavitra Brahmacharya aur NoFap Sadhana me aapka swagat hai.\nApne Veerya ki raksha karein, Ojas shakti jagayein aur apne senses par vijay paayein.",
        "or": "ରାମ ରାମ ବ୍ରହ୍ମଚାରୀ {name} 🙏\n\nପବିତ୍ର ବ୍ରହ୍ମଚର୍ଯ୍ୟ ଏବଂ ନୋଫାପ୍ ସାଧନାରେ ଆପଣଙ୍କୁ ସ୍ୱାଗତ।\nଆପଣଙ୍କ ଦିବ୍ୟ ବୀର୍ଯ୍ୟ ଶକ୍ତି ସଂରକ୍ଷଣ କରନ୍ତୁ, ଓଜ ଶକ୍ତି ଜାଗ୍ରତ କରନ୍ତୁ ଏବଂ ଇନ୍ଦ୍ରିୟ ଉପରେ ବିଜୟ ଲାଭ କରନ୍ତୁ।"
    },
    "streak_title": {
        "en": "⚡ **BRAHMACHARYA STREAK STATUS** ⚡",
        "hi": "⚡ **ब्रह्मचर्य साधना स्थिति** ⚡",
        "hinglish": "⚡ **BRAHMACHARYA STREAK STATUS** ⚡",
        "or": "⚡ **ବ୍ରହ୍ମଚର୍ଯ୍ୟ ସାଧନା ସ୍ଥିତି** ⚡"
    },
    "rank_title": {
        "en": "👑 **Current Rank & Badge**:",
        "hi": "👑 **वर्तमान पद एवं उपाधि**:",
        "hinglish": "👑 **Current Rank & Badge**:",
        "or": "👑 **ବର୍ତ୍ତମାନ ପଦବୀ ଏବଂ ଉପାଧି**:"
    }
}

@lru_cache(maxsize=512)
def translate_text(text: str, target_lang: str) -> str:
    """Translates text with caching to avoid rate limits and improve speed."""
    if not text or target_lang in ["en", "hinglish"]:
        return text
    try:
        # map odia code to 'or' if deep-translator supports it, or google translation
        lang = "or" if target_lang == "or" else target_lang
        translated = GoogleTranslator(source='auto', target=lang).translate(text)
        return translated if translated else text
    except Exception as e:
        logger.debug(f"Translation fallback for lang {target_lang}: {e}")
        return text

def get_text(key: str, lang: str, **kwargs) -> str:
    """Get localized text or auto-translate."""
    if key in STATIC_TEXTS:
        if lang in STATIC_TEXTS[key]:
            return STATIC_TEXTS[key][lang].format(**kwargs)
        elif "en" in STATIC_TEXTS[key]:
            base = STATIC_TEXTS[key]["en"].format(**kwargs)
            return translate_text(base, lang)
    return ""

def get_rank_and_badge(days: int) -> tuple[str, str]:
    """Calculates spiritual rank, title and badge emoji."""
    if days < 4:
        return "🥉 Shishya (Seeker)", "Beginning of self-mastery. Hold the fort!"
    elif days < 8:
        return "🌱 Sadhak (Disciplined)", "First milestone crossed. Mind is stabilizing."
    elif days < 15:
        return "🌿 Veerya Rakshak (Energy Preserver)", "Vital energy is circulating into your blood."
    elif days < 22:
        return "🔥 Agni Sadhak (Habit Master)", "Old neuro-pathways are burning away."
    elif days < 31:
        return "⚡ Ojas Seeker (Transmuter)", "One full solar cycle! Eyes radiate clarity."
    elif days < 61:
        return "🛡️ Mahaveer Brahmachari (Indomitable)", "Immense willpower and physical stamina."
    elif days < 91:
        return "⚔️ Tapasvi (Sense Conqueror)", "Sensual desires lose their grip over you."
    elif days < 181:
        return "👑 Siddha Purusha (Master of Self)", "Mind operates at peak spiritual clarity."
    elif days < 365:
        return "🔱 Paramhansa (Divine Yogi)", "Transcended mundane cravings completely."
    else:
        return "🕉️ Divya Atman (Enlightened Brahmachari)", "Legendary discipline. A living inspiration!"

def format_progress_bar(current_days: int, target_days: int = 30) -> str:
    """Creates a visual progress bar."""
    total_blocks = 10
    progress = min(1.0, current_days / max(1, target_days))
    filled_blocks = int(progress * total_blocks)
    empty_blocks = total_blocks - filled_blocks
    bar = "█" * filled_blocks + "░" * empty_blocks
    percentage = int(progress * 100)
    return f"[{bar}] {percentage}% ({current_days}/{target_days} Days)"

# ==================== TELEGRAM BOT CLIENT ====================
# Safe session lock cleanup: remove temporary journal and lock files before starting Pyrogram client
_script_dir = os.path.dirname(os.path.abspath(__file__))
for _fname in os.listdir(_script_dir):
    if _fname.endswith((".session-journal", ".session-wal", ".session-shm", ".db-journal", ".db-wal", ".db-shm")):
        try:
            os.remove(os.path.join(_script_dir, _fname))
        except Exception:
            pass

# Ensure session DB uses WAL mode and busy timeout
_session_db = os.path.join(_script_dir, "brahmacharya_bot.session")
if os.path.exists(_session_db):
    try:
        _sconn = sqlite3.connect(_session_db, timeout=30, isolation_level=None)
        _sconn.execute("PRAGMA journal_mode=WAL;")
        _sconn.execute("PRAGMA busy_timeout=30000;")
        _sconn.close()
    except Exception:
        pass

app = Client("brahmacharya_bot", api_id=API_ID, api_hash=API_HASH, bot_token=BOT_TOKEN)

# ==================== CHANNEL MEDIA & LOGGING ====================
def get_channel_peers():
    """Returns possible peer representations for database channel & group."""
    peers = set()
    for raw_id in [DB_CHANNEL_ID, DATABASE_CHANNEL_ID, DATABASE_GROUP_ID, -1004440598458, -5353068930]:
        raw = str(raw_id).strip()
        digits = raw.lstrip("-")
        for base in [raw, digits]:
            try:
                peers.add(int(base))
                peers.add(-int(base))
            except ValueError:
                pass
        if digits.startswith("100"):
            without_100 = digits[3:]
            try:
                peers.add(int(without_100))
                peers.add(-int(without_100))
            except ValueError:
                pass
        else:
            with_100 = "100" + digits
            try:
                peers.add(int(with_100))
                peers.add(-int(with_100))
            except ValueError:
                pass
    return list(peers)

async def log_to_database_channel(client: Client, text: str):
    """Safely logs alerts to the database channel."""
    if not DATABASE_CHANNEL_ID:
        return
    for ch_id in get_channel_peers():
        try:
            await client.send_message(
                chat_id=ch_id,
                text=text,
                disable_web_page_preview=True
            )
            return
        except Exception as e:
            logger.debug(f"Channel log attempt failed for {ch_id}: {e}")

# ==================== CATEGORY DEFINITIONS ====================
CATEGORY_COMMANDS = {
    "book": "books",
    "books": "books",
    "song": "songs",
    "songs": "songs",
    "health": "health",
    "workout": "workout",
    "workouts": "workout",
    "quote": "quotes",
    "quotes": "quotes",
    "mindset": "mindset"
}

def detect_category_from_caption(text: str) -> str:
    """Detects slash command or hashtag in text/caption and returns canonical category."""
    if not text:
        return ""
    text_lower = text.lower()
    for trigger, cat in CATEGORY_COMMANDS.items():
        if f"/{trigger}" in text_lower or f"#{trigger}" in text_lower:
            return cat
    return ""

async def send_category_media(client: Client, chat_id: int, category: str) -> int:
    """
    Delivers media for a specific category (books, songs, health, workout, etc.)
    using block-based auto indexing from DATABASE_CHANNEL_ID history,
    with fallback to file mime types (PDF -> Books, Audio -> Songs).
    """
    category = category.lower().strip()
    category = CATEGORY_COMMANDS.get(category, category)
    sent_count = 0
    seen_ids = set()

    # 1. Deliver already indexed media from SQLite database
    saved_items = db.get_saved_media(category, limit=50)
    for item in saved_items:
        mid = item.get("message_id")
        cid = item.get("channel_id") or DATABASE_CHANNEL_ID
        fid = item.get("file_id")
        ident = fid or f"{cid}_{mid}"
        if ident in seen_ids:
            continue
        try:
            if mid and cid:
                await client.copy_message(chat_id=chat_id, from_chat_id=cid, message_id=mid)
                sent_count += 1
                seen_ids.add(ident)
            elif fid:
                await client.send_document(chat_id=chat_id, document=fid, caption=item.get("caption") or "")
                sent_count += 1
                seen_ids.add(ident)
        except Exception as e:
            logger.debug(f"Error delivering indexed media item {item}: {e}")

    # 2. Block-Based Auto Indexing from DATABASE_CHANNEL_ID history
    for peer in get_channel_peers():
        try:
            raw_msgs = []
            async for m in client.get_chat_history(peer, limit=100):
                raw_msgs.append(m)

            # Sort chronologically (oldest to newest) to track blocks accurately
            chronological_msgs = sorted(raw_msgs, key=lambda m: m.id)

            active_block_category = None

            for msg in chronological_msgs:
                text_content = (msg.text or msg.caption or "").strip()

                # Check if this message starts or switches the active category block
                # (e.g. /songs, /books, /workout, /health, /quotes, /mindset)
                detected_cat = detect_category_from_caption(text_content)
                if detected_cat:
                    active_block_category = detected_cat

                file_obj = msg.document or msg.audio or msg.video or msg.photo or msg.voice
                if not file_obj:
                    continue

                fname = ""
                mime = ""
                if msg.document:
                    fname = (msg.document.file_name or "").lower()
                    mime = (msg.document.mime_type or "").lower()
                elif msg.audio:
                    fname = (msg.audio.file_name or msg.audio.title or "").lower()
                    mime = (msg.audio.mime_type or "").lower()

                # Determine effective category for this file:
                # - Any audio file posted after a /songs message (until another category command appears) is treated as a song.
                # - Any document/PDF posted after a /book or /books message (until another category command appears) is treated as a book.
                # - Also fallback to file mime types (PDF -> Books, Audio -> Songs) if no section break is explicitly set.
                media_cat = None

                # Check explicit caption on the file itself first
                explicit_cat = detect_category_from_caption(msg.caption or "")
                if explicit_cat:
                    media_cat = explicit_cat
                elif active_block_category:
                    # In an active block:
                    if active_block_category == "songs":
                        # Any audio file posted after a /songs message is treated as a song
                        if msg.audio or msg.voice or "audio" in mime or fname.endswith((".mp3", ".m4a", ".wav", ".aac", ".ogg", ".opus")):
                            media_cat = "songs"
                    elif active_block_category == "books":
                        # Any document/PDF posted after a /book or /books message is treated as a book
                        if msg.document and ("pdf" in mime or fname.endswith((".pdf", ".epub", ".mobi", ".djvu", ".txt", ".doc", ".docx")) or not (msg.audio or msg.voice)):
                            media_cat = "books"
                    else:
                        media_cat = active_block_category
                else:
                    # Fallback to file mime types (PDF -> Books, Audio -> Songs) if no section break is explicitly set
                    if msg.audio or msg.voice or "audio" in mime or fname.endswith((".mp3", ".m4a", ".wav", ".aac", ".ogg", ".opus")):
                        media_cat = "songs"
                    elif msg.document and ("pdf" in mime or fname.endswith((".pdf", ".epub", ".mobi", ".djvu"))):
                        media_cat = "books"

                # If this file matches the requested category, deliver directly to user and cache in DB
                if media_cat == category:
                    fid = getattr(file_obj, "file_id", "")
                    ident = fid or f"{peer}_{msg.id}"
                    if ident not in seen_ids:
                        try:
                            await msg.copy(chat_id=chat_id)
                            sent_count += 1
                            seen_ids.add(ident)

                            # Save to SQLite index
                            db.save_media(
                                message_id=msg.id,
                                channel_id=peer,
                                category=category,
                                file_id=fid,
                                file_name=fname,
                                caption=msg.caption or ""
                            )
                        except Exception as e:
                            logger.debug(f"Error copying channel message {msg.id}: {e}")

            if sent_count > 0:
                break
        except Exception as e:
            logger.debug(f"Could not read chat history from peer {peer}: {e}")

    return sent_count

async def scan_and_get_category_files(client: Client, category: str) -> list[dict]:
    """
    Scans DATABASE_CHANNEL_ID history for matching files
    (audios for songs, PDFs/documents for books), auto-indexes them into SQLite,
    and returns list of indexed items.
    """
    category = category.lower().strip()
    category = CATEGORY_COMMANDS.get(category, category)

    for peer in get_channel_peers():
        try:
            raw_msgs = []
            async for m in client.get_chat_history(peer, limit=100):
                raw_msgs.append(m)

            chronological_msgs = sorted(raw_msgs, key=lambda m: m.id)
            active_block_category = None

            for msg in chronological_msgs:
                text_content = (msg.text or msg.caption or "").strip()

                # Check if message switches indexing mode with /index
                if text_content.startswith("/index"):
                    parts = text_content.split()
                    if len(parts) > 1:
                        raw_mode = parts[1].lower().replace("#", "").strip()
                        if raw_mode in ["book", "books"]:
                            active_block_category = "books"
                        elif raw_mode in ["song", "songs"]:
                            active_block_category = "songs"
                        else:
                            active_block_category = CATEGORY_COMMANDS.get(raw_mode, raw_mode)

                detected_cat = detect_category_from_caption(text_content)
                if detected_cat:
                    active_block_category = detected_cat

                file_obj = msg.document or msg.audio or msg.video or msg.photo or msg.voice
                if not file_obj:
                    continue

                fname = ""
                mime = ""
                title = ""
                if msg.document:
                    fname = msg.document.file_name or ""
                    mime = (msg.document.mime_type or "").lower()
                    title = fname
                elif msg.audio:
                    fname = msg.audio.file_name or ""
                    mime = (msg.audio.mime_type or "").lower()
                    title = msg.audio.title or msg.audio.file_name or ""
                    if msg.audio.performer:
                        title = f"{msg.audio.performer} - {title}" if title else msg.audio.performer

                # Category classification
                media_cat = None
                explicit_cat = detect_category_from_caption(msg.caption or "")
                if explicit_cat:
                    media_cat = explicit_cat
                elif active_block_category:
                    if active_block_category == "songs":
                        if msg.audio or msg.voice or "audio" in mime or fname.lower().endswith((".mp3", ".m4a", ".wav", ".aac", ".ogg", ".opus")):
                            media_cat = "songs"
                    elif active_block_category == "books":
                        if msg.document and ("pdf" in mime or fname.lower().endswith((".pdf", ".epub", ".mobi", ".djvu", ".txt", ".doc", ".docx")) or not (msg.audio or msg.voice)):
                            media_cat = "books"
                    else:
                        media_cat = active_block_category
                else:
                    if msg.audio or msg.voice or "audio" in mime or fname.lower().endswith((".mp3", ".m4a", ".wav", ".aac", ".ogg", ".opus")):
                        media_cat = "songs"
                    elif msg.document and ("pdf" in mime or fname.lower().endswith((".pdf", ".epub", ".mobi", ".djvu"))):
                        media_cat = "books"

                if media_cat:
                    display_name = title or fname or (msg.caption or "").split("\n")[0].strip() or f"{media_cat.capitalize()} #{msg.id}"
                    fid = getattr(file_obj, "file_id", "")
                    db.save_media(
                        message_id=msg.id,
                        channel_id=peer,
                        category=media_cat,
                        file_id=fid,
                        file_name=display_name,
                        caption=msg.caption or ""
                    )
        except Exception as e:
            logger.debug(f"Scan peer {peer} error: {e}")

    return db.get_saved_media(category, limit=50)

def build_category_menu_keyboard(files: list[dict], category: str) -> InlineKeyboardMarkup:
    """Generates an interactive inline button keyboard for each file found in category."""
    keyboard_rows = []
    icon = "🎵" if category == "songs" else "📖"

    for f in files:
        fid_db = f["id"]
        raw_name = f.get("file_name") or f.get("caption") or f"Item #{fid_db}"
        clean = raw_name.split("\n")[0].strip()
        for ext in [".pdf", ".epub", ".mobi", ".djvu", ".mp3", ".m4a", ".wav", ".aac", ".ogg", ".opus"]:
            if clean.lower().endswith(ext):
                clean = clean[:-len(ext)]
                break
        clean = clean.replace("_", " ").strip()
        if not clean:
            clean = f"Item #{fid_db}"
        if len(clean) > 36:
            clean = clean[:33] + "..."
        btn_text = f"{icon} {clean}"
        keyboard_rows.append([
            InlineKeyboardButton(text=btn_text, callback_data=f"cb_dl_{fid_db}")
        ])

    keyboard_rows.append([
        InlineKeyboardButton("🔙 Back to Sanctum", callback_data="cb_home")
    ])
    return InlineKeyboardMarkup(keyboard_rows)

# ==================== INLINE KEYBOARDS ====================
def main_menu_keyboard(lang: str = "en") -> InlineKeyboardMarkup:
    """Returns the main interactive control panel buttons."""
    return InlineKeyboardMarkup([
        [
            InlineKeyboardButton("📊 My Streak", callback_data="cb_streak"),
            InlineKeyboardButton("🏆 Leaderboard", callback_data="cb_leaderboard")
        ],
        [
            InlineKeyboardButton("🔄 Log Relapse", callback_data="cb_relapse_prompt"),
            InlineKeyboardButton("🎯 Challenge Target", callback_data="cb_challenge_menu")
        ],
        [
            InlineKeyboardButton("🧘 Mindset & Ojas", callback_data="cb_mindset"),
            InlineKeyboardButton("📜 Daily Shlokas", callback_data="cb_quotes")
        ],
        [
            InlineKeyboardButton("⚔️ Workout & Vyayam", callback_data="cb_workout"),
            InlineKeyboardButton("🥗 Sattvic Health", callback_data="cb_health")
        ],
        [
            InlineKeyboardButton("📚 Sacred Books", callback_data="cb_books"),
            InlineKeyboardButton("🎵 Sacred Songs", callback_data="cb_songs")
        ],
        [
            InlineKeyboardButton("🌐 Language / भाषा", callback_data="cb_language_menu")
        ]
    ])

def language_selection_keyboard() -> InlineKeyboardMarkup:
    """Returns language selection keyboard."""
    buttons = []
    row = []
    for code, info in SUPPORTED_LANGUAGES.items():
        row.append(InlineKeyboardButton(f"{info['flag']} {info['name']}", callback_data=f"setlang_{code}"))
        if len(row) == 2:
            buttons.append(row)
            row = []
    if row:
        buttons.append(row)
    buttons.append([InlineKeyboardButton("🔙 Back to Sanctum", callback_data="cb_home")])
    return InlineKeyboardMarkup(buttons)

def back_home_keyboard() -> InlineKeyboardMarkup:
    return InlineKeyboardMarkup([
        [InlineKeyboardButton("📊 View My Streak", callback_data="cb_streak")],
        [InlineKeyboardButton("🔙 Back to Main Menu", callback_data="cb_home")]
    ])

def relapse_confirmation_keyboard() -> InlineKeyboardMarkup:
    return InlineKeyboardMarkup([
        [
            InlineKeyboardButton("⚠️ Yes, I Relapsed (Reset)", callback_data="cb_relapse_confirm"),
            InlineKeyboardButton("🛡️ No, I Stayed Strong!", callback_data="cb_home")
        ]
    ])

def challenge_keyboard() -> InlineKeyboardMarkup:
    return InlineKeyboardMarkup([
        [
            InlineKeyboardButton("🌱 7 Days (Shankha)", callback_data="setpledge_7"),
            InlineKeyboardButton("🌿 21 Days (Sankalp)", callback_data="setpledge_21")
        ],
        [
            InlineKeyboardButton("🔥 30 Days (Agni)", callback_data="setpledge_30"),
            InlineKeyboardButton("🛡️ 90 Days (Mahavrata)", callback_data="setpledge_90")
        ],
        [
            InlineKeyboardButton("👑 365 Days (Divya Vrata)", callback_data="setpledge_365")
        ],
        [
            InlineKeyboardButton("🔙 Back", callback_data="cb_home")
        ]
    ])

# ==================== TOPIC CONTENT GENERATORS ====================
def get_streak_message(user_dict: dict) -> str:
    user_id = user_dict["user_id"]
    name = user_dict.get("first_name") or "Brahmachari"
    start_dt = datetime.fromisoformat(user_dict["streak_start"])
    now = datetime.now(timezone.utc)
    diff = now - start_dt
    
    days = max(0, diff.days)
    hours = int((diff.total_seconds() % 86400) // 3600)
    minutes = int((diff.total_seconds() % 3600) // 60)
    
    pledge = user_dict.get("pledge_days", 30)
    rank, rank_desc = get_rank_and_badge(days)
    longest = max(user_dict.get("longest_streak_days", 0), days)
    relapses = user_dict.get("relapses_count", 0)
    progress_bar = format_progress_bar(days, pledge)

    msg = (
        f"⚡ **BRAHMACHARYA STREAK TRACKER** ⚡\n"
        f"━━━━━━━━━━━━━━━━━━━━━━\n"
        f"👤 **Brahmachari**: {name}\n"
        f"⏳ **Live Streak**: **{days} Days, {hours}h {minutes}m**\n"
        f"🎖️ **Rank**: {rank}\n"
        f"📝 **Status**: _{rank_desc}_\n\n"
        f"🎯 **Pledge Goal**: {pledge} Days\n"
        f"📈 **Progress**: `{progress_bar}`\n\n"
        f"🏆 **Personal Record**: {longest} Days\n"
        f"⚠️ **Total Relapses**: {relapses}\n"
        f"📅 **Started On**: `{start_dt.strftime('%d %b %Y, %I:%M %p UTC')}`\n"
        f"━━━━━━━━━━━━━━━━━━━━━━\n"
        f"💡 *\"The vital fluid (Veerya) when preserved rises up to the brain as Ojas Shakti, providing radiant intelligence and fearlessness.\"* — Swami Sivananda"
    )
    return msg

def get_mindset_message() -> str:
    return (
        "🧘 **BRAHMACHARYA MINDSET & OJAS TRANSMUTATION** 🧘\n"
        "━━━━━━━━━━━━━━━━━━━━━━\n"
        "Sexual energy is the most concentrated creative force in the universe. Do not suppress it; **TRANSMUTE** it into intellectual brilliance, physical strength, and spiritual magnetism.\n\n"
        "🔱 **The 3 Pillars of Mind Control**:\n"
        "1. **Pranayama (Breath Control)**:\n"
        "   • *Anulom Vilom (Alternate Nostril)*: 15 mins daily calms the central nervous system.\n"
        "   • *Kapalabhati & Bhastrika*: Generates internal fire and clears lethargy.\n"
        "   • *Moola Bandha & Uddiyana Bandha*: Directs the seminal energy upwards toward Sahasrara.\n\n"
        "2. **The 10-Minute Urge Rule**:\n"
        "   • When a strong craving hits, do NOT fight it mentally.\n"
        "   • Immediately drop down and do 25 pushups, or wash your face with ice-cold water.\n"
        "   • Observe the craving like an ocean wave—it peaks in 10 minutes and dissolves.\n\n"
        "3. **Drishti Shuddhi (Sight Purification)**:\n"
        "   • What enters the eyes becomes the thought, and what becomes thought triggers the action.\n"
        "   • Practice *Trataka* (gazing at a ghee lamp flame for 5 mins) to build razor-sharp focus.\n"
        "━━━━━━━━━━━━━━━━━━━━━━"
    )

def get_workout_message() -> str:
    return (
        "⚔️ **BRAHMACHARI PHYSICAL STRENGTH & VYAYAM GUIDE** ⚔️\n"
        "━━━━━━━━━━━━━━━━━━━━━━\n"
        "A weak body cannot sustain powerful Ojas. Build iron endurance with traditional Bharatiya Vyayam:\n\n"
        "☀️ **Morning Sadhana (4:30 AM - 6:00 AM)**:\n"
        "1. **Surya Namaskar (12-24 Rounds)**:\n"
        "   • Complete spinal flexibility, stimulates endocrine glands and activates solar plexus.\n\n"
        "2. **Desi Dands (Hindu Push-Ups) — 50-100 Reps**:\n"
        "   • Builds upper body armor, core fortitude, and shoulder strength.\n\n"
        "3. **Desi Baithaks (Hindu Squats) — 100-200 Reps**:\n"
        "   • Strengthens legs, pelvic floor, and increases testosterone naturally.\n\n"
        "4. **Inversions (Shirshasana & Sarvangasana) — 5-10 Mins**:\n"
        "   • Reverses gravity, nourishes brain capillaries, and pulls energy upwards.\n\n"
        "💪 *\"You will be nearer to Heaven through football than through the study of the Gita.\"* — Swami Vivekananda"
    )

def get_health_message() -> str:
    return (
        "🥗 **SATTVIC HEALTH & AYURVEDIC DIET PROTOCOL** 🥗\n"
        "━━━━━━━━━━━━━━━━━━━━━━\n"
        "Food directly transforms into mind stuff (*Ahara Shuddhau Sattva Shuddhih*).\n\n"
        "✅ **What to Consume (Sattvic & Ojas-Building)**:\n"
        "• Soaked Almonds, Walnuts, and Munakka (Dry Grapes)\n"
        "• Pure A2 Cow Milk with Ashwagandha & Cardamom\n"
        "• Fresh seasonal fruits (Apples, Pomegranates, Bananas)\n"
        "• Ghee, Green vegetables, Moong Dal, Sprouts\n"
        "• Ample hydration (Copper vessel water)\n\n"
        "🚫 **What to Strictly Eliminate (Tamasic & Rajasic)**:\n"
        "• Excess chilies, garlic, deep-fried junk food\n"
        "• Artificial sugars, energy drinks, and alcohol/smoking\n"
        "• Late-night eating (dinner must be 3 hours before sleep)\n\n"
        "❄️ **Cold Shower Therapy (Snana)**:\n"
        "• Cold water bath immediately cools the genital nervous center and resets dopamine receptors."
    )

def get_quotes_message() -> str:
    return (
        "📜 **SACRED SHLOKAS & MOTIVATIONAL WISDOM** 📜\n"
        "━━━━━━━━━━━━━━━━━━━━━━\n"
        "📖 **Bhagavad Gita (Chapter 2, Verse 62-63)**:\n"
        "ध्यायतो विषयान्पुंसः सङ्गस्तेषूपजायते।\n"
        "सङ्गात्संजायते कामः कामात्क्रोधोऽभिजायते॥\n"
        "_\"Contemplating the objects of the senses leads to attachment; from attachment arises lust, and from unfulfilled lust arises anger.\"_\n\n"
        "📖 **Swami Vivekananda**:\n"
        "_\"Every boy should be trained to practice complete Brahmacharya; only then can there be built up in him the tremendous power of head and heart.\"_\n\n"
        "📖 **Patanjali Yoga Sutras (2.38)**:\n"
        "ब्रह्मचर्यप्रतिष्ठायां वीर्यलाभः॥\n"
        "_\"Upon establishment in Brahmacharya, unyielding vitality and divine potency are acquired.\"_\n\n"
        "📖 **Chanakya Neeti**:\n"
        "_\"He who controls his senses rules over the entire kingdom of destiny.\"_\n"
        "━━━━━━━━━━━━━━━━━━━━━━"
    )

def get_books_message() -> str:
    return (
        "📚 **SACRED BRAHMACHARYA LITERATURE** 📚\n"
        "━━━━━━━━━━━━━━━━━━━━━━\n"
        "Deepen your understanding with these essential classic scriptures:\n\n"
        "1. 📖 **The Practice of Brahmacharya** — *Swami Sivananda*\n"
        "   The ultimate encyclopedia on celibacy, science of sex sublimation, and mind control.\n\n"
        "2. 📖 **Raja Yoga** — *Swami Vivekananda*\n"
        "   Master the mechanics of thought control, concentration, and Kundalini awakening.\n\n"
        "3. 📖 **Brahmacharya (Self-Restraint)** — *Mahatma Gandhi*\n"
        "   Practical experiments in truth, dietetics, and conquering sensory habits.\n\n"
        "4. 📖 **Autobiography of a Yogi** — *Paramahansa Yogananda*\n"
        "   Life transforming spiritual classic on Kriya Yoga and cosmic consciousness.\n\n"
        "5. 📖 **Bhagavad Gita As It Is** — *Lord Sri Krishna's timeless wisdom*."
    )

def get_songs_message() -> str:
    return (
        "🎵 **SACRED CHANTS, BHAJANS & VEDIC AUDIO** 🎵\n"
        "━━━━━━━━━━━━━━━━━━━━━━\n"
        "Sound vibrations (*Shabda Brahman*) immediately elevate your frequency and calm restless neural impulses.\n\n"
        "🔱 **Recommended Tracks for Ojas & Mental Purity**:\n"
        "• **Shiva Tandava Stotram** — Awakens warrior energy and supreme focus.\n"
        "• **Hanuman Chalisa** — Destroys sensual cravings and invokes unbreakable fortitude.\n"
        "• **Mahamrityunjaya Mantra** — Cellular healing and nervous system tranquility.\n"
        "• **Gayatri Mantra (108 Japa)** — Illuminates intellect and strengthens discriminative willpower.\n"
        "• **Flute / Om 432Hz Meditation** — Facilitates restful sleep and eliminates late-night insomnia.\n"
        "━━━━━━━━━━━━━━━━━━━━━━"
    )

# ==================== BOT HANDLERS ====================

@app.on_message(filters.command("start"))
async def start_command(client: Client, message: Message):
    user = message.from_user
    if not user:
        return

    is_new = db.add_or_update_user(
        user_id=user.id,
        first_name=user.first_name,
        last_name=user.last_name,
        username=user.username
    )

    user_data = db.get_user(user.id)
    lang = user_data.get("language", "en") if user_data else "en"

    # Send Log Alert to Database Channel if new user
    if is_new:
        log_text = (
            f"🚀 **New Brahmachari Registered!**\n"
            f"━━━━━━━━━━━━━━━━━━━━━━\n"
            f"👤 **Name**: {user.first_name} {user.last_name or ''}\n"
            f"🆔 **User ID**: `{user.id}`\n"
            f"🔗 **Username**: @{user.username if user.username else 'None'}\n"
            f"📅 **Date**: `{datetime.now(timezone.utc).strftime('%Y-%m-%d %H:%M:%S UTC')}`"
        )
        await log_to_database_channel(client, log_text)

    # Greeting Message
    greeting_text = (
        f"Ram Ram Brahmachari {user.first_name} 🙏\n\n"
        f"Welcome to the sacred **Brahmacharya & NoFap Sanctum**.\n"
        f"Here you master sensory control, cultivate **Ojas Shakti**, and build an indomitable character.\n\n"
        f"⚡ **Your Live Journey Status**:\n"
        f"{get_streak_message(user_data)}\n\n"
        f"👇 Select an option below to guide your sadhana:"
    )

    if lang != "en":
        greeting_text = translate_text(greeting_text, lang)

    await message.reply_text(
        text=greeting_text,
        reply_markup=main_menu_keyboard(lang),
        disable_web_page_preview=True
    )

@app.on_message(filters.command("streak"))
async def streak_command(client: Client, message: Message):
    user = message.from_user
    if not user:
        return
    db.add_or_update_user(user.id, user.first_name, user.last_name, user.username)
    user_data = db.get_user(user.id)
    lang = user_data.get("language", "en")

    msg = get_streak_message(user_data)
    if lang != "en":
        msg = translate_text(msg, lang)

    await message.reply_text(
        text=msg,
        reply_markup=InlineKeyboardMarkup([
            [InlineKeyboardButton("🔄 Refresh Streak", callback_data="cb_streak")],
            [InlineKeyboardButton("🏆 Leaderboard", callback_data="cb_leaderboard")],
            [InlineKeyboardButton("🔙 Main Menu", callback_data="cb_home")]
        ]),
        disable_web_page_preview=True
    )

@app.on_message(filters.command("leaderboard"))
async def leaderboard_command(client: Client, message: Message):
    top_list = db.get_top_leaderboard(10)
    if not top_list:
        await message.reply_text("🏆 No streaks recorded yet. Be the first!")
        return

    text = "🏆 **BRAHMACHARYA LEADERBOARD (TOP SADHAKS)** 🏆\n━━━━━━━━━━━━━━━━━━━━━━\n"
    medals = ["🥇", "🥈", "🥉", "🎖️", "🎖️", "🎖️", "🎖️", "🎖️", "🎖️", "🎖️"]

    for idx, member in enumerate(top_list):
        medal = medals[idx] if idx < len(medals) else "🎖️"
        uname = f"@{member['username']}" if member['username'] else member['name']
        rank_badge, _ = get_rank_and_badge(member['days'])
        badge_icon = rank_badge.split()[0]
        text += f"{medal} **{idx+1}. {uname}** — **{member['days']} Days** ({badge_icon})\n"

    text += "\n━━━━━━━━━━━━━━━━━━━━━━\n💡 *\"Purity is strength. Keep moving forward!\"*"

    await message.reply_text(
        text=text,
        reply_markup=back_home_keyboard(),
        disable_web_page_preview=True
    )

@app.on_message(filters.command("relapse"))
async def relapse_command(client: Client, message: Message):
    user = message.from_user
    if not user:
        return
    prompt_text = (
        "⚠️ **RELAPSE CONFIRMATION** ⚠️\n\n"
        "Brother, are you sure you want to log a relapse and reset your streak?\n\n"
        "Remember: A setback is only permanent if you give up. Honesty is the foundation of true character."
    )
    await message.reply_text(
        text=prompt_text,
        reply_markup=relapse_confirmation_keyboard()
    )

@app.on_message(filters.command("language"))
async def language_command(client: Client, message: Message):
    await message.reply_text(
        text="🌐 **Choose Your Preferred Language / अपनी भाषा चुनें**:\n\nSelect your language for all bot responses and guides:",
        reply_markup=language_selection_keyboard()
    )

# ==================== INDEXING HELPERS ====================

async def try_index_replied_media(client: Client, message: Message, category: str) -> bool:
    """Indexes replied media under category if called by owner or in database channel."""
    if not message.reply_to_message:
        return False
    is_owner = (message.from_user and message.from_user.id == OWNER_ID)
    is_chan = (message.chat and message.chat.id in get_channel_peers()) or (message.sender_chat and message.sender_chat.id in get_channel_peers())
    if not (is_owner or is_chan):
        return False

    replied = message.reply_to_message
    file_obj = replied.document or replied.audio or replied.video or replied.photo or replied.voice
    if not file_obj:
        return False

    cat_detected, f_id, f_name, f_size, f_caption, f_mime, f_type = extract_file_details(replied)
    cat = CATEGORY_COMMANDS.get(category.lower(), category.lower()) if category else (cat_detected or "book")
    file_id = f_id or getattr(file_obj, "file_id", "")
    file_name = f_name or getattr(file_obj, "file_name", "") or getattr(file_obj, "title", "") or ""
    caption = f_caption or replied.caption or ""

    db.save_file(
        message_id=replied.id,
        channel_id=replied.chat.id,
        category=cat,
        file_id=file_id,
        file_name=file_name,
        file_size=f_size,
        file_type=f_type,
        caption=caption,
        mime_type=f_mime
    )
    await message.reply_text(
        f"✅ **Media Indexed Under #{cat}!**\n"
        f"📄 `{file_name or 'Media File'}`\n"
        f"🆔 Message ID: `{replied.id}`\n\n"
        f"Users can now access this file via `/{cat}`! 🚀"
    )
    return True

def extract_file_details(msg: Message) -> tuple[str, str, str, int, str, str, str]:
    """
    Extracts file details for ALL media types from a message:
    * Documents / PDFs -> category = 'book'
    * Audio / Voice -> category = 'song'
    * Photos / Images -> category = 'quote'
    * Text / Links -> category = 'text'
    Returns: (category, file_id, file_name, file_size, caption, mime_type, file_type)
    """
    if not msg:
        return "", "", "", 0, "", "", ""

    caption = msg.caption or ""

    # 1. Audio message
    if msg.audio:
        f_id = getattr(msg.audio, "file_id", "") or ""
        f_size = getattr(msg.audio, "file_size", 0) or 0
        f_name = getattr(msg.audio, "file_name", "") or getattr(msg.audio, "title", "") or f"song_{msg.id}.mp3"
        mime = getattr(msg.audio, "mime_type", "") or "audio/mpeg"
        return "song", f_id, f_name, f_size, caption, mime, "audio"

    # 2. Voice message
    if msg.voice:
        f_id = getattr(msg.voice, "file_id", "") or ""
        f_size = getattr(msg.voice, "file_size", 0) or 0
        f_name = f"voice_{msg.id}.ogg"
        mime = getattr(msg.voice, "mime_type", "") or "audio/ogg"
        return "song", f_id, f_name, f_size, caption, mime, "voice"

    # 3. Photo message
    if msg.photo:
        f_id = getattr(msg.photo, "file_id", "") or ""
        f_size = getattr(msg.photo, "file_size", 0) or 0
        f_name = f"quote_{msg.id}.jpg"
        mime = "image/jpeg"
        return "quote", f_id, f_name, f_size, caption, mime, "photo"

    # 4. Document message
    if msg.document:
        doc = msg.document
        f_id = getattr(doc, "file_id", "") or ""
        f_size = getattr(doc, "file_size", 0) or 0
        f_name = getattr(doc, "file_name", "") or f"doc_{msg.id}"
        mime = (getattr(doc, "mime_type", "") or "").lower()
        f_lower = f_name.lower()

        is_audio = ("audio" in mime) or f_lower.endswith((".mp3", ".wav", ".m4a", ".aac", ".ogg", ".opus", ".flac", ".wma"))
        is_image = ("image" in mime) or f_lower.endswith((".jpg", ".jpeg", ".png", ".webp", ".bmp", ".gif"))

        if is_audio:
            return "song", f_id, f_name, f_size, caption, mime or "audio/mpeg", "audio"
        elif is_image:
            return "quote", f_id, f_name, f_size, caption, mime or "image/jpeg", "photo"
        else:
            return "book", f_id, f_name, f_size, caption, mime or "application/pdf", "document"

    # 5. Text / Links message
    if msg.text:
        text_str = msg.text.strip()
        if not text_str.startswith("/"):
            f_id = f"text_{msg.id}"
            first_line = text_str.split("\n")[0][:60].strip()
            f_name = first_line or f"Text_{msg.id}"
            f_size = len(text_str.encode("utf-8"))
            return "text", f_id, f_name, f_size, text_str, "text/plain", "text"

    return "", "", "", 0, "", "", ""

classify_message_media = extract_file_details

def is_owner_or_channel_admin(message: Message) -> bool:
    """Checks if message is sent by OWNER_ID (5650859707) or as channel admin."""
    if message.from_user and message.from_user.id == OWNER_ID:
        return True
    if message.sender_chat and message.sender_chat.id in get_channel_peers():
        return True
    if message.chat and message.chat.id in get_channel_peers() and message.from_user is None:
        return True
    return False

async def index_chat_media(client: Client, message: Message, category_arg: str = None):
    """
    Completely rewritten index command handler for DB_CHANNEL_ID (-1004440598458):
    - When /index (or /index books, /index songs, /index quotes) is sent by OWNER_ID (5650859707) in DB_CHANNEL_ID (-1004440598458):
      - Iterates over ALL past chat messages using async loop without pagination limit.
      - Extracts file details for ALL media types:
        * Documents / PDFs -> category = 'book'
        * Audio / Voice -> category = 'song'
        * Photos / Images -> category = 'quote'
        * Text / Links -> category = 'text'
      - Inserts or REPLACES into SQLite database table 'files' (file_id, file_name, file_size, category, caption, mime_type).
    - Immediate Progress & Feedback:
      - Sends progress update message while scanning.
      - Replies with final breakdown:
        ✅ Indexing Complete!
        📚 Books/PDFs: X
        🎵 Songs/Audio: Y
        🖼️ Quotes/Images: Z
    """
    target_chat = DB_CHANNEL_ID
    if message.chat and message.chat.id in get_channel_peers():
        target_chat = message.chat.id

    progress_msg = None
    try:
        progress_msg = await message.reply_text("⏳ Scanning channel history and indexing files...")
    except Exception as e:
        logger.debug(f"Could not reply progress message: {e}")
        try:
            progress_msg = await client.send_message(chat_id=target_chat, text="⏳ Scanning channel history and indexing files...")
        except Exception:
            pass

    total_scanned = 0
    books_count = 0
    songs_count = 0
    quotes_count = 0
    texts_count = 0
    last_update_time = time.time()

    async def scan_history_stream(stream):
        nonlocal total_scanned, books_count, songs_count, quotes_count, texts_count, last_update_time
        async for msg in stream:
            if not msg or msg.id == message.id:
                continue

            text_body = (msg.text or msg.caption or "").strip()
            if text_body.startswith("/index"):
                continue

            cat, fid, fname, fsize, fcaption, fmime, ftype = extract_file_details(msg)
            if not cat:
                continue

            total_scanned += 1
            display_name = (fcaption.split("\n")[0].strip() if fcaption else "") or fname or f"{cat.capitalize()}_{msg.id}"

            # Insert or REPLACE into SQLite database table 'files' (file_id, file_name, file_size, category, caption, mime_type)
            db.save_file(
                message_id=msg.id,
                channel_id=target_chat,
                category=cat,
                file_id=fid,
                file_name=display_name,
                file_size=fsize,
                file_type=ftype,
                caption=fcaption,
                mime_type=fmime
            )

            if cat == "book":
                books_count += 1
            elif cat == "song":
                songs_count += 1
            elif cat == "quote":
                quotes_count += 1
            elif cat == "text":
                texts_count += 1

            now = time.time()
            if progress_msg and (now - last_update_time >= 3.0):
                last_update_time = now
                try:
                    await progress_msg.edit_text(
                        f"⏳ Indexing in progress...\n"
                        f"📊 Scanned: {total_scanned} messages\n"
                        f"📚 Books: {books_count} | 🎵 Songs: {songs_count} | 🖼️ Quotes: {quotes_count}"
                    )
                except Exception:
                    pass

    # Async loop over ALL past chat messages without pagination limit
    try:
        await scan_history_stream(client.get_chat_history(chat_id=target_chat))
    except Exception as e:
        logger.warning(f"Error scanning {target_chat} with client.get_chat_history: {e}")
        try:
            await scan_history_stream(app.get_chat_history(chat_id=target_chat))
        except Exception as e2:
            logger.error(f"Error scanning with app.get_chat_history: {e2}")

    # Fallback to alternate peers if no messages were found
    if total_scanned == 0:
        for alt_peer in get_channel_peers():
            if alt_peer == target_chat:
                continue
            try:
                await scan_history_stream(client.get_chat_history(chat_id=alt_peer))
                if total_scanned > 0:
                    break
            except Exception:
                pass

    # Fallback to reply range if history scan was blocked and a message was replied to
    if total_scanned == 0 and message.reply_to_message:
        batch_chat = message.chat.id if message.chat else target_chat
        start_id = min(message.reply_to_message.id, message.id)
        end_id = max(message.reply_to_message.id, message.id)
        msg_ids = list(range(start_id, end_id + 1))
        for i in range(0, len(msg_ids), 200):
            chunk = msg_ids[i:i + 200]
            try:
                fetched = await client.get_messages(batch_chat, chunk)
                msg_list = fetched if isinstance(fetched, list) else ([fetched] if fetched else [])
                for m in msg_list:
                    if not m or m.id == message.id:
                        continue
                    cat, fid, fname, fsize, fcaption, fmime, ftype = extract_file_details(m)
                    if not cat:
                        continue
                    total_scanned += 1
                    display_name = (fcaption.split("\n")[0].strip() if fcaption else "") or fname or f"{cat.capitalize()}_{m.id}"
                    db.save_file(
                        message_id=m.id,
                        channel_id=target_chat,
                        category=cat,
                        file_id=fid,
                        file_name=display_name,
                        file_size=fsize,
                        file_type=ftype,
                        caption=fcaption,
                        mime_type=fmime
                    )
                    if cat == "book":
                        books_count += 1
                    elif cat == "song":
                        songs_count += 1
                    elif cat == "quote":
                        quotes_count += 1
                    elif cat == "text":
                        texts_count += 1
            except Exception as e:
                logger.debug(f"Error fetching chunk: {e}")

    # If history iteration is restricted for bots, report current database counts
    if total_scanned == 0:
        db_books = len(db.get_category_media("book"))
        db_songs = len(db.get_category_media("song"))
        db_quotes = len(db.get_category_media("quote"))
        if db_books > 0 or db_songs > 0 or db_quotes > 0:
            books_count = db_books
            songs_count = db_songs
            quotes_count = db_quotes

    final_breakdown = (
        "✅ Indexing Complete!\n"
        f"📚 Books/PDFs: {books_count}\n"
        f"🎵 Songs/Audio: {songs_count}\n"
        f"🖼️ Quotes/Images: {quotes_count}"
    )

    edited = False
    if progress_msg:
        try:
            await progress_msg.edit_text(final_breakdown)
            edited = True
        except Exception as e:
            logger.debug(f"Could not edit progress message: {e}")

    if not edited:
        try:
            await message.reply_text(final_breakdown)
        except Exception as e:
            logger.warning(f"Could not reply final breakdown: {e}")
            try:
                await client.send_message(chat_id=target_chat, text=final_breakdown)
            except Exception:
                pass

def is_db_channel_message(_, __, message: Message) -> bool:
    if not message:
        return False
    peers = get_channel_peers()
    chat_id = getattr(message.chat, "id", None)
    if chat_id and chat_id in peers:
        return True
    sender_chat_id = getattr(message.sender_chat, "id", None)
    if sender_chat_id and sender_chat_id in peers:
        return True
    return False

db_channel_filter = filters.chat(get_channel_peers()) | filters.create(is_db_channel_message)

@app.on_message(db_channel_filter)
async def channel_post_auto_indexer(client: Client, message: Message):
    """
    Listens to messages in DB_CHANNEL_ID (-1004440598458).
    1. Active History Scanning: /index (or /index books, /index songs, /index quotes)
    2. On-Message Real-Time Indexer:
       Automatically index any new PDF, song, or photo posted/forwarded into DB_CHANNEL_ID (-1004440598458) into categories ('book', 'song', 'quote').
    """
    if getattr(message, "outgoing", False) or (message.from_user and message.from_user.is_self):
        return

    text_content = (message.text or message.caption or "").strip()

    # 1. /index command
    if text_content.startswith("/index"):
        if is_owner_or_channel_admin(message):
            parts = text_content.split()
            cat_arg = parts[1] if len(parts) > 1 else None
            await index_chat_media(client, message, cat_arg)
            return

    # 2. Reply command
    if message.reply_to_message and message.command:
        cmd = message.command[0].lower()
        if cmd in CATEGORY_COMMANDS:
            if await try_index_replied_media(client, message, cmd):
                return

    # 3. Real-Time Indexer: Automatically index any new PDF, song, or photo posted/forwarded into DB_CHANNEL_ID (-1004440598458) into categories ('book', 'song', 'quote')
    cat, fid, fname, fsize, fcaption, fmime, ftype = extract_file_details(message)
    if cat in ["book", "song", "quote"] and fid:
        target_chat = message.chat.id if message.chat else DB_CHANNEL_ID
        display_name = (fcaption.split("\n")[0].strip() if fcaption else "") or fname or f"{cat.capitalize()}_{message.id}"
        db.save_file(
            message_id=message.id,
            channel_id=target_chat,
            category=cat,
            file_id=fid,
            file_name=display_name,
            file_size=fsize,
            file_type=ftype,
            caption=fcaption,
            mime_type=fmime
        )
        logger.info(f"✅ Real-time indexed new/forwarded {ftype} {message.id} ('{display_name}', size={fsize}) into category '{cat}' for {target_chat}")
        try:
            await message.react("👍")
        except Exception:
            pass

@app.on_message(filters.command("index"))
async def admin_index_command(client: Client, message: Message):
    """Allows OWNER_ID to trigger indexing."""
    if message.chat and message.chat.id in get_channel_peers():
        return

    if not is_owner_or_channel_admin(message):
        return

    parts = message.command
    cat_arg = parts[1] if len(parts) > 1 else None
    await index_chat_media(client, message, cat_arg)

@app.on_message(filters.command(["workout", "workouts"]))
async def workout_command(client: Client, message: Message):
    if await try_index_replied_media(client, message, "workout"):
        return
    user_data = db.get_user(message.from_user.id)
    lang = user_data.get("language", "en") if user_data else "en"
    msg = get_workout_message()
    if lang != "en":
        msg = translate_text(msg, lang)
    await message.reply_text(msg, reply_markup=back_home_keyboard())
    files_sent = await send_category_media(client, message.chat.id, "workout")
    if files_sent > 0:
        await message.reply_text(f"⚔️ Delivered **{files_sent}** workout media file(s) from our archive above! 👆")

@app.on_message(filters.command("health"))
async def health_command(client: Client, message: Message):
    if await try_index_replied_media(client, message, "health"):
        return
    user_data = db.get_user(message.from_user.id)
    lang = user_data.get("language", "en") if user_data else "en"
    msg = get_health_message()
    if lang != "en":
        msg = translate_text(msg, lang)
    await message.reply_text(msg, reply_markup=back_home_keyboard())
    files_sent = await send_category_media(client, message.chat.id, "health")
    if files_sent > 0:
        await message.reply_text(f"🥗 Delivered **{files_sent}** diet & health media file(s) from our archive above! 👆")

@app.on_message(filters.command("mindset"))
async def mindset_command(client: Client, message: Message):
    if await try_index_replied_media(client, message, "mindset"):
        return
    user_data = db.get_user(message.from_user.id)
    lang = user_data.get("language", "en") if user_data else "en"
    msg = get_mindset_message()
    if lang != "en":
        msg = translate_text(msg, lang)
    await message.reply_text(msg, reply_markup=back_home_keyboard())

@app.on_message(filters.command(["quotes", "quote"]))
async def quotes_command(client: Client, message: Message):
    if await try_index_replied_media(client, message, "quotes"):
        return
    user_data = db.get_user(message.from_user.id)
    lang = user_data.get("language", "en") if user_data else "en"
    msg = get_quotes_message()
    if lang != "en":
        msg = translate_text(msg, lang)
    await message.reply_text(msg, reply_markup=back_home_keyboard())

@app.on_message(filters.command(["books", "book"]))
async def books_command(client: Client, message: Message):
    if await try_index_replied_media(client, message, "books"):
        return
    user_data = db.get_user(message.from_user.id)
    lang = user_data.get("language", "en") if user_data else "en"

    # Query the database directly for indexed books
    files = db.get_category_media("books")
    if not files:
        files = await scan_and_get_category_files(client, "books")

    if files:
        text = (
            "📚 **SACRED BRAHMACHARYA BOOKS** 📚\n"
            "━━━━━━━━━━━━━━━━━━━━━━\n"
            "The following spiritual texts and guides are available.\n\n"
            "👇 **Tap any book below to receive it directly:**"
        )
        if lang != "en":
            text = translate_text(text, lang)
        await message.reply_text(text, reply_markup=build_category_menu_keyboard(files, "books"))
    else:
        msg = get_books_message()
        if lang != "en":
            msg = translate_text(msg, lang)
        await message.reply_text(msg, reply_markup=back_home_keyboard())

@app.on_message(filters.command(["songs", "song"]))
async def songs_command(client: Client, message: Message):
    if await try_index_replied_media(client, message, "songs"):
        return
    user_data = db.get_user(message.from_user.id)
    lang = user_data.get("language", "en") if user_data else "en"

    # Query the database directly for indexed songs
    files = db.get_category_media("songs")
    if not files:
        files = await scan_and_get_category_files(client, "songs")

    if files:
        text = (
            "🎵 **SACRED AUDIO & CHANTS** 🎵\n"
            "━━━━━━━━━━━━━━━━━━━━━━\n"
            "The following high-vibration chants and tracks are available.\n\n"
            "👇 **Tap any track below to receive it directly:**"
        )
        if lang != "en":
            text = translate_text(text, lang)
        await message.reply_text(text, reply_markup=build_category_menu_keyboard(files, "songs"))
    else:
        msg = get_songs_message()
        if lang != "en":
            msg = translate_text(msg, lang)
        await message.reply_text(msg, reply_markup=back_home_keyboard())

@app.on_message(filters.command("challenge"))
async def challenge_command(client: Client, message: Message):
    user_data = db.get_user(message.from_user.id)
    pledge = user_data.get("pledge_days", 30) if user_data else 30
    await message.reply_text(
        f"🎯 **SELECT YOUR SANKALP / PLEDGE TARGET** 🎯\n\n"
        f"Your current target: **{pledge} Days**\n\n"
        f"Choose a milestone below to set your sacred vow:",
        reply_markup=challenge_keyboard()
    )

@app.on_message(filters.command("motivation"))
async def motivation_command(client: Client, message: Message):
    user_data = db.get_user(message.from_user.id)
    lang = user_data.get("language", "en") if user_data else "en"
    msg = (
        "⚡ **INSTANT MOTIVATION & VICTORY MINDSET** ⚡\n"
        "━━━━━━━━━━━━━━━━━━━━━━\n"
        "🔥 *\"Do not look back, look forward! Infinite energy, infinite enthusiasm, infinite daring, and infinite patience — then alone can great things be accomplished!\"* — Swami Vivekananda\n\n"
        "🛡️ **Remember Why You Began**:\n"
        "• 5 seconds of cheap pixel dopamine vs. a lifetime of supreme confidence, mental clarity, and spiritual brilliance.\n"
        "• Every urge you overcome directly elevates your testosterone, sharpens your eyesight, and strengthens your nervous system.\n"
        "• You are not a slave to biological impulses. You are the master of your destiny."
    )
    if lang != "en":
        msg = translate_text(msg, lang)
    await message.reply_text(msg, reply_markup=back_home_keyboard())

# ==================== ADMIN COMMANDS ====================

@app.on_message(filters.command("stats") & filters.user(OWNER_ID))
async def admin_stats_command(client: Client, message: Message):
    stats = db.get_stats()
    lang_breakdown = "\n".join([f"  • {k.upper()}: {v} users" for k, v in stats['languages'].items()])
    
    report = (
        f"📊 **BOT ADMIN & DATABASE STATS** 📊\n"
        f"━━━━━━━━━━━━━━━━━━━━━━\n"
        f"👥 **Total Registered Users**: `{stats['total_users']}`\n"
        f"⚡ **Active Trackers**: `{stats['active_users']}`\n"
        f"🏆 **Highest Streak Record**: `{stats['max_streak']} Days`\n"
        f"⚠️ **Total Relapses Logged**: `{stats['total_relapses']}`\n\n"
        f"🌐 **Language Distribution**:\n{lang_breakdown}\n"
        f"━━━━━━━━━━━━━━━━━━━━━━\n"
        f"👑 Owner ID: `{OWNER_ID}`\n"
        f"📡 Database Channel: `{DATABASE_CHANNEL_ID}`"
    )
    await message.reply_text(report)

@app.on_message(filters.command("broadcast") & filters.user(OWNER_ID))
async def admin_broadcast_command(client: Client, message: Message):
    if not message.reply_to_message and len(message.command) < 2:
        await message.reply_text("❌ **Usage**:\n`/broadcast [message text]`\nOr reply to any text/media with `/broadcast`")
        return

    user_ids = db.get_all_user_ids()
    total_users = len(user_ids)
    if total_users == 0:
        await message.reply_text("No users registered in database.")
        return

    status_msg = await message.reply_text(f"🚀 Broadcasting announcement to {total_users} users...")
    
    success_count = 0
    fail_count = 0
    blocked_count = 0

    broadcast_msg = message.reply_to_message if message.reply_to_message else None
    broadcast_text = message.text.split(None, 1)[1] if not broadcast_msg and len(message.command) > 1 else None

    for idx, uid in enumerate(user_ids):
        try:
            if broadcast_msg:
                await broadcast_msg.copy(chat_id=uid)
            elif broadcast_text:
                await client.send_message(chat_id=uid, text=broadcast_text)
            success_count += 1
            await asyncio.sleep(0.05)  # Avoid Telegram flood limits
        except FloodWait as fw:
            await asyncio.sleep(fw.value)
            try:
                if broadcast_msg:
                    await broadcast_msg.copy(chat_id=uid)
                elif broadcast_text:
                    await client.send_message(chat_id=uid, text=broadcast_text)
                success_count += 1
            except Exception:
                fail_count += 1
        except (UserIsBlocked, InputUserDeactivated):
            blocked_count += 1
        except Exception:
            fail_count += 1

        # Periodic status update
        if (idx + 1) % 25 == 0 or (idx + 1) == total_users:
            try:
                await status_msg.edit_text(
                    f"📢 **Broadcast Progress**: `{idx+1}/{total_users}`\n"
                    f"✅ Delivered: {success_count}\n"
                    f"🚫 Blocked/Inactive: {blocked_count}\n"
                    f"❌ Failed: {fail_count}"
                )
            except Exception:
                pass

    await status_msg.edit_text(
        f"✅ **Broadcast Completed!**\n"
        f"━━━━━━━━━━━━━━━━━━━━━━\n"
        f"👥 Total Targeted: `{total_users}`\n"
        f"✅ Successfully Sent: `{success_count}`\n"
        f"🚫 Blocked/Inactive: `{blocked_count}`\n"
        f"❌ Failed: `{fail_count}`"
    )

@app.on_message(filters.command("reset_user") & filters.user(OWNER_ID))
async def admin_reset_user_command(client: Client, message: Message):
    if len(message.command) < 2:
        await message.reply_text("❌ Usage: `/reset_user [user_id]`")
        return

    try:
        target_uid = int(message.command[1])
    except ValueError:
        await message.reply_text("❌ Invalid User ID. Must be a numeric ID.")
        return

    success = db.reset_user_streak(target_uid)
    if success:
        await message.reply_text(f"✅ Successfully reset streak for user `{target_uid}` to 0 days.")
    else:
        await message.reply_text(f"❌ User `{target_uid}` not found in database.")

@app.on_message(filters.command("save"))
async def admin_save_media_command(client: Client, message: Message):
    """
    Allows OWNER_ID to reply to any document or audio in DATABASE_CHANNEL_ID
    or private chat with `/save [category]` to index it under that category.
    """
    is_owner = (message.from_user and message.from_user.id == OWNER_ID)
    is_db_channel = (message.chat and message.chat.id in get_channel_peers())

    if not (is_owner or is_db_channel):
        return

    if not message.reply_to_message:
        await message.reply_text(
            "❌ **Usage**: Reply to any file/audio with `/save [category]`\n\n"
            "Supported categories: `books`, `songs`, `health`, `workout`, `quotes`, `mindset`"
        )
        return

    replied = message.reply_to_message
    file_obj = replied.document or replied.audio or replied.video or replied.photo or replied.voice
    if not file_obj:
        await message.reply_text("❌ The replied message does not contain any file/media.")
        return

    if len(message.command) > 1:
        category = message.command[1].lower().replace("#", "").strip()
    else:
        await message.reply_text("❌ Please specify category: `/save books`, `/save songs`, `/save workout`, `/save health`")
        return

    file_id = getattr(file_obj, "file_id", "")
    file_name = getattr(file_obj, "file_name", "") or getattr(file_obj, "title", "") or ""
    caption = replied.caption or ""

    # Save to SQLite index
    db.save_media(
        message_id=replied.id,
        channel_id=replied.chat.id,
        category=category,
        file_id=file_id,
        file_name=file_name,
        caption=caption
    )

    await message.reply_text(
        f"✅ **File Successfully Indexed!**\n"
        f"━━━━━━━━━━━━━━━━━━━━━━\n"
        f"📁 **Category**: `#{category}`\n"
        f"📄 **File Name**: `{file_name or 'Media File'}`\n"
        f"🆔 **Message ID**: `{replied.id}`\n\n"
        f"Users will now automatically receive this file when using `/{category}`! 🚀"
    )

# ==================== CALLBACK QUERY ROUTING ====================

@app.on_callback_query()
async def handle_callback_query(client: Client, callback_query: CallbackQuery):
    data = callback_query.data
    user = callback_query.from_user
    if not user:
        return

    db.add_or_update_user(user.id, user.first_name, user.last_name, user.username)
    user_data = db.get_user(user.id)
    lang = user_data.get("language", "en") if user_data else "en"

    if data == "cb_home":
        greeting_text = (
            f"Ram Ram Brahmachari {user.first_name} 🙏\n\n"
            f"Welcome to the sacred **Brahmacharya & NoFap Sanctum**.\n\n"
            f"⚡ **Your Live Journey Status**:\n"
            f"{get_streak_message(user_data)}\n\n"
            f"👇 Select an option below:"
        )
        if lang != "en":
            greeting_text = translate_text(greeting_text, lang)
        await callback_query.edit_message_text(
            text=greeting_text,
            reply_markup=main_menu_keyboard(lang),
            disable_web_page_preview=True
        )

    elif data == "cb_streak":
        msg = get_streak_message(user_data)
        if lang != "en":
            msg = translate_text(msg, lang)
        await callback_query.edit_message_text(
            text=msg,
            reply_markup=InlineKeyboardMarkup([
                [InlineKeyboardButton("🔄 Refresh", callback_data="cb_streak")],
                [InlineKeyboardButton("🏆 Leaderboard", callback_data="cb_leaderboard")],
                [InlineKeyboardButton("🔙 Main Menu", callback_data="cb_home")]
            ]),
            disable_web_page_preview=True
        )

    elif data == "cb_leaderboard":
        top_list = db.get_top_leaderboard(10)
        text = "🏆 **BRAHMACHARYA LEADERBOARD (TOP SADHAKS)** 🏆\n━━━━━━━━━━━━━━━━━━━━━━\n"
        medals = ["🥇", "🥈", "🥉", "🎖️", "🎖️", "🎖️", "🎖️", "🎖️", "🎖️", "🎖️"]
        for idx, member in enumerate(top_list):
            medal = medals[idx] if idx < len(medals) else "🎖️"
            uname = f"@{member['username']}" if member['username'] else member['name']
            rank_badge, _ = get_rank_and_badge(member['days'])
            badge_icon = rank_badge.split()[0]
            text += f"{medal} **{idx+1}. {uname}** — **{member['days']} Days** ({badge_icon})\n"
        text += "\n━━━━━━━━━━━━━━━━━━━━━━\n💡 *\"Purity is strength. Keep moving forward!\"*"
        await callback_query.edit_message_text(
            text=text,
            reply_markup=back_home_keyboard(),
            disable_web_page_preview=True
        )

    elif data == "cb_relapse_prompt":
        prompt_text = (
            "⚠️ **RELAPSE CONFIRMATION** ⚠️\n\n"
            "Brother, are you sure you want to log a relapse and reset your streak?\n\n"
            "Remember: A setback is only a learning curve if you rise immediately."
        )
        await callback_query.edit_message_text(
            text=prompt_text,
            reply_markup=relapse_confirmation_keyboard()
        )

    elif data == "cb_relapse_confirm":
        ended_days, total_relapses = db.record_relapse(user.id)
        
        # Log to Database Channel
        alert_msg = (
            f"⚠️ **RELAPSE LOG ALERT** ⚠️\n"
            f"━━━━━━━━━━━━━━━━━━━━━━\n"
            f"👤 **User**: {user.first_name} {user.last_name or ''}\n"
            f"🆔 **ID**: `{user.id}`\n"
            f"🔗 **Username**: @{user.username if user.username else 'None'}\n"
            f"⏳ **Streak Ended At**: `{ended_days} Days`\n"
            f"⚠️ **Total Relapses**: `{total_relapses}`\n"
            f"📅 **Timestamp**: `{datetime.now(timezone.utc).strftime('%Y-%m-%d %H:%M:%S UTC')}`"
        )
        await log_to_database_channel(client, alert_msg)

        recovery_msg = (
            f"🔄 **STREAK RESET TO DAY 0** 🔄\n"
            f"━━━━━━━━━━━━━━━━━━━━━━\n"
            f"Previous Streak: **{ended_days} Days**\n\n"
            f"🙏 **Do not despair!** Rise immediately:\n"
            f"1. Take a cold shower right now.\n"
            f"2. Perform 10 minutes of Anulom Vilom.\n"
            f"3. Note down the trigger that caused this slip, and destroy that habit loop.\n\n"
            f"🔥 *\"Arise, awake, and stop not till the goal is reached!\"* — Swami Vivekananda"
        )
        if lang != "en":
            recovery_msg = translate_text(recovery_msg, lang)

        await callback_query.edit_message_text(
            text=recovery_msg,
            reply_markup=back_home_keyboard()
        )

    elif data == "cb_language_menu":
        await callback_query.edit_message_text(
            text="🌐 **Choose Your Preferred Language / अपनी भाषा चुनें**:\n\nSelect your language below:",
            reply_markup=language_selection_keyboard()
        )

    elif data.startswith("setlang_"):
        selected_lang = data.split("_", 1)[1]
        db.set_language(user.id, selected_lang)
        lang_info = SUPPORTED_LANGUAGES.get(selected_lang, {"name": selected_lang, "flag": "🌐"})
        confirm_text = f"✅ Language updated to **{lang_info['flag']} {lang_info['name']}**!"
        if selected_lang != "en":
            confirm_text = translate_text(confirm_text, selected_lang)
        await callback_query.answer(f"Language set to {lang_info['name']}")
        await callback_query.edit_message_text(
            text=confirm_text,
            reply_markup=back_home_keyboard()
        )

    elif data == "cb_challenge_menu":
        await callback_query.edit_message_text(
            text="🎯 **CHOOSE YOUR SANKALP / PLEDGE TARGET**:\n\nSelect your milestone goal:",
            reply_markup=challenge_keyboard()
        )

    elif data.startswith("setpledge_"):
        days = int(data.split("_")[1])
        db.set_pledge(user.id, days)
        await callback_query.answer(f"🎯 Target set to {days} Days!")
        await callback_query.edit_message_text(
            text=f"✅ **Sankalp Confirmed!**\n\nYour target pledge has been updated to **{days} Days**.\nStay focused, disciplined, and steadfast on the path of Brahmacharya! 🕉️",
            reply_markup=back_home_keyboard()
        )

    elif data == "cb_mindset":
        msg = get_mindset_message()
        if lang != "en":
            msg = translate_text(msg, lang)
        await callback_query.edit_message_text(text=msg, reply_markup=back_home_keyboard())

    elif data == "cb_workout":
        msg = get_workout_message()
        if lang != "en":
            msg = translate_text(msg, lang)
        await callback_query.edit_message_text(text=msg, reply_markup=back_home_keyboard())

    elif data == "cb_health":
        msg = get_health_message()
        if lang != "en":
            msg = translate_text(msg, lang)
        await callback_query.edit_message_text(text=msg, reply_markup=back_home_keyboard())

    elif data == "cb_quotes":
        msg = get_quotes_message()
        if lang != "en":
            msg = translate_text(msg, lang)
        await callback_query.edit_message_text(text=msg, reply_markup=back_home_keyboard())

    elif data == "cb_books":
        files = db.get_category_media("books")
        if not files:
            files = await scan_and_get_category_files(client, "books")
        if files:
            text = (
                "📚 **SACRED BRAHMACHARYA BOOKS** 📚\n"
                "━━━━━━━━━━━━━━━━━━━━━━\n"
                "The following spiritual texts and guides are available.\n\n"
                "👇 **Tap any book below to receive it directly:**"
            )
            if lang != "en":
                text = translate_text(text, lang)
            await callback_query.edit_message_text(text=text, reply_markup=build_category_menu_keyboard(files, "books"))
        else:
            msg = get_books_message()
            if lang != "en":
                msg = translate_text(msg, lang)
            await callback_query.edit_message_text(text=msg, reply_markup=back_home_keyboard())

    elif data == "cb_songs":
        files = db.get_category_media("songs")
        if not files:
            files = await scan_and_get_category_files(client, "songs")
        if files:
            text = (
                "🎵 **SACRED AUDIO & CHANTS** 🎵\n"
                "━━━━━━━━━━━━━━━━━━━━━━\n"
                "The following high-vibration chants and tracks are available.\n\n"
                "👇 **Tap any track below to receive it directly:**"
            )
            if lang != "en":
                text = translate_text(text, lang)
            await callback_query.edit_message_text(text=text, reply_markup=build_category_menu_keyboard(files, "songs"))
        else:
            msg = get_songs_message()
            if lang != "en":
                msg = translate_text(msg, lang)
            await callback_query.edit_message_text(text=msg, reply_markup=back_home_keyboard())

    elif data.startswith("cb_dl_"):
        try:
            media_id = int(data.split("_")[2])
        except (IndexError, ValueError):
            await callback_query.answer("❌ Invalid file selection.", show_alert=True)
            return

        item = db.get_media_by_id(media_id)
        if not item:
            await callback_query.answer("❌ File not found in archive.", show_alert=True)
            return

        raw_title = item.get("file_name") or "File"
        clean_title = raw_title.split("\n")[0].strip()
        for ext in [".pdf", ".epub", ".mobi", ".djvu", ".mp3", ".m4a", ".wav", ".aac", ".ogg", ".opus"]:
            if clean_title.lower().endswith(ext):
                clean_title = clean_title[:-len(ext)]
                break
        clean_title = clean_title.replace("_", " ").strip()
        if not clean_title:
            clean_title = "Requested File"

        await callback_query.answer(f"Sending: {clean_title[:24]}... ⏳", show_alert=False)

        target_chat = callback_query.message.chat.id
        mid = item.get("message_id")
        cid = item.get("channel_id") or DATABASE_CHANNEL_ID
        fid = item.get("file_id")

        sent = False
        if mid:
            possible_chats = [cid] + [p for p in get_channel_peers() if p != cid]
            for peer_chat in possible_chats:
                try:
                    await client.copy_message(chat_id=target_chat, from_chat_id=peer_chat, message_id=mid)
                    sent = True
                    break
                except Exception as e:
                    logger.debug(f"copy_message attempt from {peer_chat} failed: {e}")

        if not sent and fid:
            try:
                cat = item.get("category", "")
                if cat in ["songs", "song"]:
                    await client.send_audio(chat_id=target_chat, audio=fid, caption=item.get("caption") or "")
                elif cat in ["quotes", "quote"] or item.get("file_type") == "photo":
                    await client.send_photo(chat_id=target_chat, photo=fid, caption=item.get("caption") or "")
                else:
                    await client.send_document(chat_id=target_chat, document=fid, caption=item.get("caption") or "")
                sent = True
            except Exception as e:
                logger.debug(f"send_document/audio fallback failed: {e}")

        if not sent:
            await callback_query.message.reply_text(
                f"⚠️ Could not deliver `{clean_title}`. Channel message might have been deleted.",
                disable_web_page_preview=True
            )

# ==================== WEB SERVER (RENDER KEEP-ALIVE) ====================
class HealthCheckHandler(BaseHTTPRequestHandler):
    def do_GET(self):
        self.send_response(200)
        self.send_header("Content-Type", "application/json")
        self.end_headers()
        response = '{"status": "ok", "service": "Brahmacharya & NoFap Streak Bot", "alive": true}'
        self.wfile.write(response.encode("utf-8"))

    def log_message(self, format, *args):
        # Suppress standard HTTP request logging
        return

def run_http_server():
    server_address = ("", PORT)
    httpd = HTTPServer(server_address, HealthCheckHandler)
    logger.info(f"🌐 Health check HTTP server running on port {PORT}")
    httpd.serve_forever()

# ==================== MAIN RUNNER ====================
async def start_services():
    logger.info("Starting Brahmacharya & NoFap Streak Bot...")
    try:
        await app.start()
        
        # Register slash commands with Telegram
        bot_commands = [
            BotCommand("start", "Start bot & view live streak menu"),
            BotCommand("streak", "View your live Brahmacharya streak & rank"),
            BotCommand("leaderboard", "View top Brahmachari rankings"),
            BotCommand("relapse", "Report a relapse & reset streak"),
            BotCommand("language", "Change bot language (Hindi, Hinglish, Odia, etc.)"),
            BotCommand("challenge", "Set your 7/21/30/90/365 Days Sankalp"),
            BotCommand("workout", "Daily Vyayam, Asanas & strength guide"),
            BotCommand("health", "Sattvic diet, Ayurvedic rules & cold showers"),
            BotCommand("mindset", "Transmutation of Ojas & Pranayama guide"),
            BotCommand("quotes", "Sacred Bhagavad Gita & Rishi shlokas"),
            BotCommand("books", "Essential Brahmacharya literature & books"),
            BotCommand("songs", "Sacred chants, bhajans & meditation audio"),
            BotCommand("index", "Admin: Scan & index (/index book, /index song, /index quote)"),
            BotCommand("save", "Admin: Index replied media under a category"),
            BotCommand("motivation", "Urge fighting rules & victory mindset")
        ]
        
        try:
            await app.set_bot_commands(bot_commands)
            logger.info("✅ Slash commands successfully registered with Telegram UI")
        except Exception as e:
            logger.warning(f"Failed to set bot commands: {e}")

        me = await app.get_me()
        logger.info(f"🔥 @{me.username} is now ONLINE and serving Brahmacharis!")
        await idle()
    finally:
        try:
            await app.stop()
            logger.info("Client session closed gracefully.")
        except Exception:
            pass

if __name__ == "__main__":
    # Start background HTTP server
    http_thread = threading.Thread(target=run_http_server, daemon=True)
    http_thread.start()

    try:
        loop = asyncio.get_event_loop()
    except RuntimeError:
        loop = asyncio.new_event_loop()
        asyncio.set_event_loop(loop)

    try:
        loop.run_until_complete(start_services())
    except (KeyboardInterrupt, SystemExit):
        logger.info("Bot shutting down gracefully.")

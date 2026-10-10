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

from pyrogram import Client, filters
from pyrogram.types import (
    InlineKeyboardMarkup,
    InlineKeyboardButton,
    CallbackQuery,
    Message,
    BotCommand
)
from pyrogram.errors import FloodWait, UserIsBlocked, InputUserDeactivated

from deep_translator import GoogleTranslator
from dotenv import load_dotenv

load_dotenv()

# ==================== CONFIGURATION ====================
API_ID = int(os.getenv("API_ID", "0"))
API_HASH = os.getenv("API_HASH", "")
BOT_TOKEN = os.getenv("BOT_TOKEN", "")
OWNER_ID = int(os.getenv("OWNER_ID", "5650859707"))
DATABASE_CHANNEL_ID = int(os.getenv("DATABASE_CHANNEL_ID", "-5353068930"))
PORT = int(os.getenv("PORT", "8080"))
DB_PATH = os.getenv("DB_PATH", "brahmacharya.db")

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
        self._init_db()

    def _get_connection(self):
        conn = sqlite3.connect(self.db_path, check_same_thread=False)
        conn.row_factory = sqlite3.Row
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
            conn.commit()

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
        logger.warning(f"Translation error for lang {target_lang}: {e}")
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
app = Client(
    name="BrahmacharyaStreakBot",
    api_id=API_ID,
    api_hash=API_HASH,
    bot_token=BOT_TOKEN
)

# Safe Channel Logger
async def log_to_database_channel(client: Client, text: str):
    """Safely logs alerts to the database channel."""
    if not DATABASE_CHANNEL_ID:
        return

    channels_to_try = [DATABASE_CHANNEL_ID]
    # If channel id is raw (e.g. -5353068930), try both raw and -100 prefix
    id_str = str(DATABASE_CHANNEL_ID)
    if id_str.startswith("-") and not id_str.startswith("-100"):
        try:
            channels_to_try.append(int("-100" + id_str[1:]))
        except Exception:
            pass

    for ch_id in channels_to_try:
        try:
            await client.send_message(
                chat_id=ch_id,
                text=text,
                disable_web_page_preview=True
            )
            return
        except Exception as e:
            logger.debug(f"Channel log attempt failed for {ch_id}: {e}")

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

@app.on_message(filters.command("workout"))
async def workout_command(client: Client, message: Message):
    user_data = db.get_user(message.from_user.id)
    lang = user_data.get("language", "en") if user_data else "en"
    msg = get_workout_message()
    if lang != "en":
        msg = translate_text(msg, lang)
    await message.reply_text(msg, reply_markup=back_home_keyboard())

@app.on_message(filters.command("health"))
async def health_command(client: Client, message: Message):
    user_data = db.get_user(message.from_user.id)
    lang = user_data.get("language", "en") if user_data else "en"
    msg = get_health_message()
    if lang != "en":
        msg = translate_text(msg, lang)
    await message.reply_text(msg, reply_markup=back_home_keyboard())

@app.on_message(filters.command("mindset"))
async def mindset_command(client: Client, message: Message):
    user_data = db.get_user(message.from_user.id)
    lang = user_data.get("language", "en") if user_data else "en"
    msg = get_mindset_message()
    if lang != "en":
        msg = translate_text(msg, lang)
    await message.reply_text(msg, reply_markup=back_home_keyboard())

@app.on_message(filters.command("quotes"))
async def quotes_command(client: Client, message: Message):
    user_data = db.get_user(message.from_user.id)
    lang = user_data.get("language", "en") if user_data else "en"
    msg = get_quotes_message()
    if lang != "en":
        msg = translate_text(msg, lang)
    await message.reply_text(msg, reply_markup=back_home_keyboard())

@app.on_message(filters.command("books"))
async def books_command(client: Client, message: Message):
    user_data = db.get_user(message.from_user.id)
    lang = user_data.get("language", "en") if user_data else "en"
    msg = get_books_message()
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
        msg = get_books_message()
        if lang != "en":
            msg = translate_text(msg, lang)
        await callback_query.edit_message_text(text=msg, reply_markup=back_home_keyboard())

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
async def main():
    # Start background HTTP server
    http_thread = threading.Thread(target=run_http_server, daemon=True)
    http_thread.start()

    logger.info("Starting Brahmacharya & NoFap Streak Bot...")
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
        BotCommand("books", "Essential Brahmacharya literature"),
        BotCommand("motivation", "Urge fighting rules & victory mindset")
    ]
    
    try:
        await app.set_bot_commands(bot_commands)
        logger.info("✅ Slash commands successfully registered with Telegram UI")
    except Exception as e:
        logger.warning(f"Failed to set bot commands: {e}")

    me = await app.get_me()
    logger.info(f"🔥 @{me.username} is now ONLINE and serving Brahmacharis!")
    
    # Keep running until stopped
    await asyncio.Event().wait()

if __name__ == "__main__":
    try:
        asyncio.run(main())
    except (KeyboardInterrupt, SystemExit):
        logger.info("Bot shutting down gracefully.")

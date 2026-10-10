# 🕉️ Brahmacharya & NoFap Streak Telegram Bot

A high-performance, multi-language Telegram Bot built with **Pyrogram** and **deep-translator** designed to guide sadhaks on their Brahmacharya (celibacy & vital energy preservation) journey, featuring live streak tracking, rank badges, leaderboards, topic guides, owner admin controls, database channel logging, and Render.com health check server.

---

## 🌟 Key Features

1. **👑 Owner / Admin Controls**:
   - `OWNER_ID`: Protected commands accessible only to the owner (default: `5650859707`).
   - `/stats`: View total registered users, active streaks, highest streak record, total relapses, and language distribution.
   - `/broadcast [message]`: Broadcast text, photo, video, or forward messages to all registered users with real-time delivery status.
   - `/reset_user [user_id]`: Reset streak for any user.

2. **📡 Database Channel Logging**:
   - `DATABASE_CHANNEL_ID`: Automatically sends log alerts on new user registration and relapse events to your private database/log channel (default: `-5353068930`).

3. **🌐 Multi-Language Auto-Translation**:
   - `/language`: Instant one-click selection for **Hindi (हिन्दी)**, **Hinglish**, **English**, **Odia (ଓଡ଼ିଆ)**, **Bengali (বাংলা)**, **Telugu (తెలుగు)**, **Tamil (தமிழ்)**, **Marathi (मराठी)**, **Gujarati (ગુજરાતી)**, **Kannada (ಕನ್ನಡ)**, **Malayalam (മലയാളം)**, **Punjabi (ਪੰਜਾਬੀ)**, **Spanish (Español)**, **Russian (Русский)**, **French (Français)**, **German (Deutsch)**, and **Arabic (العربية)** using `deep-translator`.

4. **⚡ Live Streak & Badge System**:
   - `/streak`: Live timer (Days, Hours, Minutes), rank badges (🥉 Shishya ➔ 🌱 Sadhak ➔ 🌿 Veerya Rakshak ➔ 🔥 Agni Sadhak ➔ ⚡ Ojas Seeker ➔ 🛡️ Mahaveer Brahmachari ➔ ⚔️ Tapasvi ➔ 👑 Siddha Purusha ➔ 🔱 Paramhansa ➔ 🕉️ Divya Atman), progress bars, and personal records.
   - `/leaderboard`: Displays the top 10 Brahmacharis with highest active streaks.
   - `/relapse`: Safe confirmation prompt before streak reset, psychological recovery advice, and automatic log alert to the database channel.
   - `/challenge`: Select your pledge milestone (7, 21, 30, 90, 365 Days).

5. **📖 Comprehensive Topic Guides**:
   - `/workout`: Bharatiya Vyayam, Surya Namaskar, Desi Dands, Baithaks, Shirshasana.
   - `/health`: Sattvic diet, foods to avoid, Ayurvedic rules, cold shower therapy.
   - `/mindset`: Ojas transmutation, Pranayama (Anulom Vilom, Kapalabhati, Bhastrika), Trataka.
   - `/quotes`: Shlokas from Bhagavad Gita, Swami Vivekananda, Patanjali Yoga Sutras, Chanakya Neeti.
   - `/books`: Recommended scriptures and literature on Brahmacharya.
   - `/motivation`: 10-Minute urge surfing rule and victory mindset.

6. **🚀 Production Ready for Render / Docker**:
   - Built-in HTTP server listening on `PORT` (e.g. 8080) for 24/7 keep-alive pings.
   - Automatic registration of `/` commands into Telegram UI using `app.set_bot_commands()`.

---

## 🛠️ Environment Variables

| Variable | Description | Default |
|---|---|---|
| `API_ID` | Telegram API ID from [my.telegram.org](https://my.telegram.org) | Required |
| `API_HASH` | Telegram API Hash from [my.telegram.org](https://my.telegram.org) | Required |
| `BOT_TOKEN` | Bot Token from [@BotFather](https://t.me/BotFather) | Required |
| `OWNER_ID` | Telegram User ID of Bot Owner | `5650859707` |
| `DATABASE_CHANNEL_ID` | Telegram Channel ID for logging alerts | `-5353068930` |
| `PORT` | HTTP Server port for Render keep-alive | `8080` |

---

## 🚀 Local Run

```bash
# Clone the repository
git clone https://github.com/bantymallick88-cell/Brahmacharya-NoFap-Streak-Bot.git
cd Brahmacharya-NoFap-Streak-Bot

# Install dependencies
pip install -r requirements.txt

# Create .env and set your credentials
cp .env.example .env

# Run the bot
python bot.py
```

---

## 🐳 Docker Deployment

```bash
docker build -t brahmacharya-bot .
docker run -p 8080:8080 --env-file .env brahmacharya-bot
```

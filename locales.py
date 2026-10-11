# -*- coding: utf-8 -*-
"""
Multi-Language Dictionary Localization Module (English, Hindi, Odia)
Supports:
- en: English
- hi: हिन्दी (Hindi)
- or: ଓଡ଼ିଆ (Odia)
"""

SUPPORTED_LANGUAGES = {
    "en": {"name": "English", "flag": "🇬🇧"},
    "hi": {"name": "हिन्दी (Hindi)", "flag": "🇮🇳"},
    "or": {"name": "ଓଡ଼ିଆ (Odia)", "flag": "🇮🇳"},
}

# 10 Spiritual Rank Tiers across English, Hindi, and Odia
RANKS_LOCALES = [
    {
        "days": 0,
        "en": ("🥉 Shishya (Seeker)", "Beginning of self-mastery. Hold the fort!"),
        "hi": ("🥉 शिष्य (साधक)", "आत्म-नियंत्रण का आरंभ। संकल्प पर अडिग रहें!"),
        "or": ("🥉 ଶିଷ୍ୟ (ସାଧକ)", "ଆତ୍ମ-ନିୟନ୍ତ୍ରଣର ଆରମ୍ଭ। ସଂକଳ୍ପରେ ଦୃଢ଼ ରୁହନ୍ତୁ!")
    },
    {
        "days": 4,
        "en": ("🌱 Sadhak (Disciplined)", "First milestone crossed. Mind is stabilizing."),
        "hi": ("🌱 साधक (अनुशासित)", "पहला पड़ाव पार हुआ। मन स्थिर हो रहा है।"),
        "or": ("🌱 ସାଧକ (ଅନୁଶାସିତ)", "ପ୍ରଥମ ସୋପାନ ପାର ହେଲା। ମନ ସ୍ଥିର ହେଉଛି।")
    },
    {
        "days": 8,
        "en": ("🌿 Veerya Rakshak (Energy Preserver)", "Vital energy is circulating into your blood."),
        "hi": ("🌿 वीर्य रक्षक (ऊर्जा संरक्षक)", "प्राण शक्ति रक्त में प्रवाहित हो रही है।"),
        "or": ("🌿 ବୀର୍ଯ୍ୟ ରକ୍ଷକ (ଶକ୍ତି ସଂରକ୍ଷକ)", "ଜୀବନୀ ଶକ୍ତି ରକ୍ତରେ ସଞ୍ଚାରିତ ହେଉଛି।")
    },
    {
        "days": 15,
        "en": ("🔥 Agni Sadhak (Habit Master)", "Old neuro-pathways are burning away."),
        "hi": ("🔥 अग्नि साधक (वासना भस्मक)", "पुरानी वासनाएं जलकर नष्ट हो रही हैं।"),
        "or": ("🔥 ଅଗ୍ନି ସାଧକ (ବାସନା ଭସ୍ମକ)", "ପୁରୁଣା କୁଅଭ୍ୟାସ ଜଳି ନଷ୍ଟ ହେଉଛି।")
    },
    {
        "days": 22,
        "en": ("⚡ Ojas Seeker (Transmuter)", "One full solar cycle! Eyes radiate clarity."),
        "hi": ("⚡ ओजस साधक (तेजस्वी)", "एक पूर्ण चक्र पूर्ण! नेत्रों में दिव्य तेज झलक रहा है।"),
        "or": ("⚡ ଓଜ ସାଧକ (ତେଜସ୍ୱୀ)", "ଏକ ପୂର୍ଣ୍ଣ ଚକ୍ର ଶେଷ! ଚକ୍ଷୁରେ ଦିବ୍ୟ ତେଜ ପ୍ରକାଶ ପାଉଛି।")
    },
    {
        "days": 31,
        "en": ("🛡️ Mahaveer Brahmachari (Indomitable)", "Immense willpower and physical stamina."),
        "hi": ("🛡️ महावीर ब्रह्मचारी (अदम्य)", "अपार इच्छाशक्ति और अदम्य शारीरिक सहनशीलता।"),
        "or": ("🛡️ ମହାବୀର ବ୍ରହ୍ମଚାରୀ (ଅପରାଜେୟ)", "ଅସୀମ ଇଚ୍ଛାଶକ୍ତି ଏବଂ ଶାରୀରିକ ସହନଶୀଳତା।")
    },
    {
        "days": 61,
        "en": ("⚔️ Tapasvi (Sense Conqueror)", "Sensual desires lose their grip over you."),
        "hi": ("⚔️ तपस्वी (इंद्रिय विजेता)", "इंद्रिय वासनाओं की पकड़ समाप्त हो रही है।"),
        "or": ("⚔️ ତପସ୍ୱୀ (ଇନ୍ଦ୍ରିୟ ବିଜେତା)", "ଇନ୍ଦ୍ରିୟ ବାସନାଗୁଡ଼ିକର ପ୍ରଭାବ ନଷ୍ଟ ହୋଇଛି।")
    },
    {
        "days": 91,
        "en": ("👑 Siddha Purusha (Master of Self)", "Mind operates at peak spiritual clarity."),
        "hi": ("👑 सिद्ध पुरुष (आत्मजयी)", "मस्तिष्क पूर्ण आध्यात्मिक शांति और स्पष्टता में स्थित है।"),
        "or": ("👑 ସିଦ୍ଧ ପୁରୁଷ (ଆତ୍ମଜୟୀ)", "ମନରେ ପରମ ଆଧ୍ୟାତ୍ମିକ ଶାନ୍ତି ଏବଂ ସ୍ପଷ୍ଟତା।")
    },
    {
        "days": 181,
        "en": ("🔱 Paramhansa (Divine Yogi)", "Transcended mundane cravings completely."),
        "hi": ("🔱 परमहंस (दिव्य योगी)", "सांसारिक और तुच्छ वासनाओं से पूर्णतः मुक्त।"),
        "or": ("🔱 ପରମହଂସ (ଦିବ୍ୟ ଯୋଗୀ)", "ସାଂସାରିକ ତୁଚ୍ଛ ବାସନାରୁ ସମ୍ପୂର୍ଣ୍ଣ ମୁକ୍ତ।")
    },
    {
        "days": 365,
        "en": ("🕉️ Divya Atman (Enlightened Brahmachari)", "Legendary discipline. A living inspiration!"),
        "hi": ("🕉️ दिव्य आत्मा (प्रबुद्ध ब्रह्मचारी)", "अलौकिक तपस्या और ब्रह्मचर्य। एक साक्षात प्रेरणा!"),
        "or": ("🕉️ ଦିବ୍ୟ ଆତ୍ମା (ପ୍ରବୁଦ୍ଧ ବ୍ରହ୍ମଚାରୀ)", "ଅଲୌକିକ ତପସ୍ୟା। ଏକ ଜୀବନ୍ତ ପ୍ରେରଣା!")
    }
]

def get_rank_and_badge_localized(days: int, lang: str = "en") -> tuple[str, str]:
    """Returns localized rank title and description."""
    target_lang = lang if lang in ["en", "hi", "or"] else "en"
    matched = RANKS_LOCALES[0]
    for tier in RANKS_LOCALES:
        if days >= tier["days"]:
            matched = tier
        else:
            break
    title, desc = matched[target_lang]
    return title, desc

LOCALES = {
    # Buttons - Main Menu
    "btn_my_streak": {
        "en": "📊 My Streak",
        "hi": "📊 मेरी साधना (Streak)",
        "or": "📊 ମୋର ଷ୍ଟ୍ରିକ୍"
    },
    "btn_leaderboard": {
        "en": "🏆 Leaderboard",
        "hi": "🏆 लीडरबोर्ड",
        "or": "🏆 ଲିଡରବୋର୍ଡ"
    },
    "btn_relapse": {
        "en": "🔄 Log Relapse",
        "hi": "🔄 पतन दर्ज करें (Reset)",
        "or": "🔄 ରିଲ୍ୟାପ୍ସ ଲଗ୍ କରନ୍ତୁ"
    },
    "btn_challenge": {
        "en": "🎯 Challenge Target",
        "hi": "🎯 संकल्प लक्ष्य",
        "or": "🎯 ସଂକଳ୍ପ ଲକ୍ଷ୍ୟ"
    },
    "btn_mindset": {
        "en": "🧘 Mindset & Ojas",
        "hi": "🧘 मनोबल एवं ओजस",
        "or": "🧘 ମନୋବଳ ଏବଂ ଓଜ"
    },
    "btn_shlokas": {
        "en": "📜 Daily Shlokas",
        "hi": "📜 दैनिक श्लोक",
        "or": "📜 ଦୈନିକ ଶ୍ଳୋକ"
    },
    "btn_workout": {
        "en": "⚔️ Workout & Vyayam",
        "hi": "⚔️ व्यायाम एवं शक्ति",
        "or": "⚔️ ବ୍ୟାୟାମ ଏବଂ ଶକ୍ତି"
    },
    "btn_health": {
        "en": "🥗 Sattvic Health",
        "hi": "🥗 सात्विक आहार",
        "or": "🥗 ସାତ୍ତ୍ୱିକ ଆହାର"
    },
    "btn_books": {
        "en": "📚 Sacred Books",
        "hi": "📚 पवित्र पुस्तकें",
        "or": "📚 ପବିତ୍ର ପୁସ୍ତକ"
    },
    "btn_songs": {
        "en": "🎵 Sacred Songs",
        "hi": "🎵 पवित्र संगीत एवं भजन",
        "or": "🎵 ପବିତ୍ର ଭଜନ ଓ ସଙ୍ଗୀତ"
    },
    "btn_language": {
        "en": "🌐 Language / भाषा / ଭାଷା",
        "hi": "🌐 भाषा / Language",
        "or": "🌐 ଭାଷା / Language"
    },

    # Navigation Buttons
    "btn_back_home": {
        "en": "🔙 Back to Sanctum",
        "hi": "🔙 मुख्य मेनू पर लौटें",
        "or": "🔙 ମୁଖ୍ୟ ମେନୁକୁ ଫେରନ୍ତୁ"
    },
    "btn_back": {
        "en": "🔙 Back",
        "hi": "🔙 वापस",
        "or": "🔙 ଫେରନ୍ତୁ"
    },
    "btn_view_streak": {
        "en": "📊 View My Streak",
        "hi": "📊 मेरी साधना देखें",
        "or": "📊 ମୋର ଷ୍ଟ୍ରିକ୍ ଦେଖନ୍ତୁ"
    },
    "btn_refresh_streak": {
        "en": "🔄 Refresh Streak",
        "hi": "🔄 ताज़ा करें (Refresh)",
        "or": "🔄 ସତେଜ କରନ୍ତୁ (Refresh)"
    },

    # Relapse Buttons
    "btn_relapse_confirm": {
        "en": "⚠️ Yes, I Relapsed (Reset)",
        "hi": "⚠️ हाँ, मुझसे पतन हुआ (Reset)",
        "or": "⚠️ ହଁ, ମୋର ପତନ ହେଲା (Reset)"
    },
    "btn_relapse_cancel": {
        "en": "🛡️ No, I Stayed Strong!",
        "hi": "🛡️ नहीं, मैं अडिग रहा!",
        "or": "🛡️ ନା, ମୁଁ ଦୃଢ଼ ରହିଲି!"
    },

    # Challenge Buttons
    "btn_pledge_7": {
        "en": "🌱 7 Days (Shankha)",
        "hi": "🌱 7 दिन (शंख व्रत)",
        "or": "🌱 ୭ ଦିନ (ଶଙ୍ଖ ବ୍ରତ)"
    },
    "btn_pledge_21": {
        "en": "🌿 21 Days (Sankalp)",
        "hi": "🌿 21 दिन (संकल्प व्रत)",
        "or": "🌿 ୨୧ ଦିନ (ସଂକଳ୍ପ ବ୍ରତ)"
    },
    "btn_pledge_30": {
        "en": "🔥 30 Days (Agni)",
        "hi": "🔥 30 दिन (अग्नि व्रत)",
        "or": "🔥 ୩୦ ଦିନ (ଅଗ୍ନି ବ୍ରତ)"
    },
    "btn_pledge_90": {
        "en": "🛡️ 90 Days (Mahavrata)",
        "hi": "🛡️ 90 दिन (महाव्रत)",
        "or": "🛡️ ୯୦ ଦିନ (ମହାବ୍ରତ)"
    },
    "btn_pledge_365": {
        "en": "👑 365 Days (Divya Vrata)",
        "hi": "👑 365 दिन (दिव्य व्रत)",
        "or": "👑 ୩୬୫ ଦିନ (ଦିବ୍ୟ ବ୍ରତ)"
    },

    # Screens & Messages
    "start_greeting": {
        "en": "Ram Ram Brahmachari {name} 🙏\n\nWelcome to the sacred **Brahmacharya & NoFap Sanctum**.\nPreserve your divine energy (Veerya), awaken your spiritual luster (Ojas), and conquer your senses.\n\n⚡ **Your Live Journey Status**:\n{streak_info}\n\n👇 Select an option below to guide your sadhana:",
        "hi": "राम राम ब्रह्मचारी {name} 🙏\n\nपवित्र **ब्रह्मचर्य एवं संकल्प साधना** में आपका स्वागत है।\nअपने दिव्य वीर्य की रक्षा करें, ओजस शक्ति को जाग्रत करें और अपनी इंद्रियों पर विजय प्राप्त करें।\n\n⚡ **आपकी लाइव साधना स्थिति**:\n{streak_info}\n\n👇 अपनी साधना के लिए नीचे से विकल्प चुनें:",
        "or": "ରାମ ରାମ ବ୍ରହ୍ମଚାରୀ {name} 🙏\n\nପବିତ୍ର **ବ୍ରହ୍ମଚର୍ଯ୍ୟ ଏବଂ ନୋଫାପ୍ ସାଧନା**କୁ ଆପଣଙ୍କୁ ସ୍ୱାଗତ।\nଆପଣଙ୍କ ଦିବ୍ୟ ବୀର୍ଯ୍ୟ ଶକ୍ତି ସଂରକ୍ଷଣ କରନ୍ତୁ, ଓଜ ଶକ୍ତି ଜାଗ୍ରତ କରନ୍ତୁ ଏବଂ ଇନ୍ଦ୍ରିୟ ଉପରେ ବିଜୟ ଲାଭ କରନ୍ତୁ।\n\n⚡ **ଆପଣଙ୍କର ଲାଇଭ୍ ସାଧନା ସ୍ଥିତି**:\n{streak_info}\n\n👇 ନିମ୍ନରୁ ଗୋଟିଏ ବିକଳ୍ପ ଚୟନ କରନ୍ତୁ:"
    },

    "menu_header": {
        "en": "🏛️ **BRAHMACHARYA SANCTUM CONTROL PANEL** 🏛️\n\nChoose an action below to navigate your spiritual journey:",
        "hi": "🏛️ **ब्रह्मचर्य साधना नियंत्रण कक्ष** 🏛️\n\nअपनी साधना को आगे बढ़ाने के लिए नीचे दिया गया विकल्प चुनें:",
        "or": "🏛️ **ବ୍ରହ୍ମଚର୍ଯ୍ୟ ସାଧନା ନିୟନ୍ତ୍ରଣ କକ୍ଷ** 🏛️\n\nଆପଣଙ୍କର ଆଧ୍ୟାତ୍ମିକ ଯାତ୍ରା ପରିଚାଳନା କରିବାକୁ ନିମ୍ନରୁ ବିକଳ୍ପ ବାଛନ୍ତୁ:"
    },

    "streak_tracker": {
        "en": (
            "⚡ **BRAHMACHARYA STREAK TRACKER** ⚡\n"
            "━━━━━━━━━━━━━━━━━━━━━━\n"
            "👤 **Brahmachari**: {name}\n"
            "⏳ **Live Streak**: **{days} Days, {hours}h {minutes}m**\n"
            "🎖️ **Rank**: {rank}\n"
            "📝 **Status**: _{rank_desc}_\n\n"
            "🎯 **Pledge Goal**: {pledge} Days\n"
            "📈 **Progress**: `{progress_bar}`\n\n"
            "🏆 **Personal Record**: {longest} Days\n"
            "⚠️ **Total Relapses**: {relapses}\n"
            "📅 **Started On**: `{start_date}`\n"
            "━━━━━━━━━━━━━━━━━━━━━━\n"
            "💡 *\"The vital fluid (Veerya) when preserved rises up to the brain as Ojas Shakti, providing radiant intelligence and fearlessness.\"* — Swami Sivananda"
        ),
        "hi": (
            "⚡ **ब्रह्मचर्य साधना ट्रैकर (STREAK)** ⚡\n"
            "━━━━━━━━━━━━━━━━━━━━━━\n"
            "👤 **ब्रह्मचारी**: {name}\n"
            "⏳ **सक्रिय साधना**: **{days} दिन, {hours} घंटे {minutes} मिनट**\n"
            "🎖️ **पदवी**: {rank}\n"
            "📝 **स्थिति**: _{rank_desc}_\n\n"
            "🎯 **संकल्प लक्ष्य**: {pledge} दिन\n"
            "📈 **प्रगति**: `{progress_bar}`\n\n"
            "🏆 **सर्वश्रेष्ठ रिकॉर्ड**: {longest} दिन\n"
            "⚠️ **कुल पतन**: {relapses}\n"
            "📅 **प्रारंभ तिथि**: `{start_date}`\n"
            "━━━━━━━━━━━━━━━━━━━━━━\n"
            "💡 *\"सुरक्षित वीर्य मस्तिष्क में ओजस शक्ति बनकर ऊपर उठता है, जिससे अद्वितीय मेधा और निर्भयता प्राप्त होती है।\"* — स्वामी शिवानंद"
        ),
        "or": (
            "⚡ **ବ୍ରହ୍ମଚର୍ଯ୍ୟ ସାଧନା ଟ୍ରାକର୍ (STREAK)** ⚡\n"
            "━━━━━━━━━━━━━━━━━━━━━━\n"
            "👤 **ବ୍ରହ୍ମଚାରୀ**: {name}\n"
            "⏳ **ସକ୍ରିୟ ସାଧନା**: **{days} ଦିନ, {hours} ଘଣ୍ଟା {minutes} ମିନିଟ୍**\n"
            "🎖️ **ପଦବୀ**: {rank}\n"
            "📝 **ସ୍ଥିତି**: _{rank_desc}_\n\n"
            "🎯 **ସଂକଳ୍ପ ଲକ୍ଷ୍ୟ**: {pledge} ଦିନ\n"
            "📈 **ପ୍ରଗତି**: `{progress_bar}`\n\n"
            "🏆 **ସର୍ବୋତ୍ତମ ରେକର୍ଡ**: {longest} ଦିନ\n"
            "⚠️ **ମୋଟ ପତନ (Relapses)**: {relapses}\n"
            "📅 **ଆରମ୍ଭ ତାରିଖ**: `{start_date}`\n"
            "━━━━━━━━━━━━━━━━━━━━━━\n"
            "💡 *\"ସଂରକ୍ଷିତ ବୀର୍ଯ୍ୟ ଶକ୍ତି ମସ୍ତିଷ୍କକୁ ଓଜ ଶକ୍ତି ଭାବରେ ପ୍ରବାହିତ ହୋଇ ଦିବ୍ୟ ବୁଦ୍ଧି ଏବଂ ନିର୍ଭୟତା ପ୍ରଦାନ କରେ।\"* — ସ୍ୱାମୀ ଶିବାନନ୍ଦ"
        )
    },

    "mindset_text": {
        "en": (
            "🧘 **BRAHMACHARYA MINDSET & OJAS TRANSMUTATION** 🧘\n"
            "━━━━━━━━━━━━━━━━━━━━━━\n"
            "Sexual energy is the most concentrated creative force in the universe. Do not suppress it; **TRANSMUTE** it into intellectual brilliance, physical strength, and spiritual magnetism.\n\n"
            "🔱 **The 3 Pillars of Mind Control**:\n"
            "1. **Pranayama (Breath Control)**:\n"
            "   • *Anulom Vilom (Alternate Nostril)*: 15 mins daily calms the central nervous system.\n"
            "   • *Kapalabhati & Bhastrika*: Generates internal fire and clears lethargy.\n"
            "   • *Moola Bandha & Uddiyana Bandha*: Directs seminal energy upwards toward Sahasrara.\n\n"
            "2. **The 10-Minute Urge Rule**:\n"
            "   • When a strong craving hits, do NOT fight it mentally.\n"
            "   • Immediately drop down and do 25 pushups, or wash your face with ice-cold water.\n"
            "   • Observe the craving like an ocean wave—it peaks in 10 minutes and dissolves.\n\n"
            "3. **Drishti Shuddhi (Sight Purification)**:\n"
            "   • What enters the eyes becomes thought, and thought triggers action.\n"
            "   • Practice *Trataka* (gazing at a ghee lamp flame for 5 mins) to build razor-sharp focus.\n"
            "━━━━━━━━━━━━━━━━━━━━━━"
        ),
        "hi": (
            "🧘 **ब्रह्मचर्य मनोबल एवं ओजस रूपांतरण** 🧘\n"
            "━━━━━━━━━━━━━━━━━━━━━━\n"
            "कामुक ऊर्जा ब्रह्मांड की सबसे शक्तिशाली रचनात्मक ऊर्जा है। इसे दबाइए मत; इसे बौद्धिक प्रखरता, शारीरिक बल और आध्यात्मिक तेज में **रूपांतरित (Transmute)** कीजिए।\n\n"
            "🔱 **मन पर नियंत्रण के ३ मुख्य स्तंभ**:\n"
            "1. **प्राणायाम (श्वास नियंत्रण)**:\n"
            "   • *अनुलोम विलोम*: प्रतिदिन १५ मिनट करने से तंत्रिका तंत्र शांत होता है।\n"
            "   • *कपालभाति एवं भस्त्रिका*: आलस्य को नष्ट कर आंतरिक अग्नि जाग्रत करता है।\n"
            "   • *मूल बंध एवं उड्डियान बंध*: वीर्य ऊर्जा को सहस्रार की ओर उर्ध्वमुख करता है।\n\n"
            "2. **१०-मिनट वासना नियम (10-Minute Rule)**:\n"
            "   • जब तीव्र वासना आए, तो मानसिक द्वंद्व मत करें।\n"
            "   • तुरंत २५ दंड लगाएं या बर्फ जैसे ठंडे पानी से मुँह धोएं।\n"
            "   • वासना को समुद्र की लहर समझें—यह १० मिनट में शांत हो जाएगी।\n\n"
            "3. **दृष्टि शुद्धि**:\n"
            "   • जो आँखों से भीतर जाता है, वही विचार बनता है और वही कर्म में बदलता है।\n"
            "   • दीपक की लौ पर त्राटक का अभ्यास करें जिससे एकाग्रता अचूक बने।\n"
            "━━━━━━━━━━━━━━━━━━━━━━"
        ),
        "or": (
            "🧘 **ବ୍ରହ୍ମଚର୍ଯ୍ୟ ମନୋବଳ ଏବଂ ଓଜ ଶକ୍ତି ରୂପାନ୍ତରଣ** 🧘\n"
            "━━━━━━━━━━━━━━━━━━━━━━\n"
            "କାମ ଶକ୍ତି ବ୍ରହ୍ମାଣ୍ଡର ସବୁଠାରୁ ଶକ୍ତିଶାଳୀ ସୃଜନଶୀଳ ଶକ୍ତି। ଏହାକୁ ଦବାନ୍ତୁ ନାହିଁ; ଏହାକୁ ବୌଦ୍ଧିକ ତେଜ, ଶାରୀରିକ ବଳ ଏବଂ ଆଧ୍ୟାତ୍ମିକ ଶକ୍ତିରେ **ରୂପାନ୍ତରିତ** କରନ୍ତୁ।\n\n"
            "🔱 **ମନ ନିୟନ୍ତ୍ରଣର ୩ଟି ମୁଖ୍ୟ ସ୍ତମ୍ଭ**:\n"
            "1. **ପ୍ରାଣାୟାମ**:\n"
            "   • *ଅନୁଲୋମ ବିଲୋମ*: ପ୍ରତିଦିନ ୧୫ ମିନିଟ୍ ସ୍ନାୟୁ ମଣ୍ଡଳକୁ ଶାନ୍ତ ରଖେ।\n"
            "   • *କପାଳଭାତି ଓ ଭସ୍ତ୍ରିକା*: ଅଳସ୍ୟ ଦୂର କରି ଆଭ୍ୟନ୍ତରୀଣ ଶକ୍ତି ଜାଗ୍ରତ କରେ।\n"
            "   • *ମୂଳ ବନ୍ଧ ଓ ଉଡ୍ଡୀୟାନ ବନ୍ଧ*: ବୀର୍ଯ୍ୟ ଶକ୍ତିକୁ ଉପରକୁ ଉର୍ଦ୍ଧ୍ୱଗାମୀ କରାଏ।\n\n"
            "2. **୧୦ ମିନିଟ୍ ଉତ୍ତେଜନା ନିୟମ**:\n"
            "   • ଯେତେବେଳେ ତୀବ୍ର ଇଚ୍ଛା ଆସେ, ମନରେ ଯୁଦ୍ଧ ନକରି ତୁରନ୍ତ ୨୫ଟି ପୁଶ-ଅପ୍ କରନ୍ତୁ କିମ୍ବା ଥଣ୍ଡା ପାଣିରେ ମୁହଁ ଧୁଅନ୍ତୁ।\n"
            "   • ତରଙ୍ଗ ଭଳି ଏହା ୧୦ ମିନିଟ୍ ମଧ୍ୟରେ ଶାନ୍ତ ହୋଇଯିବ।\n\n"
            "3. **ଦୃଷ୍ଟି ଶୁଦ୍ଧି**:\n"
            "   • ଆଖି ଯାହା ଦେଖେ, ତାହା ଭାବନାରେ ପରିଣତ ହୁଏ। କୁଦୃଷ୍ଟିରୁ ସର୍ବଦା ଦୂରେଇ ରୁହନ୍ତୁ।\n"
            "━━━━━━━━━━━━━━━━━━━━━━"
        )
    },

    "workout_text": {
        "en": (
            "⚔️ **BRAHMACHARI PHYSICAL STRENGTH & VYAYAM GUIDE** ⚔️\n"
            "━━━━━━━━━━━━━━━━━━━━━━\n"
            "A weak body cannot sustain powerful Ojas. Build iron endurance with traditional Bharatiya Vyayam:\n\n"
            "☀️ **Morning Sadhana (4:30 AM - 6:00 AM)**:\n"
            "1. **Surya Namaskar (12-24 Rounds)**:\n"
            "   • Complete spinal flexibility, activates endocrine glands and solar plexus.\n\n"
            "2. **Desi Dands (Hindu Push-Ups) — 50-100 Reps**:\n"
            "   • Builds upper body armor, core fortitude, and shoulder strength.\n\n"
            "3. **Desi Baithaks (Hindu Squats) — 100-200 Reps**:\n"
            "   • Strengthens legs, pelvic floor, and increases natural testosterone.\n\n"
            "4. **Inversions (Shirshasana & Sarvangasana) — 5-10 Mins**:\n"
            "   • Pulls seminal energy upwards to nourish the brain.\n\n"
            "💪 *\"You will be nearer to Heaven through football than through the study of the Gita.\"* — Swami Vivekananda"
        ),
        "hi": (
            "⚔️ **ब्रह्मचारी शारीरिक बल एवं व्यायाम साधना** ⚔️\n"
            "━━━━━━━━━━━━━━━━━━━━━━\n"
            "एक दुर्बल शरीर कभी भी प्रचंड ओजस को धारण नहीं कर सकता। पारंपरिक भारतीय व्यायाम से लौह शरीर का निर्माण करें:\n\n"
            "☀️ **प्रातःकालीन साधना (प्रातः 4:30 - 6:00)**:\n"
            "1. **सूर्य नमस्कार (12-24 चक्र)**:\n"
            "   • रीढ़ की हड्डी में लचीलापन लाता है और सौर चक्र को जाग्रत करता है।\n\n"
            "2. **देसी दंड (Hindu Push-Ups) — 50-100 बार**:\n"
            "   • सीना, कंधे और भुजाओं को वज्र के समान सुदृढ़ बनाता है।\n\n"
            "3. **देसी बैठक (Hindu Squats) — 100-200 बार**:\n"
            "   • पैरों, पेल्विक फ्लोर को मजबूत कर टेस्टोस्टेरोन को प्राकृतिक रूप से बढ़ाता है।\n\n"
            "4. **शीर्षासन एवं सर्वांगासन — 5-10 मिनट**:\n"
            "   • ऊर्जा को उर्ध्वगामी बनाकर मस्तिष्क की कोशिकाओं को पोषण देता है।\n\n"
            "💪 *\"गीता पढ़ने की अपेक्षा फुटबॉल खेलने से तुम स्वर्ग के अधिक निकट होगे।\"* — स्वामी विवेकानंद"
        ),
        "or": (
            "⚔️ **ବ୍ରହ୍ମଚାରୀ ଶାରୀରିକ ବଳ ଏବଂ ବ୍ୟାୟାମ ମାର୍ଗଦର୍ଶିକା** ⚔️\n"
            "━━━━━━━━━━━━━━━━━━━━━━\n"
            "ଗୋଟିଏ ଦୁର୍ବଳ ଶରୀର କଦାପି ପ୍ରଚଣ୍ଡ ଓଜ ଶକ୍ତି ଧାରଣ କରିପାରିବ ନାହିଁ। ପାରମ୍ପରିକ ଭାରତୀୟ ବ୍ୟାୟାମ ଦ୍ୱାରା ବଜ୍ର ଶରୀର ଗଠନ କରନ୍ତୁ:\n\n"
            "☀️ **ପ୍ରାତଃକାଳୀନ ସାଧନା (୪:୩୦ - ୬:୦୦ AM)**:\n"
            "1. **ସୂର୍ଯ୍ୟ ନମସ୍କାର (୧୨-୨୪ ଚକ୍ର)**:\n"
            "   • ମେରୁଦଣ୍ଡକୁ ସୁଦୃଢ଼ କରେ ଏବଂ ସମଗ୍ର ଶରୀରକୁ ସକ୍ରିୟ କରେ।\n\n"
            "2. **ଦେଶୀ ଦଣ୍ଡ (Hindu Push-Ups) — ୫୦-୧୦୦ ଥର**:\n"
            "   • ଛାତି, ବାହୁ ଏବଂ କାନ୍ଧକୁ ଲୁହା ଭଳି ଶକ୍ତ କରେ।\n\n"
            "3. **ଦେଶୀ ବୈଠକ (Hindu Squats) — ୧୦୦-୨୦୦ ଥର**:\n"
            "   • ଗୋଡ଼କୁ ଶକ୍ତିଶାଳୀ କରେ ଏବଂ ସ୍ୱାଭାବିକ ଶକ୍ତି ବୃଦ୍ଧି କରେ।\n\n"
            "4. **ଶୀର୍ଷାସନ ଓ ସର୍ବାଙ୍ଗାସନ — ୫-୧୦ ମିନିଟ୍**:\n"
            "   • ଶକ୍ତିକୁ ଉର୍ଦ୍ଧ୍ୱମୁଖୀ କରି ମସ୍ତିଷ୍କକୁ ତେଜସ୍ୱୀ କରେ।\n\n"
            "💪 *\"ଶରୀରକୁ ବଳବାନ କରନ୍ତୁ, ଆପଣଙ୍କ ମନ ସ୍ୱତଃ ଶକ୍ତିଶାଳୀ ହେବ।\"* — ସ୍ୱାମୀ ବିବେକାନନ୍ଦ"
        )
    },

    "health_text": {
        "en": (
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
            "• Excess chilies, garlic, onion, deep-fried junk food\n"
            "• Artificial sugars, energy drinks, alcohol, smoking\n"
            "• Late-night eating (dinner must be 3 hours before sleep)\n\n"
            "❄️ **Cold Shower Therapy (Snana)**:\n"
            "• Cold water bath immediately cools the genital nervous center and resets dopamine receptors."
        ),
        "hi": (
            "🥗 **सात्विक आहार एवं आयुर्वेदिक स्वास्थ्य नियम** 🥗\n"
            "━━━━━━━━━━━━━━━━━━━━━━\n"
            "आहार से ही मन का निर्माण होता है (*आहार शुद्धौ सत्त्व शुद्धिः*)।\n\n"
            "✅ **क्या खाएं (ओजस बढ़ाने वाले सात्विक पदार्थ)**:\n"
            "• भीगे हुए बादाम, अखरोट और मुनक्का\n"
            "• देसी गाय का दूध (अश्वगंधा एवं इलायची के साथ)\n"
            "• ताजे मौसमी फल (सेब, अनार, केला)\n"
            "• शुद्ध देसी घी, हरी सब्जियां, मूंग दाल, अंकुरित अनाज\n"
            "• तांबे के पात्र का जल\n\n"
            "🚫 **किसका त्याग करें (तामसिक एवं राजसिक)**:\n"
            "• अत्यधिक मिर्च-मसाला, लहसुन, प्याज, तला-भुना भोजन\n"
            "• डिब्बाबंद मीठा, कोल्ड ड्रिंक, शराब, धूम्रपान\n"
            "• देर रात भोजन करना (सोने से ३ घंटे पहले भोजन करें)\n\n"
            "❄️ **शीतल जल स्नान (Cold Shower)**:\n"
            "• ठंडे पानी से स्नान करने से कामुक आवेग तुरंत शांत हो जाते हैं।"
        ),
        "or": (
            "🥗 **ସାତ୍ତ୍ୱିକ ଆହାର ଏବଂ ଆୟୁର୍ବେଦିକ ସ୍ୱାସ୍ଥ୍ୟ ନିୟମ** 🥗\n"
            "━━━━━━━━━━━━━━━━━━━━━━\n"
            "ଆହାରରୁ ହିଁ ମନର ଗଠନ ହୁଏ (*ଆହାର ଶୁଦ୍ଧୌ ସତ୍ତ୍ୱ ଶୁଦ୍ଧିଃ*)।\n\n"
            "✅ **କ’ଣ ଖାଇବେ (ଓଜ ଶକ୍ତି ବୃଦ୍ଧିକାରୀ ସାତ୍ତ୍ୱିକ ଖାଦ୍ୟ)**:\n"
            "• ଭିଜା ବାଦାମ, ଅଖରୋଟ ଏବଂ କିସମିସ୍\n"
            "• ଗାଈ କ୍ଷୀର, ଅଶ୍ୱଗନ୍ଧା ଓ ଅଳେଇଚ\n"
            "• ସତେଜ ଋତୁକାଳୀନ ଫଳ (ସେଓ, ଡାଳିମ୍ବ, କଦଳୀ)\n"
            "• ଶୁଦ୍ଧ ଘିଅ, ଶାଗ-ପନିପରିବା, ମୁଗ ଡାଲି ଓ ଗଜା ମୁଗ\n"
            "• ତମ୍ବା ପାତ୍ରରେ ରଖାଯାଇଥିବା ଜଳ\n"
            "\n🚫 **କ’ଣ ବର୍ଜନ କରିବେ (ତାମସିକ ଖାଦ୍ୟ)**:\n"
            "• ଅତ୍ୟଧିକ ଲଙ୍କା, ପିଆଜ, ରସୁଣ, ତେଲ ଛଣା ଖାଦ୍ୟ\n"
            "• ମଦ୍ୟପାନ, ଧୂମପାନ ଓ ରାତ୍ରୀ ବିଳମ୍ବରେ ଭୋଜନ\n\n"
            "❄️ **ଥଣ୍ଡା ପାଣିରେ ସ୍ନାନ (Cold Shower)**:\n"
            "• ଥଣ୍ଡା ପାଣିରେ ଗାଧୋଇବା ଦ୍ୱାରା ମନ ଶାନ୍ତ ହୁଏ ଏବଂ କାମନା ନଷ୍ଟ ହୁଏ।"
        )
    },

    "quotes_text": {
        "en": (
            "📜 **SACRED SHLOKAS & MOTIVATIONAL WISDOM** 📜\n"
            "━━━━━━━━━━━━━━━━━━━━━━\n"
            "📖 **Bhagavad Gita (Chapter 2, Verse 62-63)**:\n"
            "ध्यायतो विषयान्पुंसः सङ्गस्तेषूपजायते।\n"
            "सङ्गात्संजायते कामः कामात्क्रोधोऽभिजायते॥\n"
            "_\"Contemplating sensory objects leads to attachment; attachment breeds lust, and frustrated lust breeds anger.\"_\n\n"
            "📖 **Swami Vivekananda**:\n"
            "_\"Every youth should be trained in Brahmacharya; only then can there be built up in him the tremendous power of head and heart.\"_\n\n"
            "📖 **Patanjali Yoga Sutras (2.38)**:\n"
            "ब्रह्मचर्यप्रतिष्ठायां वीर्यलाभः॥\n"
            "_\"Upon establishment in Brahmacharya, unyielding vitality and divine potency are acquired.\"_\n\n"
            "📖 **Chanakya Neeti**:\n"
            "_\"He who controls his senses rules over the entire kingdom of destiny.\"_\n"
            "━━━━━━━━━━━━━━━━━━━━━━"
        ),
        "hi": (
            "📜 **दिव्य श्लोक एवं प्रेरणादायी सद्वाक्य** 📜\n"
            "━━━━━━━━━━━━━━━━━━━━━━\n"
            "📖 **श्रीमद्भगवद्गीता (अध्याय २, श्लोक ६२-६३)**:\n"
            "ध्यायतो विषयान्पुंसः सङ्गस्तेषूपजायते।\n"
            "सङ्गात्संजायते कामः कामात्क्रोधोऽभिजायते॥\n"
            "_\"विषयों का ध्यान करने से उनमें आसक्ति होती है; आसक्ति से काम (वासना) उत्पन्न होती है और वासना में बाधा आने पर क्रोध उत्पन्न होता है।\"_\n\n"
            "📖 **स्वामी विवेकानंद**:\n"
            "_\"प्रत्येक युवक को ब्रह्मचर्य का अभ्यास करना चाहिए; तभी उसके मस्तिष्क और हृदय में प्रचंड शक्ति का संचार हो सकता है।\"_\n\n"
            "📖 **पतंजलि योगसूत्र (२.३୮)**:\n"
            "ब्रह्मचर्यप्रतिष्ठायां वीर्यलाभः॥\n"
            "_\"ब्रह्मचर्य में प्रतिष्ठित होने पर अपार वीर्य और आत्मबल की प्राप्ति होती है।\"_\n\n"
            "📖 **चाणक्य नीति**:\n"
            "_\"जिसने अपनी इंद्रियों को वश में कर लिया, वह पूरे भाग्य का स्वामी बन जाता है।\"_\n"
            "━━━━━━━━━━━━━━━━━━━━━━"
        ),
        "or": (
            "📜 **ପବିତ୍ର ଶ୍ଳୋକ ଏବଂ ପ୍ରେରଣାଦାୟୀ ବାଣୀ** 📜\n"
            "━━━━━━━━━━━━━━━━━━━━━━\n"
            "📖 **ଶ୍ରୀମଦ୍ଭଗବଦ୍ଗୀତା (୨.୬୨-୬୩)**:\n"
            "ध्यायतो विषयान्पुंसः सङ्गस्तेषूपजायते।\n"
            "सङ्गात्संजायते कामः कामात्क्रोधोऽभिजायते॥\n"
            "_\"ଭୋଗ ବିଷୟ ଚିନ୍ତା କରିବା ଦ୍ୱାରା ଆସକ୍ତି ଜନ୍ମେ, ଆସକ୍ତିରୁ କାମନା ଏବଂ କାମନାରୁ କ୍ରୋଧ ଉତ୍ପନ୍ନ ହୁଏ।\"_\n\n"
            "📖 **ସ୍ୱାମୀ ବିବେକାନନ୍ଦ**:\n"
            "_\"ପ୍ରତ୍ୟେକ ଯୁବକ ବ୍ରହ୍ମଚର୍ଯ୍ୟ ପାଳନ କରିବା ଉଚିତ; ତେବେ ଯାଇ ତାହାଙ୍କ ଭିତରେ ଅସୀମ ଆତ୍ମବଳ ଓ ବୁଦ୍ଧି ଜାଗ୍ରତ ହେବ।\"_\n\n"
            "📖 **ପତଞ୍ଜଳି ଯୋଗସୂତ୍ର (୨.୩୮)**:\n"
            "ब्रह्मचर्यप्रतिष्ठायां वीर्यलाभः॥\n"
            "_\"ବ୍ରହ୍ମଚର୍ଯ୍ୟ ପ୍ରତିଷ୍ଠା ହେଲେ ଅକ୍ଷୟ ଶକ୍ତି ଏବଂ ଦିବ୍ୟ ବୀର୍ଯ୍ୟ ପ୍ରାପ୍ତ ହୁଏ।\"_\n\n"
            "📖 **ଚାଣକ୍ୟ ନୀତି**:\n"
            "_\"ଯିଏ ଇନ୍ଦ୍ରିୟକୁ ଜୟ କରେ, ସେ ଭାଗ୍ୟର ମାଲିକ ପାଲଟେ।\"_\n"
            "━━━━━━━━━━━━━━━━━━━━━━"
        )
    },

    "books_header": {
        "en": "📚 **SACRED BRAHMACHARYA BOOKS** 📚\n━━━━━━━━━━━━━━━━━━━━━━\nThe following spiritual texts and guides are available.\n\n👇 **Tap any book below to receive it directly:**",
        "hi": "📚 **पवित्र ब्रह्मचर्य साहित्य एवं पुस्तकें** 📚\n━━━━━━━━━━━━━━━━━━━━━━\nनिम्नलिखित आध्यात्मिक ग्रंथ एवं पुस्तकें उपलब्ध हैं।\n\n👇 **किसी भी पुस्तक पर टैप करके उसे तुरंत प्राप्त करें:**",
        "or": "📚 **ପବିତ୍ର ବ୍ରହ୍ମଚର୍ଯ୍ୟ ପୁସ୍ତକାବଳୀ** 📚\n━━━━━━━━━━━━━━━━━━━━━━\nନିମ୍ନଲିଖିତ ପବିତ୍ର ଗ୍ରନ୍ଥ ଏବଂ ପୁସ୍ତକ ଉପଲବ୍ଧ ଅଛି।\n\n👇 **ନିମ୍ନରୁ ଯେକୌଣସି ପୁସ୍ତକ ଚୟନ କରି ଡାଉନଲୋଡ୍ କରନ୍ତୁ:**"
    },

    "songs_header": {
        "en": "🎵 **SACRED AUDIO, BHAJANS & CHANTS** 🎵\n━━━━━━━━━━━━━━━━━━━━━━\nThe following high-vibration chants and audio tracks are available.\n\n👇 **Tap any track below to receive it directly:**",
        "hi": "🎵 **पवित्र भजन, मंत्र एवं वैदिक संगीत** 🎵\n━━━━━━━━━━━━━━━━━━━━━━\nनिम्नलिखित दिव्य मंत्र एवं भजन उपलब्ध हैं।\n\n👇 **किसी भी भजन या मंत्र पर टैप करके तुरंत प्राप्त करें:**",
        "or": "🎵 **ପବିତ୍ର ଭଜନ, ମନ୍ତ୍ର ଏବଂ ସଙ୍ଗୀତ** 🎵\n━━━━━━━━━━━━━━━━━━━━━━\nନିମ୍ନଲିଖିତ ଦିବ୍ୟ ଭଜନ ଓ ମନ୍ତ୍ର ଉପଲବ୍ଧ ଅଛି।\n\n👇 **ନିମ୍ନରୁ ଯେକୌଣସି ଟ୍ରାକ୍ ଚୟନ କରି ଶ୍ରବଣ କରନ୍ତୁ:**"
    },

    "challenge_text": {
        "en": "🎯 **SELECT YOUR SANKALP / PLEDGE TARGET** 🎯\n\nYour current pledge: **{pledge} Days**\n\nChoose a milestone below to set your sacred vow:",
        "hi": "🎯 **अपना संकल्प / प्रतिज्ञा लक्ष्य चुनें** 🎯\n\nआपका वर्तमान लक्ष्य: **{pledge} दिन**\n\nनीचे दिए गए मील के पत्थरों में से अपना पवित्र संकल्प चुनें:",
        "or": "🎯 **ଆପଣଙ୍କର ସଂକଳ୍ପ ଲକ୍ଷ୍ୟ ଚୟନ କରନ୍ତୁ** 🎯\n\nଆପଣଙ୍କର ବର୍ତ୍ତମାନର ଲକ୍ଷ୍ୟ: **{pledge} ଦିନ**\n\nନିମ୍ନରୁ ଗୋଟିଏ ପବିତ୍ର ସଂକଳ୍ପ ବାଛନ୍ତୁ:"
    },

    "challenge_confirmed": {
        "en": "✅ **Sankalp Confirmed!**\n\nYour target pledge has been set to **{days} Days**.\nStay focused, disciplined, and steadfast on the path of Brahmacharya! 🕉️",
        "hi": "✅ **संकल्प स्वीकार हुआ!**\n\nआपका प्रतिज्ञा लक्ष्य **{days} दिन** पर निर्धारित कर दिया गया है।\nब्रह्मचर्य के पथ पर दृढ़, अनुशासित और अडिग रहें! 🕉️",
        "or": "✅ **ସଂକଳ୍ପ ସ୍ୱୀକୃତ ହେଲା!**\n\nଆପଣଙ୍କର ଲକ୍ଷ୍ୟ **{days} ଦିନ** ନିର୍ଦ୍ଧାରିତ କରାଗଲା।\nବ୍ରହ୍ମଚର୍ଯ୍ୟ ପଥରେ ଏକାଗ୍ର ଓ ନିଷ୍ଠାବାନ ରୁହନ୍ତୁ! 🕉️"
    },

    "relapse_prompt": {
        "en": "⚠️ **RELAPSE CONFIRMATION** ⚠️\n\nBrother, are you sure you want to log a relapse and reset your streak?\n\nRemember: A setback is only permanent if you give up. Honesty is the foundation of true character.",
        "hi": "⚠️ **पतन पुष्टि (Relapse Confirmation)** ⚠️\n\nप्रिय भाई, क्या आप सच में पतन दर्ज करके अपनी साधना (Streak) रीसेट करना चाहते हैं?\n\nयाद रखें: भूल तभी स्थायी होती है जब आप हार मान लें। ईमानदारी ही चरित्र का आधार है।",
        "or": "⚠️ **ପତନ ନିଶ୍ଚିତକରଣ (Relapse Confirmation)** ⚠️\n\nଭାଇ, ଆପଣ ପ୍ରକୃତରେ ପତନ ଲଗ୍ କରି ନିଜର ଷ୍ଟ୍ରିକ୍ ରିସେଟ୍ କରିବାକୁ ଚାହାଁନ୍ତି କି?\n\nମନେରଖନ୍ତୁ: ଭୁଲ୍ ସେତେବେଳେ ସ୍ଥାୟୀ ହୁଏ ଯେତେବେଳେ ଆପଣ ହାର୍ ମାନିଯାଆନ୍ତି। ସଚ୍ଚୋଟତା ହିଁ ଚରିତ୍ରର ମୂଳଦୁଆ।"
    },

    "relapse_reset_recovery": {
        "en": (
            "🔄 **STREAK RESET TO DAY 0** 🔄\n"
            "━━━━━━━━━━━━━━━━━━━━━━\n"
            "Previous Streak: **{ended_days} Days**\n\n"
            "🙏 **Do not despair!** Rise immediately:\n"
            "1. Take a cold shower right now.\n"
            "2. Perform 10 minutes of Anulom Vilom.\n"
            "3. Note down the trigger that caused this slip, and destroy that habit loop.\n\n"
            "🔥 *\"Arise, awake, and stop not till the goal is reached!\"* — Swami Vivekananda"
        ),
        "hi": (
            "🔄 **साधना रीसेट — दिन 0** 🔄\n"
            "━━━━━━━━━━━━━━━━━━━━━━\n"
            "पिछली साधना: **{ended_days} दिन**\n\n"
            "🙏 **निराश मत हों!** तुरंत खड़े हों:\n"
            "1. अभी ठंडे पानी से स्नान करें।\n"
            "2. १० मिनट अनुलोम-विलोम प्राणायाम करें।\n"
            "3. जिस कारण से पतन हुआ, उसे पहचानें और उस आदत को जड़ से मिटाएं।\n\n"
            "🔥 *\"उठो, जागो और तब तक मत रुको जब तक लक्ष्य प्राप्त न हो जाए!\"* — स्वामी विवेकानंद"
        ),
        "or": (
            "🔄 **ସାଧନା ରିସେଟ୍ — ଦିନ ୦** 🔄\n"
            "━━━━━━━━━━━━━━━━━━━━━━\n"
            "ପୂର୍ବ ସାଧନା: **{ended_days} ଦିନ**\n\n"
            "🙏 **ହତାଶ ହୁଅନ୍ତୁ ନାହିଁ!** ପୁନର୍ବାର ଉଠନ୍ତୁ:\n"
            "1. ବର୍ତ୍ତମାନ ଥଣ୍ଡା ପାଣିରେ ଗାଧୋଇ ପଡ଼ନ୍ତୁ।\n"
            "2. ୧୦ ମିନିଟ୍ ଅନୁଲୋମ-ବିଲୋମ ପ୍ରାଣାୟାମ କରନ୍ତୁ।\n"
            "3. କେଉଁ କାରଣରୁ ଏହି ଭୁଲ୍ ହେଲା, ତାହା ଚିହ୍ନଟ କରନ୍ତୁ ଏବଂ ସେହି କୁଅଭ୍ୟାସକୁ ନଷ୍ଟ କରନ୍ତୁ।\n\n"
            "🔥 *\"ଉଠ, ଜାଗ୍ରତ ହୁଅ ଏବଂ ଲକ୍ଷ୍ୟ ହାସଲ ନହେବା ପର୍ଯ୍ୟନ୍ତ ଅଟକ ନାହିଁ!\"* — ସ୍ୱାମୀ ବିବେକାନନ୍ଦ"
        )
    },

    "leaderboard_header": {
        "en": "🏆 **BRAHMACHARYA LEADERBOARD (TOP SADHAKS)** 🏆\n━━━━━━━━━━━━━━━━━━━━━━\n",
        "hi": "🏆 **ब्रह्मचर्य लीडरबोर्ड (शीर्ष साधक)** 🏆\n━━━━━━━━━━━━━━━━━━━━━━\n",
        "or": "🏆 **ବ୍ରହ୍ମଚର୍ଯ୍ୟ ଲିଡରବୋର୍ଡ (ଶ୍ରେଷ୍ଠ ସାଧକ)** 🏆\n━━━━━━━━━━━━━━━━━━━━━━\n"
    },

    "leaderboard_empty": {
        "en": "🏆 No streaks recorded yet. Be the first to start!",
        "hi": "🏆 अभी तक कोई साधना दर्ज नहीं हुई है। पहले साधक बनें!",
        "or": "🏆 ଏପର୍ଯ୍ୟନ୍ତ କୌଣସି ସାଧନା ଲିପିବଦ୍ଧ ହୋଇନାହିଁ। ପ୍ରଥମେ ଆରମ୍ଭ କରନ୍ତୁ!"
    },

    "leaderboard_footer": {
        "en": "\n━━━━━━━━━━━━━━━━━━━━━━\n💡 *\"Purity is supreme strength. Keep moving forward!\"*",
        "hi": "\n━━━━━━━━━━━━━━━━━━━━━━\n💡 *\"पवित्रता ही परम शक्ति है। आगे बढ़ते रहें!\"*",
        "or": "\n━━━━━━━━━━━━━━━━━━━━━━\n💡 *\"ପବିତ୍ରତା ହିଁ ପରମ ଶକ୍ତି। ଆଗକୁ ବଢ଼ନ୍ତୁ!\"*"
    },

    "motivation_text": {
        "en": (
            "⚡ **INSTANT MOTIVATION & VICTORY MINDSET** ⚡\n"
            "━━━━━━━━━━━━━━━━━━━━━━\n"
            "🔥 *\"Do not look back, look forward! Infinite energy, infinite enthusiasm, infinite daring, and infinite patience — then alone can great things be accomplished!\"* — Swami Vivekananda\n\n"
            "🛡️ **Remember Why You Began**:\n"
            "• 5 seconds of cheap pixel dopamine vs. a lifetime of supreme confidence, mental clarity, and spiritual brilliance.\n"
            "• Every urge you overcome directly elevates your testosterone, sharpens your eyesight, and strengthens your nervous system.\n"
            "• You are not a slave to biological impulses. You are the master of your destiny."
        ),
        "hi": (
            "⚡ **तात्कालिक प्रेरणा एवं विजय संकल्प** ⚡\n"
            "━━━━━━━━━━━━━━━━━━━━━━\n"
            "🔥 *\"पीछे मत देखो, आगे देखो! अनंत ऊर्जा, अनंत उत्साह, अनंत साहस और अनंत धैर्य — केवल तभी महान कार्य संभव हैं!\"* — स्वामी विवेकानंद\n\n"
            "🛡️ **याद रखें आपने क्यों शुरू किया था**:\n"
            "• ५ सेकंड का क्षणिक डोपामाइन बनाम जीवनभर का आत्मविश्वास, मानसिक स्पष्टता और आध्यात्मिक तेज।\n"
            "• वासना पर आपकी हर विजय आपके पुरुषार्थ और आत्मबल को सुदृढ़ बनाती है।\n"
            "• आप इंद्रियों के दास नहीं हैं; आप अपने भाग्य के स्वामी हैं।"
        ),
        "or": (
            "⚡ **ତତ୍କାଳ ପ୍ରେରଣା ଏବଂ ବିଜୟୀ ମନୋଭାବ** ⚡\n"
            "━━━━━━━━━━━━━━━━━━━━━━\n"
            "🔥 *\"ପଛକୁ ଚାହାଁନ୍ତୁ ନାହିଁ, ଆଗକୁ ବଢ଼ନ୍ତୁ! ଅନନ୍ତ ଶକ୍ତି, ଅନନ୍ତ ଉତ୍ସାହ ଏବଂ ଅନନ୍ତ ଧୈର୍ଯ୍ୟ ହିଁ ମହାନ କାର୍ଯ୍ୟ ସାଧନ କରିପାରିବ!\"* — ସ୍ୱାମୀ ବିବେକାନନ୍ଦ\n\n"
            "🛡️ **ମନେପକାନ୍ତୁ ଆପଣ କାହିଁକି ଆରମ୍ଭ କରିଥିଲେ**:\n"
            "• କିଛି ସେକେଣ୍ଡର ତୁଚ୍ଛ ଉତ୍ତେଜନା ବନାମ ଆଜୀବନର ଆତ୍ମବିଶ୍ୱାସ, ସ୍ପଷ୍ଟ ଚିନ୍ତାଧାରା ଏବଂ ଦିବ୍ୟ ଶକ୍ତି।\n"
            "• ଆପଣ କୌଣସି ବାସନାର ଦାସ ନୁହଁନ୍ତି; ଆପଣ ନିଜ ଭାଗ୍ୟର ବିଧାତା।"
        )
    },

    "help_text": {
        "en": (
            "📖 **BRAHMACHARYA BOT GUIDE & COMMANDS** 📖\n"
            "━━━━━━━━━━━━━━━━━━━━━━\n"
            "⚡ `/start` - Launch sanctum & view live progress\n"
            "🏛️ `/menu` - Open interactive control panel\n"
            "📊 `/streak` - Check current live streak & rank\n"
            "🏆 `/leaderboard` - View top disciplined sadhaks\n"
            "🔄 `/relapse` - Log a slip and reset journey\n"
            "🎯 `/challenge` - Set your commitment pledge target\n"
            "🧘 `/mindset` - Ojas transmutation & mind mastery\n"
            "⚔️ `/workout` - Traditional physical conditioning\n"
            "🥗 `/health` - Sattvic diet & cold shower regimen\n"
            "📜 `/quotes` - Sacred shlokas & motivational wisdom\n"
            "📚 `/books` - Access divine spiritual literature\n"
            "🎵 `/songs` - Access devotional chants & tracks\n"
            "⚡ `/motivation` - Instant urge killer & motivation\n"
            "🌐 `/language` - Change language (English, Hindi, Odia)"
        ),
        "hi": (
            "📖 **ब्रह्मचर्य बॉट मार्गदर्शिका एवं कमांड्स** 📖\n"
            "━━━━━━━━━━━━━━━━━━━━━━\n"
            "⚡ `/start` - साधना केंद्र प्रारंभ करें\n"
            "🏛️ `/menu` - मुख्य नियंत्रण मेनू खोलें\n"
            "📊 `/streak` - अपनी लाइव साधना व पदवी देखें\n"
            "🏆 `/leaderboard` - शीर्ष साधकों की सूची देखें\n"
            "🔄 `/relapse` - पतन दर्ज करें और पुनः उठें\n"
            "🎯 `/challenge` - अपना संकल्प लक्ष्य निर्धारित करें\n"
            "🧘 `/mindset` - ओजस रूपांतरण व मन नियंत्रण\n"
            "⚔️ `/workout` - पारंपरिक व्यायाम व शक्ति साधना\n"
            "🥗 `/health` - सात्विक आहार व शीतल स्नान\n"
            "📜 `/quotes` - दिव्य श्लोक व प्रेरक विचार\n"
            "📚 `/books` - आध्यात्मिक पुस्तकें प्राप्त करें\n"
            "🎵 `/songs` - दिव्य मंत्र एवं भजन सुनें\n"
            "⚡ `/motivation` - वासना नाशक त्वरित प्रेरणा\n"
            "🌐 `/language` - भाषा बदलें (English, हिन्दी, ଓଡ଼ିଆ)"
        ),
        "or": (
            "📖 **ବ୍ରହ୍ମଚର୍ଯ୍ୟ ବଟ୍ ନିର୍ଦ୍ଦେଶାବଳୀ ଓ କମାଣ୍ଡ୍** 📖\n"
            "━━━━━━━━━━━━━━━━━━━━━━\n"
            "⚡ `/start` - ସାଧନା ଆରମ୍ଭ କରନ୍ତୁ\n"
            "🏛️ `/menu` - ମୁଖ୍ୟ ନିୟନ୍ତ୍ରଣ ମେନୁ ଖୋଲନ୍ତୁ\n"
            "📊 `/streak` - ନିଜର ଷ୍ଟ୍ରିକ୍ ଏବଂ ପଦବୀ ଦେଖନ୍ତୁ\n"
            "🏆 `/leaderboard` - ଶ୍ରେଷ୍ଠ ସାଧକଙ୍କ ତାଲିକା ଦେଖନ୍ତୁ\n"
            "🔄 `/relapse` - ପତନ ଲଗ୍ କରନ୍ତୁ ଏବଂ ନୂଆ ଆରମ୍ଭ କରନ୍ତୁ\n"
            "🎯 `/challenge` - ସଂକଳ୍ପ ଲକ୍ଷ୍ୟ ସ୍ଥିର କରନ୍ତୁ\n"
            "🧘 `/mindset` - ଓଜ ଶକ୍ତି ଓ ମନ ନିୟନ୍ତ୍ରଣ\n"
            "⚔️ `/workout` - ବ୍ୟାୟାମ ଓ ଶାରୀରିକ ସାଧନା\n"
            "🥗 `/health` - ସାତ୍ତ୍ୱିକ ଆହାର ଓ ଥଣ୍ଡା ପାଣି ସ୍ନାନ\n"
            "📜 `/quotes` - ପବିତ୍ର ଶ୍ଳୋକ ଓ ପ୍ରେରଣାଦାୟୀ ବାଣୀ\n"
            "📚 `/books` - ଆଧ୍ୟାତ୍ମିକ ପୁସ୍ତକ ପାଆନ୍ତୁ\n"
            "🎵 `/songs` - ଭଜନ ଓ ମନ୍ତ୍ର ଶୁଣନ୍ତୁ\n"
            "⚡ `/motivation` - ତତ୍କାଳ ପ୍ରେରଣା\n"
            "🌐 `/language` - ଭାଷା ପରିବର୍ତ୍ତନ କରନ୍ତୁ (English, हिन्दी, ଓଡ଼ିଆ)"
        )
    },

    "language_menu_title": {
        "en": "🌐 **Choose Your Preferred Language**:\n\nSelect your language for all bot responses and guides:",
        "hi": "🌐 **अपनी पसंदीदा भाषा चुनें**:\n\nसभी संदेशों एवं मार्गदर्शिकाओं के लिए अपनी भाषा चुनें:",
        "or": "🌐 **ଆପଣଙ୍କର ପସନ୍ଦର ଭାଷା ବାଛନ୍ତୁ**:\n\nସମସ୍ତ ବାର୍ତ୍ତା ଏବଂ ନିର୍ଦ୍ଦେଶାବଳୀ ପାଇଁ ନିଜ ଭାଷା ଚୟନ କରନ୍ତୁ:"
    },

    "language_updated": {
        "en": "✅ Language updated to **{lang_name}**!",
        "hi": "✅ भाषा बदलकर **{lang_name}** कर दी गई है!",
        "or": "✅ ଭାଷା ସଫଳତାର ସହ **{lang_name}** କୁ ପରିବର୍ତ୍ତନ ହେଲା!"
    }
}

def get_text(key: str, lang: str = "en", **kwargs) -> str:
    """Fetches localized text for key in target lang, with fallback to English."""
    target_lang = lang if lang in ["en", "hi", "or"] else "en"
    entry = LOCALES.get(key, {})
    if target_lang in entry:
        template = entry[target_lang]
    elif "en" in entry:
        template = entry["en"]
    else:
        template = ""

    if template and kwargs:
        # Convenience mapping for language_updated
        if "lang_name" in kwargs and "name" not in kwargs:
            kwargs["name"] = kwargs["lang_name"]
            kwargs.setdefault("flag", "")
        elif "name" in kwargs and "lang_name" not in kwargs:
            flag_str = kwargs.get("flag", "")
            kwargs["lang_name"] = f"{flag_str} {kwargs['name']}".strip()

        try:
            return template.format(**kwargs)
        except KeyError:
            # Fallback formatting without failing on missing keys
            import string
            formatter = string.Formatter()
            mapping = {fname: kwargs.get(fname, f"{{{fname}}}") for _, fname, _, _ in formatter.parse(template) if fname}
            return template.format(**mapping)
    return template

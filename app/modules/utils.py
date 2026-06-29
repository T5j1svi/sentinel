from __future__ import annotations
import re
import hashlib
from datetime import datetime
from urllib.parse import urlparse, unquote

# Core social platforms plus regional information environments requested by the user.
PLATFORMS = [
    "X", "Instagram", "Facebook", "TikTok", "LinkedIn", "Telegram", "YouTube",
    "Pakistan News", "China News", "Bangladesh News", "Tibet News", "Global News", "Websites"
]

PLATFORM_DOMAINS = {
    "X": ["x.com", "twitter.com"],
    "Instagram": ["instagram.com"],
    "Facebook": ["facebook.com", "fb.watch"],
    "TikTok": ["tiktok.com"],
    "LinkedIn": ["linkedin.com"],
    "Telegram": ["t.me", "telegram.me"],
    "YouTube": ["youtube.com", "youtu.be"],
    # Regional / digital media packs. These are public-search source filters, not privileged access.
    "Pakistan News": [
        "dawn.com", "geo.tv", "thenews.com.pk", "tribune.com.pk", "arynews.tv", "samaa.tv",
        "dunyanews.tv", "nation.com.pk", "brecorder.com", "dialoguepakistan.com", "pakobserver.net"
    ],
    "China News": [
        "globaltimes.cn", "cgtn.com", "chinadaily.com.cn", "xinhuanet.com", "english.news.cn",
        "people.cn", "ecns.cn", "cri.cn", "china.org.cn"
    ],
    "Bangladesh News": [
        "thedailystar.net", "bdnews24.com", "dhakatribune.com", "prothomalo.com", "jugantor.com",
        "banglanews24.com", "newagebd.net", "observerbd.com"
    ],
    "Tibet News": [
        "tibet.cn", "xizang.gov.cn", "tibet.net", "phayul.com", "tibetanreview.net", "savetibet.org",
        "freetibet.org", "voatibetan.com"
    ],
    "Global News": [
        "reuters.com", "apnews.com", "bbc.com", "aljazeera.com", "theguardian.com", "dw.com",
        "france24.com", "rferl.org"
    ],
    "Websites": [],
}


# User-specified Kashmir/AJK and regional digital-media watchlist. These are public-search source filters;
# the app records clickable source URLs returned by search and does not fabricate links.
KASHMIR_AJK_SOURCES = [
    "kmsnews.org", "dailyshaheen.com", "e.roznamakashmirlink.com", "kashmirtimes.com",
    "dunyanews.tv", "app.com.pk", "dawn.com", "youtube.com", "facebook.com",
    "dialoguepakistan.com", "republicworld.com", "greaterkashmir.com",
    "instagram.com", "arynews.tv", "thenews.com.pk", "geo.tv",
]

KASHMIR_AJK_PRIORITY_HANDLES = [
    "KashmirDigital360", "KashmirDigitalOfficial", "Kashmir Media Service",
    "Daily Shaheen Mirpur", "Daily Kashmir Link", "Digital Awaz News",
    "greaterkashmirnews", "kashmirtodaynews", "expressnewspk", "jhelum_journal", "arynewstv",
]

# Add a separate pack while also feeding key sources into Pakistan News / Global discovery.
if "Kashmir / AJK News" not in PLATFORMS:
    PLATFORMS.insert(7, "Kashmir / AJK News")
PLATFORM_DOMAINS["Kashmir / AJK News"] = KASHMIR_AJK_SOURCES
for _d in KASHMIR_AJK_SOURCES:
    if _d not in PLATFORM_DOMAINS.get("Pakistan News", []):
        PLATFORM_DOMAINS.setdefault("Pakistan News", []).append(_d)

SOCIAL_PLATFORMS = {"X", "Instagram", "Facebook", "TikTok", "LinkedIn", "Telegram", "YouTube"}
REGIONAL_PLATFORMS = {"Pakistan News", "Kashmir / AJK News", "China News", "Bangladesh News", "Tibet News", "Global News"}

STOPWORDS = {
    "a", "an", "the", "is", "are", "was", "were", "to", "of", "and", "or", "in", "on", "for", "with", "by", "from", "that", "this", "it", "as", "be", "has", "have", "had", "will", "shall", "may", "can", "about", "into", "over", "under", "after", "before", "at", "their", "his", "her", "its", "new", "latest", "news", "post", "video", "live", "updates", "watch"
}


def now_case_name() -> str:
    return "case_" + datetime.now().strftime("%Y%m%d_%H%M")


def clean_text(text: str) -> str:
    if not text:
        return ""
    text = unquote(str(text))
    text = re.sub(r"https?://\S+", " ", text)
    text = re.sub(r"\s+", " ", text).strip()
    return text


def normalize_for_match(text: str) -> str:
    text = clean_text(text).lower()
    # Keep Unicode words, hashtags, handles and spaces. Strip punctuation that breaks phrase comparisons.
    text = re.sub(r"[^\w\s#@.-]+", " ", text, flags=re.UNICODE)
    text = re.sub(r"\s+", " ", text).strip()
    return text


def significant_terms(text: str, min_len: int = 3) -> list[str]:
    toks = re.findall(r"[#@]?[\w.-]+", normalize_for_match(text), flags=re.UNICODE)
    out = []
    for t in toks:
        root = t.strip("#@").lower()
        if len(root) >= min_len and root not in STOPWORDS and t not in out:
            out.append(t)
    return out


def phrase_variants(text: str) -> list[str]:
    """Small offline expansion for common influence-operation wording. Keeps full phrase intact first."""
    base = clean_text(text)
    variants = [base]
    lower = base.lower()
    replacements = [
        ("removed", ["sacked", "dismissed", "fired", "relieved", "terminated", "ousted"]),
        ("general", ["officer", "commander", "army general", "senior officer"]),
        ("indian army", ["india army", "bharatiya sena", "indian military"]),
        ("fake", ["false", "fabricated", "doctored"]),
        ("attack", ["strike", "operation", "incident"]),
    ]
    for src, alts in replacements:
        if src in lower:
            for alt in alts[:3]:
                variants.append(re.sub(src, alt, base, flags=re.I))
    # Dedupe while preserving order.
    seen, out = set(), []
    for v in variants:
        key = normalize_for_match(v)
        if key and key not in seen:
            seen.add(key); out.append(v)
    return out[:8]


def domain_of(url: str) -> str:
    try:
        return urlparse(url).netloc.lower().replace("www.", "")
    except Exception:
        return ""


def detect_platform(url: str, title: str = "") -> str:
    hay = f"{url} {title}".lower()
    # Specific domain packs before generic websites.
    for platform, domains in PLATFORM_DOMAINS.items():
        for d in domains:
            if d in hay:
                return platform
    return "Websites"


def extract_x_handle(url_or_text: str) -> str:
    text = (url_or_text or "").strip()
    m = re.search(r"(?:https?://)?(?:www\.)?(?:x|twitter)\.com/([A-Za-z0-9_]{1,20})(?:/|$)", text)
    if m and m.group(1).lower() not in ["i", "home", "search", "explore", "hashtag", "intent", "share"]:
        return "@" + m.group(1)
    m = re.search(r"@([A-Za-z0-9_]{1,20})", text)
    if m:
        return "@" + m.group(1)
    return ""


def extract_handle_from_title_or_url(title: str, url: str) -> str:
    combined = f"{title} {url}"
    patterns = [
        r"(?:x|twitter)\.com/([A-Za-z0-9_]{1,20})",
        r"instagram\.com/([A-Za-z0-9_.]{2,30})",
        r"tiktok\.com/@([A-Za-z0-9_.]{2,30})",
        r"linkedin\.com/in/([A-Za-z0-9_-]{2,80})",
        r"linkedin\.com/company/([A-Za-z0-9_-]{2,80})",
        r"t\.me/([A-Za-z0-9_]{2,80})",
        r"youtube\.com/@([A-Za-z0-9_.-]{2,80})",
        r"youtube\.com/c/([A-Za-z0-9_.-]{2,80})",
        r"youtube\.com/channel/([A-Za-z0-9_.-]{2,100})",
        r"facebook\.com/([A-Za-z0-9_.-]{2,80})",
    ]
    for pat in patterns:
        m = re.search(pat, combined, flags=re.I)
        if m:
            val = m.group(1).strip("/")
            if val.lower() not in ["posts", "watch", "share", "reel", "reels", "story", "hashtag", "search"]:
                return "@" + val
    m = re.search(r"@([A-Za-z0-9_.-]{2,80})", combined)
    if m:
        return "@" + m.group(1)
    return "Unknown"


def hash_text(text: str) -> str:
    return hashlib.sha256((text or "").encode("utf-8", errors="ignore")).hexdigest()[:16]


def youtube_thumbnail(url: str) -> str:
    m = re.search(r"(?:v=|youtu\.be/|shorts/)([A-Za-z0-9_-]{6,})", url or "")
    if m:
        vid = m.group(1)
        return f"https://img.youtube.com/vi/{vid}/hqdefault.jpg"
    return ""


def safe_filename(name: str) -> str:
    name = re.sub(r"[^A-Za-z0-9_.-]+", "_", name or "case")
    return name.strip("_")[:80] or "case"
# ==============================================================================
# --- NEW APPENDED CAPABILITIES: EXTRACTION (PII, WALLETS, HANDLERS) ---
# ==============================================================================
def extract_personal_info_and_wallets(text: str) -> dict:
    """Extracts PII, BTC/ETH wallets, and potential account handlers from raw text."""
    if not text:
        return {"btc_wallets": [], "eth_wallets": [], "emails": [], "phones": [], "handlers": []}
    
    btc = re.findall(r'\b[13][a-km-zA-HJ-NP-Z1-9]{25,34}\b', text)
    eth = re.findall(r'\b0x[a-fA-F0-9]{40}\b', text)
    emails = re.findall(r'[a-zA-Z0-9_.+-]+@[a-zA-Z0-9-]+\.[a-zA-Z0-9-.]+', text)
    phones = re.findall(r'\+?\d{10,14}', text)
    handlers = re.findall(r'@([A-Za-z0-9_.-]{2,50})', text)
    
    return {
        "btc_wallets": list(set(btc)),
        "eth_wallets": list(set(eth)),
        "emails": list(set(emails)),
        "phones": list(set(phones)),
        "handlers": list(set(handlers))
    }
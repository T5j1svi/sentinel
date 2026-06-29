# SENTINEL OSINT ENGINE — PRD v3.0
## "Cyber Intelligence Lab — Investigator Grade"
### Sunday Build Gameplan | Full Stack | All Free APIs

---

## 0. THE MISSION

SENTINEL v3 is a **cyber intelligence investigation lab** built for one purpose: take any input — a narrative, a username, an image, a video, a CSV, a PDF — and produce actionable intelligence with proof. Not a dashboard of charts. Not a search results page. A war room where every finding is verified, every source is traced to its infrastructure, every actor is mapped in a network, and every piece of evidence is locked with a cryptographic chain of custody.

When an analyst opens SENTINEL, they should feel like they walked into a professional intelligence operations centre. The UI is dark, focused, and dense with credible data. No noise. Every pixel earns its place.

**Target deadline:** Sunday
**Input types:** Narrative text · Username · Image/MP4 · CSV · PDF
**Output:** Risk score + Intelligence report (PDF/DOCX/STIX)

---

## 1. CURRENT STATE AUDIT

### What exists and works (0% mock):
- DuckDuckGo-based narrative search → real web results
- Basic network graph from search results
- Platform source packs (Kashmir, Pakistan, China news)
- CSV import, SQLite evidence storage

### What is 100% mock (replace immediately):
- `velocity.py` → random.random() fake data → replace with GDELT API
- Bot detection → placeholder scores → replace with behavioral analysis
- Infrastructure OSINT → not implemented → build from scratch
- Image/video forensics → not implemented → build from scratch
- Cross-lingual semantic search → keyword only → replace with embeddings

### Critical architectural problem:
Everything runs synchronously. One 20-minute blocking loop.
Fix: Celery + Redis async workers. Results stream as they arrive.

---

## 2. FIVE INPUT TYPES — FULL SPECIFICATION

### INPUT 1: Narrative Text
- User types a narrative description in natural language
- System expands into semantic queries in EN/UR/HI/ZH/BN/AR
- Searches all platforms simultaneously (async)
- Returns: ranked evidence clusters by semantic similarity

### INPUT 2: Username / Account Handle
- User enters @handle or username
- System searches across: X, Instagram, Telegram, YouTube, TikTok, Reddit, LinkedIn, GitHub, Facebook
- Extracts: post history, entity mentions, linked accounts, language patterns, posting intervals
- Produces: account behaviour profile + bot probability score + linked identity graph

### INPUT 3: Image or MP4
- Image: reverse image search (Google Lens API / Yandex Image / TinEye)
- Image: EXIF extraction (GPS, device, timestamp, software)
- Image: perceptual hash deduplication (find same image re-uploaded)
- Image: AI deepfake probability score (Hive Moderation API — free tier)
- MP4: keyframe extraction via ffmpeg → each frame reverse searched
- MP4: audio transcription via Whisper (local, free, multilingual)
- MP4: perceptual video hash (videohash library)
- Output: media intelligence card with provenance timeline

### INPUT 4: CSV Dataset
- Upload CSV of accounts, URLs, posts, or events
- Bulk analysis: entity extraction, coordination scoring, platform classification
- Produces: network graph of relationships in the dataset
- Exports: enriched CSV with SENTINEL scores appended

### INPUT 5: PDF Document
- Extract text via pdfplumber
- NER: extract all entities (people, orgs, places, dates, events)
- Cross-reference entities against live OSINT search
- Claim extraction: identify factual claims → ClaimBuster check-worthiness score
- Output: annotated PDF summary with entity map

---

## 3. THE 6 PIPELINE STAGES

```
INPUT
  │
  ▼
[1] COLLECTION ENGINE
    Async parallel fetch across all sources
    Telegram · X · YouTube · Facebook · Instagram
    TikTok · LinkedIn · Kashmir/Pakistan/China news packs
    GDELT · Wayback · CommonCrawl · paste sites
    Matrix/Element public rooms
    RSS continuous feed (100+ sources)
  │
  ▼
[2] EXTRACTION ENGINE
    Text: trafilatura clean extraction
    Entities: spaCy multilingual NER (person, org, place, event, date)
    Account handles: regex + platform resolver
    Personal info: email, phone, wallet address patterns
    Language: fasttext auto-detect
    Audio: Whisper transcription
    Frames: ffmpeg keyframe extraction
  │
  ▼
[3] INTELLIGENCE ENGINE
    Semantic similarity: paraphrase-multilingual-mpnet-base-v2
    Coordination scoring: interval analysis + Jaccard content similarity
    Bot probability: posting pattern + template reuse + sync analysis
    DISARM tactic classification: Claude API + local fallback
    Claim verification: ClaimBuster API + existing fact-check lookup
    Toxicity: Google Perspective API
    Deepfake: Hive Moderation API (images)
  │
  ▼
[4] INFRASTRUCTURE ATTRIBUTION
    WHOIS/RDAP → registrar, country, date, privacy
    Reverse WHOIS (WhoisXML API) → all domains by same registrant
    DNS history → SecurityTrails passive DNS
    Certificate transparency → crt.sh subdomains + issuance timeline
    ASN/BGP → RIPEstat routing history + network ownership
    GreyNoise → IP threat classification
    URLScan.io → full site scan + screenshot
    Shodan → open ports + server tech + linked infrastructure
  │
  ▼
[5] GRAPH & PATTERN ENGINE
    NetworkX: full influence network (source → amplifier → audience)
    Louvain community detection: find coordinated clusters
    Betweenness centrality: identify bridge nodes
    Temporal analysis: spread timeline + velocity anomaly detection
    Geographic mapping: IP/domain geolocation + Folium choropleth
    Propagation chain: trace how content moves platform to platform
    Identity graph: link accounts across platforms via shared signals
  │
  ▼
[6] RISK SCORE + REPORT
    Composite confidence score per finding (0-100)
    Overall campaign risk score (Critical / High / Medium / Low)
    Evidence locking: SHA-256 + Wayback + archive.ph
    Report generation: PDF + DOCX + STIX 2.1
    DISARM matrix summary
    One-page executive brief (Claude API auto-generated)
```

---

## 4. COMPLETE FREE API REGISTRY

### Tier 1 — No account required
| API | What it gives SENTINEL | Python library |
|---|---|---|
| DuckDuckGo Search | Public web search, no rate limit issues | `duckduckgo_search` |
| GDELT Project | Global event database, tone, actors, locations, velocity | `gdeltdoc` |
| Common Crawl CDX | Archived web content, historical snapshots | `requests` (CDX API) |
| Wayback Machine CDX | Historical URL versions, first-seen dates | `waybackpy` |
| crt.sh | Certificate transparency, all SSL certs for a domain | `requests` |
| RDAP (iana.org) | Domain registration data, registrar, country | `requests` |
| RIPEstat | ASN ownership, BGP routing history, IP prefix | `requests` |
| BGP.he.net | Hurricane Electric BGP data, ASN lookups | `requests` |
| ip-api.com | IP geolocation (free, no key, 45 req/min) | `requests` |
| Maxmind GeoLite2 | Local IP geolocation DB, city/country/ASN | `geoip2` |
| ClaimBuster | Claim check-worthiness scoring | `requests` (REST) |
| ClaimReview API | Existing fact-checks from AFP/Snopes/AltNews | `requests` |
| Ahmia.fi | Tor-indexed clearnet search | `requests` |
| archive.ph | Evidence preservation (submit URL) | `requests` |
| Ghostarchive | Alternative evidence archive | `requests` |
| feedparser | RSS/Atom ingestion, 100+ news sources | `feedparser` |
| Telethon MTProto | Telegram public channels, no login needed | `telethon` |
| yt-dlp | YouTube metadata, subtitles, thumbnails | `yt-dlp` |
| instaloader | Instagram public profiles | `instaloader` |

### Tier 2 — Free API key required (register once)
| API | Free tier | What it gives | Registration |
|---|---|---|---|
| Shodan | 100 results/month | Infrastructure scan, open ports, server tech | shodan.io |
| URLScan.io | 5000 scans/month | Full site scan, screenshot, outbound links | urlscan.io |
| SecurityTrails | 50 queries/month | Passive DNS history, subdomain enumeration | securitytrails.com |
| WhoisXML API | 500 queries/month | Bulk WHOIS + reverse WHOIS (killer feature) | whoisxmlapi.com |
| GreyNoise | 100 IPs/day | IP threat classification, bot/scanner detection | greynoise.io |
| VirusTotal | 500 requests/day | Domain/IP reputation + passive DNS history | virustotal.com |
| Hive Moderation | 100 images/day | AI-generated/deepfake image detection | hivemoderation.com |
| ViewDNS.info | 1000 queries/month | DNS history, IP history, reverse WHOIS | viewdns.info |
| ipinfo.io | 50k requests/month | IP geolocation + ASN enrichment | ipinfo.io |
| Perspective API | Free (apply) | Toxicity/manipulation scoring | perspectiveapi.com |
| Google Custom Search | 100 queries/day | Reverse image search (via CSE) | console.developers.google.com |
| Groq API | Very generous free tier | Ultra-fast LLM inference (Llama 3, Mixtral) | console.groq.com |

### Tier 3 — Groq + Anthropic AI stack
| Service | Use in SENTINEL | Model |
|---|---|---|
| Groq API | Fast tactic classification, entity extraction, summarisation (free, 6000 tokens/min) | `llama-3.3-70b-versatile` |
| Anthropic Claude | Executive report writing, complex reasoning, DISARM analysis | `claude-sonnet-4-6` |
| OpenAI Whisper | Audio/video transcription, local (free) | `base` or `small` model |
| sentence-transformers | Cross-lingual semantic embeddings, local (free) | `paraphrase-multilingual-mpnet-base-v2` |

**Strategy:** Use Groq for all high-volume fast inference (tactic tagging, entity extraction per result). Use Claude only for the final report synthesis and complex reasoning. This minimises cost while maximising speed.

---

## 5. COMPLETE NEW TECH STACK

### Backend
```
Python 3.12+
FastAPI 0.111+          — async REST backend
Celery 5.4+             — task queue (replaces blocking loops)
Redis 5.0+              — Celery broker + result backend
SQLAlchemy 2.0+         — ORM for evidence/case storage
SQLite (dev) / PostgreSQL (prod)
Meilisearch             — full-text search over evidence (replaces Elasticsearch — 50MB vs 2GB)
```

### Collection
```
playwright              — headless browser for JS-rendered pages
yt-dlp                  — YouTube metadata + subtitles + thumbnails
telethon                — Telegram MTProto public channels
instaloader             — Instagram public profiles
snscrape / ntscrape     — X/Twitter public search
feedparser              — RSS continuous ingestion
trafilatura             — clean article text extraction (replaces BS4 for news)
waybackpy               — Wayback Machine CDX API
gdeltdoc                — GDELT global event database
```

### Media Forensics (new)
```
ffmpeg-python           — video keyframe extraction
opencv-python-headless  — frame analysis, scene detection
imagehash               — perceptual image hashing (pHash, dHash)
videohash               — perceptual video hashing
exifread                — EXIF metadata extraction
openai-whisper          — audio transcription (local, no API cost)
Pillow                  — image processing
```

### NLP / AI
```
spacy + spacy-transformers    — multilingual NER (en, ur, hi, zh, bn)
sentence-transformers         — cross-lingual semantic embeddings
langdetect + fasttext-wheel   — language identification
deep-translator               — query expansion (EN→UR/HI/ZH/BN/AR)
transformers                  — HuggingFace models
scikit-learn                  — clustering, cosine similarity
groq                          — fast LLM inference (free tier)
anthropic                     — Claude API for reports
```

### Infrastructure OSINT (new)
```
python-whois            — basic WHOIS
requests (RDAP)         — modern RDAP registration data
shodan                  — infrastructure scanning
greynoise               — IP threat classification
securitytrails          — passive DNS (API key)
whoisxml-api            — bulk + reverse WHOIS (API key)
```

### Graph & Visualisation
```
networkx                — graph construction
python-louvain          — community detection
pyvis                   — interactive network graphs (HTML export)
plotly                  — velocity charts, timelines, scatter
folium                  — geo maps (choropleth)
streamlit-folium        — Folium in Streamlit
```

### Evidence & Reporting
```
hashlib (stdlib)        — SHA-256 content hashing
stix2                   — STIX 2.1 threat intel format
python-docx             — DOCX report generation
weasyprint              — PDF report generation
reportlab               — alternative PDF with charts
pymisp                  — MISP integration (optional)
```

### Frontend
```
Streamlit 1.35+         — UI framework (keep — it works)
streamlit-extras        — enhanced components
streamlit-aggrid        — advanced sortable/filterable tables
streamlit-plotly-events — clickable chart interactions
streamlit-option-menu   — better sidebar navigation
```

### Full requirements.txt
```txt
# ── Core backend ──────────────────────────────────────
fastapi==0.111.0
uvicorn==0.30.1
celery==5.4.0
redis==5.0.6
sqlalchemy==2.0.30
alembic==1.13.1
meilisearch==0.31.0

# ── Streamlit frontend ────────────────────────────────
streamlit==1.35.0
streamlit-extras==0.4.3
streamlit-aggrid==0.3.4
streamlit-plotly-events==0.0.6
streamlit-option-menu==0.3.12
streamlit-folium==0.20.0

# ── Data collection ───────────────────────────────────
playwright==1.44.0
yt-dlp==2024.5.27
telethon==1.34.0
instaloader==4.11
snscrape==0.7.0.20230622
feedparser==6.0.11
trafilatura==1.10.0
waybackpy==3.0.6
gdeltdoc==1.4.2
aiohttp==3.9.5
requests==2.32.0
beautifulsoup4==4.12.3
lxml==5.2.2

# ── Media forensics ───────────────────────────────────
ffmpeg-python==0.2.0
opencv-python-headless==4.9.0.80
Pillow==10.3.0
imagehash==4.3.1
videohash==2.1.0
exifread==3.0.0
openai-whisper==20231117

# ── NLP / AI ──────────────────────────────────────────
spacy==3.7.4
spacy-transformers==1.3.5
sentence-transformers==3.0.0
langdetect==1.0.9
fasttext-wheel==0.9.2
deep-translator==1.11.4
transformers==4.41.2
torch==2.2.2
scikit-learn==1.5.0
groq==0.9.0
anthropic==0.28.0

# ── Infrastructure OSINT ──────────────────────────────
python-whois==0.9.3
shodan==1.31.0
greynoise==2.3.0

# ── Graph & visualisation ─────────────────────────────
networkx==3.3
python-louvain==0.16
pyvis==0.3.2
plotly==5.22.0
folium==0.16.0

# ── Evidence & reporting ──────────────────────────────
stix2==3.0.1
python-docx==1.1.2
weasyprint==62.1
reportlab==4.2.0
pdfplumber==0.11.1
pymisp==2.4.190

# ── Utilities ─────────────────────────────────────────
pydantic==2.7.1
python-dotenv==1.0.1
loguru==0.7.2
tqdm==4.66.4
numpy==1.26.4
pandas==2.2.2
```

---

## 6. THE 10 MODULES — FULL SPECIFICATION v3

---

### MODULE 1 — NARRATIVE HUNT (upgraded)

**Status:** Exists but keyword-only → replace core search logic

**New capabilities:**
- Cross-lingual semantic expansion: query → Urdu/Hindi/Chinese/Bengali variants via deep-translator
- Multilingual embedding comparison: `paraphrase-multilingual-mpnet-base-v2` (runs locally)
- Fast-mode: top 5 results per source, bounded 90 seconds
- Deep-mode: full crawl, no time limit
- Streaming results: first results appear in 8-10 seconds while rest load

**Data sources searched simultaneously:**
- X/Twitter (snscrape)
- Telegram public channels (Telethon)
- YouTube (yt-dlp)
- Instagram public (instaloader)
- Facebook public pages (Playwright)
- TikTok (via search)
- Reddit (public JSON API)
- GDELT global events
- Kashmir/Pakistan/China/Bangladesh news packs (RSS + scraper)
- Paste sites (Pastebin, Rentry public)
- Wayback Machine (archived versions)
- Matrix/Element public rooms

**Per-result card shows:**
- Platform badge + language tag
- Semantic similarity % (0-100)
- Extracted entities (NER)
- DISARM tactic badge (auto-classified via Groq)
- Coordination flag (if part of a bot cluster)
- Credibility score (source domain age + authority)
- One-click: Lock Evidence / Archive / Open / Add to Case

---

### MODULE 2 — VELOCITY MONITOR (replace mock data)

**Status:** 100% mock → replace with GDELT + real timestamps

**Replace `velocity.py` with:**
```python
from gdeltdoc import GdeltDoc, Filters
import pandas as pd

def get_real_velocity(query: str, timespan: str = "48h") -> dict:
    gd = GdeltDoc()
    f = Filters(keyword=query, timespan=timespan)
    articles = gd.article_search(f)
    # Returns real article timestamps from GDELT
    # Group by hour, count events, detect anomalies via IQR
    hourly = articles.groupby(articles['seendate'].dt.hour).size()
    return {
        "timestamps": hourly.index.tolist(),
        "counts": hourly.values.tolist(),
        "spike_detected": detect_iqr_anomaly(hourly),
        "first_seen": articles['seendate'].min().isoformat(),
        "peak_hour": hourly.idxmax()
    }
```

**New features:**
- Real GDELT data replaces random numbers
- IQR anomaly detection (no more hardcoded thresholds)
- Platform breakdown: which platform is driving the spike
- Baseline comparison: how does this velocity compare to 7-day average
- Alert threshold: configurable by analyst

---

### MODULE 3 — NETWORK MAPPER (upgraded)

**Status:** Basic cluster graph → upgrade to full intelligence network

**New nodes:**
- Source (created content — coloured red)
- Amplifier (reposted/shared — coloured orange)
- Bridge (cross-platform linker — coloured blue)
- Bot cluster (coordinated group — coloured pink)
- Infrastructure (domain/hosting node — coloured grey)
- Media (images/videos shared — coloured teal)

**New analytics:**
- Louvain community detection → find coordinated clusters
- Betweenness centrality → identify bridge nodes (most strategic for takedown)
- In-degree centrality → identify top amplifiers
- Temporal graph → how network grows over time
- Infrastructure edges → link content nodes to their hosting infrastructure

**Export formats:**
- Interactive pyvis HTML (in-app)
- Gephi `.gexf` format
- Maltego `.mtgx` format
- GraphML `.graphml` format

---

### MODULE 4 — BEHAVIOUR PROFILER (upgraded from bot detector)

**Status:** Placeholder → build real behavioral analysis

**For each account found in investigation:**

```python
def behaviour_profile(posts: list[Post]) -> BehaviourProfile:
    # 1. Posting interval regularity (low std dev = bot-like)
    intervals = [posts[i+1].ts - posts[i].ts for i in range(len(posts)-1)]
    regularity_score = 1 - (np.std(intervals) / (np.mean(intervals) + 1))

    # 2. Content template reuse (high Jaccard = copy-paste operation)
    pairs = combinations(posts, 2)
    max_jaccard = max(jaccard(p1.tokens, p2.tokens) for p1, p2 in pairs)

    # 3. Language switching (authentic users don't switch on schedule)
    langs = [detect_language(p.text) for p in posts]
    lang_switches = sum(1 for i in range(len(langs)-1) if langs[i] != langs[i+1])
    switch_rate = lang_switches / len(posts)

    # 4. Hashtag synchronization (same hashtag within 60-second window)
    sync_score = detect_hashtag_sync(posts, window_seconds=60)

    # 5. Account age vs activity ratio
    age_activity = posts_per_day / account_age_days

    return BehaviourProfile(
        bot_probability=weighted_score(...),
        coordination_score=sync_score,
        classification=classify(bot_probability, coordination_score),
        posting_pattern=regularity_score,
        template_reuse=max_jaccard,
        language_consistency=1 - switch_rate
    )
```

**Output timeline view:**
- Hourly post frequency bar chart per account
- Highlighted synchronised posting bursts (when multiple accounts post simultaneously)
- Language switch markers on timeline
- Hashtag co-occurrence heatmap

---

### MODULE 5 — MEDIA FORENSICS (entirely new)

**Status:** Not implemented → build from scratch

**Image pipeline:**
```python
async def analyse_image(image_path: str) -> MediaIntelligence:
    # 1. EXIF extraction
    exif = exifread.process_file(open(image_path, 'rb'))
    gps = extract_gps(exif)  # lat/lon if present
    device = exif.get('Image Make', 'Unknown')
    timestamp = exif.get('EXIF DateTimeOriginal', None)

    # 2. Perceptual hash (find duplicates)
    img = Image.open(image_path)
    phash = str(imagehash.phash(img))
    dhash = str(imagehash.dhash(img))

    # 3. Reverse image search
    # Use Google Lens public API or SerpAPI (free tier)
    matches = reverse_image_search(image_path)

    # 4. Deepfake/AI detection
    result = hive_moderation_check(image_path)  # free API key
    ai_probability = result['ai_generated_probability']

    # 5. Provenance timeline
    earliest_occurrence = min(m.date for m in matches) if matches else None

    return MediaIntelligence(
        exif_data=exif, gps_coordinates=gps,
        phash=phash, dhash=dhash,
        reverse_search_matches=matches,
        ai_probability=ai_probability,
        earliest_seen=earliest_occurrence,
        provenance_chain=build_provenance_chain(matches)
    )
```

**Video pipeline:**
```python
async def analyse_video(video_path: str) -> VideoIntelligence:
    # 1. Extract keyframes
    frames = extract_keyframes_ffmpeg(video_path, interval_seconds=5)

    # 2. Transcribe audio
    model = whisper.load_model("base")
    transcript = model.transcribe(video_path, language=None)  # auto-detect

    # 3. Perceptual video hash
    vh = videohash.VideoHash(path=video_path)
    vhash = str(vh)

    # 4. Reverse search each keyframe
    frame_matches = [reverse_image_search(f) for f in frames[:10]]

    # 5. Deduplicate against known videos
    known_hashes = db.get_all_video_hashes()
    duplicates = [h for h in known_hashes if hamming_distance(vhash, h) < 5]

    return VideoIntelligence(
        transcript=transcript['text'],
        language=transcript['language'],
        keyframes=frames,
        frame_matches=frame_matches,
        video_hash=vhash,
        known_duplicates=duplicates,
        entities=extract_entities(transcript['text'])
    )
```

---

### MODULE 6 — INFRASTRUCTURE ATTRIBUTION (new)

**Status:** Not implemented → build from scratch

**Domain intelligence pipeline:**
```python
async def infrastructure_profile(domain: str) -> InfrastructureProfile:
    tasks = await asyncio.gather(
        whois_lookup(domain),          # python-whois
        rdap_lookup(domain),           # RDAP API
        crt_sh_lookup(domain),         # certificate transparency
        security_trails_dns(domain),   # passive DNS history (API key)
        urlscan_submit(domain),        # site scan (API key)
        shodan_host(domain),           # infrastructure scan (API key)
        greynoise_check(domain),       # IP threat classification (API key)
        ripest_asn(domain),            # ASN/BGP lookup (free)
        ip_geolocation(domain),        # ip-api.com (free)
        virustotal_domain(domain),     # reputation (API key)
    )
    return InfrastructureProfile(
        registrar=tasks[0].registrar,
        country=tasks[0].country,
        registration_date=tasks[0].creation_date,
        hosting_asn=tasks[6].asn,
        hosting_country=tasks[6].country,
        ip_subnet=tasks[6].ip[:ip.rfind('.')]+'.0/24',
        subdomains=tasks[2].subdomains,
        cert_history=tasks[2].cert_history,
        dns_history=tasks[3].dns_records,
        scan_screenshot=tasks[4].screenshot_url,
        open_ports=tasks[5].ports,
        threat_classification=tasks[6].classification,
    )

def find_infrastructure_clusters(profiles: list) -> list[InfraCluster]:
    # Group domains sharing same /24 subnet
    # Group domains sharing same registrar + registration_date window (±7 days)
    # Group domains sharing same nameserver
    # Each group = a probable coordinated infrastructure cluster
```

---

### MODULE 7 — TACTIC CLASSIFIER — DISARM (upgraded)

**Status:** Claude API only → add Groq fast-path + full DISARM v2 taxonomy

**Implementation:**
```python
from groq import Groq

DISARM_SYSTEM = """You are an expert disinformation analyst.
Classify the following content against the DISARM framework.
Return JSON only: {"tactic_id": "T0001", "tactic_name": "...",
"confidence": 0.0-1.0, "reasoning": "one sentence", "secondary_tactic": "..."}
DISARM tactics: T0001 False context, T0002 Fabricated content,
T0003 Impersonation, T0004 Astroturfing, T0005 State-sponsored,
T0006 Emotional manipulation, T0007 Conspiracy, T0008 Hack-and-leak,
T0009 Misattribution, T0010 Selective emphasis"""

async def classify_tactic_fast(content: str) -> DISARMClassification:
    # Use Groq for speed (6000 tokens/min free tier)
    client = Groq(api_key=GROQ_API_KEY)
    resp = client.chat.completions.create(
        model="llama-3.3-70b-versatile",
        messages=[
            {"role": "system", "content": DISARM_SYSTEM},
            {"role": "user", "content": content[:1000]}
        ],
        response_format={"type": "json_object"}
    )
    return DISARMClassification(**json.loads(resp.choices[0].message.content))

async def classify_tactic_deep(content: str) -> DISARMClassification:
    # Use Claude for complex/ambiguous cases
    client = anthropic.Anthropic(api_key=CLAUDE_API_KEY)
    # ... full reasoning chain
```

---

### MODULE 8 — GEO INTELLIGENCE (new)

**Status:** Not implemented → build from scratch

**Data sources:**
- IP geolocation: ip-api.com (free, 45 req/min)
- Maxmind GeoLite2 local DB (free, download once)
- WHOIS registrant country
- Domain TLD inference
- Language-to-region mapping

**Anomaly detection:**
```python
def detect_geo_anomaly(content_node: ContentNode, infra: InfrastructureProfile) -> GeoAnomaly:
    claimed_origin = content_node.claimed_location  # e.g., "Mirpur, AJK"
    actual_hosting = infra.hosting_country          # e.g., "China"
    registrant = infra.registrant_country           # e.g., "Pakistan"

    if claimed_origin_country != actual_hosting:
        return GeoAnomaly(
            type="origin_mismatch",
            claimed=claimed_origin,
            actual_infrastructure=actual_hosting,
            severity="high",
            note=f"Content claims {claimed_origin} but infrastructure in {actual_hosting}"
        )
```

---

### MODULE 9 — EVIDENCE LOCKER (upgraded)

**Status:** Basic CSV → upgrade to cryptographic evidence ledger

**Evidence record schema (SQLite/PostgreSQL):**
```sql
CREATE TABLE evidence (
    id          TEXT PRIMARY KEY,           -- UUID
    case_id     TEXT NOT NULL,              -- investigation case
    collected_at TEXT NOT NULL,             -- ISO timestamp UTC
    analyst_id  TEXT,                       -- who collected
    source_url  TEXT NOT NULL,              -- original URL
    archive_url TEXT,                       -- Wayback/archive.ph URL
    content_hash TEXT NOT NULL,             -- SHA-256 of raw content
    screenshot_path TEXT,                   -- local screenshot path
    screenshot_hash TEXT,                   -- SHA-256 of screenshot
    platform    TEXT,                       -- telegram/x/youtube/etc
    language    TEXT,                       -- detected language
    entities    JSON,                       -- NER entities
    disarm_tags JSON,                       -- DISARM classifications
    bot_score   REAL,                       -- coordination score
    infra_data  JSON,                       -- infrastructure findings
    notes       TEXT,                       -- analyst annotation
    locked      BOOLEAN DEFAULT FALSE,      -- immutable once locked
    lock_timestamp TEXT,                    -- when locked
    version     INTEGER DEFAULT 1           -- version tracking
);
```

**Locking mechanism:**
```python
async def lock_evidence(url: str, content: str, analyst_id: str) -> EvidenceRecord:
    content_hash = hashlib.sha256(content.encode('utf-8')).hexdigest()
    archive_url_wb = await wayback_submit(url)
    archive_url_ph = await archive_ph_submit(url)
    record = EvidenceRecord(
        id=str(uuid.uuid4()),
        source_url=url,
        content_hash=content_hash,
        archive_url=archive_url_wb or archive_url_ph,
        collected_at=datetime.utcnow().isoformat() + 'Z',
        analyst_id=analyst_id,
        locked=True,
        lock_timestamp=datetime.utcnow().isoformat() + 'Z'
    )
    await db.save(record)  # immutable after this point
    return record
```

---

### MODULE 10 — RISK SCORE + REPORT GENERATOR (upgraded)

**Status:** CSV export only → full intelligence report

**Risk scoring:**
```python
def compute_risk_score(investigation: Investigation) -> RiskScore:
    signals = {
        "coordination_detected": 25,      # bot cluster found
        "infrastructure_cluster": 20,     # shared hosting
        "state_actor_indicators": 30,     # ASN in state-controlled network
        "velocity_anomaly": 15,           # unnatural spread spike
        "cross_platform_simultaneous": 20, # same narrative, multiple platforms
        "deepfake_media": 25,             # AI-generated imagery
        "geo_origin_mismatch": 15,        # claimed vs actual location
        "known_disinfo_source": 20,       # domain in known-bad registry
    }
    total = sum(v for k, v in signals.items() if investigation.has_signal(k))
    level = "critical" if total >= 70 else "high" if total >= 45 else "medium" if total >= 25 else "low"
    return RiskScore(score=min(total, 100), level=level, signals_triggered=triggered)
```

**Report sections (auto-generated via Claude API):**
1. Executive summary (2-3 sentences, analyst-ready)
2. Narrative description and suspected intent
3. Evidence table (all locked items)
4. Network graph (exported PNG)
5. Velocity timeline
6. DISARM tactic breakdown
7. Infrastructure cluster analysis
8. Geo origin map
9. Risk score with signal breakdown
10. Recommended actions
11. Appendix: all source URLs with SHA-256 hashes

**Output formats:**
- PDF (WeasyPrint) — primary
- DOCX (python-docx) — for Word users
- STIX 2.1 JSON (stix2) — for threat intel sharing / MISP
- HTML (self-contained, portable archive)

---

## 7. UI/UX DESIGN — INVESTIGATOR-GRADE INTERFACE

### Design philosophy:
An OSINT investigator wants **density without noise**. They need to see everything relevant at a glance, drill into anything with one click, and never have to scroll past marketing fluff. The interface should feel like a professional intelligence terminal — not a SaaS dashboard.

### Key UX principles:
1. **Dark mode default** — analysts work long hours, dark is easier on the eyes
2. **Status always visible** — running tasks, locked evidence count, case name always in header
3. **One-click actions** — Lock / Archive / Add to Case should never require a modal
4. **Progressive disclosure** — show summary card first, full data on expand
5. **No empty states** — every panel shows "investigating..." while loading, not blank
6. **Keyboard shortcuts** — L to lock evidence, A to archive, N for new search
7. **Confidence everywhere** — every finding shows its confidence score (not just raw data)

### Top navigation:
```
[🔴 SENTINEL]  Case: [Kashmir-Op-July ▼]  [+ New Case]    [18 evidence]  [●●○ 2 tasks running]
─────────────────────────────────────────────────────────────────────────────────────────────
[🔍 Hunt]  [👤 Identity]  [🖼 Media]  [📊 Velocity]  [🕸 Network]  [🏛 Infrastructure]  [🗺 Geo]  [🔐 Evidence]  [📋 Report]
```

### Hunt tab layout:
```
┌─ INPUT ────────────────────────────────────────────────────────────────────────┐
│  [Narrative text / username / paste URL]                [🌐 Languages ▼]  [Hunt ↗] │
│  Mode: [◉ Fast 90s]  [○ Deep]     Sources: [X] [Telegram] [YT] [KMS] [PAK] [+] │
└────────────────────────────────────────────────────────────────────────────────┘
┌─ LIVE RESULTS ── 34 results ● streaming ────── Sort: [Relevance ▼] ──────────┐
│  [TELEGRAM]  Kashmir Liberation Resistance  ●LIVE  Semantic: 96%  Lang: [UR]  │
│  Tactic: [⚑ False context]  Bot risk: [▲ HIGH 84]  Entities: Kupwara · Modi  │
│  "Modi fauj ne Kupwara mein 14 masoom shehriyon ko..."                         │
│  [🔒 Lock]  [📎 Archive]  [🌐 Open]  [+ Case]  [▼ Expand]                    │
├────────────────────────────────────────────────────────────────────────────────┤
│  [X/TWITTER]  @KashmirResist_1  Semantic: 89%  Lang: [EN]                     │
│  Tactic: [⚑ Astroturfing]  Bot risk: [▲ HIGH 91]  Coord: 12 accounts         │
│  "Indian army massacre in #Kashmir cannot be silenced..."                      │
│  [🔒 Lock]  [📎 Archive]  [🌐 Open]  [+ Case]  [▼ Expand]                    │
└────────────────────────────────────────────────────────────────────────────────┘
```

### Identity tab layout (new):
```
┌─ ACCOUNT PROFILE ──────────────────────────────────────────────────────────────┐
│  @KashmirResist_1  [X]   Created: 2023-01-14   Posts: 8,421   Following: 234  │
│  Bot probability: 84%  ████████░░  Coordination score: 91/100                 │
│  Languages: EN 67% · UR 33%    Posting hours: 08:00-10:00 UTC (suspicious)    │
├─ ACTIVITY TIMELINE ────────────────────────────────────────────────────────────┤
│  [Plotly bar chart: posts/hour for last 7 days, spikes highlighted]            │
├─ LINKED ACCOUNTS (cross-platform) ──────────────────────────────────────────  │
│  Instagram: @kashmir_resist (same profile photo, perceptual hash match)        │
│  Telegram: Kashmir Liberation Channel (same content, 4-min delay)             │
│  YouTube: Kashmir News Live (same URL pattern in bio)                          │
├─ SYNCHRONISED ACCOUNTS ─────────────────────────────────────────────────────  │
│  11 other X accounts posted within 4-minute window: [view cluster]            │
└────────────────────────────────────────────────────────────────────────────────┘
```

### Media tab layout (new):
```
┌─ UPLOAD ────────────────────────────────────────────────────────────────────  │
│  [Drop image or video here]  or  [Paste URL]                                   │
└────────────────────────────────────────────────────────────────────────────────┘
┌─ MEDIA INTELLIGENCE ───────────────────────────────────────────────────────── │
│  ┌──────────────┐  EXIF DATA                   REVERSE SEARCH                 │
│  │              │  GPS: 34.0°N 74.8°E           4 matches found               │
│  │  [thumbnail] │  Device: Samsung SM-G991B     Earliest: 2023-08-12          │
│  │              │  Timestamp: 2025-07-14 08:32  Source: dawn.com              │
│  └──────────────┘  Software: None               Caption mismatch: YES ⚠️      │
│  Deepfake: 8% probability (genuine)   pHash: a3f8c2d1...   Duplicates: 0     │
└────────────────────────────────────────────────────────────────────────────────┘
```

---

## 8. SUNDAY BUILD PLAN — PRIORITISED TASK LIST

### PRIORITY 1 — Replace mock data (do this first, 2-3 hours)
- [ ] Replace `velocity.py` random data with GDELT API (`gdeltdoc`)
- [ ] Add IQR anomaly detection to velocity
- [ ] Add `trafilatura` for clean article text extraction
- [ ] Add `feedparser` for continuous RSS ingestion of news packs

### PRIORITY 2 — Core intelligence upgrades (3-4 hours)
- [ ] Add Groq API integration for fast DISARM tactic classification
- [ ] Add `sentence-transformers` multilingual embeddings to search
- [ ] Add cross-lingual query expansion via `deep-translator`
- [ ] Add Whisper audio transcription for YouTube/Telegram videos
- [ ] Add EXIF extraction for image inputs (`exifread`)
- [ ] Add perceptual image hashing (`imagehash`)

### PRIORITY 3 — Infrastructure OSINT (2-3 hours)
- [ ] Add crt.sh certificate transparency lookup
- [ ] Add RDAP domain registration lookup
- [ ] Add ip-api.com geolocation (free, no key)
- [ ] Add RIPEstat ASN lookup (free, no key)
- [ ] Add URLScan.io submission (free tier API key)
- [ ] Build infrastructure cluster detection (shared /24 subnet)

### PRIORITY 4 — Evidence integrity (1-2 hours)
- [ ] Add SHA-256 content hashing to all locked evidence
- [ ] Add Wayback Machine auto-submit on lock (`waybackpy`)
- [ ] Add archive.ph fallback
- [ ] Build evidence ledger with version control

### PRIORITY 5 — Report generator (2 hours)
- [ ] Build PDF report with WeasyPrint
- [ ] Build DOCX report with python-docx
- [ ] Add STIX 2.1 export via `stix2`
- [ ] Add Claude API executive summary generation

### PRIORITY 6 — UI upgrades (2-3 hours)
- [ ] Add Identity profiling tab
- [ ] Add Media forensics tab
- [ ] Replace basic graph with pyvis interactive network
- [ ] Add streamlit-aggrid for sortable evidence table
- [ ] Add dark mode default
- [ ] Add confidence score to every result card

### PRIORITY 7 — Testing (1-2 hours)
- [ ] 20 test input sets (see Section 9)
- [ ] Validate all free API connections
- [ ] Performance test: time-to-first-result < 10 seconds
- [ ] Evidence lock/unlock cycle test
- [ ] Report generation test (PDF + DOCX)

**Total estimated: 15-20 hours → achievable by Sunday**

---

## 9. 20 TEST INPUT SETS

### Narrative inputs (8 tests)
1. "Indian army kills civilians in Kashmir crackdown" — baseline test
2. "China's Belt and Road Initiative is debt trap diplomacy" — cross-platform narrative
3. "Pakistan government is oppressing Baloch people" — regional sensitive
4. "Bangladeshi army committed genocide in Chittagong Hill Tracts" — historical claim
5. "Tibet independence movement violently suppressed" — state actor narrative
6. "Imran Khan arrested by US-backed conspiracy" — political disinfo
7. "Modi is a fascist killing Muslims" — coordinated Muslim-world narrative
8. "AJK azadi movement gaining momentum" — regional independence narrative

### Username inputs (4 tests)
9. @kashmirliberation (or similar active handle)
10. A Telegram channel URL (public Kashmir resistance channel)
11. A YouTube channel posting regional conflict content
12. A Facebook page with state-linked characteristics

### Image inputs (4 tests)
13. An image from a known protest (test reverse search)
14. An AI-generated protest scene (test deepfake detection)
15. An image with GPS EXIF data intact (test provenance)
16. An image shared multiple times with different captions (test misuse)

### CSV inputs (2 tests)
17. CSV of 50 accounts with usernames + post counts (test bulk bot scoring)
18. CSV of 100 URLs with domain, date, content (test infrastructure clustering)

### PDF inputs (2 tests)
19. A news article PDF (test entity extraction + claim verification)
20. A PDF report about Kashmir/AJK situation (test cross-reference against live data)

---

## 10. ENVIRONMENT VARIABLES (.env file)

```env
# Required — get free tier keys
GROQ_API_KEY=your_groq_key_here           # console.groq.com
ANTHROPIC_API_KEY=your_claude_key_here    # console.anthropic.com
URLSCAN_API_KEY=your_urlscan_key          # urlscan.io
SHODAN_API_KEY=your_shodan_key            # shodan.io
GREYNOISE_API_KEY=your_greynoise_key      # greynoise.io
SECURITY_TRAILS_API_KEY=your_st_key       # securitytrails.com
WHOISXML_API_KEY=your_whoisxml_key        # whoisxmlapi.com
VIRUSTOTAL_API_KEY=your_vt_key            # virustotal.com
HIVE_MODERATION_API_KEY=your_hive_key    # hivemoderation.com
PERSPECTIVE_API_KEY=your_perspective_key  # perspectiveapi.com

# Optional (Telegram MTProto — public channels only)
TELEGRAM_API_ID=your_api_id              # my.telegram.org
TELEGRAM_API_HASH=your_api_hash          # my.telegram.org

# Local config
REDIS_URL=redis://localhost:6379/0
DATABASE_URL=sqlite:///./sentinel.db
MEILISEARCH_URL=http://localhost:7700
SECRET_KEY=your_random_secret_key
```

---

## 11. KNOWN PROBLEMS TO SOLVE

### Problem 1: Statement validation
Every narrative claim that SENTINEL surfaces needs a check-worthiness assessment. ClaimBuster API takes raw text and returns a check-worthiness score (0-1). Integrate this on every result card. High score = worth verifying. Cross-reference against ClaimReview schema to surface existing AFP/Snopes/AltNews fact-checks.

### Problem 2: Concept understanding
SENTINEL should not just find content — it should understand it. Use Groq to extract:
- Core claim: what is being asserted?
- Actors: who are the named parties?
- Events: what specific incident is referenced?
- Temporal context: when does the claim say this happened?
This structured extraction makes cross-platform matching far more accurate than keyword search alone.

### Problem 3: 20-set testing protocol
For each of the 20 test inputs:
- Record time-to-first-result
- Count evidence items found
- Check DISARM classification accuracy (manually validate 5 per test)
- Verify infrastructure findings (spot-check 2 domains per test)
- Test evidence lock/archive cycle
- Generate sample report and review

---

## 12. ARCHITECTURE: FILE STRUCTURE

```
sentinel/
├── app/
│   ├── main.py                    # Streamlit entry point
│   ├── pages/
│   │   ├── hunt.py                # Narrative Hunt tab
│   │   ├── identity.py            # Account profiler tab (new)
│   │   ├── media.py               # Media forensics tab (new)
│   │   ├── velocity.py            # Velocity monitor (replace mock)
│   │   ├── network.py             # Network mapper
│   │   ├── infrastructure.py      # Infrastructure OSINT (new)
│   │   ├── geo.py                 # Geo intelligence (new)
│   │   ├── evidence.py            # Evidence locker
│   │   └── report.py              # Report generator
│   └── components/
│       ├── result_card.py         # Reusable result card component
│       ├── evidence_card.py       # Evidence item component
│       └── network_graph.py       # pyvis graph renderer
├── backend/
│   ├── api/
│   │   └── routes.py              # FastAPI routes
│   ├── services/
│   │   ├── collection/
│   │   │   ├── narrative_hunt.py  # Async parallel search
│   │   │   ├── telegram.py        # Telethon connector
│   │   │   ├── youtube.py         # yt-dlp connector
│   │   │   ├── rss_monitor.py     # feedparser continuous ingestion (new)
│   │   │   └── gdelt.py           # GDELT API (replace mock)
│   │   ├── extraction/
│   │   │   ├── ner_pipeline.py    # spaCy NER
│   │   │   ├── media_forensics.py # Image/video analysis (new)
│   │   │   ├── whisper_transcribe.py # Audio transcription (new)
│   │   │   └── pdf_extractor.py   # pdfplumber (new)
│   │   ├── intelligence/
│   │   │   ├── semantic_search.py # Multilingual embeddings
│   │   │   ├── disarm_classifier.py # Groq + Claude tactic tagging
│   │   │   ├── bot_detector.py    # Behavioral analysis
│   │   │   ├── claim_checker.py   # ClaimBuster integration (new)
│   │   │   └── credibility.py     # Source credibility scoring
│   │   ├── infrastructure/
│   │   │   ├── domain_intel.py    # WHOIS + RDAP + crt.sh
│   │   │   ├── ip_intel.py        # Geolocation + ASN + GreyNoise
│   │   │   ├── cluster_detect.py  # Infrastructure cluster detection
│   │   │   └── urlscan.py         # URLScan.io integration
│   │   ├── graph/
│   │   │   ├── influence_network.py # NetworkX graph builder
│   │   │   ├── community.py       # Louvain detection
│   │   │   └── identity_graph.py  # Cross-platform account linking
│   │   ├── evidence/
│   │   │   ├── locker.py          # SHA-256 + archiving
│   │   │   ├── wayback.py         # Wayback Machine integration
│   │   │   └── chain_of_custody.py
│   │   └── reporting/
│   │       ├── risk_score.py      # Composite scoring engine
│   │       ├── pdf_report.py      # WeasyPrint PDF
│   │       ├── docx_report.py     # python-docx DOCX
│   │       └── stix_export.py     # STIX 2.1 export
│   ├── tasks/
│   │   ├── celery_app.py          # Celery configuration
│   │   └── task_registry.py       # All async tasks
│   └── models/
│       ├── evidence.py            # SQLAlchemy models
│       ├── investigation.py
│       └── intelligence.py
├── data/
│   ├── source_packs/              # Kashmir/Pakistan/China news URLs
│   ├── disarm_taxonomy.json       # Full DISARM framework
│   └── known_disinfo_domains.csv  # Known bad domain list
├── tests/
│   └── test_inputs/               # 20 test cases
├── .env                           # API keys
├── requirements.txt
└── run_windows.bat
```

---

## 13. SUCCESS CRITERIA

| Metric | Current | Target Sunday |
|---|---|---|
| Time to first results | 20+ min | < 10 seconds |
| Velocity data | 100% mock | Real GDELT data |
| Languages covered | 5 (keyword) | 12 (semantic) |
| Data sources | ~8 | 30+ |
| Evidence integrity | None | SHA-256 + archive |
| Infrastructure analysis | None | 8 data sources |
| Media forensics | None | Image + video pipeline |
| Tactic detection | None | DISARM via Groq |
| Report output | CSV | PDF + DOCX + STIX |
| Bot detection | None | Behavioral scoring |
| Confidence scoring | None | Per-finding composite |
| Test coverage | 0 | 20 input sets validated |

---

*SENTINEL PRD v3.0 | Sunday Build | Classification: Unclassified / Open Research*
*Build for the analyst. Every pixel earns its place. Every finding earns its proof.*

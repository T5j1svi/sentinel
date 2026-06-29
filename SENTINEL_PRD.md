# SENTINEL — Advanced OSINT Intelligence Platform
## Product Requirements Document v2.0
### "From search tool to cyber intelligence lab"

---

## 0. Vision Statement

SENTINEL is not a search aggregator. It is a **cyber OSINT investigation lab** — a professional-grade platform where every piece of collected data is verified, fingerprinted, cross-linked, and actionable. When an analyst opens SENTINEL, they walk into a war room, not a browser tab. Every narrative finds its origin. Every amplifier reveals its network. Every piece of evidence leaves a legal chain of custody. The output is not a list of results — it is an intelligence report ready for action.

**Tagline:** *Find the source. Map the network. Prove the narrative.*

---

## 1. The Problem (What's Broken Today)

| Problem | Current State | Impact |
|---|---|---|
| Search latency | 20+ min runs | Unusable in live situations |
| No pattern detection | Finds content, not coordination | Misses actual ops |
| No evidence integrity | Screenshots only | Legally and professionally weak |
| All sources equal | No credibility scoring | Noise overwhelming signal |
| Text only | No image/media OSINT | Misses half the content |
| No Telegram depth | Surface-level only | Misses primary regional channel |
| No tactic labelling | Raw content dump | Analyst must do all interpretation |
| No geo attribution | Can't locate sources | Missing geographic dimension |
| No cross-lingual semantics | English-only matching | Misses multilingual ops |
| No infrastructure analysis | Content only, no domains | Can't attribute state actors |

---

## 2. Target Users

**Primary:** OSINT analysts, investigative journalists, counter-disinformation researchers, academic researchers studying South/Central Asia narratives.

**Secondary:** NGOs and fact-checking organizations covering Kashmir, Pakistan, Bangladesh, Tibet. Government and security researchers requiring documented evidence chains.

**Anti-user:** Offensive operators. SENTINEL is a detection and research tool, not a targeting tool. No data on private individuals. No surveillance capability.

---

## 3. Core Design Principles

1. **Credibility over volume** — show fewer, better-evidenced results
2. **Action over display** — every finding has a "so what" and a "what next"
3. **Chain of custody always** — if it can't be proven, it's not shown as fact
4. **Multilingual by default** — no second-class treatment of Urdu/Hindi/Bengali content
5. **Speed is respect** — no analyst should wait 20 minutes for anything
6. **Lab aesthetic** — feels like a professional intelligence tool, not a web scraper UI

---

## 4. New Tech Stack

### Backend Core
```
Python 3.12+
FastAPI (async backend, replaces Streamlit backend logic)
Celery + Redis (async task queue — no more blocking 20-min searches)
SQLite (case files) → PostgreSQL (production)
Elasticsearch (fast full-text search across collected evidence)
```

### Data Collection Layer
```
Playwright (headless browser for JS-rendered pages)
yt-dlp (YouTube metadata + transcript extraction)
telethon (Telegram public channel MTProto — no login required for public)
instaloader (Instagram public profiles)
snscrape / ntscrape (X/Twitter public search)
GDELT API client (global event database)
Common Crawl API (archived web content)
Wayback Machine API (archive.org content retrieval)
crt.sh API (certificate transparency)
WHOIS / RDAP (domain intelligence)
Shodan API (infrastructure mapping)
URLScan.io API (site scanning)
```

### NLP / AI Layer
```
spaCy (multilingual NER — English, Hindi, Urdu via multilingual model)
sentence-transformers (cross-lingual semantic embeddings — paraphrase-multilingual-mpnet-base-v2)
langdetect + fasttext (language identification)
deep-translator (multilingual expansion)
transformers (Hugging Face — propaganda technique classifier, sentiment)
scikit-learn (clustering, similarity)
anthropic SDK (Claude API — tactic labelling, summary generation, report writing)
```

### Visualization Layer
```
Streamlit (front end — keep, it works)
pyvis / networkx (network graphs — replace basic cluster graph)
folium + plotly (geo maps, timelines)
Plotly Express (dashboards, velocity charts)
streamlit-extras (enhanced components)
ReportLab / WeasyPrint (PDF report generation)
```

### Evidence Layer
```
hashlib (SHA-256 content hashing)
Pillow + imagehash (perceptual image hashing)
exifread (EXIF metadata extraction)
archive.ph API / Wayback API (evidence archiving)
SQLite (evidence ledger with timestamps)
```

---

## 5. Architecture Overview

```
┌─────────────────────────────────────────────────────────────────┐
│                        SENTINEL PLATFORM                         │
├──────────────────┬──────────────────┬───────────────────────────┤
│   COLLECTION     │   INTELLIGENCE   │      ACTION LAYER         │
│   ENGINE         │   ENGINE         │                           │
│                  │                  │                           │
│  ┌─────────────┐ │ ┌──────────────┐ │  ┌────────────────────┐  │
│  │ Platform    │ │ │ NLP Pipeline │ │  │ Investigation      │  │
│  │ Connectors  │ │ │  - NER       │ │  │ Dashboard          │  │
│  │  X/Twitter  │ │ │  - Sentiment │ │  │ Network Graph      │  │
│  │  Telegram   │ │ │  - Language  │ │  │ Timeline View      │  │
│  │  YouTube    │ │ │  - Embeddings│ │  │ Geo Map            │  │
│  │  Facebook   │ │ └──────────────┘ │  │ Evidence Locker    │  │
│  │  Instagram  │ │                  │  │ Report Generator   │  │
│  │  TikTok     │ │ ┌──────────────┐ │  └────────────────────┘  │
│  │  LinkedIn   │ │ │ Pattern      │ │                           │
│  └─────────────┘ │ │ Detection    │ │  ┌────────────────────┐  │
│                  │ │  - Velocity  │ │  │ Evidence Layer     │  │
│  ┌─────────────┐ │ │  - Clusters  │ │  │  - SHA-256 hash    │  │
│  │ Infrastructure│ │ │  - Amplifiers│ │  │  - Archive.org    │  │
│  │ OSINT        │ │ │  - Bot sigs  │ │  │  - Timestamp cert │  │
│  │  WHOIS/RDAP  │ │ └──────────────┘ │  │  - Chain custody  │  │
│  │  crt.sh      │ │                  │  └────────────────────┘  │
│  │  Shodan      │ │ ┌──────────────┐ │                           │
│  │  URLScan     │ │ │ DISARM       │ │                           │
│  └─────────────┘ │ │ Classifier   │ │                           │
│                  │ │  - Tactic tag │ │                           │
│  ┌─────────────┐ │ │  - Confidence│ │                           │
│  │ Archive     │ │ └──────────────┘ │                           │
│  │ Sources     │ │                  │                           │
│  │  Wayback    │ │ ┌──────────────┐ │                           │
│  │  GDELT      │ │ │ Cross-lingual│ │                           │
│  │  CommonCrawl│ │ │ Semantic     │ │                           │
│  └─────────────┘ │ │ Matching     │ │                           │
│                  │ └──────────────┘ │                           │
└──────────────────┴──────────────────┴───────────────────────────┘
         │                  │                      │
         └──────────────────┴──────────────────────┘
                         Celery + Redis
                    (Async Task Queue)
                         SQLite / PostgreSQL
                    (Evidence + Case Storage)
```

---

## 6. The 9 Intelligence Modules (New App Structure)

---

### MODULE 1 — Narrative Hunt

**What it replaces:** Basic keyword search

**What it does:**
- Input: narrative description in natural language (not just keywords)
- Semantic query expansion in EN/UR/HI/ZH/BN/AR
- Parallel async search across all platforms simultaneously
- Cross-lingual embedding comparison — finds the Urdu version of an English narrative even if no keywords match
- Returns: ranked evidence clusters, not a flat list

**Key techniques:**
- `sentence-transformers` multilingual embeddings for query
- Cosine similarity scoring on retrieved content
- Language detection auto-tagging on every result
- Semantic deduplication — suppress near-duplicates

**UX:** Single search bar. Progress spinner per-platform. Results stream in as platforms complete (not wait for all). Each result card shows: source, platform, language, semantic similarity %, extracted entities, and one-click archive.

---

### MODULE 2 — Velocity Monitor

**What it replaces:** Nothing (completely new)

**What it does:**
- Tracks how fast a narrative is spreading across platforms
- Plots volume over time (hourly/daily/weekly)
- Flags anomalies — sudden spikes = coordinated push
- Compares spread velocity against historical baseline for that source cluster

**Key techniques:**
- GDELT API for global event velocity
- Time-series anomaly detection (IQR method, simple but effective)
- Rolling 24h / 7d / 30d views
- Platform breakdown: where is it gaining the most traction right now?

**UX:** Live line chart with anomaly markers. Alert badge when velocity crosses threshold. "First seen" timestamp with source.

---

### MODULE 3 — Network Mapper

**What it replaces:** Basic cluster graph

**What it does:**
- Builds full influence network: sources → amplifiers → audiences
- Node types: Source (created content), Amplifier (reposted), Bridge (cross-platform link), Isolated (only one platform)
- Edge weights = number of interactions / repost count
- Identifies hub nodes — the accounts/channels doing the most amplification
- Infrastructure edges — links domains to their hosting providers to find shared infrastructure clusters

**Key techniques:**
- NetworkX for graph construction
- Louvain community detection (finds clusters within the network)
- Betweenness centrality (finds bridge nodes = most valuable for takedown)
- pyvis for interactive visualization
- Export to Gephi / Maltego format

**UX:** Interactive drag-and-drop graph. Click node = see all associated evidence. Color by type (source/amplifier/bot/human). Size node by centrality. Filter by platform, date range, community cluster.

---

### MODULE 4 — Bot & Coordination Detector

**What it replaces:** Nothing (completely new)

**What it does:**
- Analyzes public behavioral signals of accounts that appear in results
- Flags probable bots and coordinated networks
- Does NOT require private account data — only publicly visible behavior

**Behavioral signals used (all public):**
- Posting interval regularity (bots post at machine-perfect intervals)
- Content template reuse (same structural pattern across accounts)
- Language switching patterns (authentic users don't flip between languages on a fixed schedule)
- Account age vs. activity ratio (new account, very high volume = suspicious)
- Hashtag synchronization (multiple accounts using same hashtag within seconds)
- Cross-account content similarity (copy-paste detection via Jaccard similarity)

**Coordination score:** 0-100 per account. Flags as: Probable Bot, Coordinated Network, Amplifier, Authentic

**UX:** Account scoring table. Coordination network sub-graph highlighting synchronized accounts. Timeline showing synchronized posting bursts.

---

### MODULE 5 — Tactic Classifier (DISARM)

**What it replaces:** Nothing (completely new)

**What it does:**
- Auto-classifies each piece of content against the DISARM Framework
- DISARM = MITRE ATT&CK equivalent for disinformation/influence operations
- Tags tactics: False Context, Impersonation, Fabricated Quotes, Emotional Manipulation, State-Sponsored, Astroturfing, etc.
- Confidence score per classification
- Maps findings to DISARM matrix view

**How it works:**
- Claude API call per content piece (batched, not per result to manage cost)
- System prompt: trained DISARM taxonomy with examples
- Returns: primary tactic, secondary tactic, confidence, reasoning excerpt
- Falls back to local classifier (scikit-learn) when API quota hit

**UX:** Each result card has a DISARM tactic badge. Aggregate DISARM matrix view — heatmap showing which tactics are most active in this investigation. Exportable as part of report.

---

### MODULE 6 — Infrastructure OSINT

**What it replaces:** Nothing (completely new)

**What it does:**
- For every domain found in results, runs full infrastructure analysis
- Finds shared infrastructure clusters (multiple propaganda sites on same host = coordinated)
- Timeline of domain registrations to find coordinated setup campaigns

**Data collected per domain:**
- WHOIS / RDAP: registrar, registrant country, registration date, privacy shield
- DNS history: IP changes over time (ViewDNS.info API)
- Certificate transparency: crt.sh — see all subdomains, cert issuance timeline
- ASN: hosting provider, country, netblock
- URLScan.io: full technical scan, screenshot, outbound links
- Shodan: open ports, server tech, any exposed services
- IP geolocation cluster: if 5 "independent" sites share same /24 subnet, they're linked

**UX:** Domain card with infrastructure breakdown. Shared infrastructure graph — colored by hosting cluster. Registration timeline to see coordinated setup dates.

---

### MODULE 7 — Evidence Locker

**What it replaces:** Basic CSV export + screenshot reminder

**What it does:**
- Cryptographically secure evidence preservation
- Every saved item gets: SHA-256 hash, timestamp, archive URL, collector metadata
- Automatic submission to Wayback Machine + archive.ph on save
- Evidence is immutable once locked — edit creates a new version, not overwrites
- Chain of custody log: who collected, when, with what tool version

**Evidence record per item:**
- `evidence_id`: UUID
- `collected_at`: ISO timestamp
- `collected_by`: analyst ID
- `source_url`: original URL
- `archive_url`: Wayback / archive.ph URL
- `content_hash`: SHA-256 of raw content
- `screenshot_hash`: SHA-256 of screenshot file
- `platform`: source platform
- `disarm_tags`: auto-classified tactics
- `entities`: extracted NER entities
- `notes`: analyst annotation
- `case_id`: associated investigation

**UX:** Evidence Locker tab — full grid view of all collected items. Filter by case, platform, tactic, date. One-click "Lock Evidence" button. Export entire locker as ZIP with manifest.

---

### MODULE 8 — Geo Intelligence

**What it replaces:** Nothing (completely new)

**What it does:**
- Maps where content is originating, being amplified, and consumed
- IP geolocation of domains and hosting infrastructure
- Domain TLD + registrant country analysis
- Language distribution by region
- Identifies geographic anomalies (e.g., content claiming to be from Kashmir but hosted in Beijing)

**Data sources:**
- IP geolocation: ip-api.com (free tier)
- Maxmind GeoLite2 (local DB, no API cost)
- WHOIS registrant country
- Domain TLD inferences

**UX:** Folium choropleth world map. Click region = see all sources associated with that region. Side panel: top hosting countries, top registrant countries, language distribution per region. Anomaly flags when claimed origin ≠ infrastructure origin.

---

### MODULE 9 — Report Generator

**What it replaces:** Manual CSV + analyst write-up

**What it does:**
- One-click generation of professional intelligence report
- Narrative: auto-written executive summary via Claude API
- Evidence: full table with all locked evidence items
- Network: exported influence graph
- DISARM: tactic breakdown with examples
- Geo: origin map
- Timeline: spread velocity chart
- Appendix: all source URLs with hashes

**Output formats:**
- PDF (WeasyPrint)
- DOCX (python-docx)
- HTML (self-contained archive)
- STIX 2.1 JSON (for formal threat intel sharing)

**UX:** Report Generator tab. Select sections to include. Preview before export. Download all formats simultaneously.

---

## 7. Data Sources — Complete Map

### Tier 1: Real-time Public Platforms
| Source | Method | Data Available |
|---|---|---|
| X / Twitter | snscrape / ntscrape | Posts, retweets, accounts (public) |
| Telegram | Telethon MTProto | Public channel messages, forwards, members |
| YouTube | yt-dlp + Data API | Titles, descriptions, transcripts, comments |
| Instagram | instaloader | Public post captions, hashtags |
| Facebook | Playwright scraper | Public page posts (limited) |
| TikTok | TikTok Research API | Public videos, captions, sounds |
| LinkedIn | Playwright scraper | Public posts (limited) |

### Tier 2: News & Media
| Source | Method | Coverage |
|---|---|---|
| Kashmir Media Service | RSS + scraper | Primary Kashmir source |
| Daily Shaheen / Kashmir Link | RSS | Regional Urdu press |
| Dawn / The News | RSS + scraper | Pakistan national press |
| The Hindu / NDTV | RSS | Indian national press |
| Xinhua | RSS | Chinese state media English |
| Dunya / Geo | RSS | Pakistan broadcast |
| APP (Pakistan Press) | RSS | Official Pakistan wire |

### Tier 3: Intelligence Databases
| Source | Method | Data Available |
|---|---|---|
| GDELT Project | REST API (free) | Global event data, tone, actors, locations |
| Common Crawl | S3 API (free) | Archived web content at scale |
| Wayback Machine | CDX API (free) | Historical versions of any URL |
| Certificate Transparency | crt.sh (free) | All SSL certs ever issued for a domain |
| URLScan.io | REST API (free tier) | Full technical site scan |
| ViewDNS.info | REST API (free tier) | DNS history, IP history, reverse WHOIS |
| WHOIS / RDAP | iana.org RDAP (free) | Domain registration data |
| VirusTotal | REST API (free tier) | Domain/IP reputation + passive DNS |
| Shodan | REST API (free tier) | Internet-connected infrastructure |

### Tier 4: Archive Sources
| Source | Method | Use |
|---|---|---|
| archive.ph | REST API | Evidence preservation |
| archive.org / Wayback | CDX API | Historical content retrieval |
| Ghostarchive | REST API | Alternative archive layer |

---

## 8. The 5 Biggest Technical Gaps — Exact Fix

### Gap 1: Search latency (20+ minutes)
**Root cause:** Synchronous sequential requests, no parallelism, waiting for all sources before showing anything.

**Fix:**
```python
# Replace this:
for source in sources:
    results += search(source, query)  # blocks 2 min each

# With this:
async def search_all(sources, query):
    tasks = [search_async(source, query) for source in sources]
    async for result in asyncio.as_completed(tasks):
        yield await result  # stream results as each platform completes
```

Use Celery workers: one worker per platform pack. Redis as broker. Results stream to frontend via WebSocket. **Target: first results in under 10 seconds.**

### Gap 2: No coordination detection
**Fix:** Implement Jaccard content similarity + posting interval analysis.
```python
def coordination_score(account_posts: list[Post]) -> float:
    intervals = [posts[i+1].ts - posts[i].ts for i in range(len(posts)-1)]
    regularity = np.std(intervals) / np.mean(intervals)  # low = bot-like
    template_reuse = max_jaccard_similarity(account_posts)  # high = coordinated
    return normalize(regularity * 0.4 + template_reuse * 0.6)
```

### Gap 3: Evidence integrity
**Fix:** SHA-256 hash + Wayback submission on every save.
```python
def lock_evidence(url: str, content: str) -> EvidenceRecord:
    content_hash = hashlib.sha256(content.encode()).hexdigest()
    archive_url = wayback_submit(url)  # submit to archive.org
    return EvidenceRecord(
        url=url, hash=content_hash,
        archive_url=archive_url,
        locked_at=datetime.utcnow().isoformat(),
        immutable=True
    )
```

### Gap 4: Cross-lingual matching
**Fix:** Multilingual sentence embeddings for semantic search.
```python
from sentence_transformers import SentenceTransformer
model = SentenceTransformer('paraphrase-multilingual-mpnet-base-v2')
# Works across: EN, UR, HI, ZH, BN, AR, FA, TR

def semantic_similarity(text_a: str, text_b: str) -> float:
    emb_a = model.encode(text_a)
    emb_b = model.encode(text_b)
    return cosine_similarity([emb_a], [emb_b])[0][0]
```

### Gap 5: Telegram depth
**Fix:** Telethon with MTProto — no login needed for public channels.
```python
from telethon import TelegramClient
# Only needs API_ID + API_HASH from my.telegram.org — no phone, no login
client = TelegramClient('sentinel_session', API_ID, API_HASH)

async def get_channel_messages(channel_username: str, limit=500):
    async with client:
        messages = await client.get_messages(channel_username, limit=limit)
        return [m.text for m in messages if m.text]
```

---

## 9. New Dashboard Layout

### Navigation Structure
```
┌─────────────────────────────────────────────────────────────┐
│ SENTINEL  [🔴 LIVE]          Case: [Kashmir-Op-Jul25  ▼]    │
├───────────────────────────────────────────────────────────  │
│ [Hunt] [Network] [Velocity] [Tactics] [Infra] [Geo] [Evidence] [Report] │
└─────────────────────────────────────────────────────────────┘
```

### Hunt Tab Layout
```
┌──────────────────────────────────────────────────────────┐
│  NARRATIVE QUERY                                          │
│  ┌────────────────────────────────┐ [Languages ▼] [Hunt] │
│  │ Describe the narrative...       │                      │
│  └────────────────────────────────┘                      │
│  Platform packs: [X] [Telegram] [YouTube] [FB] [Insta]  │
│  [TikTok] [Kashmir News] [Pakistan News] [China] [Global]│
├──────────────────────────────────────────────────────────┤
│  LIVE RESULTS                    34 results — streaming  │
│  ┌────────────────────────────────────────────────────┐  │
│  │ [Telegram] Kashmir Liberation Front           🔴   │  │
│  │ Semantic match: 94%  |  Language: UR  |  Entities: │  │
│  │ [India] [Kupwara] [Modi]   Tactic: [False Context] │  │
│  │ "Modi regime kills 12 in Kupwara crackdown..."     │  │
│  │ [🔒 Lock Evidence] [🌐 Open] [📎 Archive] [+Case] │  │
│  └────────────────────────────────────────────────────┘  │
│  [+ 33 more results...]                                  │
└──────────────────────────────────────────────────────────┘
```

### Network Tab Layout
```
┌────────────────────────────────────────────────────────┐
│  INFLUENCE NETWORK     [Filter by: Platform/Type/Date] │
│  ┌──────────────────────────────────────────────────┐  │
│  │                                                   │  │
│  │  [Full interactive pyvis network graph here]     │  │
│  │  Nodes: Sources/Amplifiers/Bots/Bridges          │  │
│  │  Edges: Reposts/Links/Mentions                   │  │
│  │                                                   │  │
│  └──────────────────────────────────────────────────┘  │
│  Top amplifiers: account1 (482 reposts) account2 (341) │
│  Communities detected: 3    Bridge nodes: 7            │
└────────────────────────────────────────────────────────┘
```

---

## 10. DISARM Tactic Reference (integrated in app)

| ID | Tactic | Description | Detection signal |
|---|---|---|---|
| T0001 | False context | Real content, false framing | Verifiable fact contradiction |
| T0002 | Fabricated content | Entirely made-up stories | No primary source found |
| T0003 | Impersonation | Fake account mimicking real one | Username/avatar similarity |
| T0004 | Astroturfing | Fake grassroots appearance | Coordination score >70 |
| T0005 | State-sponsored | Government-linked amplification | Infrastructure attribution |
| T0006 | Emotional manipulation | Fear/anger/outrage appeals | Sentiment extremity |
| T0007 | Conspiracy narrative | Unverified hidden-hand claims | Claim without evidence |
| T0008 | Hack-and-leak | Stolen materials | Unverified document drops |

---

## 11. Implementation Gameplan — 12 Weeks

### Phase 1 — Foundation (Weeks 1-3)
- [ ] Migrate backend to FastAPI + async
- [ ] Implement Celery + Redis task queue
- [ ] Build streaming results to Streamlit via WebSocket
- [ ] Implement SHA-256 evidence hashing + Wayback integration
- [ ] Add multilingual sentence embeddings (paraphrase-multilingual-mpnet-base-v2)
- [ ] **Target: search under 10s, evidence locking working**

### Phase 2 — Intelligence Layer (Weeks 4-6)
- [ ] Integrate GDELT API
- [ ] Implement coordination/bot detection scorer
- [ ] Implement DISARM tactic classifier (Claude API + fallback)
- [ ] Build velocity tracking + anomaly detection
- [ ] Build NER entity extraction pipeline (spaCy multilingual)
- [ ] **Target: every result has entity tags + tactic badge**

### Phase 3 — Network & Infrastructure (Weeks 7-9)
- [ ] Build full NetworkX influence graph
- [ ] Add Louvain community detection
- [ ] Implement WHOIS / crt.sh / URLScan infrastructure module
- [ ] Build Telegram MTProto connector (Telethon)
- [ ] Add archive.ph evidence layer
- [ ] **Target: network mapper live, infra OSINT running**

### Phase 4 — Visualization & Reporting (Weeks 10-12)
- [ ] Build Folium geo map
- [ ] Build spread timeline visualization
- [ ] Build DISARM matrix heatmap view
- [ ] Implement PDF/DOCX/HTML report generator
- [ ] Polish Evidence Locker with chain-of-custody view
- [ ] Full end-to-end test on real Kashmir narrative
- [ ] **Target: ship v2.0**

---

## 12. Requirements Files

### requirements.txt (new full stack)
```
# Core
fastapi==0.111.0
uvicorn==0.30.0
celery==5.4.0
redis==5.0.6
streamlit==1.35.0
streamlit-extras==0.4.3

# Collection
playwright==1.44.0
yt-dlp==2024.5.27
telethon==1.34.0
instaloader==4.11
snscrape==0.7.0.20230622

# NLP / AI
spacy==3.7.4
sentence-transformers==3.0.0
langdetect==1.0.9
fasttext-wheel==0.9.2
deep-translator==1.11.4
transformers==4.41.2
scikit-learn==1.5.0
anthropic==0.28.0

# Data
requests==2.32.0
aiohttp==3.9.5
beautifulsoup4==4.12.3
lxml==5.2.2
gdeltdoc==1.4.2
python-whois==0.9.3
shodan==1.31.0

# Visualization
plotly==5.22.0
folium==0.16.0
networkx==3.3
pyvis==0.3.2
streamlit-folium==0.20.0

# Evidence
hashlib  # stdlib
pillow==10.3.0
imagehash==4.3.1
exifread==3.0.0
weasyprint==62.1
python-docx==1.1.2
reportlab==4.2.0

# Storage
sqlalchemy==2.0.30
elasticsearch==8.13.1  # optional, for scale
```

---

## 13. Success Metrics

| Metric | Current | Target |
|---|---|---|
| Time to first results | 8-20 min | < 10 seconds |
| Languages covered | 5 | 12 |
| Data sources | ~8 | 30+ |
| Evidence integrity | None | SHA-256 + archive |
| Tactic detection | None | DISARM-tagged |
| Network analysis | Basic cluster | Full NetworkX + communities |
| Report output | CSV | PDF + DOCX + STIX |
| Cross-lingual matching | Keyword only | Semantic embeddings |
| Bot detection | None | Coordination score per account |
| Infrastructure analysis | None | WHOIS + crt.sh + Shodan |

---

## 14. What "Overwhelmed with Credible Data" Looks Like

When an analyst investigates a narrative in SENTINEL v2:

1. **Hunt** finds 40 results in under 10 seconds, across Telegram, X, YouTube, and Kashmir news — in Urdu, English and Hindi — semantically matched to the original narrative query.

2. **Every result card shows:** platform, language, semantic similarity score, extracted entities (people, places, orgs), DISARM tactic badge, and one-click evidence lock.

3. **Network mapper** shows 3 amplifier communities, 7 bridge nodes, and 2 probable bot clusters coordinating the push.

4. **Velocity chart** shows the narrative was flat for 3 days then spiked 800% in 4 hours — characteristic of a coordinated push.

5. **Infrastructure module** links 4 "independent" news sites to the same hosting subnet in Shenzhen, with domains registered on the same date.

6. **Geo map** shows the narrative claims to originate in Mirpur AJK, but all infrastructure is hosted in two ASNs: one in Pakistan, one in China.

7. **Evidence Locker** has 18 locked items, all SHA-256 hashed, archived to Wayback + archive.ph, with full chain of custody.

8. **One click:** export full intelligence report — executive summary, evidence table, network graph, geo map, DISARM breakdown. PDF ready in 30 seconds.

That is the SENTINEL experience.

---

*Document version: 2.0 | Status: Ready for implementation | Classification: Unclassified / Open Research*

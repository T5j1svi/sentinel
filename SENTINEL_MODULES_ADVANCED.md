# SENTINEL — Advanced Module Specifications
## Deep Implementation Guide — Every Module, Every Source, Every Graph
### Version 3.1 | Investigator-Grade OSINT Engine

---

> **How to read this document:**
> Each module has: What it currently does (basic) → What it becomes (advanced) → Full data source map → Exact techniques → All graphs/visualisations → Connection to other modules → Implementation code skeleton.

---

## MODULE 1 — NARRATIVE HUNT ENGINE
### *"Find every version of a lie across every language and platform"*

---

### Basic (current state)
DuckDuckGo keyword search. Returns 10 links. No language handling. Sequential. Blocks for 20 minutes.

---

### Advanced (target state)

The Narrative Hunt Engine is a **semantic multi-vector search system** that treats a narrative as a fingerprint, not a keyword. It finds every expression of that narrative — in any language, on any platform, with any wording — by comparing meaning, not text.

**Core intelligence concept:** A narrative is not its words. "Indian army kills civilians" and "فوج نے شہریوں کو شہید کیا" are the same narrative. The engine finds both by converting both into a 768-dimensional semantic vector and comparing distance in embedding space.

---

### Full data source map

| Source | Method | Rate limit | What you get |
|---|---|---|---|
| DuckDuckGo | `duckduckgo_search` | None (throttle to 1 req/s) | Web snippets, URLs, thumbnails |
| Bing Search | `requests` + headers | 1000/month free tier | Wider web coverage than DDG |
| Google Custom Search | CSE API | 100/day free | High-quality results, image search |
| Telegram public | `telethon` MTProto | Limited by server | Channel posts, forwards, message count |
| YouTube | `yt-dlp` + Data API v3 | 10,000 units/day free | Titles, descriptions, transcripts, comment counts |
| Reddit | Public JSON API `reddit.com/search.json` | 60 req/min no key | Posts, comments, subreddit metadata |
| GDELT GKG | `gdeltdoc` | Unlimited free | Global media articles, tone, actor mentions |
| Common Crawl | CDX API | Unlimited free | Historical web content at petabyte scale |
| Wayback CDX | `waybackpy` | Unlimited free | All versions of a URL over time |
| Kashmir news pack | RSS + `feedparser` | Unlimited | KMS, Daily Shaheen, Kashmir Link, Kashmir Times |
| Pakistan news pack | RSS + `feedparser` | Unlimited | Dawn, Geo, Dunya, The News, APP wire |
| China news pack | RSS + `feedparser` | Unlimited | Xinhua EN, CGTN, Global Times EN |
| Bangladesh pack | RSS + `feedparser` | Unlimited | Daily Star, Prothom Alo English, BDNews24 |
| Paste sites | `requests` public API | Unlimited | Pastebin recent, Rentry public |
| Matrix rooms | `matrix-nio` | Unlimited public | Public Element/Matrix channel posts |
| Mastodon | Public API | 300 req/5min | Federated social content |

---

### Exact techniques

**Step 1: Semantic query expansion**
```python
from deep_translator import GoogleTranslator
from sentence_transformers import SentenceTransformer

model = SentenceTransformer('paraphrase-multilingual-mpnet-base-v2')

LANGUAGES = {
    'ur': 'Urdu', 'hi': 'Hindi', 'zh-CN': 'Chinese Simplified',
    'zh-TW': 'Chinese Traditional', 'bn': 'Bengali', 'ar': 'Arabic',
    'fa': 'Persian', 'ps': 'Pashto', 'tr': 'Turkish'
}

def expand_query(narrative: str) -> dict[str, str]:
    """Translate narrative to all target languages for native-language search."""
    expansions = {'en': narrative}
    for lang_code, lang_name in LANGUAGES.items():
        try:
            translated = GoogleTranslator(source='en', target=lang_code).translate(narrative)
            expansions[lang_code] = translated
        except Exception:
            pass
    return expansions

def encode_narrative(narrative: str) -> np.ndarray:
    """Encode narrative as 768-dim semantic vector for comparison."""
    return model.encode(narrative, normalize_embeddings=True)
```

**Step 2: Async parallel collection**
```python
import asyncio
from typing import AsyncGenerator

async def hunt_all_sources(narrative: str) -> AsyncGenerator:
    """Fire all source searches simultaneously, yield results as they arrive."""
    query_vector = encode_narrative(narrative)
    expanded = expand_query(narrative)

    tasks = {
        'ddg': search_duckduckgo(expanded['en'], limit=20),
        'telegram': search_telegram_channels(expanded['ur'], expanded['en']),
        'youtube': search_youtube(expanded['en'], limit=15),
        'gdelt': search_gdelt(expanded['en'], timespan='7d'),
        'reddit': search_reddit(expanded['en'], limit=25),
        'kashmir_rss': search_rss_pack('kashmir', expanded['en']),
        'pakistan_rss': search_rss_pack('pakistan', expanded['ur']),
        'china_rss': search_rss_pack('china', expanded['zh-CN']),
        'wayback': search_wayback(expanded['en'], limit=10),
        'paste_sites': search_paste_sites(expanded['en']),
        'matrix': search_matrix_rooms(expanded['en']),
    }

    for coro in asyncio.as_completed(tasks.values()):
        results = await coro
        for r in results:
            # Score each result against narrative vector
            r.semantic_score = cosine_similarity(
                query_vector,
                encode_narrative(r.content_snippet)
            )
            r.language = detect_language(r.content_snippet)
            yield r  # Stream immediately — don't wait for all sources
```

**Step 3: Semantic deduplication**
```python
def deduplicate_results(results: list[Result], threshold: float = 0.92) -> list[Result]:
    """Remove near-duplicate results keeping highest-confidence version."""
    vectors = [encode_narrative(r.content_snippet) for r in results]
    seen = set()
    unique = []
    for i, r in enumerate(results):
        if i in seen:
            continue
        for j in range(i+1, len(results)):
            if cosine_similarity(vectors[i], vectors[j]) > threshold:
                seen.add(j)  # Mark as duplicate
        unique.append(r)
    return sorted(unique, key=lambda r: r.semantic_score, reverse=True)
```

**Step 4: Per-result enrichment pipeline**
Every result that streams in passes through:
1. `langdetect` → language tag
2. `spaCy xx_ent_wiki_sm` → entity extraction (person, org, place, event)
3. `ClaimBuster API` → check-worthiness score (0-1)
4. `Groq/llama-3.3-70b` → DISARM tactic classification
5. `Perspective API` → toxicity/manipulation score
6. `domain_credibility()` → source credibility (domain age + Alexa rank + WHOIS)
7. `coordination_check()` → is this account in a known bot cluster?

---

### All graphs and visualisations

**Graph 1: Semantic similarity heatmap**
- X-axis: all results found
- Y-axis: semantic similarity to original narrative (0-100%)
- Colour: platform (Telegram=red, X=orange, YouTube=teal, news=blue)
- Interactive: click bar → open full result card

**Graph 2: Language distribution donut**
- Shows EN/UR/HI/ZH/BN breakdown of all results
- Insight: if 60% of results are Urdu, narrative is targeting Urdu-speaking audience

**Graph 3: Source timeline (first seen)**
- Horizontal timeline: when each source first published a version of the narrative
- Colour by platform
- Insight: reveals which platform was seeded first

**Graph 4: Credibility scatter plot**
- X: source credibility score (0-100)
- Y: semantic similarity to narrative (0-100)
- Bubble size: volume of content from that source
- Quadrant analysis: High credibility + High similarity = strong evidence; Low credibility + High similarity = propaganda amplification

**Graph 5: Entity co-occurrence network**
- Nodes: entities extracted across all results (people, places, orgs)
- Edges: co-occurrence in same article/post
- Size: frequency of mention
- Insight: who/what is being mentioned together — reveals the cast of the narrative

---

### Connections to other modules
- All results → **Module 4 (Behaviour)**: account handles extracted → profiled
- All domains → **Module 6 (Infrastructure)**: every domain auto-submitted for infra analysis
- All timestamps → **Module 2 (Velocity)**: feed into spread timeline
- All results → **Module 3 (Network)**: build influence graph from amplification patterns
- High-confidence results → **Module 9 (Evidence)**: auto-lock prompt

---

## MODULE 2 — VELOCITY MONITOR & ANOMALY DETECTION
### *"Know the moment a narrative goes from seeded to amplified"*

---

### Basic (current state)
`random.random()` generating fake data points. Completely mock. No real intelligence.

---

### Advanced (target state)

The Velocity Monitor is an **early warning system**. It doesn't just show how much content exists — it detects the moment an organic narrative becomes a coordinated push, and flags the precise hour the amplification began.

**Core intelligence concept:** Authentic narratives grow organically — slow build, gradual spread. Coordinated operations spike — flat for days, then 800% increase in 4 hours. The pattern itself is the signature.

---

### Full data source map

| Source | Method | Temporal resolution | Coverage |
|---|---|---|---|
| GDELT GKG | `gdeltdoc` Article Search | 15-minute intervals | 100+ languages, 65+ countries |
| GDELT Event DB | `gdeltdoc` Event Search | Daily | Georeferenced events, actors, event types |
| RSS feed timestamps | `feedparser` + SQLite | Real-time (polling) | All 50+ ingested news sources |
| Telegram message timestamps | `telethon` | Per-message | Public channels in investigation |
| YouTube upload timestamps | `yt-dlp` | Per-video | Upload date + view velocity |
| Reddit post timestamps | Public JSON API | Per-post | Post date + upvote velocity |
| Wayback CDX timestamps | `waybackpy` | Per-snapshot | First archived date = earliest known existence |
| Internal evidence DB | SQLite | Per-lock | All SENTINEL-collected timestamps |

---

### Exact techniques

**Replace `velocity.py` entirely:**

```python
from gdeltdoc import GdeltDoc, Filters
import pandas as pd
import numpy as np
from scipy import stats

class VelocityMonitor:

    def __init__(self):
        self.gd = GdeltDoc()

    def get_gdelt_timeseries(self, query: str, timespan: str = "3months") -> pd.DataFrame:
        """Pull real GDELT article volume over time — replaces random data."""
        f = Filters(keyword=query, timespan=timespan)
        timeline = self.gd.timeline_search("timelinevol", f)
        # Returns: DataFrame with columns [datetime, Volume Intensity]
        return timeline

    def get_platform_timeseries(self, results: list[Result]) -> pd.DataFrame:
        """Build per-platform hourly volume from collected results."""
        df = pd.DataFrame([{
            'timestamp': r.published_at,
            'platform': r.platform,
            'source': r.source_domain
        } for r in results])
        df['timestamp'] = pd.to_datetime(df['timestamp'])
        return df.groupby(['platform', pd.Grouper(key='timestamp', freq='1H')]).size().reset_index()

    def detect_anomaly_iqr(self, series: pd.Series) -> list[AnomalyPoint]:
        """IQR-based anomaly detection — no hardcoded thresholds."""
        Q1, Q3 = series.quantile(0.25), series.quantile(0.75)
        IQR = Q3 - Q1
        upper_fence = Q3 + 1.5 * IQR
        anomalies = series[series > upper_fence]
        return [AnomalyPoint(timestamp=ts, value=v, severity=self._severity(v, upper_fence))
                for ts, v in anomalies.items()]

    def detect_coordinated_surge(self, df: pd.DataFrame) -> CoordinationEvent | None:
        """Detect when multiple platforms spike simultaneously — signature of coordinated push."""
        platform_hourly = df.pivot_table(index='timestamp', columns='platform', values=0, fill_value=0)
        # Check if 3+ platforms spike within same 2-hour window
        for hour in platform_hourly.index:
            window = platform_hourly.loc[hour:hour + pd.Timedelta('2H')]
            platforms_spiking = sum(
                1 for col in window.columns
                if window[col].max() > window[col].mean() * 3
            )
            if platforms_spiking >= 3:
                return CoordinationEvent(
                    timestamp=hour,
                    platforms_involved=platforms_spiking,
                    surge_factor=window.max().max() / window.mean().mean()
                )
        return None

    def find_origin_point(self, all_timestamps: list[datetime]) -> OriginPoint:
        """Find the earliest known appearance of the narrative."""
        return OriginPoint(
            timestamp=min(all_timestamps),
            delta_to_spike=spike_time - min(all_timestamps)
        )

    def compute_spread_rate(self, series: pd.Series) -> dict:
        """How fast is the narrative doubling? What is its R-value?"""
        # Fit exponential growth model
        log_series = np.log1p(series.values)
        slope, intercept, r_value, p_value, _ = stats.linregress(
            range(len(log_series)), log_series
        )
        return {
            'doubling_time_hours': np.log(2) / slope if slope > 0 else None,
            'r_squared': r_value**2,
            'growth_phase': 'exponential' if r_value**2 > 0.85 else 'linear' if slope > 0 else 'declining'
        }
```

---

### All graphs and visualisations

**Graph 1: Master velocity timeline (primary view)**
- Multi-layer line chart (Plotly)
- Layer 1: Total volume (all platforms) — thick white line
- Layer 2: Per-platform stacked area (Telegram=red, X=orange, YouTube=teal, news=blue)
- Overlay: Red vertical markers at anomaly points
- Overlay: Green marker at "first seen" origin point
- Overlay: Yellow band = baseline ±1.5 IQR range
- X-axis: time (zoom from 6h to 3 months)
- Y-axis: volume (log scale option for exponential growth)
- Interactive: click anomaly marker → show what spiked, where, who amplified

**Graph 2: Platform contribution waterfall**
- Which platform contributed what % of volume at each hour
- Waterfall shows: Telegram seed → X amplification wave → YouTube lag
- Reveals the amplification sequence and delay between stages

**Graph 3: Spread rate heatmap (geographic)**
- World map with choropleth
- Colour intensity = volume per country per hour
- Animation: play forward to watch narrative spread geographically
- Insight: where did it ignite first, which regions amplified it

**Graph 4: Velocity vs credibility scatter**
- X: publication velocity (articles per hour)
- Y: average source credibility score
- Quadrant: high velocity + low credibility = coordinated low-quality push
- Quadrant: high velocity + high credibility = organic mainstream pickup

**Graph 5: Tone trajectory (GDELT)**
- GDELT provides tone score (-100 to +100) per article
- Plot average tone of narrative over time
- Pattern: tone often starts highly negative (to provoke outrage), then shifts
- Alert: sudden tone shift may indicate second phase of operation

---

### Connections to other modules
- Anomaly timestamps → **Module 3 (Network)**: show network state at moment of spike
- First-seen timestamp → **Module 1 (Hunt)**: Wayback lookup at that exact date
- Platform breakdown → **Module 6 (Infrastructure)**: which domains were active during spike
- Coordinated surge events → **Module 4 (Behaviour)**: which accounts posted at spike moment

---

## MODULE 3 — INFLUENCE NETWORK MAPPER
### *"Show who is pulling the strings and how the message travels"*

---

### Basic (current state)
Basic NetworkX graph built from search result domains. No node types. No community detection. Static image.

---

### Advanced (target state)

The Influence Network Mapper is a **living intelligence map** of every actor, platform, domain, and piece of content involved in a narrative — and every relationship between them. It answers: who created it, who amplified it, who bridges platforms, and who is operating as a coordinated unit.

**Core intelligence concept:** In a coordinated influence operation, the network structure is the proof. Authentic narratives have organic, distributed networks. Operations have hub-and-spoke structures, bridge nodes linking platforms, and tightly synchronised clusters.

---

### Full data source map

| Data type | Source | What it contributes to the graph |
|---|---|---|
| Platform posts | All collected results | Content nodes + publishing edges |
| Repost/share data | X/Telegram/Reddit | Amplification edges with timestamps |
| Domain links | All URLs in results | Infrastructure nodes + hosting edges |
| WHOIS clusters | Module 6 output | Infrastructure ownership edges |
| Account handles | Extracted from content | Account nodes + mention edges |
| Bot scores | Module 4 output | Node colouring + cluster flagging |
| GDELT actor data | `gdeltdoc` | Named actor nodes + event edges |
| Cross-platform matches | Semantic similarity | Cross-platform equivalence edges |
| Email/registrant | WhoisXML reverse | Registrant identity nodes |
| ASN/hosting | RIPEstat + Shodan | Infrastructure cluster edges |

---

### Exact techniques

**Node taxonomy:**
```python
class NodeType(Enum):
    CONTENT     = "content"       # Individual post/article
    ACCOUNT     = "account"       # Social media account
    DOMAIN      = "domain"        # Website/news outlet
    CHANNEL     = "channel"       # Telegram/YouTube channel
    INFRA       = "infrastructure" # Hosting provider / ASN
    REGISTRANT  = "registrant"    # Domain registrant identity
    BOT_CLUSTER = "bot_cluster"   # Group of coordinated accounts
    MEDIA       = "media"         # Specific image/video
    NARRATIVE   = "narrative"     # Abstract narrative node (root)

class EdgeType(Enum):
    PUBLISHED   = "published"     # account → content
    REPOSTED    = "reposted"      # account → content (with timestamp delta)
    HOSTED_ON   = "hosted_on"     # domain → infrastructure
    REGISTERED_BY = "registered_by" # domain → registrant
    MENTIONS    = "mentions"      # content → entity
    LINKED_TO   = "linked_to"     # content → external URL
    EQUIVALENT  = "equivalent"    # cross-platform semantic match
    COORDINATED_WITH = "coordinated_with"  # bot cluster edge
    BRIDGES     = "bridges"       # cross-platform amplifier
```

**Graph construction:**
```python
import networkx as nx
from community import community_louvain  # python-louvain
import numpy as np

class InfluenceNetworkBuilder:

    def __init__(self):
        self.G = nx.DiGraph()
        self.timestamps = {}  # edge → timestamp for temporal analysis

    def add_narrative_root(self, narrative: str) -> str:
        """Root node — everything connects back to this."""
        nid = f"narrative_{hash(narrative)}"
        self.G.add_node(nid, type=NodeType.NARRATIVE, label=narrative[:50],
                        size=30, color='#ffffff')
        return nid

    def add_content_node(self, result: Result, narrative_id: str):
        """Add a content node and connect to narrative."""
        cid = f"content_{result.id}"
        self.G.add_node(cid,
            type=NodeType.CONTENT,
            platform=result.platform,
            language=result.language,
            semantic_score=result.semantic_score,
            disarm_tactic=result.disarm_tactic,
            timestamp=result.published_at,
            url=result.url,
            size=10 + (result.semantic_score * 20),  # bigger = more relevant
            color=PLATFORM_COLORS[result.platform]
        )
        self.G.add_edge(narrative_id, cid,
            type=EdgeType.EQUIVALENT,
            weight=result.semantic_score
        )
        self.timestamps[(narrative_id, cid)] = result.published_at

    def add_amplification_edges(self, reposts: list[Repost]):
        """Build amplification chain from repost data."""
        for r in reposts:
            self.G.add_edge(r.original_account, r.repost_account,
                type=EdgeType.REPOSTED,
                delay_minutes=(r.repost_time - r.original_time).seconds // 60,
                platform=r.platform
            )

    def add_infrastructure_cluster(self, domains: list[str], shared_asn: str):
        """Link domains sharing infrastructure to reveal coordinated networks."""
        infra_id = f"infra_{shared_asn}"
        self.G.add_node(infra_id, type=NodeType.INFRA, label=shared_asn,
                        color='#666666', size=15)
        for domain in domains:
            self.G.add_edge(domain, infra_id, type=EdgeType.HOSTED_ON)

    def detect_communities(self) -> dict:
        """Louvain community detection on undirected projection."""
        undirected = self.G.to_undirected()
        partition = community_louvain.best_partition(undirected, resolution=1.2)
        nx.set_node_attributes(self.G, partition, 'community')
        return partition

    def compute_centrality(self) -> dict:
        """Find bridge nodes and top amplifiers."""
        betweenness = nx.betweenness_centrality(self.G, normalized=True)
        in_degree = dict(self.G.in_degree(weight='weight'))
        pagerank = nx.pagerank(self.G, alpha=0.85)

        for node in self.G.nodes():
            self.G.nodes[node]['betweenness'] = betweenness.get(node, 0)
            self.G.nodes[node]['in_degree'] = in_degree.get(node, 0)
            self.G.nodes[node]['pagerank'] = pagerank.get(node, 0)
            # Scale node size by pagerank
            self.G.nodes[node]['size'] = 5 + (pagerank.get(node, 0) * 1000)

        return {
            'bridge_nodes': sorted(betweenness, key=betweenness.get, reverse=True)[:10],
            'top_amplifiers': sorted(in_degree, key=in_degree.get, reverse=True)[:10],
            'most_influential': sorted(pagerank, key=pagerank.get, reverse=True)[:10]
        }

    def detect_bridge_nodes(self) -> list[BridgeNode]:
        """Find accounts that link multiple platforms — most strategic nodes."""
        bridges = []
        for node in self.G.nodes():
            if self.G.nodes[node].get('type') != NodeType.ACCOUNT:
                continue
            connected_platforms = set(
                self.G.nodes[n].get('platform')
                for n in list(self.G.predecessors(node)) + list(self.G.successors(node))
                if self.G.nodes[n].get('platform')
            )
            if len(connected_platforms) >= 2:
                bridges.append(BridgeNode(
                    node_id=node,
                    platforms=connected_platforms,
                    betweenness=self.G.nodes[node]['betweenness']
                ))
        return sorted(bridges, key=lambda b: b.betweenness, reverse=True)

    def export_pyvis(self, output_path: str):
        """Export interactive HTML network — embeddable in Streamlit."""
        from pyvis.network import Network
        net = Network(height='600px', width='100%', bgcolor='#0d1117',
                     font_color='#ffffff', directed=True)
        net.from_nx(self.G)
        net.set_options("""{ "physics": { "stabilization": false,
            "barnesHut": { "gravitationalConstant": -8000 } } }""")
        net.save_graph(output_path)

    def export_gephi(self, output_path: str):
        """Export .gexf for Gephi analysis."""
        nx.write_gexf(self.G, output_path)

    def export_maltego(self, output_path: str):
        """Export .mtgx for Maltego — standard professional OSINT tool."""
        # Maltego MTGX format serialisation
        ...
```

**Temporal network (how the graph grows over time):**
```python
def build_temporal_graph(results: list[Result]) -> list[GraphSnapshot]:
    """Create graph snapshots at each hour — animate network growth."""
    snapshots = []
    for hour in time_range:
        results_to_hour = [r for r in results if r.published_at <= hour]
        snapshot = build_graph(results_to_hour)
        snapshots.append(GraphSnapshot(timestamp=hour, graph=snapshot,
                                       node_count=len(snapshot.nodes),
                                       edge_count=len(snapshot.edges)))
    return snapshots
```

---

### All graphs and visualisations

**Graph 1: Full interactive influence network (pyvis HTML)**
- Nodes coloured by type: content/account/domain/infra/bot-cluster
- Node size = PageRank (influence score)
- Edge thickness = interaction weight
- Edge colour = type (published/reposted/hosted/equivalent)
- Physics simulation: clusters naturally group
- Click node → side panel with full node intelligence card
- Filter controls: by platform, date range, node type, community
- Search: highlight specific account or domain in graph

**Graph 2: Community cluster cards**
- Each Louvain community gets a summary card:
  - Member count, dominant platform, primary language
  - Top entities mentioned, suspected role (source/amplifier/audience)
  - Internal coordination score

**Graph 3: Propagation chain view (new)**
- Linear directed view: seed node → amplifiers → secondary amplifiers
- Shows the exact path content travelled
- Each hop shows: time delay, platform switch, account type
- Like a family tree but for disinformation

**Graph 4: Infrastructure overlay**
- Same network but coloured by hosting infrastructure
- Domains on same ASN cluster visually
- Reveals: which "independent" sites are actually co-hosted

**Graph 5: Temporal animation**
- Plotly animated network: shows graph at T+0, T+6h, T+12h, T+24h
- Watch the network grow from seed to full operation
- Play/pause/scrub timeline controls

**Graph 6: Centrality leaderboard**
- Table: top 10 nodes by PageRank, Betweenness, In-degree
- Each row links to node detail panel
- Export as CSV for report

---

## MODULE 4 — BEHAVIOUR PROFILER & BOT DETECTION
### *"Prove an account is a bot or part of a coordinated network using only public data"*

---

### Basic (current state)
Placeholder coordination scores. No real analysis. Static fake numbers.

---

### Advanced (target state)

The Behaviour Profiler builds a **complete behavioural fingerprint** of every account that appears in an investigation. Using only publicly visible data, it produces a defensible, multi-signal bot probability score and coordination network map.

**Core intelligence concept:** Humans are unpredictable. Bots are regular. Coordinated networks are synchronised. These differences are measurable from public post timestamps, content patterns, and cross-account similarity — without ever accessing private data.

---

### Full data source map

| Signal | Source | Bot indicator |
|---|---|---|
| Post timestamps | Platform public timeline | High regularity (low std dev of intervals) |
| Posting hours | Platform public timeline | Posts only during narrow window (scheduled) |
| Content text | Platform public posts | High Jaccard similarity across accounts |
| Hashtag use | Platform public posts | Same hashtag within 60-second window |
| Language switching | `langdetect` on posts | Switches language on fixed schedule |
| Account creation date | Public profile data | New account + high volume = suspicious |
| Follower/following ratio | Public profile | Very high following, very low followers |
| Bio text | Public profile | Template bio matching other accounts |
| Profile image | Download + pHash | Same image on multiple accounts |
| URL patterns | Posts | Same URL structure across accounts |
| Cross-platform match | Module 1 semantic search | Same content appears across platforms |
| GDELT actor linkage | `gdeltdoc` | Account named in GDELT as disinfo actor |

---

### Exact techniques

**Multi-signal scoring engine:**
```python
import numpy as np
from itertools import combinations
from langdetect import detect as detect_lang

class BehaviourProfiler:

    WEIGHTS = {
        'posting_regularity': 0.20,
        'content_similarity':  0.25,
        'hashtag_sync':        0.20,
        'language_consistency': 0.10,
        'age_activity_ratio':  0.10,
        'bio_template_match':  0.08,
        'profile_image_reuse': 0.07,
    }

    def score_posting_regularity(self, timestamps: list[datetime]) -> float:
        """Low variation in post intervals = bot-like regularity."""
        if len(timestamps) < 5:
            return 0.0
        intervals = [(timestamps[i+1] - timestamps[i]).seconds
                     for i in range(len(timestamps)-1)]
        cv = np.std(intervals) / (np.mean(intervals) + 1)  # coefficient of variation
        return max(0, 1 - cv)  # 1.0 = perfectly regular (bot), 0.0 = random (human)

    def score_content_similarity(self, posts: list[str]) -> float:
        """High similarity across posts = template reuse = coordination."""
        if len(posts) < 2:
            return 0.0
        def jaccard(a: str, b: str) -> float:
            sa, sb = set(a.lower().split()), set(b.lower().split())
            return len(sa & sb) / len(sa | sb) if sa | sb else 0
        similarities = [jaccard(p1, p2) for p1, p2 in combinations(posts[:20], 2)]
        return np.percentile(similarities, 90)  # 90th percentile, not mean

    def score_hashtag_sync(self, posts_with_timestamps: list[tuple],
                            other_accounts: list[list], window_secs: int = 60) -> float:
        """Did multiple accounts use same hashtag within N seconds of each other?"""
        hashtag_times = {}
        for text, ts in posts_with_timestamps:
            tags = re.findall(r'#\w+', text.lower())
            for tag in tags:
                hashtag_times.setdefault(tag, []).append(ts)

        sync_count = 0
        for tag, times in hashtag_times.items():
            times_sorted = sorted(times)
            for i in range(len(times_sorted)-1):
                if (times_sorted[i+1] - times_sorted[i]).seconds <= window_secs:
                    sync_count += 1
        return min(1.0, sync_count / max(len(hashtag_times), 1))

    def score_language_consistency(self, posts: list[str]) -> float:
        """Authentic multilingual accounts switch naturally; bots switch on schedule."""
        langs = []
        for p in posts[:50]:
            try:
                langs.append(detect_lang(p))
            except:
                langs.append('unknown')
        if not langs:
            return 0.0
        # Count sudden switches (not gradual bilingual use)
        switches = sum(1 for i in range(len(langs)-1)
                      if langs[i] != langs[i+1] and langs[i] != 'unknown')
        # Bots switch language exactly, often on a fixed schedule
        switch_rate = switches / len(langs)
        return switch_rate  # High switch rate + high regularity = suspicious

    def detect_coordinated_cluster(self, accounts: list[AccountProfile]) -> list[ClusterResult]:
        """Find accounts that are coordinating with each other."""
        clusters = []
        # Method 1: Content similarity across accounts
        for a1, a2 in combinations(accounts, 2):
            sim = self.score_content_similarity(a1.recent_posts + a2.recent_posts)
            if sim > 0.7:
                clusters.append(CoordinationPair(a1, a2, sim, 'content_match'))

        # Method 2: Simultaneous hashtag use
        all_hashtag_events = self._collect_hashtag_events(accounts)
        sync_pairs = self._find_sync_pairs(all_hashtag_events, window_secs=60)
        clusters.extend(sync_pairs)

        # Method 3: Profile image hash match
        image_hashes = {a.id: a.profile_image_hash for a in accounts}
        for a1, a2 in combinations(accounts, 2):
            if hamming_distance(image_hashes[a1.id], image_hashes[a2.id]) < 10:
                clusters.append(CoordinationPair(a1, a2, 1.0, 'profile_image_match'))

        return merge_clusters(clusters)  # Merge overlapping pairs into groups

    def full_profile(self, account: AccountData) -> BehaviourProfile:
        scores = {
            'posting_regularity': self.score_posting_regularity(account.post_timestamps),
            'content_similarity': self.score_content_similarity(account.post_texts),
            'hashtag_sync': self.score_hashtag_sync(account.posts_with_times, []),
            'language_consistency': self.score_language_consistency(account.post_texts),
            'age_activity_ratio': self._age_activity(account),
            'bio_template_match': self._bio_similarity(account),
            'profile_image_reuse': self._image_reuse(account),
        }
        bot_probability = sum(
            scores[k] * self.WEIGHTS[k] for k in scores
        )
        classification = (
            'Confirmed bot' if bot_probability > 0.85 else
            'Probable bot' if bot_probability > 0.70 else
            'Coordinated' if bot_probability > 0.50 else
            'Suspicious' if bot_probability > 0.35 else
            'Authentic'
        )
        return BehaviourProfile(scores=scores, bot_probability=bot_probability,
                                classification=classification)
```

---

### All graphs and visualisations

**Graph 1: Bot probability radar chart**
- 7-axis radar: regularity / content_sim / hashtag_sync / language / age / bio / image
- One radar per account
- Overlay multiple accounts to compare fingerprints visually

**Graph 2: Posting pattern heatmap**
- X: hour of day (0-23), Y: day of week
- Cell colour: post count
- Human pattern: irregular, clustered around waking hours in one timezone
- Bot pattern: uniform across all hours, or only posting in 2-3 hour window

**Graph 3: Synchronised burst timeline**
- For a cluster of accounts: show each account as a row
- X: time, Dots: each post
- When dots align vertically across rows = synchronised posting burst
- Alert line: highlight windows where 5+ accounts posted within 60 seconds

**Graph 4: Content similarity matrix**
- NxN matrix where N = accounts in investigation
- Cell colour = Jaccard similarity between account's post sets
- Dark diagonal = self-similarity (always 1.0)
- Off-diagonal dark cells = coordinated pair

**Graph 5: Account network (identity graph)**
- Nodes: accounts
- Edges: coordination signal (content match / image match / hashtag sync)
- Edge label: type of signal
- Reveals: community structure of coordinated network

**Graph 6: Cross-platform identity bridge**
- Shows same account appearing on multiple platforms (matched by profile image pHash, bio text similarity, URL patterns)
- Visual: account node with spokes to each platform icon where it appears

---

## MODULE 5 — MEDIA FORENSICS LAB
### *"Prove an image is fake, old, misattributed, or AI-generated"*

---

### Basic (current state)
Not implemented. `imagehash` mentioned but no pipeline built.

---

### Advanced (target state)

The Media Forensics Lab is a **full image and video provenance engine**. For every piece of media encountered in an investigation, it answers: where did this first appear, has it been manipulated, is it AI-generated, where was it taken, and has it been recycled with a false caption.

**Core intelligence concept:** Recycled imagery is the most common visual disinformation technique. A 2019 protest photo gets captioned as 2025 atrocity. The pipeline finds the original source and proves the mismatch.

---

### Full data source map

| Analysis | Tool/API | Free? | What it finds |
|---|---|---|---|
| Reverse image search | Google Lens via CSE | 100/day free | Where image appears across the web |
| Reverse image search | Yandex Images | Scrape public | Better for Urdu/Asian content than Google |
| Reverse image search | TinEye API | 150/month free | Exact + near-duplicate matches with dates |
| Perceptual hash | `imagehash` pHash/dHash | Free local | Near-duplicate detection (crop/resize/filter) |
| EXIF extraction | `exifread` | Free local | GPS, device, timestamp, software |
| GPS verification | OpenStreetMap/Nominatim | Free | Reverse geocode GPS to location name |
| AI detection | Hive Moderation API | 100/day free | AI-generated probability (0-100%) |
| AI detection | `CNNDetection` model | Free local | Alternative deepfake detection |
| Video keyframes | `ffmpeg-python` | Free local | Extract one frame every N seconds |
| Audio transcription | `openai-whisper` | Free local | Multilingual audio → text |
| Video hash | `videohash` | Free local | Perceptual video fingerprint |
| Error level analysis | `PIL` + custom | Free local | JPEG compression inconsistencies = edit |
| Metadata strip detect | `exifread` | Free local | Missing EXIF = likely processed/edited |
| Face detection | `opencv` Haar cascade | Free local | Are there faces? (for PimEyes follow-up) |

---

### Exact techniques

**Complete image analysis pipeline:**
```python
import exifread, imagehash, requests
from PIL import Image, ImageChops, ImageEnhance
import numpy as np

class MediaForensicsLab:

    def analyse_image(self, image_path: str, image_url: str = None) -> ImageIntelligence:
        img = Image.open(image_path)

        # 1. EXIF deep extraction
        with open(image_path, 'rb') as f:
            exif_tags = exifread.process_file(f, details=True)
        gps = self._extract_gps(exif_tags)
        device = str(exif_tags.get('Image Make', 'Unknown'))
        original_timestamp = str(exif_tags.get('EXIF DateTimeOriginal', None))
        software = str(exif_tags.get('Image Software', None))
        exif_missing = len(exif_tags) < 5  # Social platforms strip EXIF

        # 2. Perceptual hashing (4 algorithms for robustness)
        phash = str(imagehash.phash(img, hash_size=16))
        dhash = str(imagehash.dhash(img, hash_size=16))
        whash = str(imagehash.whash(img))
        ahash = str(imagehash.average_hash(img))

        # 3. Error Level Analysis (detect edited regions)
        ela_result = self._error_level_analysis(image_path, quality=90)

        # 4. Reverse image search (parallel)
        matches = await asyncio.gather(
            self._google_reverse_search(image_path),
            self._yandex_reverse_search(image_path),
            self._tineye_search(image_url or image_path),
        )
        all_matches = [m for batch in matches for m in batch]
        earliest = min(all_matches, key=lambda m: m.date) if all_matches else None

        # 5. AI detection
        ai_score = await self._hive_moderation_check(image_path)
        # Fallback: local CNN model
        if ai_score is None:
            ai_score = self._local_deepfake_detect(image_path)

        # 6. Face detection (for follow-up research)
        faces = self._detect_faces(img)

        # 7. Duplicate search against internal evidence DB
        known_hashes = db.get_all_image_hashes()
        duplicates = [
            h for h in known_hashes
            if imagehash.hex_to_hash(phash) - imagehash.hex_to_hash(h.phash) < 12
        ]

        # 8. GPS verification
        location_verified = None
        if gps:
            location_verified = self._reverse_geocode(gps['lat'], gps['lon'])

        return ImageIntelligence(
            phash=phash, dhash=dhash,
            exif_data=dict(exif_tags),
            gps=gps, gps_location=location_verified,
            device=device, original_timestamp=original_timestamp,
            software=software, exif_missing=exif_missing,
            reverse_search_matches=all_matches,
            earliest_occurrence=earliest,
            ai_probability=ai_score,
            ela_manipulation_detected=ela_result['manipulation_detected'],
            ela_heatmap=ela_result['heatmap_path'],
            faces_detected=faces,
            known_duplicates=duplicates,
            provenance_chain=self._build_provenance_chain(all_matches)
        )

    def _error_level_analysis(self, image_path: str, quality: int = 90) -> dict:
        """Detect edited regions via JPEG compression inconsistency."""
        original = Image.open(image_path).convert('RGB')
        buffer = BytesIO()
        original.save(buffer, 'JPEG', quality=quality)
        buffer.seek(0)
        resaved = Image.open(buffer).convert('RGB')
        diff = ImageChops.difference(original, resaved)
        # Amplify differences for visualisation
        diff_enhanced = ImageEnhance.Brightness(diff).enhance(15)
        ela_array = np.array(diff_enhanced)
        manipulation_score = ela_array.max() / 255
        return {
            'manipulation_detected': manipulation_score > 0.3,
            'manipulation_score': manipulation_score,
            'heatmap_path': save_ela_heatmap(diff_enhanced)
        }

    async def analyse_video(self, video_path: str) -> VideoIntelligence:
        import whisper, ffmpeg
        import videohash

        # 1. Extract keyframes every 5 seconds
        keyframes = self._extract_keyframes(video_path, interval=5)

        # 2. Whisper transcription (local, free, multilingual)
        model = whisper.load_model("small")  # ~500MB, good multilingual
        result = model.transcribe(video_path, task="transcribe")
        transcript = result['text']
        detected_language = result['language']
        segments = result['segments']  # timestamped transcript segments

        # 3. Perceptual video hash
        vh = videohash.VideoHash(path=video_path)
        video_hash_str = str(vh)

        # 4. Reverse search each keyframe (first 10 only)
        frame_matches = []
        for frame_path in keyframes[:10]:
            matches = await self._google_reverse_search(frame_path)
            frame_matches.append({'frame': frame_path, 'matches': matches})

        # 5. Audio-video sync check (detect dubbing)
        av_sync_score = self._check_av_sync(video_path)

        # 6. Known video hash lookup
        known_videos = db.get_all_video_hashes()
        duplicates = [v for v in known_videos
                     if vh.hamming_distance(v.hash) < 5]

        # 7. NER on transcript
        entities = extract_entities_multilingual(transcript)

        return VideoIntelligence(
            transcript=transcript,
            language=detected_language,
            transcript_segments=segments,
            keyframes=keyframes,
            frame_matches=frame_matches,
            video_hash=video_hash_str,
            av_sync_score=av_sync_score,
            known_duplicates=duplicates,
            entities=entities
        )
```

---

### All graphs and visualisations

**Graph 1: Provenance timeline**
- Horizontal timeline showing every known occurrence of this image/video
- Y: source credibility
- X: date
- First occurrence highlighted in green (origin)
- Each dot labelled with source platform and caption used
- Reveals: how caption changed as image was recycled

**Graph 2: ELA (Error Level Analysis) heatmap**
- Side-by-side: original image | ELA heatmap
- Red regions = edited areas
- Interpretation key: what different patterns mean
- Confidence score for manipulation

**Graph 3: Perceptual hash similarity tree**
- All near-duplicate versions of the image
- Tree structure showing how edits were applied (crop → filter → watermark)
- Each node = a unique version, edge = transformation applied

**Graph 4: Reverse search match map**
- World map: where has this image appeared geographically
- Colour by source credibility
- Timeline slider: filter by date range

**Graph 5: Frame-by-frame analysis grid (video)**
- Grid of keyframes with reverse search count per frame
- Highlight frames that appear on other sites (recycled footage)
- Click frame → show where else it appears

**Graph 6: Transcript entity map**
- NER visualisation on transcript text
- People, places, orgs highlighted in different colours
- Cross-reference against known actors in Module 3 network

---

## MODULE 6 — INFRASTRUCTURE ATTRIBUTION ENGINE
### *"Trace any website to its real owners, co-tenants, and state sponsors"*

---

### Basic (current state)
Not implemented. WHOIS mentioned but no code.

---

### Advanced (target state)

The Infrastructure Attribution Engine maps the **digital nervous system** of a propaganda operation. Every domain, IP address, hosting provider, registrar, and SSL certificate leaves traces that link apparently independent sites to a single coordinating entity.

**Core intelligence concept:** Operators reuse infrastructure because it's expensive and complex. The same registrar account, same /24 subnet, same SSL certificate provider, same nameserver — these are fingerprints left in public records that link "independent" sites to a single actor.

---

### Full data source map

| Layer | API/Tool | Free? | What it reveals |
|---|---|---|---|
| Domain registration | RDAP (iana.org) | Free | Registrar, country, dates, privacy shield |
| WHOIS history | ViewDNS.info API | 1000/month free | Past registrant data before privacy shield |
| Reverse WHOIS | WhoisXML API | 500/month free | All domains registered by same email/org |
| DNS records | `dnspython` | Free local | A, MX, NS, TXT, CNAME records |
| DNS history | SecurityTrails | 50/month free | IP changes over lifetime of domain |
| Certificate transparency | crt.sh (REST) | Unlimited free | All SSL certs, subdomains, issuance dates |
| IP geolocation | ip-api.com | 45/min free | Country, city, region, ISP |
| IP geolocation | ipinfo.io API | 50k/month free | ASN, org, hostname, timezone |
| ASN data | RIPEstat REST | Unlimited free | ASN owner, prefix, country, routing history |
| BGP routing | BGP.he.net | Unlimited free | AS routing relationships |
| Infrastructure scan | Shodan API | 100/month free | Open ports, server software, vulns |
| Site analysis | URLScan.io API | 5000/month free | Full technical scan, screenshot, outbound links |
| IP reputation | GreyNoise API | 100/day free | Bot/scanner/malicious classification |
| Domain reputation | VirusTotal API | 500/day free | Malicious flags, passive DNS, historical data |
| Hosting neighbours | Shodan same-IP | Free | Other sites on same server |

---

### Exact techniques

**Full domain intelligence pipeline:**
```python
import asyncio, requests, whois, socket, ssl
import dns.resolver, json

class InfrastructureEngine:

    async def full_domain_profile(self, domain: str) -> DomainProfile:
        """Run all 14 data sources in parallel."""
        results = await asyncio.gather(
            self._rdap_lookup(domain),
            self._whois_history(domain),
            self._crt_sh_lookup(domain),
            self._dns_records(domain),
            self._security_trails_dns(domain),
            self._ip_geolocation(domain),
            self._asn_lookup(domain),
            self._shodan_scan(domain),
            self._urlscan_submit(domain),
            self._greynoise_check(domain),
            self._virustotal_domain(domain),
            self._shodan_neighbours(domain),
            self._reverse_whois(domain),
            self._ssl_cert_analysis(domain),
            return_exceptions=True
        )
        return self._merge_profile(domain, results)

    async def _crt_sh_lookup(self, domain: str) -> CertData:
        """Find all SSL certificates ever issued for this domain."""
        r = requests.get(f"https://crt.sh/?q={domain}&output=json", timeout=10)
        certs = r.json()
        return CertData(
            total_certs=len(certs),
            subdomains=list(set(c['name_value'] for c in certs)),
            issuers=list(set(c['issuer_name'] for c in certs)),
            earliest_cert=min(c['not_before'] for c in certs),
            latest_cert=max(c['not_before'] for c in certs),
            cert_frequency_by_month=self._cert_timeline(certs)
        )

    async def _asn_lookup(self, domain: str) -> ASNData:
        """RIPEstat: who owns the network this domain is hosted on."""
        ip = socket.gethostbyname(domain)
        r = requests.get(f"https://stat.ripe.net/data/prefix-overview/data.json?resource={ip}")
        data = r.json()['data']
        return ASNData(
            ip=ip, asn=data['asns'][0]['asn'],
            asn_name=data['asns'][0]['holder'],
            prefix=data['resource'],
            country=data['asns'][0].get('country', 'Unknown')
        )

    def detect_infrastructure_clusters(self, profiles: list[DomainProfile]) -> list[InfraCluster]:
        """Find domains that share infrastructure — reveals coordinated networks."""
        clusters = []

        # Method 1: Shared /24 subnet
        subnet_groups = {}
        for p in profiles:
            subnet = '.'.join(p.ip.split('.')[:3]) + '.0/24'
            subnet_groups.setdefault(subnet, []).append(p.domain)
        for subnet, domains in subnet_groups.items():
            if len(domains) >= 2:
                clusters.append(InfraCluster(
                    type='shared_subnet', shared_value=subnet,
                    domains=domains, confidence=0.75
                ))

        # Method 2: Same registration date window (±7 days)
        date_groups = {}
        for p in profiles:
            if p.registration_date:
                week_bucket = p.registration_date.isocalendar()[1]  # ISO week number
                date_groups.setdefault(week_bucket, []).append(p)
        for week, domain_profiles in date_groups.items():
            if len(domain_profiles) >= 2:
                # Also check same registrar
                registrars = set(p.registrar for p in domain_profiles)
                if len(registrars) == 1:  # Same registrar same week = very suspicious
                    clusters.append(InfraCluster(
                        type='coordinated_registration',
                        shared_value=f"week_{week}_{list(registrars)[0]}",
                        domains=[p.domain for p in domain_profiles],
                        confidence=0.90
                    ))

        # Method 3: Same nameserver
        ns_groups = {}
        for p in profiles:
            for ns in p.nameservers:
                ns_groups.setdefault(ns, []).append(p.domain)
        for ns, domains in ns_groups.items():
            if len(domains) >= 3:  # 3+ domains sharing a nameserver = notable
                clusters.append(InfraCluster(
                    type='shared_nameserver', shared_value=ns,
                    domains=domains, confidence=0.65
                ))

        # Method 4: Reverse WHOIS — same registrant email
        email_groups = {}
        for p in profiles:
            if p.registrant_email:
                email_groups.setdefault(p.registrant_email, []).append(p.domain)
        for email, domains in email_groups.items():
            if len(domains) >= 2:
                clusters.append(InfraCluster(
                    type='shared_registrant', shared_value=email,
                    domains=domains, confidence=0.95  # Highest confidence
                ))

        return merge_overlapping_clusters(clusters)
```

---

### All graphs and visualisations

**Graph 1: Infrastructure map (geo + network combined)**
- World map (Folium): each domain plotted at its hosting location
- Line connecting domains in same cluster
- Cluster colour: type of connection (subnet / registrant / nameserver / date)
- Click domain → full profile card

**Graph 2: Domain timeline (coordinated setup detection)**
- X: time, Y: domains
- Dot = domain registration date
- Vertical band highlighting: when 3+ domains registered within same week
- Colour: registrar (shows if same account registered them all)

**Graph 3: Infrastructure cluster cards**
- One card per detected cluster:
  - Cluster type (subnet/registrant/nameserver/date)
  - Member domains
  - Confidence score
  - Shared infrastructure value (the subnet / email / nameserver)
  - Risk implication

**Graph 4: ASN ownership tree**
- Tree: Country → Telecom/ISP → ASN → IP prefix → Domains
- Highlight known state-controlled ASNs (PTCL, China Telecom, etc.)
- Click ASN → see all domains in investigation hosted there

**Graph 5: Certificate issuance timeline**
- X: time, Y: domain
- Dot = SSL cert issued
- Pattern: coordinated ops often issue certs the same day (before launch)
- Reveals preparation timeline

**Graph 6: Shodan neighbours**
- For each domain: show all other sites on same server
- Are other sites on that server also propaganda outlets?
- Table: neighbour domain + category + registration date

---

## MODULE 7 — DISARM TACTIC CLASSIFIER
### *"Map every piece of content to a named influence operation technique"*

---

### Basic (current state)
Claude API called per item. No local fallback. Single tactic returned. No confidence. Expensive.

---

### Advanced (target state)

A **three-layer classification system** that tags every result with DISARM tactics, confidence scores, technique reasoning, and aggregates findings into a campaign-level playbook analysis.

---

### Three-layer classification architecture

```python
from groq import Groq
import anthropic
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.svm import LinearSVC

class DISARMClassifier:

    FULL_TAXONOMY = {
        # Phase 1: Plan
        "TA01": {"name": "Plan Strategy", "tactics": ["T0001", "T0002", "T0003"]},
        # Phase 2: Prepare
        "TA02": {"name": "Prepare Assets", "tactics": ["T0010", "T0011", "T0014"]},
        # Phase 3: Execute
        "TA03": {"name": "Execute", "tactics": ["T0015", "T0016", "T0017", "T0018",
                  "T0019", "T0020", "T0021", "T0022", "T0023"]},
        # Phase 4: Assess
        "TA04": {"name": "Assess", "tactics": ["T0030", "T0031"]},
    }

    TACTICS_DETAIL = {
        "T0001": "False context — real content, misleading framing",
        "T0002": "Fabricated content — entirely invented",
        "T0003": "Impersonation — fake account mimicking real entity",
        "T0004": "Astroturfing — fake grassroots appearance",
        "T0005": "State-sponsored influence — government-linked amplification",
        "T0006": "Emotional manipulation — fear, anger, outrage exploitation",
        "T0007": "Conspiracy narrative — unverified hidden-hand claims",
        "T0008": "Hack-and-leak — stolen materials published",
        "T0009": "Misattribution — attributed to wrong source",
        "T0010": "Selective emphasis — real facts, misleading selection",
        "T0011": "Exaggeration — real event, inflated severity",
        "T0012": "Decontextualisation — real content, removed context",
        "T0013": "Satire misrepresented as fact",
        "T0014": "Bot amplification — automated account coordination",
        "T0015": "Coordinated inauthentic behaviour",
        "T0016": "Cross-platform flooding — simultaneous multi-platform push",
        "T0017": "Hashtag hijacking — co-opting trending topics",
        "T0018": "Manufactured consensus — making fringe seem mainstream",
        "T0019": "Targeting journalists — harassment to silence reporting",
        "T0020": "Redirect — pointing to existing content to amplify",
    }

    def __init__(self):
        # Layer 1: Fast local TF-IDF + SVM (trained on DISARM examples)
        self.local_classifier = self._load_local_classifier()
        # Layer 2: Groq LLM (fast, free tier)
        self.groq = Groq(api_key=GROQ_API_KEY)
        # Layer 3: Claude (deep reasoning for complex cases)
        self.claude = anthropic.Anthropic(api_key=CLAUDE_API_KEY)

    async def classify(self, content: str, confidence_threshold: float = 0.75) -> DISARMResult:
        # Layer 1: Local classifier (instant, no API cost)
        local_pred = self.local_classifier.predict([content])[0]
        local_proba = self.local_classifier.predict_proba([content]).max()

        if local_proba >= confidence_threshold:
            return DISARMResult(
                tactic_id=local_pred, confidence=local_proba,
                method='local', reasoning='Pattern match'
            )

        # Layer 2: Groq (fast LLM — 6000 tokens/min free)
        groq_result = await self._classify_groq(content)
        if groq_result.confidence >= confidence_threshold:
            return groq_result

        # Layer 3: Claude (deep reasoning for ambiguous content)
        return await self._classify_claude(content)

    async def _classify_groq(self, content: str) -> DISARMResult:
        prompt = f"""Classify this content using DISARM framework.
Return JSON: {{"tactic_id": "T00XX", "tactic_name": "...",
"confidence": 0.0-1.0, "reasoning": "one sentence",
"secondary_tactics": ["T00XX"], "phase": "TA0X"}}

DISARM tactics reference:
{json.dumps(self.TACTICS_DETAIL, indent=2)}

Content to classify:
{content[:800]}"""

        resp = self.groq.chat.completions.create(
            model="llama-3.3-70b-versatile",
            messages=[{"role": "user", "content": prompt}],
            response_format={"type": "json_object"},
            temperature=0.1
        )
        data = json.loads(resp.choices[0].message.content)
        return DISARMResult(**data, method='groq')

    def campaign_analysis(self, classified_results: list[DISARMResult]) -> CampaignPlaybook:
        """Aggregate individual classifications into campaign-level playbook."""
        tactic_counts = Counter(r.tactic_id for r in classified_results)
        phase_distribution = Counter(r.phase for r in classified_results)

        primary_tactic = tactic_counts.most_common(1)[0][0]
        playbook_pattern = self._identify_playbook(tactic_counts)

        return CampaignPlaybook(
            primary_tactic=primary_tactic,
            tactic_distribution=dict(tactic_counts),
            phase_distribution=dict(phase_distribution),
            playbook_pattern=playbook_pattern,  # e.g., "Seeding + Amplification"
            estimated_sophistication=self._score_sophistication(tactic_counts),
            likely_actor_type=self._infer_actor(tactic_counts, phase_distribution)
        )
```

---

### All graphs and visualisations

**Graph 1: DISARM matrix heatmap**
- Full DISARM matrix: phases on X, tactics on Y
- Cell colour = number of results classified with that tactic
- Hot cells = the playbook being used
- Click cell → show all results using that tactic

**Graph 2: Tactic confidence distribution**
- For each tactic found: box plot of confidence scores
- Low confidence = classifier uncertain → analyst should review
- High confidence = strong signal

**Graph 3: Campaign phase wheel**
- Donut chart: TA01 Plan / TA02 Prepare / TA03 Execute / TA04 Assess
- Which phases are visible in the evidence?
- Interpretation: if TA02 visible (asset preparation), operation is still ramping up

**Graph 4: Tactic evolution over time**
- Line chart: tactic frequency by day
- Different tactics appear at different campaign phases
- Pattern: T0002 Fabricated content appears first, then T0004 Astroturfing

**Graph 5: Actor type classification card**
- Based on tactic combination: estimate actor type
- State actor / State-adjacent / Non-state political / Commercial / Hacktivist
- Evidence for each signal in the classification

---

## MODULE 8 — GEO INTELLIGENCE ENGINE
### *"Where does a narrative claim to originate, versus where does its infrastructure actually live?"*

---

### Basic (current state)
Not implemented.

---

### Advanced (target state)

The Geo Intelligence Engine **locates every actor, source, and piece of infrastructure** in geographic space and flags mismatches between claimed and actual origin — the defining signature of foreign influence operations.

---

### Full data source map

| Data | Source | Resolution |
|---|---|---|
| Domain IP location | ip-api.com (free) | City-level |
| Domain IP location | ipinfo.io (free tier) | City + ASN |
| Infrastructure location | Maxmind GeoLite2 (free download) | City-level, local |
| WHOIS registrant country | RDAP + WHOIS | Country |
| Post geotag | Platform API (when available) | GPS |
| Content language → region | `langdetect` + region mapping | Country |
| GDELT event location | `gdeltdoc` | Georeferenced |
| News source TLD | URL parsing | Country |
| ASN country | RIPEstat (free) | Country |
| Account location claim | Profile scrape | Self-reported |

---

### Exact techniques

```python
import folium
from folium.plugins import HeatMap, MarkerCluster, AntPath
import geoip2.database, requests

class GeoIntelligenceEngine:

    def __init__(self):
        # Local Maxmind GeoLite2 database (free download, update monthly)
        self.geoip_reader = geoip2.database.Reader('data/GeoLite2-City.mmdb')
        self.asn_reader = geoip2.database.Reader('data/GeoLite2-ASN.mmdb')

    def locate_domain(self, domain: str) -> GeoLocation:
        """Geolocate a domain via multiple methods, cross-validate."""
        import socket
        ip = socket.gethostbyname(domain)

        # Method 1: Local Maxmind (fast, no rate limit)
        try:
            geo = self.geoip_reader.city(ip)
            asn_data = self.asn_reader.asn(ip)
            return GeoLocation(
                ip=ip, domain=domain,
                country=geo.country.name,
                country_code=geo.country.iso_code,
                city=geo.city.name,
                lat=geo.location.latitude,
                lon=geo.location.longitude,
                asn=asn_data.autonomous_system_number,
                asn_org=asn_data.autonomous_system_organization
            )
        except:
            pass

        # Method 2: ip-api.com (fallback, 45 req/min)
        r = requests.get(f"http://ip-api.com/json/{ip}?fields=66846719")
        return GeoLocation(**r.json())

    def detect_origin_mismatch(self, content: ContentNode, infra: DomainProfile,
                                claimed_location: str = None) -> list[GeoAnomaly]:
        """Find mismatches between claimed and actual geographic origin."""
        anomalies = []

        # Mismatch 1: Content claims location X, infrastructure in country Y
        if claimed_location and infra.hosting_country:
            claimed_country = self._resolve_location_to_country(claimed_location)
            if claimed_country and claimed_country != infra.hosting_country:
                anomalies.append(GeoAnomaly(
                    type='origin_infrastructure_mismatch',
                    claimed=claimed_location,
                    actual=infra.hosting_country,
                    severity='high',
                    confidence=0.85
                ))

        # Mismatch 2: Registrant country ≠ hosting country (common in ops)
        if infra.registrant_country and infra.hosting_country:
            if infra.registrant_country != infra.hosting_country:
                anomalies.append(GeoAnomaly(
                    type='registrant_hosting_mismatch',
                    claimed=infra.registrant_country,
                    actual=infra.hosting_country,
                    severity='medium',
                    confidence=0.70
                ))

        # Mismatch 3: Language of content ≠ claimed target audience region
        if content.language and claimed_location:
            expected_lang = REGION_TO_LANGUAGE.get(claimed_location)
            if expected_lang and content.language != expected_lang:
                anomalies.append(GeoAnomaly(
                    type='language_location_mismatch',
                    claimed=claimed_location,
                    actual=content.language,
                    severity='low',
                    confidence=0.50
                ))

        return anomalies

    def build_geo_map(self, investigation: Investigation) -> folium.Map:
        """Build full interactive geo intelligence map."""
        m = folium.Map(location=[30, 70], zoom_start=4,
                      tiles='CartoDB dark_matter')

        # Layer 1: Content origin heatmap
        heat_data = [(r.geo.lat, r.geo.lon, r.semantic_score)
                     for r in investigation.results if r.geo]
        HeatMap(heat_data, radius=15, blur=10).add_to(m)

        # Layer 2: Infrastructure nodes
        infra_cluster = MarkerCluster(name="Infrastructure").add_to(m)
        for domain in investigation.domains:
            folium.CircleMarker(
                location=[domain.geo.lat, domain.geo.lon],
                radius=8, color='#e24b4a', fill=True,
                popup=folium.Popup(self._domain_popup_html(domain), max_width=300),
                tooltip=f"🏛 {domain.domain} — {domain.hosting_country}"
            ).add_to(infra_cluster)

        # Layer 3: Propagation flow lines (AntPath animation)
        if investigation.propagation_chain:
            for step in investigation.propagation_chain:
                AntPath(
                    locations=[step.origin_coords, step.destination_coords],
                    color='#4a9eff', weight=2, opacity=0.8,
                    tooltip=f"{step.platform}: {step.time_delta}h delay"
                ).add_to(m)

        # Layer 4: Geo anomaly markers
        for anomaly in investigation.geo_anomalies:
            folium.Marker(
                location=[anomaly.lat, anomaly.lon],
                icon=folium.Icon(color='orange', icon='exclamation-sign'),
                popup=folium.Popup(anomaly.description, max_width=250)
            ).add_to(m)

        folium.LayerControl().add_to(m)
        return m
```

---

### All graphs and visualisations

**Graph 1: Master geo intelligence map (Folium)**
- Dark base map (CartoDB dark matter)
- Layer 1: Heatmap of content volume by region
- Layer 2: Infrastructure nodes (red circles) at hosting locations
- Layer 3: Animated flow lines showing propagation routes
- Layer 4: Orange warning markers at geo anomalies
- Layer control: toggle each layer independently

**Graph 2: Country attribution table**
- Columns: Domain | Claimed origin | Actual hosting | Registrant | Anomaly
- Colour rows: red = high mismatch, yellow = partial mismatch, green = consistent
- Sort by anomaly severity

**Graph 3: Hosting country breakdown**
- Treemap: countries by number of domains hosted there
- Colour by state-control classification (free/partly free/not free)
- Insight: if 80% of "independent" Kashmir news is hosted in Pakistan → state-adjacent

**Graph 4: Propagation flow sankey**
- Sankey diagram: source country → amplification country → target country
- Width = volume
- Shows: originated in Pakistan, amplified through UAE accounts, targeting UK Kashmiri diaspora

**Graph 5: Timezone anomaly chart**
- Posting hours converted to UTC
- Overlay: expected timezone for claimed location
- Pattern: accounts claiming to be in AJK but posting at 2am local = different timezone

---

## MODULE 9 — EVIDENCE LOCKER
### *"Cryptographic proof that this content existed, at this time, with this content"*

---

### Basic (current state)
Basic CSV export. No hashing. No archiving. Evidence can be challenged or denied.

---

### Advanced (target state)

The Evidence Locker is a **legally defensible evidence management system**. Every item is cryptographically fingerprinted, independently archived, and stored with immutable chain of custody metadata. If challenged, the analyst can prove the content existed at exactly that timestamp with that exact content.

---

### Exact techniques

```python
import hashlib, uuid, json
from datetime import datetime, timezone
from waybackpy import WaybackMachineSaveAPI

class EvidenceLocker:

    def lock_evidence(self, url: str, content: str, screenshot_path: str,
                      analyst_id: str, case_id: str,
                      auto_archive: bool = True) -> EvidenceRecord:
        """Lock evidence with cryptographic integrity."""

        # 1. Hash the raw content (SHA-256)
        content_bytes = content.encode('utf-8')
        content_hash = hashlib.sha256(content_bytes).hexdigest()
        content_size = len(content_bytes)

        # 2. Hash the screenshot
        with open(screenshot_path, 'rb') as f:
            screenshot_hash = hashlib.sha256(f.read()).hexdigest()

        # 3. Create combined manifest hash
        manifest = {
            'url': url, 'content_hash': content_hash,
            'screenshot_hash': screenshot_hash,
            'locked_at': datetime.now(timezone.utc).isoformat()
        }
        manifest_hash = hashlib.sha256(
            json.dumps(manifest, sort_keys=True).encode()
        ).hexdigest()

        # 4. Archive to Wayback Machine
        archive_url_wb = None
        if auto_archive:
            try:
                save_api = WaybackMachineSaveAPI(url, user_agent="SENTINEL-OSINT/3.0")
                archive_url_wb = save_api.save()
            except Exception as e:
                pass

        # 5. Archive to archive.ph (fallback)
        archive_url_ph = None
        try:
            r = requests.post('https://archive.ph/submit/',
                             data={'url': url}, allow_redirects=True, timeout=30)
            archive_url_ph = r.url
        except:
            pass

        # 6. Store in immutable evidence ledger
        record = EvidenceRecord(
            evidence_id=str(uuid.uuid4()),
            case_id=case_id,
            analyst_id=analyst_id,
            collected_at=datetime.now(timezone.utc).isoformat(),
            source_url=url,
            content_hash=content_hash,
            screenshot_hash=screenshot_hash,
            manifest_hash=manifest_hash,
            content_size_bytes=content_size,
            archive_wayback=archive_url_wb,
            archive_ph=archive_url_ph,
            locked=True,
            lock_timestamp=datetime.now(timezone.utc).isoformat(),
            version=1,
            # Cannot be edited after locking — edits create new version
        )
        db.insert_evidence(record)  # IMMUTABLE after this point

        return record

    def verify_integrity(self, evidence_id: str) -> IntegrityCheck:
        """Verify a locked evidence item hasn't been tampered with."""
        record = db.get_evidence(evidence_id)
        # Re-fetch content and re-hash
        current_content = fetch_url(record.source_url)
        current_hash = hashlib.sha256(current_content.encode()).hexdigest()

        return IntegrityCheck(
            evidence_id=evidence_id,
            original_hash=record.content_hash,
            current_hash=current_hash,
            content_matches=(current_hash == record.content_hash),
            content_deleted=(current_content is None),
            archive_available=(record.archive_wayback or record.archive_ph),
            integrity_status=(
                'INTACT' if current_hash == record.content_hash else
                'MODIFIED' if current_content else
                'DELETED — ARCHIVED COPY EXISTS'
            )
        )

    def export_chain_of_custody(self, case_id: str) -> str:
        """Generate formal chain of custody document."""
        records = db.get_case_evidence(case_id)
        return generate_chain_of_custody_pdf(records)
```

---

### All graphs and visualisations

**Graph 1: Evidence collection timeline**
- X: time of locking, Y: source platform
- Dot per evidence item
- Shows: when investigation was active, collection rhythm
- Gap detection: did analyst miss a period?

**Graph 2: Evidence integrity dashboard**
- Table: all locked items with current integrity status
- Traffic light: green=intact / yellow=modified / red=deleted(archived)
- One-click re-verify all items

**Graph 3: Source distribution donut**
- Breakdown of locked evidence by platform
- Hover: number of items, % of total, any integrity issues

**Graph 4: Chain of custody flow**
- For each evidence item: URL → SENTINEL lock → Wayback archive → archive.ph
- Shows all preservation layers for each item
- Visual confirmation that multiple independent archives exist

---

## MODULE 10 — RISK SCORE + INTELLIGENCE REPORT
### *"Turn 40 pieces of evidence into one executive brief that drives decisions"*

---

### Basic (current state)
CSV export only. No scoring. No narrative. No formal report.

---

### Advanced (target state)

The Report Generator takes every finding across all 9 modules and produces a **professional intelligence report** with executive summary, evidence table, network graph, risk score with full signal breakdown, and recommended actions — in PDF, DOCX, and STIX 2.1 formats.

---

### Risk scoring engine

```python
class RiskScoreEngine:

    SIGNALS = {
        # Infrastructure signals
        'shared_hosting_cluster': {
            'weight': 20, 'description': 'Multiple domains share hosting infrastructure',
            'module': 'M6'
        },
        'state_controlled_asn': {
            'weight': 30, 'description': 'Infrastructure hosted on state-controlled ASN',
            'module': 'M6'
        },
        'coordinated_registration': {
            'weight': 25, 'description': 'Domains registered same day, same registrar',
            'module': 'M6'
        },
        # Behavioural signals
        'bot_cluster_detected': {
            'weight': 25, 'description': 'Coordinated bot network amplifying narrative',
            'module': 'M4'
        },
        'cross_platform_sync': {
            'weight': 30, 'description': 'Simultaneous multi-platform narrative push',
            'module': 'M4'
        },
        # Velocity signals
        'velocity_anomaly': {
            'weight': 20, 'description': 'Unnatural volume spike detected by IQR analysis',
            'module': 'M2'
        },
        'three_stage_amplification': {
            'weight': 25, 'description': 'Classic seed→amplify→mainstream pattern detected',
            'module': 'M2'
        },
        # Media signals
        'deepfake_media': {
            'weight': 30, 'description': 'AI-generated imagery detected',
            'module': 'M5'
        },
        'recycled_imagery': {
            'weight': 20, 'description': 'Image first seen before claimed event date',
            'module': 'M5'
        },
        # Geo signals
        'geo_origin_mismatch': {
            'weight': 25, 'description': 'Content claimed origin ≠ infrastructure location',
            'module': 'M8'
        },
        # Tactic signals
        'state_sponsored_tactic': {
            'weight': 30, 'description': 'DISARM T0005 State-sponsored tactic classified',
            'module': 'M7'
        },
        'fabricated_content': {
            'weight': 25, 'description': 'DISARM T0002 Fabricated content detected',
            'module': 'M7'
        },
        # Network signals
        'cross_platform_bridges': {
            'weight': 15, 'description': 'Accounts bridging 3+ platforms identified',
            'module': 'M3'
        },
        'known_disinfo_domain': {
            'weight': 35, 'description': 'Domain in known disinformation registry',
            'module': 'M6'
        },
    }

    def compute(self, investigation: Investigation) -> RiskScore:
        triggered = {}
        for signal_id, signal in self.SIGNALS.items():
            if investigation.has_signal(signal_id):
                triggered[signal_id] = signal

        raw_score = sum(s['weight'] for s in triggered.values())
        capped = min(raw_score, 100)

        level = (
            'CRITICAL' if capped >= 75 else
            'HIGH'     if capped >= 50 else
            'MEDIUM'   if capped >= 25 else
            'LOW'
        )

        return RiskScore(
            score=capped, level=level,
            signals_triggered=triggered,
            signals_count=len(triggered),
            highest_weight_signal=max(triggered, key=lambda k: triggered[k]['weight']),
            confidence=self._compute_confidence(triggered, investigation)
        )
```

**Report generation via Claude API:**
```python
async def generate_executive_summary(investigation: Investigation,
                                      risk_score: RiskScore) -> str:
    """Claude generates the executive brief."""
    prompt = f"""You are a senior intelligence analyst writing an executive brief.

Investigation: {investigation.narrative_query}
Risk Level: {risk_score.level} ({risk_score.score}/100)
Evidence items: {investigation.evidence_count}
Signals triggered: {[s['description'] for s in risk_score.signals_triggered.values()]}
Primary tactic: {investigation.primary_disarm_tactic}
Infrastructure finding: {investigation.infra_summary}
Geo anomalies: {investigation.geo_anomalies_count}

Write a 3-paragraph executive brief:
Paragraph 1: What was found and how serious it is
Paragraph 2: Key evidence and patterns that support the assessment
Paragraph 3: Recommended actions for the receiving organisation

Write in clear, direct intelligence prose. No hedging. State what the evidence shows."""

    response = claude.messages.create(
        model="claude-sonnet-4-6",
        max_tokens=600,
        messages=[{"role": "user", "content": prompt}]
    )
    return response.content[0].text
```

**STIX 2.1 export:**
```python
from stix2 import (Campaign, ThreatActor, Infrastructure, Report,
                   Relationship, Bundle, Indicator, Malware)

def export_stix(investigation: Investigation, risk_score: RiskScore) -> Bundle:
    campaign = Campaign(
        name=investigation.narrative_query[:100],
        description=investigation.executive_summary,
        first_seen=investigation.earliest_evidence_date,
        confidence=int(risk_score.score),
        labels=[risk_score.primary_tactic]
    )
    infra_objects = [
        Infrastructure(
            name=domain.domain,
            infrastructure_types=['botnet'] if domain.is_suspicious else ['command-and-control'],
            first_seen=domain.registration_date
        )
        for domain in investigation.suspicious_domains
    ]
    relationships = [
        Relationship(relationship_type='uses', source_ref=campaign.id,
                    target_ref=infra.id)
        for infra in infra_objects
    ]
    return Bundle(objects=[campaign] + infra_objects + relationships)
```

---

### All graphs and visualisations

**Graph 1: Risk score gauge**
- Large circular gauge: 0-100, coloured zones (green/yellow/orange/red)
- Needle pointing to score
- Below: signal breakdown table with weight contribution of each triggered signal

**Graph 2: Signal radar chart**
- 6-axis radar: Infrastructure / Behaviour / Velocity / Media / Geo / Tactics
- Area filled proportional to signals triggered in each category
- Shows: which dimensions of the operation are strongest

**Graph 3: Evidence summary matrix**
- All locked evidence in a filterable, sortable grid (streamlit-aggrid)
- Columns: Source | Platform | Language | DISARM tactic | Bot score | Locked | Archived
- Click row → expand full evidence card

**Graph 4: Report preview panel**
- Live preview of report sections as they're generated
- Section toggles: include/exclude each section
- Export buttons: PDF | DOCX | STIX | HTML

**Graph 5: Investigation summary dashboard**
- One-screen view of all module outputs:
  - Narrative: 42 results, 96% peak similarity, 3 languages
  - Velocity: 840% spike at T+38h, GDELT confirms
  - Network: 127 nodes, 3 communities, 7 bridges, 19 bots
  - Infrastructure: 2 clusters, Rawalpindi ASN + Beijing ASN
  - Media: 4 images analysed, 1 recycled, 0 deepfake
  - Tactics: False context × 18, Astroturfing × 12
  - Geo: 3 anomalies (claimed AJK, hosted China/Pakistan)
  - Evidence: 18 items locked, all archived

---

## APPENDIX — ALL MODULE CONNECTIONS

```
M1 (Hunt) ──────→ M2 (Velocity): timestamps feed spread timeline
M1 (Hunt) ──────→ M3 (Network): results build influence graph
M1 (Hunt) ──────→ M4 (Behaviour): accounts extracted, profiled
M1 (Hunt) ──────→ M6 (Infrastructure): domains auto-submitted
M1 (Hunt) ──────→ M7 (DISARM): content classified per result
M1 (Hunt) ──────→ M9 (Evidence): high-confidence results prompted to lock

M2 (Velocity) ──→ M3 (Network): spike timestamps overlay on graph
M2 (Velocity) ──→ M4 (Behaviour): which accounts active at spike moment
M2 (Velocity) ──→ M10 (Risk): velocity anomaly signal

M3 (Network) ───→ M4 (Behaviour): bot clusters fed from network communities
M3 (Network) ───→ M6 (Infrastructure): infrastructure nodes in graph
M3 (Network) ───→ M10 (Risk): bridge nodes, cluster count → risk signals

M4 (Behaviour) →  M3 (Network): coordination scores → edge weights
M4 (Behaviour) →  M10 (Risk): bot cluster signal

M5 (Media) ─────→ M1 (Hunt): frame-extracted entities feed narrative search
M5 (Media) ─────→ M9 (Evidence): media items locked with provenance
M5 (Media) ─────→ M10 (Risk): deepfake / recycled imagery signals

M6 (Infra) ─────→ M3 (Network): infrastructure cluster edges
M6 (Infra) ─────→ M8 (Geo): hosting locations feed geo map
M6 (Infra) ─────→ M10 (Risk): state ASN, cluster signals

M7 (DISARM) ────→ M3 (Network): node colour / tactic label
M7 (DISARM) ────→ M10 (Risk): state-sponsored, fabricated signals

M8 (Geo) ───────→ M10 (Risk): geo anomaly signals
M8 (Geo) ───────→ M3 (Network): geo layer overlay

M9 (Evidence) ──→ M10 (Risk/Report): locked evidence feeds report
M9 (Evidence) ──→ All modules: integrity verification layer

M10 (Report) ←── All modules: final aggregation point
```

---

*SENTINEL Module Specs v3.1 | Advanced Implementation | Every module earns its intelligence*
*Build for the analyst who needs proof, not possibilities.*

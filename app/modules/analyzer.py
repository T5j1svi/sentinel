from __future__ import annotations
import math
from difflib import SequenceMatcher
import pandas as pd

# Advanced OSINT Imports - DISABLED for Render Free Tier OOM
_semantic_model = None
# try:
#     from sentence_transformers import SentenceTransformer
#     # We load a small, fast, multilingual model
#     _semantic_model = SentenceTransformer('paraphrase-multilingual-MiniLM-L12-v2')
# except ImportError:
#     _semantic_model = None

_nlp = None
# try:
#     import spacy
#     _nlp = spacy.load("en_core_web_sm")
# except ImportError:
#     _nlp = None

from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics.pairwise import cosine_similarity


from .utils import (
    PLATFORMS, PLATFORM_DOMAINS, REGIONAL_PLATFORMS, KASHMIR_AJK_PRIORITY_HANDLES,
    significant_terms, normalize_for_match, clean_text, phrase_variants,
    extract_x_handle, hash_text
)
from .translate_utils import build_translations
from .web_search import search_text_queries, search_images, fetch_public_metadata


def _platform_domain_budget(platform: str) -> int:
    # Large regional source packs are valuable, but unbounded domain x language x depth causes long runs.
    if platform in REGIONAL_PLATFORMS:
        return 4
    if platform in {"Websites"}:
        return 0
    return 1


def _budget_queries(query_rows: list[dict], max_total: int = 32) -> list[dict]:
    # Preserve high-value exact stages first, then platform/source-pack coverage.
    priority_prefix = {
        "01 Exact complete narrative": 0,
        "02 Translated exact narrative": 1,
        "03 Full narrative variant": 2,
        "04 Platform exact": 3,
        "05 Regional media pack": 4,
        "06 All significant terms": 5,
        "07 Platform all-terms": 6,
    }
    def rank(q):
        st = str(q.get("stage", ""))
        p = 99
        for k, v in priority_prefix.items():
            if st.startswith(k):
                p = v
                break
        # English/Urdu/Hindi are usually most useful for the user's region; still retain Chinese/Bengali early in translation stage.
        lang_rank = {"English": 0, "Urdu": 1, "Hindi": 2, "Chinese Simplified": 3, "Chinese Traditional": 4, "Bengali": 5}.get(q.get("language", ""), 9)
        return (p, lang_rank, len(q.get("query", "")))
    seen, out = set(), []
    for q in sorted(query_rows, key=rank):
        key = " ".join(str(q.get("query", "")).split()).lower()
        if not key or key in seen:
            continue
        seen.add(key)
        out.append(q)
        if len(out) >= max_total:
            break
    return out


def build_exact_narrative_queries(narrative: str, platforms: list[str], depth: int = 8, max_queries: int | None = None) -> tuple[list[dict], pd.DataFrame]:
    narrative = clean_text(narrative)
    translations = build_translations(narrative)
    terms = significant_terms(narrative)
    variants = phrase_variants(narrative)
    query_rows: list[dict] = []

    def add(stage, label, lang, query, method="", platform_hint="", strength="normal"):
        if query and query.strip():
            query_rows.append({
                "stage": stage,
                "label": label,
                "language": lang,
                "query": query.strip(),
                "translation_method": method,
                "platform_hint": platform_hint,
                "query_strength": strength,
            })

    # 1. Exact narrative always first.
    add("01 Exact complete narrative", "Exact phrase - English", "English", f'"{narrative}"', "original", strength="exact")

    # 2. Translated exact narrative, global search. This keeps Urdu/Chinese/Hindi/Bengali coverage without multiplying by every domain.
    for tr in translations:
        text = clean_text(tr.get("text", ""))
        lang = tr.get("language", "")
        if text and lang != "English" and text.lower() != narrative.lower():
            add("02 Translated exact narrative", f"Exact phrase - {lang}", lang, f'"{text}"', tr.get("method", ""), strength="exact_translation")

    # 3. A few full-phrase variants only. No broad keyword-only drift.
    for v in variants[1:3]:
        add("03 Full narrative variant", "Narrative variant", "English", f'"{v}"', "offline_variant", strength="variant")

    # 4. Platform/domain exact search in bounded form.
    # Social platforms get English exact phrase; YouTube/Telegram also get Urdu because regional Urdu video ecosystems matter.
    for platform in platforms:
        domains = PLATFORM_DOMAINS.get(platform, [])[:_platform_domain_budget(platform)]
        for d in domains:
            add(f"04 Platform exact - {platform}", f"{platform} exact", "English", f'site:{d} "{narrative}"', "original", platform_hint=platform, strength="platform_exact")
            if platform in {"YouTube", "Telegram", "Facebook", "Pakistan News"}:
                for tr in translations:
                    if tr.get("language") == "Urdu" and tr.get("text") and tr.get("text") != narrative:
                        add(f"04 Platform exact - {platform}", f"{platform} Urdu exact", "Urdu", f'site:{d} "{tr["text"]}"', tr.get("method", ""), platform_hint=platform, strength="platform_exact_translation")

    # 5. Regional media packs: top domains only; English narrative + Urdu where relevant.
    for platform in platforms:
        if platform not in REGIONAL_PLATFORMS:
            continue
        for d in PLATFORM_DOMAINS.get(platform, [])[:_platform_domain_budget(platform)]:
            add(f"05 Regional media pack - {platform}", f"{platform} source exact", "English", f'site:{d} "{narrative}"', "regional_exact", platform_hint=platform, strength="regional_exact")
            if platform in {"Pakistan News", "Kashmir / AJK News"}:
                urdu = next((tr for tr in translations if tr.get("language") == "Urdu"), None)
                if urdu and urdu.get("text") and urdu.get("text") != narrative:
                    add(f"05 Regional media pack - {platform}", f"{platform} Urdu source exact", "Urdu", f'site:{d} "{urdu["text"]}"', urdu.get("method", ""), platform_hint=platform, strength="regional_exact_translation")

    # 5b. User-curated Kashmir/AJK handles and digital media names. Bounded to avoid long runs.
    if "Kashmir / AJK News" in platforms or "Pakistan News" in platforms:
        for handle_name in KASHMIR_AJK_PRIORITY_HANDLES[:6]:
            add("05b Kashmir/AJK priority source", f"Priority source: {handle_name}", "English", f'"{narrative}" "{handle_name}"', "priority_source", platform_hint="Kashmir / AJK News", strength="regional_exact")

    # 6. Controlled all-term search as fallback only.
    if len(terms) >= 3:
        must_terms = " ".join([f'"{t}"' for t in terms[:6]])
        add("06 All significant terms", "All narrative terms", "English", must_terms, "term_controlled", strength="all_terms")
        # Only a few high-value platform all-term fallbacks.
        for platform in [p for p in platforms if p in {"X", "YouTube", "Pakistan News", "Websites"}]:
            for d in PLATFORM_DOMAINS.get(platform, [])[:2]:
                add("07 Platform all-terms", f"{platform} all terms", "English", f"site:{d} {must_terms}", "term_controlled", platform_hint=platform, strength="platform_terms")

    if max_queries is None:
        # Depth controls result count, not unlimited query multiplication.
        max_queries = max(14, min(34, int(depth) * 2 + 8))
    query_rows = _budget_queries(query_rows, max_total=max_queries)
    qdf = pd.DataFrame(query_rows).drop_duplicates(subset=["query"]).reset_index(drop=True)
    return query_rows, qdf


def _score_row(narrative: str, row: dict) -> dict:
    base = normalize_for_match(narrative)
    terms = significant_terms(narrative)
    hay_raw = f"{row.get('title','')} {row.get('snippet','')} {row.get('url','')}"
    hay = normalize_for_match(hay_raw)
    exact = bool(base and base in hay)
    term_hits = [t for t in terms if t.lower() in hay]
    term_ratio = len(term_hits) / max(1, len(terms))
    required_hits = max(2, math.ceil(len(terms) * 0.65)) if len(terms) >= 3 else len(terms)
    enough_terms = len(term_hits) >= required_hits
    seq = SequenceMatcher(None, base, hay[: max(40, len(base) * 4)]).ratio() if base and hay else 0
    generic_only_penalty = 18 if len(terms) >= 3 and len(term_hits) < required_hits else 0
    tfidf_hint = float(row.get("_tfidf", 0) or 0)
    semantic_score = float(row.get("_semantic_score", 0) or 0)

    sim = max(
        96 if exact else 0,
        88 if enough_terms and seq > 0.28 else 0,
        term_ratio * 76,
        seq * 70,
        tfidf_hint * 100,
        semantic_score * 100, # Use the new semantic score!
    ) - generic_only_penalty
    sim = round(max(0, min(100, sim)), 2)

    strength = row.get("query_strength", "")
    if exact or (strength in ["exact", "platform_exact", "regional_exact", "exact_translation", "platform_exact_translation", "regional_exact_translation"] and enough_terms and sim >= 78):
        conf = "High"; role = "Exact Narrative Match"
    elif enough_terms and sim >= 62:
        conf = "Medium"; role = "Candidate Amplifier"
    elif sim >= 45 and (enough_terms or len(terms) <= 2):
        conf = "Low"; role = "Related Narrative Lead"
    else:
        conf = "Low"; role = "Broad / Weak Lead"
        
    # Autonomous LLM Extraction for High Confidence nodes
    disarm_tags = []
    entities = []
    if conf == "High":
        try:
            from backend.services.llm_service import extract_tactics_and_entities
            llm_result = extract_tactics_and_entities(hay_raw)
            disarm_tags = llm_result.get("disarm_tags", [])
            entities = llm_result.get("entities", [])
        except Exception:
            pass

    row.update({
        "similarity_score": sim,
        "confidence": conf,
        "matched_terms": ", ".join(term_hits[:14]),
        "matched_term_count": len(term_hits),
        "required_term_count": required_hits,
        "exact_phrase_match": exact,
        "role": role,
        "result_id": hash_text(row.get("url", "") + row.get("title", "")),
        "disarm_tags": disarm_tags,
        "entities": entities,
    })
    return row


def compute_similarity(narrative: str, rows: list[dict]) -> list[dict]:
    if not rows:
        return []
    base = normalize_for_match(narrative)
    docs = [base] + [normalize_for_match((r.get("title", "") + " " + r.get("snippet", ""))) for r in rows]
    
    # 1. Fallback TF-IDF
    try:
        vec = TfidfVectorizer(ngram_range=(1, 4), min_df=1).fit_transform(docs)
        cos = cosine_similarity(vec[0:1], vec[1:]).flatten().tolist()
    except Exception:
        cos = [0.0] * len(rows)

    # 2. Advanced Semantic Similarity (Sentence Transformers)
    semantic_cos = [0.0] * len(rows)
    if _semantic_model:
        try:
            # We encode the base narrative and all the docs
            embeddings = _semantic_model.encode(docs, convert_to_tensor=True)
            import torch
            # Calculate cosine similarity of the narrative (index 0) against all others
            cosine_scores = torch.nn.functional.cosine_similarity(embeddings[0].unsqueeze(0), embeddings[1:])
            semantic_cos = cosine_scores.tolist()
        except Exception as e:
            print(f"[Analyzer] Semantic embedding failed: {e}")

    for idx, r in enumerate(rows):
        r["_tfidf"] = cos[idx]
        r["_semantic_score"] = semantic_cos[idx]
        _score_row(narrative, r)
        r.pop("_tfidf", None)
        r.pop("_semantic_score", None)
    return rows


def add_metadata(rows: list[dict], max_fetch: int = 8) -> list[dict]:
    for i, r in enumerate(rows):
        r.setdefault("metadata_status", "not_fetched")
        r.setdefault("og_image", "")
        if i < max_fetch:
            meta = fetch_public_metadata(r.get("url", ""), timeout=4)
            r["metadata_status"] = meta.get("status", "not_fetched")
            r["og_title"] = meta.get("title", "")
            r["og_description"] = meta.get("description", "")
            r["og_image"] = meta.get("image", "") or r.get("thumbnail_url", "")
            if meta.get("title") and not r.get("title"):
                r["title"] = meta.get("title")
            if meta.get("description") and not r.get("snippet"):
                r["snippet"] = meta.get("description")
        if not r.get("thumbnail_url") and r.get("og_image"):
            r["thumbnail_url"] = r["og_image"]
    return rows


def _sort_results(df: pd.DataFrame) -> pd.DataFrame:
    if df.empty:
        return df
    conf_order = {"High": 0, "Medium": 1, "Low": 2}
    df["_conf_order"] = df["confidence"].map(conf_order).fillna(3)
    stage_order = {
        "01 Exact complete narrative": 0,
        "02 Translated exact narrative": 1,
        "03 Full narrative variant": 2,
        "04 Platform exact": 3,
        "05 Regional media pack": 4,
        "06 All significant terms": 5,
        "07 Platform all-terms": 6,
    }
    def stg(s):
        s = str(s)
        for k, v in stage_order.items():
            if s.startswith(k): return v
        return 99
    df["_stage_order"] = df["search_stage"].apply(stg)
    return df.sort_values(["_conf_order", "similarity_score", "_stage_order"], ascending=[True, False, True]).drop(columns=["_conf_order", "_stage_order"], errors="ignore").reset_index(drop=True)


def run_narrative_investigation(narrative: str, platforms: list[str], depth: int = 8, fetch_metadata: bool = True, deadline_s: int = 150, progress_callback=None) -> dict:
    depth = max(3, min(int(depth), 12))
    max_queries = max(14, min(32, depth * 2 + 8))
    queries, qdf = build_exact_narrative_queries(narrative, platforms, depth, max_queries=max_queries)
    rows = search_text_queries(queries, max_results_each=max(3, min(depth, 8)), max_queries=max_queries, deadline_s=deadline_s, progress_callback=progress_callback)
    rows = compute_similarity(narrative, rows)
    if fetch_metadata:
        rows = add_metadata(rows, max_fetch=8)
    df = pd.DataFrame(rows)
    if not df.empty:
        df = _sort_results(df)

    # Small bounded image search. This prevents the media phase from dominating runtime.
    image_rows = []
    image_queries = [f'"{narrative}"', f'"{narrative}" video thumbnail']
    for tr in build_translations(narrative):
        if tr["language"] in {"Urdu", "Chinese Simplified"} and tr["text"] != narrative:
            image_queries.append(f'"{tr["text"]}"')
    seen_img = set()
    for iq in image_queries[:4]:
        for img in search_images(iq, max_results=6):
            key = img.get("image_url", "")
            if key and key not in seen_img:
                seen_img.add(key)
                img["image_query"] = iq
                image_rows.append(img)
    return {"queries": qdf, "results": df, "images": pd.DataFrame(image_rows), "translations": pd.DataFrame(build_translations(narrative))}


def build_target_account_queries(x_link: str, platforms: list[str], depth: int = 8) -> tuple[str, list[dict], pd.DataFrame]:
    handle = extract_x_handle(x_link)
    hclean = handle.lstrip("@")
    queries = []
    def add(stage, label, query, platform_hint="", strength="target"):
        if query:
            queries.append({"stage": stage, "label": label, "language": "English", "query": query, "translation_method": "source_handle", "platform_hint": platform_hint, "query_strength": strength})
    if handle:
        add("01 Source profile", "X profile", f"site:x.com/{hclean} {handle}", "X", "target_exact")
        add("02 Top public posts", "X top post candidates", f"site:x.com/{hclean}/status {handle}", "X", "target_posts")
        add("03 Same-platform amplification", "X mentions/reposts", f"site:x.com {handle} -site:x.com/{hclean}", "X", "target_mentions")
        add("04 Web references", "External references to handle", f'"{handle}" OR "{hclean}"', "Websites", "target_mentions")
        for p in platforms:
            for d in PLATFORM_DOMAINS.get(p, [])[:_platform_domain_budget(p)]:
                add("05 Cross-platform identity discovery", f"{p} same handle/name", f'site:{d} "{handle}" OR "{hclean}"', p, "identity")
    queries = _budget_queries(queries, max_total=max(12, min(26, depth * 2 + 6)))
    qdf = pd.DataFrame(queries).drop_duplicates(subset=["query"]).reset_index(drop=True)
    return handle, queries, qdf


def run_target_account_investigation(x_link: str, platforms: list[str], depth: int = 8, fetch_metadata: bool = True, deadline_s: int = 120, progress_callback=None) -> dict:
    depth = max(3, min(int(depth), 10))
    handle, queries, qdf = build_target_account_queries(x_link, platforms, depth)
    rows = search_text_queries(queries, max_results_each=max(3, min(depth, 8)), max_queries=max(12, min(26, depth * 2 + 6)), deadline_s=deadline_s, progress_callback=progress_callback)
    narrative_for_match = " ".join([handle, x_link]).strip()
    rows = compute_similarity(narrative_for_match, rows)
    hclean = handle.lstrip("@").lower()
    for r in rows:
        hay = f"{r.get('title','')} {r.get('snippet','')} {r.get('url','')}".lower()
        if hclean and (f"/{hclean}" in hay or f"@{hclean}" in hay):
            r["confidence"] = "High"
            r["role"] = "Candidate Same-Entity Account"
            r["similarity_score"] = max(float(r.get("similarity_score", 0)), 92.0)
        elif handle and handle.lower() in hay:
            r["confidence"] = "Medium"
            r["role"] = "Handle Mention / Amplification Node"
            r["similarity_score"] = max(float(r.get("similarity_score", 0)), 70.0)
        else:
            r["role"] = "Related Search Result"
    if fetch_metadata:
        rows = add_metadata(rows, max_fetch=8)
    df = pd.DataFrame(rows)
    if not df.empty:
        df = _sort_results(df)
    images = search_images(handle or x_link, max_results=10)
    return {"handle": handle, "queries": qdf, "results": df, "images": pd.DataFrame(images), "translations": pd.DataFrame()}


def summarize_results(df: pd.DataFrame) -> dict:
    if df is None or df.empty:
        return {"results": 0, "platforms": 0, "high_confidence": 0, "media_items": 0, "likely_amplifiers": 0}
    return {
        "results": int(len(df)),
        "platforms": int(df["platform"].nunique()) if "platform" in df else 0,
        "high_confidence": int((df.get("confidence", pd.Series(dtype=str)) == "High").sum()),
        "media_items": int(df.get("thumbnail_url", pd.Series(dtype=str)).fillna("").astype(str).ne("").sum()),
        "likely_amplifiers": int(df.get("role", pd.Series(dtype=str)).astype(str).str.contains("Amplifier|Exact|Same-Entity|Mention", case=False, na=False).sum()),
    }
# ==============================================================================
# --- NEW APPENDED CAPABILITIES: BEHAVIOR, BOT DETECTION & RISK REPORTING ---
# ==============================================================================
def calculate_bot_risk_score(df: pd.DataFrame) -> pd.DataFrame:
    """Evaluates handle randomness, missing metadata, and behavioral flags to generate a bot risk score."""
    if df is None or df.empty:
        return pd.DataFrame()
    
    import re
    out = df.copy()
    
    texts = (out.get("title", "").fillna("").astype(str) + " " + out.get("snippet", "").fillna("").astype(str)).tolist()
    
    def jaccard(a, b):
        sa, sb = set(a.lower().split()), set(b.lower().split())
        return len(sa & sb) / len(sa | sb) if sa | sb else 0
        
    def bot_score(row, idx):
        score = 10
        handle = str(row.get("handle", ""))
        title = str(row.get("title", ""))
        text = texts[idx]
        
        if re.search(r'\d{6,}', handle): score += 35
        if handle.lower() == "unknown": score += 15
        
        if len(title) < 10: score += 15
        
        role = str(row.get("role", ""))
        if "Amplifier" in role: score += 25
        
        # New Mathematical Feature: Jaccard Template Reuse
        max_jaccard = 0.0
        for i, other_text in enumerate(texts):
            if i != idx and len(other_text) > 20 and len(text) > 20:
                sim = jaccard(text, other_text)
                if sim > max_jaccard:
                    max_jaccard = sim
        if max_jaccard > 0.7:
            score += 30 # High penalty for synchronized template pasting
            
        return min(100, score), max_jaccard
        
    scores_and_jaccards = [bot_score(row, idx) for idx, row in out.iterrows()]
    out["bot_risk_score"] = [s[0] for s in scores_and_jaccards]
    out["template_reuse"] = [s[1] for s in scores_and_jaccards]
    
    def bot_classification(score):
        if score >= 75: return "High Likelihood Bot/Sockpuppet"
        if score >= 45: return "Suspicious / Automated Behavior"
        return "Likely Human / Standard Account"
        
    out["bot_classification"] = out["bot_risk_score"].apply(bot_classification)
    return out

def generate_risk_report(df: pd.DataFrame) -> dict:
    """Summarizes network-level risks based on the analysis dataframe."""
    if df is None or df.empty:
        return {"overall_risk": "Low", "summary": "No data available."}
        
    high_conf = len(df[df.get("confidence", "") == "High"])
    amplifiers = len(df[df.get("role", "").str.contains("Amplifier", na=False)])
    platforms_targeted = df.get("platform").nunique() if "platform" in df else 0
    
    overall_risk = "Low"
    if high_conf > 10 or amplifiers > 5:
        overall_risk = "Critical (Coordinated Activity Likely)"
    elif high_conf > 3 or amplifiers > 1:
        overall_risk = "Medium (Emerging Narrative)"
        
    return {
        "overall_risk": overall_risk,
        "high_confidence_nodes": high_conf,
        "suspected_amplifiers": amplifiers,
        "cross_platform_spread": platforms_targeted,
        "total_analyzed": len(df)
    }
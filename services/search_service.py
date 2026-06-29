"""
SENTINEL Intel — Search Service
Wraps existing app/modules/analyzer.py and web_search.py for FastAPI use.
"""
from __future__ import annotations
import sys
import time
from pathlib import Path

# Add the project root so we can import existing modules
PROJECT_ROOT = Path(__file__).resolve().parent.parent.parent
if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT))

from app.modules.analyzer import (
    run_narrative_investigation,
    run_target_account_investigation,
    compute_similarity,
    summarize_results,
    calculate_bot_risk_score,
    generate_risk_report,
)
from app.modules.utils import (
    PLATFORMS,
    PLATFORM_DOMAINS,
    hash_text,
    extract_x_handle,
    significant_terms,
    extract_personal_info_and_wallets,
)
from app.modules.translate_utils import build_translations
from app.modules.web_search import search_text_queries, search_images


def run_hunt(
    narrative: str,
    platforms: list[str],
    depth: int = 6,
    fetch_metadata: bool = True,
    fast_mode: bool = True,
    timeout_seconds: int = 120,
    progress_callback=None
) -> dict:
    """Run a full narrative hunt and return structured results."""
    start = time.monotonic()
    deadline = timeout_seconds if fast_mode else 240

    data = run_narrative_investigation(
        narrative,
        platforms,
        depth=depth,
        fetch_metadata=fetch_metadata,
        deadline_s=deadline,
        progress_callback=progress_callback
    )

    df = data.get("results")
    stats = summarize_results(df) if df is not None and not df.empty else {
        "results": 0, "platforms": 0, "high_confidence": 0, "media_items": 0, "likely_amplifiers": 0
    }
    elapsed = round(time.monotonic() - start, 2)

    results = []
    if df is not None and not df.empty:
        for _, row in df.iterrows():
            results.append({
                "id": str(row.get("result_id", hash_text(str(row.get("url", ""))))),
                "platform": str(row.get("platform", "")),
                "handle": str(row.get("handle", "")),
                "title": str(row.get("title", "")),
                "snippet": str(row.get("snippet", "")),
                "url": str(row.get("url", "")),
                "thumbnail_url": str(row.get("thumbnail_url", "")),
                "domain": str(row.get("domain", "")),
                "language": str(row.get("query_language", "")),
                "similarity_score": float(row.get("similarity_score", 0)),
                "confidence": str(row.get("confidence", "Low")),
                "role": str(row.get("role", "")),
                "matched_terms": str(row.get("matched_terms", "")),
                "matched_term_count": int(row.get("matched_term_count", 0)),
                "search_stage": str(row.get("search_stage", "")),
                "query_language": str(row.get("query_language", "")),
                "disarm_tags": [],
                "entities": [],
                "archived": False,
                "evidence_id": None,
            })

    queries_df = data.get("queries")
    queries_used = len(queries_df) if queries_df is not None and not queries_df.empty else 0

    return {
        "total_results": stats.get("results", 0),
        "results": results,
        "platforms_searched": stats.get("platforms", 0),
        "high_confidence": stats.get("high_confidence", 0),
        "media_items": stats.get("media_items", 0),
        "search_time_seconds": elapsed,
        "queries_used": queries_used,
    }


def run_bot_analysis(results: list[dict]) -> dict:
    """Run bot/coordination analysis on search results."""
    import pandas as pd
    df = pd.DataFrame(results)
    if df.empty:
        return {"total_analyzed": 0, "high_risk_count": 0, "suspicious_count": 0, "coordinated_clusters": 0, "scores": []}

    df_risk = calculate_bot_risk_score(df)
    report = generate_risk_report(df_risk)

    scores = []
    for _, row in df_risk.iterrows():
        handle = str(row.get("handle", "Unknown"))
        if handle == "Unknown" or not handle.strip():
            domain = str(row.get("domain", ""))
            handle = f"[{domain}]" if domain else f"Result ID: {str(row.get('result_id', ''))[:6]}"
        scores.append({
            "handle": handle,
            "platform": str(row.get("platform", "")),
            "bot_risk_score": int(row.get("bot_risk_score", 0)),
            "classification": str(row.get("bot_classification", "")),
            "posting_regularity": float(row.get("posting_regularity", 0.0)),
            "template_reuse": float(row.get("template_reuse", 0.0)),
            "account_age_ratio": float(row.get("account_age_ratio", 0.0)),
            "hashtag_sync": float(row.get("hashtag_sync", 0.0)),
            "signals": ["High template reuse"] if float(row.get("template_reuse", 0)) > 0.7 else [],
        })

    return {
        "total_analyzed": report.get("total_analyzed", 0),
        "high_risk_count": len([s for s in scores if s["bot_risk_score"] >= 75]),
        "suspicious_count": len([s for s in scores if 45 <= s["bot_risk_score"] < 75]),
        "coordinated_clusters": 0,
        "scores": scores,
    }


def get_available_platforms() -> list[str]:
    """Return all available platform/source pack names."""
    return PLATFORMS


def get_translations(text: str) -> list[dict]:
    """Get multilingual translations of text."""
    return build_translations(text)

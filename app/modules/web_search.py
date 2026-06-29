from __future__ import annotations
import time
import requests
from bs4 import BeautifulSoup
from typing import Iterable, Callable
from .utils import detect_platform, extract_handle_from_title_or_url, youtube_thumbnail, clean_text, domain_of

USER_AGENT = "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 Chrome/126 Safari/537.36 PropagandaDetectorOSINT/4.0"


def _make_ddgs():
    """Create ddgs client with graceful compatibility across versions."""
    try:
        from ddgs import DDGS
        try:
            return DDGS(timeout=8)
        except TypeError:
            return DDGS()
    except Exception:
        try:
            from duckduckgo_search import DDGS
            try:
                return DDGS(timeout=8)
            except TypeError:
                return DDGS()
        except Exception:
            return None


def _ddgs_text(query: str, max_results: int = 8) -> list[dict]:
    results = []
    client = _make_ddgs()
    if client is None:
        return results
    try:
        with client as ddgs:
            for r in ddgs.text(query, max_results=max(1, min(int(max_results), 10))):
                url = r.get("href") or r.get("url") or ""
                title = r.get("title") or ""
                body = r.get("body") or r.get("snippet") or ""
                if url:
                    results.append({"title": title, "url": url, "snippet": body, "source": "ddgs"})
    except Exception as e:
        # Return partial/empty rather than hanging or breaking the Streamlit run.
        return results
    return results


def _ddgs_images(query: str, max_results: int = 12) -> list[dict]:
    results = []
    client = _make_ddgs()
    if client is None:
        return results
    try:
        with client as ddgs:
            for r in ddgs.images(query, max_results=max(1, min(int(max_results), 12))):
                img = r.get("image") or r.get("thumbnail") or ""
                url = r.get("url") or r.get("source") or ""
                title = r.get("title") or ""
                if img:
                    results.append({"title": clean_text(title), "image_url": img, "source_url": url, "platform": detect_platform(url, title)})
    except Exception:
        pass
    return results


def _is_low_value_result(url: str, title: str) -> bool:
    hay = f"{url} {title}".lower()
    blockers = [
        "/search?", "?q=", "accounts.google", "support.google", "help.instagram", "help.twitter", "help.x.com",
        "login", "signin", "signup", "privacy", "terms", "policies", "ads.google", "play.google.com"
    ]
    return any(b in hay for b in blockers)


def search_text_queries(
    queries: Iterable[dict],
    max_results_each: int = 8,
    sleep_s: float = 0.05,
    max_queries: int = 32,
    deadline_s: int = 150,
    progress_callback: Callable[[str], None] | None = None,
) -> list[dict]:
    """Fast bounded public search.

    This intentionally caps query count and time. Without this, all platforms + all
    regional packs + translations can create hundreds of DDGS calls and appear to hang.
    """
    start = time.monotonic()
    seen_urls = set()
    seen_queries = set()
    all_rows = []

    clean_queries = []
    for q in queries:
        query = q.get("query", "") if isinstance(q, dict) else str(q)
        if not query or not query.strip():
            continue
        norm = " ".join(query.split()).lower()
        if norm in seen_queries:
            continue
        seen_queries.add(norm)
        clean_queries.append(q)
        if len(clean_queries) >= max_queries:
            break

    for idx, q in enumerate(clean_queries, 1):
        if time.monotonic() - start > deadline_s:
            if progress_callback:
                progress_callback(f"Time budget reached after {idx-1} queries. Returning partial results.")
            break
        query = q.get("query", "") if isinstance(q, dict) else str(q)
        label = q.get("label", "Search") if isinstance(q, dict) else "Search"
        lang = q.get("language", "English") if isinstance(q, dict) else "English"
        stage = q.get("stage", "Search") if isinstance(q, dict) else "Search"
        platform_hint = q.get("platform_hint", "") if isinstance(q, dict) else ""
        query_strength = q.get("query_strength", "normal") if isinstance(q, dict) else "normal"
        if progress_callback:
            progress_callback(f"{idx}/{len(clean_queries)}: {stage} | {label}")
        for r in _ddgs_text(query, max_results=max(2, min(max_results_each, 8))):
            url = r.get("url", "")
            title = clean_text(r.get("title", ""))
            if not url or url in seen_urls or _is_low_value_result(url, title):
                continue
            seen_urls.add(url)
            snippet = clean_text(r.get("snippet", ""))
            platform = detect_platform(url, title) or platform_hint or "Websites"
            handle = extract_handle_from_title_or_url(title, url)
            thumb = youtube_thumbnail(url)
            all_rows.append({
                "query_label": label,
                "query_language": lang,
                "search_stage": stage,
                "query_strength": query_strength,
                "platform": platform,
                "handle": handle,
                "title": title,
                "snippet": snippet,
                "url": url,
                "domain": domain_of(url),
                "thumbnail_url": thumb,
                "source_engine": r.get("source", "public_search"),
            })
        time.sleep(max(0.0, min(sleep_s, 0.2)))
    return all_rows


def search_images(query: str, max_results: int = 12) -> list[dict]:
    return _ddgs_images(query, max_results=max_results)


def fetch_public_metadata(url: str, timeout: int = 4) -> dict:
    """Best-effort metadata extraction only from publicly accessible pages. No login/bypass."""
    if not url:
        return {}
    out = {"url": url, "title": "", "description": "", "image": "", "site_name": "", "status": "not_fetched"}
    try:
        resp = requests.get(url, headers={"User-Agent": USER_AGENT}, timeout=timeout, allow_redirects=True)
        out["status_code"] = resp.status_code
        if resp.status_code >= 400:
            out["status"] = f"http_{resp.status_code}"
            return out
        ctype = resp.headers.get("content-type", "")
        if "text/html" not in ctype and "application/xhtml" not in ctype:
            out["status"] = "non_html"
            return out
        soup = BeautifulSoup(resp.text[:450000], "lxml")
        def meta(prop):
            tag = soup.find("meta", attrs={"property": prop}) or soup.find("meta", attrs={"name": prop})
            return tag.get("content", "").strip() if tag else ""
        out["title"] = meta("og:title") or meta("twitter:title") or (soup.title.string.strip() if soup.title and soup.title.string else "")
        out["description"] = meta("og:description") or meta("twitter:description") or meta("description")
        out["image"] = meta("og:image") or meta("twitter:image") or meta("twitter:image:src")
        out["site_name"] = meta("og:site_name")
        out["status"] = "ok"
    except Exception as e:
        out["status"] = f"error: {type(e).__name__}"
    return out

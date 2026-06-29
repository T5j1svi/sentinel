from __future__ import annotations
from pathlib import Path
import pandas as pd
import streamlit as st

from modules.utils import PLATFORMS, now_case_name, safe_filename
from modules.analyzer import run_narrative_investigation, run_target_account_investigation, summarize_results
from modules.graphing import build_cluster_graph, plot_cluster_graph, platform_bar
from modules.db import init_db, save_case, export_csv
from modules.media_utils import save_upload, compute_media_hash

st.set_page_config(page_title="Propaganda Detector", page_icon="🛰️", layout="wide", initial_sidebar_state="expanded")

CSS = """
<style>
:root { --pd-red:#ef4444; --pd-blue:#2563eb; --pd-slate:#0f172a; --pd-muted:#64748b; --pd-bg:#f8fafc; }
.block-container { padding-top: 1.4rem; max-width: 1580px; }
section[data-testid="stSidebar"] { background: linear-gradient(180deg,#f8fafc 0%,#eef2ff 100%); border-right:1px solid #e5e7eb; }
.pd-hero { padding: 26px 30px; border:1px solid #e5e7eb; border-radius: 22px; background: linear-gradient(135deg,#ffffff 0%,#f8fafc 48%,#eef2ff 100%); box-shadow: 0 10px 26px rgba(15,23,42,.06); margin-bottom: 22px; }
.pd-title { font-size: 44px; font-weight: 850; letter-spacing: -.04em; color:#111827; margin:0; }
.pd-subtitle { color:#64748b; font-size:15px; margin-top:6px; }
.metric-card { border:1px solid #e5e7eb; border-radius:16px; padding:18px 18px; background:#fff; box-shadow:0 8px 18px rgba(15,23,42,.04); min-height:92px; }
.metric-label { color:#64748b; font-size:13px; }
.metric-value { color:#111827; font-size:30px; font-weight:780; }
.section-card { border:1px solid #e5e7eb; border-radius:18px; background:#ffffff; padding:20px; margin: 12px 0 18px 0; box-shadow:0 8px 20px rgba(15,23,42,.035); }
.badge { display:inline-block; padding:4px 9px; border-radius:999px; background:#eef2ff; color:#3730a3; font-size:12px; margin-right:6px; margin-bottom:6px; border:1px solid #c7d2fe; }
.note { border-left:4px solid #f59e0b; background:#fffbeb; padding:12px 14px; border-radius:12px; color:#78350f; font-size:14px; }
.good { border-left:4px solid #22c55e; background:#f0fdf4; padding:12px 14px; border-radius:12px; color:#14532d; font-size:14px; }
.warn { border-left:4px solid #ef4444; background:#fef2f2; padding:12px 14px; border-radius:12px; color:#7f1d1d; font-size:14px; }
.media-card { border:1px solid #e5e7eb; border-radius:14px; padding:10px; background:#fff; height:100%; box-shadow:0 4px 12px rgba(15,23,42,.04); }
.small-muted { color:#64748b; font-size:12px; }
.query-pill { display:inline-block; margin:3px; padding:4px 8px; border-radius:10px; background:#f1f5f9; color:#334155; font-size:12px; }
</style>
"""
st.markdown(CSS, unsafe_allow_html=True)

init_db()
for d in ["exports", "database", "uploads", "graphs", "cases", "logs"]:
    Path(d).mkdir(exist_ok=True)


def ensure_state():
    defaults = {
        "case_name": now_case_name(),
        "last_results": pd.DataFrame(),
        "last_images": pd.DataFrame(),
        "last_queries": pd.DataFrame(),
        "last_translations": pd.DataFrame(),
        "last_input": "",
        "last_mode": "",
    }
    for k, v in defaults.items():
        if k not in st.session_state:
            st.session_state[k] = v


def render_metric(label, value):
    st.markdown(f'<div class="metric-card"><div class="metric-label">{label}</div><div class="metric-value">{value}</div></div>', unsafe_allow_html=True)


def render_header():
    st.markdown(
        """
        <div class="pd-hero">
          <div class="pd-title">🛰️ Propaganda Detector</div>
          <div class="pd-subtitle">Professional public-OSINT workbench with fast bounded narrative discovery, regional source packs, media previews and cluster mapping.</div>
          <div style="margin-top:12px;">
            <span class="badge">Complete phrase first</span>
            <span class="badge">Urdu + Chinese + Hindi + Bengali</span>
            <span class="badge">X / Instagram / Facebook / TikTok</span>
            <span class="badge">Bounded regional source packs</span>
            <span class="badge">Media gallery + cluster graph</span>
            <span class="badge">No fake URLs</span>
          </div>
        </div>
        """,
        unsafe_allow_html=True,
    )


def prepare_display_df(df: pd.DataFrame, min_similarity: int, show_low: bool):
    if df is None or df.empty:
        return pd.DataFrame()
    out = df.copy()
    if "similarity_score" in out:
        out = out[out["similarity_score"].fillna(0) >= min_similarity]
    if not show_low and "confidence" in out:
        out = out[out["confidence"].isin(["High", "Medium"])]
    cols = [
        "section", "search_stage", "query_language", "platform", "handle", "role", "confidence",
        "similarity_score", "matched_terms", "matched_term_count", "title", "snippet", "url", "thumbnail_url", "query_label", "domain"
    ]
    for c in cols:
        if c not in out.columns:
            out[c] = ""
    return out[cols].reset_index(drop=True)



def source_link_column_config():
    return {
        "url": st.column_config.LinkColumn(
            "Source URL",
            help="Click to open the original public source/result used for this row",
            display_text="Open source",
        ),
        "thumbnail_url": st.column_config.LinkColumn(
            "Thumbnail URL",
            help="Click to open the public thumbnail/media preview, if available",
            display_text="Open thumbnail",
        ),
        "source_url": st.column_config.LinkColumn(
            "Media source",
            help="Click to open the page from which the media preview was found",
            display_text="Open media source",
        ),
    }

def render_media_gallery(images_df: pd.DataFrame, results_df: pd.DataFrame):
    media_rows = []
    if results_df is not None and not results_df.empty:
        for _, r in results_df.iterrows():
            thumb = str(r.get("thumbnail_url", "") or r.get("og_image", "") or "")
            if thumb:
                media_rows.append({
                    "image_url": thumb,
                    "title": r.get("title", ""),
                    "source_url": r.get("url", ""),
                    "platform": r.get("platform", ""),
                    "type": "Post / page preview",
                    "confidence": r.get("confidence", ""),
                })
    if images_df is not None and not images_df.empty:
        for _, r in images_df.iterrows():
            media_rows.append({
                "image_url": r.get("image_url", ""),
                "title": r.get("title", ""),
                "source_url": r.get("source_url", ""),
                "platform": r.get("platform", ""),
                "type": "Public image result",
                "confidence": "Lead",
            })
    seen, clean = set(), []
    for r in media_rows:
        img = r.get("image_url", "")
        if img and img not in seen:
            seen.add(img); clean.append(r)
    if not clean:
        st.info("No public thumbnails/images were available. Many social platforms block previews unless results are public and indexed. Upload media/OCR text or use platform exports for better visual matching.")
        return
    st.markdown("### Public Media / Thumbnail Gallery")
    st.caption("These are public previews and search thumbnails. They are leads, not automatic proof of repost lineage.")
    cols = st.columns(4)
    for i, r in enumerate(clean[:32]):
        with cols[i % 4]:
            st.markdown('<div class="media-card">', unsafe_allow_html=True)
            try:
                st.image(r["image_url"], caption=f"{r.get('platform') or 'Media'} | {r.get('confidence','')}", width="stretch")
            except Exception:
                st.write("Preview unavailable")
            title = str(r.get("title", ""))[:95]
            st.markdown(f"<div class='small-muted'><b>{r.get('type','')}</b><br>{title}</div>", unsafe_allow_html=True)
            if r.get("source_url"):
                st.link_button("Open source", r["source_url"])
            st.markdown('</div>', unsafe_allow_html=True)


def render_results(mode_label: str, input_value: str, min_similarity: int, show_low: bool):
    df_all = st.session_state.last_results
    df = prepare_display_df(df_all, min_similarity, show_low)
    stats = summarize_results(df)
    m1, m2, m3, m4, m5 = st.columns(5)
    with m1: render_metric("Relevant results", stats["results"])
    with m2: render_metric("Platforms", stats["platforms"])
    with m3: render_metric("High confidence", stats["high_confidence"])
    with m4: render_metric("Amplifier candidates", stats["likely_amplifiers"])
    with m5: render_metric("Media previews", stats["media_items"])

    if df.empty:
        st.markdown('<div class="warn">No results after filtering. Reduce the minimum similarity, enable low-confidence leads, or paste the exact caption/hashtags/source URL.</div>', unsafe_allow_html=True)
        if st.session_state.last_queries is not None and not st.session_state.last_queries.empty:
            with st.expander("Queries used", expanded=True):
                st.dataframe(st.session_state.last_queries, width="stretch", height=300, column_config=source_link_column_config())
        return

    tabs = st.tabs(["Assessment", "Priority Leads", "Cluster Graph", "Media Gallery", "Queries & Translations", "Clickable Source Links", "Export"])
    with tabs[0]:
        st.markdown('<div class="section-card">', unsafe_allow_html=True)
        st.subheader("Assessment")
        high = df[df["confidence"] == "High"] if "confidence" in df else pd.DataFrame()
        med = df[df["confidence"] == "Medium"] if "confidence" in df else pd.DataFrame()
        if not high.empty:
            st.markdown(f'<div class="good">High-confidence exact or near-exact matches found: <b>{len(high)}</b>. Review these first for likely originators/amplifiers.</div>', unsafe_allow_html=True)
        elif not med.empty:
            st.markdown(f'<div class="note">Medium-confidence candidate matches found: <b>{len(med)}</b>. Treat as leads requiring manual verification.</div>', unsafe_allow_html=True)
        else:
            st.markdown('<div class="warn">Only broad leads found. Exact narrative may not be publicly indexed or may be hidden behind login/captcha/rate limits.</div>', unsafe_allow_html=True)
        st.plotly_chart(platform_bar(df), width="stretch")
        if st.session_state.last_translations is not None and not st.session_state.last_translations.empty:
            st.markdown("#### Language expansion used")
            pills = []
            for _, r in st.session_state.last_translations.iterrows():
                pills.append(f"<span class='query-pill'><b>{r.get('language')}</b>: {str(r.get('text'))[:80]}</span>")
            st.markdown(" ".join(pills), unsafe_allow_html=True)
        st.markdown('</div>', unsafe_allow_html=True)

    with tabs[1]:
        st.subheader("Priority leads")
        st.caption("Sorted by exact phrase / term coverage / confidence. Generic entity-only results are demoted.")
        top = df.sort_values(["confidence", "similarity_score"], ascending=[True, False])
        st.dataframe(top, width="stretch", height=580, column_config=source_link_column_config())

    with tabs[2]:
        center_type = "Target" if "Target" in mode_label else "Narrative"
        center = input_value[:80] if input_value else center_type
        G, metrics = build_cluster_graph(df, center_label=center, center_type=center_type)
        fig = plot_cluster_graph(G, title="Clustered narrative / platform / media candidate network")
        st.plotly_chart(fig, width="stretch")
        with st.expander("Network metrics", expanded=False):
            st.dataframe(metrics, width="stretch", height=390, column_config=source_link_column_config())
        st.markdown('<div class="note">Graph shows public-search candidate clusters by language, platform/source and similarity. It does not claim hidden repost lineage unless visible in public evidence.</div>', unsafe_allow_html=True)

    with tabs[3]:
        render_media_gallery(st.session_state.last_images, df)

    with tabs[4]:
        c1, c2 = st.columns(2)
        with c1:
            st.markdown("#### Translation / query expansion")
            if st.session_state.last_translations is not None and not st.session_state.last_translations.empty:
                st.dataframe(st.session_state.last_translations, width="stretch", height=300)
            else:
                st.info("No translation table for this mode.")
        with c2:
            st.markdown("#### Exact queries used")
            if st.session_state.last_queries is not None and not st.session_state.last_queries.empty:
                st.dataframe(st.session_state.last_queries, width="stretch", height=300, column_config=source_link_column_config())
            else:
                st.info("No queries recorded.")

    with tabs[5]:
        st.subheader("Clickable source evidence links")
        st.caption("Every row below retains the direct public URL used for evidence review. Open links manually and preserve screenshots/PDF captures for formal reporting.")
        link_cols = ["platform", "handle", "role", "confidence", "similarity_score", "title", "domain", "url", "thumbnail_url", "search_stage", "query_language"]
        for c in link_cols:
            if c not in df.columns:
                df[c] = ""
        links_df = df[link_cols].copy().drop_duplicates(subset=["url", "title"]).reset_index(drop=True)
        st.dataframe(links_df, width="stretch", height=520, column_config=source_link_column_config())
        st.markdown("#### Quick-open priority sources")
        for i, r in links_df.head(30).iterrows():
            url = str(r.get("url", "") or "")
            if not url:
                continue
            c1, c2, c3 = st.columns([1.2, 5.5, 1.6])
            with c1:
                st.markdown(f"**{r.get('platform','')}**")
                st.caption(f"{r.get('confidence','')} | {r.get('similarity_score','')}")
            with c2:
                st.markdown(str(r.get("title", "Untitled"))[:180])
                st.caption(str(r.get("domain", "")))
            with c3:
                st.link_button("Open source", url)

    with tabs[6]:
        st.subheader("Export and case storage")
        csv_data = df.to_csv(index=False, encoding="utf-8-sig")
        st.download_button("Download visible results CSV", data=csv_data, file_name=f"{safe_filename(st.session_state.case_name)}_visible_results.csv", mime="text/csv")
        all_csv_data = df_all.to_csv(index=False, encoding="utf-8-sig")
        st.download_button("Download all raw results CSV", data=all_csv_data, file_name=f"{safe_filename(st.session_state.case_name)}_all_raw_results.csv", mime="text/csv")
        if st.button("Save case to local SQLite database", type="primary"):
            save_case(st.session_state.case_name, mode_label, input_value, df_all)
            out_path = export_csv(st.session_state.case_name, df_all)
            st.success(f"Saved to database and exported: {out_path}")


ensure_state()

default_platforms = ["X", "Instagram", "Facebook", "TikTok", "Telegram", "YouTube", "Pakistan News", "China News", "Bangladesh News", "Tibet News"]

with st.sidebar:
    st.title("Case Controls")
    st.session_state.case_name = st.text_input("Case name", value=st.session_state.case_name)
    mode = st.selectbox(
        "Investigation Mode",
        ["Narrative / Keyword Investigation", "Target Account Investigation - X Link", "Media / Image Investigation", "Import CSV Dataset"],
    )
    platforms = st.multiselect("Platforms / source packs", PLATFORMS, default=default_platforms)
    depth = st.slider("Search depth per query (bounded)", 3, 12, 6, 1)
    min_similarity = st.slider("Minimum similarity shown", 0, 95, 45, 5)
    show_low = st.checkbox("Show low-confidence / broad leads", value=False)
    fetch_metadata = st.checkbox("Fetch public preview thumbnails / metadata", value=False)
    quick_mode = st.checkbox("Fast bounded mode (recommended)", value=True)
    timeout_budget = st.slider("Maximum runtime per search (seconds)", 45, 240, 120, 15)
    st.divider()
    st.markdown('<div class="note">Public data only. Fast bounded mode caps query volume to avoid 20+ minute searches. For deeper collection, run one platform/source pack at a time.</div>', unsafe_allow_html=True)

render_header()

if mode == "Narrative / Keyword Investigation":
    st.header("Narrative / Keyword Investigation")
    st.caption("Searches the complete narrative first, then translated variants and platform/source-pack exact searches. It avoids reducing the query to only broad terms such as 'Indian Army'.")
    narrative = st.text_area("Claim / caption / hashtag / keyword", placeholder="Example: Indian Army General removed", height=120)
    cols = st.columns([1, 3])
    with cols[0]:
        run = st.button("Run Narrative Search", type="primary")
    with cols[1]:
        st.markdown('<div class="small-muted">Tip: Paste the exact caption, hashtags, source URL and OCR text from the image/video. The exact phrase is searched before broad lead discovery.</div>', unsafe_allow_html=True)
    if run:
        if not narrative.strip():
            st.warning("Enter a narrative / caption / claim first.")
        else:
            with st.status("Running complete phrase, Urdu/Chinese/Hindi/Bengali, social and regional news searches...", expanded=True) as status:
                st.write("Building complete narrative and translation queries...")
                placeholder = st.empty()
                def _progress(msg):
                    placeholder.write(msg)
                data = run_narrative_investigation(narrative, platforms, depth, fetch_metadata, deadline_s=timeout_budget if quick_mode else 240, progress_callback=_progress)
                df = data["results"]
                if not df.empty:
                    df.insert(0, "section", "Narrative / Keyword Search")
                st.session_state.last_results = df
                st.session_state.last_images = data["images"]
                st.session_state.last_queries = data["queries"]
                st.session_state.last_translations = data["translations"]
                st.session_state.last_input = narrative
                st.session_state.last_mode = mode
                status.update(label="Search complete", state="complete")
    if not st.session_state.last_results.empty and st.session_state.last_mode == mode:
        render_results(mode, st.session_state.last_input, min_similarity, show_low)

elif mode == "Target Account Investigation - X Link":
    st.header("Target Account Investigation - X Link")
    st.caption("Extracts the central X handle, searches source profile/post candidates, same-platform amplification leads and cross-platform same-entity candidates.")
    x_link = st.text_input("X / Twitter profile or post link", placeholder="https://x.com/handle/status/123456789")
    run = st.button("Run Target Investigation", type="primary")
    if run:
        if not x_link.strip():
            st.warning("Enter an X link or handle first.")
        else:
            with st.status("Investigating target account, X propagation and cross-platform identity candidates...", expanded=True) as status:
                placeholder = st.empty()
                def _progress(msg):
                    placeholder.write(msg)
                data = run_target_account_investigation(x_link, platforms, depth, fetch_metadata, deadline_s=timeout_budget if quick_mode else 180, progress_callback=_progress)
                df = data["results"]
                if not df.empty:
                    df.insert(0, "section", "Target Account Investigation")
                st.session_state.last_results = df
                st.session_state.last_images = data["images"]
                st.session_state.last_queries = data["queries"]
                st.session_state.last_translations = pd.DataFrame()
                st.session_state.last_input = data.get("handle") or x_link
                st.session_state.last_mode = mode
                status.update(label="Target investigation complete", state="complete")
    if not st.session_state.last_results.empty and st.session_state.last_mode == mode:
        render_results(mode, st.session_state.last_input, min_similarity, show_low)

elif mode == "Media / Image Investigation":
    st.header("Media / Image Investigation")
    st.caption("Upload media and add caption/OCR/narrative. The app stores local hashes and searches public thumbnails/references through the narrative.")
    media_file = st.file_uploader("Upload image/video", type=["jpg", "jpeg", "png", "webp", "bmp", "mp4", "mov", "avi", "mkv", "webm"])
    caption = st.text_area("Caption / OCR text / narrative linked to media", height=100)
    if st.button("Run Media Investigation", type="primary"):
        media_hash = {}
        if media_file is not None:
            path = save_upload(media_file)
            media_hash = compute_media_hash(path)
            st.success(f"Media saved: {path}")
            st.json(media_hash)
        if not caption.strip():
            st.warning("Add caption/OCR text/narrative for public search.")
        else:
            data = run_narrative_investigation(caption, platforms, depth, fetch_metadata, deadline_s=timeout_budget if quick_mode else 180)
            df = data["results"]
            if not df.empty:
                df.insert(0, "section", "Media / Image Search")
                for k, v in media_hash.items():
                    df[f"uploaded_{k}"] = v
            st.session_state.last_results = df
            st.session_state.last_images = data["images"]
            st.session_state.last_queries = data["queries"]
            st.session_state.last_translations = data["translations"]
            st.session_state.last_input = caption
            st.session_state.last_mode = mode
    if not st.session_state.last_results.empty and st.session_state.last_mode == mode:
        render_results(mode, st.session_state.last_input, min_similarity, show_low)

else:
    st.header("Import CSV Dataset")
    st.caption("Use platform exports or OSINT collection CSVs for higher accuracy. Recommended columns: platform, handle/account, title/caption/text, snippet, url/post_url, followers, likes, reposts, timestamp, thumbnail_url.")
    csv = st.file_uploader("Upload CSV dataset", type=["csv"])
    narrative = st.text_input("Optional narrative to score against imported rows")
    if csv is not None:
        df = pd.read_csv(csv)
        rename = {}
        for c in df.columns:
            cl = c.lower()
            if cl in ["account", "username", "user", "profile"]: rename[c] = "handle"
            if cl in ["post_url", "link", "source", "source_url"]: rename[c] = "url"
            if cl in ["caption", "text", "post_text", "content"]: rename[c] = "snippet"
        df = df.rename(columns=rename)
        for c in ["section", "platform", "handle", "role", "confidence", "similarity_score", "title", "snippet", "url", "thumbnail_url", "query_label", "query_language", "search_stage", "domain"]:
            if c not in df.columns:
                df[c] = ""
        df["section"] = df["section"].replace("", "Imported CSV")
        df["role"] = df["role"].replace("", "Imported Lead")
        df["confidence"] = df["confidence"].replace("", "Imported")
        if narrative:
            from modules.analyzer import compute_similarity
            rows = df.to_dict("records")
            df = pd.DataFrame(compute_similarity(narrative, rows))
            df["section"] = "Imported CSV Scored"
        st.session_state.last_results = df
        st.session_state.last_images = pd.DataFrame()
        st.session_state.last_queries = pd.DataFrame()
        st.session_state.last_translations = pd.DataFrame()
        st.session_state.last_input = narrative or "Imported CSV"
        st.session_state.last_mode = mode
    if not st.session_state.last_results.empty and st.session_state.last_mode == mode:
        render_results(mode, st.session_state.last_input, min_similarity, show_low=True)

with st.expander("Operational Notes and Limitations"):
    st.markdown(
        """
        - Complete narrative phrase searches are prioritised before broad keyword searches.
        - Urdu, Chinese simplified/traditional, Hindi and Bengali variants are generated where possible.
        - Social platforms and regional source packs are searched only through public/search-indexed data. The app does not bypass login, captcha, rate limits or private content controls.
        - Repost lineage is shown only when public evidence indicates it; otherwise graph edges are candidate similarity/source-cluster links.
        - For production-grade accuracy, combine this with platform exports/API datasets, screenshot OCR, known handles and manual verification.
        """
    )
# ==============================================================================
# --- NEW APPENDED CAPABILITIES: ADVANCED UI EXTENSIONS ---
# ==============================================================================
st.divider()
st.markdown('<div class="pd-hero"><div class="pd-title">🔍 Advanced OSINT Extensions</div><div class="pd-subtitle">PDF Extractions, Crypto Wallet Tracing, Bot Behavior Scoring, and Propagation Chain Mapping.</div></div>', unsafe_allow_html=True)

ext_tabs = st.tabs(["📄 Document & Wallet Extraction", "🤖 Bot Behavior & Risk Report", "🕸️ Propagation Chain Graph"])

# 1. Document & Wallet Extraction UI
with ext_tabs[0]:
    st.subheader("Extract Entities, PII & Wallets from PDF")
    pdf_file = st.file_uploader("Upload PDF Document", type=["pdf"])
    if pdf_file:
        from modules.media_utils import save_upload, extract_text_from_pdf
        from modules.utils import extract_personal_info_and_wallets
        
        path = save_upload(pdf_file)
        with st.spinner("Parsing document and running entity extraction..."):
            extracted_text = extract_text_from_pdf(path)
            pii_data = extract_personal_info_and_wallets(extracted_text)
            
        st.success("Extraction Complete")
        col_pii1, col_pii2 = st.columns(2)
        with col_pii1:
            st.markdown("**Wallets Discovered:**")
            st.json({"Bitcoin (BTC)": pii_data.get("btc_wallets"), "Ethereum (ETH)": pii_data.get("eth_wallets")})
        with col_pii2:
            st.markdown("**Personal Info & Handlers:**")
            st.json({"Emails": pii_data.get("emails"), "Phones": pii_data.get("phones"), "Handlers": pii_data.get("handlers")})
            
        with st.expander("View Raw Extracted Text"):
            st.text_area("PDF Text", extracted_text, height=300)

# 2. Behavior, Bot Analysis & Risk Report UI
with ext_tabs[1]:
    st.subheader("Generate Target Risk & Bot Activity Report")
    if st.button("Run Threat & Bot Assessment", type="primary"):
        if st.session_state.last_results is not None and not st.session_state.last_results.empty:
            from modules.analyzer import calculate_bot_risk_score, generate_risk_report
            
            with st.spinner("Analyzing cross-platform behavior and handle anomalies..."):
                df_risk = calculate_bot_risk_score(st.session_state.last_results)
                report = generate_risk_report(df_risk)
                
            st.markdown(f"### Campaign Risk Level: **{report['overall_risk']}**")
            r1, r2, r3 = st.columns(3)
            r1.metric("High Confidence Nodes", report["high_confidence_nodes"])
            r2.metric("Suspected Amplifiers", report["suspected_amplifiers"])
            r3.metric("Platforms Targeted", report["cross_platform_spread"])
            
            st.markdown("#### Bot & Sockpuppet Analysis List")
            display_cols = ["handle", "platform", "bot_classification", "bot_risk_score", "role"]
            clean_risk_df = df_risk[df_risk["handle"] != "Unknown"][display_cols].sort_values("bot_risk_score", ascending=False)
            st.dataframe(clean_risk_df, width="stretch", height=400)
        else:
            st.warning("Please run a standard investigation from the sidebar first to generate data for the report.")

# 3. Propagation Graph UI
with ext_tabs[2]:
    st.subheader("Cross-Platform Propagation & Identity Mapping")
    st.caption("Visualizes directional flow highlighting source accounts and downstream amplifiers.")
    if st.session_state.last_results is not None and not st.session_state.last_results.empty:
        from modules.graphing import build_propagation_chain_graph
        fig_chain = build_propagation_chain_graph(st.session_state.last_results)
        st.plotly_chart(fig_chain, width="stretch", use_container_width=True)
    else:
        st.info("No data available. Run an investigation to view the propagation chain.")
from __future__ import annotations
import pandas as pd
import networkx as nx
import plotly.graph_objects as go
from .utils import hash_text, SOCIAL_PLATFORMS, REGIONAL_PLATFORMS

PLATFORM_COLORS = {
    "X": "#1DA1F2", "Instagram": "#C13584", "Facebook": "#1877F2", "TikTok": "#111111",
    "LinkedIn": "#0A66C2", "Telegram": "#229ED9", "YouTube": "#FF0000", "Websites": "#6B7280",
    "Pakistan News": "#16A34A", "China News": "#DC2626", "Bangladesh News": "#059669", "Tibet News": "#7C3AED", "Global News": "#334155",
    "Narrative": "#F97316", "Target": "#7C3AED", "Language": "#F59E0B", "Cluster": "#94A3B8",
}


def build_cluster_graph(df: pd.DataFrame, center_label: str = "Narrative", center_type: str = "Narrative") -> tuple[nx.Graph, pd.DataFrame]:
    G = nx.Graph()
    center_label = center_label[:80] or center_type
    G.add_node(center_label, node_type=center_type, platform=center_type, role="Central Input", size=42, confidence="Central", url="", layer=0)
    if df is None or df.empty:
        return G, pd.DataFrame()

    # Language clusters -> platform clusters -> post/account nodes. This makes the graph less star-like.
    for _, r in df.iterrows():
        platform = str(r.get("platform", "Websites") or "Websites")
        confidence = str(r.get("confidence", "Low") or "Low")
        role = str(r.get("role", "Related Node") or "Related Node")
        lang = str(r.get("query_language", "English") or "English")
        stage = str(r.get("search_stage", "Search") or "Search")
        handle = str(r.get("handle", "Unknown") or "Unknown")
        title = str(r.get("title", ""))[:110]
        url = str(r.get("url", ""))
        sim = float(r.get("similarity_score", 0) or 0)
        domain = str(r.get("domain", "") or "")
        media = bool(str(r.get("thumbnail_url", "") or ""))

        lang_node = f"{lang} narrative"
        if not G.has_node(lang_node):
            G.add_node(lang_node, node_type="Language", platform="Language", role="Query language", size=26, confidence="Cluster", url="", layer=1)
            G.add_edge(center_label, lang_node, weight=3.0, edge_type="translation/query")

        platform_node = f"{platform} | {confidence}"
        if not G.has_node(platform_node):
            G.add_node(platform_node, node_type="Platform cluster", platform=platform, role="Platform / source cluster", size=22, confidence=confidence, url="", layer=2)
            G.add_edge(lang_node, platform_node, weight=2.0, edge_type="platform cluster")

        label_base = handle if handle and handle != "Unknown" else (domain or title[:45] or hash_text(url))
        node_label = f"{label_base} [{platform}]"
        if node_label in G:
            node_label = f"{label_base} [{platform}] {hash_text(url)}"
        size = 12 + min(24, sim / 4)
        if confidence == "High": size += 12
        elif confidence == "Medium": size += 6
        if media: size += 4
        G.add_node(
            node_label, node_type="Post/Account/Source", platform=platform, role=role, size=size,
            confidence=confidence, url=url, title=title, similarity=sim, domain=domain, media=media,
            stage=stage, layer=3
        )
        G.add_edge(platform_node, node_label, weight=max(0.6, sim / 25), edge_type=role)
        if confidence == "High":
            G.add_edge(center_label, node_label, weight=max(0.8, sim / 35), edge_type="exact/near-exact")

    # Add similarity / same-domain / same-handle links between relevant nodes to show clusters.
    nodes = [(n, a) for n, a in G.nodes(data=True) if a.get("node_type") == "Post/Account/Source"]
    for i, (n1, a1) in enumerate(nodes):
        for n2, a2 in nodes[i + 1:]:
            same_handle = n1.split("[")[0].strip() and n1.split("[")[0].strip() == n2.split("[")[0].strip()
            same_domain = a1.get("domain") and a1.get("domain") == a2.get("domain")
            both_high = a1.get("confidence") == "High" and a2.get("confidence") in ["High", "Medium"]
            same_platform = a1.get("platform") == a2.get("platform")
            if same_handle or same_domain or (both_high and same_platform):
                G.add_edge(n1, n2, weight=1.1, edge_type="cluster linkage")

    metrics = []
    if G.number_of_nodes() > 1:
        deg = nx.degree_centrality(G)
        bet = nx.betweenness_centrality(G, normalized=True)
        try: pr = nx.pagerank(G, weight="weight")
        except Exception: pr = {n: 0 for n in G.nodes}
        for n, attrs in G.nodes(data=True):
            metrics.append({
                "node": n, "node_type": attrs.get("node_type", ""), "platform": attrs.get("platform", ""),
                "role": attrs.get("role", ""), "confidence": attrs.get("confidence", ""),
                "degree_centrality": round(deg.get(n, 0), 4), "betweenness": round(bet.get(n, 0), 4),
                "pagerank": round(pr.get(n, 0), 5), "url": attrs.get("url", ""),
            })
    return G, pd.DataFrame(metrics).sort_values(["pagerank", "degree_centrality"], ascending=False) if metrics else pd.DataFrame()


def plot_cluster_graph(G: nx.Graph, title: str = "Propagation / Identity Candidate Network"):
    if G.number_of_nodes() == 0:
        return go.Figure()
    try:
        pos = nx.spring_layout(G, seed=27, k=0.95, weight="weight", iterations=180)
    except Exception:
        pos = nx.spring_layout(G, seed=27)

    edge_x, edge_y, edge_widths = [], [], []
    for u, v, attrs in G.edges(data=True):
        x0, y0 = pos[u]; x1, y1 = pos[v]
        edge_x += [x0, x1, None]; edge_y += [y0, y1, None]
        edge_widths.append(float(attrs.get("weight", 1)))
    edge_trace = go.Scatter(x=edge_x, y=edge_y, line=dict(width=1.25, color="rgba(100,116,139,0.36)"), hoverinfo="none", mode="lines")

    traces = [edge_trace]
    # Separate traces by node_type to allow a clean legend.
    by_type = {}
    for n, attrs in G.nodes(data=True):
        by_type.setdefault(attrs.get("node_type", "Node"), []).append((n, attrs))
    for node_type, items in by_type.items():
        node_x, node_y, texts, hover, sizes, colors, symbols = [], [], [], [], [], [], []
        for n, attrs in items:
            x, y = pos[n]
            node_x.append(x); node_y.append(y)
            platform = attrs.get("platform", "Websites")
            colors.append(PLATFORM_COLORS.get(platform, "#64748B"))
            sizes.append(float(attrs.get("size", 12)))
            symbols.append("diamond" if attrs.get("node_type") in ["Narrative", "Target"] else ("square" if "cluster" in attrs.get("node_type", "").lower() else "circle"))
            texts.append(str(n)[:34])
            hover.append(f"<b>{n}</b><br>Type: {node_type}<br>Platform: {platform}<br>Role: {attrs.get('role','')}<br>Confidence: {attrs.get('confidence','')}<br>Similarity: {attrs.get('similarity','')}<br>Media: {attrs.get('media','')}<br>{attrs.get('url','')}")
        traces.append(go.Scatter(
            x=node_x, y=node_y, mode="markers+text", name=node_type, text=texts, textposition="top center",
            hovertext=hover, hoverinfo="text",
            marker=dict(size=sizes, color=colors, symbol=symbols, line=dict(width=1.2, color="white"), opacity=0.93),
        ))
    fig = go.Figure(data=traces)
    fig.update_layout(
        title=dict(text=title, x=0.02, font=dict(size=18)), showlegend=True, height=760,
        legend=dict(orientation="h", yanchor="bottom", y=1.02, xanchor="right", x=1),
        margin=dict(l=10, r=10, t=70, b=10), plot_bgcolor="white",
        xaxis=dict(showgrid=False, zeroline=False, showticklabels=False),
        yaxis=dict(showgrid=False, zeroline=False, showticklabels=False),
    )
    return fig


def platform_bar(df: pd.DataFrame):
    if df is None or df.empty or "platform" not in df:
        return go.Figure()
    counts = df.groupby(["platform", "confidence"]).size().reset_index(name="count")
    order = counts.groupby("platform")["count"].sum().sort_values(ascending=False).index.tolist()
    fig = go.Figure()
    for conf in ["High", "Medium", "Low"]:
        sub = counts[counts["confidence"] == conf]
        if not sub.empty:
            fig.add_bar(x=sub["platform"], y=sub["count"], name=conf)
    fig.update_layout(height=340, barmode="stack", title="Matches by platform and confidence", margin=dict(l=10, r=10, t=45, b=10), plot_bgcolor="white", xaxis={"categoryorder":"array","categoryarray":order})
    return fig
# ==============================================================================
# --- NEW APPENDED CAPABILITIES: PROPAGATION & TIMELINE GRAPHS ---
# ==============================================================================
def build_propagation_chain_graph(df: pd.DataFrame, title: str = "Propagation Chain & Identity Graph"):
    """Builds a directional chain graph emphasizing amplifiers and cross-platform spread."""
    if df is None or df.empty or "handle" not in df:
        return go.Figure()
        
    G = nx.DiGraph()
    G.add_node("Source Narrative", size=40, color="#ef4444", role="Origin")
    
    for i, r in df.iterrows():
        handle = str(r.get("handle", "Unknown"))
        platform = str(r.get("platform", "Unknown"))
        conf = str(r.get("confidence", "Low"))
        role = str(r.get("role", ""))
        
        if handle == "Unknown":
            continue
            
        node_id = f"{handle} ({platform})"
        size = 25 if conf == "High" else 15
        color = PLATFORM_COLORS.get(platform, "#64748B")
        
        G.add_node(node_id, size=size, color=color, role=role, platform=platform)
        
        # Link high confidence back to narrative (Source)
        if conf == "High" or "Exact" in role:
            G.add_edge("Source Narrative", node_id)
        # Link amplifiers to exact matches (Propagation)
        elif "Amplifier" in role:
            G.add_edge("Source Narrative", node_id) # Simplified linkage

    try:
        pos = nx.spring_layout(G, seed=42)
    except Exception:
        return go.Figure()

    edge_x, edge_y = [], []
    for u, v in G.edges():
        x0, y0 = pos[u]; x1, y1 = pos[v]
        edge_x += [x0, x1, None]; edge_y += [y0, y1, None]

    edge_trace = go.Scatter(x=edge_x, y=edge_y, line=dict(width=1, color="#94a3b8"), mode="lines", hoverinfo="none")

    node_x, node_y, texts, colors, sizes = [], [], [], [], []
    for n, attr in G.nodes(data=True):
        x, y = pos[n]
        node_x.append(x); node_y.append(y)
        texts.append(n)
        colors.append(attr.get("color", "#000"))
        sizes.append(attr.get("size", 10))

    node_trace = go.Scatter(
        x=node_x, y=node_y, mode="markers+text", text=texts, textposition="bottom center",
        marker=dict(size=sizes, color=colors, line=dict(width=2, color="white"))
    )

    fig = go.Figure(data=[edge_trace, node_trace], layout=go.Layout(
        title=title, showlegend=False, hovermode="closest",
        margin=dict(b=0, l=0, r=0, t=40), xaxis=dict(showgrid=False, zeroline=False, showticklabels=False),
        yaxis=dict(showgrid=False, zeroline=False, showticklabels=False), plot_bgcolor="white"
    ))
    return fig
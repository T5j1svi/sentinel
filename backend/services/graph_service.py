"""
SENTINEL Intel — Graph Service
Wraps existing graphing module and provides JSON-serializable network data.
"""
from __future__ import annotations
import sys
from pathlib import Path

PROJECT_ROOT = Path(__file__).resolve().parent.parent.parent
if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT))

import pandas as pd
import networkx as nx
from app.modules.graphing import build_cluster_graph, PLATFORM_COLORS


def build_network_data(results: list[dict], center_label: str = "Narrative") -> dict:
    """Build network graph from results and return JSON-serializable node/edge data."""
    df = pd.DataFrame(results) if results else pd.DataFrame()
    if df.empty:
        return {"nodes": [], "edges": [], "communities": 0, "bridge_nodes": 0, "hub_nodes": []}

    G, metrics_df = build_cluster_graph(df, center_label=center_label[:80], center_type="Narrative")

    nodes = []
    for n, attrs in G.nodes(data=True):
        nodes.append({
            "id": n,
            "label": str(n)[:60],
            "node_type": attrs.get("node_type", "Node"),
            "platform": attrs.get("platform", ""),
            "role": attrs.get("role", ""),
            "confidence": attrs.get("confidence", ""),
            "size": float(attrs.get("size", 12)),
            "color": PLATFORM_COLORS.get(attrs.get("platform", ""), "#64748B"),
            "url": attrs.get("url", ""),
            "similarity": float(attrs.get("similarity", 0)),
            "community": 0,
        })

    edges = []
    for u, v, attrs in G.edges(data=True):
        edges.append({
            "source": u,
            "target": v,
            "weight": float(attrs.get("weight", 1)),
            "edge_type": attrs.get("edge_type", ""),
        })

    try:
        try:
            import community as community_louvain
            partition = community_louvain.best_partition(G.to_undirected(), resolution=1.2)
            nx.set_node_attributes(G, partition, 'community')
            communities = len(set(partition.values()))
        except ImportError:
            components = list(nx.connected_components(G.to_undirected()))
            communities = len(components)

        bet = nx.betweenness_centrality(G, normalized=True)
        bridge_nodes = len([n for n, b in bet.items() if b > 0.05])
        hub_nodes = sorted(bet, key=bet.get, reverse=True)[:5]
        
        # Export interactive HTML using PyVis
        from pyvis.network import Network
        net = Network(height='600px', width='100%', bgcolor='#0f172a', font_color='#ffffff', directed=True)
        
        # Transfer nodes with sizes and colors
        for node, attrs in G.nodes(data=True):
            size = float(attrs.get("size", 12)) + (bet.get(node, 0) * 100) # Scale by betweenness
            title = f"{str(node)[:60]}\nType: {attrs.get('node_type', '')}\nScore: {attrs.get('similarity', 0)}"
            net.add_node(
                str(node),
                label=str(node)[:20] + "..." if len(str(node)) > 20 else str(node),
                title=title,
                size=size,
                color=PLATFORM_COLORS.get(attrs.get("platform", ""), "#64748B")
            )
            
        for u, v, attrs in G.edges(data=True):
            net.add_edge(str(u), str(v), title=attrs.get("edge_type", ""), value=float(attrs.get("weight", 1)))
            
        net.set_options("""
        var options = {
          "physics": {
            "forceAtlas2Based": {
              "gravitationalConstant": -150,
              "centralGravity": 0.015,
              "springLength": 100,
              "springConstant": 0.08
            },
            "minVelocity": 0.75,
            "solver": "forceAtlas2Based",
            "stabilization": {
              "enabled": true,
              "iterations": 1000
            }
          }
        }
        """)
        import os
        os.makedirs("exports", exist_ok=True)
        net.save_graph("exports/network.html")
    except Exception as e:
        print(f"[Graph] Error generating pyvis: {e}")

    return {
        "nodes": nodes,
        "edges": edges,
        "communities": communities,
        "bridge_nodes": bridge_nodes,
        "hub_nodes": hub_nodes,
    }

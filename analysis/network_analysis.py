"""
Network analysis and visualization of YouTube recommendation graphs.

Computes graph statistics (connected components, most-appearing channels,
cross-topic videos) and creates interactive network visualizations.
"""

import json
from pathlib import Path
from collections import defaultdict, Counter
import networkx as nx
import matplotlib.pyplot as plt
import matplotlib.patches as mpatches


def build_graph(data_dir="data"):
    """Build a directed graph from all crawl JSON files."""
    G = nx.DiGraph()
    video_topics = defaultdict(set)
    node_meta = {}
    channel_map = {}

    for data_file in sorted(Path(data_dir).glob("*.json")):
        nodes = json.loads(data_file.read_text())
        for n in nodes:
            vid = n["video_id"]
            video_topics[vid].add(n["topic"])
            node_meta[vid] = {
                "title": n["title"],
                "channel": n["channel_title"],
                "topic": n["topic"],
                "depth": n["depth"],
            }
            channel_map[vid] = n["channel_title"]
            G.add_node(vid)
            if n.get("parent_video_id"):
                G.add_edge(n["parent_video_id"], vid)

    return G, video_topics, node_meta, channel_map


def print_stats(G, video_topics, channel_map):
    """Print basic graph statistics and channel convergence patterns."""
    print(f"Nodes : {G.number_of_nodes()}")
    print(f"Edges : {G.number_of_edges()}")

    # Most connected channels (by number of videos appearing in graph)
    channel_counts = Counter(channel_map[v] for v in G.nodes)
    print(f"\nTop 10 most-appearing channels:")
    for channel, count in channel_counts.most_common(10):
        print(f"  {count:3d}x  {channel}")

    # Videos appearing in multiple topic trees
    cross_topic = {vid: topics for vid, topics in video_topics.items() if len(topics) > 1}
    print(f"\nVideos appearing in multiple topic trees: {len(cross_topic)}")
    for vid, topics in sorted(cross_topic.items(), key=lambda x: -len(x[1]))[:15]:
        title = G.nodes[vid].get("title", vid) if vid in G.nodes else vid
        print(f"  {sorted(topics)}  \"{title[:70]}\"")


def plot_network(G, video_topics, node_meta, output_path="visualizations/network_graph.png"):
    """Create a network visualization of the recommendation graph."""
    COLORS = {
        "tech":        "#4C72B0",
        "health":      "#55A868",
        "immigration": "#C44E52",
        "finance":     "#DD8452",
        "climate":     "#8172B3",
    }

    # Node color: primary topic (first assigned)
    node_colors = [COLORS.get(node_meta[v]["topic"], "#aaaaaa") for v in G.nodes]

    # Node size: scaled by how many topic trees it appears in
    cross_count = {v: len(video_topics[v]) for v in G.nodes}
    node_sizes = [40 + cross_count[v] ** 2.5 * 120 for v in G.nodes]

    pos = nx.spring_layout(G, k=0.45, seed=42, iterations=60)

    fig, ax = plt.subplots(figsize=(16, 12))
    fig.patch.set_facecolor("#f9f9f9")
    ax.set_facecolor("#f9f9f9")

    nx.draw_networkx_edges(G, pos, ax=ax, alpha=0.15, edge_color="#555555",
                           arrows=True, arrowsize=6, width=0.6)

    nx.draw_networkx_nodes(G, pos, ax=ax, node_color=node_colors,
                           node_size=node_sizes, alpha=0.85)

    # Label only cross-topic nodes (appear in 2+ trees)
    labels = {v: node_meta[v]["title"][:30] for v in G.nodes if cross_count[v] > 1}
    nx.draw_networkx_labels(G, pos, labels, ax=ax, font_size=5.5,
                            font_color="#111111", font_weight="bold")

    legend_patches = [mpatches.Patch(color=c, label=t.capitalize())
                      for t, c in COLORS.items()]
    legend_patches.append(mpatches.Patch(color="#aaaaaa", label="Cross-topic"))
    ax.legend(handles=legend_patches, frameon=False, loc="lower left", fontsize=10)

    ax.set_title("YouTube Recommendation Graph — Colored by Topic, Sized by Cross-Topic Appearances",
                 fontsize=13, fontweight="bold", pad=14)
    ax.axis("off")

    plt.tight_layout()
    plt.savefig(output_path, dpi=150, bbox_inches="tight")
    print(f"Saved to {output_path}")


if __name__ == "__main__":
    G, video_topics, node_meta, channel_map = build_graph()
    print_stats(G, video_topics, channel_map)
    plot_network(G, video_topics, node_meta)

"""
Semantic drift analysis across YouTube recommendation depths.

Measures how much video titles diverge semantically from the seed video
as you traverse deeper into the recommendation tree. Uses sentence embeddings
(all-MiniLM-L6-v2) and cosine similarity.
"""

import json
from pathlib import Path
from collections import defaultdict
from sentence_transformers import SentenceTransformer
from sklearn.metrics.pairwise import cosine_similarity
import matplotlib.pyplot as plt

model = SentenceTransformer("all-MiniLM-L6-v2")


def analyze_topic(nodes):
    """Analyze semantic drift for a single topic crawl."""
    seed = next((n for n in nodes if n["depth"] == 0), None)
    if not seed:
        return None

    by_depth = defaultdict(list)
    for n in nodes:
        by_depth[n["depth"]].append(n["title"])

    all_titles = [t for titles in by_depth.values() for t in titles]
    seed_vec = model.encode([seed["title"]])
    all_vecs = model.encode(all_titles)

    # Map each title back to its score
    title_to_score = {}
    for title, vec in zip(all_titles, all_vecs):
        title_to_score[title] = cosine_similarity(seed_vec, [vec])[0][0]

    # Compute stats by depth
    depth_stats = {}
    for depth in sorted(by_depth):
        scores = [title_to_score[t] for t in by_depth[depth]]
        depth_stats[depth] = {
            "avg": sum(scores) / len(scores),
            "min": min(scores),
            "max": max(scores),
            "count": len(scores),
        }

    return {
        "seed": seed,
        "title_to_score": title_to_score,
        "by_depth": by_depth,
        "depth_stats": depth_stats,
    }


def print_topic_stats(analysis):
    """Print detailed similarity stats for a topic."""
    seed = analysis["seed"]
    print(f"\nTopic: {seed['topic']}  |  Seed: \"{seed['title']}\"")
    print(f"{'Depth':<8} {'Videos':<8} {'Avg Similarity':<16} {'Min':<8} {'Max'}")
    print("-" * 52)
    for depth in sorted(analysis["depth_stats"]):
        stats = analysis["depth_stats"][depth]
        print(f"{depth:<8} {stats['count']:<8} {stats['avg']:<16.3f} {stats['min']:<8.3f} {stats['max']:.3f}")


def print_depth3_rankings(analysis):
    """Print videos at depth 3 ranked by similarity to seed."""
    depth3 = analysis["by_depth"].get(3, [])
    if not depth3:
        return

    title_to_score = analysis["title_to_score"]
    scores = [(title_to_score[t], t) for t in depth3]
    ranked = sorted(scores, reverse=True)

    print("\nDepth 3 videos ranked by similarity to seed:")
    for score, title in ranked:
        print(f"  {score:.3f}  {title}")


def run_analysis(data_dir="data"):
    """Run semantic drift analysis on all crawl files."""
    topic_drift = {}
    all_analyses = {}

    for data_file in sorted(Path(data_dir).glob("*.json")):
        nodes = json.loads(data_file.read_text())
        analysis = analyze_topic(nodes)
        if analysis:
            topic = analysis["seed"]["topic"]
            all_analyses[topic] = analysis
            topic_drift[topic] = {
                d: stats["avg"] for d, stats in analysis["depth_stats"].items()
            }
            print_topic_stats(analysis)
            print_depth3_rankings(analysis)

    return topic_drift, all_analyses


def plot_drift(topic_drift, output_path="visualizations/semantic_drift.png"):
    """Plot semantic drift across depths for all topics."""
    fig, ax = plt.subplots(figsize=(8, 5))

    colors = {
        "tech": "#4C72B0",
        "health": "#55A868",
        "immigration": "#C44E52",
        "finance": "#DD8452",
        "climate": "#8172B3",
    }

    for topic, depth_scores in sorted(topic_drift.items()):
        if not depth_scores:
            continue
        depths = sorted(depth_scores.keys())
        scores = [depth_scores[d] for d in depths]
        ax.plot(depths, scores, marker="o", label=topic.capitalize(),
                color=colors.get(topic), linewidth=2, markersize=6)

    ax.axhline(0.5, color="gray", linestyle="--", linewidth=1, alpha=0.7, label="0.5 reference")

    ax.set_xlabel("Recommendation Depth", fontsize=12)
    ax.set_ylabel("Avg Cosine Similarity to Seed", fontsize=12)
    ax.set_title("Semantic Drift Across YouTube Recommendation Depths", fontsize=13, fontweight="bold")
    ax.set_xticks(sorted(set(d for scores in topic_drift.values() for d in scores)))
    ax.set_ylim(0, 1)
    ax.yaxis.grid(True, linestyle=":", alpha=0.5)
    ax.set_axisbelow(True)
    ax.spines["top"].set_visible(False)
    ax.spines["right"].set_visible(False)
    ax.legend(frameon=False, fontsize=10)

    plt.tight_layout()
    plt.savefig(output_path, dpi=150)
    print(f"\nSaved to {output_path}")


if __name__ == "__main__":
    topic_drift, all_analyses = run_analysis()
    plot_drift(topic_drift)

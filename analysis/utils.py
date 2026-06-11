"""
Utility functions for enriching and analyzing video nodes.

Includes sentiment scoring (VADER), channel credibility signals,
and drift metrics computation.
"""

from vaderSentiment.vaderSentiment import SentimentIntensityAnalyzer
import pandas as pd

_analyzer = SentimentIntensityAnalyzer()


# Sentiment scoring

def score_video(video: dict) -> dict:
    """
    Add sentiment scores to a video node dict.

    Adds:
      - title_sentiment: compound score for title (-1 to 1)
      - desc_sentiment: compound score for description
      - combined_sentiment: 0.7 * title + 0.3 * desc
      - sentiment_magnitude: abs(combined_sentiment), measures extremity
    """
    title_score = _analyzer.polarity_scores(video.get("title", ""))["compound"]
    desc_score = _analyzer.polarity_scores(video.get("description", ""))["compound"]
    combined = round(0.7 * title_score + 0.3 * desc_score, 4)

    return {
        **video,
        "title_sentiment": title_score,
        "desc_sentiment": desc_score,
        "combined_sentiment": combined,
        "sentiment_magnitude": abs(combined),
    }


def score_all(nodes: list[dict]) -> list[dict]:
    """Score all nodes with VADER sentiment."""
    return [score_video(n) for n in nodes]


# Channel credibility signals

def view_to_subscriber_ratio(video: dict) -> float:
    """
    High ratio can indicate viral/sensational content from a small channel.
    Returns 0 if subscriber count is unknown.
    """
    subs = video.get("subscriber_count", 0)
    views = video.get("view_count", 0)
    if subs == 0:
        return 0.0
    return round(views / subs, 4)


def engagement_rate(video: dict) -> float:
    """
    (likes + comments) / views — proxy for how activating the content is.
    """
    views = video.get("view_count", 0)
    if views == 0:
        return 0.0
    likes = video.get("like_count", 0)
    comments = video.get("comment_count", 0)
    return round((likes + comments) / views, 4)


def enrich_credibility(nodes: list[dict]) -> list[dict]:
    """Enrich nodes with credibility signals."""
    enriched = []
    for node in nodes:
        enriched.append({
            **node,
            "view_to_sub_ratio": view_to_subscriber_ratio(node),
            "engagement_rate": engagement_rate(node),
        })
    return enriched


# Drift metrics

def compute_drift(nodes: list[dict]) -> pd.DataFrame:
    """
    Returns a DataFrame with one row per depth level, showing mean values
    for key metrics across all videos at that depth.
    """
    df = pd.DataFrame(nodes)

    metrics = [
        "combined_sentiment",
        "sentiment_magnitude",
        "view_to_sub_ratio",
        "engagement_rate",
        "subscriber_count",
        "view_count",
    ]

    # Only include columns that exist
    available = [m for m in metrics if m in df.columns]

    drift = df.groupby("depth")[available].mean().round(4)
    drift["unique_channels"] = df.groupby("depth")["channel_id"].nunique()
    drift["video_count"] = df.groupby("depth")["video_id"].count()

    return drift


def channel_convergence(nodes: list[dict]) -> pd.DataFrame:
    """
    Shows which channels appear most frequently across the entire crawl,
    and at what depths — to detect recommendation convergence.
    """
    df = pd.DataFrame(nodes)
    conv = (
        df.groupby(["channel_title", "depth"])
        .size()
        .reset_index(name="appearances")
        .sort_values("appearances", ascending=False)
    )
    return conv

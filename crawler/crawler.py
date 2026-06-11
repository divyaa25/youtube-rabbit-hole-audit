"""
YouTube recommendation tree crawler.

Starts from a seed video and recursively follows "up next" recommendations
up to MAX_DEPTH layers, building a tree of video metadata.

Related videos are scraped from YouTube's ytInitialData (the YouTube Data API
removed relatedToVideoId support in 2023). Video metadata and channel stats
still use the official API.
"""

import json
import sys
import time
from pathlib import Path

import json as _json
import re
import requests
from googleapiclient.discovery import build

sys.path.insert(0, str(Path(__file__).parent.parent))

from config import YOUTUBE_API_KEY, MAX_DEPTH, MAX_RECOMMENDATIONS

HEADERS = {
    "User-Agent": (
        "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) "
        "AppleWebKit/537.36 (KHTML, like Gecko) "
        "Chrome/124.0.0.0 Safari/537.36"
    ),
    "Accept-Language": "en-US,en;q=0.9",
}


def get_youtube_client():
    return build("youtube", "v3", developerKey=YOUTUBE_API_KEY)


def get_related_video_ids(video_id, max_results=MAX_RECOMMENDATIONS):
    """
    Scrape related video IDs from YouTube's ytInitialData.
    This is the JSON blob YouTube embeds in every watch page that
    powers the sidebar recommendations.
    """
    url = f"https://www.youtube.com/watch?v={video_id}"
    resp = requests.get(url, headers=HEADERS, timeout=10)
    resp.raise_for_status()

    match = re.search(r"var ytInitialData = ({.*?});</script>", resp.text, re.DOTALL)
    if not match:
        return []

    data = _json.loads(match.group(1))

    try:
        section_contents = (
            data["contents"]["twoColumnWatchNextResults"]
            ["secondaryResults"]["secondaryResults"]["results"][0]
            ["itemSectionRenderer"]["contents"]
        )
    except (KeyError, TypeError, IndexError):
        return []

    ids = []
    for item in section_contents:
        lvm = item.get("lockupViewModel", {})
        # Video ID is embedded in the thumbnail image URL: /vi/{VIDEO_ID}/
        try:
            thumb_url = lvm["contentImage"]["thumbnailViewModel"]["image"]["sources"][0]["url"]
            vid_match = re.search(r"/vi/([a-zA-Z0-9_-]{11})/", thumb_url)
            if vid_match:
                ids.append(vid_match.group(1))
        except (KeyError, TypeError):
            continue
        if len(ids) >= max_results:
            break

    return ids


def get_video_metadata(youtube, video_id):
    """Fetch title, description, channel info, and stats for a video."""
    response = youtube.videos().list(
        part="snippet,statistics",
        id=video_id
    ).execute()

    items = response.get("items", [])
    if not items:
        return None

    item = items[0]
    snippet = item["snippet"]
    stats = item.get("statistics", {})

    return {
        "video_id": video_id,
        "title": snippet.get("title", ""),
        "description": snippet.get("description", "")[:500],
        "channel_id": snippet.get("channelId", ""),
        "channel_title": snippet.get("channelTitle", ""),
        "published_at": snippet.get("publishedAt", ""),
        "category_id": snippet.get("categoryId", ""),
        "tags": snippet.get("tags", []),
        "view_count": int(stats.get("viewCount", 0)),
        "like_count": int(stats.get("likeCount", 0)),
        "comment_count": int(stats.get("commentCount", 0)),
    }


def get_channel_stats(youtube, channel_id):
    """Fetch subscriber count for a channel."""
    response = youtube.channels().list(
        part="statistics",
        id=channel_id
    ).execute()

    items = response.get("items", [])
    if not items:
        return {}

    stats = items[0].get("statistics", {})
    return {
        "subscriber_count": int(stats.get("subscriberCount", 0)),
        "video_count": int(stats.get("videoCount", 0)),
    }


def crawl(seed_video_id, topic, depth=MAX_DEPTH):
    """
    Recursively crawl recommendation tree from a seed video.

    Returns a list of node dicts, each with:
      - video metadata
      - channel stats
      - depth (0 = seed)
      - parent_video_id
      - topic
    """
    youtube = get_youtube_client()
    nodes = []
    visited = set()

    def _crawl(video_id, parent_id, current_depth):
        if video_id in visited or current_depth > depth:
            return
        visited.add(video_id)

        metadata = get_video_metadata(youtube, video_id)
        if not metadata:
            return

        channel_stats = get_channel_stats(youtube, metadata["channel_id"])

        node = {
            **metadata,
            **channel_stats,
            "depth": current_depth,
            "parent_video_id": parent_id,
            "topic": topic,
        }
        nodes.append(node)
        print(f"  [depth {current_depth}] {metadata['title'][:60]}")

        if current_depth < depth:
            related_ids = get_related_video_ids(video_id)
            time.sleep(0.5)
            for related_id in related_ids:
                _crawl(related_id, video_id, current_depth + 1)

    print(f"Crawling from seed: {seed_video_id} (topic: {topic})")
    _crawl(seed_video_id, None, 0)
    return nodes


def save_crawl(nodes, topic, seed_video_id):
    out_path = Path(__file__).parent.parent / "data" / f"{topic}_{seed_video_id}.json"
    out_path.parent.mkdir(exist_ok=True)
    with open(out_path, "w") as f:
        json.dump(nodes, f, indent=2)
    print(f"Saved {len(nodes)} nodes to {out_path}")


if __name__ == "__main__":
    from config import SEED_VIDEOS
    print(f"Topics to crawl: {list(SEED_VIDEOS.keys())}")

    for topic, seeds in SEED_VIDEOS.items():
        for seed_id in seeds:
            nodes = crawl(seed_id, topic)
            save_crawl(nodes, topic, seed_id)

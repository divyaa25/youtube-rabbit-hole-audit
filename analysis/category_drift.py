import json
from collections import Counter
from pathlib import Path

# YouTube category ID → name mapping
CATEGORY_NAMES = {
    "1": "Film & Animation",
    "2": "Autos & Vehicles",
    "10": "Music",
    "15": "Pets & Animals",
    "17": "Sports",
    "19": "Travel & Events",
    "20": "Gaming",
    "22": "People & Blogs",
    "23": "Comedy",
    "24": "Entertainment",
    "25": "News & Politics",
    "26": "Howto & Style",
    "27": "Education",
    "28": "Science & Technology",
    "29": "Nonprofits & Activism",
}

data_file = Path("data/tech_rng_yUSwrgU.json")
nodes = json.loads(data_file.read_text())

by_depth = {}
for node in nodes:
    d = node["depth"]
    cat = node.get("category_id", "unknown")
    by_depth.setdefault(d, []).append(cat)

for depth in sorted(by_depth):
    counts = Counter(by_depth[depth])
    total = sum(counts.values())
    print(f"\nDepth {depth} ({total} videos):")
    for cat_id, count in counts.most_common():
        name = CATEGORY_NAMES.get(cat_id, f"Unknown ({cat_id})")
        print(f"  {count:2d}x  {name}")

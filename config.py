import os
from dotenv import load_dotenv

load_dotenv()

YOUTUBE_API_KEY = os.getenv("YOUTUBE_API_KEY")

# Crawl parameters
MAX_DEPTH = 3          # How many layers deep to follow recommendations
MAX_RECOMMENDATIONS = 5  # How many "up next" videos to collect per video

# Seed videos by topic — replace with actual video IDs
SEED_VIDEOS = {
    "tech": ["rng_yUSwrgU"],
    "immigration": ["oqAnzGNfxCY"],
    "health": ["s2lwUIKsRWg"],
    "finance": ["kTxx_Jpnpn0"],
    "climate": ["YtAL8y2lACs"],
}

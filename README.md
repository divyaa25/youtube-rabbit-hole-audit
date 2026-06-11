# YouTube Recommendation Audit: The Rabbit Hole Effect

This project audits whether YouTube's recommendation algorithm systematically pushes viewers toward more extreme, sensationalized, or ideologically narrow content—the "rabbit hole" effect.

## Project Overview

**Research Question:** As viewers follow YouTube's "Up Next" recommendations deeper into the recommendation tree, does content systematically drift along measurable axes (sentiment extremity, channel diversity, content category)?

**Approach:**
1. **Crawl** recommendation trees starting from mainstream seed videos across multiple topics
2. **Enrich** the collected data with metadata (sentiment, engagement metrics, channel credibility signals)
3. **Analyze** drift patterns across recommendation depth
4. **Visualize** recommendation networks and semantic shifts
5. **Report** findings for policy and academic audiences

**Topics Covered:** Tech, Health, Immigration, Finance, Climate

---

## Directory Structure

```
youtube-rec-audit/
├── README.md                    # Project overview and findings
├── config.py                    # Seed video IDs, API keys, constants
├── requirements.txt             # Python dependencies
│
├── crawler/
│   └── crawler.py               # YouTube API crawler (BFS from seed videos)
│
├── analysis/
│   ├── semantic_drift.py        # Semantic similarity analysis across depths
│   ├── network_analysis.py      # Graph stats and network visualization
│   ├── category_drift.py        # YouTube category distribution by depth
│   └── utils.py                 # Shared utilities (sentiment, credibility, drift metrics)
│
├── data/
│   └── *.json                   # Raw crawl output (git-ignored)
│
├── visualizations/
│   ├── semantic_drift.png       # Semantic drift curve plot
│   └── network_graph.png        # Recommendation network graph
│
└── notebooks/                   # Jupyter notebooks (optional exploratory work)
```

---

## Quick Start

### 1. Install Dependencies
```bash
pip install -r requirements.txt
```

### 2. Set Up API Key
```bash
cp .env.example .env
# Edit .env and add your YouTube Data API v3 key
export $(cat .env | xargs)
```

### 3. Run the Crawler
```bash
python crawler/crawler.py
```
This generates JSON files in `data/` with recommendation trees for each seed video.

### 4. Run Analysis
```bash
# Semantic drift analysis
python analysis/semantic_drift.py

# Network graph statistics and visualization
python analysis/network_analysis.py

# YouTube category drift by depth
python analysis/category_drift.py
```

Outputs are saved to `visualizations/`.

---

## Key Findings (Placeholder)

_Update this section as analysis completes._

- **Semantic Drift:** How much do video titles diverge semantically from the seed as depth increases?
- **Channel Convergence:** Do recommendations funnel viewers toward a small set of dominant channels?
- **Category Drift:** Do YouTube video categories shift toward certain categories at deeper depths?
- **Sentiment Extremity:** Does extremity increase (higher magnitude sentiment scores) at deeper recommendation depths?

---

## Analysis Modules

### `semantic_drift.py`
Measures semantic drift using sentence embeddings (all-MiniLM-L6-v2). For each topic crawl:
- Encodes seed video title and all recommendations as dense vectors
- Computes cosine similarity from seed to each recommendation
- Reports average similarity by depth
- Produces a line plot showing how semantic drift evolves

**Output:** `visualizations/semantic_drift.png`

### `network_analysis.py`
Builds a directed graph of all recommendations and produces statistics and visualizations:
- **Graph stats:** Node/edge count, degree distribution
- **Channel convergence:** Which channels appear most frequently? Do certain channels dominate deeper layers?
- **Cross-topic videos:** Which videos appear in multiple topic trees (unusual/viral/sensational content)?
- **Network visualization:** Force-directed layout, colored by topic, sized by cross-topic appearances

**Output:** `visualizations/network_graph.png`

### `category_drift.py`
Analyzes how YouTube's video categories shift across recommendation depths. For each seed video, reports the distribution of categories at each depth level.

### `utils.py`
Shared utility functions:
- **Sentiment scoring** (VADER): `score_video()`, `score_all()`
- **Credibility signals:** `view_to_subscriber_ratio()`, `engagement_rate()`, `enrich_credibility()`
- **Drift metrics:** `compute_drift()`, `channel_convergence()`

---

## Data Format

Each JSON file contains a list of video nodes:

```json
{
  "video_id": "dQw4w9WgXcQ",
  "title": "Rick Astley - Never Gonna Give You Up",
  "description": "...",
  "channel_id": "UCuAXFkgsw1L7xaCfnd5J_vQ",
  "channel_title": "Rick Astley",
  "published_at": "2009-10-25T06:57:33Z",
  "category_id": "10",
  "view_count": 1200000000,
  "like_count": 9000000,
  "comment_count": 500000,
  "subscriber_count": 5000000,
  "depth": 0,
  "parent_video_id": null,
  "topic": "tech"
}
```

---

## Dependencies

- **Crawler:** `googleapiclient`, `requests`, `beautifulsoup4`
- **Analysis:** `networkx`, `matplotlib`, `sentence-transformers`, `scikit-learn`, `pandas`, `vaderSentiment`

See `requirements.txt` for versions.

---

## Caveats & Limitations

- The crawler follows **top 5-10 recommendations per video** up to 3-4 depths. Deeper crawls are exponentially expensive.
- **Sentiment analysis** via VADER is simplistic; fine-tuned transformer models may be more accurate.
- **Credibility signals** (view-to-subscriber ratio, engagement rate) are heuristic proxies, not ground truth.
- The analysis is **descriptive**, not causal. Observed drift does not prove YouTube's algorithm *causes* radicalization.

---

## Policy & Academic Context

This work is relevant to:
- **EU Digital Services Act:** Algorithmic accountability and transparency
- **US Congressional Hearings:** Algorithmic amplification and extremism
- **Media Studies & Computational Social Science:** Recommendation algorithm effects

The final deliverable combines technical rigor with policy accessibility.

---

## Contact & Attribution

Project by Divya Chougule. For questions or feedback, check the GitHub issues.

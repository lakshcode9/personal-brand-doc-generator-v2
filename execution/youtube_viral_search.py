"""
YouTube Viral Content Finder
Searches YouTube for videos matching persona keywords,
calculates virality ratio (views / subscribers), and filters winners (>=3x).
"""

import json
import os
import sys
import time
import io
from datetime import datetime, timedelta
from urllib.request import urlopen, Request
from urllib.parse import urlencode, quote_plus
from urllib.error import HTTPError

# Fix Windows console encoding
sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8', errors='replace')
sys.stderr = io.TextIOWrapper(sys.stderr.buffer, encoding='utf-8', errors='replace')

def load_config():
    """Load brand configuration from local JSON."""
    config_file = os.path.join(os.path.dirname(__file__), "..", "brand_config.json")
    if not os.path.exists(config_file):
        print(f"  [ERROR] brand_config.json not found in root directory!")
        sys.exit(1)
    
    with open(config_file, "r", encoding="utf-8") as f:
        return json.load(f)

# Global Config
CONFIG = load_config()
API_KEY = os.environ.get("YOUTUBE_API_KEY", "")
BASE_URL = "https://www.googleapis.com/youtube/v3"


def api_get(endpoint, params):
    """Make a GET request to YouTube Data API."""
    params["key"] = API_KEY
    url = f"{BASE_URL}/{endpoint}?{urlencode(params, quote_via=quote_plus)}"
    req = Request(url, headers={"Accept": "application/json"})
    try:
        with urlopen(req) as resp:
            return json.loads(resp.read().decode())
    except HTTPError as e:
        error_body = e.read().decode() if e.fp else ""
        print(f"  [API ERROR] {e.code}: {error_body[:200]}")
        return None


def search_videos(query, max_results=15, published_after=None):
    """Search YouTube for videos matching a query."""
    params = {
        "part": "snippet",
        "q": query,
        "type": "video",
        "order": "viewCount",
        "maxResults": min(max_results, 50),
        "relevanceLanguage": "en",
    }
    if published_after:
        params["publishedAfter"] = published_after

    data = api_get("search", params)
    if not data:
        return []

    return data.get("items", [])


def get_video_stats(video_ids):
    """Get view counts for a batch of videos."""
    if not video_ids:
        return {}

    # API allows up to 50 IDs per call
    params = {
        "part": "statistics",
        "id": ",".join(video_ids),
    }
    data = api_get("videos", params)
    if not data:
        return {}

    stats = {}
    for item in data.get("items", []):
        vid = item["id"]
        s = item.get("statistics", {})
        stats[vid] = {
            "views": int(s.get("viewCount", 0)),
            "likes": int(s.get("likeCount", 0)),
            "comments": int(s.get("commentCount", 0)),
        }
    return stats


def get_channel_stats(channel_ids):
    """Get subscriber counts for a batch of channels."""
    if not channel_ids:
        return {}

    unique_ids = list(set(channel_ids))
    params = {
        "part": "statistics",
        "id": ",".join(unique_ids),
    }
    data = api_get("channels", params)
    if not data:
        return {}

    stats = {}
    for item in data.get("items", []):
        cid = item["id"]
        s = item.get("statistics", {})
        stats[cid] = {
            "subscribers": int(s.get("subscriberCount", 0)),
            "hiddenSubscribers": s.get("hiddenSubscriberCount", False),
        }
    return stats


def search_and_analyze(keywords, persona_name, months_back=6):
    """Search for viral videos across keywords for a persona."""
    print(f"\n{'='*60}")
    print(f"  SEARCHING FOR: {persona_name}")
    print(f"{'='*60}")

    published_after = (datetime.utcnow() - timedelta(days=months_back * 30)).strftime(
        "%Y-%m-%dT00:00:00Z"
    )

    all_results = []
    seen_video_ids = set()

    for i, keyword in enumerate(keywords):
        print(f"\n  [{i+1}/{len(keywords)}] Searching: '{keyword}'")

        search_results = search_videos(keyword, max_results=10, published_after=published_after)
        if not search_results:
            print(f"    No results found.")
            continue

        # Extract video IDs and channel IDs
        video_ids = []
        channel_map = {}  # video_id -> channel_id
        snippet_map = {}  # video_id -> snippet data

        for item in search_results:
            vid = item["id"]["videoId"]
            if vid not in seen_video_ids:
                seen_video_ids.add(vid)
                video_ids.append(vid)
                channel_map[vid] = item["snippet"]["channelId"]
                snippet_map[vid] = item["snippet"]

        if not video_ids:
            print(f"    All results already seen.")
            continue

        # Get video stats
        video_stats = get_video_stats(video_ids)

        # Get channel stats
        channel_ids = list(set(channel_map[vid] for vid in video_ids))
        channel_stats = get_channel_stats(channel_ids)

        # Calculate virality
        for vid in video_ids:
            v_stats = video_stats.get(vid, {})
            cid = channel_map[vid]
            c_stats = channel_stats.get(cid, {})

            views = v_stats.get("views", 0)
            subs = c_stats.get("subscribers", 0)

            if subs > 0:
                ratio = views / subs
            else:
                ratio = 0

            snippet = snippet_map[vid]

            all_results.append({
                "video_id": vid,
                "title": snippet.get("title", ""),
                "channel": snippet.get("channelTitle", ""),
                "channel_id": cid,
                "published": snippet.get("publishedAt", ""),
                "url": f"https://youtube.com/watch?v={vid}",
                "views": views,
                "likes": v_stats.get("likes", 0),
                "comments": v_stats.get("comments", 0),
                "subscribers": subs,
                "virality_ratio": round(ratio, 2),
                "search_keyword": keyword,
                "persona": persona_name,
            })

        found_count = len(video_ids)
        print(f"    Found {found_count} new videos.")

        # Small delay to avoid quota issues
        time.sleep(0.3)

    # Sort by virality ratio descending
    all_results.sort(key=lambda x: x["virality_ratio"], reverse=True)

    # Filter winners (ratio >= 3)
    winners = [r for r in all_results if r["virality_ratio"] >= 3]

    print(f"\n  Total videos analyzed: {len(all_results)}")
    print(f"  WINNERS (>=3x virality): {len(winners)}")

    return all_results, winners


def main():
    output_dir = os.path.join(os.path.dirname(__file__), "..", ".tmp")
    os.makedirs(output_dir, exist_ok=True)

    all_data = {}
    
    # Check if personas are defined
    personas = CONFIG.get("personas", [])
    if not personas:
        print("  [WARNING] No personas found in brand_config.json!")
        return

    for i, persona_data in enumerate(personas):
        persona_id = persona_data.get("id", f"persona_{i+1}")
        persona_name = persona_data.get("name", "Unknown Persona")
        keywords = persona_data.get("youtube_keywords", [])
        
        if not keywords:
            print(f"  [SKIP] {persona_name}: No YouTube keywords provided.")
            continue
            
        all_p, winners_p = search_and_analyze(keywords, persona_name)
        all_data[persona_id] = {"all": all_p, "winners": winners_p, "name": persona_name}

    # Save results
    output_file = os.path.join(output_dir, "youtube_viral_results.json")
    with open(output_file, "w", encoding="utf-8") as f:
        json.dump(all_data, f, indent=2, ensure_ascii=False)

    print(f"\n{'='*60}")
    print(f"  RESULTS SAVED TO: {output_file}")
    print(f"{'='*60}")

    # Print top winners summary
    for pid, p_res in all_data.items():
        label = p_res.get("name")
        winners = p_res.get("winners", [])
        
        print(f"\n\n{'='*60}")
        print(f"  TOP WINNERS — {label}")
        print(f"{'='*60}")

        if not winners:
            print("    No winners found (virality ratio >= 3x).")
            continue

        for idx, w in enumerate(winners[:15]):
            print(f"\n  #{idx+1}")
            print(f"    Title: {w['title']}")
            print(f"    Channel: {w['channel']} ({w['subscribers']:,} subs)")
            print(f"    Views: {w['views']:,}")
            print(f"    Virality: {w['virality_ratio']}x")
            print(f"    URL: {w['url']}")
            print(f"    Keyword: {w['search_keyword']}")


if __name__ == "__main__":
    main()

"""
Instagram Viral Content Finder via Apify
Uses apify/instagram-hashtag-scraper to find viral reels by hashtag.
Then uses apify/instagram-profile-scraper to get follower counts for owners.
Calculates virality ratio (views / followers) and filters winners (>=3x).
"""

import json
import os
import sys
import io
import time
from urllib.request import urlopen, Request
from urllib.parse import urlencode
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
APIFY_TOKEN = os.environ.get("APIFY_API_TOKEN", "")
APIFY_BASE = "https://api.apify.com/v2"

RESULTS_PER_HASHTAG = 20  # Keep modest to control Apify costs


def apify_request(method, endpoint, body=None):
    """Make a request to the Apify API."""
    url = f"{APIFY_BASE}/{endpoint}?token={APIFY_TOKEN}"
    data = json.dumps(body).encode() if body else None
    headers = {"Content-Type": "application/json"} if body else {}

    req = Request(url, data=data, headers=headers, method=method)
    try:
        with urlopen(req) as resp:
            return json.loads(resp.read().decode())
    except HTTPError as e:
        error_body = e.read().decode() if e.fp else ""
        print(f"  [API ERROR] {e.code}: {error_body[:500]}")
        return None


def run_hashtag_scraper(hashtags, results_per_tag=20):
    """Run Instagram Hashtag Scraper actor and wait for results."""
    actor_id = "apify~instagram-hashtag-scraper"

    input_data = {
        "hashtags": hashtags,
        "resultsLimit": results_per_tag,
        "searchType": "hashtag",
        "resultsType": "reels",  # Must be "reels" to get video content with play counts
    }

    print(f"  Starting actor run for {len(hashtags)} hashtags...")
    result = apify_request("POST", f"acts/{actor_id}/runs", input_data)

    if not result or "data" not in result:
        print("  Failed to start actor run!")
        return []

    run_id = result["data"]["id"]
    print(f"  Run started: {run_id}")

    # Wait for run to finish
    max_wait = 300  # 5 minutes max
    waited = 0
    while waited < max_wait:
        time.sleep(10)
        waited += 10
        status_resp = apify_request("GET", f"actor-runs/{run_id}")
        if not status_resp:
            continue
        status = status_resp.get("data", {}).get("status", "")
        print(f"  Status after {waited}s: {status}")

        if status in ("SUCCEEDED", "FAILED", "ABORTED", "TIMED-OUT"):
            break

    if status != "SUCCEEDED":
        print(f"  Run ended with status: {status}")
        return []

    # Get dataset items
    dataset_id = status_resp.get("data", {}).get("defaultDatasetId", "")
    if not dataset_id:
        print("  No dataset ID found!")
        return []

    items_resp = apify_request("GET", f"datasets/{dataset_id}/items?limit=1000")
    if not items_resp:
        return []

    # items_resp is a list here
    if isinstance(items_resp, list):
        return items_resp
    return items_resp.get("items", items_resp) if isinstance(items_resp, dict) else []


def process_results(raw_items, persona_name):
    """Process scraped Instagram results into standardized format."""
    results = []

    for item in raw_items:
        # Only care about videos/reels
        item_type = item.get("type", "")
        if item_type != "Video":
            continue

        views = item.get("videoPlayCount", 0) or item.get("igPlayCount", 0) or 0
        likes = item.get("likesCount", 0)
        if likes == -1:
            likes = 0
        comments = item.get("commentsCount", 0)
        reshares = item.get("reshareCount", 0) or 0
        username = item.get("ownerUsername", "")
        url = item.get("url", "")
        caption = item.get("caption", "")[:200]  # Truncate
        hashtags = item.get("hashtags", [])
        input_url = item.get("inputUrl", "")

        results.append({
            "url": url,
            "username": username,
            "owner_id": item.get("ownerId", ""),
            "profile_url": f"https://instagram.com/{username}" if username else "",
            "views": views,
            "likes": likes,
            "comments": comments,
            "reshares": reshares,
            "caption_preview": caption,
            "hashtags": hashtags[:10],  # Keep top 10
            "timestamp": item.get("timestamp", ""),
            "duration": item.get("videoDuration", 0),
            "source_hashtag": input_url.split("/tags/")[-1] if "/tags/" in input_url else "",
            "persona": persona_name,
            # Follower count needs separate lookup
            "followers": None,
            "virality_ratio": None,
        })

    return results


def get_follower_counts(usernames):
    """Use the Instagram Profile Scraper to get follower counts for unique usernames."""
    if not usernames:
        return {}

    unique_usernames = list(set(usernames))[:50]  # Limit to save costs

    actor_id = "apify~instagram-profile-scraper"
    input_data = {
        "usernames": unique_usernames,
    }

    print(f"\n  Fetching follower counts for {len(unique_usernames)} unique profiles...")
    result = apify_request("POST", f"acts/{actor_id}/runs", input_data)

    if not result or "data" not in result:
        print("  Failed to start profile scraper!")
        return {}

    run_id = result["data"]["id"]

    # Wait for run
    max_wait = 300
    waited = 0
    status = ""
    while waited < max_wait:
        time.sleep(10)
        waited += 10
        status_resp = apify_request("GET", f"actor-runs/{run_id}")
        if not status_resp:
            continue
        status = status_resp.get("data", {}).get("status", "")
        print(f"  Profile scraper status after {waited}s: {status}")

        if status in ("SUCCEEDED", "FAILED", "ABORTED", "TIMED-OUT"):
            break

    if status != "SUCCEEDED":
        print(f"  Profile scraper ended with status: {status}")
        return {}

    dataset_id = status_resp.get("data", {}).get("defaultDatasetId", "")
    items = apify_request("GET", f"datasets/{dataset_id}/items?limit=500")

    if not items:
        return {}

    if isinstance(items, dict):
        items = items.get("items", [])

    follower_map = {}
    for item in items:
        username = item.get("username", "")
        followers = item.get("followersCount", 0) or item.get("edgeFollowedBy", {}).get("count", 0)
        if username:
            follower_map[username] = followers

    return follower_map


def main():
    output_dir = os.path.join(os.path.dirname(__file__), "..", ".tmp")
    os.makedirs(output_dir, exist_ok=True)

    all_data = {}
    
    # Check personas
    personas = CONFIG.get("personas", [])
    if not personas:
        print("  [WARNING] No personas found in brand_config.json!")
        return

    all_initial_results = []

    for i, persona_data in enumerate(personas):
        persona_id = persona_data.get("id", f"persona_{i+1}")
        persona_name = persona_data.get("name", "Unknown Persona")
        hashtags = persona_data.get("instagram_hashtags", [])
        
        if not hashtags:
            print(f"  [SKIP] {persona_name}: No Instagram hashtags provided.")
            continue

        print("\n" + "=" * 60)
        print(f"  {persona_name}")
        print("=" * 60)

        raw_items = run_hashtag_scraper(hashtags, RESULTS_PER_HASHTAG)
        processed = process_results(raw_items, persona_name)
        print(f"  {persona_name}: {len(processed)} reels found")
        
        all_initial_results.extend(processed)

    if not all_initial_results:
        print("  [ERROR] No items found across any personas.")
        return

    # ---- Get follower counts ----
    all_usernames = [r["username"] for r in all_initial_results if r["username"]]
    follower_map = get_follower_counts(all_usernames)

    # Update results with follower counts and virality ratios
    for r in all_initial_results:
        followers = follower_map.get(r["username"], 0)
        r["followers"] = followers
        if followers > 0:
            r["virality_ratio"] = round(r["views"] / followers, 2)
        else:
            r["virality_ratio"] = 0

    # Group results back by persona_id
    for persona_data in personas:
        p_id = persona_data.get("id")
        p_name = persona_data.get("name")
        p_results = [r for r in all_initial_results if r["persona"] == p_name]
        
        # Sort by virality
        p_results.sort(key=lambda x: x.get("virality_ratio", 0) or 0, reverse=True)
        winners = [r for r in p_results if (r.get("virality_ratio") or 0) >= 3]
        
        all_data[p_id] = {"all": p_results, "winners": winners, "name": p_name}

    # Save results
    output_file = os.path.join(output_dir, "instagram_viral_results.json")
    with open(output_file, "w", encoding="utf-8") as f:
        json.dump(all_data, f, indent=2, ensure_ascii=False)

    print(f"\n{'=' * 60}")
    print(f"  RESULTS SAVED TO: {output_file}")
    print(f"{'=' * 60}")

    # Print top winners
    for pid, p_res in all_data.items():
        label = p_res.get("name")
        winners = p_res.get("winners", [])
        
        print(f"\n\n{'=' * 60}")
        print(f"  TOP WINNERS -- {label}")
        print(f"{'=' * 60}")

        if not winners:
            print("    No winners found (virality ratio >= 3x).")
            continue

        for idx, w in enumerate(winners[:15]):
            print(f"\n  #{idx+1}")
            print(f"    User: @{w['username']} ({w.get('followers', '?'):,} followers)")
            print(f"    Views: {w['views']:,}")
            print(f"    Virality: {w.get('virality_ratio', 0)}x")
            print(f"    Likes: {w['likes']:,} | Comments: {w['comments']}")
            print(f"    URL: {w['url']}")
            print(f"    Hashtag: #{w['source_hashtag']}")


if __name__ == "__main__":
    main()

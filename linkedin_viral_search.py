"""
LinkedIn Viral Content Finder via Apify
Uses harvestapi/linkedin-profile-posts actor to scrape posts from target profiles.
Analyzes engagement to find winning content.
No cookies or LinkedIn account required.
"""

import json
import os
import sys
import io
import time
from urllib.request import urlopen, Request
from urllib.error import HTTPError

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


def apify_request(method, endpoint, body=None):
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


def run_linkedin_scraper(profile_urls, posted_limit=30):
    """Run the LinkedIn Profile Posts Scraper actor."""
    actor_id = "harvestapi~linkedin-profile-posts"

    input_data = {
        "targetUrls": profile_urls,
        "postedLimit": "6months",  # Enum: any, 1h, 24h, week, month, 3months, 6months, year
    }

    print(f"  Starting actor run for {len(profile_urls)} profiles...")
    result = apify_request("POST", f"acts/{actor_id}/runs", input_data)

    if not result or "data" not in result:
        print("  Failed to start actor run!")
        print(f"  Response: {result}")
        return []

    run_id = result["data"]["id"]
    print(f"  Run started: {run_id}")

    # Wait for completion
    max_wait = 600  # 10 minutes
    waited = 0
    status = ""
    while waited < max_wait:
        time.sleep(15)
        waited += 15
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

    items_resp = apify_request("GET", f"datasets/{dataset_id}/items?limit=5000")
    if isinstance(items_resp, list):
        return items_resp
    return items_resp.get("items", items_resp) if isinstance(items_resp, dict) else []


def process_results(raw_items):
    """Process LinkedIn posts into analyzed results."""
    results = []

    for item in raw_items:
        if item.get("type") != "post":
            continue

        engagement = item.get("engagement") or {}
        likes = engagement.get("likes", 0) or 0
        comments = engagement.get("comments", 0) or 0
        shares = engagement.get("shares", 0) or 0
        total_engagement = likes + comments + shares

        author = item.get("author", {})
        author_name = author.get("name", "")
        author_id = author.get("publicIdentifier", "")
        author_info = author.get("info", "")
        profile_url = author.get("linkedinUrl", "")

        content = item.get("content", "")
        post_url = item.get("linkedinUrl", "")
        posted_at = item.get("postedAt", {})
        posted_date = posted_at.get("date", "")

        results.append({
            "post_url": post_url,
            "author_name": author_name,
            "author_id": author_id,
            "author_info": author_info,
            "profile_url": profile_url,
            "content_preview": content[:200] if content else "",
            "likes": likes,
            "comments": comments,
            "shares": shares,
            "total_engagement": total_engagement,
            "posted_date": posted_date,
        })

    # Sort by total engagement
    results.sort(key=lambda x: x["total_engagement"], reverse=True)
    return results


def main():
    output_dir = os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", ".tmp")
    os.makedirs(output_dir, exist_ok=True)

    # Collect all profile URLs from personas
    all_profiles = []
    personas = CONFIG.get("personas", [])
    for p in personas:
        profiles = p.get("linkedin_profiles", [])
        all_profiles.extend(profiles)
    
    # Remove duplicates
    all_profiles = list(set(all_profiles))

    if not all_profiles:
        print("  [WARNING] No LinkedIn profiles found in brand_config.json!")
        return

    print(f"\n{'='*60}")
    print(f"  LINKEDIN PROFILE POSTS SCRAPER (via Apify)")
    print(f"  Unique Profiles: {len(all_profiles)}")
    print(f"{'='*60}")

    raw_items = run_linkedin_scraper(all_profiles, posted_limit=20)
    print(f"\n  Total raw items: {len(raw_items)}")

    # Process and analyze
    results = process_results(raw_items)
    print(f"  Processed posts: {len(results)}")

    # Save results
    output_file = os.path.join(output_dir, "linkedin_viral_results.json")
    with open(output_file, "w", encoding="utf-8") as f:
        json.dump({"all": results, "raw_count": len(raw_items)}, f, indent=2, ensure_ascii=False)

    print(f"\n  Results saved to: {output_file}")

    # Print top posts by engagement
    print(f"\n{'='*60}")
    print(f"  TOP LINKEDIN POSTS BY ENGAGEMENT")
    print(f"{'='*60}")

    for i, post in enumerate(results[:25]):
        print(f"\n  #{i+1}")
        print(f"    Author: {post['author_name']} ({post.get('author_info', '')[:60]})")
        print(f"    Likes: {post['likes']:,} | Comments: {post['comments']} | Shares: {post['shares']}")
        print(f"    Total Engagement: {post['total_engagement']:,}")
        print(f"    Content: {post.get('content_preview', '')[:120]}...")
        print(f"    URL: {post['post_url']}")


if __name__ == "__main__":
    main()

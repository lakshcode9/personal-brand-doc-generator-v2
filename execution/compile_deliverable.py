"""
Compile all viral content data into the final deliverable markdown document.
Reads YouTube, Instagram, and LinkedIn results from .tmp/ and generates
the comprehensive viral content research report.
"""
import json
import io
import sys
import os

sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8', errors='replace')

# Determine paths relative to script location
SCRIPT_DIR = os.path.dirname(os.path.abspath(__file__))
BASE = os.path.dirname(SCRIPT_DIR)
TMP = os.path.join(BASE, ".tmp")
BRAND_CONFIG_PATH = os.path.join(BASE, "brand_config.json")

# Load Brand Strategy
if os.path.exists(BRAND_CONFIG_PATH):
    with open(BRAND_CONFIG_PATH, "r", encoding="utf-8") as f:
        brand_config = json.load(f)
else:
    brand_config = {
        "brand": {"name": "Your Brand", "tagline": "Dynamic Personal Brand"},
        "strategy": {"offers": ["Your Primary Offer"]}
    }

# Load data
def load_json(name):
    path = os.path.join(TMP, name)
    if os.path.exists(path):
        return json.load(open(path, "r", encoding="utf-8"))
    return None

yt = load_json("youtube_viral_results.json")
ig = load_json("instagram_viral_results.json")
li = load_json("linkedin_viral_results.json")

lines = []
def w(text=""):
    lines.append(text)

# =================== HEADER ===================
w(f"# Viral Content Research Report")
w()
w(f"> **Compiled for {brand_config['brand']['name']}**")
w(f"> **Focus:** {brand_config['strategy'].get('focus', 'General')}")
w("> ")
w("> Data collected across YouTube, Instagram, and LinkedIn. Winning content = views >= 3x followers.")
w()

# =================== YOUTUBE ===================
if yt:
    w("---")
    w()
    w("## YouTube Winners")
    w()
    for persona_id, p_res in yt.items():
        persona_name = p_res.get("name", persona_id)
        w(f"### {persona_name}")
        w()
        w("| # | Channel | Title | Views | Subs | Virality | Link |")
        w("|---|---------|-------|-------|------|----------|------|")
        winners = p_res.get("winners", [])[:20]
        for i, v in enumerate(winners):
            title = v["title"][:60].replace("|", "/")
            channel = v["channel"][:25].replace("|", "/")
            link = f"[Watch]({v['url']})"
            w(f"| {i+1} | {channel} | {title} | {v['views']:,} | {v['subscribers']:,} | **{v['virality_ratio']}x** | {link} |")
        w()
        w(f"*Total analyzed: {len(p_res.get('all', []))} | Winners (>=3x): {len(winners)}*")
        w()

# =================== INSTAGRAM ===================
if ig:
    w("---")
    w()
    w("## Instagram Reels")
    w()
    for persona_id, p_res in ig.items():
        persona_name = p_res.get("name", persona_id)
        w(f"### {persona_name}")
        w()
        w("| # | Creator | Followers | Views | Virality | Link |")
        w("|---|---------|-----------|-------|----------|------|")
        winners = p_res.get("winners", [])[:20]
        for i, r in enumerate(winners):
            username = f"@{r['username']}"[:20]
            link = f"[View]({r['url']})"
            w(f"| {i+1} | {username} | {r.get('followers', 0):,} | {r['views']:,} | **{r.get('virality_ratio', 0)}x** | {link} |")
        w()
        w(f"*Total analyzed: {len(p_res.get('all', []))} | Winners (>=3x): {len(winners)}*")
        w()

# =================== LINKEDIN ===================
if li:
    w("---")
    w()
    w("## LinkedIn Top Posts")
    w()
    w("| # | Author | Content Preview | Likes | Comments | Total | Link |")
    w("|---|--------|----------------|-------|----------|-------|------|")
    posts = li.get("all", [])[:30]
    for i, p in enumerate(posts):
        author = p["author_name"][:25].replace("|", "/")
        content = p.get("content_preview", "")[:70].replace("|", "/").replace("\n", " ")
        link = f"[View]({p.get('post_url', '')})"
        w(f"| {i+1} | {author} | {content} | {p['likes']:,} | {p['comments']:,} | **{p['total_engagement']:,}** | {link} |")
    w()

# =================== PATTERNS ===================
w("---")
w()
w("## Winning Micro-Patterns")
w()
w("1. **Hooks**: Attention-grabbing 'What if' and tutorial hooks dominate.")
w("2. **Format**: Short-form vertical loops show high-virality coefficients.")
w("3. **Identity**: Vulnerable, zero-to-one storytelling builds the strongest trust.")

# Write file
output_path = os.path.join(BASE, "viral_content_research.md")
with open(output_path, "w", encoding="utf-8") as f:
    f.write("\n".join(lines))

print(f"Deliverable written to: {output_path}")

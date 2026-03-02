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

from pathlib import Path

def get_paths():
    script_dir = Path(__file__).parent.resolve()
    skill_dir = script_dir.parent
    results_dir = skill_dir / "results"
    return results_dir

RESULTS = get_paths()

# Load data
def load_json(filename):
    path = RESULTS / filename
    if not path.exists():
        print(f"  [ERROR] File not found: {path}")
        return {}
    with open(path, "r", encoding="utf-8") as f:
        return json.load(f)

yt = load_json("youtube_viral_results.json")
ig = load_json("instagram_viral_results.json")
li = load_json("linkedin_viral_results.json")

lines = []
def w(text=""):
    lines.append(text)

# =================== HEADER ===================
w("# Viral Content Research Report")
w()

# Load brand info if available
script_dir = Path(__file__).parent.resolve()
root_config = script_dir.parents[2] / "brand_config.json"
brand_name = "Your Brand"
if root_config.exists():
    with open(root_config, "r", encoding="utf-8") as f:
        config = json.load(f)
        brand_name = config['brand']['name']

w(f"> **Compiled for {brand_name}** | Data-Driven Content Strategy")
w("> ")
w("> Data collected across YouTube, Instagram, and LinkedIn. Winning content = views >= 3x followers.")
w()

# =================== YOUTUBE ===================
w("---")
w()
w("## YouTube Winners")
w()

# Persona 1
w("### Persona 1: Business Professionals (AI for Work)")
w()
w("| # | Channel | Title | Views | Subs | Virality | Link |")
w("|---|---------|-------|-------|------|----------|------|")

yt_p1_winners = yt["persona_1"]["winners"][:20]
for i, v in enumerate(yt_p1_winners):
    title = v["title"][:60].replace("|", "/")
    channel = v["channel"][:25].replace("|", "/")
    link = f"[Watch]({v['url']})"
    w(f"| {i+1} | {channel} | {title} | {v['views']:,} | {v['subscribers']:,} | **{v['virality_ratio']}x** | {link} |")

w()
w(f"*Total videos analyzed: {len(yt['persona_1']['all'])} | Winners (>=3x): {len(yt['persona_1']['winners'])}*")
w()

# Persona 2
w("### Persona 2: AI Agency Builders")
w()
w("| # | Channel | Title | Views | Subs | Virality | Link |")
w("|---|---------|-------|-------|------|----------|------|")

yt_p2_winners = yt["persona_2"]["winners"][:20]
for i, v in enumerate(yt_p2_winners):
    title = v["title"][:60].replace("|", "/")
    channel = v["channel"][:25].replace("|", "/")
    link = f"[Watch]({v['url']})"
    w(f"| {i+1} | {channel} | {title} | {v['views']:,} | {v['subscribers']:,} | **{v['virality_ratio']}x** | {link} |")

w()
w(f"*Total videos analyzed: {len(yt['persona_2']['all'])} | Winners (>=3x): {len(yt['persona_2']['winners'])}*")
w()

# =================== INSTAGRAM ===================
w("---")
w()
w("## Instagram Reel Winners")
w()

# Persona 1
w("### Persona 1: Business Professionals (AI for Work)")
w()
w("| # | Creator | Followers | Views | Virality | Hashtag | Link |")
w("|---|---------|-----------|-------|----------|---------|------|")

ig_p1_winners = ig["persona_1"]["winners"][:20]
for i, r in enumerate(ig_p1_winners):
    username = f"@{r['username']}"[:20]
    link = f"[View]({r['url']})"
    hashtag = f"#{r.get('source_hashtag', '?')}"
    w(f"| {i+1} | {username} | {r.get('followers',0):,} | {r['views']:,} | **{r.get('virality_ratio',0)}x** | {hashtag} | {link} |")

w()
w(f"*Total reels analyzed: {len(ig['persona_1']['all'])} | Winners (>=3x): {len(ig['persona_1']['winners'])}*")
w()

# Persona 2
w("### Persona 2: AI Agency Builders")
w()
w("| # | Creator | Followers | Views | Virality | Hashtag | Link |")
w("|---|---------|-----------|-------|----------|---------|------|")

ig_p2_winners = ig["persona_2"]["winners"][:20]
for i, r in enumerate(ig_p2_winners):
    username = f"@{r['username']}"[:20]
    link = f"[View]({r['url']})"
    hashtag = f"#{r.get('source_hashtag', '?')}"
    w(f"| {i+1} | {username} | {r.get('followers',0):,} | {r['views']:,} | **{r.get('virality_ratio',0)}x** | {hashtag} | {link} |")

w()
w(f"*Total reels analyzed: {len(ig['persona_2']['all'])} | Winners (>=3x): {len(ig['persona_2']['winners'])}*")
w()

# =================== LINKEDIN ===================
w("---")
w()
w("## LinkedIn Top Posts (by Engagement)")
w()
w("> LinkedIn doesn't expose follower counts publicly, so we rank by total engagement (likes + comments + shares).")
w()

w("| # | Author | Content Preview | Likes | Comments | Shares | Total | Link |")
w("|---|--------|----------------|-------|----------|--------|-------|------|")

li_posts = li["all"][:30]
for i, p in enumerate(li_posts):
    author = p["author_name"][:25].replace("|", "/")
    content = p["content_preview"][:70].replace("|", "/").replace("\n", " ").replace("\r", "")
    link = f"[View]({p['post_url']})" if p["post_url"] else ""
    w(f"| {i+1} | {author} | {content} | {p['likes']:,} | {p['comments']} | {p['shares']} | **{p['total_engagement']:,}** | {link} |")

w()
w(f"*Total posts scraped: {li.get('raw_count', len(li['all']))} from 13 creator profiles*")
w()

# =================== CONTENT IDEAS ===================
w("---")
w()
w(f"## Content Ideas for {brand_name}")
w()
w("Based on patterns from winning content across all three platforms.")
w()

w("### YouTube Ideas")
w()
w("| # | Persona | Hook / Idea | Format | Why It Works |")
w("|---|---------|-------------|--------|--------------|")
yt_ideas = [
    ("P1", "\"I Automated My Entire Workday With AI (Here's How)\"", "Long-form (10-15 min)", "Practical, shows real transformation. High-performing 'how I did it' format"),
    ("P1", "\"AI Will Replace Your Job in 2026 -- Unless You Do This\"", "Short (< 60s)", "Fear + solution hook. Top performers in this niche use urgency"),
    ("P1", "\"10 AI Tools That Will Make You 10x Faster at Work\"", "Listicle (8-12 min)", "Tool roundups crush on YouTube. Practical + searchable"),
    ("P1", "\"The Prompt Engineering Trick Nobody Talks About\"", "Short/Medium", "Curiosity gap + practical skill. Prompt eng is trending hard"),
    ("P1", "\"How To Become The AI Person At Your Company\"", "Long-form", "Career positioning angle -- unique to your mentorship offering"),
    ("P2", "\"I Built an AI Agency From Scratch in 30 Days\"", "Documentary-style", "Journey content outperforms. Alex Hormozi x Replit did 206x virality"),
    ("P2", "\"How To Land Your First AI Client (Step-by-Step)\"", "Tutorial (15-20 min)", "Addresses the #1 pain point of agency starters"),
    ("P2", "\"Why 95% of AI Projects Don't Make Money\"", "Short/Medium", "Contrarian take + real insight. Alberta Tech did 7.26x with this"),
    ("P2", "\"The Truth About AI Agencies Nobody Tells You\"", "Talking head", "Raw, honest take from someone who actually builds production systems"),
    ("P2", "\"Stop Building Prompt Wrappers. Build Real AI Systems.\"", "Short", "Your unique angle -- depth over volume, zero BS engineering"),
]
for i, (persona, hook, fmt, why) in enumerate(yt_ideas):
    w(f"| {i+1} | {persona} | {hook} | {fmt} | {why} |")

w()

w("### Instagram Reel Ideas")
w()
w("| # | Persona | Hook / Idea | Why It Works |")
w("|---|---------|-------------|--------------|")
ig_ideas = [
    ("P1", "\"POV: You just learned AI and now you finish work at 2pm\"", "Aspirational + relatable. Short-form storytelling works for this audience"),
    ("P1", "\"3 AI hacks that will save you 2 hours today\"", "Listicle reels with quick demos perform well. Actionable = shares"),
    ("P1", "\"My boss asked me to learn AI. Here's what I did.\"", "Personal story hook. Narrative reels outperform tutorial reels"),
    ("P1", "\"Stop using ChatGPT like this (do THIS instead)\"", "Correction hooks drive massive engagement. Quick, visual, shareable"),
    ("P2", "\"How I closed my first AI client in 7 days\"", "Social proof + achievable timeline. Agency builders eat this up"),
    ("P2", "\"Building an AI agent in 60 seconds (watch this)\"", "Speed demo format. @forgemind_ai crushed with 27x+ virality on n8n content"),
    ("P2", "\"The AI agency model that actually works\"", "Contrarian/truth-telling. Addresses 'which model' confusion"),
    ("P2", "\"Drop out. Build. Survive. (My AI story)\"", "Your authentic narrative. Vulnerability + hustle resonates deeply"),
]
for i, (persona, hook, why) in enumerate(ig_ideas):
    w(f"| {i+1} | {persona} | {hook} | {why} |")

w()

w("### LinkedIn Ideas")
w()
w("| # | Persona | Hook / Idea | Why It Works |")
w("|---|---------|-------------|--------------|")
li_ideas = [
    ("P1", "\"I dropped out of engineering. Now I teach AI to professionals.\"", "Origin story + vulnerability. Justin Welsh format: personal narrative + lesson"),
    ("P1", "\"AI is moving faster than your company's 'AI transformation' plan.\"", "Calls out corporate BS. Relatable to every working professional"),
    ("P1", "\"You don't need a CS degree to understand AI. Here's proof.\"", "Anti-gatekeeping angle. Pascal Bornet-style practical AI posts crush"),
    ("P1", "\"The #1 AI skill that will save your career (it's not prompting)\"", "Contrarian + curiosity gap. Forces engagement through comments"),
    ("P2", "\"I've built AI systems for $850K+ revenue. Here's what most AI agencies get wrong.\"", "Credibility + contrarian take. Your unique proof point"),
    ("P2", "\"Production-grade AI > Prompt wrappers. Always.\"", "Hot take format. Polarizing = engagement. Your core brand message"),
    ("P2", "\"3 things I wish I knew before starting my AI agency\"", "Lessons-learned format consistently gets high engagement (Zain Kahn does 3000+ likes)"),
    ("P2", "\"The difference between an AI freelancer and an AI architect\"", "Identity-shifting content. Positions your depth as the differentiator"),
]
for i, (persona, hook, why) in enumerate(li_ideas):
    w(f"| {i+1} | {persona} | {hook} | {why} |")

w()
w("---")
w()
w("## Key Patterns Observed")
w()
w("### What Makes Content Go Viral Across Platforms")
w()
w("1. **Fear + Solution hooks** -- \"AI will replace you... unless you do X\" performs massively on YouTube")
w("2. **Speed demos** -- 60-second AI builds get insane virality on Instagram (@forgemind_ai, @karam.mahaan)")
w("3. **Personal story format** -- Justin Welsh dominates LinkedIn with personal narrative + universal lesson")
w("4. **Contrarian takes** -- \"Why 95% of AI projects fail\" or \"Stop doing X, do Y instead\" drives comments")
w("5. **Tool roundups** -- Still work on YouTube. \"Best 10 AI tools\" is a reliable format")
w("6. **Origin stories** -- Your dropout-to-architect narrative is underused and highly engaging")
w()
w("### Platform-Specific Insights")
w()
w("| Platform | What Works Best | Optimal Length | Key Metric |")
w("|----------|----------------|----------------|------------|")
w("| YouTube | Tutorials, tool demos, 'how I did it' stories | 8-15 min (long), <60s (shorts) | Views/Subs ratio >= 3x |")
w("| Instagram | Speed demos, AI hacks, aspirational lifestyle | 15-45 seconds | Views/Followers >= 3x |")
w("| LinkedIn | Personal stories, hot takes, credibility posts | 150-300 words | Likes+Comments+Shares total |")
w()

# Write file
output_path = RESULTS / "viral_content_research.md"
with open(output_path, "w", encoding="utf-8") as f:
    f.write("\n".join(lines))

print(f"Deliverable written to: {output_path}")
print(f"Total lines: {len(lines)}")

# Also save raw data summary
summary = {
    "youtube": {
        "total_videos": len(yt["persona_1"]["all"]) + len(yt["persona_2"]["all"]),
        "p1_winners": len(yt["persona_1"]["winners"]),
        "p2_winners": len(yt["persona_2"]["winners"]),
    },
    "instagram": {
        "total_reels": len(ig["persona_1"]["all"]) + len(ig["persona_2"]["all"]),
        "p1_winners": len(ig["persona_1"]["winners"]),
        "p2_winners": len(ig["persona_2"]["winners"]),
    },
    "linkedin": {
        "total_posts": li.get("raw_count", len(li["all"])),
        "processed_posts": len(li["all"]),
    },
}
print(f"\nData Summary: {json.dumps(summary, indent=2)}")

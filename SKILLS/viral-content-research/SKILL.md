---
name: viral-content-research
description: Researches viral content on YouTube, Instagram, and LinkedIn for specific business personas. Identifies "winning" posts (high view-to-follower ratio), analyzes engagement, and generates tailored content ideas. Use this skill when tasked with identifying content trends, finding viral hooks, or performing competitor research for AI-focused creators and agencies.
---

# Viral Content Research

## Overview

This skill automates the discovery and analysis of viral content across major social platforms (YouTube, Instagram, LinkedIn). It is specifically tuned for two target personas: **Business Professionals** (AI for productivity) and **AI Agency Builders**. By identifying content that significantly outperforms a creator's average (3x+ virality ratio), it extracts the underlying patterns that drive engagement.

## Workflow

To perform a complete research cycle, follow these steps:

### 1. Configure Personas and API Keys

Before running research, ensure the following reference files are up-to-date:

- `references/api-keys.md`: Contains YouTube API Key and Apify Token.
- `references/personas.md`: Defines keywords for YouTube and hashtags for Instagram.
- `references/creators.md`: Lists LinkedIn profile URLs to be monitored.

### 2. Run Platform Scrapers

Execute the following scripts located in the `scripts/` directory. Each script will save its results to the `results/` folder.

- **YouTube Research**:

  ```bash
  python scripts/youtube_viral_search.py
  ```

- **Instagram Research**:

  ```bash
  python scripts/instagram_viral_search.py
  ```

- **LinkedIn Research**:

  ```bash
  python scripts/linkedin_viral_search.py
  ```

### 3. Compile Deliverable

Once all platform data is collected in `results/`, run the compiler to generate the final report:

```bash
python scripts/compile_deliverable.py
```

The final report will be generated as `results/viral_content_research.md`.

## Methodology

### Virality Metrics

- **YouTube/Instagram**: Calculated as `Views / Followers`. A ratio of **3.0 or higher** is considered a "Winning Post".
- **LinkedIn**: Since follower counts are less accessible, content is ranked by **Total Engagement** (Likes + Comments + Shares).

### Personas

1. **Business Professionals**: Interested in AI tools (ChatGPT, Claude), productivity hacks, and future-of-work trends.
2. **AI Agency Builders**: Interested in business models, technical tutorials (n8n, agents), and client acquisition strategies.

## Resources

- **scripts/**:
  - `youtube_viral_search.py`: Searches YouTube Data API v3 and calculates virality.
  - `instagram_viral_search.py`: Uses Apify's Instagram Scraper (requires Token).
  - `linkedin_viral_search.py`: Uses Apify's LinkedIn Profile Posts Scraper (no cookies needed).
  - `compile_deliverable.py`: Consolidates JSON results into a beautiful Markdown report.
- **references/**:
  - `api-keys.md`: Securely store keys (parse using regex or split).
  - `personas.md`: Update keywords/hashtags as trends shift.
  - `creators.md`: Add new competitive creators to monitor on LinkedIn.
- **results/**: (Generated)
  - Raw JSON results for each platform.
  - `viral_content_research.md`: The final consumable report.

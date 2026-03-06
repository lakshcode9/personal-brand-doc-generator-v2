import os
import json
import sys
from googleapiclient.discovery import build
from youtube_transcript_api import YouTubeTranscriptApi

SCRIPT_DIR = os.path.dirname(os.path.abspath(__file__))
BASE_DIR = os.path.dirname(SCRIPT_DIR)
INPUT_PATH = os.path.join(BASE_DIR, "client_input.json")
TMP_DIR = os.path.join(BASE_DIR, ".tmp")
OUTPUT_PATH = os.path.join(TMP_DIR, "youtube_data.json")

# Load Env
from dotenv import load_dotenv
load_dotenv(os.path.join(BASE_DIR, '.env'))

def get_transcript(video_id):
    try:
        transcript_list = YouTubeTranscriptApi.get_transcript(video_id)
        # Combine all text pieces
        full_text = " ".join([t['text'] for t in transcript_list])
        return full_text
    except Exception as e:
        print(f"    ⚠️ Could not fetch transcript for {video_id}: {e}")
        return None

def scrape_youtube():
    if not os.path.exists(INPUT_PATH):
        print(f"❌ Error: {INPUT_PATH} not found.")
        sys.exit(1)
        
    api_key = os.environ.get("YOUTUBE_API_KEY")
    youtube = None
    if not api_key:
        print("⚠️ Warning: YOUTUBE_API_KEY not found in .env. Using mock data for search, but will still try to fetch transcripts if video IDs are mocked.")
    else:
        youtube = build("youtube", "v3", developerKey=api_key)
    
    with open(INPUT_PATH, "r", encoding="utf-8") as f:
        client_data = json.load(f)
        
    personas = client_data.get("personas", [])
    if not personas:
        print("❌ Error: No personas found in client_input.json")
        sys.exit(1)
        
    os.makedirs(TMP_DIR, exist_ok=True)
    
    all_results = {}
    
    print("🎥 Starting YouTube Scraper & Transcript Engine...")
    for persona in personas:
        persona_id = persona["id"]
        keywords = persona.get("youtube_keywords", [])
        print(f"\n🔍 Processing Persona: {persona['name']}")
        
        persona_videos = []
        for kw in keywords[:2]: # Limit to top 2 keywords per persona to save API quota
            print(f"  -> Searching keyword: '{kw}'")
            try:
                if youtube:
                    search_response = youtube.search().list(
                        q=kw,
                        part="id,snippet",
                        maxResults=3, # Top 3 videos per keyword
                        type="video",
                        order="viewCount"
                    ).execute()
                    
                    for item in search_response.get("items", []):
                        vid_id = item["id"]["videoId"]
                        title = item["snippet"]["title"]
                        channel = item["snippet"]["channelTitle"]
                        
                        print(f"    🎬 Found Video: {title} ({channel})")
                        transcript = get_transcript(vid_id)
                        
                        persona_videos.append({
                            "video_id": vid_id,
                            "title": title,
                            "channel": channel,
                            "keyword": kw,
                            "transcript": transcript
                        })
                else:
                    # Mock Video ID that definitely has a transcript for demo purposes
                    vid_id = "jNQXAC9IVRw" # Me at the zoo (has transcript sometimes, or we can use another famous one)
                    # Actually let's use a very popular AI video 
                    vid_id = "zjkBMFhNj_g" 
                    title = f"Secret to {kw} (Mocked)"
                    channel = "MockChannel"
                    
                    print(f"    🎬 Found Video (MOCK): {title} ({channel})")
                    transcript = get_transcript(vid_id) or "This is a mock transcript about how AI is changing content creation."
                    
                    persona_videos.append({
                        "video_id": vid_id,
                        "title": title,
                        "channel": channel,
                        "keyword": kw,
                        "transcript": transcript
                    })

            except Exception as e:
                print(f"  ❌ Error searching YouTube API: {e}")
                
        all_results[persona_id] = persona_videos
        
    with open(OUTPUT_PATH, "w", encoding="utf-8") as f:
        json.dump(all_results, f, indent=4)
        
    print(f"\n✅ YouTube scraping complete! Transcripts saved to {OUTPUT_PATH}")

if __name__ == "__main__":
    scrape_youtube()

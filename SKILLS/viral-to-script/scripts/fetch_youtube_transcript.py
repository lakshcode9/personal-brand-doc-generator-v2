"""
Utility to fetch YouTube transcripts.
"""
import sys
import io
import json
from youtube_transcript_api import YouTubeTranscriptApi

# Fix terminal encoding issues on Windows
if sys.stdout.encoding.lower() != 'utf-8':
    sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8', errors='replace')
if sys.stderr.encoding.lower() != 'utf-8':
    sys.stderr = io.TextIOWrapper(sys.stderr.buffer, encoding='utf-8', errors='replace')

def get_transcript(video_id):
    try:
        from youtube_transcript_api import YouTubeTranscriptApi
        api = YouTubeTranscriptApi()
        # Based on dir(api) showing 'list' and 'fetch'
        transcript_list = api.list(video_id)
        # Try to get manual transcript in English, then auto in English
        try:
            transcript = transcript_list.find_transcript(['en'])
        except:
            transcript = transcript_list.find_generated_transcript(['en'])
        
        data = transcript.fetch()
        # The FetchedTranscriptSnippet objects have 'text' attribute or it's a list of dicts?
        # Standard return for fetch() is a list of dicts with 'text', 'start', 'duration'
        # Wait, the error said 'object is not subscriptable' which is weird for a dict.
        # Let's try to see if it's an object with .text attribute
        try:
            transcript_text = " ".join([item['text'] for item in data])
        except (TypeError, KeyError):
            transcript_text = " ".join([item.text for item in data])
        return transcript_text
    except Exception as e:
        print(f"Error fetching transcript for {video_id}: {e}")
        return None

if __name__ == "__main__":
    if len(sys.argv) < 2:
        print("Usage: python fetch_youtube_transcript.py <video_id>")
        sys.exit(1)
    
    video_id = sys.argv[1]
    transcript = get_transcript(video_id)
    if transcript:
        # If run as script, just print first 500 chars
        print(transcript[:1000] + "...")

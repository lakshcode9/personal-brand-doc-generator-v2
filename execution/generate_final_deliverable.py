import json
import os
import sys
from groq_client import generate_completion

SCRIPT_DIR = os.path.dirname(os.path.abspath(__file__))
BASE_DIR = os.path.dirname(SCRIPT_DIR)

INPUT_PATH = os.path.join(BASE_DIR, "client_input.json")
YT_PATH = os.path.join(BASE_DIR, ".tmp", "youtube_data.json")
MD_OUTPUT_PATH = os.path.join(BASE_DIR, "client_deliverable.md")

def generate_deliverable():
    if not os.path.exists(INPUT_PATH):
        print("❌ Error: client_input.json not found.")
        sys.exit(1)
        
    with open(INPUT_PATH, "r", encoding="utf-8") as f:
        client_data = json.load(f)
        
    yt_data = {}
    if os.path.exists(YT_PATH):
        with open(YT_PATH, "r", encoding="utf-8") as f:
            yt_data = json.load(f)
            
    print("🧠 Generating Final Synthesis & Scripts using Groq...")
    
    # We will build a massive context string incorporating all the transcripts.
    context_str = ""
    for persona_id, videos in yt_data.items():
        context_str += f"\n\n--- PERSONA: {persona_id} ---\n"
        for v in videos:
            if v.get('transcript'):
                context_str += f"\nVIDEO: {v['title']}\n"
                # Limiting transcript length so we don't blow up context window unnecessarily
                context_str += f"TRANSCRIPT EXTRACT:\n{v['transcript'][:1500]}...\n"

    prompt = f"""
    You are an elite short-form content scriptwriter. 
    You have analyzed the transcripts of the top competing viral videos for our personas.
    
    Client Info:
    Name: {client_data['brand']['name']}
    Offer: {client_data['brand']['core_offer']}
    Tone: {client_data['brand']['brand_tone']}
    
    Viral Transcripts Context:
    {context_str}
    
    Your task is to write a final client deliverable formatted as a Premium Markdown Document titled "# Final Synthesis & Scripts".
    Include the following sections:
    1. "Viral Hook Analysis" - What hooks are currently working based on the transcripts?
    2. "Content Gap" - What are the competitors missing that {client_data['brand']['name']} can provide?
    3. "3 Ready-to-Shoot Scripts" - Write 3 distinct, fully fleshed-out short-form video scripts (Title, Hook, Body, Call to Action). Ensure they match the client's tone perfectly.
    
    Do NOT output anything other than the raw Markdown text.
    """
    
    system_prompt = "You are a master of algorithmic storytelling and a top-tier brand strategist."
    deliverable_md = generate_completion(prompt, system_prompt=system_prompt)
    
    with open(MD_OUTPUT_PATH, "w", encoding="utf-8") as f:
        f.write(deliverable_md)
        
    print(f"✅ Final Deliverable generated and saved to {MD_OUTPUT_PATH}")

if __name__ == "__main__":
    generate_deliverable()

import json
import os
import sys
from groq_client import generate_completion

SCRIPT_DIR = os.path.dirname(os.path.abspath(__file__))
BASE_DIR = os.path.dirname(SCRIPT_DIR)
INPUT_PATH = os.path.join(BASE_DIR, "client_input.json")
ICP_PATH = os.path.join(BASE_DIR, "icp.md")
MD_OUTPUT_PATH = os.path.join(BASE_DIR, "personas.md")

def generate_personas():
    if not os.path.exists(INPUT_PATH) or not os.path.exists(ICP_PATH):
        print("❌ Error: client_input.json or icp.md not found.")
        sys.exit(1)
        
    with open(INPUT_PATH, "r", encoding="utf-8") as f:
        client_data = json.load(f)
        
    with open(ICP_PATH, "r", encoding="utf-8") as f:
        icp_md = f.read()

    print("🧠 Generating Platform Personas & Search Keywords using Groq...")
    
    prompt = f"""
    You are a growth marketing data engineer. Based on the client's information and ICP, create exactly 2 distinct target personas.
    
    Client Info:
    Name: {client_data['brand']['name']}
    Niche: {client_data['brand']['niche']}
    
    ICP Summary:
    {icp_md[:1000]}...
    
    You MUST output valid JSON ONLY, in matching this schema exactly:
    {{
      "personas": [
        {{
          "id": "persona_1",
          "name": "Persona 1 Name",
          "description": "Short bio",
          "youtube_keywords": ["keyword 1", "keyword 2", "keyword 3", "keyword 4"],
          "instagram_hashtags": ["tag1", "tag2", "tag3", "tag4"],
          "linkedin_profiles": ["https://linkedin.com/in/example1", "https://linkedin.com/in/example2", "https://linkedin.com/in/example3"]
        }},
        ... (repeat for persona_2)
      ]
    }}
    
    Ensure the YouTube keywords are highly searchable phrases. Ensure the LinkedIn profiles are real, active big creators in this exact niche (give best guesses). 
    """
    
    try:
        response_json = generate_completion(prompt, json_mode=True)
        personas_data = json.loads(response_json)
    except Exception as e:
        print(f"❌ Error parsing LLM response: {e}")
        print("Raw response:", response_json)
        sys.exit(1)
        
    # Save the JSON back to the client_input as configuration
    client_data["personas"] = personas_data.get("personas", [])
    with open(INPUT_PATH, "w", encoding="utf-8") as f:
        json.dump(client_data, f, indent=4)
        
    # Create the markdown view for the dashboard
    md_lines = ["# 👤 Platform Search Personas\n"]
    md_lines.append("> These are the AI-generated target avatars driving our automated scraping pipelines.\n\n")
    
    for p in client_data["personas"]:
        md_lines.append(f"## {p['name']}\n")
        md_lines.append(f"*{p['description']}*\n\n")
        md_lines.append("### 🔴 YouTube Target Keywords\n")
        for kw in p.get("youtube_keywords", []):
            md_lines.append(f"- `{kw}`\n")
        md_lines.append("\n### 🟣 Instagram Target Hashtags\n")
        for tag in p.get("instagram_hashtags", []):
            md_lines.append(f"- `#{tag.replace('#', '')}`\n")
        md_lines.append("\n### 🔵 LinkedIn Target Creators\n")
        for url in p.get("linkedin_profiles", []):
            md_lines.append(f"- [{url}]({url})\n")
        md_lines.append("\n---\n\n")
        
    with open(MD_OUTPUT_PATH, "w", encoding="utf-8") as f:
        f.write("".join(md_lines))
        
    print(f"✅ Personas generated and saved to {INPUT_PATH} and {MD_OUTPUT_PATH}")

if __name__ == "__main__":
    generate_personas()

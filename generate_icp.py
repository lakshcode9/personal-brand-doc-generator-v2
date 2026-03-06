import json
import os
import sys
from groq_client import generate_completion
from supabase_client import upsert_brand_project

SCRIPT_DIR = os.path.dirname(os.path.abspath(__file__))
BASE_DIR = os.path.dirname(SCRIPT_DIR)
INPUT_PATH = os.path.join(BASE_DIR, "client_input.json")
OUTPUT_PATH = os.path.join(BASE_DIR, "icp.md")

def generate_icp():
    if not os.path.exists(INPUT_PATH):
        print(f"❌ Error: {INPUT_PATH} not found. Run mock_webhook.py first.")
        sys.exit(1)
        
    with open(INPUT_PATH, "r", encoding="utf-8") as f:
        client_data = json.load(f)["brand"]
        
    print(f"🧠 Generating ICP for {client_data['name']} using Groq...")
    
    prompt = f"""
    Analyze the following deep-dive client business data and create a comprehensive Ideal Customer Profile (ICP) markdown document.
    This business needs a content engine that solves their specific bottleneck.
    
    -- CLIENT BUSINESS PROFILE --
    Name: {client_data.get('name')}
    Niche: {client_data.get('niche')}
    Target Audience: {client_data.get('target_audience')}
    Core Offer: {client_data.get('core_offer')}
    Current LTV: {client_data.get('ltv')}
    Current CAC: {client_data.get('cac')}
    Lead Gen Strategy: {client_data.get('lead_gen')}
    Sales Process & Closing: {client_data.get('current_sales_process')} | {client_data.get('closing_mech')}
    Delivery & Retention: {client_data.get('delivery')} | {client_data.get('retention')}
    Current MRR/Profit: {client_data.get('current_mrr')}
    12-Month Goal: {client_data.get('goals')}
    Biggest Bottleneck: {client_data.get('bottleneck')}
    ---------------------------
    
    Output a beautiful, highly structured Markdown document titled "# Target ICP Strategy".
    Include sections for:
    1. The Ultimate Avatar (Demographics, Psychographics, core fears based on the client's niche)
    2. The Symptom vs. The Root Cause (What the avatar thinks is the problem vs what the client's offer actually solves)
    3. 3 Core Content Pillars (tailored to solve their {client_data.get('bottleneck')} bottleneck via social content)
    4. The Value Proposition (Why the avatar should trust {client_data.get('name')} based on their delivery/offer)
    
    Make the response formatting rich (use quotes, bolding, bullet points).
    DO NOT output anything other than the markdown text itself.
    """
    
    system_prompt = "You are a top-tier brand strategist executing an elite branding framework."
    
    icp_md = generate_completion(prompt, system_prompt=system_prompt)
    
    with open(OUTPUT_PATH, "w", encoding="utf-8") as f:
        f.write(icp_md)
        
    print(f"✅ ICP generated successfully at {OUTPUT_PATH}")
    
    # Sync with Supabase
    with open(INPUT_PATH, "r", encoding="utf-8") as f:
        cid = json.load(f)["client_id"]
        
    upsert_brand_project(cid, {
        "icp_markdown": icp_md,
        "status": "pending_personas"
    })

if __name__ == "__main__":
    generate_icp()

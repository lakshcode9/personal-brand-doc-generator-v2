"""
Main Orchestrator for analyzing viral content and generating On-Brand scripts.
"""
import sys
import io
import json
import os
from pathlib import Path
from fetch_youtube_transcript import get_transcript

# Fix terminal encoding issues on Windows
if sys.stdout.encoding.lower() != 'utf-8':
    sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8', errors='replace')
if sys.stderr.encoding.lower() != 'utf-8':
    sys.stderr = io.TextIOWrapper(sys.stderr.buffer, encoding='utf-8', errors='replace')

def load_brand_voice():
    script_dir = Path(__file__).parent.resolve()
    # Check for root brand_config first
    root_config = script_dir.parents[2] / "brand_config.json"
    if root_config.exists():
        with open(root_config, "r", encoding="utf-8") as f:
            config = json.load(f)
            return f"{config['brand']['name']} - {config['brand']['tagline']}. Focus: {config['strategy']['focus']}"
            
    voice_file = script_dir.parent / "references" / "brand-voice.md"
    if voice_file.exists():
        return voice_file.read_text(encoding='utf-8')
    return "Generic Brand Voice: High-authority, data-driven content."

def load_viral_results():
    # Attempt to load from the viral-content-research skill results
    script_dir = Path(__file__).parent.resolve()
    research_results_dir = script_dir.parents[1] / "viral-content-research" / "results"
    
    data = {}
    for platform in ['youtube', 'instagram', 'linkedin']:
        file_path = research_results_dir / f"{platform}_viral_results.json"
        if file_path.exists():
            with open(file_path, "r", encoding="utf-8") as f:
                data[platform] = json.load(f)
    return data

def generate_brand_script(platform, original_content, brand_voice):
    """
    PLACEHOLDER for LLM generation logic.
    In the actual agent workflow, the agent uses its own 'thinking' 
    to process these prompts and generate the output.
    """
    # This function is intended to be used by the agent during the task
    pass

def main():
    print("🚀 Starting Content Generation Orchestrator...")
    brand_voice = load_brand_voice()
    viral_data = load_viral_results()
    
    if not viral_data:
        print("❌ Error: No viral research results found in SKILLS/viral-content-research/results/")
        sys.exit(1)
        
    script_dir = Path(__file__).parent.resolve()
    output_dir = script_dir.parent / "results"
    output_dir.mkdir(parents=True, exist_ok=True)
    
    # We will pick top 1-2 winners from each platform to analyze
    # This script will act as a template for the agent to follow
    print("✅ Logic ready. I will now proceed to analyze top winners and generate scripts.")

if __name__ == "__main__":
    main()

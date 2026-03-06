import os
import sys
import time
import subprocess

SCRIPT_DIR = os.path.dirname(os.path.abspath(__file__))

def run_script(script_name):
    print(f"\n=====================================")
    print(f"🚀 RUNNING: {script_name}")
    print(f"=====================================")
    
    script_path = os.path.join(SCRIPT_DIR, script_name)
    try:
        subprocess.run(["python", script_path], check=True)
    except subprocess.CalledProcessError as e:
        print(f"\n❌ Pipeline failed at {script_name}.")
        print(f"Error details: {e}")
        sys.exit(1)
    except Exception as e:
        print(f"\n❌ Unexpected pipeline failure at {script_name}: {e}")
        sys.exit(1)

def main():
    print("🌟 STARTING 3H CREATOR - TALLY TO DELIVERABLE PIPELINE 🌟\n")
    
    # Phase 1: Ingestion
    run_script("mock_webhook.py")
    time.sleep(1)
    
    # Phase 2: ICP Generation
    run_script("generate_icp.py")
    time.sleep(1)
    
    # Phase 3: Persona Generation
    run_script("generate_personas.py")
    time.sleep(1)
    
    # Phase 4: Social Scrapers (YouTube Transcripts & Apify)
    run_script("scraper_youtube.py")
    run_script("scraper_apify.py")
    time.sleep(1)
    
    # # Phase 5: Final Groq Synthesis
    run_script("generate_final_deliverable.py")
    
    print("\n✅ PIPELINE COMPLETED SUCCESSFULLY! Output ready for dashboard.")

if __name__ == "__main__":
    main()

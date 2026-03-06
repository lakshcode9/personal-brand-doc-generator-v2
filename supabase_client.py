import os
from supabase import create_client, Client
from dotenv import load_dotenv

load_dotenv()

def get_supabase() -> Client:
    url: str = os.environ.get("SUPABASE_URL")
    key: str = os.environ.get("SUPABASE_KEY")
    if not url or not key:
        print("⚠️ SUPABASE_URL or SUPABASE_KEY not found in .env")
        return None
    return create_client(url, key)

def upsert_brand_project(client_id, data: dict):
    sb = get_supabase()
    if not sb: return
    
    # Check if exists
    try:
        sb.table("brand_projects").upsert({
            "client_id": client_id,
            **data
        }, on_conflict="client_id").execute()
    except Exception as e:
        print(f"❌ Supabase Sync Error: {e}")

def get_brand_project(client_id):
    sb = get_supabase()
    if not sb: return None
    
    res = sb.table("brand_projects").select("*").eq("client_id", client_id).execute()
    if res.data:
        return res.data[0]
    return None

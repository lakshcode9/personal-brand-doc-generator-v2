import os
import json
import threading
import sys

# Ensure current directory is in path for module resolution
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from flask import Flask, request, jsonify, send_from_directory, Response
# Flattened structure for Heroku compatibility (Windows/Linux filename issues)
from mock_webhook import process_tally_webhook
from main_pipeline import main as run_pipeline
from supabase_client import get_brand_project

app = Flask(__name__, static_folder='.', static_url_path='')

@app.route('/')
def index():
    return send_from_directory('.', 'index.html')

@app.route('/<path:path>')
def serve_static(path):
    # If the file exists locally, serve it standard
    if os.path.exists(path):
        return send_from_directory('.', path)
    
    # Fallback for Markdown docs: fetch from Supabase
    if path.endswith('.md'):
        # For simplicity, we fetch the first project or use a hardcoded client_id for now
        # Ideally, we'd pass client_id in the URL or session.
        # Here we attempt to find the latest submission.
        project = get_brand_project("test_client") # Default test ID from mock_webhook
        if not project:
            # Try to get any project if test_client fails
            from supabase_client import get_supabase
            sb = get_supabase()
            res = sb.table("brand_projects").select("*").limit(1).execute()
            if res.data: project = res.data[0]
            
        if project:
            content = ""
            if path == 'icp.md': content = project.get('icp_markdown', '')
            elif path == 'personas.md': content = project.get('persona_markdown', '')
            elif path == 'client_deliverable.md': content = project.get('final_deliverable_markdown', '')
            
            if content:
                return Response(content, mimetype='text/markdown')

    # Fallback for client_input.json
    if path == 'client_input.json':
        project = get_brand_project("test_client")
        if project:
            # Reconstruction of the structure for frontend
            client_input = {
                "brand": project.get("brand_profile", {}),
                "contact": project.get("contact_info", {}),
                "status": project.get("status", "unknown")
            }
            return jsonify(client_input)

    return send_from_directory('.', path)

@app.route('/api/webhook', methods=['POST'])
def tally_webhook():
    """Endpoint for the actual Tally webhook."""
    data = request.json
    
    # Save the incoming payload temporarily (if using ephemeral storage)
    # In a full Supabase DB implementation, we would write this straight to Postgres.
    payload_path = "sample_tally_payload.json"
    with open(payload_path, "w", encoding="utf-8") as f:
        json.dump(data, f)
        
    process_tally_webhook()
    
    # Spin up AI pipeline in background so we don't block the webhook response (Tally expects a fast 200 OK)
    threading.Thread(target=run_pipeline).start()
    
    return jsonify({"status": "success", "message": "Pipeline started."}), 200

@app.route('/api/generate-dummy', methods=['POST'])
def generate_dummy():
    """Endpoint triggered by UI to mock a webhook event for testing without filling out a form."""
    
    # The sample_tally_payload.json is already formulated with dummy data
    process_tally_webhook()
    
    # Run pipeline in background
    threading.Thread(target=run_pipeline).start()
    
    return jsonify({"status": "success", "message": "Dummy pipeline started."}), 200

if __name__ == '__main__':
    port = int(os.environ.get('PORT', 8080))
    app.run(host='0.0.0.0', port=port)

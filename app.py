import os
import json
import threading
from flask import Flask, request, jsonify, send_from_directory

from execution.mock_webhook import process_tally_webhook
from execution.main_pipeline import main as run_pipeline

app = Flask(__name__, static_folder='.', static_url_path='')

@app.route('/')
def index():
    return send_from_directory('.', 'index.html')

@app.route('/<path:path>')
def serve_static(path):
    # Serve static files (Markdown docs, JSON config, CSS, JS)
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

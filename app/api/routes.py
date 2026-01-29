from flask import Blueprint, jsonify
from app.extensions import mongo

api = Blueprint('api', __name__, url_prefix='/api')

@api.route('/events', methods=['GET'])
def get_events():
    try:
        # Fetch events sorted by timestamp descending
        events = list(mongo.db.events.find().sort('timestamp', -1).limit(50))

        for event in events:
            event['_id'] = str(event['_id'])
        
        return jsonify(events), 200
    except Exception as e:
        print(f"Error fetching events: {str(e)}")
        return jsonify({"error": str(e)}), 500

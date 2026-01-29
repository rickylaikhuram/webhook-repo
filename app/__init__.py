from flask import Flask
from flask_cors import CORS
from app.webhook.routes import webhook
from app.api.routes import api
from app.extensions import init_db
from dotenv import load_dotenv
load_dotenv()

# Creating our flask app
def create_app():
    app = Flask(__name__)
    
    # Enable CORS for frontend requests
    CORS(app)
    
    # Initialize MongoDB
    init_db(app)
    
    # Registering all the blueprints
    app.register_blueprint(webhook)
    app.register_blueprint(api)
    
    return app
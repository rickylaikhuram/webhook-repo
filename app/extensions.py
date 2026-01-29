import os
from flask_pymongo import PyMongo

mongo = PyMongo()

def init_db(app):
    mongo_uri = os.getenv("MONGO_URI")

    if not mongo_uri:
        raise RuntimeError("MONGO_URI environment variable not set")

    app.config["MONGO_URI"] = mongo_uri
    mongo.init_app(app)

    try:
        # Force a connection check
        mongo.cx.server_info()
        print("MongoDB connected successfully!")
    except Exception as e:
        raise RuntimeError(f"MongoDB connection failed: {e}")

    return mongo

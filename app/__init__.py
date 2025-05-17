from flask import Flask
import os
from flask_cors import CORS

def create_app():
    # Create the Flask app
    app = Flask(__name__, static_folder="../static", template_folder="../frontend")
    app.config["ENV"] = os.getenv("FLASK_ENV", "production")  # Defaults to 'production'

    # Enable CORS for all domains and all routes
    CORS(app, supports_credentials=True, resources={r"/*": {"origins": "*"}})

    # Only register the query and static blueprints
    from app.routes.query import query_bp
    from app.routes.static_files import static_bp

    app.register_blueprint(query_bp)
    app.register_blueprint(static_bp)

    return app
from flask import Flask
from flask_cors import CORS
import os

def create_app():
    # Create the Flask app
    app = Flask(__name__, static_folder="../app/static", template_folder="../app/templates")
    app.config["ENV"] = os.getenv("FLASK_ENV", "production")  # Defaults to 'production'

    # Enable CORS
    CORS(app, supports_credentials=True, resources={r"/*": {"origins": "*"}})

    # Register Blueprints
    from app.routes.query import query_bp
    from app.routes.static_files import static_bp
    from app.routes.dashboard import dashboard_bp

    app.register_blueprint(query_bp)
    app.register_blueprint(static_bp)
    app.register_blueprint(dashboard_bp, url_prefix="/dashboard")

    return app
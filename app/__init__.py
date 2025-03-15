from flask import Flask, jsonify
from flask_cors import CORS
import os

def create_app():
    # Create the Flask app
    app = Flask(__name__, static_folder="../static", template_folder="../frontend")
    app.config["ENV"] = os.getenv("FLASK_ENV", "production")  # Defaults to 'production'

    # Enable CORS
    CORS(app, supports_credentials=True, resources={r"/*": {"origins": "*"}})

    # Register Blueprints
    from app.routes.query import query_bp
    from app.routes.static_files import static_bp
    from app.routes.upload_pdf import upload_pdf_bp
    from app.routes.admin import admin_bp 

    app.register_blueprint(query_bp)
    app.register_blueprint(static_bp)
    app.register_blueprint(upload_pdf_bp)
    app.register_blueprint(admin_bp)

    # -----------------------------
    # ✅ Global Error Handlers (Ensures JSON Responses)
    # -----------------------------

    @app.errorhandler(404)
    def not_found_error(error):
        return jsonify({"error": "Endpoint not found"}), 404

    @app.errorhandler(500)
    def internal_server_error(error):
        return jsonify({"error": "Internal server error"}), 500

    return app
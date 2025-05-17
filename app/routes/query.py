from flask import Blueprint, request, jsonify, render_template, current_app
import uuid
import os

query_bp = Blueprint('query', __name__)

PORT = os.getenv('PORT', 5000)

def get_base_urls():
    """Utility function to compute script_base_url and base_url."""
    script_base_url = (
        f"http://127.0.0.1:{PORT}/cdn"  # Internal during local development
        if current_app.config.get("ENV") == "development"  # ENV should be set in your Flask app
        else "https://rstmh-ai-agent-cdn.onrender.com"  # External for production
    )
    base_url = (
        f"http://127.0.0.1:{PORT}"
        if current_app.config.get("ENV") == "development"
        else "https://rstmh-ai-agent.onrender.com"
    )
    return script_base_url, base_url

@query_bp.route("/")
def index():
    # Call the utility function to get the URLs
    script_base_url, base_url = get_base_urls()
    return render_template("index.html", script_base_url=script_base_url, base_url=base_url)

@query_bp.route("/debug")
def debug():
    # Call the same utility function to get the URLs
    script_base_url, base_url = get_base_urls()
    return jsonify({
        "ENV": current_app.config.get("ENV"),
        "script_base_url": script_base_url,
        "base_url": base_url
    })

@query_bp.route("/query", methods=["POST"])
def query_handler():
    print("[QUERY] Received request: headers=", dict(request.headers))
    print("[QUERY] Raw body:", request.get_data(as_text=True))
    user_id = request.headers.get("X-User-ID")
    if user_id in [None, 'null']:
        user_id = str(uuid.uuid4())
    session_id = request.headers.get("X-Session-ID")
    if session_id in [None, 'null']:
        session_id = str(uuid.uuid4())
    data = request.json or {}
    user_query = data.get("user_query", "").strip()
    response = {
        "user_id": user_id,
        "session_id": session_id,
        "query": user_query,
        "answer": "Thank you for your interest. Applications for the 2025 RSTMH Early Career Grants Programme are now closed.",
        "context": [],
        "source": None
    }
    print("[QUERY] Sending response:", response)
    return jsonify(response)

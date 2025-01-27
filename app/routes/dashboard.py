from flask import Blueprint, render_template, jsonify, current_app, request
from app.services.supabase_logging import SupabaseLogger

dashboard_bp = Blueprint("dashboard", __name__)

logger = SupabaseLogger()

@dashboard_bp.route("/", methods=["GET"])
def dashboard_page():
    """Render the dashboard page."""
    return render_template("dashboard.html")

@dashboard_bp.route("/api/dashboard-data", methods=["GET"])
def dashboard_data():
    """Provide data for the dashboard."""
    try:
        # Fetch user and session counts from Supabase
        session_count = logger.get_total_sessions()
        user_count = logger.get_total_users()
        return jsonify({"sessions": session_count, "users": user_count})
    except Exception as e:
        current_app.logger.error("Failed to fetch dashboard data: %s", str(e))
        return jsonify({"error": "Failed to fetch dashboard data"}), 500
    
@dashboard_bp.route("/api/session-details", methods=["GET"])
def session_details():
    """Fetch details of sessions."""
    try:
        session_id = request.args.get("session_id")
        details = logger.get_session_details(session_id=session_id)
        return jsonify(details)
    except Exception as e:
        current_app.logger.error("Failed to fetch session details: %s", str(e))
        return jsonify({"error": "Failed to fetch session details"}), 500
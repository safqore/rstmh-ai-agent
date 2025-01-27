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
    """Provide session details for a given session."""
    try:
        # Required parameters
        session_id = request.args.get("session_id")
        if not session_id:
            raise ValueError("Session ID is required.")

        # Optional filters
        limit = int(request.args.get("limit", 10))  # Default pagination limit
        offset = int(request.args.get("offset", 0))  # Default pagination offset
        start_date = request.args.get("start_date")  # Filter by start date
        end_date = request.args.get("end_date")  # Filter by end date
        user_id = request.args.get("user_id")  # Filter by user ID
        search_query = request.args.get("search_query", "")  # Optional search term

        # Fetch session details
        details, total_count = logger.get_session_details(
            session_id=session_id,
            limit=limit,
            offset=offset,
            start_date=start_date,
            end_date=end_date,
            user_id=user_id,
            search_query=search_query,
        )

        return jsonify({
            "session_id": session_id,
            "details": details,
            "total_count": total_count,
            "limit": limit,
            "offset": offset,
        })
    except ValueError as e:
        current_app.logger.error("Invalid input: %s", str(e))
        return jsonify({"error": str(e)}), 400
    except Exception as e:
        current_app.logger.error("Failed to fetch session details: %s", str(e))
        return jsonify({"error": "Failed to fetch session details"}), 500
    
@dashboard_bp.route("/api/all-sessions", methods=["GET"])
def list_all_sessions():
    """Fetch all distinct sessions with a sample question."""
    try:
        limit = int(request.args.get("limit", 10))
        offset = int(request.args.get("offset", 0))

        query = logger.client.table("interactions").select(
            "session_id, user_id, prompt, timestamp"
        )
        query = query.range(offset, offset + limit - 1)
        query = query.order("timestamp", desc=True)  # Order by most recent

        response = query.execute()
        if not response.data:
            return jsonify({"sessions": [], "total_count": 0})

        # Group sessions by session_id
        sessions = {}
        for row in response.data:
            if row["session_id"] not in sessions:
                sessions[row["session_id"]] = {
                    "session_id": row["session_id"],
                    "user_id": row["user_id"],
                    "sample_prompt": row["prompt"],
                    "timestamp": row["timestamp"],
                }

        return jsonify({"sessions": list(sessions.values()), "total_count": len(sessions)})
    except Exception as e:
        current_app.logger.error(f"Failed to fetch all sessions: {str(e)}")
        return jsonify({"error": "Failed to fetch sessions"}), 500
    
@dashboard_bp.route("/api/sessions", methods=["GET"])
def get_sessions():
    """Fetch all sessions with optional filters."""
    try:
        search_query = request.args.get("search_query", "")
        limit = int(request.args.get("limit", 10))
        offset = int(request.args.get("offset", 0))

        # Fetch sessions from the interactions table
        sessions, total_count = logger.get_sessions_with_filters(
            search_query=search_query,
            limit=limit,
            offset=offset,
        )

        return jsonify({"sessions": sessions, "total_count": total_count})
    except Exception as e:
        current_app.logger.error("Failed to fetch sessions: %s", str(e))
        return jsonify({"error": "Failed to fetch sessions"}), 500
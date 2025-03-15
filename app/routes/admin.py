from flask import Blueprint, request, jsonify, render_template
from app.services.qdrant_service import delete_all_collections
from functools import wraps

admin_bp = Blueprint("admin", __name__)

# Admin credentials (change this!)
ADMIN_USERNAME = "admin"
ADMIN_PASSWORD = "securepassword"

def require_auth(func):
    """Decorator to enforce basic authentication"""
    @wraps(func)
    def wrapper(*args, **kwargs):
        auth = request.authorization
        if not auth or auth.username != ADMIN_USERNAME or auth.password != ADMIN_PASSWORD:
            return jsonify({"error": "Unauthorized"}), 401
        return func(*args, **kwargs)
    return wrapper

@admin_bp.route("/admin", methods=["GET"])
def admin_dashboard():
    """Render the admin page for deleting Qdrant collections."""
    return render_template("admin.html")

@admin_bp.route("/admin/delete-all-collections_handler", methods=["DELETE"])
@require_auth
def delete_all_collections_handler():
    """Deletes all collections from Qdrant, protected by authentication."""
    try:
        response, status_code = delete_all_collections()
        return jsonify(response), status_code
    except Exception as e:
        print(f"[ERROR] Unexpected error during deletion: {str(e)}")  # Log error
        return jsonify({"error": f"Unexpected error: {str(e)}"}), 500
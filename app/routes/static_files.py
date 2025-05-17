from flask import Blueprint, send_from_directory

static_bp = Blueprint('static', __name__)

@static_bp.route('/cdn/<path:filename>')
def serve_static(filename):
    return send_from_directory('../static/cdn', filename)
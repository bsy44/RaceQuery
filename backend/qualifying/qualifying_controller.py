from flask import Blueprint, jsonify
from backend.qualifying.qualifying_service import QualifyingService

qualifying_bp = Blueprint("qualifying", __name__)

@qualifying_bp.get("/<int:season>/<int:round>/<string:session_q>")
def get_qualifying_split(season: int, round: int, session_q: str):
    if session_q not in ["Q1", "Q2", "Q3"]:
        return jsonify({"error": "Invalid session, must be Q1, Q2, or Q3"}), 400

    service = QualifyingService(season, round)
    data = service.get_split(session_q)
    return jsonify(data)

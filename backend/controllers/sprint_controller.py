from flask import Blueprint, jsonify
from backend.services.sprint_service import SprintService

sprint_bp = Blueprint('sprint', __name__)

@sprint_bp.get("/<int:season>/<int:round>")
def get_results(season, round):
    service = SprintService(season, round)
    results = service.get_sprint()

    return jsonify(results)

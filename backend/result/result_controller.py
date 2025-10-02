from flask import Blueprint, jsonify
from backend.result.result_service import ResultService

result_bp = Blueprint('results', __name__)

@result_bp.get("/<int:season>")
def list_results(season):
    service = ResultService(season)
    results = service.get_results()

    return jsonify(results)

@result_bp.get("/<int:season>/<int:round>")
def get_results(season, round):
    service = ResultService(season, round)
    results = service.get_results()

    return jsonify(results)

@result_bp.get("/<int:season>/<int:round>/stint/<driver_id>")
def get_stint(season, round, driver_id):
    service = ResultService(season, round)
    stints = service.get_stints(driver_id)
    return jsonify(stints)

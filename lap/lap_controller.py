from flask import Blueprint, jsonify
from lap.lap_service import LapService

lap_bp = Blueprint('lap', __name__)

@lap_bp.get("/<int:season>/<int:round>")
def list_laps(season, round):
    service = LapService(season, round)
    lap = service.get_lap()

    return jsonify(lap)

@lap_bp.get("/<int:season>/<int:round>/<int:lap>")
def get_lap(season, round, lap):
    service = LapService(season, round)
    lap = service.get_lap(lap)

    return jsonify(lap)
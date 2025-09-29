from flask import Blueprint, jsonify
from backend.services.race_service import RaceService

race_bp = Blueprint('race', __name__)

@race_bp.get("/<int:season>")
def list_races(season):
    service = RaceService(season)
    races = service.get_races()

    return jsonify(races)

@race_bp.get("/<int:season>/<int:round>")
def get_races(season, round):
    service = RaceService(season, round)
    races = service.get_races()

    return jsonify(races)

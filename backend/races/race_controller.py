from http import HTTPStatus
from flask import Blueprint, jsonify
from backend.races.race_service import RaceService

race_bp = Blueprint('races', __name__)

@race_bp.get("/<int:season>")
def list_races(season):
    service = RaceService(season)
    races = service.get_races()

    return jsonify([r.to_dict() for r in races]), HTTPStatus.OK

@race_bp.get("/<int:season>/<int:round>")
def get_race(season, round):
    service = RaceService(season, round)
    races = service.get_races()

    return jsonify([r.to_dict() for r in races]), HTTPStatus.OK

"""
Race RESULTS
"""
@race_bp.route("/results/<int:season>/<int:round>")
def get_race_result(season, round):
    service = RaceService(season, round)
    results = service.get_race_results()

    return jsonify([{
        "race": r.race.to_dict_for_results(),
        "Results": [dr.to_dict() for dr in r.results]
    } for r in results]), HTTPStatus.OK

"""
QUALIFYING RESULTS
"""
@race_bp.get("/qualifying/<int:season>/<int:round>/<session_q>")
def get_qualifying_split(season, round, session_q):
    service = RaceService(season, round)
    results = service.get_split(session_q)

    return jsonify(results), HTTPStatus.OK

"""
SPRINT RACE RESULTS
"""
@race_bp.get("/sprint/<int:season>/<int:round>")
def get_results(season, round):
    service = RaceService(season, round)
    results = service.get_sprint()

    return jsonify([r.to_dict() for r in results]), HTTPStatus.OK

"""
RACE LAP
"""
@race_bp.get("/<int:season>/<int:round>/lap/<driver_id>")
def list_laps(season, round, driver_id):
    service = RaceService(season, round)
    laps = service.get_laps_for_driver(driver_id)
    return jsonify([l.to_dict() for l in laps]), HTTPStatus.OK


@race_bp.get("/<int:season>/<int:round>/lap/<int:lap>")
def get_lap(season, round, lap):
    service = RaceService(season, round)
    lap = service.get_lap(lap)

    return jsonify(lap), HTTPStatus.OK

"""
DRIVERS RACE STINT
"""
@race_bp.get("/<int:season>/<int:round>/stint/<driver_id>")
def get_driver_stints(season, round, driver_id):
    service = RaceService(season, round)
    stints = service.get_stints(driver_id)

    return jsonify(stints), HTTPStatus.OK
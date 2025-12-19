from http import HTTPStatus
from flask import Blueprint, jsonify
from races.race_service import RaceService


race_bp = Blueprint('races', __name__, url_prefix='/races')

@race_bp.get('/<int:season>')
def get_schedule(season):
   service = RaceService(season)
   races = service.get_schedule()
   return jsonify(races), HTTPStatus.OK


@race_bp.get('/<int:season>/<int:round>')
def get_event(season, round):
   service = RaceService(season, round)
   races = service.get_event()
   return jsonify(races), HTTPStatus.OK


@race_bp.get('/<int:season>/<int:round>/<session>-results')
def get_session_result(session, season, round):
   service = RaceService(season, round)
   session = service.get_session_results(session)

   return jsonify(session), HTTPStatus.OK
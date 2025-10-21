from http import HTTPStatus
from flask import Blueprint, jsonify
from events.event_service import EventService

event_bp = Blueprint('events', __name__)

@event_bp.get('/<int:season>')
def get_schedule(season):
   service = EventService(season)
   events = service.get_schedule()
   return jsonify(events), HTTPStatus.OK

@event_bp.get('/<int:season>/<int:round>')
def get_event(season, round):
   service = EventService(season, round)
   events = service.get_event()
   return jsonify(events), HTTPStatus.OK

@event_bp.get('/<session>-results/<int:season>/<int:round>')
def get_session_result(session, season, round):
   service = EventService(season, round)
   session = service.get_session_results(session)

   return jsonify(session), HTTPStatus.OK
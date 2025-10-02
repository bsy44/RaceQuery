from http import HTTPStatus
from flask import Blueprint, jsonify
from backend.teams.team_service import ConstructorStandingService

team_standing_bp = Blueprint('teams_standings', __name__)

@team_standing_bp.get("/<int:year>")
def get_teams_standings(year):
    service = ConstructorStandingService(year)
    standings = service.get_constructor_standings()
    return jsonify([s.to_dict() for s in standings]), HTTPStatus.OK


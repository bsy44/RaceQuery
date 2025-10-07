from http import HTTPStatus
from flask import Blueprint, jsonify
from backend.teams.team_service import ConstructorService

team_standing_bp = Blueprint('teams', __name__)

@team_standing_bp.get("/standings/<int:year>")
def get_teams_standings(year):
    service = ConstructorService(year)
    standings = service.get_constructor_standings()
    return jsonify(standings), HTTPStatus.OK

@team_standing_bp.get("/<int:year>/<id_team>")
def get_team(year, id_team):
    service = ConstructorService(year)
    team = service.get_team(id_team)
    return jsonify(team), HTTPStatus.OK
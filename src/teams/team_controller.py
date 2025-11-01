from http import HTTPStatus
from flask import Blueprint, jsonify
from teams.services.team_service import TeamService
from teams.services.team_stat_service import TeamStatService
from teams.services.team_standing_service import TeamStandingService

team_standing_bp = Blueprint('teams', __name__)

@team_standing_bp.get("/standings/<int:year>")
def get_teams_standings(year):
    service = TeamStandingService(year)
    standings = service.get_team_standings()
    standings_dict = [s.to_dict() for s in standings]

    return jsonify(standings_dict), HTTPStatus.OK

@team_standing_bp.get("/<int:year>/<id_team>")
def get_team(year, id_team):
    service = TeamService(year)
    team = service.get_team(id_team)
    return jsonify(team.to_dict()), HTTPStatus.OK

@team_standing_bp.get("/<int:year>/<id_team>/stats")
def detail_team_stats(year, id_team):
    service = TeamStatService(year)
    stats = service.get_team_stats_summary(id_team)
    return jsonify(stats.to_dict()), HTTPStatus.OK
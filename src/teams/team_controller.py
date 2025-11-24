from http import HTTPStatus
from flask import Blueprint, jsonify
from teams.services.team_service import TeamService
from teams.services.team_stat_service import TeamStatService
from teams.services.team_standing_service import TeamStandingService


team_bp = Blueprint('teams', __name__)


@team_bp.get("/<int:year>")
def list_teams(year):
    service = TeamService(year)
    teams = service.list_teams()
    teams_dict = [t.to_dict() for t in teams]

    return jsonify(teams_dict), HTTPStatus.OK


@team_bp.get("/<int:year>/<team_id>")
def get_team(year, team_id):
    service = TeamService(year)
    result = service.get_team(team_id)

    if isinstance(result, dict) and "error" in result:
        return jsonify(result), HTTPStatus.NOT_FOUND

    return jsonify(result.to_dict()), HTTPStatus.OK


@team_bp.get("/<int:year>/standings")
def get_teams_standings(year):
    service = TeamStandingService(year)
    standings = service.get_team_standings()
    standings_dict = [s.to_dict() for s in standings]

    return jsonify(standings_dict), HTTPStatus.OK


@team_bp.get("/<int:year>/<id_team>/stats")
def get_team_stats(year, id_team):
    service = TeamStatService(year)
    stats = service.get_team_stats_summary(id_team)
    return jsonify(stats.to_dict()), HTTPStatus.OK
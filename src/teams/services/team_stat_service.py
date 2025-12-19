from teams.models.team_stat import TeamStats
from teams.services.team_service import TeamService
from utils.cache_reader import load_json_file


class TeamStatService:
    def __init__(self, year: int):
        self.year = year
        self.team_service = TeamService(year)


    def get_team_stats_summary(self, team_id: str) -> TeamStats | dict:
        filename = f"{self.year}_team_stats.json"
        all_stats = load_json_file('data_cache/services/team', filename)

        if not all_stats:
            return {
                "error": f"Pas de statistiques d'équipe disponibles pour {self.year}. Avez-vous lancé preprocess_stats.py ?"}

        team_stat_data = next((item for item in all_stats if item["constructorId"] == team_id), None)

        if not team_stat_data:
            return {"error": f"Écurie '{team_id}' non trouvée dans les services de {self.year}"}

        team_obj = self.team_service.get_team(team_id)

        if isinstance(team_obj, dict):
            team_obj = None

        return TeamStats(
            team=team_obj,
            position=int(team_stat_data.get("position", 0)),
            points=team_stat_data.get("points"),
            win=team_stat_data.get("wins"),
            podium=int(team_stat_data.get("stat_podiums", 0)),
            pole=int(team_stat_data.get("stat_poles", 0)),
            top10=int(team_stat_data.get("stat_top10", 0)),
            dnf=int(team_stat_data.get("stat_dnf", 0)),
            sprint_win=int(team_stat_data.get("stat_sprint_wins", 0)),
            sprint_podium=int(team_stat_data.get("stat_sprint_podiums", 0)),
            sprint_pole=int(team_stat_data.get("stat_sprint_poles", 0)),
            avg_race_finish=team_stat_data.get("stat_avg_race_position"),
            avg_qualifying_finish=team_stat_data.get("stat_avg_qualifying_position")
        )
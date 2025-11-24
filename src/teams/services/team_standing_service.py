from teams.models.team import Team
from teams.models.team_standing import TeamStanding
from cache_reader import load_json_file


class TeamStandingService:
    def __init__(self, year: int):
        self.year = year


    def _clean_val(self, val):
        if val == 0 or val == 0.0:
            return val
        return None if str(val).lower() == "nan" or val is None else val


    def _format_constructor(self, row: dict) -> Team:
        return Team(
            constructorId=str(row.get("constructorId")),
            constructorName=str(row.get("constructorName") or row.get("name")),
            nationality=str(row.get("constructorNationality") or row.get("nationality"))
        )


    def get_team_standings(self) -> list[TeamStanding]:
        main_filename = f"{self.year}_constructor_standings.json"

        data = load_json_file(f'data_cache/ergast/{self.year}/team', main_filename)

        if not data:
            return []

        results = []

        standings_list = data
        current_round = 0

        if isinstance(data, dict) and "standings" in data:
            standings_list = data["standings"]
            current_round = int(data.get("round", 0))

        prev_positions = {}
        if current_round > 1:
            prev_round = current_round - 1
            prev_filename = f"{self.year}_R{prev_round}_constructor_standings.json"
            prev_data = load_json_file(f'data_cache/ergast/{self.year}/team', prev_filename)

            if prev_data:
                for row in prev_data:
                    c_id = row.get('constructorId')
                    pos = int(float(row.get('position', 0)))
                    if c_id:
                        prev_positions[c_id] = pos

        for row in standings_list:
            c_id = row.get("constructorId")
            current_pos = int(row.get("position", 0))

            if c_id in prev_positions:
                evolution = prev_positions[c_id] - current_pos
            else:
                evolution = 0

            standing = TeamStanding(
                position=current_pos,
                points=row.get("points"),
                wins=row.get("wins"),
                team=self._format_constructor(row),
                evolution=evolution
            )

            results.append(standing)

        return results
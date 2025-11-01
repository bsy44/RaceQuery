import os
import fastf1
from fastf1.ergast import Ergast
from teams.models.team import Team


class TeamService:
    def __init__(self, year: int):
        self.year = year
        self.ergast = Ergast()

        cache_dir = 'src/data/fastf1_cache'
        os.makedirs(cache_dir, exist_ok=True)
        fastf1.Cache.enable_cache(cache_dir)

    def get_team(self, team_id: str) -> Team:
        standings = self.ergast.get_constructor_standings(season=self.year)
        df = standings.content[0]

        if df is None or df.empty:
            return None

        team_row = df[df["constructorId"] == team_id]
        if team_row.empty:
            return None

        row = team_row.iloc[0]

        return Team(
            constructorId=row.get("constructorId"),
            constructorName=row.get("constructorName"),
            nationality=row.get("constructorNationality")
        )

import os
import fastf1
from fastf1.ergast import Ergast
from backend.teams.team import ConstructorStanding

class ConstructorStandingService:
    def __init__(self, year: int):
        self.year = year
        self.ergast = Ergast()

        cache_dir = 'backend/data/fastf1_cache'
        os.makedirs(cache_dir, exist_ok=True)
        fastf1.Cache.enable_cache(cache_dir)

    def get_constructor_standings(self) -> list[ConstructorStanding]:
        standings = self.ergast.get_constructor_standings(season=self.year)
        df = standings.content[0] if standings and standings.content else None

        results = []
        for _, row in df.iterrows():
            results.append(ConstructorStanding(
                position=int(row["position"]),
                points=float(row["points"]),
                wins=int(row["wins"]),
                constructor=row["constructorName"]
            ))
        return results

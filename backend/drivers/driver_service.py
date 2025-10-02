import os
import fastf1
from fastf1.ergast import Ergast
from backend.drivers.driver import DriverStanding

class DriverStandingService:
    def __init__(self, year: int):
        self.year = year
        self.ergast = Ergast()

        cache_dir = "backend/data/fastf1_cache"
        os.makedirs(cache_dir, exist_ok=True)
        fastf1.Cache.enable_cache(cache_dir)

    def get_driver_standings(self) -> dict:
        standings = self.ergast.get_driver_standings(season=self.year)
        df = standings.content[0] if standings and standings.content else None

        if df is None or df.empty:
            return {"season": str(self.year), "DriverStandings": []}

        results = []
        for _, row in df.iterrows():
            standing = DriverStanding(
                position=int(row.get("position", 0)),
                points=float(row.get("points", 0.0)),
                wins=int(row.get("wins", 0)),
                driver=f"{row.get('givenName', '')} {row.get('familyName', '')}".strip(),
                constructor=row.get("constructorNames", "")
            )
            results.append(standing.to_dict())

        return {"season": str(self.year), "DriverStandings": results}

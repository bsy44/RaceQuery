import fastf1
from fastf1.ergast import Ergast
import os


class CircuitService:
    def __init__(self, season: int):
        self.season = season
        self.ergast = Ergast()

        cache_dir = 'backend/data/fastf1_cache'
        os.makedirs(cache_dir, exist_ok=True)
        fastf1.Cache.enable_cache(cache_dir)

    def get_circuits(self) -> list[dict]:
        df = self.ergast.get_circuits(season=self.season)

        result = []
        for _, row in df.iterrows():
            result.append({
                "circuitId": row["circuitId"],
                "name": row.get("circuitName"),
                "locality": row.get("locality"),
                "country": row.get("country"),
            })

        return result

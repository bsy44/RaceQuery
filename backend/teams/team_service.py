import os
import fastf1
from fastf1.ergast import Ergast

class ConstructorStandingService:
    def __init__(self, year: int):
        self.year = year
        self.ergast = Ergast()

        cache_dir = 'backend/data/fastf1_cache'
        os.makedirs(cache_dir, exist_ok=True)
        fastf1.Cache.enable_cache(cache_dir)

    def get_constructor_standings(self) -> list[dict]:
        standings = self.ergast.get_constructor_standings(season=self.year)
        df = standings.content[0]
        if df is None or df.empty:
            return []

        results = []
        first_points = float(df.iloc[0]["points"])
        for _, row in df.iterrows():
            points = float(row["points"])
            diff = first_points - points

            results.append({
                "position": str(row["position"]),
                "points": str(points),
                "wins": str(row["wins"]),
                "constructor": row["constructorName"],
                "points_diff": str(diff)
            })

        return results


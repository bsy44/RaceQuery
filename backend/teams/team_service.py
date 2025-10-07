import os
import fastf1
from fastf1.ergast import Ergast

class ConstructorService:
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

    def get_team(self, team_id: str) -> dict:
        standings = self.ergast.get_constructor_standings(season=self.year)
        df = standings.content[0]
        if df is None or df.empty:
            return {"error": f"Aucun classement constructeur disponible pour {self.year}"}

        team_row = df[df["constructorId"] == team_id]
        if team_row.empty:
            return {"error": f"Constructeur '{team_id}' non trouvé pour {self.year}"}

        row = team_row.iloc[0]
        first_points = float(df.iloc[0]["points"])
        points = float(row["points"])
        diff = first_points - points

        constructor_info = {
            "constructorId": row.get("constructorId"),
            "nationality": row.get("constructorNationality")
        }

        result = {
            "position": str(row["position"]),
            "points": str(points),
            "wins": str(row["wins"]),
            "constructor": row["constructorName"],
            "points_diff": str(diff),
            "Constructor": constructor_info
        }

        return result


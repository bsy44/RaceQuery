from fastf1.ergast import Ergast

class ConstructorStandingService:
    def __init__(self, year: int):
        self.year = year
        self.ergast = Ergast()

    def get_constructor_standings(self) -> list[dict]:
        standings = self.ergast.get_constructor_standings(season=self.year)
        df = standings.content[0]

        results = []
        for _, row in df.iterrows():
            results.append({
                "position": int(row["position"]),
                "points": float(row["points"]),
                "wins": int(row["wins"]),
                "constructor": row["constructorName"]
            })
        return results

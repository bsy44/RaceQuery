from fastf1.ergast import Ergast

class DriverStandingService:
    def __init__(self, year: int):
        self.year = year
        self.ergast = Ergast()

    def get_driver_standings(self) -> list[dict]:
        standings = self.ergast.get_driver_standings(season=self.year)
        df = standings.content[0]

        results = []
        for _, row in df.iterrows():
            results.append({
                "position": int(row["position"]),
                "points": float(row["points"]),
                "wins": int(row["wins"]),
                "driver": f"{row['givenName']} {row['familyName']}",
                "constructor": row["constructorNames"]
            })
        return results

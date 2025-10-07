import os
import fastf1
from fastf1.ergast import Ergast
from backend.drivers.driver import DriverStanding

class DriverService:
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
        first_points = float(df.iloc[0]["points"])

        for _, row in df.iterrows():
            drivers = {
                "driverId": row.get("driverId"),
                "fullName": f"{row.get('givenName')} {row.get('familyName')}",
                "code": row.get("driverCode"),
                "nationality": row.get("driverNationality")
            }

            constructor_names = row.get("constructorNames")
            if isinstance(constructor_names, list):
                last_constructor = constructor_names[-1]
            else:
                last_constructor = constructor_names

            points = float(row.get("points", 0.0))
            diff = first_points - points  # Différence avec le premier

            standing = DriverStanding(
                position=int(row.get("position", 0)),
                points=points,
                wins=int(row.get("wins", 0)),
                driver=drivers,
                constructor=[last_constructor]
            )

            standing_dict = standing.to_dict()
            standing_dict["points_diff"] = round(diff, 1)

            results.append(standing_dict)

        return {"season": str(self.year), "DriverStandings": results}

    def get_driver(self, id_driver: str) -> dict:
        standings = self.ergast.get_driver_standings(season=self.year)
        df = standings.content[0] if standings and standings.content else None

        if df is None or df.empty:
            return {"error": f"Aucun classement disponible pour {self.year}"}

        driver_row = df[df["driverId"] == id_driver]

        if driver_row.empty:
            return {"error": f"Pilote '{id_driver}' non trouvé pour {self.year}"}

        row = driver_row.iloc[0]

        constructor_names = row.get("constructorNames")
        if isinstance(constructor_names, list):
            last_constructor = constructor_names[-1]
        else:
            last_constructor = constructor_names

        driver_detail = {
            "position": int(row.get("position", 0)),
            "points": float(row.get("points", 0.0)),
            "wins": int(row.get("wins", 0)),
            "podium": int(self.get_nb_podium(str(row.get("driverId")))),
            "constructor": str(last_constructor),
            "Drivers": [
                {
                    "driverId": str(row.get("driverId")),
                    "fullName": f"{row.get('givenName')} {row.get('familyName')}",
                    "driverNumber": int(row.get("driverNumber")) if row.get("driverNumber") else None,
                    "code": str(row.get("driverCode")),
                    "dateOfBirth": str(row.get("dateOfBirth")),
                    "nationality": str(row.get("driverNationality"))
                }
            ]
        }

        return driver_detail

    def get_nb_podium(self, id_driver: str) -> int:
        ergast = Ergast()
        races = ergast.get_race_schedule(season=self.year)
        podium_count = 0

        for _, race in races.iterrows():
            results_resp = ergast.get_race_results(season=self.year, round=race["round"])
            df = results_resp.content[0] if results_resp.content else None
            if df is None:
                continue
            driver_row = df[df["driverId"] == id_driver]
            if not driver_row.empty:
                try:
                    pos = int(driver_row.iloc[0]["position"])
                    if 1 <= pos <= 3:
                        podium_count += 1
                except (ValueError, TypeError):
                    continue

        return podium_count

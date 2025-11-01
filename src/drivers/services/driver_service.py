import os
import pandas as pd
import fastf1
from fastf1.ergast import Ergast
from drivers.models.driver import Driver


class DriverService:
    def __init__(self, year: int):
        self.year = year
        self.ergast = Ergast()

        cache_dir = "src/data/fastf1_cache"
        os.makedirs(cache_dir, exist_ok=True)
        fastf1.Cache.enable_cache(cache_dir)

    def _format_driver(self, row) -> Driver:
        driver_number = row.get("driverNumber")
        driver_code = row.get("code") or row.get("driverCode")

        return Driver(
            driverId=str(row.get("driverId")),
            driverNumber=int(driver_number) if pd.notna(driver_number) else None,
            code=str(driver_code) if driver_code else None,
            fullName=f"{row.get('givenName')} {row.get('familyName')}",
            givenName=str(row.get('givenName')),
            familyName=str(row.get('familyName')),
            nationality=str(row.get("driverNationality")),
            birthday=str(row.get("dateOfBirth"))
        )


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
        if isinstance(constructor_names, list) and constructor_names:
            last_constructor = constructor_names[-1]
        else:
            last_constructor = constructor_names or "Inconnu"

        driver = self._format_driver(row)
        driver_detail = {
            "team": str(last_constructor),
            "driver": driver.to_dict()
        }

        return driver_detail

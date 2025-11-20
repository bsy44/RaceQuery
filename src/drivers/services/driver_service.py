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
        constructor_names = row.get("constructorNames")
        constructor_ids = row.get("constructorIds")

        if isinstance(constructor_names, list) and constructor_names:
            last_constructor = constructor_names[-1]
            last_constructor_id = (
                constructor_ids[-1] if isinstance(constructor_ids, list) and constructor_ids else None
            )
        else:
            last_constructor = constructor_names or "Inconnu"
            last_constructor_id = constructor_ids or None

        return Driver(
            driverId=str(row.get("driverId")),
            driverNumber=int(driver_number) if pd.notna(driver_number) else None,
            code=str(driver_code) if driver_code else None,
            fullName=f"{row.get('givenName')} {row.get('familyName')}",
            givenName=str(row.get("givenName")),
            familyName=str(row.get("familyName")),
            nationality=str(row.get("driverNationality")),
            birthday=str(row.get("dateOfBirth")),
            team=str(last_constructor),
            team_id=str(last_constructor_id) if last_constructor_id else None
        )

    def list_drivers(self) -> list[Driver]:
        drivers = self.ergast.get_driver_standings(season=self.year)
        df = drivers.content[0] if drivers and drivers.content else None

        if df is None or df.empty:
            return []

        drivers = []
        for _, row in df.iterrows():
            driver = self._format_driver(row)
            drivers.append(driver)

        return drivers

    def get_driver(self, id_driver: str) -> Driver | dict:
        standings = self.ergast.get_driver_standings(season=self.year)
        df = standings.content[0] if standings and standings.content else None

        if df is None or df.empty:
            return {"error": f"Aucun classement disponible pour {self.year}"}

        driver_row = df[df["driverId"] == id_driver]

        if driver_row.empty:
            return {"error": f"Pilote '{id_driver}' non trouve pour {self.year}"}

        row = driver_row.iloc[0]

        driver = self._format_driver(row)

        return driver

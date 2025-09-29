import os
import pandas as pd
import fastf1
from fastf1.ergast import Ergast


class DriverService:
    def __init__(self):
        self.ergast = Ergast()

        cache_dir = 'data/fastf1_cache'
        os.makedirs(cache_dir, exist_ok=True)
        fastf1.Cache.enable_cache(cache_dir)

    def get_drivers(self, season: int) -> list[dict]:
        df = self.ergast.get_driver_info(season=season)

        return [self._format_driver(row) for _, row in df.iterrows()]

    def get_driver_by_id(self, driver_id: str) -> dict | None:
        df = self.ergast.get_driver_info(driver=driver_id)
        if df.empty:
            return None
        return self._format_driver(df.iloc[0])

    def _format_driver(self, row) -> dict:
        dob = row.get("dateOfBirth")
        if pd.notna(dob):
            dob_str = str(pd.to_datetime(dob).date())
        else:
            dob_str = None

        return {
            "driverId": str(row["driverId"]),
            "driverNumber": int(row["driverNumber"]) if not pd.isna(row.get("driverNumber")) else None,
            "code": row.get("driverCode"),
            "fullName": f"{row['givenName']} {row['familyName']}",
            "givenName": row["givenName"],
            "familyName": row["familyName"],
            "dateOfBirth": dob_str,
            "nationality": row.get("driverNationality"),
        }


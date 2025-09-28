import fastf1
from fastf1.ergast import Ergast
import os


class DriverService:
    def __init__(self, season: int):
        self.season = season
        self.ergast = Ergast()

        cache_dir = 'backend/data/fastf1_cache'
        os.makedirs(cache_dir, exist_ok=True)
        fastf1.Cache.enable_cache(cache_dir)

    def get_drivers(self) -> list[dict]:
        df = self.ergast.get_driver_info(season=self.season)

        result = []
        for _, row in df.iterrows():
            result.append({
                "driverId": row["driverId"],
                "driverNumber": row.get("driverNumber"),
                "code": row.get("driverCode"),
                "fullName": f"{row['givenName']} {row['familyName']}",
                "givenName": row["givenName"],
                "familyName": row["familyName"],
                "dateOfBirth": row.get("dateOfBirth"),
                "nationality": row.get("driverNationality"),
            })

        return result

import fastf1
import os

class DriverService:
    def __init__(self, year: int, grand_prix: str, session_type: str):
        self.year = year
        self.grand_prix = grand_prix
        self.session_type = session_type

        cache_dir = 'backend/data/fastf1_cache'
        os.makedirs(cache_dir, exist_ok=True)
        fastf1.Cache.enable_cache(cache_dir)

    def get_drivers(self) -> list[dict]:
        session = fastf1.get_session(self.year, self.grand_prix, self.session_type)
        session.load()

        drivers_info = []

        for driver_id in session.drivers:
            info = session.get_driver(driver_id)
            drivers_info.append({
                "id": info['DriverNumber'],
                "first_name": info['FirstName'],
                "last_name": info['LastName'],
                "full_name": info['FullName'],
                "country_code": info['CountryCode'],
                "team": info['TeamName']
            })

        return drivers_info

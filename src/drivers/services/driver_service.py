from drivers.models.driver import Driver
from cache_reader import load_json_file


class DriverService:
    def __init__(self, year: int):
        self.year = year

    def _format_driver(self, row: dict) -> Driver:
        def clean_val(val):
            return None if val == "nan" or val is None else val

        driver_number = clean_val(row.get("driverNumber"))
        driver_code = clean_val(row.get("code")) or clean_val(row.get("driverCode"))

        constructor_names = row.get("constructorNames")
        constructor_ids = row.get("constructorIds")

        last_constructor = "Inconnu"
        last_constructor_id = None

        if isinstance(constructor_names, list) and constructor_names:
            last_constructor = constructor_names[-1]
        elif isinstance(constructor_names, str) and constructor_names.startswith("["):
            try:
                last_constructor = constructor_names.strip("[]'\" ").split(",")[-1].strip("'\" ")
            except:
                last_constructor = constructor_names
        elif isinstance(constructor_names, str):
            last_constructor = constructor_names

        if isinstance(constructor_ids, list) and constructor_ids:
            last_constructor_id = constructor_ids[-1]
        elif isinstance(constructor_ids, str) and constructor_ids.startswith("["):
            try:
                last_constructor_id = constructor_ids.strip("[]'\" ").split(",")[-1].strip("'\" ")
            except:
                last_constructor_id = constructor_ids
        elif isinstance(constructor_ids, str):
            last_constructor_id = constructor_ids

        return Driver(
            driverId=str(row.get("driverId")),
            driverNumber=int(float(driver_number)) if driver_number else None,
            code=str(driver_code) if driver_code else None,
            fullName=f"{row.get('givenName')} {row.get('familyName')}",
            familyName=row.get('familyName'),
            givenName=row.get('givenName'),
            nationality=str(row.get("driverNationality")),
            birthday=str(row.get("dateOfBirth")),
            team=str(last_constructor) if last_constructor else None,
            team_id=str(last_constructor_id) if last_constructor_id else None
        )

    def list_drivers(self) -> list[Driver]:
        filename = f"{self.year}_drivers.json"
        data = load_json_file(f'data_cache/static/{self.year}', filename)

        if not data:
            return []

        drivers = []
        for row in data:
            driver = self._format_driver(row)
            drivers.append(driver)

        team_standings = load_json_file(f'data_cache/ergast/{self.year}/team', f"{self.year}_constructor_standings.json")

        team_rank_map = {}
        if team_standings:
            t_list = team_standings.get("standings", []) if isinstance(team_standings, dict) else team_standings

            for rank, team in enumerate(t_list, start=1):
                c_id = team.get('constructorId')
                if c_id:
                    team_rank_map[c_id] = rank

        def sort_key(d):
            team_rank = team_rank_map.get(d.team_id, 999)
            driver_num = d.driverNumber if d.driverNumber is not None else 999
            return (team_rank, driver_num)

        drivers.sort(key=sort_key)

        return drivers

    def get_driver(self, id_driver: str) -> Driver | dict:
        drivers_list = self.list_drivers()
        if not drivers_list:
            return {"error": f"Aucun classement disponible pour {self.year}"}
        found_driver = next((d for d in drivers_list if d.driverId == id_driver), None)
        if found_driver:
            return found_driver
        return {"error": f"Pilote '{id_driver}' non trouve pour {self.year}"}
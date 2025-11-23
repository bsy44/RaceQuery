from drivers.models.driver import Driver
from drivers.models.driver_standing import DriverStanding
from cache_reader import load_json_file


class DriverStandingService:
    def __init__(self, year: int):
        self.year = year

    def _format_driver(self, row: dict) -> Driver:
        def clean_val(val):
            return None if val == "nan" or val is None else val

        driver_number = clean_val(row.get("driverNumber"))
        driver_code = clean_val(row.get("code")) or clean_val(row.get("driverCode"))

        constructor_names = row.get("constructorNames")
        last_constructor = "Inconnu"
        if isinstance(constructor_names, list) and constructor_names:
            last_constructor = constructor_names[-1]
        elif isinstance(constructor_names, str):
            last_constructor = constructor_names.strip("[]'\" ").split(",")[-1].strip("'\" ")

        return Driver(
            driverId=str(row.get("driverId")),
            driverNumber=int(float(driver_number)) if driver_number else None,
            code=str(driver_code) if driver_code else None,
            fullName=f"{row.get('givenName')} {row.get('familyName')}",
            givenName=str(row.get('givenName')),
            familyName=str(row.get('familyName')),
            nationality=str(row.get("driverNationality")),
            birthday=str(row.get("dateOfBirth")),
            team=str(last_constructor)
        )


    def get_driver_standings(self) -> list[DriverStanding]:
        main_filename = f"{self.year}_driver_standings.json"
        main_data = load_json_file('ergast', main_filename)

        if not main_data or "standings" not in main_data:
            return []

        current_round = int(main_data.get("round", 0))
        current_standings = main_data.get("standings", [])

        prev_positions = {}
        if current_round > 1:
            prev_round = current_round - 1
            prev_filename = f"{self.year}_R{prev_round}_driver_standings.json"
            prev_data = load_json_file('ergast', prev_filename)

            if prev_data:
                for row in prev_data:
                    d_id = row.get('driverId')
                    pos = int(float(row.get('position', 0)))
                    if d_id:
                        prev_positions[d_id] = pos

        results = []
        if not current_standings:
            return []

        leader_points = float(current_standings[0].get('points', 0))

        for row in current_standings:
            current_points = float(row.get('points', 0))
            driver_id = row.get('driverId')
            current_pos = int(float(row.get('position', 0)))

            if driver_id in prev_positions:
                evolution = prev_positions[driver_id] - current_pos
            else:
                evolution = 0

            constructor_names = row.get("constructorNames")
            team_name = "Inconnu"
            if isinstance(constructor_names, list) and constructor_names:
                team_name = constructor_names[-1]
            elif isinstance(constructor_names, str):
                team_name = constructor_names.strip("[]'\" ").split(",")[-1].strip("'\" ")

            standing = DriverStanding(
                driver=self._format_driver(row),
                points=current_points,
                points_diff=round(leader_points - current_points, 1),
                position=current_pos,
                team=team_name,
                evolution=evolution
            )

            results.append(standing)

        return results
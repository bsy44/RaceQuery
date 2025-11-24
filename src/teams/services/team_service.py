from teams.models.team import Team
from drivers.models.driver import Driver
from cache_reader import load_json_file


class TeamService:
    def __init__(self, year: int):
        self.year = year


    def _clean_val(self, val):
        return None if str(val).lower() == "nan" or val is None else val


    def _parse_list_field(self, field_value):
        if isinstance(field_value, list) and field_value:
            return field_value[-1]
        elif isinstance(field_value, str):
            clean = field_value.strip("[]'\" ")
            if "," in clean:
                return clean.split(",")[-1].strip("'\" ")
            return clean
        return None


    def _format_driver(self, row: dict) -> Driver:
        driver_number = self._clean_val(row.get("driverNumber"))
        driver_code = self._clean_val(row.get("code")) or self._clean_val(row.get("driverCode"))

        team_name = self._parse_list_field(row.get("constructorNames")) or "Inconnu"
        team_id = self._parse_list_field(row.get("constructorIds"))

        return Driver(
            driverId=str(row.get("driverId")),
            fullName=f"{row.get('givenName')} {row.get('familyName')}",
            givenName=str(row.get("givenName")),
            familyName=str(row.get("familyName")),
            driverNumber=int(float(driver_number)) if driver_number else None,
            code=str(driver_code) if driver_code else None,
            nationality=str(row.get("driverNationality")),
            birthday=str(row.get("dateOfBirth")),
            team=str(team_name),
            team_id=str(team_id) if team_id else None
        )


    def list_teams(self) -> list[Team]:
        teams_data = load_json_file('data_cache/static', f"{self.year}_constructors.json")

        drivers_data_raw = load_json_file(f'data_cache/static', f"{self.year}_drivers.json")

        if not teams_data:
            return []

        drivers_by_team_id = {}

        if drivers_data_raw:
            if isinstance(drivers_data_raw, dict):
                standings_list = drivers_data_raw.get("standings", [])
            else:
                standings_list = drivers_data_raw

            for d_row in standings_list:
                driver = self._format_driver(d_row)

                if driver.team_id:
                    # On utilise l'ID (ex: 'mclaren') comme clé
                    if driver.team_id not in drivers_by_team_id:
                        drivers_by_team_id[driver.team_id] = []
                    drivers_by_team_id[driver.team_id].append(driver)

        teams = []
        for team_row in teams_data:
            c_id = team_row.get("constructorId")

            team_drivers = drivers_by_team_id.get(c_id, [])

            team = Team(
                constructorId=c_id,
                constructorName=team_row.get("constructorName") or team_row.get("name"),
                nationality=team_row.get("constructorNationality") or team_row.get("nationality"),
                drivers=team_drivers
            )
            teams.append(team)

        return teams


    def get_team(self, team_id: str) -> Team | dict:
        all_teams = self.list_teams()
        found_team = next((t for t in all_teams if t.constructorId == team_id), None)

        if found_team:
            return found_team

        return {"error": f"Écurie '{team_id}' non trouvée pour {self.year}"}
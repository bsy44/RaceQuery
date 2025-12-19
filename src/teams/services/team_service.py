from teams.models.team import Team
from drivers.models.driver import Driver
from utils.cache_reader import load_json_file


class TeamService:
    def __init__(self, year: int):
        self.year = year


    def list_teams(self) -> list[Team]:
        teams_data = load_json_file('data_cache/static', f"{self.year}_constructors.json")

        if not teams_data:
            return []

        teams = []
        for team_row in teams_data:

            raw_drivers = team_row.get("drivers", [])
            driver_objects = []

            for d in raw_drivers:
                new_driver = Driver(
                    driverId=d.get("driverId"),
                    birthday=str(d.get("dateOfBirth")),
                    code=d.get("code"),
                    driverNumber=d.get("driverNumber"),
                    givenName=d.get("givenName"),
                    familyName=d.get("familyName"),
                    nationality=d.get("nationality"),
                    team=team_row.get("constructorName"),
                    team_id=team_row.get("constructorId"),
                    fullName=f"{d.get('givenName')} {d.get('familyName')}",
                )
                driver_objects.append(new_driver)

            team = Team(
                constructorId=team_row.get("constructorId"),
                constructorName=team_row.get("constructorName") or team_row.get("name"),
                nationality=team_row.get("constructorNationality") or team_row.get("nationality"),
                drivers=driver_objects,
            )
            teams.append(team)

        return teams


    def get_team(self, team_id: str) -> Team | dict:
        all_teams = self.list_teams()
        found_team = next((t for t in all_teams if t.constructorId == team_id), None)

        if found_team:
            return found_team

        return {"error": f"Écurie '{team_id}' non trouvée pour {self.year}"}
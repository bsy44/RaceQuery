from drivers.models.driver import Driver


class DriverStanding:
    def __init__(self, position: int, points: float, points_diff: float, driver: Driver, team: str, team_id: str, evolution: int):
        self.driver = driver
        self.position = position
        self.points = points
        self.points_diff = points_diff
        self.fullName = driver.fullName
        self.family_name = driver.familyName
        self.driver_id = driver.driverId
        self.driver_nationality = driver.nationality
        self.team = team
        self.team_id = team_id
        self.evolution = evolution


    def to_dict(self):
        return {
            "driver_id": self.driver_id,
            "fullName": self.fullName,
            "family_name": self.family_name,
            "nationality": self.driver_nationality,
            "position": str(self.position),
            "points": str(self.points),
            "points_diff": self.points_diff,
            "team": self.team,
            "constructorId": self.team_id,
            "evolution": self.evolution
        }


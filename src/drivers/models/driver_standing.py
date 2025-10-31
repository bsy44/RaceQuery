from drivers.models.driver import Driver


class DriverStanding:
    def __init__(self, position: int, points: float, points_diff: float, driver: Driver, team: str, evolution: int):
        self.driver = driver
        self.position = position
        self.points = points
        self.points_diff = points_diff
        self.fullName = driver.fullName
        self.driver_id = driver.driverId
        self.driver_nationality = driver.nationality
        self.team = team
        self.evolution = evolution

    def to_dict(self):
        return {
            "driver_id": self.driver_id,
            "fullName": self.fullName,
            "nationality": self.driver_nationality,
            "position": str(self.position),
            "points": str(self.points),
            "points_diff": self.points_diff,
            "team": self.team,
            "evolution": self.evolution
        }


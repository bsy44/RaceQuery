class Driver:
    def __init__(self, driverId: str, driverNumber: int = None, code: str = None,
                 fullName: str = None, givenName: str = None, familyName: str = None,
                 nationality: str = None, evolution: str = None):
        self.driverId = driverId
        self.driverNumber = driverNumber
        self.code = code
        self.fullName = fullName
        self.givenName = givenName
        self.familyName = familyName
        self.nationality = nationality

    def to_dict(self):
        return {
            "driverId": self.driverId,
            "driverNumber": self.driverNumber,
            "code": self.code,
            "fullName": self.fullName,
            "givenName": self.givenName,
            "familyName": self.familyName,
            "nationality": self.nationality
        }

class DriverStanding:
    def __init__(self, position: int, points: float, driver: Driver, team: str, evolution: str):
        self.position = position
        self.points = points
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
            "team": self.team,
            "evolution": self.evolution
        }
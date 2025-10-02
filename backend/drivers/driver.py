class Driver:
    def __init__(self, driverId: str, driverNumber: int = None, code: str = None,
                 fullName: str = None, givenName: str = None, familyName: str = None,
                 nationality: str = None):
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
    def __init__(self, position: int, points: float, wins: int, driver: str, constructor: str):
        self.position = position
        self.points = points
        self.wins = wins
        self.driver = driver
        self.constructor = constructor

    def to_dict(self):
        return {
            "position": str(self.position),
            "points": str(self.points),
            "wins": str(self.wins),
            "driver": self.driver,
            "constructor": self.constructor
        }
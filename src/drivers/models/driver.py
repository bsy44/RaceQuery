class Driver:
    def __init__(self, driverId: str, driverNumber: int, code: str, fullName: str, nationality: str,
                 givenName: str = None, familyName: str = None, birthday: str = None, team: str = None):

        self.driverId = driverId
        self.driverNumber = driverNumber
        self.code = code
        self.fullName = fullName
        self.givenName = givenName
        self.familyName = familyName
        self.nationality = nationality
        self.birthday = birthday
        self.team = team

    def to_dict(self):
        return {
            "driverId": self.driverId,
            "driverNumber": self.driverNumber,
            "code": self.code,
            "fullName": self.fullName,
            "givenName": self.givenName,
            "familyName": self.familyName,
            "nationality": self.nationality,
            "date_of_birth": self.birthday,
            "team": self.team
        }

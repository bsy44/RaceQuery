from drivers.models.driver import Driver


class Team:
    def __init__(self, constructorId: str, constructorName: str, nationality: str = None, drivers: list[Driver] = None):
        self.constructorId = constructorId
        self.constructorName = constructorName
        self.nationality = nationality
        self.drivers = drivers or []

    def to_dict(self):
        return {
            "constructorId": self.constructorId,
            "constructorName": self.constructorName,
            "nationality": self.nationality,
            "drivers": [driver.to_dict() for driver in self.drivers]
        }

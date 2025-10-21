class ConstructorStanding:
    def __init__(self, position: int, points: float, wins: int, constructor: str):
        self.position = position
        self.points = points
        self.wins = wins
        self.constructor = constructor

    def to_dict(self) -> dict:
        return {
            "position": self.position,
            "points": self.points,
            "wins": self.wins,
            "constructor": self.constructor
        }

class Constructor:
    def __init__(self, constructorId: str, constructorName: str, nationality: str = None):
        self.constructorId = constructorId
        self.constructorName = constructorName
        self.nationality = nationality

    def to_dict(self):
        return {
            "constructorId": self.constructorId,
            "constructorName": self.constructorName,
            "nationality": self.nationality if self.nationality else None
        }
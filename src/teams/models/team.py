class Team:
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
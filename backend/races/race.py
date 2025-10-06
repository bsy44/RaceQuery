from typing import Optional
from backend.races.circuits.circuit import Circuit

class Race:
    def __init__(self, season: int, round: int, raceName: str, circuit: Circuit,
                 date: Optional[str] = None, time: Optional[str] = None,
                 firstPractice: Optional[dict] = None,
                 secondPractice: Optional[dict] = None,
                 thirdPractice: Optional[dict] = None,
                 qualifying: Optional[dict] = None,
                 sprint: Optional[dict] = None):
        self.season = season
        self.round = round
        self.raceName = raceName
        self.circuit = circuit
        self.date = date
        self.time = time
        self.firstPractice = firstPractice
        self.secondPractice = secondPractice
        self.thirdPractice = thirdPractice
        self.qualifying = qualifying
        self.sprint = sprint

    def to_dict(self):
        return {
            "season": str(self.season),
            "round": str(self.round),
            "raceName": self.raceName,
            "Circuit": self.circuit.to_dict(),
            "date": self.date,
            "time": self.time,
            "FirstPractice": self.firstPractice,
            "SecondPractice": self.secondPractice,
            "ThirdPractice": self.thirdPractice,
            "Qualifying": self.qualifying,
            "Sprint": self.sprint
        }

    def to_dict_for_results(self):
        return {
            "season": str(self.season),
            "round": str(self.round),
            "raceName": self.raceName,
            "Circuit": {
                "circuitId": self.circuit.circuitId,
                "circuitName": self.circuit.circuitName
            }
        }
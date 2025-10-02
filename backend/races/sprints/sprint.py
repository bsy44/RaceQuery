from typing import List, Optional
from backend.drivers.driver import Driver
from backend.teams.team import Constructor

class FastestLap:
    def __init__(self, rank: Optional[int], time: Optional[str]):
        self.rank = rank
        self.time = time

    def to_dict(self):
        return {
            "rank": self.rank,
            "time": self.time
        }


class SprintResult:
    def __init__(self, position: str, points: str, grid: str, laps: str, status: str,
                 driver: Driver, constructor: Constructor, total_time: Optional[str],
                 total_millis: Optional[str], fastest_lap: Optional[FastestLap]):
        self.position = position
        self.points = points
        self.grid = grid
        self.laps = laps
        self.status = status
        self.driver = driver
        self.constructor = constructor
        self.total_time = total_time
        self.total_millis = total_millis
        self.fastest_lap = fastest_lap

    def to_dict(self):
        return {
            "position": self.position,
            "points": self.points,
            "grid": self.grid,
            "laps": self.laps,
            "status": self.status,
            "Driver": self.driver.to_dict(),
            "Constructor": self.constructor.to_dict(),
            "Time": {
                "time": self.total_time,
                "millis": self.total_millis
            },
            "FastestLap": self.fastest_lap.to_dict() if self.fastest_lap else None
        }


class Sprint:
    def __init__(self, season: int, round: int, race_name: str, circuit: dict,
                 date: str, time: str, results: Optional[List[SprintResult]] = None):
        self.season = season
        self.round = round
        self.race_name = race_name
        self.circuit = circuit
        self.date = date
        self.time = time
        self.results = results or []

    def to_dict(self):
        return {
            "season": self.season,
            "round": self.round,
            "raceName": self.race_name,
            "Circuit": self.circuit,
            "date": self.date,
            "time": self.time,
            "SprintResults": [r.to_dict() for r in self.results]
        }

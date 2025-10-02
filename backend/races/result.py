from typing import Optional, List
from backend.races.race import Race
from backend.drivers.driver import Driver
from backend.teams.team import Constructor

class FastestLap:
    def __init__(self, rank: Optional[int], time: Optional[str]):
        self.rank = rank
        self.time = time

    def to_dict(self):
        return {
            "rank": str(self.rank) if self.rank is not None else None,
            "Time": {"time": self.time}
        }

class DriverResult:
    def __init__(self, driver: Driver, constructor: Constructor, position: str,
                 points: str, grid: str, laps: str, status: str,
                 total_time: Optional[str], total_millis: Optional[str],
                 fastest_lap: Optional[FastestLap]):
        self.driver = driver
        self.constructor = constructor
        self.position = position
        self.points = points
        self.grid = grid
        self.laps = laps
        self.status = status
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
                "millis": self.total_millis,
                "time": self.total_time
            },
            "FastestLap": self.fastest_lap.to_dict() if self.fastest_lap else None
        }

class Result:
    def __init__(self, race: Race, results: List[DriverResult]):
        self.race = race
        self.results = results

    def to_dict(self):
        return {
            "race": self.race.to_dict(),
            "Results": [r.to_dict() for r in self.results]
        }

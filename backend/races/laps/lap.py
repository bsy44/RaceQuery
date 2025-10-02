class Timing:
    def __init__(self, driverId: str, position: str):
        self.driverId = driverId
        self.position = position

    def to_dict(self):
        return {
            "driverId": self.driverId,
            "position": self.position
        }

class Lap:
    def __init__(self, lap_number: int, timings: list[Timing]):
        self.lap_number = lap_number
        self.timings = timings

    def to_dict(self):
        return {
            "lap_number": self.lap_number,
            "timings": [t.to_dict() for t in self.timings]
        }

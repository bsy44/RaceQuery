class QualifyingResult:
    def __init__(self, position, driver_id, number, code, full_name, constructor, lap_time, session):
        self.position = position
        self.driver_id = driver_id
        self.number = number
        self.code = code
        self.full_name = full_name
        self.constructor = constructor
        self.lap_time = lap_time
        self.session = session

    def to_dict(self):
        return {
            "position": self.position,
            "driverId": self.driver_id,
            "number": self.number,
            "code": self.code,
            "fullName": self.full_name,
            "constructor": self.constructor,
            self.session: self.lap_time
        }


class Qualifying:
    def __init__(self, season, round, race_name, results):
        self.season = season
        self.round = round
        self.race_name = race_name
        self.results = results

    def to_dict(self):
        return {
            "season": str(self.season),
            "round": str(self.round),
            "raceName": self.race_name,
            "QualifyingSplit": [r.to_dict() for r in self.results]
        }


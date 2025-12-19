from drivers.models.driver import Driver


class DriverStats:
    def __init__(self, driver: Driver, position: str, points: str, win: str, podium: int, pole: int, top10: int,
                 dnf: int, sprint_win: int, sprint_podium: int, sprint_pole: int, avg_race_finish: float,
                 avg_qualifying_finish: float, best_result: int, q3_appearance: int, total_quali: int, total_races: int):

        self.driver = driver
        self.win = win
        self.points = points
        self.position = position
        self.podium = podium
        self.pole = pole
        self.top10 = top10
        self.dnf = dnf
        self.sprint_win = sprint_win
        self.sprint_podium = sprint_podium
        self.sprint_pole = sprint_pole
        self.avg_race_finish = avg_race_finish
        self.avg_qualifying_finish = avg_qualifying_finish
        self.best_result = best_result
        self.q3_appearance = q3_appearance
        self.total_quali = total_quali
        self.total_races = total_races

    def to_dict(self):
        return {
            "Driver": self.driver.to_dict(),
            "position": str(self.position),
            "win": str(self.win),
            "podium": int(self.podium),
            "pole": int(self.pole),
            "top10": int(self.top10),
            "dnf": int(self.dnf),
            "sprint_win": int(self.sprint_win),
            "sprint_podium": int(self.sprint_podium),
            "sprint_pole": int(self.sprint_pole),
            "points": str(self.points),
            "avg_race_finish": float(self.avg_race_finish),
            "avg_qualifying_finish": float(self.avg_qualifying_finish),
            "best_result": int(self.best_result),
            "q3_appearance": int(self.q3_appearance),
            "total_quali": int(self.total_quali),
            "total_races": int(self.total_races)
        }


from teams.models.team import Team


class TeamStats:
    def __init__(self, team: Team, position: int, points: str, win: str, podium: int, pole: int, top10: int,
                 dnf: int, sprint_win: int, sprint_podium: int, sprint_pole: int, avg_race_finish: float,
                 avg_qualifying_finish: float):

        self.team = team
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

    def to_dict(self):
        return {
            "Team": self.team.to_dict(),
            "position": int(self.position),
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
        }


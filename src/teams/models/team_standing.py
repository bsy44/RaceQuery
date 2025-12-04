from teams.models.team import Team


class TeamStanding:
    def __init__(self, position: int, points: float, wins: str, team: Team, evolution: float, points_diff: float):
        self.position = position
        self.points = points
        self.wins = wins
        self.team = team
        self.evolution = evolution
        self.points_diff = points_diff


    def to_dict(self) -> dict:
        return {
            "position": self.position,
            "points": self.points,
            "wins": self.wins,
            "Team": self.team,
            "evolution": self.evolution,
            "points_diff": self.points_diff
        }
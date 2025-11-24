from teams.models.team import Team


class TeamStanding:
    def __init__(self, position: int, points: str, wins: str, team: Team, evolution: float):
        self.position = position
        self.points = points
        self.wins = wins
        self.team_name = team.constructorName
        self.evolution = evolution

    def to_dict(self) -> dict:
        return {
            "position": self.position,
            "points": self.points,
            "wins": self.wins,
            "Team": self.team_name,
            "evolution": self.evolution
        }
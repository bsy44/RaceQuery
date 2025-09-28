import fastf1
from fastf1.ergast import Ergast
import os

class RaceService:
    def __init__(self, season: int):
        self.season = season
        self.ergast = Ergast()

        cache_dir = 'backend/data/fastf1_cache'
        os.makedirs(cache_dir, exist_ok=True)
        fastf1.Cache.enable_cache(cache_dir)

    def _format_date(self, value):
        """Convertit date/NaT en string"""
        if value is None or str(value) == "NaT":
            return None
        return str(value)

    def _format_time(self, value):
        """Convertit time/NaT en string au format HH:MM:SSZ"""
        if value is None or str(value) == "NaT":
            return None
        return str(value) + "Z"

    def get_races(self)-> list[dict]:
        df = self.ergast.get_race_schedule(season=self.season)

        races = []
        for _, row in df.iterrows():
            races.append({
                "season": str(row.get("season")),
                "round": str(row.get("round")),
                "raceName": row.get("raceName"),
                "Circuit": {
                    "circuitId": row.get("circuitId"),
                    "url": row.get("circuitUrl"),
                    "circuitName": row.get("circuitName"),
                    "Location": {
                        "locality": row.get("locality"),
                        "country": row.get("country")
                    }
                },
                "date": self._format_date(row.get("raceDate")),
                "time": self._format_time(row.get("raceTime")),
                "FirstPractice": {
                    "date": self._format_date(row.get("fp1Date")),
                    "time": self._format_time(row.get("fp1Time"))
                },
                "SecondPractice": {
                    "date": self._format_date(row.get("fp2Date")),
                    "time": self._format_time(row.get("fp2Time"))
                },
                "ThirdPractice": {
                    "date": self._format_date(row.get("fp3Date")),
                    "time": self._format_time(row.get("fp3Time"))
                },
                "Qualifying": {
                    "date": self._format_date(row.get("qualifyingDate")),
                    "time": self._format_time(row.get("qualifyingTime"))
                },
                "Sprint": {
                    "date": self._format_date(row.get("sprintDate")),
                    "time": self._format_time(row.get("sprintTime"))
                }
            })

        return races

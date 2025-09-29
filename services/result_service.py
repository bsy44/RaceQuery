import fastf1
from fastf1.ergast import Ergast
import os

class ResultService:
    def __init__(self, season: int, round: int = None):
        self.season = season
        self.round = round
        self.ergast = Ergast()

        cache_dir = 'data/fastf1_cache'
        os.makedirs(cache_dir, exist_ok=True)
        fastf1.Cache.enable_cache(cache_dir)

    def _format_date(self, value):
        if value is None or str(value) == "NaT":
            return None
        return str(value)

    def _format_time(self, value):
        if value is None or str(value) == "NaT":
            return None
        return str(value) + "Z"

    def _format_timedelta(self, td):
        if td is None:
            return None
        try:
            total_seconds = int(td.total_seconds())
            minutes, seconds = divmod(total_seconds, 60)
            millis = int(td.microseconds / 1000) if hasattr(td, "microseconds") else 0
            return f"{minutes}:{seconds:02d}.{millis:03d}"
        except:
            return str(td)

    def get_results(self) -> dict:
        schedule_df = self.ergast.get_race_schedule(season=self.season, round=self.round)

        if self.round is not None:
            schedule_df = schedule_df[schedule_df['round'] == self.round]

        races = []

        for _, race_row in schedule_df.iterrows():
            round_num = race_row['round']

            results_resp = self.ergast.get_race_results(season=self.season, round=round_num)
            results_df = results_resp.content[0] if hasattr(results_resp, "content") and len(results_resp.content) > 0 else None

            race_info = {
                "season": str(race_row.get("season")),
                "round": str(round_num),
                "raceName": race_row.get("raceName"),
                "Circuit": {
                    "circuitId": race_row.get("circuitId"),
                    "circuitName": race_row.get("circuitName"),
                    "Location": {
                        "locality": race_row.get("locality"),
                        "country": race_row.get("country")
                    }
                },
                "date": self._format_date(race_row.get("raceDate")),
                "time": self._format_time(race_row.get("raceTime")),
                "Results": []
            }

            if results_df is not None:
                for _, r in results_df.iterrows():
                    race_info["Results"].append({
                        "position": str(r.get("position")),
                        "points": str(r.get("points")),
                        "grid": str(r.get("grid")),
                        "laps": str(r.get("laps")),
                        "status": r.get("status"),
                        "Driver": {
                            "driverId": r.get("driverId"),
                            "number": str(r.get("driverNumber")),
                            "code": r.get("driverCode"),
                            "givenName": r.get("givenName"),
                            "familyName": r.get("familyName"),
                            "nationality": r.get("driverNationality")
                        },
                        "Constructor": {
                            "constructorId": r.get("constructorId"),
                            "name": r.get("constructorName"),
                        },
                        "Time": {
                            "millis": str(r.get("totalRaceTimeMillis")) if r.get("totalRaceTimeMillis") else None,
                            "time": self._format_timedelta(r.get("totalRaceTime"))
                        },
                        "FastestLap": {
                            "rank": str(r.get("fastestLapRank")) if r.get("fastestLapRank") else None,
                            "Time": {
                                "time": self._format_timedelta(r.get("fastestLapTime"))
                            }
                        }
                    })

            races.append(race_info)

        return {
            "season": str(self.season),
            "Races": races
        }

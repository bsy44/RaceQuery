import fastf1
from fastf1.ergast import Ergast
import os

class LapService:
    def __init__(self, season: int, round: int):
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

    def get_lap(self, lap: int = None) -> dict:
        schedule_df = self.ergast.get_race_schedule(season=self.season, round=self.round)

        if self.round is not None:
            schedule_df = schedule_df[schedule_df['round'] == self.round]

        races = []

        for _, race_row in schedule_df.iterrows():
            round_num = race_row['round']

            lap_resp = self.ergast.get_lap_times(
                season=self.season,
                round=round_num,
                lap_number=lap
            )
            lap_df = lap_resp.content[0] if (hasattr(lap_resp, "content") and len(lap_resp.content) > 0) else None

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
                "Laps": []
            }

            if lap_df is not None:

                for lap_num, group in lap_df.groupby("number"):
                    lap_info = {
                        "lap": str(lap_num),
                        "Timings": []
                    }

                    for _, row in group.iterrows():
                        lap_info["Timings"].append({
                            "driverId": row.get("driverId"),
                            "position": str(row.get("position")),
                        })

                    race_info["Laps"].append(lap_info)

            races.append(race_info)

        return {
            "season": str(self.season),
            "Races": races
        }

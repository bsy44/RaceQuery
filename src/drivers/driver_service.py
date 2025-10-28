import os
from datetime import datetime
from functools import lru_cache

import pandas as pd
import fastf1
from fastf1.ergast import Ergast
from drivers.driver import DriverStanding, Driver


class DriverService:
    def __init__(self, year: int):
        self.year = year
        self.ergast = Ergast()

        cache_dir = "src/data/fastf1_cache"
        os.makedirs(cache_dir, exist_ok=True)
        fastf1.Cache.enable_cache(cache_dir)

    @staticmethod
    @lru_cache(maxsize=50)
    def _load_fastf1_session_cached(season, round_, session_id):
        session = fastf1.get_session(season, round_, session_id)
        sid = session_id.upper()
        if sid.startswith("FP") or "PRACTICE" in session.name.upper():
            session.load(laps=True, telemetry=False, weather=False)
        elif sid in ["Q", "QUALIFYING"]:
            session.load(laps=False, telemetry=False, weather=False)
        elif sid in ["SPRINT", "SS", "SR"]:
            session.load(laps=True, telemetry=False, weather=False)
        else:
            session.load(laps=True, telemetry=False, weather=False)
        return session

    def _format_driver(self, row) -> Driver:
        return Driver(
            driverId=row.get("driverId"),
            driverNumber=row.get("driverNumber"),
            code=row.get("code"),
            fullName=f"{row.get('givenName')} {row.get('familyName')}",
            givenName=row.get('givenName'),
            familyName=row.get('familyName'),
            nationality=row.get("driverNationality")
        )

    def get_driver_standings(self) -> list[dict]:
        standings = self.ergast.get_driver_standings(season=self.year)
        df = standings.content[0] if standings and standings.content else None
        if df is None or df.empty:
            return []

        schedule = fastf1.get_event_schedule(self.year, include_testing=False).copy()
        schedule['EventDate'] = pd.to_datetime(schedule['EventDate'])

        past_events = schedule[schedule['EventDate'] <= datetime.now()]
        last_completed_round = past_events['RoundNumber'].max() if not past_events.empty else None

        prev_positions = {}
        if last_completed_round and last_completed_round > 1:
            prev_resp = self.ergast.get_driver_standings(season=self.year, round=last_completed_round - 1)
            prev_df = prev_resp.content[0] if prev_resp.content else pd.DataFrame()
            if not prev_df.empty:
                prev_positions = {row['driverId']: int(row['position']) for _, row in prev_df.iterrows()}

        results = []
        first_points = float(df.iloc[0]["points"])

        for _, row in df.iterrows():
            driver_id = row['driverId']
            current_pos = int(row['position'])
            prev_pos = prev_positions.get(driver_id, current_pos)
            evolution = prev_pos - current_pos

            constructor_names = row.get("constructorNames")
            last_constructor = constructor_names[-1] if isinstance(constructor_names, list) else constructor_names

            standing_dict = {
                "driver_id": driver_id,
                "fullName": f"{row.get('givenName')} {row.get('familyName')}",
                "nationality": row.get('driverNationality'),
                "points": float(row['points']),
                "points_diff": round(float(df.iloc[0]['points']) - float(row['points']), 1),
                "position": current_pos,
                "team": last_constructor,
                "evolution": evolution
            }
            results.append(standing_dict)

        return results


    def get_driver(self, id_driver: str) -> dict:
        standings = self.ergast.get_driver_standings(season=self.year)
        df = standings.content[0] if standings and standings.content else None

        if df is None or df.empty:
            return {"error": f"Aucun classement disponible pour {self.year}"}

        driver_row = df[df["driverId"] == id_driver]

        if driver_row.empty:
            return {"error": f"Pilote '{id_driver}' non trouvé pour {self.year}"}

        row = driver_row.iloc[0]

        constructor_names = row.get("constructorName")
        if isinstance(constructor_names, list) and constructor_names:
            last_constructor = constructor_names[-1]
        else:
            last_constructor = constructor_names or "Inconnu"

        driver_detail = {
            "position": int(row.get("position", 0)),
            "points": float(row.get("points", 0.0)),
            "wins": int(row.get("wins", 0)),
            "podium": int(self.get_nb_podium(str(row.get("driverId")))),
            "team": str(last_constructor),
            "Drivers": [
                {
                    "driverId": str(row.get("driverId")),
                    "fullName": f"{row.get('givenName')} {row.get('familyName')}",
                    "driverNumber": int(row.get("driverNumber")) if row.get("driverNumber") else None,
                    "code": str(row.get("driverCode")),
                    "dateOfBirth": str(row.get("dateOfBirth")),
                    "nationality": str(row.get("driverNationality"))
                }
            ]
        }

        return driver_detail

    def get_nb_podium(self, id_driver: str) -> int:
        ergast = Ergast()
        races = ergast.get_race_schedule(season=self.year)
        podium_count = 0

        for _, race in races.iterrows():
            results_resp = ergast.get_race_results(season=self.year, round=race["round"])
            df = results_resp.content[0] if results_resp.content else None
            if df is None:
                continue
            driver_row = df[df["driverId"] == id_driver]
            if not driver_row.empty:
                try:
                    pos = int(driver_row.iloc[0]["position"])
                    if 1 <= pos <= 3:
                        podium_count += 1
                except (ValueError, TypeError):
                    continue

        return podium_count

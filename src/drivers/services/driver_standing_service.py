import os
from datetime import datetime
import pandas as pd
import fastf1
from fastf1.ergast import Ergast
from drivers.models.driver import Driver
from drivers.models.driver_standing import DriverStanding


class DriverStandingService:
    def __init__(self, year: int):
        self.year = year
        self.ergast = Ergast()

        cache_dir = "src/data/fastf1_cache"
        os.makedirs(cache_dir, exist_ok=True)
        fastf1.Cache.enable_cache(cache_dir)


    def _format_driver(self, row) -> Driver:
        driver_number = row.get("driverNumber")
        driver_code = row.get("code") or row.get("driverCode")

        return Driver(
            driverId=str(row.get("driverId")),
            driverNumber=int(driver_number) if pd.notna(driver_number) else None,
            code=str(driver_code) if driver_code else None,
            fullName=f"{row.get('givenName')} {row.get('familyName')}",
            givenName=str(row.get('givenName')),
            familyName=str(row.get('familyName')),
            nationality=str(row.get("driverNationality")),
            birthday=str(row.get("dateOfBirth"))
        )

    def get_driver_standings(self) -> list[DriverStanding]:
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

        for _, row in df.iterrows():
            driver_id = row['driverId']
            current_pos = int(row['position'])
            prev_pos = prev_positions.get(driver_id, current_pos)
            evolution = prev_pos - current_pos

            constructor_names = row.get("constructorNames")
            last_constructor = constructor_names[-1] if isinstance(constructor_names, list) else constructor_names

            standing = DriverStanding(
                driver=self._format_driver(row),
                points=float(row['points']),
                points_diff=round(float(df.iloc[0]['points']) - float(row['points']), 1),
                position=current_pos,
                team=last_constructor,
                evolution=evolution
            )

            results.append(standing)

        return results
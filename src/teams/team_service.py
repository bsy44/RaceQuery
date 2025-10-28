import os
from datetime import datetime

import pandas as pd
import fastf1
from fastf1.ergast import Ergast
from teams.team import Constructor

class ConstructorService:
    def __init__(self, year: int):
        self.year = year
        self.ergast = Ergast()

        cache_dir = 'src/data/fastf1_cache'
        os.makedirs(cache_dir, exist_ok=True)
        fastf1.Cache.enable_cache(cache_dir)

    def _format_constructor(self, row) -> Constructor:
        return Constructor(
            constructorId=row.get("constructorId"),
            constructorName=row.get("constructorName"),
            nationality=row.get("constructorNationality")
        )

    def get_team_standings(self) -> list[dict]:
        standings = self.ergast.get_constructor_standings(season=self.year)
        df = standings.content[0]
        if df is None or df.empty:
            return []

        schedule = fastf1.get_event_schedule(self.year, include_testing=False).copy()
        schedule['EventDate'] = pd.to_datetime(schedule['EventDate'])

        past_events = schedule[schedule['EventDate'] <= datetime.now()]
        last_completed_round = past_events['RoundNumber'].max() if not past_events.empty else None

        prev_positions = {}
        if last_completed_round and last_completed_round > 1:
            prev_resp = self.ergast.get_constructor_standings(season=self.year, round=last_completed_round - 1)
            prev_df = prev_resp.content[0] if prev_resp.content else pd.DataFrame()

            if not prev_df.empty:
                prev_positions = {
                    row['constructorId']: int(row['position'])
                    for _, row in prev_df.iterrows()
                }

        results = []
        first_points = float(df.iloc[0]["points"])

        for _, row in df.iterrows():
            team_id = row['constructorId']
            current_pos = int(row['position'])
            prev_pos = prev_positions.get(team_id, current_pos)
            evolution = prev_pos - current_pos

            results.append({
                "position": str(row["position"]),
                "points": str(float(row["points"])),
                "Team": self._format_constructor(row).to_dict(),
                "points_diff": str(first_points - float(row["points"])),
                "evolution": evolution
            })

        return results

    def get_team(self, team_id: str) -> dict:
        standings = self.ergast.get_constructor_standings(season=self.year)
        df = standings.content[0]
        if df is None or df.empty:
            return {"error": f"Aucun classement constructeur disponible pour {self.year}"}

        team_row = df[df["constructorId"] == team_id]
        if team_row.empty:
            return {"error": f"Constructeur '{team_id}' non trouvé pour {self.year}"}

        row = team_row.iloc[0]
        first_points = float(df.iloc[0]["points"])
        points = float(row["points"])
        diff = first_points - points

        result = {
            "position": str(row["position"]),
            "points": str(points),
            "wins": str(row["wins"]),
            "podiums": int(self.get_nb_podium(str(row.get("constructorId")))),
            "points_diff": str(diff),
            "Team": self._format_constructor(row).to_dict()
        }

        return result

    def get_nb_podium(self, team_id: str) -> int:
        podium_count = 0
        races = self.ergast.get_race_schedule(season=self.year)

        for _, race in races.iterrows():
            results_resp = self.ergast.get_race_results(season=self.year, round=race["round"])
            df = results_resp.content[0] if results_resp.content else None
            if df is None:
                continue

            team_results = df[df["constructorId"] == team_id]
            for _, row in team_results.iterrows():
                try:
                    pos = int(row["position"])
                    if 1 <= pos <= 3:
                        podium_count += 1
                except (ValueError, TypeError):
                    continue

        return podium_count

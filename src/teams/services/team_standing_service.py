import os
from datetime import datetime
import pandas as pd
import fastf1
from fastf1.ergast import Ergast
from teams.models.team import Team
from teams.models.team_standing import TeamStanding


class TeamStandingService:
    def __init__(self, year: int):
        self.year = year
        self.ergast = Ergast()

        cache_dir = 'src/data/fastf1_cache'
        os.makedirs(cache_dir, exist_ok=True)
        fastf1.Cache.enable_cache(cache_dir)

    def _format_constructor(self, row) -> Team:
        return Team(
            constructorId=row.get("constructorId"),
            constructorName=row.get("constructorName"),
            nationality=row.get("constructorNationality")
        )

    def get_team_standings(self) -> list[TeamStanding]:
        standings = self.ergast.get_constructor_standings(season=self.year)
        df = standings.content[0] if standings and standings.content else None

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
                prev_positions = {row['constructorId']: int(row['position']) for _, row in prev_df.iterrows()}

        results = []

        for _, row in df.iterrows():
            team_id = row['constructorId']
            current_pos = row['position']
            prev_pos = prev_positions.get(team_id, current_pos)
            evolution = prev_pos - current_pos

            standing = TeamStanding(
                position=current_pos,
                points=row["points"],
                wins=row.get("wins", 0),
                team=self._format_constructor(row),
                evolution=evolution
            )

            results.append(standing)

        return results

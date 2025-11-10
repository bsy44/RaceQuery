import os
import fastf1
import pandas as pd
from fastf1.ergast import Ergast

from drivers.models.driver import Driver
from teams.models.team import Team


class TeamService:
    def __init__(self, year: int):
        self.year = year
        self.ergast = Ergast()

        cache_dir = 'src/data/fastf1_cache'
        os.makedirs(cache_dir, exist_ok=True)
        fastf1.Cache.enable_cache(cache_dir)

    def _format_driver(self, row) -> Driver:
        constructor_names = row.get("constructorNames")

        if isinstance(constructor_names, list) and constructor_names:
            last_constructor = constructor_names[-1]
        else:
            last_constructor = constructor_names or "Inconnu"

        return Driver(
            driverId=str(row.get("driverId")),
            fullName=f"{row.get('givenName')} {row.get('familyName')}",
            driverNumber=int(row.get("driverNumber")) if pd.notna(row.get("driverNumber")) else None,
            code=str(row.get("driverCode")) if row.get("driverCode") else None,
            nationality=str(row.get("driverNationality")),
            team=str(last_constructor)
        )

    def _get_standings_data(self):
        teams_data = self.ergast.get_constructor_standings(season=self.year)
        drivers_data = self.ergast.get_driver_standings(season=self.year)

        df_teams = teams_data.content[0] if teams_data and teams_data.content else None
        df_drivers = drivers_data.content[0] if drivers_data and drivers_data.content else None

        if df_teams is None or df_teams.empty or df_drivers is None or df_drivers.empty:
            return None, None

        df_drivers["fullname"] = df_drivers["givenName"] + " " + df_drivers["familyName"]
        return df_teams, df_drivers

    def list_teams(self) -> list[Team]:
        df_teams, df_drivers = self._get_standings_data()
        if df_teams is None or df_drivers is None:
            return []

        teams = []

        for _, team_row in df_teams.iterrows():
            team_name = team_row["constructorName"]

            filtered_drivers = []
            for _, d_row in df_drivers.iterrows():
                driver = self._format_driver(d_row)
                if driver.team == team_name:
                    filtered_drivers.append(driver)

            team = Team(
                constructorId=team_row["constructorId"],
                constructorName=team_row["constructorName"],
                nationality=team_row["constructorNationality"],
                drivers=filtered_drivers
            )
            teams.append(team)

        return teams

    def get_team(self, team_id: str) -> Team | None:
        df_teams, df_drivers = self._get_standings_data()
        if df_teams is None or df_drivers is None:
            return None

        team_row = df_teams[df_teams["constructorId"] == team_id]
        if team_row.empty:
            return None

        row = team_row.iloc[0]
        team_name = row["constructorName"]

        filtered_drivers = []
        for _, d_row in df_drivers.iterrows():
            driver = self._format_driver(d_row)
            if driver.team == team_name:
                filtered_drivers.append(driver)

        return Team(
            constructorId=row["constructorId"],
            constructorName=row["constructorName"],
            nationality=row["constructorNationality"],
            drivers=filtered_drivers
        )

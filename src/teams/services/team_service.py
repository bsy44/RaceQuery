import os
import fastf1
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

    def get_team(self, team_id: str) -> Team:
        standings = self.ergast.get_constructor_standings(season=self.year)
        drivers_data = self.ergast.get_driver_standings(season=self.year)

        df_teams = standings.content[0] if standings and standings.content else None
        df_drivers = drivers_data.content[0] if drivers_data and drivers_data.content else None

        if df_teams is None or df_teams.empty or df_drivers is None or df_drivers.empty:
            return []

        df_drivers["constructorNames"] = df_drivers["constructorNames"].apply(
            lambda x: x[0] if isinstance(x, list) and len(x) > 0 else None
        )
        df_drivers["fullname"] = df_drivers["givenName"] + " " + df_drivers["familyName"]

        team_row = df_teams[df_teams["constructorId"] == team_id]
        if team_row.empty:
            return None

        row = team_row.iloc[0]
        team_name = row["constructorName"]

        drivers_df = df_drivers[df_drivers["constructorNames"] == team_name][
            ["driverId", "fullname", "driverNumber", "driverCode", "driverNationality"]
        ].reset_index(drop=True)

        drivers_list = [
            Driver(
                driverId=d_row["driverId"],
                fullName=d_row["fullname"],
                driverNumber=d_row["driverNumber"],
                code=d_row["driverCode"],
                nationality=d_row["driverNationality"]
            )
            for _, d_row in drivers_df.iterrows()
        ]

        return Team(
            constructorId=row["constructorId"],
            constructorName=row["constructorName"],
            nationality=row["constructorNationality"],
            drivers=drivers_list
        )


    def list_teams(self) -> list[Team]:
        teams_data = self.ergast.get_constructor_standings(season=self.year)
        drivers_data = self.ergast.get_driver_standings(season=self.year)

        df_teams = teams_data.content[0] if teams_data and teams_data.content else None
        df_drivers = drivers_data.content[0] if drivers_data and drivers_data.content else None

        if df_teams is None or df_teams.empty or df_drivers is None or df_drivers.empty:
            return []

        df_drivers["constructorNames"] = df_drivers["constructorNames"].apply(
            lambda x: x[0] if isinstance(x, list) and len(x) > 0 else None
        )
        df_drivers["fullname"] = df_drivers["givenName"] + " " + df_drivers["familyName"]

        teams = []

        for _, team_row in df_teams.iterrows():
            team_name = team_row["constructorName"]

            drivers_df = df_drivers[df_drivers["constructorNames"] == team_name][
                ["driverId", "fullname", "driverNumber", "driverCode", "driverNationality"]
            ].reset_index(drop=True)

            drivers_list = [
                Driver(
                    driverId=d_row["driverId"],
                    fullName=d_row["fullname"],
                    driverNumber=d_row["driverNumber"],
                    code=d_row["driverCode"],
                    nationality=d_row["driverNationality"]
                )
                for _, d_row in drivers_df.iterrows()
            ]

            team = Team(
                constructorId=team_row["constructorId"],
                constructorName=team_row["constructorName"],
                nationality=team_row["constructorNationality"],
                drivers=drivers_list
            )

            teams.append(team)

        return teams




import os
import pandas as pd
import fastf1
from fastf1.ergast import Ergast

from drivers.models.driver import Driver
from teams.models.team import Team
from teams.models.team_stat import TeamStats


class TeamStatService:
    def __init__(self, year: int):
        self.year = year
        self.ergast = Ergast()

        cache_dir = "src/data/fastf1_cache"
        os.makedirs(cache_dir, exist_ok=True)
        fastf1.Cache.enable_cache(cache_dir)

        self.race_schedule = self.ergast.get_race_schedule(season=self.year)
        self.race_results = self._cached_load("race_results", "race")
        self.qualifying_results = self._cached_load("qualifying_results", "qualifying")
        self.sprint_results = self._cached_load("sprint_results", "sprint")

    def _cached_load(self, name: str, result_type: str) -> pd.DataFrame:
        cache_file = f"src/data/fastf1_cache/{self.year}_{name}.parquet"
        if os.path.exists(cache_file):
            return pd.read_parquet(cache_file)

        df = self._load_all_results(result_type)
        if not df.empty:
            df.to_parquet(cache_file)
        return df

    def _load_all_results(self, result_type: str) -> pd.DataFrame:
        dfs = []
        for _, race in self.race_schedule.iterrows():
            round_num = race["round"]
            func = getattr(self.ergast, f"get_{result_type}_results", None)
            if func:
                res = func(season=self.year, round=round_num)
                if res and hasattr(res, "content") and res.content:
                    df_race = self._clean_dataframe(res.content[0])
                    df_race["round"] = round_num  # on garde la course pour la chronologie
                    dfs.append(df_race)
        return pd.concat(dfs, ignore_index=True) if dfs else pd.DataFrame()

    def _clean_dataframe(self, df: pd.DataFrame) -> pd.DataFrame:
        for col in ["position", "grid", "driverNumber"]:
            if col in df.columns:
                df[col] = pd.to_numeric(df[col], errors="coerce")
        return df

    def _format_Team(self, row) -> Team:
        drivers_data = self.ergast.get_driver_standings(season=self.year)
        df_drivers = drivers_data.content[0] if drivers_data and drivers_data.content else None

        drivers_list = []
        if df_drivers is not None and not df_drivers.empty:
            df_drivers["fullname"] = df_drivers["givenName"] + " " + df_drivers["familyName"]

            def get_last_constructor(x):
                if isinstance(x, list) and len(x) > 0:
                    return x[-1]
                return x or "Inconnu"

            df_drivers["lastConstructor"] = df_drivers["constructorNames"].apply(get_last_constructor)

            df_filtered = df_drivers[df_drivers["lastConstructor"] == row["constructorName"]]

            drivers_list = [
                Driver(
                    driverId=d_row["driverId"],
                    fullName=d_row["fullname"],
                    birthday=d_row.get("dateOfBirth"),
                    driverNumber=d_row.get("driverNumber"),
                    code=d_row.get("driverCode"),
                    nationality=d_row.get("driverNationality"),
                    team=d_row.get("lastConstructor")
                )
                for _, d_row in df_filtered.iterrows()
            ]

        return Team(
            constructorId=row.get("constructorId"),
            constructorName=row.get("constructorName"),
            nationality=row.get("constructorNationality"),
            drivers=drivers_list
        )

    def get_nb_podium(self, id_team: str) -> int:
        df = self.race_results
        return 0 if df.empty else df[df["constructorId"] == id_team]["position"].isin([1, 2, 3]).sum()

    def get_top_10(self, id_team: str) -> int:
        df = self.race_results
        return 0 if df.empty else df[df["constructorId"] == id_team]["position"].le(10).sum()

    def get_pole(self, id_team: str) -> int:
        df = self.qualifying_results
        return 0 if df.empty else df[df["constructorId"] == id_team]["position"].eq(1).sum()

    def get_dnf(self, id_team: str) -> int:
        df = self.race_results
        return 0 if df.empty else df[(df["constructorId"] == id_team) & (df["status"] == "Retired")].shape[0]

    def get_sprint_win(self, id_team: str) -> int:
        df = self.sprint_results
        return 0 if df.empty else df[df["constructorId"] == id_team]["position"].eq(1).sum()

    def get_sprint_podium(self, id_team: str) -> int:
        df = self.sprint_results
        return 0 if df.empty else df[df["constructorId"] == id_team]["position"].isin([1, 2, 3]).sum()

    def get_sprint_pole(self, id_team: str) -> int:
        df = self.sprint_results
        return 0 if df.empty else df[df["constructorId"] == id_team]["grid"].eq(1).sum()

    def get_avg_race_position(self, id_team: str) -> float:
        df = self.race_results
        if df.empty:
            return 0
        team_positions = df[df["constructorId"] == id_team]["position"].dropna()
        return round(team_positions.mean(), 2) if not team_positions.empty else None

    def get_avg_qualifying_position(self, id_team: str) -> float:
        df = self.qualifying_results
        if df.empty:
            return 0
        team_positions = df[df["constructorId"] == id_team]["position"].dropna()
        return round(team_positions.mean(), 2) if not team_positions.empty else None

    def get_team_stats_summary(self, id_team: str) -> TeamStats | dict:
        standing = self.ergast.get_constructor_standings(season=self.year, constructor=id_team)
        df = standing.content[0] if standing and standing.content else None

        if df is None or df.empty:
            return {"error": f"Aucune donnée trouvée pour {id_team} en {self.year}"}

        row = df.iloc[0]
        team = self._format_Team(row)

        team_stats = TeamStats(
            team=team,
            position=row["position"],
            points=row["points"],
            win=row["wins"],
            podium=self.get_nb_podium(id_team),
            pole=self.get_pole(id_team),
            top10=self.get_top_10(id_team),
            dnf=self.get_dnf(id_team),
            sprint_win=self.get_sprint_win(id_team),
            sprint_podium=self.get_sprint_podium(id_team),
            sprint_pole=self.get_sprint_pole(id_team),
            avg_race_finish=self.get_avg_race_position(id_team),
            avg_qualifying_finish=self.get_avg_qualifying_position(id_team)
        )

        return team_stats

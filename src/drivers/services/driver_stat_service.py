import os
import pandas as pd
import fastf1
from fastf1.ergast import Ergast
from drivers.models.driver import Driver
from drivers.models.driver_stat import DriverStats


class DriverStatService:
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
                    dfs.append(df_race)
        return pd.concat(dfs, ignore_index=True) if dfs else pd.DataFrame()

    def _clean_dataframe(self, df: pd.DataFrame) -> pd.DataFrame:
        for col in ["position", "grid", "driverNumber"]:
            if col in df.columns:
                df[col] = pd.to_numeric(df[col], errors="coerce")
        return df

    def _format_driver(self, row) -> Driver:
        driver_number = row.get("driverNumber")
        driver_code = row.get("code") or row.get("driverCode")
        constructor_names = row.get("constructorNames")
        constructor_ids = row.get("constructorIds")

        if isinstance(constructor_names, list) and constructor_names:
            last_constructor = constructor_names[-1]
            last_constructor_id = (
                constructor_ids[-1] if isinstance(constructor_ids, list) and constructor_ids else None
            )
        else:
            last_constructor = constructor_names or "Inconnu"
            last_constructor_id = constructor_ids or None

        return Driver(
            driverId=str(row.get("driverId")),
            driverNumber=int(driver_number) if pd.notna(driver_number) else None,
            code=str(driver_code) if driver_code else None,
            fullName=f"{row.get('givenName')} {row.get('familyName')}",
            givenName=str(row.get("givenName")),
            familyName=str(row.get("familyName")),
            nationality=str(row.get("driverNationality")),
            birthday=str(row.get("dateOfBirth")),
            team=str(last_constructor),
            team_id=str(last_constructor_id) if last_constructor_id else None
        )

    def get_nb_podium(self, id_driver: str) -> int:
        df = self.race_results
        if df.empty:
            return 0
        return df[df["driverId"] == id_driver]["position"].isin([1, 2, 3]).sum()

    def get_top_10(self, id_driver: str) -> int:
        df = self.race_results
        if df.empty:
            return 0
        return df[df["driverId"] == id_driver]["position"].le(10).sum()

    def get_pole(self, id_driver: str) -> int:
        df = self.qualifying_results
        if df.empty:
            return 0
        return df[df["driverId"] == id_driver]["position"].eq(1).sum()

    def get_dnf(self, id_driver: str) -> int:
        df = self.race_results
        if df.empty:
            return 0
        return df[(df["driverId"] == id_driver) & (df["status"] == "Retired")].shape[0]

    def get_sprint_win(self, id_driver: str) -> int:
        df = self.sprint_results
        if df.empty:
            return 0
        return df[df["driverId"] == id_driver]["position"].eq(1).sum()

    def get_sprint_podium(self, id_driver: str) -> int:
        df = self.sprint_results
        if df.empty:
            return 0
        return df[df["driverId"] == id_driver]["position"].isin([1, 2, 3]).sum()

    def get_sprint_pole(self, id_driver: str) -> int:
        df = self.sprint_results
        if df.empty:
            return 0
        return df[df["driverId"] == id_driver]["grid"].eq(1).sum()

    def get_avg_race_position(self, id_driver: str) -> float:
        df = self.race_results
        if df.empty:
            return 0
        driver_positions = df[df["driverId"] == id_driver]["position"].dropna()
        return round(driver_positions.mean(), 2) if not driver_positions.empty else None

    def get_avg_qualifying_position(self, id_driver: str) -> float:
        df = self.qualifying_results
        if df.empty:
            return 0
        driver_positions = df[df["driverId"] == id_driver]["position"].dropna()
        return round(driver_positions.mean(), 2) if not driver_positions.empty else None

    def get_driver_stats_summary(self, id_driver: str) -> DriverStats | dict:
        standing = self.ergast.get_driver_standings(season=self.year, driver=id_driver)
        df = standing.content[0] if standing and standing.content else None

        if df is None or df.empty:
            return {"error": f"Aucune donnée trouvée pour {id_driver} en {self.year}"}

        row = df.iloc[0]
        driver = self._format_driver(row)

        driver_stats = DriverStats(
            driver=driver,
            position=row["position"],
            points=row["points"],
            win=row["wins"],
            podium=self.get_nb_podium(id_driver),
            pole=self.get_pole(id_driver),
            top10=self.get_top_10(id_driver),
            dnf=self.get_dnf(id_driver),
            sprint_win=self.get_sprint_win(id_driver),
            sprint_podium=self.get_sprint_podium(id_driver),
            sprint_pole=self.get_sprint_pole(id_driver),
            avg_race_finish=self.get_avg_race_position(id_driver),
            avg_qualifying_finish=self.get_avg_qualifying_position(id_driver),
        )

        return driver_stats

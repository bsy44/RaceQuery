import os
import pandas as pd
import fastf1
from fastf1.ergast import Ergast
from backend.races.race import Race
from backend.drivers.driver import Driver
from backend.teams.team import Constructor
from backend.races.circuits.circuit import Circuit
from backend.races.result import Result, DriverResult, FastestLap
from backend.races.qualifyings.qualifying import Qualifying, QualifyingResult
from backend.races.sprints.sprint import Sprint, SprintResult
from backend.races.laps.lap import Lap, Timing

class RaceService:
    def __init__(self, season: int, round: int = None):
        self.season = season
        self.round = round
        self.ergast = Ergast()

        cache_dir = 'backend/data/fastf1_cache'
        os.makedirs(cache_dir, exist_ok=True)
        fastf1.Cache.enable_cache(cache_dir)

    def _format_date(self, value):
        return None if value is None or str(value) == "NaT" else str(value)

    def _format_time(self, value):
        return None if value is None or str(value) == "NaT" else str(value) + "Z"

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

    def _format_driver(self, row) -> Driver:
        return Driver(
            driverId=row.get("driverId"),
            fullName=f"{row.get('givenName')} {row.get('familyName')}",
            nationality=row.get("driverNationality"),
            driverNumber=row.get("driverNumber"),
            code=row.get("driverCode")
        )

    def _format_constructor(self, row) -> Constructor:
        return Constructor(
            constructorId=row.get("constructorId"),
            constructorName=row.get("constructorName"),
            nationality=row.get("constructorNationality")
        )

    def _format_fastest_lap(self, row) -> FastestLap | None:
        if row.get("fastestLapTime") is None:
            return None
        return FastestLap(
            rank=row.get("fastestLapRank"),
            time=self._format_timedelta(row.get("fastestLapTime"))
        )

    def _create_circuit(self, row) -> Circuit:
        return Circuit(
            circuitId=row.get("circuitId"),
            circuitName=row.get("circuitName"),
            locality=row.get("locality"),
            country=row.get("country")
        )

    def _create_race(self, row) -> Race:
        circuit = self._create_circuit(row)
        return Race(
            season=row.get("season"),
            round=row.get("round"),
            raceName=row.get("raceName"),
            circuit=circuit,
            date=self._format_date(row.get("raceDate")),
            time=self._format_time(row.get("raceTime")),
            firstPractice={
                "date": self._format_date(row.get("fp1Date")),
                "time": self._format_time(row.get("fp1Time"))
            },
            secondPractice={
                "date": self._format_date(row.get("fp2Date")),
                "time": self._format_time(row.get("fp2Time"))
            },
            thirdPractice={
                "date": self._format_date(row.get("fp3Date")),
                "time": self._format_time(row.get("fp3Time"))
            },
            qualifying={
                "date": self._format_date(row.get("qualifyingDate")),
                "time": self._format_time(row.get("qualifyingTime"))
            },
            sprint={
                "date": self._format_date(row.get("sprintDate")),
                "time": self._format_time(row.get("sprintTime"))
            }
        )

    def _create_driver_result(self, r) -> DriverResult:
        driver = self._format_driver(r)
        constructor = self._format_constructor(r)
        fastest_lap =self._format_fastest_lap(r)

        return DriverResult(
            driver=driver,
            constructor=constructor,
            position=str(r.get("position")),
            points=str(r.get("points")),
            grid=str(r.get("grid")),
            laps=str(r.get("laps")),
            status=r.get("status"),
            total_time=self._format_timedelta(r.get("totalRaceTime")),
            total_millis=str(r.get("totalRaceTimeMillis")) if r.get("totalRaceTimeMillis") else None,
            fastest_lap=fastest_lap
        )

    def get_races(self) -> list[Race]:
        df = self.ergast.get_race_schedule(season=self.season, round=self.round)
        return [self._create_race(row) for _, row in df.iterrows()]

    def get_race_results(self) -> list[Result]:
        schedule_df = self.ergast.get_race_schedule(season=self.season, round=self.round)
        if self.round is not None:
            schedule_df = schedule_df[schedule_df['round'] == self.round]

        results_list = []
        for _, race_row in schedule_df.iterrows():
            race = self._create_race(race_row)
            race_results_resp = self.ergast.get_race_results(season=self.season, round=race_row['round'])
            results_df = race_results_resp.content[0] if (
                hasattr(race_results_resp, "content") and len(race_results_resp.content) > 0) else None

            driver_results = [self._create_driver_result(r)
                              for _, r in results_df.iterrows()] \
                if results_df is not None else []

            results_list.append(Result(race=race, results=driver_results))

        return results_list

    def get_split(self, session_q: str) -> dict:
        """Retourne les résultats de qualification pour Q1/Q2/Q3"""

        # récupération calendrier
        df = self.ergast.get_race_schedule(season=self.season)
        if self.round:
            df = df[df['round'] == self.round]

        races = []

        for _, row in df.iterrows():
            round_num = row['round']
            quali_resp = self.ergast.get_qualifying_results(season=self.season, round=round_num)
            quali_df = quali_resp.content[0] if hasattr(quali_resp, "content") and len(quali_resp.content) > 0 else None

            results = []
            if quali_df is not None:
                for _, drv in quali_df.iterrows():
                    lap_time = drv.get(session_q)
                    if pd.isna(lap_time):
                        continue

                    results.append(QualifyingResult(
                        position=None,
                        driver_id=drv.get("driverId"),
                        number=str(drv.get("driverNumber")) if pd.notna(drv.get("driverNumber")) else None,
                        code=drv.get("driverCode"),
                        full_name=f"{drv.get('givenName')} {drv.get('familyName')}",
                        constructor=drv.get("constructorName"),
                        lap_time=self._format_timedelta(lap_time),
                        session=session_q
                    ))

                results.sort(key=lambda r: r.lap_time)

                # Filtre selon Q2/Q3
                if session_q == "Q2":
                    results = results[:15]
                elif session_q == "Q3":
                    results = results[:10]

                for idx, r in enumerate(results, start=1):
                    r.position = str(idx)

            races.append(Qualifying(
                season=self.season,
                round=round_num,
                race_name=row.get("raceName"),
                results=results
            ))

        return {
            "season": str(self.season),
            "Races": [r.to_dict() for r in races]
        }

    def _format_sprint_result(self, row) -> SprintResult:
        return SprintResult(
            position=str(row.get("position")),
            points=str(row.get("points")),
            grid=str(row.get("grid")),
            laps=str(row.get("laps")),
            status=row.get("status"),
            driver=self._format_driver(row),
            constructor=self._format_constructor(row),
            total_time=self._format_timedelta(row.get("totalRaceTime")),
            total_millis=str(row.get("totalRaceTimeMillis")) if row.get("totalRaceTimeMillis") else None,
            fastest_lap=self._format_fastest_lap(row)
        )

    def get_sprint(self) -> list[Sprint]:
        schedule_df = self.ergast.get_race_schedule(season=self.season, round=self.round)
        if self.round is not None:
            schedule_df = schedule_df[schedule_df['round'] == self.round]

        sprints = []

        for _, race_row in schedule_df.iterrows():
            round_num = race_row['round']

            sprint_resp = self.ergast.get_sprint_results(season=self.season, round=round_num)
            sprint_df = sprint_resp.content[0] if hasattr(sprint_resp, "content") and sprint_resp.content else None

            results = [self._format_sprint_result(r) for _, r in sprint_df.iterrows()] if sprint_df is not None else []

            sprints.append(Sprint(
                season=race_row.get("season"),
                round=round_num,
                race_name=race_row.get("raceName"),
                circuit= self._create_circuit(race_row),
                date=self._format_date(race_row.get("raceDate")),
                time=self._format_time(race_row.get("raceTime")),
                results=results
            ))

        return sprints

    def get_stints(self, driver_id: str) -> dict:
        session = fastf1.get_session(self.season, self.round, "R")
        session.load(laps=True, telemetry=False, weather=False)

        laps = session.laps
        if driver_id:
            laps = laps.pick_drivers([driver_id])

        # Créer un Stint à chaque changement de pneu
        laps.loc[:, 'Stint'] = (laps['Compound'] != laps['Compound'].shift()).cumsum()

        results = []
        for drv in laps["Driver"].unique():
            drv_laps = laps.pick_drivers([drv])
            stint_groups = drv_laps.groupby("Stint")

            driver_stints = [
                {
                    "stintId": int(stint_id),
                    "startLap": int(grp["LapNumber"].min()),
                    "endLap": int(grp["LapNumber"].max()),
                    "compound": grp["Compound"].iloc[0] if "Compound" in grp else None,
                    "tyreLifeStart": int(grp["TyreLife"].min()) if "TyreLife" in grp else None,
                    "laps": int(grp["LapNumber"].max() - grp["LapNumber"].min() + 1)
                }
                for stint_id, grp in stint_groups
            ]

            results.append({
                "driverId": drv,
                "Stints": driver_stints
            })

        return {
            "season": self.season,
            "round": self.round,
            "stints": results
        }

    def get_lap(self, lap: int = None) -> dict:
        """
        Récupère les tours d'une course (par round),
        soit tous les tours, soit un tour spécifique si `lap` est fourni.
        """
        schedule_df = self.ergast.get_race_schedule(season=self.season, round=self.round)
        if self.round is not None:
            schedule_df = schedule_df[schedule_df["round"] == self.round]

        races = []

        for _, race_row in schedule_df.iterrows():
            round_num = race_row["round"]

            lap_resp = self.ergast.get_lap_times(
                season=self.season,
                round=round_num,
                lap_number=lap
            )
            lap_df = lap_resp.content[0] if hasattr(lap_resp, "content") and len(lap_resp.content) > 0 else None

            laps = []
            if lap_df is not None:
                for lap_num, group in lap_df.groupby("number"):
                    timings = [
                        Timing(
                            driverId=row.get("driverId"),
                            position=str(row.get("position"))
                        )
                        for _, row in group.iterrows()
                    ]
                    laps.append(Lap(lap_number=lap_num, timings=timings))

            race_info = Race(
                season=self.season,
                round=self.round,
                raceName=race_row.get("raceName"),
                circuit=self._create_circuit(race_row),
                date=self._format_date(race_row.get("raceDate")),
                time=self._format_time(race_row.get("raceTime")),
                laps= [lap.to_dict() for lap in laps]
            )

            races.append(race_info)

        return {
            "season": str(self.season),
            "Races": races
        }

    def get_laps_for_driver(self, driver_id: str) -> list[Lap]:
        session = fastf1.get_session(self.season, self.round, "R")
        session.load(laps=True, telemetry=False, weather=False)

        driver_laps = session.laps.pick_drivers([driver_id])

        laps_for_driver = []
        for lap_num, lap_row in driver_laps.iterlaps():
            lap_obj = Lap(
                lap_number=lap_row["LapNumber"],
                timings=[Timing(driverId=driver_id, position=str(lap_row["Position"]))]
            )
            laps_for_driver.append(lap_obj)

        return laps_for_driver

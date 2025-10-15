import os
import pandas as pd
import fastf1
from fastf1.ergast import Ergast
from backend.events.race import Race
from backend.drivers.driver import Driver
from backend.teams.team import Constructor

class EventService:
    def __init__(self, season: int, round: int = None):
       self.season = season
       self.round = round
       self.ergast = Ergast()

       cache_dir = 'backend/data/fastf1_cache'
       os.makedirs(cache_dir, exist_ok=True)
       fastf1.Cache.enable_cache(cache_dir)

    def get_schedule(self):
        schedule = fastf1.get_event_schedule(self.season, include_testing=False)

        events_list = []

        for _, event in schedule.iterrows():

           circuit_df = self.ergast.get_circuits(self.season)
           circuit_row = circuit_df[circuit_df['locality'].str.contains(event['Location'], case=False)]
           circuit_name = circuit_row.iloc[0]['circuitName'] if not circuit_row.empty else ''

           event_info = {
               "season": self.season,
               "round": int(event['RoundNumber']),
               "country": event['Country'],
               "location": event['Location'],
               "circuit_name": circuit_name,
               "official_name": event['OfficialEventName'],
               "short_name": event['EventName'],
               "event_format": event['EventFormat'],
               "event_date": str(event['EventDate']),
               "sessions": []
           }

           for i in range(1, 6):
               name_col = f"Session{i}"
               date_col = f"Session{i}Date"
               date_utc_col = f"Session{i}DateUtc"

               if name_col in event and event[name_col]:
                   event_info["sessions"].append({
                       "name": event[name_col],
                       "local_date": str(event[date_col]),
                       "utc_date": str(event[date_utc_col]) if date_utc_col in event else None,
                   })

           events_list.append(event_info)

        return events_list

    def get_event(self):
        schedule = fastf1.get_event_schedule(self.season, include_testing=False)

        try:
           event = schedule.get_event_by_round(self.round)
        except ValueError:
           return None

        circuit_df = self.ergast.get_circuits(self.season)
        circuit_row = circuit_df[circuit_df['locality'].str.contains(event['Location'], case=False)]
        circuit_name = circuit_row.iloc[0]['circuitName'] if not circuit_row.empty else ''
        event_info = {
           "season": self.season,
           "round": int(event['RoundNumber']),
           "country": event['Country'],
           "location": event['Location'],
           "circuit_name": circuit_name,
           "official_name": event['OfficialEventName'],
           "short_name": event['EventName'],
           "event_format": event['EventFormat'],
           "event_date": str(event['EventDate']),
           "sessions": []
        }

        for i in range(1, 6):
           name_col = f"Session{i}"
           date_col = f"Session{i}Date"
           date_utc_col = f"Session{i}DateUtc"

           if name_col in event and event[name_col]:
               event_info["sessions"].append({
                   "name": event[name_col],
                   "local_date": str(event[date_col]),
                   "utc_date": str(event[date_utc_col]) if date_utc_col in event else None
               })

        return event_info

    def get_session_results(self, session_id: str) -> list[dict]:
        try:
            session = fastf1.get_session(self.season, self.round, session_id)
            session.load(laps=True, telemetry=False, weather=False)
        except Exception as e:
            print(f"Erreur FastF1 : {e}")
            return []

        results = []

        if "Practice" in session.name or "FP" in session.name:
            laps = session.laps

            if laps.empty:
                print("Aucun tour enregistré pour cette session.")
                return []

            driver_col = next((col for col in ["Driver", "DriverId", "DriverNumber"] if col in laps.columns), None)
            if not driver_col:
                print("Impossible de trouver la colonne du pilote.")
                return []

            best_laps_idx = laps.groupby(driver_col)["LapTime"].idxmin().dropna()
            best_laps = laps.loc[best_laps_idx].copy()

            best_laps = best_laps.sort_values("LapTime").reset_index(drop=True)

            for pos, (_, lap) in enumerate(best_laps.iterrows(), start=1):
                driver_id = lap.get(driver_col)
                driver_info = session.get_driver(driver_id)

                # Nombre total de tours du pilote
                total_laps = laps[laps[driver_col] == driver_id].shape[0]

                results.append({
                    "position": pos,
                    "driver": driver_info.get("FullName", None),
                    "team": lap.get("Team", None),
                    "best_lap": str(lap["LapTime"]).split(" days ")[-1] if pd.notna(lap["LapTime"]) else None,
                    "lap": total_laps
                })

            return results

        if session.results is None:
            print("Pas de résultats disponibles pour cette session.")
            return []

        for _, row in session.results.iterrows():
            result_data = {
                "position": int(row["Position"]) if not pd.isna(row["Position"]) else None,
                "driver": row.get("FullName"),
                "team": row.get("TeamName"),
                "laps": int(row["Laps"]) if not pd.isna(row.get("Laps")) else None,
                "time": str(row.get("Time")) if row.get("Time") is not None else None,
                "points": float(row["Points"]) if not pd.isna(row.get("Points")) else 0.0,
                "status": row.get("Status"),
                "grid_position": int(row["GridPosition"]) if not pd.isna(row.get("GridPosition")) else None,
                "q1": str(row.get("Q1")) if pd.notna(row.get("Q1")) else None,
                "q2": str(row.get("Q2")) if pd.notna(row.get("Q2")) else None,
                "q3": str(row.get("Q3")) if pd.notna(row.get("Q3")) else None,
            }
            results.append(result_data)

        return results
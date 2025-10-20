import os
import pandas as pd
import fastf1
import re
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

    def get_session_results(self, session_id: str) -> dict:
        """
        Retourne les résultats de la session avec infos supplémentaires :
        - vainqueur
        - poleman
        - meilleur tour
        """
        DEFAULT_INFO = {
            "driver": "Information non disponible",
            "team": "",
            "time": ""
        }

        try:
            session = fastf1.get_session(self.season, self.round, session_id)
            session.load(laps=True, telemetry=False, weather=False)
        except Exception as e:
            print(f"Erreur FastF1 : {e}")
            return {
                "results": [],
                "winner": DEFAULT_INFO,
                "poleman": DEFAULT_INFO,
                "fastestLap": DEFAULT_INFO
            }

        results = []

        # --- FP / Practice ---
        if "Practice" in session.name or "FP" in session.name:
            laps = session.laps
            if laps.empty:
                return {"results": [], "winner": None, "poleman": None, "fastestLap": None}

            driver_col = next((c for c in ["Driver", "DriverId", "DriverNumber"] if c in laps.columns), None)
            if not driver_col:
                return {"results": [], "winner": None, "poleman": None, "fastestLap": None}

            best_laps_idx = laps.groupby(driver_col)["LapTime"].idxmin().dropna()
            best_laps = laps.loc[best_laps_idx].copy().sort_values("LapTime").reset_index(drop=True)

            for pos, (_, lap) in enumerate(best_laps.iterrows(), start=1):
                driver_id = lap.get(driver_col)
                driver_info = session.get_driver(driver_id)
                total_laps = laps[laps[driver_col] == driver_id].shape[0]

                driver_name = getattr(driver_info, "FullName", None)
                driver_number = getattr(driver_info, "DriverNumber", None)

                results.append({
                    "position": pos,
                    "driver": driver_name,
                    "DriverNumber": driver_number,
                    "team": lap.get("Team"),
                    "best_lap": self._clean_fastf1_time(lap["LapTime"]) if pd.notna(lap["LapTime"]) else None,
                    "laps": total_laps
                })

            return {"results": results, "winner": None, "poleman": None, "fastestLap": None}

        # --- Course / Qualification ---
        results_df = pd.DataFrame(session.results) if session.results is not None else pd.DataFrame()
        if results_df.empty:
            return {"results": [], "winner": DEFAULT_INFO, "poleman": DEFAULT_INFO, "fastestLap": DEFAULT_INFO}

        winner = None
        poleman = None
        fastest_lap = None

        for _, row in results_df.iterrows():
            status = str(row.get("Status")) if row.get("Status") else ""
            time_val = row.get("Time")
            clean_time = None
            if "Lapped" in status or "+1 Lap" in status or "+2 Laps" in status:
                match = re.search(r"\+(\d+)\s+Lap", status)
                clean_time = f"{int(match.group(1))} Tours" if match else "1 Tour"
            elif time_val and pd.notna(time_val):
                clean_time = self._clean_fastf1_time(time_val)

            result_data = {
                "position": int(row["Position"]) if not pd.isna(row.get("Position")) else None,
                "driver": row.get("FullName"),
                "DriverNumber": row.get("DriverNumber"),
                "team": row.get("TeamName"),
                "teamColor": row.get("TeamColor"),
                "laps": int(row["Laps"]) if not pd.isna(row.get("Laps")) else None,
                "time": clean_time,
                "points": float(row["Points"]) if not pd.isna(row.get("Points")) else 0.0,
                "status": row.get("Status"),
                "grid_position": int(row["GridPosition"]) if not pd.isna(row.get("GridPosition")) else None,
                "q1": self._clean_fastf1_time(row.get("Q1")) if pd.notna(row.get("Q1")) else None,
                "q2": self._clean_fastf1_time(row.get("Q2")) if pd.notna(row.get("Q2")) else None,
                "q3": self._clean_fastf1_time(row.get("Q3")) if pd.notna(row.get("Q3")) else None
            }
            results.append(result_data)

            if session_id.upper() == "R" and row.get("Position") == 1:
                winner = {"driver": row.get("FullName"), "team": row.get("TeamName"), "time": clean_time}

        # --- Statut du weekend
        race_finished = False
        if session_id.upper() == "R" and not results_df.empty:
            statuses = results_df['Status'].dropna().unique()
            if "Finished" in statuses:
                race_finished = True

        try:
            quali_session = fastf1.get_session(self.season, self.round, "Q")
            quali_session.load()
            quali_df = pd.DataFrame(quali_session.results) if quali_session.results is not None else pd.DataFrame()
            if not quali_df.empty:
                first = quali_df.iloc[0]
                poleman = {"driver": first["FullName"], "team": first["TeamName"],
                           "time": self._clean_fastf1_time(first.get("Q3"))}
        except Exception as e:
            print(f"Impossible de charger la qualif pour la pole : {e}")

        try:
            laps = session.laps
            if not laps.empty:
                best_lap = laps.loc[laps["LapTime"].idxmin()]
                driver_info = session.get_driver(best_lap["Driver"])
                driver_name = getattr(driver_info, "FullName", None)
                fastest_lap = {"driver": driver_name, "team": best_lap.get("Team"),
                               "time": self._clean_fastf1_time(best_lap["LapTime"])}
        except Exception as e:
            print(f"Erreur lors de la récupération du meilleur tour : {e}")

        if race_finished:
            data = {
                "results": results,
                "winner": winner or DEFAULT_INFO,
                "poleman": poleman or DEFAULT_INFO,
                "fastestLap": fastest_lap or DEFAULT_INFO
            }
        else:
            data = {
                "results": results,
                "poleman": poleman or DEFAULT_INFO
            }

        return data

    def _clean_fastf1_time(self, time_str):
        if not time_str:
            return None
        t = str(time_str).strip()
        t = t.replace("0 days ", "")
        t = re.sub(r'(\.\d*?)0+$', r'\1', t)
        t = re.sub(r'\.$', '', t)
        parts = t.split(":")
        parts = [p.lstrip("0") or "0" for p in parts]
        if len(parts) == 3:
            h, m, s = parts
            if h == "0":
                t = f"{m}:{s}" if m != "0" else s
            else:
                t = f"{h}:{m}:{s}"
        elif len(parts) == 2:
            m, s = parts
            t = s if m == "0" else f"{m}:{s}"
        else:
            t = parts[0]
        if t.startswith("."):
            t = "0" + t
        return t

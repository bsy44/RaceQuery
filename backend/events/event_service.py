import os
import pandas as pd
import fastf1
import re
import threading
from functools import lru_cache
from fastf1.ergast import Ergast


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


    @staticmethod
    @lru_cache(maxsize=50)
    def _load_fastf1_session_cached(season, round_, session_id):
        session = fastf1.get_session(season, round_, session_id)

        sid = session_id.upper()
        if sid.startswith("FP") or "PRACTICE" in session.name.upper():
            session.load(laps=True, telemetry=False, weather=False)
        elif sid in ["Q", "QUALIFYING"]:
            session.load(laps=False, telemetry=False, weather=False)
        elif sid in ["SPRINT", "SS", "SR"]:
            session.load(laps=True, telemetry=False, weather=False)
        else:
            session.load(laps=True, telemetry=False, weather=False)
        return session


    def _preload_weekend_async(self):
        def preload():
            for sid in ["FP1", "FP2", "FP3", "Q", "R"]:
                try:
                    self._load_fastf1_session_cached(self.season, self.round, sid)
                except Exception:
                    pass
        threading.Thread(target=preload, daemon=True).start()

    def get_session_results(self, session_id: str) -> dict:
        DEFAULT_INFO = {"driver": "Information non disponible", "team": "", "time": ""}
        results, winner, poleman, fastest_lap = [], None, None, None

        # Charger la session demandée
        try:
            session = self._load_fastf1_session_cached(self.season, self.round, session_id)
        except Exception as e:
            print(f"Erreur FastF1 : {e}")
            return {"results": [], "winner": DEFAULT_INFO, "poleman": DEFAULT_INFO, "fastestLap": DEFAULT_INFO}

        # 🟢 On essaie de charger la course (pour winner & fastest lap)
        race_session = None
        try:
            race_session = self._load_fastf1_session_cached(self.season, self.round, "R")
        except Exception:
            pass

        race_finished = race_session and race_session.results is not None and not race_session.results.empty

        # --- Calcul winner / fastest lap s’ils existent ---
        if race_finished:
            race_df = pd.DataFrame(race_session.results)
            if not race_df.empty:
                first = race_df.iloc[0]
                winner = {
                    "driver": first.get("FullName"),
                    "team": first.get("TeamName"),
                    "time": self._clean_fastf1_time(first.get("Time"))
                }

            # Meilleur tour global du week-end
            try:
                laps = race_session.laps
                if not laps.empty:
                    best_lap = laps.loc[laps["LapTime"].idxmin()]
                    driver_info = race_session.get_driver(best_lap["Driver"])
                    fastest_lap = {
                        "driver": getattr(driver_info, "FullName", None),
                        "team": best_lap.get("Team"),
                        "time": self._clean_fastf1_time(best_lap["LapTime"])
                    }
            except Exception:
                pass

        # --- Pole position ---
        try:
            quali_session = self._load_fastf1_session_cached(self.season, self.round, "Q")
            quali_df = pd.DataFrame(quali_session.results)
            if not quali_df.empty:
                first = quali_df.iloc[0]
                poleman = {
                    "driver": first["FullName"],
                    "team": first["TeamName"],
                    "time": self._clean_fastf1_time(first.get("Q3"))
                }
        except Exception:
            pass

        # --- Si c’est une session d’essais libres ---
        if "Practice" in session.name or "FP" in session.name:
            laps = session.laps
            if laps.empty:
                return {
                    "results": [],
                    "winner": winner or DEFAULT_INFO,
                    "poleman": poleman or DEFAULT_INFO,
                    "fastestLap": fastest_lap or DEFAULT_INFO
                }

            driver_col = next((c for c in ["Driver", "DriverId", "DriverNumber"] if c in laps.columns), None)
            if not driver_col:
                return {"results": [], "winner": winner or DEFAULT_INFO, "poleman": poleman or DEFAULT_INFO,
                        "fastestLap": fastest_lap or DEFAULT_INFO}

            best_laps_idx = laps.groupby(driver_col)["LapTime"].idxmin().dropna()
            best_laps = laps.loc[best_laps_idx].copy().sort_values("LapTime").reset_index(drop=True)

            for pos, (_, lap) in enumerate(best_laps.iterrows(), start=1):
                driver_id = lap.get(driver_col)
                driver_info = session.get_driver(driver_id)
                total_laps = laps[laps[driver_col] == driver_id].shape[0]

                results.append({
                    "position": pos,
                    "driver": getattr(driver_info, "FullName", None),
                    "DriverNumber": getattr(driver_info, "DriverNumber", None),
                    "team": lap.get("Team"),
                    "best_lap": self._clean_fastf1_time(lap["LapTime"]) if pd.notna(lap["LapTime"]) else None,
                    "laps": total_laps
                })

            self._preload_weekend_async()
            return {
                "results": results,
                "winner": winner or DEFAULT_INFO,
                "poleman": poleman or DEFAULT_INFO,
                "fastestLap": fastest_lap or DEFAULT_INFO
            }

        # --- Pour la course / qualif normales ---
        results_df = pd.DataFrame(session.results) if session.results is not None else pd.DataFrame()
        if results_df.empty:
            return {"results": [], "winner": winner or DEFAULT_INFO, "poleman": poleman or DEFAULT_INFO,
                    "fastestLap": fastest_lap or DEFAULT_INFO}

        for _, row in results_df.iterrows():
            time_val = row.get("Time")
            clean_time = self._clean_fastf1_time(time_val) if pd.notna(time_val) else None

            results.append({
                "position": int(row["Position"]) if not pd.isna(row.get("Position")) else None,
                "driver": row.get("FullName"),
                "DriverNumber": row.get("DriverNumber"),
                "team": row.get("TeamName"),
                "laps": int(row["Laps"]) if not pd.isna(row.get("Laps")) else None,
                "q1": self._clean_fastf1_time(row.get("Q1")) if pd.notna(row.get("Q1")) else None,
                "q2": self._clean_fastf1_time(row.get("Q2")) if pd.notna(row.get("Q2")) else None,
                "q3": self._clean_fastf1_time(row.get("Q3")) if pd.notna(row.get("Q3")) else None,
                "time": clean_time,
                "points": float(row["Points"]) if not pd.isna(row.get("Points")) else 0.0,
                "status": row.get("Status"),
            })

        return {
            "results": results,
            "winner": winner or DEFAULT_INFO,
            "poleman": poleman or DEFAULT_INFO,
            "fastestLap": fastest_lap or DEFAULT_INFO
        }

    def _clean_fastf1_time(self, time_str):
        if not time_str:
            return None
        t = str(time_str).strip().replace("0 days ", "")
        t = re.sub(r'(\.\d*?)0+$', r'\1', t)
        t = re.sub(r'\.$', '', t)
        parts = t.split(":")
        parts = [p.lstrip("0") or "0" for p in parts]
        if len(parts) == 3:
            h, m, s = parts
            t = f"{m}:{s}" if h == "0" and m != "0" else (s if m == "0" else f"{h}:{m}:{s}")
        elif len(parts) == 2:
            m, s = parts
            t = s if m == "0" else f"{m}:{s}"
        else:
            t = parts[0]
        if t.startswith("."):
            t = "0" + t
        return t

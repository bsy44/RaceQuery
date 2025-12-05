import math
from cache_reader import load_json_file


class RaceService:
    def __init__(self, season: int, round: int = None):
        self.season = season
        self.round = round


    def _safe_float(self, val):
        if val is None: return None
        try:
            f = float(val)
            if math.isnan(f) or math.isinf(f):
                return None
            return f
        except (ValueError, TypeError):
            return None


    def _format_time_ms(self, time_ms):
        total_ms = self._safe_float(time_ms)

        if total_ms is None:
            return str(time_ms) if time_ms and str(time_ms).lower() != "nan" else None

        try:
            seconds = int(total_ms / 1000)
            ms = int(total_ms % 1000)

            minutes = seconds // 60
            seconds = seconds % 60

            hours = minutes // 60
            minutes = minutes % 60

            if hours > 0:
                return f"{hours}:{minutes:02d}:{seconds:02d}.{ms:03d}"
            elif minutes > 0:
                return f"{minutes}:{seconds:02d}.{ms:03d}"
            else:
                return f"{seconds}.{ms:03d}"
        except Exception:
            return str(time_ms)


    def _clean_time_str(self, time_str):
        if not time_str or str(time_str).lower() in ["nat", "nan", "none", "null"]:
            return None

        t = str(time_str).strip().replace("0 days ", "")

        try:
            if len(t) < 8 and ":" not in t: return t

            if "." in t:
                main, ms = t.split(".")
                t = f"{main}.{ms[:3]}"

            parts = t.split(":")
            if len(parts) == 3:
                hours = int(parts[0])
                minutes = int(parts[1])
                seconds_part = parts[2]

                if hours > 0:
                    return f"{hours}:{minutes:02d}:{seconds_part}"
                elif minutes > 0:
                    return f"{minutes}:{seconds_part}"
                else:
                    return seconds_part
            return t
        except:
            return t


    def _get_session_filename(self, session_type: str):
        sid = session_type.upper()
        name = "Race"
        if sid in ["FP1", "PRACTICE 1"]:
            name = "Practice1"
        elif sid in ["FP2", "PRACTICE 2"]:
            name = "Practice2"
        elif sid in ["FP3", "PRACTICE 3"]:
            name = "Practice3"
        elif sid in ["Q", "QUALIFYING"]:
            name = "Qualifying"
        elif sid in ["S", "SPRINT"]:
            name = "Sprint"
        elif sid in ["SQ", "SPRINT QUALIFYING"]:
            name = "SprintQualifying"
        elif sid in ["SS", "SPRINT SHOOTOUT"]:
            name = "SprintShootout"
        return f"{self.season}_R{self.round}_{name}.json"


    def get_schedule(self):
        filename = f"{self.season}_schedule.json"
        schedule = load_json_file(f'data_cache/ergast/{self.season}', filename)
        return schedule if schedule else []


    def get_event(self):
        full_schedule = self.get_schedule()
        if not full_schedule: return None
        return next((e for e in full_schedule if e['round'] == self.round), None)


    def get_session_results(self, session_id: str) -> dict:
        DEFAULT_INFO = {"driver": "N/A", "team": "", "team_id": "", "time": ""}

        filename = self._get_session_filename(session_id)
        is_practice = "Practice" in filename or "FP" in session_id.upper()

        session_data = load_json_file(f'data_cache/sessions/{self.season}', filename)

        if not session_data:
            return {"results": [], "winner": DEFAULT_INFO, "poleman": DEFAULT_INFO, "fastestLap": DEFAULT_INFO}

        results_raw = session_data.get('results', [])
        laps_raw = session_data.get('laps', [])

        winner = DEFAULT_INFO
        poleman = DEFAULT_INFO
        fastest_lap = DEFAULT_INFO

        try:
            q_filename = self._get_session_filename("Q")
            q_data = session_data if "Qualifying" in filename else load_json_file(f'data_cache/sessions/{self.season}', q_filename)
            if q_data and q_data.get('results'):
                p = q_data['results'][0]
                poleman = {
                    "driver": p.get("FullName"),
                    "team": p.get("TeamName"),
                    "team_id": p.get("TeamId"),
                    "time": self._clean_time_str(p.get("Q3") or p.get("Q1"))
                }
        except:
            pass

        try:
            r_filename = self._get_session_filename("Race")
            r_data = session_data if "Race" in filename else load_json_file(f'data_cache/sessions/{self.season}', r_filename)
            if r_data:
                if r_data.get('results'):
                    w = r_data['results'][0]
                    w_time_raw = w.get("Time_ms") if w.get("Time_ms") and str(w.get("Time_ms")) != "nan" else w.get(
                        "Time")
                    formatted_w_time = self._format_time_ms(w_time_raw)

                    winner = {
                        "driver": w.get("FullName"),
                        "team": w.get("TeamName"),
                        "team_id": w.get("TeamId"),
                        "time": formatted_w_time
                    }

                r_laps = r_data.get('laps', [])
                valid_laps = [l for l in r_laps if self._safe_float(l.get('LapTime_ms')) is not None]
                if valid_laps:
                    best = min(valid_laps, key=lambda x: self._safe_float(x['LapTime_ms']))
                    d_code = best.get("Driver")
                    d_info = next((r for r in r_data.get('results', []) if r.get("Abbreviation") == d_code), None)
                    fastest_lap = {
                        "driver": d_info.get("FullName", d_code) if d_info else d_code,
                        "team": d_info.get("TeamName", "") if d_info else "",
                        "team_id": d_info.get("TeamId", "") if d_info else "",
                        "time": self._format_time_ms(best.get("LapTime_ms"))
                    }
        except:
            pass

        results_formatted = []
        winner_time_ms = None
        winner_laps = 0

        try:
            winner_row = next(
                (r for r in results_raw if str(r.get('Position')) == '1.0' or str(r.get('Position')) == '1'), None)
            if winner_row:
                t_ms = winner_row.get('Time_ms')
                if not t_ms or str(t_ms).lower() == 'nan':
                    t_ms = winner_row.get('LapTime_ms')
                winner_time_ms = self._safe_float(t_ms)

                w_laps = self._safe_float(winner_row.get('Laps'))
                winner_laps = int(w_laps) if w_laps else 0
        except:
            pass

        for row in results_raw:
            time_ms = row.get("Time_ms")
            if not time_ms or str(time_ms).lower() in ["nan", "none", "nat", "null", ""]:
                time_ms = row.get("LapTime_ms")

            status = str(row.get("Status", "")).strip()
            pos_val = row.get("Position")

            time_display = ""
            position = int(self._safe_float(pos_val)) if self._safe_float(pos_val) is not None else None
            current_laps = int(self._safe_float(row.get("Laps")) or 0)
            current_ms = self._safe_float(time_ms)

            valid_statuses = ["Finished", "Lapped", "+1 Lap"]
            is_finished = any(v in status for v in valid_statuses) or status.startswith("+") or "Lap" in status

            if not is_finished and position != 1 and status:
                time_display = status

            elif not is_practice and winner_laps > 0 and current_laps < winner_laps:
                diff = winner_laps - current_laps
                suffix = "Tour" if diff == 1 else "Tours"
                time_display = f"+ {diff} {suffix}"

            elif current_ms is not None:
                if position == 1:
                    time_display = self._format_time_ms(current_ms)
                elif winner_time_ms:
                    if current_ms < winner_time_ms:
                        gap = current_ms
                    else:
                        gap = current_ms - winner_time_ms

                    if gap < 60000:
                        s = int(gap / 1000)
                        ms = int(gap % 1000)
                        time_display = f"+ {s}.{ms:03d}"
                    else:
                        time_display = f"+ {self._format_time_ms(gap)}"
                else:
                    time_display = self._format_time_ms(current_ms)

            else:
                time_display = status if status else "-"

            evolution = 0
            try:
                grid_float = self._safe_float(row.get("GridPosition"))
                if grid_float is not None and position is not None:
                    evolution = int(grid_float) - position
            except:
                pass

            results_formatted.append({
                "position": position,
                "driver": row.get("FullName"),
                "last_name": row.get("LastName"),
                "DriverNumber": row.get("DriverNumber"),
                "teamColor": row.get("TeamColor", ""),
                "team": row.get("TeamName"),
                "team_id": row.get("TeamId", ""),
                "laps": current_laps,
                "q1": self._clean_time_str(row.get("Q1")),
                "q2": self._clean_time_str(row.get("Q2")),
                "q3": self._clean_time_str(row.get("Q3")),
                "time": time_display,
                "evolution": evolution,
                "points": float(self._safe_float(row.get("Points")) or 0),
                "status": status,
                "tyre": row.get("Tyre"),
            })

        results_formatted.sort(key=lambda x: x['position'] if x['position'] is not None else 999)

        return {
            "results": results_formatted,
            "winner": winner,
            "poleman": poleman,
            "fastestLap": fastest_lap
        }
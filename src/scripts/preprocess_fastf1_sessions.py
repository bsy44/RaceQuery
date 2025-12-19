import json
import os
import fastf1
import pandas as pd
from fastf1.core import Session
import numpy as np
from datetime import datetime

BASE_OUTPUT_DIR = "../data_cache/sessions"
CACHE_DIR = '../data/fastf1_cache'

COLOR_TO_TEAM_ID = {
    "3671C6": "red_bull", "1E41FF": "red_bull",
    "27F4D2": "mercedes", "00D2BE": "mercedes",
    "E80020": "ferrari", "DC0000": "ferrari",
    "FF8000": "mclaren",
    "229971": "aston_martin", "006F62": "aston_martin",
    "0093CC": "alpine", "2293D1": "alpine",
    "64C4FF": "williams", "005AFF": "williams",
    "6692FF": "rb", "4E7CFF": "rb",
    "52E252": "sauber", "00E701": "sauber",
    "B6BABD": "haas", "FFFFFF": "haas", "767676": "haas"
}


def ensure_directory_exists(directory_path):
    if not os.path.exists(directory_path):
        os.makedirs(directory_path, exist_ok=True)


def get_output_dir_for_year(year: int):
    year_dir = os.path.join(BASE_OUTPUT_DIR, str(year))
    ensure_directory_exists(year_dir)
    return year_dir


def save_json(year: int, filename: str, data: dict):
    output_dir = get_output_dir_for_year(year)
    path = os.path.join(output_dir, filename)
    with open(path, "w", encoding="utf-8") as f:
        json.dump(data, f, indent=2)
    print(f"   ✔ Saved {filename}")


def td_to_ms(td):
    if pd.isna(td): return None
    if isinstance(td, pd.Timedelta): return int(td.total_seconds() * 1000)
    return None


def clean_nat_values(data):
    if isinstance(data, dict):
        return {k: clean_nat_values(v) for k, v in data.items()}
    elif isinstance(data, list):
        return [clean_nat_values(elem) for elem in data]
    elif pd.isna(data) or str(data).lower() in ["nan", "nat", "none"]:
        return None
    elif isinstance(data, (pd.Timestamp, datetime, np.datetime64)):
        return str(data)
    return data


def get_valid_val(val):
    if val is None or pd.isna(val): return ""
    s = str(val).strip()
    if s.lower() in ["nan", "nat", "none", ""]: return ""
    return s


def generate_id(name):
    name = get_valid_val(name)
    if not name: return ""
    return name.lower().replace("'", "").replace(" ", "_").replace("-", "_")


def normalize_team_id(t_id, color=""):
    t_id = get_valid_val(t_id).lower()

    if "red_bull" in t_id: return "red_bull"
    if "racing_bulls" in t_id or "rb" in t_id or "visa" in t_id: return "rb"
    if "haas" in t_id: return "haas"
    if "aston" in t_id: return "aston_martin"
    if "alpine" in t_id: return "alpine"
    if "williams" in t_id: return "williams"
    if "mclaren" in t_id: return "mclaren"
    if "ferrari" in t_id: return "ferrari"
    if "mercedes" in t_id: return "mercedes"
    if "sauber" in t_id or "stake" in t_id or "kick" in t_id: return "sauber"
    if "alpha" in t_id: return "alphatauri"
    if "alfa" in t_id: return "alfa"

    if not t_id and color:
        clean_color = str(color).upper().strip()
        if clean_color in COLOR_TO_TEAM_ID:
            return COLOR_TO_TEAM_ID[clean_color]

    return t_id


def build_results(session: Session, session_type: str):
    results_df = session.results
    laps = session.laps

    tyre_map = {}
    if laps is not None and not laps.empty:
        is_race = "Race" in session_type or ("Sprint" in session_type and "Qualifying" not in session_type)
        try:
            if is_race:
                last_laps = laps.sort_values('LapNumber').groupby('Driver').last()
                tyre_map = last_laps['Compound'].to_dict()
            else:
                best_laps_compound = laps.sort_values('LapTime').groupby('Driver').first()
                tyre_map = best_laps_compound['Compound'].to_dict()
        except:
            pass

    if "Position" not in results_df.columns or results_df["Position"].isna().all():
        if laps is None or laps.empty: return []

        best_laps_df = laps.sort_values("LapTime").groupby("Driver").first().sort_values("LapTime")
        results = []
        pos = 1

        for driver_code, row_lap in best_laps_df.iterrows():
            drv = session.get_driver(driver_code)

            raw_did = get_valid_val(drv.get("DriverId"))
            raw_tid = get_valid_val(drv.get("TeamId"))
            t_name = get_valid_val(drv.get("TeamName"))
            t_color = get_valid_val(drv.get("TeamColor"))

            d_id = raw_did if raw_did else generate_id(drv.get("LastName") or drv.get("Abbreviation"))

            t_id = raw_tid if raw_tid else generate_id(t_name)
            t_id = normalize_team_id(t_id, t_color)

            tyre = str(row_lap.get("Compound", ""))

            results.append({
                "DriverNumber": drv.get("DriverNumber", ""),
                "BroadcastName": drv.get("BroadcastName", ""),
                "Abbreviation": drv.get("Abbreviation", ""),
                "DriverId": d_id,
                "TeamName": t_name,
                "TeamColor": t_color,
                "TeamId": t_id,
                "FirstName": drv.get("FirstName", ""),
                "LastName": drv.get("LastName", ""),
                "FullName": drv.get("FullName", ""),
                "HeadshotUrl": drv.get("HeadshotUrl", ""),
                "CountryCode": drv.get("CountryCode", ""),
                "Position": pos,
                "ClassifiedPosition": pos,
                "GridPosition": "",
                "Status": "",
                "Points": "",
                "Laps": int(laps[laps["Driver"] == driver_code].shape[0]),
                "LapTime_ms": td_to_ms(row_lap["LapTime"]),
                "Tyre": tyre
            })
            pos += 1
        return results

    results_df = results_df.copy()

    def repair_row_ids(row):
        d_id = get_valid_val(row.get('DriverId'))
        t_id = get_valid_val(row.get('TeamId'))

        if not d_id:
            d_id = generate_id(row.get('LastName')) or generate_id(row.get('Abbreviation'))

        if not t_id:
            t_name = get_valid_val(row.get('TeamName'))
            t_id = generate_id(t_name)

        t_color = get_valid_val(row.get('TeamColor'))
        t_id = normalize_team_id(t_id, t_color)

        return pd.Series([d_id, t_id])

    if 'DriverId' in results_df.columns and 'TeamId' in results_df.columns:
        results_df[['DriverId', 'TeamId']] = results_df.apply(repair_row_ids, axis=1)

    if 'Status' in results_df.columns and 'Laps' in results_df.columns:
        winner_laps = results_df['Laps'].max()

        def fill_missing_status(row):
            original = get_valid_val(row.get('Status'))
            if original: return original
            try:
                laps = float(row.get('Laps', 0))
                if pd.isna(laps): return "DNF"
                if laps == winner_laps:
                    return "Finished"
                elif laps < winner_laps:
                    diff = int(winner_laps - laps)
                    return f"+{diff} Laps" if diff > 1 else "+1 Lap"
                else:
                    return "Finished"
            except:
                return ""

        results_df['Status'] = results_df.apply(fill_missing_status, axis=1)

    if 'Time' in results_df.columns:
        results_df['Time_ms'] = results_df['Time'].apply(td_to_ms)
        results_df = results_df.drop(columns=['Time'])

    if 'Abbreviation' in results_df.columns:
        results_df['Tyre'] = results_df['Abbreviation'].map(tyre_map).fillna("")
    else:
        results_df['Tyre'] = ""

    return results_df.astype(str).to_dict("records")


def preprocess_session_data(year: int, gp_round: int, session_type: str):
    try:
        print(f"   ⏳ Processing {session_type}...")

        results_data = []
        laps_data = []
        stints_data = []
        event_name = "Unknown GP"

        try:
            session: Session = fastf1.get_session(year, gp_round, session_type)

            try:
                session.load(laps=True, weather=True, telemetry=False)
            except Exception:
                pass

            if hasattr(session, 'event'):
                event_name = session.event['EventName']

            if hasattr(session, 'drivers') and session.drivers:
                results_data = build_results(session, session_type)
            else:
                print(f"      ⚠️ No drivers found for {session_type}, generating empty results.")

            if session.laps is not None and not session.laps.empty:
                laps_df = session.laps.reset_index(drop=True).copy()
                for col in ['LapTime', 'Sector1Time', 'Sector2Time', 'Sector3Time']:
                    if col in laps_df:
                        laps_df[col + "_ms"] = laps_df[col].apply(td_to_ms)
                laps_df = laps_df.drop(columns=['LapTime', 'Sector1Time', 'Sector2Time', 'Sector3Time'],
                                       errors='ignore')
                lap_cols = ['Driver', 'LapNumber', 'IsPersonalBest', 'Compound', 'TyreLife', 'Stint', 'LapTime_ms',
                            'Sector1Time_ms', 'Sector2Time_ms', 'Sector3Time_ms', 'TrackStatus']
                lap_cols_existing = [c for c in lap_cols if c in laps_df.columns]
                laps_data = laps_df[lap_cols_existing].astype(str).to_dict('records')

                stint_cols = ['Driver', 'Stint', 'Compound', 'TyreLife']
                stint_cols_existing = [c for c in stint_cols if c in session.laps.columns]
                stints = session.laps[stint_cols_existing].dropna(subset=['Stint']).drop_duplicates(
                    subset=['Driver', 'Stint']).sort_values(['Driver', 'Stint'])
                stints_data = stints.astype(str).to_dict('records')

        except Exception as e:
            print(f"      ⚠️ FastF1 Load Error for {session_type}: {e}")

        session_info = {
            "year": year,
            "round": gp_round,
            "name": event_name,
            "session_type": session_type
        }
        try:
            session_info["event_details"] = session.event.to_dict()
        except:
            pass

        session_info = clean_nat_values(session_info)

        session_data = {
            "info": session_info,
            "results": results_data,
            "laps": laps_data,
            "stints": stints_data,
        }

        normalized_name = session_type.replace(' ', '')
        if "Sprint" in session_type and "Shootout" in session_type:
            normalized_name = "SprintQualifying"

        filename = f"{year}_R{gp_round}_{normalized_name}.json"
        save_json(year, filename, session_data)

    except Exception as e:
        print(f"❌ CRITICAL ERROR {year} R{gp_round} {session_type}: {e}")


def preprocess_year(year: int):
    ensure_directory_exists(CACHE_DIR)
    fastf1.Cache.enable_cache(CACHE_DIR)
    print(f"   ✅ FastF1 Cache enabled at: {os.path.abspath(CACHE_DIR)}")
    pd.set_option('display.max_columns', None)

    print(f"\n=== Processing all sessions for {year} ===")

    try:
        schedule = fastf1.get_event_schedule(year, include_testing=False)
        schedule = schedule[schedule['EventName'].notna()].reset_index(drop=True)
    except Exception as e:
        print(f"❌ Could not load schedule for {year}: {e}")
        return

    if schedule.empty: return

    for _, event in schedule.iterrows():
        gp_round = event['RoundNumber']
        print(f"--- R{gp_round} {event['EventName']} ---")

        for i in range(1, 6):
            session_name_col = f"Session{i}"
            if session_name_col in event and event[session_name_col]:
                session_type = event[session_name_col]
                if isinstance(session_type, str):
                    preprocess_session_data(year, gp_round, session_type)
        print("-" * 40)
    print(f"\n🎉 Pre-processing of {year} completed successfully!")


if __name__ == "__main__":
    TARGET_YEAR = 2025
    try:
        preprocess_year(TARGET_YEAR)
    except KeyboardInterrupt:
        print("\n🛑 Interrupted by user.")
    except Exception as e:
        print(f"\n❌ Unexpected error: {e}")
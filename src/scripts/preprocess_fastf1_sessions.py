import json
import os
import fastf1
import pandas as pd
from fastf1.core import Session


BASE_OUTPUT_DIR = "../data_cache/sessions"
CACHE_DIR = '../data/fastf1_cache'


def ensure_directory_exists(directory_path):
    if not os.path.exists(directory_path):
        os.makedirs(directory_path, exist_ok=True)
        print(f"   📂 Created directory: {directory_path}")


def get_output_dir_for_year(year: int):
    year_dir = os.path.join(BASE_OUTPUT_DIR, str(year))
    ensure_directory_exists(year_dir)
    return year_dir


def save_json(year: int, filename: str, data: dict):
    output_dir = get_output_dir_for_year(year)
    path = os.path.join(output_dir, filename)

    absolute_path = os.path.abspath(path)
    print(f"   📂 Attempting to save to: {absolute_path}")

    with open(path, "w", encoding="utf-8") as f:
        json.dump(data, f, indent=2)

    print(f"✔ Saved {filename}")


def td_to_ms(td):
    if pd.isna(td):
        return None
    if isinstance(td, pd.Timedelta):
        return int(td.total_seconds() * 1000)
    return None


def build_practice_results(session: Session):
    results_df = session.results

    if results_df["Position"].isna().all():
        laps = session.laps

        if laps.empty:
            print("   ⚠️ Practice session has no laps → no reconstructed results.")
            return []

        best_laps = (
            laps.groupby("Driver")["LapTime"]
                .min()
                .sort_values()
        )

        results = []

        for pos, (driver, lap_time) in enumerate(best_laps.items(), start=1):
            drv = session.get_driver(driver)

            results.append({
                "DriverNumber": drv.get("DriverNumber", ""),
                "BroadcastName": drv.get("BroadcastName", ""),
                "Abbreviation": drv.get("Abbreviation", ""),
                "DriverId": drv.get("DriverId", ""),
                "TeamName": drv.get("TeamName", ""),
                "TeamColor": drv.get("TeamColor", ""),
                "TeamId": drv.get("TeamId", ""),
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
                "Laps": int(laps[laps["Driver"] == driver].shape[0]),
                "LapTime_ms": td_to_ms(lap_time)
            })

        return results

    results_df = results_df.copy()

    if 'Time' in results_df.columns:
        results_df['Time_ms'] = results_df['Time'].apply(td_to_ms)
        results_df = results_df.drop(columns=['Time'])

    return results_df.astype(str).to_dict("records")


def preprocess_session_data(year: int, gp_round: int, session_type: str):
    try:
        session: Session = fastf1.get_session(year, gp_round, session_type)
        print(f"   ⏳ Loading data for {session_type}...")

        session.load(laps=True, weather=True, telemetry=False)

        if session.drivers is None or not session.drivers:
            print(f"   ❌ No drivers loaded → skip {session_type}")
            return

        results_data = build_practice_results(session)

        laps_df = session.laps.reset_index(drop=True).copy()

        for col in ['LapTime', 'Sector1Time', 'Sector2Time', 'Sector3Time']:
            if col in laps_df:
                laps_df[col + "_ms"] = laps_df[col].apply(td_to_ms)

        laps_df = laps_df.drop(columns=['LapTime', 'Sector1Time', 'Sector2Time', 'Sector3Time'], errors='ignore')

        lap_cols = [
            'Driver', 'LapNumber', 'IsPersonalBest', 'Compound', 'TyreLife',
            'Stint', 'LapTime_ms', 'Sector1Time_ms', 'Sector2Time_ms',
            'Sector3Time_ms', 'TrackStatus'
        ]
        lap_cols_existing = [c for c in lap_cols if c in laps_df.columns]
        laps_data = laps_df[lap_cols_existing].astype(str).to_dict('records')

        stint_cols = ['Driver', 'Stint', 'Compound', 'TyreLife']
        stints = (
            session.laps[stint_cols]
            .dropna(subset=['Stint'])
            .drop_duplicates(subset=['Driver', 'Stint'])
            .sort_values(['Driver', 'Stint'])
        )
        stints_data = stints.astype(str).to_dict('records')

        session_data = {
            "info": {
                "year": year,
                "round": gp_round,
                "name": session.event['EventName'],
                "session_type": session_type
            },
            "results": results_data,
            "laps": laps_data,
            "stints": stints_data,
        }

        filename = f"{year}_R{gp_round}_{session_type.replace(' ', '')}.json"
        save_json(year, filename, session_data)

    except Exception as e:
        print(f"❌ Could not process {year} R{gp_round} {session_type}: {e}")


def preprocess_year(year: int):
    ensure_directory_exists(CACHE_DIR)
    fastf1.Cache.enable_cache(CACHE_DIR)
    print(f"   ✅ FastF1 Cache enabled at: {os.path.abspath(CACHE_DIR)}")

    pd.set_option('display.max_columns', None)

    session_types = [
        'Race', 'Qualifying', 'Sprint',
        'Practice 1', 'Practice 2', 'Practice 3'
    ]

    print(f"\n=== Processing all sessions for {year} ===")

    try:
        schedule = fastf1.get_event_schedule(year, include_testing=False)
        schedule = schedule[schedule['EventName'].notna()].reset_index(drop=True)
    except Exception as e:
        print(f"❌ Could not load schedule for {year}: {e}")
        return

    if schedule.empty:
        print(f"   ⚠️ No official events found for {year}.")
        return

    for _, event in schedule.iterrows():
        gp_round = event['RoundNumber']
        print(f"--- R{gp_round} {event['EventName']} ---")

        for st in session_types:
            preprocess_session_data(year, gp_round, st)

        print("-" * 40)

    print(f"\n🎉 Pre-processing of {year} completed successfully!")


if __name__ == "__main__":
    TARGET_YEAR = 2022

    try:
        preprocess_year(TARGET_YEAR)

    except KeyboardInterrupt:
        print("\n🛑 Interrupted by user.")
    except Exception as e:
        print(f"\n❌ Unexpected error: {e}")

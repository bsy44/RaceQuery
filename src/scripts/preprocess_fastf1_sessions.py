import json
import os
import fastf1
import pandas as pd
from fastf1.core import Session
import numpy as np
from datetime import datetime

# 🎯 Chemins
BASE_OUTPUT_DIR = "../data_cache/sessions"
CACHE_DIR = '../data/fastf1_cache'


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


def generate_id(name):
    if not name or pd.isna(name): return ""
    return str(name).lower().strip().replace(" ", "_").replace("-", "_")


def build_results(session: Session):
    """Construit les résultats ou renvoie une liste vide si données manquantes."""
    if session.results is None or session.results.empty:
        return []

    results_df = session.results

    # CAS 1 : ESSAIS LIBRES (Reconstruction via Laps)
    if "Position" not in results_df.columns or results_df["Position"].isna().all():
        laps = session.laps
        if laps is None or laps.empty: return []

        try:
            best_laps = laps.groupby("Driver")["LapTime"].min().sort_values()
            results = []
            for pos, (driver_code, lap_time) in enumerate(best_laps.items(), start=1):
                drv = session.get_driver(driver_code)

                d_id = drv.get("DriverId") or generate_id(drv.get("LastName") or drv.get("Abbreviation"))
                t_id = drv.get("TeamId") or generate_id(drv.get("TeamName"))

                # Normalisation Team ID
                if "red_bull" in t_id:
                    t_id = "red_bull"
                elif "racing_bulls" in t_id or "rb" in t_id:
                    t_id = "rb"
                elif "haas" in t_id:
                    t_id = "haas"
                elif "aston" in t_id:
                    t_id = "aston_martin"
                elif "alpine" in t_id:
                    t_id = "alpine"
                elif "williams" in t_id:
                    t_id = "williams"
                elif "mclaren" in t_id:
                    t_id = "mclaren"
                elif "ferrari" in t_id:
                    t_id = "ferrari"
                elif "mercedes" in t_id:
                    t_id = "mercedes"
                elif "sauber" in t_id or "kick" in t_id:
                    t_id = "sauber"

                results.append({
                    "DriverNumber": drv.get("DriverNumber", ""),
                    "BroadcastName": drv.get("BroadcastName", ""),
                    "Abbreviation": drv.get("Abbreviation", ""),
                    "DriverId": d_id,
                    "TeamName": drv.get("TeamName", ""),
                    "TeamColor": drv.get("TeamColor", ""),
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
                    "LapTime_ms": td_to_ms(lap_time)
                })
            return results
        except Exception as e:
            print(f"   ⚠️ Error building practice results: {e}")
            return []

    # CAS 2 : COURSE / QUALIF
    results_df = results_df.copy()

    if 'DriverId' in results_df.columns:
        mask = (results_df['DriverId'] == "") | (results_df['DriverId'].isna())
        if mask.any():
            results_df.loc[mask, 'DriverId'] = results_df.loc[mask, 'LastName'].apply(generate_id)

    if 'TeamId' in results_df.columns:
        mask_team = (results_df['TeamId'] == "") | (results_df['TeamId'].isna())
        if mask_team.any():
            results_df.loc[mask_team, 'TeamId'] = results_df.loc[mask_team, 'TeamName'].apply(generate_id)
            results_df['TeamId'] = results_df['TeamId'].apply(lambda x: "red_bull" if "red_bull" in x else x)
            results_df['TeamId'] = results_df['TeamId'].apply(lambda x: "rb" if "racing_bulls" in x or "rb" in x else x)
            results_df['TeamId'] = results_df['TeamId'].apply(lambda x: "haas" if "haas" in x else x)
            results_df['TeamId'] = results_df['TeamId'].apply(lambda x: "sauber" if "stake" in x or "kick" in x else x)
            results_df['TeamId'] = results_df['TeamId'].apply(lambda x: "aston_martin" if "aston" in x else x)

    if 'Status' in results_df.columns and 'Laps' in results_df.columns:
        winner_laps = results_df['Laps'].max()

        def fill_missing_status(row):
            original_status = str(row.get('Status', '')).strip()
            if original_status and original_status.lower() != "nan": return original_status
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

    return results_df.astype(str).to_dict("records")


def preprocess_session_data(year: int, gp_round: int, session_type: str):
    try:
        print(f"   ⏳ Processing {session_type}...")

        # 1. Initialiser des données vides par défaut
        results_data = []
        laps_data = []
        stints_data = []

        # 2. Tenter de charger FastF1
        try:
            session: Session = fastf1.get_session(year, gp_round, session_type)
            # On charge sans lever d'erreur si ça échoue
            session.load(laps=True, weather=True, telemetry=False)

            # Si le chargement réussit partiellement
            if session.drivers:
                results_data = build_results(session)
            else:
                print(f"      ⚠️ No drivers found for {session_type}, generating empty file.")

            if session.laps is not None and not session.laps.empty:
                laps_df = session.laps.reset_index(drop=True).copy()
                for col in ['LapTime', 'Sector1Time', 'Sector2Time', 'Sector3Time']:
                    if col in laps_df:
                        laps_df[col + "_ms"] = laps_df[col].apply(td_to_ms)

                # Nettoyage colonnes laps
                laps_df = laps_df.drop(columns=['LapTime', 'Sector1Time', 'Sector2Time', 'Sector3Time'],
                                       errors='ignore')
                lap_cols = ['Driver', 'LapNumber', 'IsPersonalBest', 'Compound', 'TyreLife', 'Stint', 'LapTime_ms',
                            'Sector1Time_ms', 'Sector2Time_ms', 'Sector3Time_ms', 'TrackStatus']
                lap_cols_existing = [c for c in lap_cols if c in laps_df.columns]
                laps_data = laps_df[lap_cols_existing].astype(str).to_dict('records')

                # Stints
                stint_cols = ['Driver', 'Stint', 'Compound', 'TyreLife']
                stint_cols_existing = [c for c in stint_cols if c in session.laps.columns]
                stints = session.laps[stint_cols_existing].dropna(subset=['Stint']).drop_duplicates(
                    subset=['Driver', 'Stint']).sort_values(['Driver', 'Stint'])
                stints_data = stints.astype(str).to_dict('records')

            # Info de base (Même si FastF1 échoue, on a les infos de l'appel)
            event_name = session.event['EventName']

        except Exception as e:
            print(f"      ⚠️ FastF1 Load Error for {session_type}: {e}")
            event_name = "Unknown GP"

        # 3. Construction du JSON (Même vide)
        session_info = {
            "year": year,
            "round": gp_round,
            "name": event_name,
            "session_type": session_type
        }

        session_data = {
            "info": session_info,
            "results": results_data,
            "laps": laps_data,
            "stints": stints_data,
        }

        # 4. Normalisation du Nom de Fichier (CRUCIAL)
        # "Sprint Qualifying" -> "SprintQualifying"
        # "Sprint Shootout" -> "SprintQualifying" (Compatibilité 2023)
        normalized_name = session_type.replace(' ', '')

        # Gestion spécifique du Sprint Shootout (2023) pour qu'il matche "SprintQualifying"
        # Cela permet à ton backend d'utiliser le même code pour 2023, 2024 et 2025
        if "Sprint" in session_type and "Shootout" in session_type:
            normalized_name = "SprintQualifying"

        # Note : Pour 2022, "Sprint" restera "Sprint", et il n'y a pas de Shootout, donc c'est parfait.

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

    if schedule.empty:
        print(f"   ⚠️ No official events found for {year}.")
        return

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
    TARGET_YEAR = 2024

    try:
        preprocess_year(TARGET_YEAR)
    except KeyboardInterrupt:
        print("\n🛑 Interrupted by user.")
    except Exception as e:
        print(f"\n❌ Unexpected error: {e}")
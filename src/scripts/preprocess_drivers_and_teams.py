import os
import fastf1
from fastf1.ergast import Ergast
import pandas as pd
import numpy as np
from utils.data_utils import get_path, save_json, apply_data_patches, ensure_directory_exists


OUTPUT_DIR = get_path("data_cache", "static")
CACHE_DIR = get_path("data", "fastf1_cache")


def format_numeric_str(val):
    if pd.isna(val) or val is None or str(val).lower() in ['nan', 'none', 'nat', '']:
        return ""
    try:
        return str(int(float(val)))
    except (ValueError, TypeError):
        return str(val).strip()


def clean_and_convert_df(df: pd.DataFrame, year: int) -> list:
    if df is None or df.empty:
        return []

    df = apply_data_patches(df, year)

    num_cols = ['driverNumber', 'number', 'permanentNumber', 'position', 'rank']
    for col in num_cols:
        if col in df.columns:
            df[col] = df[col].apply(format_numeric_str)

    return df.astype(str).replace('nan', '').replace('None', '').to_dict('records')


def preprocess_static_data(year: int):
    api = Ergast(result_type='pandas')
    print(f"\n--- 🛠️ Processing static data for season {year} ---")

    print(f"   ⏳ Fetching drivers via get_driver_info...")

    drivers_df = pd.DataFrame()
    try:
        response = api.get_driver_info(season=year)
        if response is not None:
            if hasattr(response, 'dataframe'):
                drivers_df = response.dataframe
            else:
                drivers_df = response

            if not drivers_df.empty:
                print(f"      ✅ {len(drivers_df)} drivers found via info.")

        if drivers_df.empty:
            print(f"      ℹ️ Driver info empty, trying standings...")
            response_standings = api.get_driver_standings(season=year)
            if response_standings is not None:
                if hasattr(response_standings, 'standings'):
                    drivers_df = response_standings.standings
                else:
                    drivers_df = response_standings

                if not drivers_df.empty:
                    print(f"      ✅ {len(drivers_df)} drivers found via standings.")
    except Exception as e:
        print(f"      ⚠️ Error fetching drivers: {e}")

    team_drivers_map = {}
    drivers_data = []

    if not drivers_df.empty:
        base_cols = [
            'driverId', 'driverCode', 'code', 'driverNumber', 'number', 'permanentNumber',
            'givenName', 'familyName', 'dateOfBirth',
            'driverNationality', 'nationality', 'url', 'constructorNames', 'constructorIds'
        ]
        cols = [col for col in base_cols if col in drivers_df.columns]

        drivers_static_df = drivers_df[cols].drop_duplicates(subset=['driverId'])
        drivers_data = clean_and_convert_df(drivers_static_df, year)

        patched_drivers = apply_data_patches(drivers_df, year)

        for _, row in patched_drivers.iterrows():
            raw_num = row.get('permanentNumber') or row.get('driverNumber') or row.get('number') or ""
            driver_num = format_numeric_str(raw_num)

            mini_driver = {
                "driverId": str(row.get('driverId')),
                "code": str(row.get('code') or row.get('driverCode') or "UNK"),
                "driverNumber": driver_num,
                "dateOfBirth": str(row.get('dateOfBirth')),
                "givenName": str(row.get('givenName')),
                "familyName": str(row.get('familyName')),
                "nationality": str(row.get('driverNationality') or row.get('nationality') or "")
            }

            c_ids = row.get('constructorIds')
            ids_list = []
            if isinstance(c_ids, (list, pd.Series, np.ndarray)):
                ids_list = list(c_ids)
            elif isinstance(c_ids, str) and c_ids:
                ids_list = [x.strip() for x in
                            c_ids.replace(
                                "[", "").replace("]", "").replace("'", "").replace('"', "").split(',')
                            ]

            for team_id in ids_list:
                if team_id:
                    if team_id not in team_drivers_map:
                        team_drivers_map[team_id] = []
                    if not any(d['driverId'] == mini_driver['driverId'] for d in team_drivers_map[team_id]):
                        team_drivers_map[team_id].append(mini_driver)
    else:
        print(f"   ⚠️ No driver data found for {year}.")

    print(f"   ⏳ Fetching constructors via get_constructor_info...")

    constructors_df = pd.DataFrame()
    try:
        response_const = api.get_constructor_info(season=year)
        if response_const is not None:
            if hasattr(response_const, 'dataframe'):
                constructors_df = response_const.dataframe
            else:
                constructors_df = response_const

        if constructors_df.empty:
            print(f"      ℹ️ Constructor info empty, trying standings...")
            response_c_standings = api.get_constructor_standings(season=year)
            if response_c_standings is not None:
                if hasattr(response_c_standings, 'standings'):
                    constructors_df = response_c_standings.standings
                else:
                    constructors_df = response_c_standings
    except Exception as e:
        print(f"      ⚠️ Error fetching constructors: {e}")

    constructors_data = []
    if not constructors_df.empty:
        constructors_data = clean_and_convert_df(constructors_df, year)

        for team in constructors_data:
            c_id = team.get('constructorId')
            team['drivers'] = team_drivers_map.get(c_id, [])
    else:
        print(f"   ⚠️ No constructor data found for {year}.")

    if drivers_data:
        save_json(OUTPUT_DIR, year, f"{year}_drivers.json", drivers_data)
    if constructors_data:
        save_json(OUTPUT_DIR, year, f"{year}_constructors.json", constructors_data)


def preprocess_all_static_data(start_year=2022, end_year=2026):
    ensure_directory_exists(OUTPUT_DIR)
    ensure_directory_exists(CACHE_DIR)
    fastf1.Cache.enable_cache(CACHE_DIR)
    print(f"   ✅ FastF1 Cache enabled at: {os.path.abspath(CACHE_DIR)}")

    for year in range(start_year, end_year + 1):
        preprocess_static_data(year)

    print("\n🎉 Pre-processing of Static Data completed!")


if __name__ == "__main__":
    preprocess_all_static_data(2026, 2026)
import os
import fastf1
from fastf1.ergast import Ergast
import pandas as pd
from utils.data_utils import get_path, save_json, apply_data_patches, ensure_directory_exists


OUTPUT_DIR = get_path("data_cache", "static")
CACHE_DIR = get_path("data", "fastf1_cache")


def clean_and_convert_df(df: pd.DataFrame, year: int) -> list:
    if df is None or df.empty:
        return []
    df = apply_data_patches(df, year)

    return df.astype(str).to_dict('records')


def preprocess_static_data(year: int):
    api = Ergast()
    print(f"\n--- 🛠️ Processing static data for season {year} ---")

    print(f"   ⏳ Fetching drivers & mapping teams...")
    drivers_collection = api.get_driver_standings(season=year)
    drivers_df = drivers_collection.content[0] if drivers_collection and drivers_collection.content else None

    team_drivers_map = {}
    drivers_data = []

    if drivers_df is not None and not drivers_df.empty:
        base_cols = [
            'driverId', 'driverCode', 'code', 'driverNumber',
            'givenName', 'familyName', 'dateOfBirth',
            'driverNationality', 'url', 'constructorNames', 'constructorIds'
        ]
        cols = [col for col in base_cols if col in drivers_df.columns]

        drivers_static_df = drivers_df[cols].drop_duplicates(subset=['driverId'])
        drivers_data = clean_and_convert_df(drivers_static_df, year)
        patched_drivers = apply_data_patches(drivers_df, year)

        for _, row in patched_drivers.iterrows():
            mini_driver = {
                "driverId": str(row.get('driverId')),
                "code": str(row.get('code') or row.get('driverCode') or "UNK"),
                "driverNumber": str(row.get('driverNumber')),
                "dateOfBirth": str(row.get('dateOfBirth')),
                "givenName": str(row.get('givenName')),
                "familyName": str(row.get('familyName')),
                "nationality": str(row.get('driverNationality'))
            }

            c_ids = row.get('constructorIds')
            ids_list = []
            if isinstance(c_ids, list):
                ids_list = c_ids
            elif isinstance(c_ids, str):
                ids_list = [x.strip() for x in
                            c_ids.replace("[", "").replace("]", "").replace("'", "").replace('"', "").split(',')]

            for team_id in ids_list:
                if team_id:
                    if team_id not in team_drivers_map:
                        team_drivers_map[team_id] = []

                    if not any(d['driverId'] == mini_driver['driverId'] for d in team_drivers_map[team_id]):
                        team_drivers_map[team_id].append(mini_driver)
    else:
        print(f"   ⚠️ No driver data found for {year}.")

    print(f"   ⏳ Fetching constructors...")
    constructors_collection = api.get_constructor_standings(season=year)
    constructors_df = constructors_collection.content[
        0] if constructors_collection and constructors_collection.content else None

    constructors_data = []
    if constructors_df is not None and not constructors_df.empty:
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


def preprocess_all_static_data(start_year=2022, end_year=2025):
    ensure_directory_exists(OUTPUT_DIR)
    ensure_directory_exists(CACHE_DIR)
    fastf1.Cache.enable_cache(CACHE_DIR)
    print(f"   ✅ FastF1 Cache enabled at: {os.path.abspath(CACHE_DIR)}")

    for year in range(start_year, end_year + 1):
        preprocess_static_data(year)

    print("\n🎉 Pre-processing of Static Data completed!")


if __name__ == "__main__":
    preprocess_all_static_data(2022, 2025)
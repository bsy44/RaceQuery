import os
import fastf1
from fastf1.ergast import Ergast
import pandas as pd
from utils.data_utils import ensure_directory_exists, save_json, apply_data_patches


SCRIPT_DIR = os.path.dirname(os.path.abspath(__file__))
PROJECT_ROOT = os.path.abspath(os.path.join(SCRIPT_DIR, ".."))
OUTPUT_DIR = os.path.join(PROJECT_ROOT, "data_cache", "ergast")
FASTF1_CACHE_DIR = os.path.join(PROJECT_ROOT, "data", "fastf1_cache")


def clean_and_convert_df(df: pd.DataFrame, year: int) -> list:
    if df is None or df.empty:
        return []
    df = apply_data_patches(df, year)

    return df.astype(str).to_dict('records')


def preprocess_season_ergast(year: int):
    api = Ergast()
    print(f"\n=== 📥 Processing Ergast data for {year} ===")

    try:
        schedule = fastf1.get_event_schedule(year, include_testing=False)
        schedule = schedule[schedule['EventName'].notna()]

        rounds = schedule['RoundNumber'].tolist()
        save_json(OUTPUT_DIR, year, f"{year}_schedule.json", [], subfolder=None)

    except Exception as e:
        print(f"❌ Error getting schedule: {e}")
        return

    print(f"   ⏳ Processing Driver Standings...")
    last_valid_standings = []
    for r in rounds:
        try:
            s = api.get_driver_standings(season=year, round=r)
            df = s.content[0] if s.content else None

            data = clean_and_convert_df(df, year)

            if not data: break
            save_json(OUTPUT_DIR, year, f"{year}_R{r}_driver_standings.json", data, "driver")
            last_valid_standings = data
        except:
            pass

    if last_valid_standings:
        df_final = pd.DataFrame(last_valid_standings)
        df_final = apply_data_patches(df_final, year)
        final = {"season": year, "standings": df_final.astype(str).to_dict('records')}
        save_json(OUTPUT_DIR, year, f"{year}_driver_standings.json", final, "driver")

    print(f"   ⏳ Downloading Results...")
    all_race = []
    for r in rounds:
        try:
            res = api.get_race_results(season=year, round=r)
            if res.content and not res.content[0].empty:
                df = res.content[0]
                df['round'] = r
                all_race.extend(clean_and_convert_df(df, year))
        except:
            pass

    if all_race:
        save_json(OUTPUT_DIR, year, f"{year}_race_results.json", all_race, "results")


def preprocess_all_ergast(start_year=2022, end_year=2026):
    ensure_directory_exists(OUTPUT_DIR)
    ensure_directory_exists(FASTF1_CACHE_DIR)
    fastf1.Cache.enable_cache(FASTF1_CACHE_DIR)

    for year in range(start_year, end_year + 1):
        preprocess_season_ergast(year)


if __name__ == "__main__":
    preprocess_all_ergast(2026, 2026)
import fastf1
import os
from utils.data_utils import ensure_directory_exists, load_json_as_df, save_json
from services.stats_service import calculate_stats_generic


SCRIPT_DIR = os.path.dirname(os.path.abspath(__file__))
PROJECT_ROOT = os.path.abspath(os.path.join(SCRIPT_DIR, ".."))
INPUT_DIR = os.path.join(PROJECT_ROOT, "data_cache", "ergast")
OUTPUT_DIR = os.path.join(PROJECT_ROOT, "data_cache", "services")
FASTF1_CACHE_DIR = os.path.join(PROJECT_ROOT, "data", "fastf1_cache")


def process_year(year):
    print(f"--- 🏁 Computing ALL STATS for {year} ---")

    try:
        schedule = fastf1.get_event_schedule(year, include_testing=False)
        schedule = schedule[schedule['EventName'].notna()].sort_values('RoundNumber')
    except Exception as e:
        print(f"   ❌ Error loading schedule: {e}")
        return

    race_df = load_json_as_df(INPUT_DIR, year, "results", f"{year}_race_results.json")
    quali_df = load_json_as_df(INPUT_DIR, year, "results", f"{year}_qualifying_results.json")
    sprint_df = load_json_as_df(INPUT_DIR, year, "results", f"{year}_sprint_results.json")

    if race_df.empty:
        print(f"   ⚠️ No race data found for {year}. Skipping.")
        return

    total_qualis_count = 0
    if not quali_df.empty and 'round' in quali_df.columns:
        total_qualis_count = quali_df['round'].nunique()

    d_standings = load_json_as_df(INPUT_DIR, year, "driver", f"{year}_driver_standings.json")
    if not d_standings.empty:
        driver_stats_list = []
        for _, row in d_standings.iterrows():
            d_id = row.get('driverId')
            if d_id:
                stats = calculate_stats_generic(
                    d_id, 'driverId', row, race_df, quali_df, sprint_df,
                    schedule, total_qualis_count, include_history=True
                )
                driver_stats_list.append(stats)

        if driver_stats_list:
            save_json(OUTPUT_DIR, year, f"{year}_driver_stats.json", driver_stats_list, "driver")

    t_standings = load_json_as_df(INPUT_DIR, year, "team", f"{year}_constructor_standings.json")
    if not t_standings.empty:
        team_stats_list = []
        for _, row in t_standings.iterrows():
            c_id = row.get('constructorId')
            if c_id:
                stats = calculate_stats_generic(
                    c_id, 'constructorId', row, race_df, quali_df, sprint_df,
                    schedule, total_qualis_count, include_history=False
                )
                team_stats_list.append(stats)

        if team_stats_list:
            save_json(OUTPUT_DIR, year, f"{year}_team_stats.json", team_stats_list, "team")


if __name__ == "__main__":
    ensure_directory_exists(OUTPUT_DIR)

    if FASTF1_CACHE_DIR:
        ensure_directory_exists(FASTF1_CACHE_DIR)
        fastf1.Cache.enable_cache(FASTF1_CACHE_DIR)
        print(f"   ✅ FastF1 Cache enabled at: {FASTF1_CACHE_DIR}")

    process_year(2024)
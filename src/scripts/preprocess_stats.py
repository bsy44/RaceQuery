import json
import os
import pandas as pd
import fastf1


INPUT_DIR = "data_cache/ergast"
OUTPUT_DIR = "data_cache/stats"
CACHE_DIR = 'data/fastf1_cache'


def ensure_directory_exists(directory_path):
    if not os.path.exists(directory_path):
        os.makedirs(directory_path, exist_ok=True)


def load_json_as_df(year, subfolder, filename):
    path = os.path.join(INPUT_DIR, str(year), subfolder, filename)

    if not os.path.exists(path):
        return pd.DataFrame()

    try:
        with open(path, "r", encoding="utf-8") as f:
            data = json.load(f)
            if isinstance(data, dict) and "standings" in data:
                return pd.DataFrame(data["standings"])
            elif isinstance(data, list):
                return pd.DataFrame(data)
            return pd.DataFrame()
    except Exception as e:
        print(f"   ⚠️ Error loading {filename}: {e}")
        return pd.DataFrame()


def save_json(year, filename, data, subfolder):
    target_dir = os.path.join(OUTPUT_DIR, subfolder)
    ensure_directory_exists(target_dir)

    path = os.path.join(target_dir, filename)
    with open(path, "w", encoding="utf-8") as f:
        json.dump(data, f, indent=2)
    print(f"✔ Saved {filename} in {subfolder}")


def safe_int(val):
    try:
        return int(float(val))
    except:
        return 0


def safe_float(val):
    try:
        return float(val)
    except:
        return 0.0


def get_positions_series(df, col_name='position'):
    if df.empty or col_name not in df.columns:
        return pd.Series(dtype='float64')
    return pd.to_numeric(df[col_name], errors='coerce')


def build_season_history(entity_id, id_column, race_df, schedule):
    history = {}

    entity_races = race_df[race_df[id_column] == entity_id] if not race_df.empty else pd.DataFrame()

    for _, event in schedule.iterrows():
        gp_name = event['EventName']
        round_num = event['RoundNumber']
        result_val = "-"

        if not entity_races.empty:
            match = entity_races[entity_races['round'].astype(str) == str(round_num)]
            if not match.empty:
                pos = match.iloc[0].get('position')
                if pos and str(pos).lower() != 'nan':
                    result_val = safe_int(pos)

        history[gp_name] = result_val

    return history


def calculate_stats_generic(entity_id, id_column, row_standing, race_df, quali_df, sprint_df, schedule,
                            include_history=True):
    races = race_df[race_df[id_column] == entity_id] if not race_df.empty else pd.DataFrame()
    qualis = quali_df[quali_df[id_column] == entity_id] if not quali_df.empty else pd.DataFrame()
    sprints = sprint_df[sprint_df[id_column] == entity_id] if not sprint_df.empty else pd.DataFrame()

    race_pos = get_positions_series(races, 'position')
    quali_pos = get_positions_series(qualis, 'position')
    sprint_pos = get_positions_series(sprints, 'position')
    sprint_grids = get_positions_series(sprints, 'grid')

    podiums = race_pos[race_pos.isin([1, 2, 3])].count()
    top10 = race_pos[race_pos <= 10].count()
    poles = quali_pos[quali_pos == 1].count()

    dnf = 0
    if not races.empty and 'status' in races.columns:
        finishing_statuses = ['Finished', '+1 Lap', '+2 Laps', '+3 Laps', '+4 Laps', '+5 Laps', '+6 Laps']
        dnf = races[~races['status'].astype(str).isin(finishing_statuses)].shape[0]

    sprint_wins = sprint_pos[sprint_pos == 1].count()
    sprint_podiums = sprint_pos[sprint_pos.isin([1, 2, 3])].count()
    sprint_poles = sprint_grids[sprint_grids == 1].count()

    avg_race = round(race_pos.mean(), 2) if not race_pos.empty else None
    avg_quali = round(quali_pos.mean(), 2) if not quali_pos.empty else None
    best_res = int(race_pos.min()) if not race_pos.dropna().empty else None

    result_dict = {
        id_column: entity_id,
        "position": safe_int(row_standing.get('position')),
        "points": safe_float(row_standing.get('points')),
        "wins": safe_int(row_standing.get('wins')),
        "stat_podiums": int(podiums),
        "stat_top10": int(top10),
        "stat_poles": int(poles),
        "stat_dnf": int(dnf),
        "stat_sprint_wins": int(sprint_wins),
        "stat_sprint_podiums": int(sprint_podiums),
        "stat_sprint_poles": int(sprint_poles),
        "stat_avg_race_position": avg_race,
        "stat_avg_qualifying_position": avg_quali,
        "stat_best_race_result": best_res
    }

    if include_history:
        result_dict["season_results_history"] = build_season_history(entity_id, id_column, race_df, schedule)

    return result_dict


def process_year(year):
    print(f"--- Computing ALL STATS for {year} ---")

    try:
        schedule = fastf1.get_event_schedule(year, include_testing=False)
        schedule = schedule[schedule['EventName'].notna()].sort_values('RoundNumber')
    except Exception as e:
        print(f"   ❌ Error loading schedule: {e}")
        return

    race_df = load_json_as_df(year, "results", f"{year}_race_results.json")
    quali_df = load_json_as_df(year, "results", f"{year}_qualifying_results.json")
    sprint_df = load_json_as_df(year, "results", f"{year}_sprint_results.json")

    d_standings = load_json_as_df(year, "driver", f"{year}_driver_standings.json")

    if not d_standings.empty:
        driver_stats_list = []
        for _, row in d_standings.iterrows():
            d_id = row.get('driverId')
            if d_id:
                stats = calculate_stats_generic(d_id, 'driverId', row, race_df, quali_df, sprint_df, schedule,
                                                include_history=True)
                driver_stats_list.append(stats)

        if driver_stats_list:
            save_json(year, f"{year}_driver_stats.json", driver_stats_list, "driver")
    else:
        print(f"   ⚠️ No driver standings found.")

    t_standings = load_json_as_df(year, "team", f"{year}_constructor_standings.json")

    if not t_standings.empty:
        team_stats_list = []
        for _, row in t_standings.iterrows():
            c_id = row.get('constructorId')
            if c_id:
                stats = calculate_stats_generic(c_id, 'constructorId', row, race_df, quali_df, sprint_df, schedule,
                                                include_history=False)
                team_stats_list.append(stats)

        if team_stats_list:
            save_json(year, f"{year}_team_stats.json", team_stats_list, "team")
    else:
        print(f"   ⚠️ No team standings found.")


if __name__ == "__main__":
    ensure_directory_exists(OUTPUT_DIR)
    ensure_directory_exists(CACHE_DIR)
    fastf1.Cache.enable_cache(CACHE_DIR)

    for y in range(2022, 2026):
        process_year(y)
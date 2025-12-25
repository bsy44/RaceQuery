import fastf1
from fastf1.ergast import Ergast
import pandas as pd
from utils.data_utils import get_path, save_json, apply_data_patches, ensure_directory_exists


OUTPUT_DIR = get_path("data_cache", "ergast")
CACHE_DIR = get_path("data", "fastf1_cache")


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

        print(f"   ⏳ Fetching official circuit names from Ergast...")
        circuit_map = {}
        try:
            ergast_cal = api.get_race_schedule(season=year)
            df_ergast = None

            if hasattr(ergast_cal, 'content') and ergast_cal.content:
                df_ergast = ergast_cal.content[0]
            elif hasattr(ergast_cal, 'data'):
                df_ergast = ergast_cal.data
            elif isinstance(ergast_cal, pd.DataFrame):
                df_ergast = ergast_cal

            if df_ergast is not None and not df_ergast.empty:
                for _, row in df_ergast.iterrows():
                    r_num = int(row['round'])
                    c_name = row.get('circuitName')
                    if c_name:
                        circuit_map[r_num] = c_name
        except Exception as e:
            print(f"   ⚠️ Could not fetch Ergast circuit names: {e}")

        rounds_info = {}
        formatted_schedule = []

        for _, row in schedule.iterrows():
            r_num = int(row['RoundNumber'])

            official_circuit_name = circuit_map.get(r_num, row['Location'])

            rounds_info[r_num] = {
                'gpName': row['EventName'],
                'country': row['Country'],
                'location': row['Location'],
                'circuitName': official_circuit_name
            }

            event_info = {
                "season": year,
                "round": r_num,
                "country": row['Country'],
                "location": row['Location'],
                "circuit_name": official_circuit_name,
                "official_name": row['OfficialEventName'],
                "short_name": row['EventName'],
                "event_format": row['EventFormat'],
                "event_date": str(row['EventDate']),
                "sessions": []
            }

            for i in range(1, 6):
                name_col, date_col, utc_col = f"Session{i}", f"Session{i}Date", f"Session{i}DateUtc"
                if name_col in row and row[name_col]:
                    event_info["sessions"].append({
                        "name": row[name_col],
                        "local_date": str(row.get(date_col)) if pd.notna(row.get(date_col)) else None,
                        "utc_date": str(row.get(utc_col)) if pd.notna(row.get(utc_col)) else None
                    })
            formatted_schedule.append(event_info)

        save_json(OUTPUT_DIR, year, f"{year}_schedule.json", formatted_schedule)
        rounds = list(rounds_info.keys())

    except Exception as e:
        print(f"❌ Error getting schedule: {e}")
        return

    print(f"   ⏳ Processing Driver Standings...")
    last_valid_drivers = []
    for r in rounds:
        try:
            s = api.get_driver_standings(season=year, round=r)
            df = s.content[0] if s.content else None
            if df is None or df.empty: break
            data = clean_and_convert_df(df, year)
            save_json(OUTPUT_DIR, year, f"{year}_R{r}_driver_standings.json", data, "driver")
            last_valid_drivers = data
        except:
            break

    if last_valid_drivers:
        final_drivers = {"season": year, "standings": last_valid_drivers}
        save_json(OUTPUT_DIR, year, f"{year}_driver_standings.json", final_drivers, "driver")

    print(f"   ⏳ Processing Constructor Standings...")
    last_valid_teams = []
    for r in rounds:
        try:
            s = api.get_constructor_standings(season=year, round=r)
            df = s.content[0] if s.content else None
            if df is None or df.empty: break
            data = clean_and_convert_df(df, year)
            save_json(OUTPUT_DIR, year, f"{year}_R{r}_constructor_standings.json", data, "team")
            last_valid_teams = data
        except:
            break

    if last_valid_teams:
        final_teams = {"season": year, "standings": last_valid_teams}
        save_json(OUTPUT_DIR, year, f"{year}_constructor_standings.json", final_teams, "team")

    print(f"   ⏳ Downloading Results (Race, Qualy, Sprint)...")
    all_race = []
    all_qualy = []
    all_sprint = []

    for r in rounds:
        meta = rounds_info.get(r, {'raceName': 'Unknown', 'country': 'Unknown'})

        try:
            res = api.get_race_results(season=year, round=r)
            if res.content and not res.content[0].empty:
                df = res.content[0]
                df['round'], df['raceName'], df['country'] = r, meta['raceName'], meta['country']
                all_race.extend(clean_and_convert_df(df, year))
        except:
            pass

        try:
            res_q = api.get_qualifying_results(season=year, round=r)
            if res_q.content and not res_q.content[0].empty:
                df_q = res_q.content[0]
                df_q['round'], df_q['raceName'], df_q['country'] = r, meta['raceName'], meta['country']
                all_qualy.extend(clean_and_convert_df(df_q, year))
        except:
            pass

        try:
            res_s = api.get_sprint_results(season=year, round=r)
            if res_s.content and not res_s.content[0].empty:
                df_s = res_s.content[0]
                df_s['round'], df_s['raceName'], df_s['country'] = r, meta['raceName'], meta['country']
                all_sprint.extend(clean_and_convert_df(df_s, year))
        except:
            pass

        print(f"      Processed R{r}", end='\r')

    if all_race:
        save_json(OUTPUT_DIR, year, f"{year}_race_results.json", all_race, "results")
    if all_qualy:
        save_json(OUTPUT_DIR, year, f"{year}_qualifying_results.json", all_qualy, "results")
    if all_sprint:
        save_json(OUTPUT_DIR, year, f"{year}_sprint_results.json", all_sprint, "results")


def preprocess_all_ergast(start_year=2022, end_year=2025):
    ensure_directory_exists(OUTPUT_DIR)
    ensure_directory_exists(CACHE_DIR)
    fastf1.Cache.enable_cache(CACHE_DIR)

    for year in range(start_year, end_year + 1):
        preprocess_season_ergast(year)


if __name__ == "__main__":
    preprocess_all_ergast(2022, 2025)
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

        print(f"   ⏳ Fetching official circuit names...")
        circuit_map = {}
        try:
            ergast_cal = api.get_race_schedule(season=year)
            df_ergast = None
            if hasattr(ergast_cal, 'content') and ergast_cal.content:
                df_ergast = ergast_cal.content[0]

            if df_ergast is not None and not df_ergast.empty:
                for _, row in df_ergast.iterrows():
                    r_num = int(row['round'])
                    c_name = row.get('circuitName')
                    if c_name: circuit_map[r_num] = c_name
        except Exception as e:
            print(f"   ⚠️ Could not fetch Ergast circuit names: {e}")

        rounds_info = {}
        formatted_schedule = []

        for _, row in schedule.iterrows():
            r_num = int(row['RoundNumber'])
            rounds_info[r_num] = {'raceName': row['EventName'], 'country': row['Country']}
            official_circuit_name = circuit_map.get(r_num, row['Location'])

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
                        "local_date": str(row[date_col]) if pd.notna(row[date_col]) else None,
                        "utc_date": str(row[utc_col]) if utc_col in row and pd.notna(row[utc_col]) else None
                    })
            formatted_schedule.append(event_info)

        rounds = list(rounds_info.keys())
        save_json(OUTPUT_DIR, year, f"{year}_schedule.json", formatted_schedule)

    except Exception as e:
        print(f"❌ Error getting schedule: {e}")
        return

    print(f"   ⏳ Processing Driver Standings...")
    last_valid_standings = []
    for r in rounds:
        try:
            s = api.get_driver_standings(season=year, round=r)
            df = s.content[0] if s.content else None
            if df is None or df.empty: break
            data = clean_and_convert_df(df, year)
            save_json(OUTPUT_DIR, year, f"{year}_R{r}_driver_standings.json", data, "driver")
            last_valid_standings = data
        except:
            pass

    if last_valid_standings:
        final = {"season": year, "standings": last_valid_standings}
        save_json(OUTPUT_DIR, year, f"{year}_driver_standings.json", final, "driver")

    print(f"   ⏳ Downloading Results...")
    all_race, all_quali, all_sprint = [], [], []
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
        print(f"      Processed R{r}", end='\r')

    if all_race: save_json(OUTPUT_DIR, year, f"{year}_race_results.json", all_race, "results")


def preprocess_all_ergast(start_year=2022, end_year=2025):
    ensure_directory_exists(OUTPUT_DIR)
    ensure_directory_exists(CACHE_DIR)
    fastf1.Cache.enable_cache(CACHE_DIR)

    for year in range(start_year, end_year + 1):
        preprocess_season_ergast(year)


if __name__ == "__main__":
    preprocess_all_ergast(2025, 2025)
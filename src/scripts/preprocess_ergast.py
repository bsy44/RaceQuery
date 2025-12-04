import json
import os
import fastf1
from fastf1.ergast import Ergast
import pandas as pd


OUTPUT_DIR = "../data_cache/ergast"
CACHE_DIR = '../data/fastf1_cache'


def ensure_directory_exists(directory_path):
    if not os.path.exists(directory_path):
        os.makedirs(directory_path, exist_ok=True)


def get_output_dir_for_year(year: int):
    year_dir = os.path.join(OUTPUT_DIR, str(year))
    ensure_directory_exists(year_dir)
    return year_dir


def save_json(year: int, filename: str, data: dict, subfolder=None):
    base_dir = get_output_dir_for_year(year)

    if subfolder:
        target_dir = os.path.join(base_dir, subfolder)
        ensure_directory_exists(target_dir)
    else:
        target_dir = base_dir

    path = os.path.join(target_dir, filename)
    with open(path, "w", encoding="utf-8") as f:
        json.dump(data, f, indent=2)
    print(f"✔ Saved {filename} in {subfolder if subfolder else 'root'}")


def clean_and_convert_df(df: pd.DataFrame) -> list:
    if df is None or df.empty: return []
    return df.astype(str).to_dict('records')


def preprocess_season_ergast(year: int):
    api = Ergast()
    print(f"\n=== Processing Ergast data for {year} ===")


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
                name_col = f"Session{i}"
                date_col = f"Session{i}Date"
                utc_col = f"Session{i}DateUtc"

                if name_col in row and row[name_col]:
                    local_date = str(row[date_col]) if pd.notna(row[date_col]) else None
                    utc_date = str(row[utc_col]) if utc_col in row and pd.notna(row[utc_col]) else None

                    event_info["sessions"].append({
                        "name": row[name_col],
                        "local_date": local_date,
                        "utc_date": utc_date
                    })

            formatted_schedule.append(event_info)

        rounds = list(rounds_info.keys())
        print(f"   ℹ️ Found {len(rounds)} rounds.")

        save_json(year, f"{year}_schedule.json", formatted_schedule)

    except Exception as e:
        print(f"❌ Error getting schedule: {e}")
        return

    print(f"   ⏳ Processing Driver Standings...")
    last_valid_standings = []
    last_round = 0
    for r in rounds:
        try:
            s = api.get_driver_standings(season=year, round=r)
            df = s.content[0] if s.content else None
            if df is None or df.empty: break
            data = clean_and_convert_df(df)
            save_json(year, f"{year}_R{r}_driver_standings.json", data, "driver")
            last_valid_standings = data
            last_round = r
        except:
            pass

    if last_valid_standings:
        final = {"season": year, "round": last_round, "standings": last_valid_standings}
        save_json(year, f"{year}_driver_standings.json", final, "driver")

    print(f"   ⏳ Processing Constructor Standings...")
    last_valid_team = []
    last_team_round = 0
    for r in rounds:
        try:
            s = api.get_constructor_standings(season=year, round=r)
            df = s.content[0] if s.content else None
            if df is None or df.empty: break
            data = clean_and_convert_df(df)
            save_json(year, f"{year}_R{r}_constructor_standings.json", data, "team")
            last_valid_team = data
            last_team_round = r
        except:
            pass

    if last_valid_team:
        final = {"season": year, "round": last_team_round, "standings": last_valid_team}
        save_json(year, f"{year}_constructor_standings.json", final, "team")

    # 4. Results
    print(f"   ⏳ Downloading Results...")
    all_race, all_quali, all_sprint = [], [], []
    for r in rounds:
        meta = rounds_info.get(r, {'raceName': 'Unknown', 'country': 'Unknown'})
        try:
            res = api.get_race_results(season=year, round=r)
            if res.content and not res.content[0].empty:
                df = res.content[0]
                df['round'] = r
                df['raceName'] = meta['raceName']
                df['country'] = meta['country']
                all_race.extend(clean_and_convert_df(df))
        except:
            pass
        try:
            res = api.get_qualifying_results(season=year, round=r)
            if res.content and not res.content[0].empty:
                df = res.content[0]
                df['round'] = r
                df['raceName'] = meta['raceName']
                df['country'] = meta['country']
                all_quali.extend(clean_and_convert_df(df))
        except:
            pass
        try:
            res = api.get_sprint_results(season=year, round=r)
            if res.content and not res.content[0].empty:
                df = res.content[0]
                df['round'] = r
                df['raceName'] = meta['raceName']
                df['country'] = meta['country']
                all_sprint.extend(clean_and_convert_df(df))
        except:
            pass
        print(f"      Processed R{r}", end='\r')

    if all_race: save_json(year, f"{year}_race_results.json", all_race, "results")
    if all_quali: save_json(year, f"{year}_qualifying_results.json", all_quali, "results")
    if all_sprint:
        save_json(year, f"{year}_sprint_results.json", all_sprint, "results")
    else:
        save_json(year, f"{year}_sprint_results.json", [], "results")
def preprocess_all_ergast(start_year=2022, end_year=2025):
    ensure_directory_exists(OUTPUT_DIR)
    ensure_directory_exists(CACHE_DIR)
    fastf1.Cache.enable_cache(CACHE_DIR)

    for year in range(start_year, end_year + 1):
        preprocess_season_ergast(year)

    print("\n🎉 Pré-processing Ergast terminé avec succès !")


if __name__ == "__main__":
    preprocess_all_ergast(2022, 2025)
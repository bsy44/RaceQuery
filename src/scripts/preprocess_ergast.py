import json
import os
from fastf1.ergast import Ergast
import pandas as pd


OUTPUT_DIR = "../data_cache/ergast_preprocessed"


def ensure_output_directory():
    if not os.path.exists(OUTPUT_DIR):
        os.makedirs(OUTPUT_DIR)


def save_json(filename, data):
    path = os.path.join(OUTPUT_DIR, filename)
    with open(path, "w", encoding="utf-8") as f:
        json.dump(data, f, indent=2)
    print(f"✔ Saved {filename}")


def preprocess_season(season: int):
    api = Ergast()

    def clean_and_convert_df(df: pd.DataFrame) -> list:
        if df is None or df.empty:
            return []

        df_str = df.astype(str)

        return df_str.to_dict('records')

    race_results_collection = api.get_race_results(season=season)
    results_list_of_df = race_results_collection.content

    race_results_data = []
    for race_result_df in results_list_of_df:
        race_results_data.extend(clean_and_convert_df(race_result_df))

    standings_collection = api.get_driver_standings(season=season)
    standings_df = standings_collection.content[0] \
        if standings_collection and standings_collection.content else None
    standings_data = clean_and_convert_df(standings_df)

    constructors_collection = api.get_constructor_standings(season=season)
    constructors_df = constructors_collection.content[0] \
        if constructors_collection and constructors_collection.content else None
    constructors_data = clean_and_convert_df(constructors_df)

    save_json(f"{season}_race_results.json", race_results_data)
    save_json(f"{season}_driver_standings.json", standings_data)
    save_json(f"{season}_constructor_standings.json", constructors_data)


def preprocess_all(start_year=2022, end_year=2025):
    ensure_output_directory()
    pd.set_option('display.max_columns', None)

    for year in range(start_year, end_year + 1):
        print(f"--- Processing season {year} ---")
        preprocess_season(year)

    print("\n Pré-processing Ergast terminé avec succès !")


if __name__ == "__main__":
    preprocess_all(2022, 2025)
import json
import os
import fastf1
import pandas as pd
from fastf1.ergast import Ergast

# 🎯 Chemins
OUTPUT_DIR = "../data_cache/static"
CACHE_DIR = '../data/fastf1_cache'


def ensure_directory_exists(directory_path):
    if not os.path.exists(directory_path):
        os.makedirs(directory_path, exist_ok=True)
        print(f"   📂 Created directory: {directory_path}")


def save_json(filename, data):
    path = os.path.join(OUTPUT_DIR, filename)
    absolute_path = os.path.abspath(path)
    print(f"   📂 Attempting to save to: {absolute_path}")
    with open(path, "w", encoding="utf-8") as f:
        json.dump(data, f, indent=2)
    print(f"✔ Saved {filename}")


def clean_and_convert_df(df: pd.DataFrame) -> list:
    if df is None or df.empty:
        return []
    # Convertit tout en string pour éviter les problèmes de sérialisation
    df_str = df.astype(str)
    return df_str.to_dict('records')


def preprocess_static_data(year: int):
    api = Ergast()

    print(f"   ⏳ Fetching drivers for {year}...")

    # On utilise les standings car c'est le moyen le plus fiable d'avoir les pilotes DE LA SAISON
    drivers_collection = api.get_driver_standings(season=year)
    drivers_df = drivers_collection.content[0] if drivers_collection and drivers_collection.content else None

    if drivers_df is not None and not drivers_df.empty:

        # 💡 CORRECTION DES NOMS DE COLONNES
        # Voici les colonnes généralement renvoyées par FastF1 pour les standings
        base_driver_info = [
            'driverId',
            'driverCode',
            'driverNumber',
            'givenName',
            'familyName',
            'dateOfBirth',
            'driverNationality',
            'url',
            'constructorNames',
            'constructorIds'
        ]

        # On ne garde que les colonnes qui existent vraiment dans le DataFrame reçu
        driver_info_cols = [col for col in base_driver_info if col in drivers_df.columns]

        # On déduplique sur driverId pour avoir une liste unique de pilotes
        drivers_static_df = drivers_df[driver_info_cols].drop_duplicates(subset=['driverId'])

        drivers_data = clean_and_convert_df(drivers_static_df)
    else:
        drivers_data = []
        print(f"   ⚠️ No driver data found for {year}.")

    print(f"   ⏳ Fetching constructors for {year}...")
    constructors_collection = api.get_constructor_standings(season=year)
    constructors_df = constructors_collection.content[
        0] if constructors_collection and constructors_collection.content else None

    if constructors_df is not None and not constructors_df.empty:
        constructors_data = clean_and_convert_df(constructors_df)
    else:
        constructors_data = []
        print(f"   ⚠️ No constructor data found for {year}.")

    if drivers_data:
        save_json(f"{year}_drivers.json", drivers_data)
    if constructors_data:
        save_json(f"{year}_constructors.json", constructors_data)


def preprocess_all_static_data(start_year=2022, end_year=2025):
    ensure_directory_exists(CACHE_DIR)
    ensure_directory_exists(OUTPUT_DIR)

    fastf1.Cache.enable_cache(CACHE_DIR)
    print(f"   ✅ FastF1 Cache enabled at: {os.path.abspath(CACHE_DIR)}")

    for year in range(start_year, end_year + 1):
        print(f"\n--- Processing static data for season {year} ---")
        preprocess_static_data(year)

    print("\n🎉 Pré-processing Pilotes/Écuries terminé avec succès !")


if __name__ == "__main__":
    preprocess_all_static_data(2022, 2025)
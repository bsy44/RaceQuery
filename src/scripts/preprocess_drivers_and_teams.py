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
    df_str = df.astype(str)
    return df_str.to_dict('records')


def preprocess_static_data(year: int):
    api = Ergast()

    print(f"   ⏳ Fetching drivers & mapping teams for {year}...")

    # 1. RÉCUPÉRATION DES PILOTES
    drivers_collection = api.get_driver_standings(season=year)
    drivers_df = drivers_collection.content[0] if drivers_collection and drivers_collection.content else None

    # Dictionnaire pour mapper : constructorId -> [Liste de Pilotes]
    team_drivers_map = {}
    drivers_data = []

    if drivers_df is not None and not drivers_df.empty:
        # Colonnes à garder pour le fichier drivers.json
        base_driver_info = [
            'driverId', 'driverCode', 'code', 'driverNumber',
            'givenName', 'familyName', 'dateOfBirth',
            'driverNationality', 'url',
            'constructorNames', 'constructorIds'
        ]
        driver_info_cols = [col for col in base_driver_info if col in drivers_df.columns]

        # Sauvegarde pour le fichier drivers.json
        drivers_static_df = drivers_df[driver_info_cols].drop_duplicates(subset=['driverId'])
        drivers_data = clean_and_convert_df(drivers_static_df)

        # --- LOGIQUE DE MAPPING PILOTES -> ÉQUIPES ---
        for _, row in drivers_df.iterrows():
            # Création d'un petit objet pilote résumé pour l'inclure dans l'équipe
            mini_driver = {
                "driverId": str(row.get('driverId')),
                "code": str(row.get('code') or row.get('driverCode') or "UNK"),
                "driverNumber": str(row.get('driverNumber')),
                "dateOfBirth": str(row.get('dateOfBirth')),
                "givenName": str(row.get('givenName')),
                "familyName": str(row.get('familyName')),
                "nationality": str(row.get('driverNationality'))
            }

            # Récupération des IDs d'équipe (parfois une liste, parfois une string)
            c_ids = row.get('constructorIds')

            # Nettoyage des IDs (FastF1 renvoie parfois "['red_bull', 'torro_rosso']")
            ids_list = []
            if isinstance(c_ids, list):
                ids_list = c_ids
            elif isinstance(c_ids, str):
                # Nettoyage barbare mais efficace des chaînes python-like
                clean = c_ids.replace("[", "").replace("]", "").replace("'", "").replace('"', "")
                ids_list = [x.strip() for x in clean.split(',')]

            # Ajout du pilote à chaque équipe pour laquelle il a conduit
            for team_id in ids_list:
                if team_id:
                    if team_id not in team_drivers_map:
                        team_drivers_map[team_id] = []

                    # On évite les doublons si le pilote apparaît plusieurs fois
                    already_in = any(d['driverId'] == mini_driver['driverId'] for d in team_drivers_map[team_id])
                    if not already_in:
                        team_drivers_map[team_id].append(mini_driver)

    else:
        print(f"   ⚠️ No driver data found for {year}.")

    # 2. RÉCUPÉRATION DES CONSTRUCTEURS
    print(f"   ⏳ Fetching constructors for {year}...")
    constructors_collection = api.get_constructor_standings(season=year)
    constructors_df = constructors_collection.content[
        0] if constructors_collection and constructors_collection.content else None

    if constructors_df is not None and not constructors_df.empty:
        constructors_data = clean_and_convert_df(constructors_df)

        # 💡 INJECTION DES PILOTES DANS L'OBJET CONSTRUCTEUR
        for team in constructors_data:
            c_id = team.get('constructorId')
            # On récupère la liste depuis notre map, ou vide si personne
            team_drivers = team_drivers_map.get(c_id, [])
            team['drivers'] = team_drivers

    else:
        constructors_data = []
        print(f"   ⚠️ No constructor data found for {year}.")

    # 3. SAUVEGARDE
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
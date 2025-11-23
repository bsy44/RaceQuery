import json
import os
import fastf1
from fastf1.ergast import Ergast
import pandas as pd

# 🎯 Chemins
OUTPUT_DIR = "../data_cache/ergast"
CACHE_DIR = '../data/fastf1_cache'


def ensure_directory_exists(directory_path):
    if not os.path.exists(directory_path):
        os.makedirs(directory_path, exist_ok=True)


def get_output_dir_for_year(year: int):
    year_dir = os.path.join(OUTPUT_DIR, str(year))
    ensure_directory_exists(year_dir)
    return year_dir


def save_json(year: int, filename: str, data: dict):
    output_dir = get_output_dir_for_year(year)
    path = os.path.join(output_dir, filename)
    with open(path, "w", encoding="utf-8") as f:
        json.dump(data, f, indent=2)
    print(f"✔ Saved {filename}")


def clean_and_convert_df(df: pd.DataFrame) -> list:
    if df is None or df.empty:
        return []
    return df.astype(str).to_dict('records')


# Dans src/scripts/preprocess_ergast.py

def preprocess_season_ergast(year: int):
    api = Ergast()
    print(f"\n=== Processing Ergast data for {year} ===")

    # 1. RECUPERATION DU CALENDRIER
    # On crée un dictionnaire pour mapper {round: {name, country}}
    try:
        schedule = fastf1.get_event_schedule(year, include_testing=False)
        # On nettoie le calendrier
        schedule = schedule[schedule['EventName'].notna()]

        # Création du mapping
        rounds_info = {}
        for _, row in schedule.iterrows():
            r_num = int(row['RoundNumber'])
            rounds_info[r_num] = {
                'raceName': row['EventName'],
                'country': row['Country']
            }

        rounds = list(rounds_info.keys())
        print(f"   ℹ️ Found {len(rounds)} rounds with metadata.")

    except Exception as e:
        print(f"❌ Error getting schedule for {year}: {e}")
        return

    # ... (PARTIE 2: STANDINGS - Inchangée) ...
    # ... (PARTIE 3: CONSTRUCTEURS - Inchangée) ...

    # ---------------------------------------------------------
    # 4. RESULTATS DÉTAILLÉS (Avec Injection des Noms)
    # ---------------------------------------------------------

    all_race_results = []
    all_quali_results = []
    all_sprint_results = []

    print(f"   ⏳ Downloading Results (Round by Round)...")

    for round_num in rounds:
        # Récupérer les infos du round courant
        meta = rounds_info.get(round_num, {'raceName': 'Unknown', 'country': 'Unknown'})

        # --- COURSE ---
        try:
            res = api.get_race_results(season=year, round=round_num)
            if res.content and not res.content[0].empty:
                df = res.content[0]
                # 💡 INJECTION DES DONNÉES MANQUANTES
                df['round'] = round_num
                df['raceName'] = meta['raceName']
                df['country'] = meta['country']

                all_race_results.extend(clean_and_convert_df(df))
        except:
            pass

        # --- QUALIFS ---
        try:
            res = api.get_qualifying_results(season=year, round=round_num)
            if res.content and not res.content[0].empty:
                df = res.content[0]
                df['round'] = round_num
                df['raceName'] = meta['raceName']  # Utile aussi pour les qualifs
                df['country'] = meta['country']

                all_quali_results.extend(clean_and_convert_df(df))
        except:
            pass

        # --- SPRINTS ---
        try:
            res = api.get_sprint_results(season=year, round=round_num)
            if res.content and not res.content[0].empty:
                df = res.content[0]
                df['round'] = round_num
                df['raceName'] = meta['raceName']
                df['country'] = meta['country']

                all_sprint_results.extend(clean_and_convert_df(df))
        except:
            pass

        print(f"      Processed R{round_num} - {meta['raceName']}", end='\r')

    print(f"\n   ✅ Compiled {len(all_race_results)} race entries.")

    # SAUVEGARDE
    if all_race_results:
        save_json(year, f"{year}_race_results.json", all_race_results)
    if all_quali_results:
        save_json(year, f"{year}_qualifying_results.json", all_quali_results)
    if all_sprint_results:
        save_json(year, f"{year}_sprint_results.json", all_sprint_results)
    else:
        save_json(year, f"{year}_sprint_results.json", [])


def preprocess_all_ergast(start_year=2022, end_year=2025):
    ensure_directory_exists(OUTPUT_DIR)
    ensure_directory_exists(CACHE_DIR)
    fastf1.Cache.enable_cache(CACHE_DIR)

    for year in range(start_year, end_year + 1):
        preprocess_season_ergast(year)

    print("\n🎉 Pré-processing Ergast terminé avec succès !")


if __name__ == "__main__":
    preprocess_all_ergast(2022, 2025)
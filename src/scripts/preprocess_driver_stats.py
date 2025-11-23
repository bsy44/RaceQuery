import json
import os
import pandas as pd
import numpy as np
import fastf1  # Nécessaire pour le calendrier

# 🎯 Chemins
INPUT_DIR = "../data_cache/ergast"
OUTPUT_DIR = "../data_cache/stats"
CACHE_DIR = '../data/fastf1_cache'  # Pour le cache fastf1 du calendrier


def ensure_directory_exists(directory_path):
    if not os.path.exists(directory_path):
        os.makedirs(directory_path, exist_ok=True)
        print(f"   📂 Created directory: {directory_path}")


# ... (Les fonctions load_json_as_df, save_json, safe_int, safe_float, get_positions_series restent inchangées) ...
def load_json_as_df(year, filename):
    path = os.path.join(INPUT_DIR, str(year), filename)
    if not os.path.exists(path): return pd.DataFrame()
    try:
        with open(path, "r", encoding="utf-8") as f:
            data = json.load(f)
            if isinstance(data, dict) and "standings" in data:
                return pd.DataFrame(data["standings"])
            elif isinstance(data, list):
                return pd.DataFrame(data)
            return pd.DataFrame()
    except:
        return pd.DataFrame()


def save_json(year, data):
    path = os.path.join(OUTPUT_DIR, f"{year}_driver_stats.json")
    with open(path, "w", encoding="utf-8") as f:
        json.dump(data, f, indent=2)
    print(f"✔ Saved stats for {year}")


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
    if df.empty or col_name not in df.columns: return pd.Series(dtype='float64')
    return pd.to_numeric(df[col_name], errors='coerce')


# --- NOUVELLE FONCTION ---
def build_season_history(driver_id, race_df, schedule):
    """
    Construit l'historique complet (Passé + Futur) pour un pilote.
    Retourne un dictionnaire { "Bahrain GP": 1, "Saudi GP": "-", ... }
    """
    history = {}

    # Filtrer les résultats du pilote pour l'année
    driver_races = race_df[race_df['driverId'] == driver_id] if not race_df.empty else pd.DataFrame()

    # On parcourt le calendrier officiel pour garder l'ordre chronologique
    for _, event in schedule.iterrows():
        gp_name = event['EventName']
        round_num = event['RoundNumber']

        # Valeur par défaut
        result_val = "-"

        # Si on a des résultats pour ce pilote
        if not driver_races.empty:
            # On cherche le résultat correspondant au numéro de round
            # (C'est plus fiable que le nom)
            # Note: race_df['round'] est souvent en string dans le JSON, RoundNumber est int
            match = driver_races[driver_races['round'].astype(str) == str(round_num)]

            if not match.empty:
                pos = match.iloc[0].get('position')
                # Si la position est valide (pas 'nan')
                if pos and str(pos).lower() != 'nan':
                    result_val = safe_int(pos)
                else:
                    # Optionnel: Mettre "DNF" si status != Finished ?
                    # Pour l'instant on laisse '-' ou on peut mettre "NC"
                    result_val = "-"

        history[gp_name] = result_val

    return history


def calculate_driver_stats(driver_id, row_standing, race_df, quali_df, sprint_df, schedule):
    # (Le début reste inchangé : filtrage des DataFrames...)
    races = race_df[
        race_df['driverId'] == driver_id] if not race_df.empty and 'driverId' in race_df.columns else pd.DataFrame()
    qualis = quali_df[
        quali_df['driverId'] == driver_id] if not quali_df.empty and 'driverId' in quali_df.columns else pd.DataFrame()
    sprints = sprint_df[sprint_df[
                            'driverId'] == driver_id] if not sprint_df.empty and 'driverId' in sprint_df.columns else pd.DataFrame()

    race_positions = get_positions_series(races, 'position')
    quali_positions = get_positions_series(qualis, 'position')
    sprint_positions = get_positions_series(sprints, 'position')
    sprint_grids = get_positions_series(sprints, 'grid')

    # ... (Tous les calculs : podiums, top10, etc. restent identiques) ...
    podiums = race_positions[race_positions.isin([1, 2, 3])].count()
    top10 = race_positions[race_positions <= 10].count()
    wins = race_positions[race_positions == 1].count()
    poles = quali_positions[quali_positions == 1].count()

    dnf = 0
    if not races.empty and 'status' in races.columns:
        finishing_statuses = ['Finished', '+1 Lap', '+2 Laps', '+3 Laps', '+4 Laps', '+5 Laps', '+6 Laps']
        dnf = races[~races['status'].astype(str).isin(finishing_statuses)].shape[0]

    sprint_wins = sprint_positions[sprint_positions == 1].count()
    sprint_podiums = sprint_positions[sprint_positions.isin([1, 2, 3])].count()
    sprint_poles = sprint_grids[sprint_grids == 1].count()

    avg_race = round(race_positions.mean(), 2) if not race_positions.empty else None
    avg_quali = round(quali_positions.mean(), 2) if not quali_positions.empty else None
    best_res = int(race_positions.min()) if not race_positions.dropna().empty else None

    # 💡 NOUVEAU : Générer l'historique complet ici
    season_history = build_season_history(driver_id, race_df, schedule)

    return {
        "driverId": driver_id,
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
        "stat_best_race_result": best_res,
        # On ajoute l'objet complet ici
        "season_results_history": season_history
    }


def process_year(year):
    print(f"--- Computing stats for {year} ---")

    # 1. Charger le Calendrier (Nécessaire pour l'ordre et les futurs GPs)
    try:
        schedule = fastf1.get_event_schedule(year, include_testing=False)
        schedule = schedule[schedule['EventName'].notna()].sort_values('RoundNumber')
    except Exception as e:
        print(f"   ❌ Error loading schedule: {e}")
        return

    standings_df = load_json_as_df(year, f"{year}_driver_standings.json")
    race_df = load_json_as_df(year, f"{year}_race_results.json")
    quali_df = load_json_as_df(year, f"{year}_qualifying_results.json")
    sprint_df = load_json_as_df(year, f"{year}_sprint_results.json")

    if standings_df.empty:
        print(f"   ⚠️ No standings found for {year}, skipping.")
        return

    stats_collection = []

    for _, row in standings_df.iterrows():
        driver_id = row.get('driverId')
        if not driver_id: continue

        # On passe le 'schedule' en plus
        driver_stats = calculate_driver_stats(driver_id, row, race_df, quali_df, sprint_df, schedule)
        stats_collection.append(driver_stats)

    if stats_collection:
        save_json(year, stats_collection)
    else:
        print(f"   ⚠️ No stats calculated for {year}.")


if __name__ == "__main__":
    ensure_directory_exists(OUTPUT_DIR)
    # Configuration du cache FastF1 pour le chargement du calendrier
    ensure_directory_exists(CACHE_DIR)
    fastf1.Cache.enable_cache(CACHE_DIR)

    for y in range(2022, 2026):
        process_year(y)
import fastf1
from fastf1.ergast import Ergast
import pandas as pd
from utils.data_utils import get_path, save_json, ensure_directory_exists
from services import ergast_service

OUTPUT_DIR = get_path("data_cache", "ergast")
CACHE_DIR = get_path("data", "fastf1_cache")


def preprocess_season_ergast(year: int):
    """
    Ingestion complète des données Ergast pour une saison donnée.
    Gère le calendrier, l'évolution des classements et les résultats de sessions.
    """
    api = Ergast(result_type='pandas')
    print(f"\n=== 📥 Ingestion des données Ergast pour {year} ===")

    # 1. CALENDRIER ET CARTE DES CIRCUITS
    try:
        schedule_resp = fastf1.get_event_schedule(year, include_testing=False)
        schedule = schedule_resp[schedule_resp['EventName'].notna()]

        print(f"   ⏳ Récupération de la carte des circuits...")
        # On récupère la map brute d'Ergast
        raw_circuit_map = ergast_service.get_official_circuit_map(api, year)

        # Correction spécifique pour 2026 :
        # Si FastF1 et Ergast sont décalés, on utilise une logique de repli par localisation
        # pour éviter que Bahrain n'affiche le circuit de Miami.
        rounds_info = {}
        formatted_schedule = []

        for _, row in schedule.iterrows():
            r_num = int(row['RoundNumber'])

            # On tente de récupérer le nom officiel via la map,
            # mais on vérifie la cohérence avec la localisation de FastF1
            location = str(row.get('Location', '')).lower()
            event_name = str(row.get('EventName', '')).lower()

            # Logique de sécurité pour les noms de circuits 2026
            official_circuit_name = raw_circuit_map.get(r_num)

            # Si c'est 2026 et que le nom semble décalé (ex: Bahrain avec Miami)
            # On force le nom basé sur la localisation de FastF1 qui est plus fiable
            if year == 2026:
                if "sakhir" in location or "bahrain" in event_name:
                    official_circuit_name = "Bahrain International Circuit"
                elif "jeddah" in location or "saudi" in event_name:
                    official_circuit_name = "Jeddah Corniche Circuit"
                elif "melbourne" in location:
                    official_circuit_name = "Albert Park Grand Prix Circuit"
                elif "shanghai" in location:
                    official_circuit_name = "Shanghai International Circuit"
                elif "suzuka" in location:
                    official_circuit_name = "Suzuka Circuit"
                elif "miami" in location:
                    official_circuit_name = "Miami International Autodrome"
                elif "monaco" in location:
                    official_circuit_name = "Circuit de Monaco"
                elif "barcelona" in location:
                    official_circuit_name = "Circuit de Barcelona-Catalunya"
                elif "montréal" in location or "montreal" in location:
                    official_circuit_name = "Circuit Gilles Villeneuve"
                elif "spielberg" in location:
                    official_circuit_name = "Red Bull Ring"
                elif "silverstone" in location:
                    official_circuit_name = "Silverstone Circuit"
                elif "budapest" in location:
                    official_circuit_name = "Hungaroring"
                elif "spa" in location:
                    official_circuit_name = "Circuit de Spa-Francorchamps"
                elif "zandvoort" in location:
                    official_circuit_name = "Circuit Zandvoort"
                elif "monza" in location:
                    official_circuit_name = "Autodromo Nazionale di Monza"
                elif "baku" in location:
                    official_circuit_name = "Baku City Circuit"
                elif "singapore" in location:
                    official_circuit_name = "Marina Bay Street Circuit"
                elif "austin" in location:
                    official_circuit_name = "Circuit of the Americas"
                elif "mexico" in location:
                    official_circuit_name = "Autódromo Hermanos Rodríguez"
                elif "são paulo" in location or "interlagos" in location:
                    official_circuit_name = "Autódromo José Carlos Pace"
                elif "las vegas" in location:
                    official_circuit_name = "Las Vegas Strip Street Circuit"
                elif "lusail" in location or "qatar" in location:
                    official_circuit_name = "Lusail International Circuit"
                elif "yas marina" in location or "abu dhabi" in location:
                    official_circuit_name = "Yas Marina Circuit"

            # Si on n'a toujours rien, on utilise le formateur générique avec la map (corrigée ou non)
            temp_map = {r_num: official_circuit_name} if official_circuit_name else raw_circuit_map
            event_info = ergast_service.format_event_info(row, year, temp_map)

            # On s'assure que le circuit_name final est bien celui qu'on a validé
            if official_circuit_name:
                event_info['circuit_name'] = official_circuit_name

            formatted_schedule.append(event_info)
            rounds_info[r_num] = {
                'gpName': event_info['short_name'],
                'country': event_info['country']
            }

        save_json(OUTPUT_DIR, year, f"{year}_schedule.json", formatted_schedule)
        rounds = sorted(list(rounds_info.keys()))

    except Exception as e:
        print(f"❌ Erreur lors de la génération du calendrier : {e}")
        return

    # 2. CLASSEMENT PILOTES (ÉVOLUTION ROUND PAR ROUND)
    print(f"   ⏳ Traitement du Championnat Pilotes...")
    last_valid_drivers = []
    last_driver_round = 0

    for r in rounds:
        try:
            s = api.get_driver_standings(season=year, round=r)
            df = s.content[0] if (hasattr(s, 'content') and len(s.content) > 0) else None

            if df is not None and not df.empty:
                current_standing = ergast_service.clean_and_convert_df(df, year)
                save_json(OUTPUT_DIR, year, f"{year}_R{r}_driver_standings.json", current_standing, "driver")
                last_valid_drivers = current_standing
                last_driver_round = r
            else:
                break
        except:
            break

    if not last_valid_drivers:
        print(f"      ℹ️ Aucun classement trouvé. Initialisation du roster à 0 pts...")
        last_valid_drivers = ergast_service.initialize_empty_driver_standings(api, year)
        last_driver_round = 0

    if last_valid_drivers:
        save_json(OUTPUT_DIR, year, f"{year}_driver_standings.json",
                  {"season": year, "round": last_driver_round, "standings": last_valid_drivers}, "driver")

    # 3. CLASSEMENT ÉQUIPES (ÉVOLUTION ROUND PAR ROUND)
    print(f"   ⏳ Traitement du Championnat Équipes...")
    last_valid_teams = []
    last_team_round = 0

    for r in rounds:
        try:
            s = api.get_constructor_standings(season=year, round=r)
            df = s.content[0] if (hasattr(s, 'content') and len(s.content) > 0) else None

            if df is not None and not df.empty:
                current_standing_teams = ergast_service.clean_and_convert_df(df, year)
                save_json(OUTPUT_DIR, year, f"{year}_R{r}_constructor_standings.json", current_standing_teams, "team")
                last_valid_teams = current_standing_teams
                last_team_round = r
            else:
                break
        except:
            break

    if not last_valid_teams:
        print(f"      ℹ️ Aucun classement trouvé. Initialisation des équipes à 0 pts...")
        last_valid_teams = ergast_service.initialize_empty_team_standings(api, year)
        last_team_round = 0

    if last_valid_teams:
        save_json(OUTPUT_DIR, year, f"{year}_constructor_standings.json",
                  {"season": year, "round": last_team_round, "standings": last_valid_teams}, "team")

    # 4. RÉSULTATS DES SESSIONS (POUR LES ROUNDS TERMINÉS)
    max_round_played = max(last_driver_round, last_team_round)

    if max_round_played > 0:
        print(f"   ⏳ Téléchargement des résultats de sessions jusqu'au Round {max_round_played}...")
        all_race, all_qualy, all_sprint = [], [], []

        for r in rounds:
            if r > max_round_played:
                continue

            meta = rounds_info.get(r, {'gpName': 'Unknown', 'country': 'Unknown'})

            try:
                res = api.get_race_results(season=year, round=r)
                df = res.content[0] if (hasattr(res, 'content') and res.content) else None
                if df is not None and not df.empty:
                    df['round'], df['raceName'], df['country'] = r, meta['gpName'], meta['country']
                    all_race.extend(ergast_service.clean_and_convert_df(df, year))
            except:
                pass

            try:
                res_q = api.get_qualifying_results(season=year, round=r)
                df_q = res_q.content[0] if (hasattr(res_q, 'content') and res_q.content) else None
                if df_q is not None and not df_q.empty:
                    df_q['round'], df_q['raceName'], df_q['country'] = r, meta['gpName'], meta['country']
                    all_qualy.extend(ergast_service.clean_and_convert_df(df_q, year))
            except:
                pass

            try:
                res_s = api.get_sprint_results(season=year, round=r)
                df_s = res_s.content[0] if (hasattr(res_s, 'content') and res_s.content) else None
                if df_s is not None and not df_s.empty:
                    df_s['round'], df_s['raceName'], df_s['country'] = r, meta['gpName'], meta['country']
                    all_sprint.extend(ergast_service.clean_and_convert_df(df_s, year))
            except:
                pass

        if all_race: save_json(OUTPUT_DIR, year, f"{year}_race_results.json", all_race, "results")
        if all_qualy: save_json(OUTPUT_DIR, year, f"{year}_qualifying_results.json", all_qualy, "results")
        if all_sprint: save_json(OUTPUT_DIR, year, f"{year}_sprint_results.json", all_sprint, "results")
    else:
        print(f"   ℹ️ Aucun résultat de session à télécharger.")


def preprocess_all_ergast(start_year=2022, end_year=2026):
    ensure_directory_exists(OUTPUT_DIR)
    ensure_directory_exists(CACHE_DIR)
    fastf1.Cache.enable_cache(CACHE_DIR)

    for year in range(start_year, end_year + 1):
        preprocess_season_ergast(year)
    print("\n🎉 Prétraitement Ergast terminé avec succès !")


if __name__ == "__main__":
    preprocess_all_ergast(2026, 2026)
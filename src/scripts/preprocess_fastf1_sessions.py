import fastf1
from utils.data_utils import get_path, save_json, ensure_directory_exists, clean_nat_values
from services import session_service


BASE_OUTPUT_DIR = get_path("data_cache", "sessions")
CACHE_DIR = get_path("data", "fastf1_cache")


def preprocess_session(year, gp_round, session_name):
    try:
        print(f"   ⏳ Traitement de {session_name}...")
        session = fastf1.get_session(year, gp_round, session_name)

        try:
            session.load(laps=True, telemetry=False, weather=False)
        except Exception:
            print(f"      ⚠️ Chargement partiel pour {session_name}")

        results = session_service.process_results(session, session_name, year)
        laps, stints = session_service.process_laps_and_stints(session)

        session_data = {
            "info": clean_nat_values({
                "year": year,
                "round": gp_round,
                "name": session.event['EventName'] if hasattr(session, 'event') else "Unknown",
                "session_type": session_name,
                "location": session.event['Location'] if hasattr(session, 'event') else ""
            }),
            "results": results,
            "laps": laps,
            "stints": stints
        }

        norm_name = session_name.replace(' ', '')
        if "Shootout" in session_name:
            norm_name = "SprintQualifying"

        save_json(BASE_OUTPUT_DIR, year, f"{year}_R{gp_round}_{norm_name}.json", session_data)

    except Exception as e:
        print(f"❌ Erreur critique R{gp_round} {session_name}: {e}")


def run_season(year):
    ensure_directory_exists(CACHE_DIR)
    fastf1.Cache.enable_cache(CACHE_DIR)

    print(f"\n=== 🏁 DÉMARRAGE DE LA SAISON {year} ===")

    schedule = fastf1.get_event_schedule(year, include_testing=False)
    schedule = schedule[schedule['EventName'].notna()].reset_index(drop=True)

    for _, event in schedule.iterrows():
        r_num = event['RoundNumber']
        print(f"\n--- GP Manche {r_num} : {event['EventName']} ---")

        for i in range(1, 6):
            s_type = event.get(f"Session{i}")
            if isinstance(s_type, str):
                preprocess_session(year, r_num, s_type)


if __name__ == "__main__":
    run_season(2025)
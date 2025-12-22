import pandas as pd
from utils.data_utils import safe_int, safe_float


def get_positions_series(df, col_name='position'):
    if df.empty or col_name not in df.columns:
        return pd.Series(dtype='float64')
    return pd.to_numeric(df[col_name], errors='coerce')


def build_season_history(entity_id, id_column, race_df, schedule):
    history = {}
    entity_races = race_df[race_df[id_column] == entity_id] if not race_df.empty else pd.DataFrame()

    for _, event in schedule.iterrows():
        gp_name = event['EventName']
        round_num = event['RoundNumber']
        result_val = "-"

        if not entity_races.empty:
            match = entity_races[entity_races['round'].astype(str) == str(round_num)]
            if not match.empty:
                row = match.iloc[0]
                pos = row.get('position')
                status = str(row.get('status', '')).strip()

                if status in ['Disqualified', 'DSQ']:
                    result_val = "DSQ"
                elif status != 'Finished' and not 'Lap' in status and status != '':
                    result_val = "DNF"
                elif pos and str(pos).lower() != 'nan':
                    result_val = safe_int(pos)

        history[gp_name] = result_val
    return history


def calculate_stats_generic(entity_id, id_column, row_standing, race_df, quali_df, sprint_df, schedule, total_qualis,
                            include_history=True):
    races = race_df[race_df[id_column] == entity_id] if not race_df.empty else pd.DataFrame()
    qualis = quali_df[quali_df[id_column] == entity_id] if not quali_df.empty else pd.DataFrame()
    sprints = sprint_df[sprint_df[id_column] == entity_id] if not sprint_df.empty else pd.DataFrame()

    race_pos = get_positions_series(races, 'position')
    quali_pos = get_positions_series(qualis, 'position')
    sprint_pos = get_positions_series(sprints, 'position')
    sprint_grids = get_positions_series(sprints, 'grid')

    total_races = int(races.shape[0])
    wins = race_pos[race_pos == 1].count()
    podiums = race_pos[race_pos.isin([1, 2, 3])].count()
    top10 = race_pos[race_pos <= 10].count()
    poles = quali_pos[quali_pos == 1].count()

    dnf = 0
    if not races.empty and 'status' in races.columns:
        def is_dnf_check(status_val):
            s = str(status_val).strip()
            if s in ['Finished', 'Disqualified'] or 'Lap' in s or s == '' or s.lower() == 'nan':
                return False
            return True

        dnf = races['status'].apply(is_dnf_check).sum()

    sprint_wins = sprint_pos[sprint_pos == 1].count()
    sprint_podiums = sprint_pos[sprint_pos.isin([1, 2, 3])].count()
    sprint_poles = sprint_grids[sprint_grids == 1].count()

    avg_race = round(race_pos.mean(), 2) if not race_pos.empty else None
    avg_quali = round(quali_pos.mean(), 2) if not quali_pos.empty else None

    best_res = int(race_pos.min()) if not race_pos.dropna().empty else None
    best_quali_res = int(quali_pos.min()) if not quali_pos.dropna().empty else None

    q3_appearances = quali_pos[quali_pos <= 10].count()

    result_dict = {
        id_column: entity_id,
        "position": safe_int(row_standing.get('position')),
        "points": safe_float(row_standing.get('points')),
        "wins": safe_int(row_standing.get('wins', wins)),
        "total_races": total_races,
        "stat_podiums": int(podiums),
        "stat_top10": int(top10),
        "stat_poles": int(poles),
        "stat_dnf": int(dnf),
        "stat_sprint_wins": int(sprint_wins),
        "stat_sprint_podiums": int(sprint_podiums),
        "stat_sprint_poles": int(sprint_poles),
        "stat_q3_appearances": int(q3_appearances),
        "total_qualis": int(total_qualis),
        "stat_avg_race_position": avg_race,
        "stat_avg_qualifying_position": avg_quali,
        "stat_best_race_result": best_res,
        "stat_best_quali_result": best_quali_res
    }

    if include_history:
        result_dict["season_results_history"] = build_season_history(entity_id, id_column, race_df, schedule)

    return result_dict
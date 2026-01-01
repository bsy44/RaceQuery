import pandas as pd
from fastf1.ergast import Ergast
from utils.data_utils import apply_data_patches


def safe_str(val):
    if val is None or pd.isna(val):
        return ""
    return str(val).strip()


def format_numeric_str(val):
    if pd.isna(val) or val is None or str(val).lower() in ['nan', 'none', 'nat', '']:
        return ""
    try:
        return str(int(float(val)))
    except (ValueError, TypeError):
        return str(val).strip()


def clean_and_convert_df(df: pd.DataFrame, year: int) -> list:
    if df is None or df.empty:
        return []

    df = apply_data_patches(df, year)

    num_cols = ['driverNumber', 'number', 'permanentNumber', 'position', 'rank', 'round', 'points', 'wins']
    for col in num_cols:
        if col in df.columns:
            df[col] = df[col].apply(format_numeric_str)

    return df.astype(str).replace(['None', 'nan', 'NaN', 'NaT'], '').to_dict('records')


def get_official_circuit_map(api: Ergast, year: int) -> dict:
    circuit_map = {}
    try:
        ergast_cal = api.get_race_schedule(season=year)
        df_ergast = None

        if hasattr(ergast_cal, 'dataframe'):
            df_ergast = ergast_cal.dataframe
        elif isinstance(ergast_cal, pd.DataFrame):
            df_ergast = ergast_cal

        if df_ergast is not None and not df_ergast.empty:
            cols = df_ergast.columns.tolist()
            round_col = 'round' if 'round' in cols else ('raceNumber' if 'raceNumber' in cols else None)
            name_col = 'circuitName' if 'circuitName' in cols else ('circuit_name' if 'circuit_name' in cols else None)

            if round_col and name_col:
                for _, row_erg in df_ergast.iterrows():
                    try:
                        r_val = row_erg[round_col]
                        if pd.isna(r_val): continue
                        r_num_erg = int(float(r_val))
                        c_name = safe_str(row_erg[name_col])
                        if c_name:
                            circuit_map[r_num_erg] = c_name
                    except:
                        continue
    except Exception as e:
        print(f"   ⚠️ Could not fetch Ergast circuit names: {e}")

    return circuit_map


def format_event_info(row: pd.Series, year: int, circuit_map: dict) -> dict:
    r_num = int(row['RoundNumber'])
    location_fallback = safe_str(row.get('Location', 'TBA'))
    official_circuit_name = circuit_map.get(r_num, location_fallback)

    event_info = {
        "season": year,
        "round": r_num,
        "country": safe_str(row['Country']),
        "location": location_fallback,
        "circuit_name": official_circuit_name,
        "official_name": safe_str(row.get('OfficialEventName', row['EventName'])),
        "short_name": safe_str(row['EventName']),
        "event_format": safe_str(row['EventFormat']),
        "event_date": safe_str(row['EventDate']),
        "sessions": []
    }

    for i in range(1, 6):
        name_col, date_col, utc_col = f"Session{i}", f"Session{i}Date", f"Session{i}DateUtc"
        if name_col in row and pd.notna(row[name_col]):
            event_info["sessions"].append({
                "name": safe_str(row[name_col]),
                "local_date": safe_str(row.get(date_col)),
                "utc_date": safe_str(row.get(utc_col))
            })
    return event_info


def initialize_empty_driver_standings(api: Ergast, year: int):
    try:
        r_info = api.get_driver_info(season=year)
        df_init = r_info.dataframe if hasattr(r_info, 'dataframe') else r_info
        if df_init is not None and not df_init.empty:
            df_init['points'], df_init['wins'] = 0, 0
            num_col = 'permanentNumber' if 'permanentNumber' in df_init.columns else 'driverNumber'
            df_init['sort_num'] = pd.to_numeric(df_init[num_col], errors='coerce').fillna(999)
            df_init = df_init.sort_values('sort_num')
            df_init['position'] = range(1, len(df_init) + 1)
            return clean_and_convert_df(df_init.drop(columns=['sort_num']), year)
    except Exception as e:
        print(f"      ⚠️ Could not initialize drivers roster: {e}")
    return []


def initialize_empty_team_standings(api: Ergast, year: int):
    try:
        t_info = api.get_constructor_info(season=year)
        df_t_init = t_info.dataframe if hasattr(t_info, 'dataframe') else t_info
        if df_t_init is not None and not df_t_init.empty:
            df_t_init['points'], df_t_init['wins'] = 0, 0
            name_col = 'name' if 'name' in df_t_init.columns else 'constructorName'
            df_t_init = df_t_init.sort_values(name_col)
            df_t_init['position'] = range(1, len(df_t_init) + 1)
            return clean_and_convert_df(df_t_init, year)
    except Exception as e:
        print(f"      ⚠️ Could not initialize teams roster: {e}")
    return []
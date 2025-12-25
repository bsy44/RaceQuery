import pandas as pd
from fastf1.core import Session
from utils.data_utils import td_to_ms, apply_data_patches


COLOR_TO_TEAM_ID = {
    "3671C6": "red_bull", "1E41FF": "red_bull",
    "27F4D2": "mercedes", "00D2BE": "mercedes",
    "E80020": "ferrari", "DC0000": "ferrari",
    "FF8000": "mclaren",
    "229971": "aston_martin", "006F62": "aston_martin",
    "0093CC": "alpine", "2293D1": "alpine",
    "64C4FF": "williams", "005AFF": "williams",
    "6692FF": "rb", "4E7CFF": "rb",
    "52E252": "sauber", "00E701": "sauber",
    "B6BABD": "haas", "FFFFFF": "haas", "767676": "haas"
}


def generate_id(name):
    if not name or pd.isna(name) or str(name).lower() in ["nan", "none", ""]:
        return ""
    return str(name).lower().strip().replace("'", "").replace(" ", "_").replace("-", "_")


def normalize_team_id(t_id, team_name="", color=""):
    if color:
        clean_color = str(color).upper().strip()
        if clean_color in COLOR_TO_TEAM_ID:
            return COLOR_TO_TEAM_ID[clean_color]

    t_id_clean = str(t_id or "").lower().strip()
    name_clean = str(team_name or "").lower().strip()
    search_str = f"{t_id_clean} {name_clean}"

    if "red bull" in search_str or "redbull" in search_str or "red_bull" in search_str:
        return "red_bull"
    if any(x in search_str for x in ["racing bulls", "vcarb", "visa cash", "app rb", "racing_bulls"]):
        return "rb"
    if t_id_clean == "rb" or " rb " in f" {search_str} ": return "rb"
    if "haas" in search_str: return "haas"
    if "aston" in search_str: return "aston_martin"
    if "alpine" in search_str: return "alpine"
    if "williams" in search_str: return "williams"
    if "mclaren" in search_str: return "mclaren"
    if "ferrari" in search_str: return "ferrari"
    if "mercedes" in search_str: return "mercedes"
    if any(x in search_str for x in ["sauber", "stake", "kick"]): return "sauber"
    if "alpha" in search_str: return "alphatauri"
    if "alfa" in search_str: return "alfa"

    return t_id_clean if t_id_clean else generate_id(team_name)


def process_results(session: Session, session_type: str, year: int):
    results_df = session.results.copy()
    laps = session.laps

    tyre_map = {}
    if laps is not None and not laps.empty:
        try:
            is_race = "Race" in session_type or ("Sprint" in session_type and "Qualifying" not in session_type)
            if is_race:
                tyre_map = laps.sort_values('LapNumber').groupby('Driver').last()['Compound'].to_dict()
            else:
                tyre_map = laps.sort_values('LapTime').groupby('Driver').first()['Compound'].to_dict()
        except:
            pass

    if "Position" not in results_df.columns or results_df["Position"].isna().all():
        best_laps = {}
        lap_counts = {}
        if laps is not None and not laps.empty:
            valid_laps = laps.dropna(subset=['LapTime'])
            if not valid_laps.empty:
                best_laps = valid_laps.sort_values("LapTime").groupby("Driver").first()["LapTime"].to_dict()
            lap_counts = laps.groupby("Driver")["LapNumber"].count().to_dict()

        results = []
        for _, drv in results_df.iterrows():
            driver_code = drv.get("Abbreviation")
            raw_time = best_laps.get(driver_code)
            time_ms = td_to_ms(raw_time) if raw_time else None

            d_id = drv.get("DriverId")
            if not d_id or pd.isna(d_id):
                d_id = generate_id(drv.get("LastName") or drv.get("Abbreviation"))

            t_id = normalize_team_id(drv.get("TeamId"), drv.get("TeamName"), drv.get("TeamColor"))

            results.append({
                "DriverNumber": str(drv.get("DriverNumber", "")),
                "BroadcastName": str(drv.get("BroadcastName", drv.get("FullName", ""))),
                "Abbreviation": str(driver_code or ""),
                "DriverId": d_id,
                "TeamName": str(drv.get("TeamName", "Unknown")),
                "TeamColor": str(drv.get("TeamColor", "767676")),
                "TeamId": t_id,
                "FirstName": str(drv.get("FirstName", "")),
                "LastName": str(drv.get("LastName", "")),
                "FullName": str(drv.get("FullName", "")),
                "HeadshotUrl": str(drv.get("HeadshotUrl", "")),
                "CountryCode": str(drv.get("CountryCode", "")),
                "Position": 0,
                "ClassifiedPosition": 0,
                "Status": "Finished" if lap_counts.get(driver_code, 0) > 0 else "No Time",
                "Laps": int(lap_counts.get(driver_code, 0)),
                "Time_ms": time_ms,
                "Tyre": str(tyre_map.get(driver_code, ""))
            })

        def sort_key(x):
            return (x["Time_ms"] is None, x["Time_ms"] or 9999999)

        results.sort(key=sort_key)

        for i, res in enumerate(results):
            res["Position"] = i + 1
            res["ClassifiedPosition"] = i + 1

        final_df = apply_data_patches(pd.DataFrame(results), year)
        return final_df.astype(str).replace('None', '').to_dict('records')

    def clean_row(row):
        d_id = row.get('DriverId')
        if not d_id or pd.isna(d_id):
            d_id = generate_id(row.get('LastName') or row.get('Abbreviation'))
        t_id = normalize_team_id(row.get('TeamId'), row.get('TeamName'), row.get('TeamColor'))
        return pd.Series([d_id, t_id])

    results_df[['DriverId', 'TeamId']] = results_df.apply(clean_row, axis=1)

    if 'Time' in results_df.columns:
        results_df['Time_ms'] = results_df['Time'].apply(td_to_ms)

    results_df['Tyre'] = results_df['Abbreviation'].map(tyre_map).fillna(
        "") if 'Abbreviation' in results_df.columns else ""
    results_df = apply_data_patches(results_df, year)

    return results_df.astype(str).replace('None', '').to_dict("records")


def process_laps_and_stints(session: Session):
    laps_data, stints_data = [], []
    if session.laps is not None and not session.laps.empty:
        laps_df = session.laps.reset_index(drop=True).copy()
        for col in ['LapTime', 'Sector1Time', 'Sector2Time', 'Sector3Time']:
            if col in laps_df:
                laps_df[col + "_ms"] = laps_df[col].apply(td_to_ms)

        lap_cols = ['Driver', 'LapNumber', 'IsPersonalBest', 'Compound', 'TyreLife', 'Stint',
                    'LapTime_ms', 'Sector1Time_ms', 'Sector2Time_ms', 'Sector3Time_ms', 'TrackStatus']
        existing = [c for c in lap_cols if c in laps_df.columns]
        laps_data = laps_df[existing].astype(str).replace('None', '').to_dict('records')

        stint_cols = ['Driver', 'Stint', 'Compound', 'TyreLife']
        existing_stints = [c for c in stint_cols if c in session.laps.columns]
        stints = session.laps[existing_stints].dropna(subset=['Stint']).drop_duplicates(
            subset=['Driver', 'Stint']).sort_values(['Driver', 'Stint'])
        stints_data = stints.astype(str).replace('None', '').to_dict('records')

    return laps_data, stints_data
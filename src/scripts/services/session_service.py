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
    if not name or pd.isna(name): return ""
    return str(name).lower().strip().replace("'", "").replace(" ", "_").replace("-", "_")


def normalize_team_id(t_id, color=""):
    t_id = str(t_id or "").lower().strip()
    if "red_bull" in t_id: return "red_bull"
    if any(x in t_id for x in ["racing_bulls", "rb", "visa"]): return "rb"
    if "haas" in t_id: return "haas"
    if "aston" in t_id: return "aston_martin"
    if "alpine" in t_id: return "alpine"
    if "williams" in t_id: return "williams"
    if "mclaren" in t_id: return "mclaren"
    if "ferrari" in t_id: return "ferrari"
    if "mercedes" in t_id: return "mercedes"
    if any(x in t_id for x in ["sauber", "stake", "kick"]): return "sauber"
    if "alpha" in t_id: return "alphatauri"

    if not t_id and color:
        clean_color = str(color).upper().strip()
        return COLOR_TO_TEAM_ID.get(clean_color, t_id)
    return t_id


def process_results(session: Session, session_type: str, year: int):
    results_df = session.results.copy()
    laps = session.laps

    if "Position" not in results_df.columns or results_df["Position"].isna().all():
        if laps is None or laps.empty: return []

        best_laps = laps.sort_values("LapTime").groupby("Driver").first().sort_values("LapTime")
        lap_counts = laps.groupby("Driver")["LapNumber"].count().to_dict()

        results = []
        pos = 1
        for driver_code, row_lap in best_laps.iterrows():
            drv = session.get_driver(driver_code)
            d_id = drv.get("DriverId") or generate_id(drv.get("LastName") or drv.get("Abbreviation"))
            t_id = normalize_team_id(drv.get("TeamId") or generate_id(drv.get("TeamName")), drv.get("TeamColor"))

            results.append({
                "DriverNumber": str(drv.get("DriverNumber", "")),
                "BroadcastName": str(drv.get("BroadcastName", "")),
                "Abbreviation": str(drv.get("Abbreviation", "")),
                "DriverId": d_id,
                "TeamName": str(drv.get("TeamName", "")),
                "TeamColor": str(drv.get("TeamColor", "")),
                "TeamId": t_id,
                "FirstName": str(drv.get("FirstName", "")),
                "LastName": str(drv.get("LastName", "")),
                "FullName": str(drv.get("FullName", "")),
                "HeadshotUrl": str(drv.get("HeadshotUrl", "")),
                "CountryCode": str(drv.get("CountryCode", "")),
                "Position": pos,
                "ClassifiedPosition": pos,
                "Status": "Finished",
                "Laps": int(lap_counts.get(driver_code, 0)),
                "Time_ms": td_to_ms(row_lap["LapTime"]),
                "Tyre": str(row_lap.get("Compound", ""))
            })
            pos += 1

        final_df = apply_data_patches(pd.DataFrame(results), year)
        return final_df.astype(str).to_dict('records')

    tyre_map = {}
    if laps is not None and not laps.empty:
        try:
            is_race = "Race" in session_type or "Sprint" in session_type
            if is_race:
                tyre_map = laps.sort_values('LapNumber').groupby('Driver').last()['Compound'].to_dict()
            else:
                tyre_map = laps.sort_values('LapTime').groupby('Driver').first()['Compound'].to_dict()
        except:
            pass

    def clean_row(row):
        d_id = row.get('DriverId') or generate_id(row.get('LastName') or row.get('Abbreviation'))
        t_id = normalize_team_id(row.get('TeamId') or generate_id(row.get('TeamName')), row.get('TeamColor'))
        return pd.Series([d_id, t_id])

    results_df[['DriverId', 'TeamId']] = results_df.apply(clean_row, axis=1)

    if 'Time' in results_df.columns:
        results_df['Time_ms'] = results_df['Time'].apply(td_to_ms)

    if 'Status' in results_df.columns and 'Laps' in results_df.columns:
        winner_laps = results_df['Laps'].max()

        def fix_status(row):
            curr = str(row.get('Status', '')).strip()
            if curr and curr.lower() != 'nan': return curr
            l_count = float(row.get('Laps', 0))
            if pd.isna(l_count) or l_count == 0: return "DNF"
            if l_count == winner_laps: return "Finished"
            return f"+{int(winner_laps - l_count)} Laps"

        results_df['Status'] = results_df.apply(fix_status, axis=1)

    results_df['Tyre'] = results_df['Abbreviation'].map(tyre_map).fillna(
        "") if 'Abbreviation' in results_df.columns else ""

    results_df = apply_data_patches(results_df, year)

    return results_df.astype(str).to_dict("records")


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
        laps_data = laps_df[existing].astype(str).to_dict('records')

        stint_cols = ['Driver', 'Stint', 'Compound', 'TyreLife']
        existing_stints = [c for c in stint_cols if c in session.laps.columns]
        stints = session.laps[existing_stints].dropna(subset=['Stint']).drop_duplicates(
            subset=['Driver', 'Stint']).sort_values(['Driver', 'Stint'])
        stints_data = stints.astype(str).to_dict('records')

    return laps_data, stints_data
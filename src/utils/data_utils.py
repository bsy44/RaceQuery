import os
import json
import pandas as pd
import numpy as np
from datetime import datetime


SCRIPT_DIR = os.path.dirname(os.path.abspath(__file__))
PROJECT_ROOT = os.path.abspath(os.path.join(SCRIPT_DIR, ".."))


def get_path(*args):
    return os.path.join(PROJECT_ROOT, *args)


def ensure_directory_exists(directory_path):
    if not os.path.exists(directory_path):
        os.makedirs(directory_path, exist_ok=True)


def td_to_ms(td):
    if pd.isna(td): return None
    if isinstance(td, pd.Timedelta): return int(td.total_seconds() * 1000)
    return None


def clean_nat_values(data):
    if isinstance(data, dict):
        return {k: clean_nat_values(v) for k, v in data.items()}
    elif isinstance(data, list):
        return [clean_nat_values(elem) for elem in data]
    elif pd.isna(data) or str(data).lower() in ["nan", "nat", "none"]:
        return None
    elif isinstance(data, (pd.Timestamp, datetime, np.datetime64)):
        return str(data)
    return data


def safe_int(val):
    try: return int(float(val))
    except: return 0


def safe_float(val):
    try: return float(val)
    except: return 0.0


def apply_data_patches(df, year):
    if df is None or df.empty: return df
    if 2022 <= int(year) <= 2025:
        if 'driverId' in df.columns:
            mask = df['driverId'] == 'max_verstappen'
            if mask.any():
                for col in ['driverNumber', 'number', 'permanentNumber', 'no', 'DriverNumber']:
                    if col in df.columns:
                        if df[col].dtype != 'object':
                            df[col] = df[col].astype(object)
                        df.loc[mask, col] = '1'
    return df


def save_json(base_dir, year, filename, data, subfolder=None):
    target_dir = os.path.join(base_dir, str(year))
    if subfolder: target_dir = os.path.join(target_dir, subfolder)
    ensure_directory_exists(target_dir)
    path = os.path.join(target_dir, filename)
    with open(path, "w", encoding="utf-8") as f:
        json.dump(data, f, indent=2)
    print(f"   ✔ Saved {filename}")


def load_json_as_df(base_dir, year, subfolder, filename):
    path = os.path.join(base_dir, str(year))
    if subfolder:
        path = os.path.join(path, subfolder)
    path = os.path.join(path, filename)

    if not os.path.exists(path):
        return pd.DataFrame()

    try:
        with open(path, "r", encoding="utf-8") as f:
            data = json.load(f)
            raw_data = data["standings"] if isinstance(data, dict) and "standings" in data else data
            df = pd.DataFrame(raw_data)
            return apply_data_patches(df, year)
    except Exception:
        return pd.DataFrame()
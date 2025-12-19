import os
import json
import pandas as pd


def ensure_directory_exists(directory_path):
    if not os.path.exists(directory_path):
        os.makedirs(directory_path, exist_ok=True)


def load_json_as_df(directory, year, subfolder, filename):
    path = os.path.join(directory, str(year), subfolder, filename)
    if not os.path.exists(path):
        return pd.DataFrame()
    try:
        with open(path, "r", encoding="utf-8") as file:
            data = json.load(file)
            if isinstance(data, dict) and "standings" in data:
                return pd.DataFrame(data["standings"])
            elif isinstance(data, list):
                return pd.DataFrame(data)
            return pd.DataFrame()
    except Exception:
        return pd.DataFrame()


def save_json(output_dir, year, filename, data, subfolder):
    target_dir = os.path.join(output_dir, subfolder)
    ensure_directory_exists(target_dir)
    path = os.path.join(target_dir, filename)
    with open(path, "w", encoding="utf-8") as file:
        json.dump(data, file, indent=2)
    print(f"✔ Saved {filename} in {subfolder}")


def safe_int(val):
    try: return int(float(val))
    except: return 0


def safe_float(val):
    try: return float(val)
    except: return 0.0
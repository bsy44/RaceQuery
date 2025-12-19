import os
import json
import pandas as pd


def ensure_directory_exists(directory_path):
    if not os.path.exists(directory_path):
        os.makedirs(directory_path, exist_ok=True)


def apply_data_patches(df, year):
    if df is None or df.empty:
        return df
    return df


def load_json_as_df(directory, year, subfolder, filename):
    path = os.path.join(directory, str(year))
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
    except Exception as e:
        print(f"❌ Erreur lors du chargement de {filename}: {e}")
        return pd.DataFrame()


def save_json(output_dir, year, filename, data, subfolder):
    target_dir = os.path.join(output_dir, str(year))
    if subfolder:
        target_dir = os.path.join(target_dir, subfolder)

    ensure_directory_exists(target_dir)
    path = os.path.join(target_dir, filename)

    with open(path, "w", encoding="utf-8") as f:
        json.dump(data, f, indent=2)
    print(f"✔ Saved {filename} in {subfolder if subfolder else 'root'}")


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
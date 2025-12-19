import json
import os

CACHE_BASE_DIR = os.path.dirname(os.path.abspath(__file__))

def load_json_file(sub_dir: str, filename: str) -> dict | list | None:
    file_path = os.path.join(CACHE_BASE_DIR, sub_dir, filename)
    if not os.path.exists(file_path):
        return None
    try:
        with open(file_path, 'r', encoding='utf-8') as f:
            return json.load(f)
    except Exception as e:
        print(f"Error loading {filename}: {e}")
        return None
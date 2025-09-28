import fastf1
from fastf1.ergast import Ergast
import os


class ConstructorService:
    def __init__(self, season: int):
        self.season = season
        self.ergast = Ergast()

        cache_dir = 'backend/data/fastf1_cache'
        os.makedirs(cache_dir, exist_ok=True)
        fastf1.Cache.enable_cache(cache_dir)

    def get_constructor(self) -> list[dict]:
        df = self.ergast.get_constructor_info(season=self.season)

        print("Colonnes disponibles :", df.columns.tolist())

        result = []
        for _, row in df.iterrows():
            result.append({
                "constructorId": row["constructorId"],
                "name": row.get("constructorName"),
                "constructorUrl": row.get("constructorUrl"),
                "nationality": row["constructorNationality"]
            }) 

        return result

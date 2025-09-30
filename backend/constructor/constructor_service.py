import fastf1
from fastf1.ergast import Ergast
import os

class ConstructorService:
    def __init__(self):
        self.ergast = Ergast()

        cache_dir = 'backend/data/fastf1_cache'
        os.makedirs(cache_dir, exist_ok=True)
        fastf1.Cache.enable_cache(cache_dir)

    def get_constructors(self, season: int) -> list[dict]:
        df = self.ergast.get_constructor_info(season)
        return [self._format_constructor(row) for _, row in df.iterrows()]

    def get_constructor_by_id(self, constructor_id: str) -> dict | None:

        df = self.ergast.get_constructor_info(constructor=constructor_id)
        if df.empty:
            return None
        return self._format_constructor(df.iloc[0])

    def _format_constructor(self, row) -> dict:
        return {
            "constructorId": str(row["constructorId"]),
            "name": row.get("constructorName"),
            "nationality": row.get("constructorNationality"),
        }

import fastf1
from fastf1.ergast import Ergast
import os

class CircuitService:
    def __init__(self, season: int = None):
        self.season = season
        self.ergast = Ergast()

        cache_dir = 'data/fastf1_cache'
        os.makedirs(cache_dir, exist_ok=True)
        fastf1.Cache.enable_cache(cache_dir)

    def _format_circuit(self, row) -> dict:
        return {
            "circuitId": row["circuitId"],
            "circuitName": row["circuitName"],
            "location": row.get("locality"),
            "country": row.get("country"),
        }

    def get_circuits(self) -> list[dict]:
        df = self.ergast.get_circuits(season=self.season)
        return [self._format_circuit(row) for _, row in df.iterrows()]

    def get_circuit_by_id(self, circuit_id: str) -> dict | None:
        df = self.ergast.get_circuits(season=self.season)

        df_filtered = df[df["circuitId"] == circuit_id]

        if df_filtered.empty:
            return None

        row = df_filtered.iloc[0]
        return self._format_circuit(row)

import os
import fastf1
from fastf1.ergast import Ergast
from backend.circuits.circuit import Circuit

class CircuitService:
    def __init__(self, season: int = None):
        self.season = season
        self.ergast = Ergast()

        cache_dir = 'backend/data/fastf1_cache'
        os.makedirs(cache_dir, exist_ok=True)
        fastf1.Cache.enable_cache(cache_dir)

    def _format_circuit(self, row) -> Circuit:
        return Circuit(
            circuitId=row["circuitId"],
            circuitName=row["circuitName"],
            locality=row.get("locality"),
            country=row.get("country")
        )

    def get_circuits(self) -> list[Circuit]:
        df = self.ergast.get_circuits(season=self.season)
        return [self._format_circuit(row) for _, row in df.iterrows()]

    def get_circuit_by_id(self, circuit_id: str) -> Circuit | None:
        df = self.ergast.get_circuits(season=self.season)
        df_filtered = df[df["circuitId"] == circuit_id]
        if df_filtered.empty:
            return None
        return self._format_circuit(df_filtered.iloc[0])

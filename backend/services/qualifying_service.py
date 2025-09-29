import os
import fastf1
from fastf1.ergast import Ergast

class QualifyingService:
    def __init__(self, season: int, round: int):
        self.season = season
        self.round = round
        self.ergast = Ergast()

        cache_dir = "backend/data/fastf1_cache"
        os.makedirs(cache_dir, exist_ok=True)
        fastf1.Cache.enable_cache(cache_dir)

    def _format_timedelta(self, td):
        """Convert timedelta en string minutes:secondes.millisecondes"""
        if td is None:
            return None
        try:
            total_seconds = int(td.total_seconds())
            minutes, seconds = divmod(total_seconds, 60)
            millis = int(td.microseconds / 1000) if hasattr(td, "microseconds") else 0
            return f"{minutes}:{seconds:02d}.{millis:03d}"
        except:
            return str(td)

    def get_split(self, session_q: str) -> dict:
        """
        session_q: 'Q1', 'Q2', 'Q3'
        """
        df = self.ergast.get_race_schedule(season=self.season)
        if self.round:
            df = df[df['round'] == self.round]

        races = []

        for _, row in df.iterrows():
            round_num = row['round']
            quali_resp = self.ergast.get_qualifying_results(season=self.season, round=round_num)
            quali_df = quali_resp.content[0] if hasattr(quali_resp, "content") and len(quali_resp.content) > 0 else None

            race_info = {
                "season": str(self.season),
                "round": str(round_num),
                "raceName": row.get("raceName"),
                "QualifyingSplit": []
            }

            if quali_df is not None:
                temp_list = []
                for _, drv in quali_df.iterrows():
                    lap_time = drv.get(session_q)
                    if lap_time is None:
                        continue

                    temp_list.append({
                        "position": None,
                        "driverId": drv.get("driverId"),
                        "number": drv.get("driverNumber"),
                        "code": drv.get("driverCode"),
                        "fullName": f"{drv.get('givenName')} {drv.get('familyName')}",
                        "constructor": drv.get("constructorName"),
                        session_q: self._format_timedelta(lap_time)
                    })

                temp_list.sort(key=lambda x: x[session_q])

                if session_q == "Q2":
                    temp_list = temp_list[:15]
                elif session_q == "Q3":
                    temp_list = temp_list[:10]

                # Affecte la position
                for idx, d in enumerate(temp_list, start=1):
                    d["position"] = str(idx)

                race_info["QualifyingSplit"] = temp_list

            races.append(race_info)

        return {"season": str(self.season), "Races": races}

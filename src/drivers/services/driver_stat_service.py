from drivers.models.driver_stat import DriverStats
from drivers.services.driver_service import DriverService
from utils.cache_reader import load_json_file


class DriverStatService:
    def __init__(self, year: int):
        self.year = year
        self.driver_service = DriverService(year)


    def get_driver_stats_summary(self, driver_id: str) -> DriverStats | dict:
        filename = f"{self.year}_driver_stats.json"
        all_stats = load_json_file('data_cache/services/driver', filename)

        if not all_stats:
            return {
                "error": f"Pas de statistiques disponibles pour {self.year}. Avez-vous lancé le script preprocess_driver_stats.py ?"}

        driver_stat_data = next((item for item in all_stats if item["driverId"] == driver_id), None)

        if not driver_stat_data:
            return {"error": f"Pilote {driver_id} non trouvé dans les services de {self.year}"}

        driver_obj = self.driver_service.get_driver(driver_id)

        if isinstance(driver_obj, dict):
            driver_obj = None

        return DriverStats(
            driver=driver_obj,
            position=driver_stat_data.get("position"),
            points=driver_stat_data.get("points"),
            win=driver_stat_data.get("wins"),
            podium=int(driver_stat_data.get("stat_podiums", 0)),
            pole=int(driver_stat_data.get("stat_poles", 0)),
            top10=int(driver_stat_data.get("stat_top10", 0)),
            dnf=int(driver_stat_data.get("stat_dnf", 0)),
            sprint_win=int(driver_stat_data.get("stat_sprint_wins", 0)),
            sprint_podium=int(driver_stat_data.get("stat_sprint_podiums", 0)),
            sprint_pole=int(driver_stat_data.get("stat_sprint_poles", 0)),
            avg_race_finish=driver_stat_data.get("stat_avg_race_position"),
            avg_qualifying_finish=driver_stat_data.get("stat_avg_qualifying_position"),
            best_result=driver_stat_data.get("stat_best_race_result"),
            q3_appearance=int(driver_stat_data.get("stat_q3_appearances", 0)),
            total_quali=driver_stat_data.get("total_qualis"),
            total_races=driver_stat_data.get("total_races")
        )


    def get_driver_race_summary(self, id_driver: str) -> dict:
        filename = f"{self.year}_driver_stats.json"
        all_stats = load_json_file('data_cache/services/driver', filename)

        if not all_stats:
            return {"driver": [], "gps": [], "countries": {}, "results": {}}

        driver_stat_data = next((item for item in all_stats if item["driverId"] == id_driver), None)

        if not driver_stat_data:
            return {"driver": [], "gps": [], "countries": {}, "results": {}}

        history = driver_stat_data.get("season_results_history", {})

        driver_obj = self.driver_service.get_driver(id_driver)
        driver_code = "UNK"
        if not isinstance(driver_obj, dict):
            driver_code = driver_obj.code

        gps = list(history.keys())

        return {
            "driver": [driver_code],
            "gps": gps,
            "results": {
                driver_code: history
            }
        }
from http import HTTPStatus
from flask import Blueprint, jsonify
from drivers.services.driver_service import DriverService
from drivers.services.driver_standing_service import DriverStandingService
from drivers.services.driver_stat_service import DriverStatService

driver_bp = Blueprint('drivers', __name__)


# 2. LISTE DES PILOTES
@driver_bp.get("/<int:year>")
def list_drivers(year):
    service = DriverService(year)
    drivers = service.list_drivers()

    # Pas besoin de check complexe, si vide ça renvoie []
    drivers_dict = [d.to_dict() for d in drivers]
    return jsonify(drivers_dict), HTTPStatus.OK


# 3. CLASSEMENT PILOTES
@driver_bp.get("/<int:year>/standings")
def get_standings(year):
    service = DriverStandingService(year)
    standings = service.get_driver_standings()

    standings_dict = [s.to_dict() for s in standings]
    return jsonify(standings_dict), HTTPStatus.OK


# 4. STATS DÉTAILLÉES (Podiums, Victoires, etc.)
@driver_bp.get("/<int:year>/<id_driver>/detail")
def detail_driver_stats(year, id_driver):
    service = DriverStatService(year)
    stats = service.get_driver_stats_summary(id_driver)

    # ✅ SÉCURITÉ AJOUTÉE : Évite le crash 'dict has no attribute to_dict'
    if isinstance(stats, dict) and "error" in stats:
        return jsonify(stats), HTTPStatus.NOT_FOUND

    return jsonify(stats.to_dict()), HTTPStatus.OK


# 5. HISTORIQUE COURSES (Graphique)
@driver_bp.get("/<int:year>/<id_driver>/season-results")
def get_driver_season_results(year, id_driver):
    service = DriverStatService(year)
    stats = service.get_driver_race_summary(id_driver)

    # Ici services est déjà un dictionnaire formaté par le service, pas besoin de to_dict()
    return jsonify(stats), HTTPStatus.OK
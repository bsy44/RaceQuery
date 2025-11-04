from http import HTTPStatus
from flask import Blueprint, jsonify
from drivers.services.driver_service import DriverService
from drivers.services.driver_standing_service import DriverStandingService
from drivers.services.driver_stat_service import DriverStatService

driver_bp = Blueprint('drivers', __name__)

@driver_bp.get("/<int:year>/<id_driver>")
def get_driver(year, id_driver):
    service = DriverService(year)
    driver = service.get_driver(id_driver)
    return jsonify(driver.to_dict()), HTTPStatus.OK

@driver_bp.get("/<int:year>")
def list_drivers(year):
    service = DriverService(year)
    drivers = service.list_drivers()
    drivers_dict = [d.to_dict() for d in drivers]

    return jsonify(drivers_dict), HTTPStatus.OK

@driver_bp.get("/standings/<int:year>")
def get_driver_standings(year):
    service = DriverStandingService(year)
    standings = service.get_driver_standings()
    standings_dict = [s.to_dict() for s in standings]

    return jsonify(standings_dict), HTTPStatus.OK

@driver_bp.get("/<int:year>/<id_driver>/stats")
def detail_driver_stats(year, id_driver):
    service = DriverStatService(year)
    stats = service.get_driver_stats_summary(id_driver)
    return jsonify(stats.to_dict()), HTTPStatus.OK
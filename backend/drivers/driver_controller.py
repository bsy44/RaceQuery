from http import HTTPStatus
from flask import Blueprint, jsonify
from backend.drivers.driver_service import DriverService

driver_standing_bp = Blueprint('drivers', __name__)

@driver_standing_bp.get("/standings/<int:year>")
def get_driver_standings(year):
    service = DriverService(year)
    standings = service.get_driver_standings()
    return jsonify(standings), HTTPStatus.OK

@driver_standing_bp.get("/<int:year>/<id_driver>")
def get_driver(year, id_driver):
    service = DriverService(year)
    driver = service.get_driver(id_driver)
    return jsonify(driver), HTTPStatus.OK
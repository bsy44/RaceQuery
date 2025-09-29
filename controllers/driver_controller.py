from flask import Blueprint, jsonify
from services.driver_service import DriverService

driver_bp = Blueprint('drivers', __name__)
service = DriverService()


@driver_bp.get("/<int:season>")
def list_drivers(season):
    drivers = service.get_drivers(season)

    return jsonify(drivers)

@driver_bp.get("/<id_driver>")
def get_drivers(id_driver):
    drivers = service.get_driver_by_id(id_driver)

    return jsonify(drivers)
from flask import Blueprint, jsonify
from backend.services.driver_service import DriverService

driver_bp = Blueprint('drivers', __name__)

@driver_bp.get("/<int:season>")
def list_drivers(season):
    service = DriverService(season)
    drivers = service.get_drivers()

    return jsonify(drivers)

from flask import Blueprint, jsonify
from backend.services.driver_service import DriverService

driver_bp = Blueprint('drivers', __name__)

@driver_bp.get('/')
def list_drivers():
    service = DriverService(year=2025, grand_prix="Monza", session_type="R")
    drivers = service.get_drivers()

    return jsonify(drivers)

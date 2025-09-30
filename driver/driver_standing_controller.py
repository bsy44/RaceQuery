from flask import Blueprint, jsonify
from driver.driver_standing_service import DriverStandingService

driver_standing_bp = Blueprint('drivers-standings', __name__)

@driver_standing_bp.get("/<int:year>")
def get_driver_standings(year):
    service = DriverStandingService(year)
    standings = service.get_driver_standings()
    return jsonify(standings)


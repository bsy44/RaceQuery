from flask import Blueprint, jsonify
from backend.services.constructor_standing_service import ConstructorStandingService

constructor_standing_bp = Blueprint('constructors-standing', __name__)

@constructor_standing_bp.get("/<int:year>")
def get_constructor_standings(year):
    service = ConstructorStandingService(year)
    standings = service.get_constructor_standings()
    return jsonify(standings)


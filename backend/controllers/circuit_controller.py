from flask import Blueprint, jsonify
from backend.services.circuit_service import CircuitService

circuit_bp = Blueprint('circuits', __name__)

@circuit_bp.get("/<int:season>")
def list_circuits(season):
    service = CircuitService(season)
    circuits = service.get_circuits()

    return jsonify(circuits)

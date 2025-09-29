from flask import Blueprint, jsonify
from services.circuit_service import CircuitService

circuit_bp = Blueprint('circuits', __name__)

@circuit_bp.get("/<int:season>")
def list_circuits(season):
    service = CircuitService(season)
    circuits = service.get_circuits()

    return jsonify(circuits)

@circuit_bp.get("/<circuit_id>")
def get_circuit(circuit_id):
    service = CircuitService()
    circuit = service.get_circuit_by_id(circuit_id)
    return jsonify(circuit)
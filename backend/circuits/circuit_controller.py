from http import HTTPStatus

from flask import Blueprint, jsonify
from backend.circuits.circuit_service import CircuitService

circuit_bp = Blueprint('circuits', __name__)

@circuit_bp.get("/<int:season>")
def all_circuits(season):
    service = CircuitService(season)
    circuits = service.get_circuits()
    return jsonify([c.to_dict() for c in circuits]), HTTPStatus.OK

@circuit_bp.get("/<circuit_id>")
def get_circuit(circuit_id):
    service = CircuitService()
    circuit = service.get_circuit_by_id(circuit_id)
    return jsonify(circuit.to_dict()), HTTPStatus.OK
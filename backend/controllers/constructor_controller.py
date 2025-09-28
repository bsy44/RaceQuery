from flask import Blueprint, jsonify
from backend.services.constructor_service import ConstructorService

contructor_bp = Blueprint('constructors', __name__)

@contructor_bp.get("/<int:season>")
def list_constructors(season):
    service = ConstructorService(season)
    constructors = service.get_constructor()

    return jsonify(constructors)

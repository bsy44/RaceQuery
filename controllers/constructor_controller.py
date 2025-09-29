from flask import Blueprint, jsonify
from services.constructor_service import ConstructorService

contructor_bp = Blueprint('constructors', __name__)
service = ConstructorService()

@contructor_bp.get("/<int:season>")
def list_constructors(season):
    constructors = service.get_constructors(season)

    return jsonify(constructors)

@contructor_bp.get("/<constructor_id>")
def get_constructor(constructor_id):
    constructors = service.get_constructor_by_id(constructor_id)

    return jsonify(constructors)
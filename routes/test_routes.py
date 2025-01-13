from flask import Blueprint, jsonify
from pydantic import ValidationError
# from . import test_routes  
test_routes = Blueprint('test_routes', __name__)
@test_routes.route('/', methods=['GET'])  
def testing():
    try:
        return jsonify({"Hello": "Working"}), 200
    except ValidationError as e:  
        return jsonify({"error": e.errors()}), 400

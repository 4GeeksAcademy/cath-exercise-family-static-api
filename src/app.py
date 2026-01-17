"""
This module takes care of starting the API Server, Loading the DB and Adding the endpoints
"""
import os
from flask import Flask, request, jsonify, url_for
from flask_cors import CORS
from utils import APIException, generate_sitemap
from datastructures import FamilyStructure
# from models import Person


app = Flask(__name__)
app.url_map.strict_slashes = False
CORS(app)

# Create the jackson family object
jackson_family = FamilyStructure("Jackson")


# Handle/serialize errors like a JSON object
@app.errorhandler(APIException)
def handle_invalid_usage(error):
    return jsonify(error.to_dict()), error.status_code


# Generate sitemap with all your endpoints
@app.route('/')
def sitemap():
    return generate_sitemap(app)


@app.route('/members', methods=['GET'])
def get_family():
    # This is how you can use the Family datastructure by calling its methods
    members = jackson_family.get_all_members()
    return jsonify(members), 200


@app.route('/members/<int:id>', methods=['GET'])
def get_member(id):
    member = jackson_family.get_member(int(id))
    return jsonify(member[0]), 200


@app.route('/members', methods=['POST'])
def add_member():
    new_member = request.get_json(force=True)

    # Validate user input
    if not new_member:
        return jsonify({"error": "Request body is required"}), 400

    required_fields = {'first_name', 'age', 'lucky_numbers'}
    for field in required_fields:
        if field not in new_member:
            return jsonify({"error": f"Missing field: {field}"}), 400

    for key in new_member:
        if key not in required_fields:
            return jsonify({"error": f"Extra field: {key}"}), 400

    if not isinstance(new_member["first_name"], str):
        return jsonify({"error": "first_name must be a string"}), 400

    if not isinstance(new_member["age"], int):
        return jsonify({"error": "age must be an integer"}), 400

    if not isinstance(new_member["lucky_numbers"], list):
        return jsonify({"error": "lucky_numbers must be a List"}), 400

    if not all(isinstance(n, int) for n in new_member["lucky_numbers"]):
        return jsonify({"error": "lucky_numbers must contain only integers"}), 400

    # Add new member
    jackson_family.add_member(new_member)
    return jsonify(new_member), 200


@app.route('/members/<int:id>', methods=['DELETE'])
def delete_member(id):
    jackson_family.delete_member(int(id))
    return jsonify({'done': True}), 200


# This only runs if `$ python src/app.py` is executed
if __name__ == '__main__':
    PORT = int(os.environ.get('PORT', 3000))
    app.run(host='0.0.0.0', port=PORT, debug=True)

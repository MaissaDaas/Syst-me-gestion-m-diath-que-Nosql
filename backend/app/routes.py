from flask import Blueprint, request, jsonify
from pymongo import MongoClient

client = MongoClient("mongodb://localhost:27017/")
db = client["gestionabonnee"]

abonne_bp = Blueprint('abonne', __name__)

@abonne_bp.route('/abonne', methods=['POST'])
def create_abonne():
    data = request.json
    db.abonne.insert_one(data)
    return jsonify({"message": "Abonné créé avec succès !"}), 201

@abonne_bp.route('/abonne', methods=['GET'])
def get_abonnes():
    abonnes = list(db.abonne.find({}, {"_id": 0}))
    return jsonify(abonnes), 200

@abonne_bp.route('/abonne/<nom>', methods=['PUT'])
def update_abonne(nom):
    data = request.json
    db.abonne.update_one({"nom": nom}, {"$set": data})
    return jsonify({"message": "Abonné mis à jour avec succès !"}), 200

@abonne_bp.route('/abonne/<nom>', methods=['DELETE'])
def delete_abonne(nom):
    db.abonne.delete_one({"nom": nom})
    return jsonify({"message": "Abonné supprimé avec succès !"}), 200
from flask import Blueprint, request, jsonify
from pymongo import MongoClient

client = MongoClient("mongodb://localhost:27017/")
db = client["mybase"]

abonne_bp = Blueprint('abonne', __name__)

@app.route('/addabonnees', methods=['POST'])
def create_abonne():
    data = {
        "nom": request.form.get("nom"),
        "prenom": request.form.get("prenom"),
        "email": request.form.get("email"),
        "adresse": request.form.get("adresse"),
        "liste_emprunt_cours": request.form.get("liste_emprunt_cours"),
        "historique_emprunt": request.form.get("historique_emprunt"),
        "date_inscription": request.form.get("date_inscription")
    }

    if not data["email"]:
        return jsonify({"error": "L'email est requis."}), 400

    existing_abonne = db.abonne.find_one({"email": data["email"]})
    if existing_abonne:
        return jsonify({"error": "Un abonné avec cet email existe déjà."}), 409

    db.abonne.insert_one(data)
    return redirect(url_for('abonnees'))  


@abonne_bp.route('/abonne', methods=['GET'])
def get_abonnes():
    abonnes = list(db.abonne.find({}, {"_id": 0}))
    return jsonify(abonnes), 200

@abonne_bp.route('/abonne/<adresse>', methods=['PUT'])
def update_abonne(adresse):
    data = request.json 
    if not data:
        return jsonify({"error": "Aucune donnée fournie"}), 400

    result = db.abonne.update_one({"adresse": adresse}, {"$set": data})

    if result.matched_count == 0:
        return jsonify({"error": f"Aucun abonné trouvé avec le adresse '{adresse}'"}), 404

    return jsonify({"message": "Abonné mis à jour avec succès !"}), 200

@abonne_bp.route('/abonne/<email>', methods=['DELETE'])
def delete_abonne(email):
    db.abonne.delete_one({"email": email})
    return jsonify({"message": "Abonné supprimé avec succès !"}), 200